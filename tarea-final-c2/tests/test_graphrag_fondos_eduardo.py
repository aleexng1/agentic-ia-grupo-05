"""GraphRAG con fondos: driver simulado, corpus y referencias versionados reales."""

import hashlib
import json
from unittest.mock import MagicMock, Mock

import pytest
from fastapi.testclient import TestClient
from langchain_core.tools import ToolException
from neo4j import READ_ACCESS, WRITE_ACCESS
from neo4j.exceptions import ServiceUnavailable

from src.comun.errores import ErrorDeServicio
from src.conocimiento.grafo import cargar_grafo as carga, conexion, fondos
from src.conocimiento.grafo.prototipo_fondos import migrar
from src.conocimiento.rag.cargar_indice import RUTA_POLITICA, _preparar_documentos
from src.principal.flujos import consulta_politica as flujo
from tests.conftest import CLAVE_DE_PRUEBA
from tests.test_grafo import filas, ruta_fija  # noqa: F401

DESTINO = "neo4j+s://neo4j.invalid:7687/neo4j"
PREGUNTA = "¿Qué recorrido conecta FR-020 con el tope P03:hotel y cómo se compara con su saldo inicial ficticio?"
NODO = {
    "etiquetas": ["Grupo05C2GraphRAGFondoPropuesto"],
    "propiedades": {
        "proyecto": "grupo05-tarea-final-c2-graphrag-fondos-propuesta-1",
        "id_fondo": "FR-020",
        "fuente": "datos/fondos_ficticios.json",
    },
}
ARISTA = {
    "tipo": "FONDO_VINCULADO_A_CARGO_PROPUESTO",
    "propiedades": {
        "proyecto": "grupo05-tarea-final-c2-graphrag-fondos-propuesta-1",
        "estado": "propuesta_academica_pendiente_de_aprobacion",
    },
    "origen_proyecto": "grupo05-tarea-final-c2-graphrag-fondos-propuesta-1",
    "origen": "FR-020",
    "destino_proyecto": "grupo05-tarea-final-c2-graphrag",
    "destino": "cargo:jefe-de-tienda",
    "etiquetas_destino": ["Grupo05C2GraphRAG", "Cargo"],
}
CAMINO = {
    "fondo": "FR-020", "cargo_id": "cargo:jefe-de-tienda", "cargo": "Jefe de tienda",
    "nivel_id": "nivel:jefatura", "nivel": "Jefatura", "categoria_id": "P03:hotel",
    "tope_id": "tope:POL-RG-01:1.6:P03:hotel", "tope_clp": 325000,
    "fuente": "datos/politica_ficticia.md#P03", "documento": "POL-RG-01", "version": "1.6",
    "base": "por_documento", "relaciones": [
        "FONDO_VINCULADO_A_CARGO_PROPUESTO", "TIENE_NIVEL", "PUEDE_RENDIR", "TIENE_TOPE",
    ],
}


@pytest.fixture
def catalogo():
    return fondos._catalogo_v1()


@pytest.fixture
def inventario(catalogo):
    nodos, aristas = carga._filas(catalogo)
    huella = hashlib.sha256(json.dumps(catalogo.model_dump(), sort_keys=True).encode()).hexdigest()
    return [
        {"etiquetas": ["Grupo05C2GraphRAG", etiqueta], "tipo": None, "origen": None, "destino": None,
         "propiedades": {**fila, "proyecto": catalogo.proyecto, "huella": huella}}
        for etiqueta, filas in nodos.items() for fila in filas
    ] + [
        {"etiquetas": None, "tipo": tipo, "origen": fila["origen"], "destino": fila["destino"],
         "propiedades": {"proyecto": catalogo.proyecto, "origen_datos": fila["origen_datos"]}}
        for tipo, filas in aristas.items() for fila in filas
    ]


