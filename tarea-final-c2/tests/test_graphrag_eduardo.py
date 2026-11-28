"""Pruebas de GraphRAG sin red; todos los registros y transacciones Neo4j se simulan."""

import json
from hashlib import sha256
from unittest.mock import MagicMock, Mock, call

import pytest
from langchain_core.tools import ToolException
from neo4j import READ_ACCESS, WRITE_ACCESS
from neo4j.exceptions import AuthError, ConnectionAcquisitionTimeoutError, ServiceUnavailable

from src.conocimiento.grafo import cargar_grafo as carga
from src.conocimiento.grafo import catalogo, conexion, consultar

DESTINO_SIMULADO = "neo4j+s://neo4j.invalid:7687/neo4j"
BASE_SIMULADA = "8a2b3c4d"
CARGO_ID = "cargo:jefe-de-tienda"


@pytest.fixture(autouse=True)
def driver_simulado(monkeypatch):
    """No usa credenciales reales; el driver y sus contextos no salen a red."""
    fabrica = MagicMock(name="driver_simulado")
    monkeypatch.setattr(conexion.GraphDatabase, "driver", fabrica)
    for variable in ("NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD", "NEO4J_DATABASE"):
        monkeypatch.delenv(variable, raising=False)
    yield fabrica


@pytest.fixture
def entorno_simulado(monkeypatch, driver_simulado):
    monkeypatch.setenv("NEO4J_URI", "neo4j+s://neo4j.invalid")
    monkeypatch.setenv("NEO4J_USER", "usuario-ficticio")
    monkeypatch.setenv("NEO4J_PASSWORD", "clave-ficticia-de-prueba")
    driver = driver_simulado.return_value.__enter__.return_value
    sesion = driver.session.return_value.__enter__.return_value
    return driver, sesion


@pytest.mark.parametrize("base", [None, BASE_SIMULADA, "ensayo.g05-v2"])
def test_configuracion_comparte_base_y_destino(entorno_simulado, monkeypatch, base):
    if base is not None:
        monkeypatch.setenv("NEO4J_DATABASE", base)
    ajustes = conexion.configuracion()
    assert ajustes.base == (base or "neo4j")
    assert ajustes.destino == f"neo4j+s://neo4j.invalid:7687/{base or 'neo4j'}"


@pytest.mark.parametrize("base", [
    "", "  ", " neo4j", "neo4j\n", "ab", "a" * 64, "ensáyo", "_ensayo",
    "-ensayo", "ensayo/base", "ensayo?base", "ensayo#base", "ensayo%2Fbase",
])
def test_base_invalida_se_rechaza_antes_del_driver(entorno_simulado, driver_simulado, monkeypatch, base):
    monkeypatch.setenv("NEO4J_DATABASE", base)
    with pytest.raises(ToolException, match="NEO4J_DATABASE"):
        consultar.tope_para("Jefe de tienda", "P02:hotel")
    with carga.confirmar_carga(DESTINO_SIMULADO), pytest.raises(conexion.ErrorGrafo, match="NEO4J_DATABASE"):
        carga.cargar_grafo(str(catalogo.RUTA_CATALOGO))
    driver_simulado.assert_not_called()


@pytest.fixture
def propuesta():
    return json.loads(catalogo.RUTA_CATALOGO.read_text(encoding="utf-8"))


@pytest.fixture
def politica():
    return catalogo.RUTA_POLITICA.read_text(encoding="utf-8")


def test_valida_catalogo_y_los_diez_topes_documentados(propuesta, politica):
    resultado = catalogo.validar_catalogo(propuesta, politica)
    assert catalogo.conteos(resultado) == {"nodos": 24, "relaciones": 27}
    assert {c.id: c.tope_clp for c in resultado.normativa.categorias} == {
        "P02:desayuno": 10000, "P02:almuerzo": 20000, "P02:cena": 45000,
        "P02:hotel": 445000, "P02:hostal": 295000,
        "P03:desayuno": 20000, "P03:almuerzo": 45000, "P03:cena": 50000,
        "P03:hotel": 325000, "P03:hostal": 265000,
    }
    assert all(c.fuente == f"datos/politica_ficticia.md#{c.id[:3]}" for c in resultado.normativa.categorias)
    assert resultado.estado == catalogo.ESTADO_PROPUESTA
    _, aristas = carga._filas(resultado)
    assert all(r["origen_datos"] == catalogo.ESTADO_PROPUESTA for r in aristas["PUEDE_RENDIR"])
    assert all(r["origen_datos"] == "POL-RG-01" for r in aristas["TIENE_TOPE"])