@pytest.fixture(autouse=True)
def servicios(monkeypatch):
    driver = MagicMock()
    monkeypatch.setattr(conexion.GraphDatabase, "driver", driver)
    monkeypatch.setenv("NEO4J_URI", "neo4j+s://neo4j.invalid")
    monkeypatch.setenv("NEO4J_USER", "lector-ficticio")
    monkeypatch.setenv("NEO4J_PASSWORD", "no-es-una-clave")
    monkeypatch.setenv("NEO4J_DATABASE", "neo4j")
    sesion = driver.return_value.__enter__.return_value.session
    tx = sesion.return_value.__enter__.return_value.begin_transaction.return_value.__enter__.return_value
    rag = Mock()
    doc = next(
        f for f in _preparar_documentos(RUTA_POLITICA.read_text(encoding="utf-8")) if f["codigo"] == "P03"
    )
    rag.invoke.return_value = [
        {"politica": doc["politica"], "texto": doc["texto_completo"], "fuente": doc["fuente"], "puntaje": 0.1},
    ]
    monkeypatch.setattr(flujo, "buscar_politica", rag)
    return driver, sesion, tx, rag


@pytest.fixture
def neo4j(servicios, inventario):
    _, _, tx, _ = servicios
    filas = {
        fondos._NODOS: [NODO], fondos._VINCULOS: [ARISTA], carga._INVENTARIO: inventario,
        fondos._RECORRIDO: [CAMINO],
    }
    tx.run.side_effect = lambda consulta, **params: Mock(**{"data.return_value": filas[consulta]})
    return filas


@pytest.fixture
def habilitado(monkeypatch):
    monkeypatch.setattr(fondos, "CONSULTA_FONDOS_HABILITADA", True)


def test_deshabilitada_por_defecto(servicios):
    driver, _, _, rag = servicios
    assert "no está habilitada" in flujo.responder_consulta(PREGUNTA, "hilo")["respuesta"]
    driver.assert_not_called()
    rag.invoke.assert_not_called()


def test_graph_agrega_recorrido_que_no_da_rag_documental(habilitado, neo4j, servicios):
    _, sesion, tx, rag = servicios
    solo_rag = flujo.responder_consulta("¿Cuál es el tope P03:hotel?", "hilo")
    grafo = flujo.responder_consulta(PREGUNTA, "hilo")

    assert solo_rag["herramientas_usadas"] == ["buscar_politica"]
    assert grafo["herramientas_usadas"] == ["recorrido_fondo", "buscar_politica"]
    assert "$325.000 CLP por documento" in solo_rag["respuesta"] and "FR-020" not in solo_rag["respuesta"]
    assert solo_rag["respuesta"] in grafo["respuesta"]
    assert "FR-020 → Jefe de tienda → Jefatura → P03:hotel → Tope" in grafo["respuesta"]
    assert "supera el saldo inicial ficticio de $20.000" in grafo["respuesta"]
    assert "no es el saldo actual" in grafo["respuesta"] and "no autoriza un gasto" in grafo["respuesta"]
    assert grafo["fuentes"] == ["datos/politica_ficticia.md#P03", "datos/fondos_ficticios.json"]
    assert "veredicto" not in grafo
    sesion.assert_called_once_with(database="neo4j", default_access_mode=READ_ACCESS)
    consultas = [llamada.args[0] for llamada in tx.run.call_args_list]
    assert consultas == [fondos._NODOS, fondos._VINCULOS, carga._INVENTARIO, fondos._RECORRIDO]
    assert tx.run.call_args.kwargs["categoria"] == "P03:hotel"
    assert tx.run.call_args.kwargs["fondo"] == "FR-020"
    assert rag.invoke.call_args_list[0] == rag.invoke.call_args_list[1]
    tx.commit.assert_not_called()