@pytest.mark.parametrize("monto", [0, -1, True, 1.0, "10000", 2**63])
def test_rechaza_montos_invalidos(propuesta, politica, monto):
    propuesta["normativa"]["categorias"][0]["tope_clp"] = monto
    with pytest.raises(catalogo.ErrorCatalogo, match="tipos"):
        catalogo.validar_catalogo(propuesta, politica)


@pytest.mark.parametrize("campo,valor", [
    ("id", "P03:desayuno"),
    ("tope_clp", 10001),
    ("fuente", "datos/politica_ficticia.md#P03"),
    ("nombre", "Desayuno modificado"),
])
def test_rechaza_hechos_que_no_corresponden_a_la_fuente(propuesta, politica, campo, valor):
    propuesta["normativa"]["categorias"][0][campo] = valor
    with pytest.raises(catalogo.ErrorCatalogo, match="duplicada|no coinciden"):
        catalogo.validar_catalogo(propuesta, politica)


def test_no_valida_con_una_version_distinta(propuesta, politica):
    with pytest.raises(catalogo.ErrorCatalogo, match="v1.6"):
        catalogo.validar_catalogo(propuesta, politica.replace("| Versión | 1.6 ", "| Versión | 1.60 "))


@pytest.mark.parametrize("duplicado", ["id", "nombre", "nivel", "arista", "grupo"])
def test_rechaza_duplicados(propuesta, politica, duplicado):
    org = propuesta["organizacion_ficticia"]
    if duplicado == "id":
        org["cargos"][1]["id"] = CARGO_ID
    elif duplicado == "nombre":
        org["cargos"][1]["nombre"] = "JÉFE DE TIENDA"
    elif duplicado == "nivel":
        org["niveles"].append(org["niveles"][0])
    elif duplicado == "arista":
        org["elegibilidad_propuesta"][0]["categorias"].append("P02:hotel")
    else:
        org["elegibilidad_propuesta"].append(org["elegibilidad_propuesta"][0])
    with pytest.raises(catalogo.ErrorCatalogo, match="duplicad"):
        catalogo.validar_catalogo(propuesta, politica)


@pytest.mark.parametrize("referencia", ["cargo", "nivel", "categoria"])
def test_rechaza_referencias_invalidas(propuesta, politica, referencia):
    org = propuesta["organizacion_ficticia"]
    if referencia == "cargo":
        org["cargos"][0]["nivel_id"] = "nivel:inexistente"
    elif referencia == "nivel":
        org["elegibilidad_propuesta"][0]["nivel_id"] = "nivel:inexistente"
    else:
        org["elegibilidad_propuesta"][0]["categorias"][0] = "P02:inexistente"
    with pytest.raises(catalogo.ErrorCatalogo, match="inexistente"):
        catalogo.validar_catalogo(propuesta, politica)


def test_rechaza_claves_json_duplicadas(monkeypatch):
    monkeypatch.setattr(catalogo.Path, "read_text", Mock(return_value='{"a": 1, "a": 2}'))
    with pytest.raises(catalogo.ErrorCatalogo, match="claves duplicadas"):
        catalogo.leer_catalogo(str(catalogo.RUTA_CATALOGO))