def test_fondo_sin_vinculo(habilitado, neo4j, servicios):
    _, _, tx, rag = servicios
    res = flujo.responder_consulta("¿Qué vínculo tiene FR-001 con Jefe de tienda y el tope P03:hotel?", "hilo")
    assert "No existe un vínculo propuesto" in res["respuesta"] and res["fuentes"] == []
    assert [llamada.args[0] for llamada in tx.run.call_args_list] == [fondos._NODOS, fondos._VINCULOS]
    rag.invoke.assert_not_called()


@pytest.mark.parametrize(("pregunta", "mensaje"), [
    ("¿Cuál es el tope P03:hotel para FR-999?", "no figura"),
    ("¿Cuál es el tope de hotel para FR-020?", "P02"),
    ("¿Cuál es el tope de hotel o hostal P03 para FR-020?", "una por consulta"),
    ("¿Qué saldo le queda hoy a FR-020?", "MCP de fondos"),
    ("¿Cuál es el tope P03:hotel para FR-020 y su saldo inicial y actual?", "MCP de fondos"),
    ("¿Cuál es el tope P03:hotel para FR-020 y FR-001?", "un solo identificador"),
])
def test_control_antes_de_contactar_servicios(habilitado, servicios, pregunta, mensaje):
    driver, _, _, rag = servicios
    assert mensaje in flujo.responder_consulta(pregunta, "hilo")["respuesta"]
    driver.assert_not_called()
    rag.invoke.assert_not_called()


def test_adaptador_directo_reconoce_ambiguedad(habilitado, servicios):
    with pytest.raises(ToolException, match="ambigua"):
        fondos.recorrido_fondo("FR-020", "hotel")
    servicios[0].assert_not_called()


@pytest.mark.parametrize(("consulta", "filas", "mensaje"), [
    (fondos._NODOS, [{**NODO, "propiedades": {**NODO["propiedades"], "fuente": "otra"}}], "extensión"),
    (fondos._VINCULOS, [ARISTA, ARISTA], "extensión"),
    (fondos._VINCULOS, [{**ARISTA, "destino": "cargo:analista-de-operaciones"}], "extensión"),
    (carga._INVENTARIO, [], "inventario"),
    (fondos._RECORRIDO, [], "recorrido íntegro esperado"),
    (fondos._RECORRIDO, [{**CAMINO, "fuente": "otra"}], "recorrido íntegro esperado"),
    (fondos._RECORRIDO, [{**CAMINO, "tope_clp": 325000.0}], "recorrido íntegro esperado"),
])
def test_recorrido_alterado_o_ausente_se_rechaza(habilitado, neo4j, servicios, consulta, filas, mensaje):
    neo4j[consulta] = filas
    with pytest.raises(ErrorDeServicio, match=mensaje):
        flujo.responder_consulta(PREGUNTA, "hilo")
    servicios[3].invoke.assert_not_called()


def test_extension_no_cargada_es_inconsistencia_para_fr020(habilitado, neo4j):
    neo4j[fondos._NODOS] = neo4j[fondos._VINCULOS] = []
    with pytest.raises(ErrorDeServicio, match="Falta en Neo4j el vínculo propuesto esperado"):
        flujo.responder_consulta(PREGUNTA, "hilo")


def test_caida_neo4j_no_inventa_resultados(habilitado, servicios):
    driver, _, _, rag = servicios
    driver.side_effect = ServiceUnavailable("dato interno")
    with pytest.raises(ErrorDeServicio, match="Neo4j no está disponible") as error:
        flujo.responder_consulta(PREGUNTA, "hilo")
    assert "dato interno" not in str(error.value)
    rag.invoke.assert_not_called()