def test_plan_no_pide_configuracion_ni_contacta_neo4j(monkeypatch, driver_simulado, capsys):
    config = Mock(side_effect=AssertionError("El plan no necesita configuración"))
    monkeypatch.setattr(carga, "configuracion", config)
    carga.main(["--plan"])
    salida = capsys.readouterr().out.splitlines()
    assert salida[0] == "PASS: POL-RG-01 v1.6; catálogo v1"
    assert salida[1] == f"Estado: {catalogo.ESTADO_PROPUESTA}"
    assert json.loads(salida[2]) == {"nodos": 24, "relaciones": 27}
    assert salida[3] == "SIN Neo4j, SIN .env, SIN escrituras"
    driver_simulado.assert_not_called()
    config.assert_not_called()


def test_plan_no_intenta_abrir_archivos_fuera_del_catalogo(monkeypatch, capsys):
    lectura = Mock(side_effect=AssertionError("No debe intentar leer .env"))
    monkeypatch.setattr(catalogo.Path, "read_text", lectura)
    with pytest.raises(SystemExit) as error:
        carga.main(["--plan", "--ruta", ".env"])
    assert error.value.code == 1
    assert "archivo JSON dentro de datos/" in capsys.readouterr().err
    lectura.assert_not_called()


def _resultado(datos):
    resultado = Mock()
    resultado.data.return_value = datos
    return resultado


def _camino(politica_id, monto):
    """Fila simulada (no evidencia) con la proyección esperada del recorrido."""
    categoria_id = f"{politica_id}:hotel"
    return {
        "cargo": "Jefe de tienda", "nivel": "Jefatura", "categoria": "Hotel", "categoria_id": categoria_id,
        "politica": politica_id, "tope_id": f"tope:POL-RG-01:1.6:{categoria_id}", "tope_clp": monto,
        "fuente": f"datos/politica_ficticia.md#{politica_id}", "documento": "POL-RG-01", "version": "1.6",
        "base": "por_documento", "estado_elegibilidad": catalogo.ESTADO_PROPUESTA,
        "cargo_id": CARGO_ID, "nivel_id": "nivel:jefatura",
        "origen_nivel": catalogo.ESTADO_PROPUESTA, "origen_tope": catalogo.DOCUMENTO,
        "relaciones": ["TIENE_NIVEL", "PUEDE_RENDIR", "TIENE_TOPE"],
    }


@pytest.fixture
def lectura(entorno_simulado):
    _, sesion = entorno_simulado
    return sesion.begin_transaction.return_value.__enter__.return_value


@pytest.mark.parametrize("politica_id,monto", [("P02", 445000), ("P03", 325000)])
@pytest.mark.parametrize("base", [None, BASE_SIMULADA])
def test_tope_publico_y_recorrido_parametrizado(
    lectura, driver_simulado, entorno_simulado, monkeypatch, politica_id, monto, base,
):
    if base is not None:
        monkeypatch.setenv("NEO4J_DATABASE", base)
    fila = _camino(politica_id, monto)
    categoria_id = fila["categoria_id"]
    candidato = [{"cargo_id": CARGO_ID, "categoria_id": categoria_id}]
    lectura.run.side_effect = [_resultado(candidato), _resultado([fila])] * 2

    assert consultar.tope_para(" JÉFE   de TIENDA  ", f" {politica_id.lower()}: HÓTEL ") == {
        "cargo": "Jefe de tienda", "nivel": "Jefatura", "categoria": "Hotel",
        "tope_clp": monto, "fuente": f"datos/politica_ficticia.md#{politica_id}",
    }
    assert lectura.run.call_args_list == [
        call(consultar._CANDIDATOS, proyecto=catalogo.PROYECTO, cargo_clave="jefe de tienda",
             categoria_id=categoria_id, categoria_clave="hotel"),
        call(consultar._RECORRIDO, proyecto=catalogo.PROYECTO, cargo_id=CARGO_ID, categoria_id=categoria_id),
    ]
    diagnostico = consultar._consultar_recorrido("Jefe de tienda", categoria_id)
    assert diagnostico["politica"] == politica_id
    assert diagnostico["relaciones"] == list(catalogo.RELACIONES)
    assert all(f":{tipo} " in consultar._RECORRIDO for tipo in catalogo.RELACIONES)
    assert "relationships(camino)" in consultar._RECORRIDO
    assert all(
        not any(op in args[0].split() for op in ("CREATE", "MERGE", "DELETE", "SET", "REMOVE"))
        for args, _ in lectura.run.call_args_list
    )
    lectura.commit.assert_not_called()
    driver, sesion = entorno_simulado
    driver.session.assert_called_with(database=base or "neo4j", default_access_mode=READ_ACCESS)
    sesion.begin_transaction.assert_called_with(timeout=5)
    driver_simulado.return_value.__exit__.assert_called()


@pytest.mark.parametrize("cargo,categoria", [
    ("Cargo inexistente", "P02:hotel"),
    ("Jefe de tienda", "P04:inexistente"),
])
def test_cargo_o_categoria_inexistente_devuelve_none(lectura, cargo, categoria):
    lectura.run.return_value = _resultado([])
    assert consultar.tope_para(cargo, categoria) is None
    lectura.run.assert_called_once()


def test_no_hay_camino_no_significa_un_tope_cero(lectura):
    lectura.run.side_effect = [
        _resultado([{"cargo_id": "cargo:analista-de-operaciones", "categoria_id": "P03:hotel"}]),
        _resultado([]),
    ]
    assert consultar.tope_para("Analista de Operaciones", "P03:hotel") is None


def test_consulta_real_rechaza_camino_incompatible_con_elegibilidad(lectura, monkeypatch):
    from src.principal.flujos import consulta_politica
    from src.conocimiento.rag.cargar_indice import _preparar_documentos

    documentos = _preparar_documentos(catalogo.RUTA_POLITICA.read_text(encoding="utf-8"))
    doc = next(d for d in documentos if d["codigo"] == "P03")
    monkeypatch.setattr(consulta_politica, "buscar_politica", Mock(invoke=Mock(return_value=[{
        "politica": doc["politica"], "fuente": doc["fuente"], "texto": doc["texto_completo"], "puntaje": -0.1,
    }])))
    cargo_id = "cargo:analista-de-operaciones"
    fila = {**_camino("P03", 325000), "cargo_id": cargo_id, "nivel_id": "nivel:profesional",
            "cargo": "Analista de Operaciones", "nivel": "Profesional"}
    lectura.run.side_effect = [
        _resultado([{"cargo_id": cargo_id, "categoria_id": "P03:hotel"}]), _resultado([fila]),
    ]
    with pytest.raises(consulta_politica.ErrorDeServicio, match="GraphRAG"):
        consulta_politica.responder_consulta(
            "¿Cuál es el tope P03 de hotel para un Analista de Operaciones?", "prueba",
        )


@pytest.mark.parametrize("ausencia", ["candidato", "recorrido", "una_politica_ambigua"])
def test_tope_rechaza_ausencias_que_el_catalogo_no_permite(lectura, ausencia):
    candidato = {"cargo_id": CARGO_ID, "categoria_id": "P02:hotel"}
    lectura.run.side_effect = [_resultado([] if ausencia == "candidato" else [candidato]), _resultado([])]
    with pytest.raises(ToolException, match="resultado incompatible"):
        consultar.tope_para("Jefe de tienda", "hotel" if ausencia == "una_politica_ambigua" else "P02:hotel")


def test_categoria_ambigua_exige_contexto_aun_si_no_hay_dos_caminos(lectura):
    lectura.run.return_value = _resultado([
        {"cargo_id": "cargo:analista-de-operaciones", "categoria_id": id_}
        for id_ in ("P02:hotel", "P03:hotel")
    ])
    with pytest.raises(ToolException, match="ambigua"):
        consultar.tope_para("Analista de Operaciones", "hotel")
    lectura.run.assert_called_once()
    assert lectura.run.call_args.kwargs["categoria_id"] is None


@pytest.mark.parametrize("cargo,categoria", [
    (None, "hotel"), ("  ", "hotel"), ("a" * 101, "hotel"),
    ("Jefe de tienda", "P02:"), ("Jefe de tienda", " \t"), ("Jefe de tienda", "viaje: hotel"),
])
def test_entrada_invalida_no_crea_driver(driver_simulado, cargo, categoria):
    with pytest.raises(ToolException, match="texto no vacío|cualificada"):
        consultar.tope_para(cargo, categoria)
    driver_simulado.assert_not_called()