@pytest.mark.parametrize("caida", [False, True])
def test_chat_preserva_contrato_e_id_ejecucion(habilitado, neo4j, servicios, ruta_fija, filas, monkeypatch, caida):
    from api.app import app
    from src.principal import grafo

    ruta_fija("consulta_politica")
    monkeypatch.setattr(grafo, "_GRAFO", grafo.construir_grafo())
    if caida:
        servicios[0].side_effect = ServiceUnavailable()
    respuesta = TestClient(app).post(
        "/chat?esperar=true", json={"texto": PREGUNTA}, headers={"X-API-Key": CLAVE_DE_PRUEBA},
    )
    cuerpo = respuesta.json()
    assert filas[0]["ruta"] == "consulta_politica"
    if caida:
        assert respuesta.status_code == 502
        assert "Neo4j no está disponible" in cuerpo["detail"]
        assert filas[0]["id_ejecucion"] in cuerpo["detail"]
        assert filas[0]["estado_final"] == "error"
    else:
        assert respuesta.status_code == 200
        assert cuerpo["id_ejecucion"] == filas[0]["id_ejecucion"]
        assert cuerpo["ruta"] == "consulta_politica" and cuerpo["estado_final"] == "ok"
        assert cuerpo["herramientas_usadas"] == ["recorrido_fondo", "buscar_politica"]
        assert "P03:hotel → Tope" in cuerpo["respuesta"] and "veredicto" not in cuerpo


@pytest.mark.parametrize("alterado", [False, True])
def test_rag_debe_recuperar_una_fuente_integra(habilitado, neo4j, servicios, alterado):
    rag = servicios[3]
    fragmento = rag.invoke.return_value[0]
    rag.invoke.return_value = [{**fragmento, "texto": fragmento["texto"].replace("325.000", "999.000")}] if alterado else []
    res = flujo.responder_consulta(PREGUNTA, "hilo")
    assert ("no coincide" if alterado else "No encontré evidencia") in res["respuesta"]
    assert not res["fuentes"] and "$325.000" not in res["respuesta"] and "$20.000" not in res["respuesta"]


@pytest.mark.parametrize(("operacion", "instalada", "esperada", "escritura"), [
    ("aplicar", False, True, migrar._ALTA),
    ("revertir", True, False, migrar._BAJA),
    ("aplicar", True, True, None),
    ("revertir", False, False, None),
    (None, True, True, None),
])
def test_migracion_aislada_y_repetible(
    neo4j, catalogo, servicios, operacion, instalada, esperada, escritura,
):
    _, sesion, tx, _ = servicios
    if not instalada:
        neo4j[fondos._NODOS] = neo4j[fondos._VINCULOS] = []
    leer = tx.run.side_effect

    def ejecutar(consulta, **params):
        if consulta == escritura:
            neo4j[fondos._NODOS] = [NODO] if esperada else []
            neo4j[fondos._VINCULOS] = [ARISTA] if esperada else []
            return Mock()
        return leer(consulta, **params)

    tx.run.side_effect = ejecutar
    assert migrar._migrar(catalogo, DESTINO, operacion, esperada) == {
        "base_verificada": {"nodos": 24, "relaciones": 27}, "instalada": esperada, "cambio": escritura is not None,
    }
    consultas = [llamada.args[0] for llamada in tx.run.call_args_list]
    assert consultas.count(carga._INVENTARIO) == (2 if escritura else 1)
    assert tx.commit.call_count == int(escritura is not None)
    sesion.assert_called_once_with(database="neo4j", default_access_mode=WRITE_ACCESS if operacion else READ_ACCESS)


def test_validacion_posterior_fallida_no_confirma_la_migracion(neo4j, catalogo, servicios):
    _, _, tx, _ = servicios
    neo4j[fondos._NODOS] = neo4j[fondos._VINCULOS] = []
    neo4j[migrar._ALTA] = []
    with pytest.raises(conexion.ErrorGrafo, match="no coincide"):
        migrar._migrar(catalogo, DESTINO, "aplicar", True)
    tx.commit.assert_not_called()


def test_revision_local_de_migracion_sin_driver(servicios, capsys):
    migrar.main(["--plan"])
    assert json.loads(capsys.readouterr().out)["base_esperada"] == {"nodos": 24, "relaciones": 27}
    servicios[0].assert_not_called()