def test_cypher_sospechoso_solo_llega_como_parametro(lectura):
    # Cadena ficticia: la prueba no envía Cypher dinámico ni consulta un servidor.
    literal = "x') RETURN 'dato de prueba' //"
    lectura.run.return_value = _resultado([])
    assert consultar.tope_para(literal, "P02:hotel") is None
    consulta, = lectura.run.call_args.args
    assert consulta == consultar._CANDIDATOS and literal not in consulta
    assert lectura.run.call_args.kwargs["cargo_clave"] == literal.lower()


@pytest.mark.parametrize("error,mensaje", [
    (TimeoutError, "tiempo de espera"),
    (ConnectionAcquisitionTimeoutError, "tiempo de espera"),
    (AuthError, "autenticación"),
    (ServiceUnavailable, "no está disponible"),
])
def test_fallas_de_neo4j_no_se_confunden_con_ausencia_ni_filtran_el_mensaje(lectura, error, mensaje):
    lectura.run.side_effect = error("detalle-interno-simulado")
    with pytest.raises(ToolException, match=mensaje) as falla:
        consultar.tope_para("Jefe de tienda", "P02:hotel")
    assert "detalle-interno" not in str(falla.value)
    assert falla.value.__suppress_context__


@pytest.mark.parametrize("campo,valor", [
    ("nivel", None), ("cargo", "Otro cargo"), ("categoria_id", "P03:hotel"),
    ("tope_clp", True), ("tope_clp", "445000"), ("tope_clp", 0),
    ("fuente", "datos/politica_ficticia.md#P03"), ("version", "1.5"),
    ("relaciones", ["TIENE_TOPE"]), ("estado_elegibilidad", "regla-oficial"),
    ("cargo_id", "cargo:otro"), ("nivel_id", "nivel:profesional"),
    ("origen_nivel", "otro-origen"), ("origen_tope", "otro-origen"),
    ("tope_clp", 999000), ("tope_clp", 445000.0),
])
def test_rechaza_recorrido_incompleto_o_incompatible(lectura, campo, valor):
    fila = _camino("P02", 445000)
    fila[campo] = valor
    lectura.run.side_effect = [
        _resultado([{"cargo_id": CARGO_ID, "categoria_id": "P02:hotel"}]), _resultado([fila]),
    ]
    with pytest.raises(ToolException, match="resultado incompatible"):
        consultar.tope_para("Jefe de tienda", "P02:hotel")


def test_no_elige_arbitrariamente_un_camino_duplicado(lectura):
    fila = _camino("P02", 445000)
    lectura.run.side_effect = [
        _resultado([{"cargo_id": CARGO_ID, "categoria_id": "P02:hotel"}]), _resultado([fila, fila]),
    ]
    with pytest.raises(ToolException, match="resultado incompatible"):
        consultar.tope_para("Jefe de tienda", "P02:hotel")


def test_carga_sin_confirmacion_o_con_otro_destino_no_crea_driver(driver_simulado, entorno_simulado):
    ruta = str(catalogo.RUTA_CATALOGO)
    with pytest.raises(conexion.ErrorGrafo, match="confirmación explícita"):
        carga.cargar_grafo(ruta)
    with carga.confirmar_carga("neo4j+s://otro.invalid:7687/neo4j"):
        with pytest.raises(conexion.ErrorGrafo, match="no coincide"):
            carga.cargar_grafo(ruta)
    driver_simulado.assert_not_called()


def test_carga_rechaza_otra_base_en_el_mismo_servidor(entorno_simulado, driver_simulado, monkeypatch):
    monkeypatch.setenv("NEO4J_DATABASE", BASE_SIMULADA)
    with carga.confirmar_carga(DESTINO_SIMULADO), pytest.raises(conexion.ErrorGrafo, match="no coincide"):
        carga.cargar_grafo(str(catalogo.RUTA_CATALOGO))
    driver_simulado.assert_not_called()


@pytest.fixture
def escritura(entorno_simulado):
    driver, sesion = entorno_simulado
    ddl, datos = MagicMock(), MagicMock()
    ddl.__enter__.return_value = ddl
    datos.__enter__.return_value = datos
    sesion.begin_transaction.side_effect = [ddl, datos] * 2
    return driver, sesion, ddl, datos


@pytest.mark.parametrize("cambio", [
    "integro", "monto", "tipo_monto", "relacion", "propiedad", "huella", "identidad", "parcial", "duplicada",
])
def test_carga_con_inventario_preexistente(escritura, cambio):
    _, _, _, datos = escritura
    referencia = catalogo.leer_catalogo(str(catalogo.RUTA_CATALOGO))
    huella = sha256(json.dumps(referencia.model_dump(), sort_keys=True).encode()).hexdigest()
    nodos, aristas = carga._filas(referencia)
    inventario = [
        {"etiquetas": ["Grupo05C2GraphRAG", etiqueta],
         "propiedades": {**fila, "proyecto": catalogo.PROYECTO, "huella": huella},
         "tipo": None, "origen": None, "destino": None}
        for etiqueta, filas in nodos.items() for fila in filas
    ] + [
        {"etiquetas": None, "tipo": tipo, "origen": fila["origen"], "destino": fila["destino"],
         "propiedades": {"proyecto": catalogo.PROYECTO, "origen_datos": fila["origen_datos"]}}
        for tipo, filas in aristas.items() for fila in filas
    ]
    tope = next(f for f in inventario if f["propiedades"].get("id") == catalogo.id_tope("P02:hotel"))
    relacion = next(f for f in inventario if f["tipo"] == "PUEDE_RENDIR")
    if cambio == "monto":
        tope["propiedades"]["tope_clp"] = 999000
    elif cambio == "tipo_monto":
        tope["propiedades"]["tope_clp"] = 445000.0
    elif cambio == "relacion":
        relacion["destino"] = "P04:hotel"
    elif cambio == "propiedad":
        relacion["propiedades"]["origen_datos"] = "otra-propuesta"
    elif cambio == "huella":
        tope["propiedades"]["huella"] = "otra-huella"
    elif cambio == "identidad":
        tope["propiedades"]["id"] = "tope:otro"
    elif cambio == "parcial":
        inventario.remove(relacion)
    elif cambio == "duplicada":
        otra = next(f for f in inventario if f["tipo"] == "TIENE_TOPE")
        inventario[inventario.index(otra)] = relacion

    datos.run.return_value = _resultado(inventario)
    with carga.confirmar_carga(DESTINO_SIMULADO):
        if cambio == "integro":
            assert carga.cargar_grafo(str(catalogo.RUTA_CATALOGO)) == {"nodos": 24, "relaciones": 27}
        else:
            with pytest.raises(conexion.ErrorGrafo, match="otro catálogo|inventario"):
                carga.cargar_grafo(str(catalogo.RUTA_CATALOGO))
            datos.commit.assert_not_called()
    datos.run.assert_called_once_with(carga._INVENTARIO, proyecto=catalogo.PROYECTO)


@pytest.mark.parametrize("base", [None, BASE_SIMULADA])
def test_carga_simulada_repetible_y_aislada(escritura, driver_simulado, monkeypatch, base):
    destino = DESTINO_SIMULADO
    if base is not None:
        monkeypatch.setenv("NEO4J_DATABASE", base)
        destino = f"neo4j+s://neo4j.invalid:7687/{base}"
    driver, sesion, ddl, datos = escritura
    ajeno = {"propiedades": {"proyecto": "proyecto-ajeno", "huella": "huella-ajena"}}
    ajena = {"propiedades": {"proyecto": "proyecto-ajeno"}, "tipo": "TIENE_TOPE"}
    nodos = {("proyecto-ajeno", "categoria:hotel"): ajeno}
    relaciones = {("proyecto-ajeno", "TIENE_TOPE", "hotel", "tope"): ajena}

    def simular_merge(cypher, *, proyecto, **params):
        assert proyecto == catalogo.PROYECTO
        if cypher == carga._INVENTARIO:
            return _resultado([f for (p, *_), f in [*nodos.items(), *relaciones.items()] if p == proyecto])
        assert "MERGE" in cypher and "$filas" in cypher and "DELETE" not in cypher
        if cypher in carga._NODOS.values():
            etiqueta = next(e for e, q in carga._NODOS.items() if q == cypher)
            for fila in params["filas"]:
                nodos.setdefault((proyecto, fila["id"]), {
                    "tipo": None, "etiquetas": [etiqueta, "Grupo05C2GraphRAG"],
                    "propiedades": {**fila, "proyecto": proyecto, "huella": params["huella"]},
                })
        else:
            tipo = next(tipo for tipo, q in carga._ARISTAS.items() if q == cypher)
            for fila in params["filas"]:
                assert (proyecto, fila["origen"]) in nodos and (proyecto, fila["destino"]) in nodos
                relaciones.setdefault((proyecto, tipo, fila["origen"], fila["destino"]), {
                    "tipo": tipo, "etiquetas": None, "origen": fila["origen"], "destino": fila["destino"],
                    "propiedades": {"proyecto": proyecto, "origen_datos": fila["origen_datos"]},
                })
        return Mock()

    datos.run.side_effect = simular_merge
    with carga.confirmar_carga(destino):
        primero = carga.cargar_grafo(str(catalogo.RUTA_CATALOGO))
        segundo = carga.cargar_grafo(str(catalogo.RUTA_CATALOGO))
    assert primero == segundo == {"nodos": 24, "relaciones": 27}
    assert len(nodos) == 25 and len(relaciones) == 28
    assert nodos[("proyecto-ajeno", "categoria:hotel")] is ajeno
    assert relaciones[("proyecto-ajeno", "TIENE_TOPE", "hotel", "tope")] is ajena
    assert [c.args[0] for c in datos.run.call_args_list] == [
        carga._INVENTARIO, *carga._NODOS.values(), *carga._ARISTAS.values(),
        carga._INVENTARIO, carga._INVENTARIO,
    ]
    assert ddl.run.call_args_list == [call(carga._RESTRICCION)] * 2
    assert "IF NOT EXISTS" in carga._RESTRICCION and "(n.proyecto, n.id) IS UNIQUE" in carga._RESTRICCION
    assert ddl.commit.call_count == datos.commit.call_count == 2
    assert sesion.begin_transaction.call_args_list == [call(timeout=20), call(timeout=10)] * 2
    driver.session.assert_called_with(database=base or "neo4j", default_access_mode=WRITE_ACCESS)
    opciones = driver_simulado.call_args.kwargs
    assert opciones["connection_timeout"] == 3
    assert opciones["connection_acquisition_timeout"] == opciones["connection_write_timeout"] == 5
    assert opciones["max_transaction_retry_time"] == 0


def test_carga_no_modifica_datos_de_un_catalogo_con_otra_huella(escritura):
    _, _, ddl, datos = escritura
    datos.run.return_value = _resultado([{"tipo": None, "propiedades": {"huella": "distinta"}}])
    with carga.confirmar_carga(DESTINO_SIMULADO), pytest.raises(conexion.ErrorGrafo, match="otro catálogo"):
        carga.cargar_grafo(str(catalogo.RUTA_CATALOGO))
    assert datos.run.call_args.args == (carga._INVENTARIO,)
    datos.run.assert_called_once()
    datos.commit.assert_not_called()
    datos.__exit__.assert_called_once()
    ddl.commit.assert_called_once()


def test_si_inventario_final_no_cuadra_no_confirma_transaccion_de_datos(escritura):
    _, _, _, datos = escritura
    datos.run.side_effect = [_resultado([]), *[Mock() for _ in range(7)], _resultado([])]
    with carga.confirmar_carga(DESTINO_SIMULADO), pytest.raises(conexion.ErrorGrafo, match="inventario"):
        carga.cargar_grafo(str(catalogo.RUTA_CATALOGO))
    datos.commit.assert_not_called()
    datos.__exit__.assert_called_once()
