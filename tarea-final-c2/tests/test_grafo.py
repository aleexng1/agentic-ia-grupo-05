"""Pruebas del grafo del agente principal (Alex), sin Gemini: router y flujos falsos."""

import json

import pytest
from fastapi.testclient import TestClient

from src.principal import grafo as modulo_grafo
from src.principal import router
from src.principal.flujos import consulta_politica as modulo_consulta
from src.principal.flujos import revisar_gasto as modulo_react
from tests.conftest import CLAVE_DE_PRUEBA
from tests.test_react_mcp import revisar_gasto  # noqa: F401  (fixture: ReAct con registro en memoria)

GASTO = {
    "id": "G-0101", "fecha_gasto": "2026-10-06", "fecha_rendicion": "2026-10-09", "monto": 7800,
    "tipo_documento": "boleta", "proveedor": "Concesionaria Vial Lago Verde",
    "glosa": "peaje ida y vuelta CD - tienda Norte", "politica_declarada": "Viajes Internos",
    "categoria_declarada": "Peaje", "unidad_negocio": "CD", "patente": "RZPT41", "id_fondo": "FR-001",
    "rut_emisor": "11.111.111-1", "folio": "000123",
}
IMAGEN = {"mime_type": "image/png", "datos_base64": "aW1hZ2VuLWRlLXBydWViYQ=="}


@pytest.fixture
def ruta_fija(monkeypatch):
    """Router falso: la ruta la decide la prueba, sin llamar a Gemini."""

    def fijar(ruta, modelo="principal"):
        monkeypatch.setattr(
            router, "clasificar",
            lambda texto, tiene_imagen=False, trae_gasto=False: {"ruta": ruta, "motivo": f"prueba: {ruta}", "modelo": modelo},
        )

    return fijar


@pytest.fixture
def filas(monkeypatch):
    """Captura lo que el grafo manda a guardar_ejecucion (Sebastián)."""
    guardadas = []
    from src.comun import registro

    monkeypatch.setattr(registro, "guardar_ejecucion", guardadas.append)
    return guardadas


def _ejecutar(texto, **kwargs):
    return modulo_grafo.ejecutar(kwargs.pop("thread_id", "t-prueba"), texto, grafo=modulo_grafo.construir_grafo(), **kwargs)


def test_fuera_de_alcance_responde_sin_herramientas(ruta_fija, filas):
    ruta_fija("fuera_de_alcance")
    salida = _ejecutar("Escríbeme un poema")
    assert salida["ruta"] == "fuera_de_alcance" and salida["estado_final"] == "ok"
    assert salida["herramientas_usadas"] == [] and salida["hubo_a2a"] is False
    assert "Consultar la política" in salida["respuesta"]
    assert len(filas) == 1 and filas[0]["ruta"] == "fuera_de_alcance"


def test_dos_solicitudes_distintas_activan_flujos_distintos(ruta_fija, filas, monkeypatch):
    # Flujo de Eduardo falso: la prueba no depende de Redis ni de Gemini.
    monkeypatch.setattr(modulo_consulta, "responder_consulta", lambda texto, thread_id: {
        "respuesta": "Plazo de 30 días. [Fuente: politica#RG-03]", "fuentes": ["politica#RG-03"],
        "herramientas_usadas": ["buscar_politica"]})
    ruta_fija("fuera_de_alcance")
    primera = _ejecutar("¿Qué tiempo hará mañana?")
    ruta_fija("consulta_politica")
    segunda = _ejecutar("¿Cuál es el plazo para rendir?")
    assert primera["ruta"] != segunda["ruta"]
    assert primera["id_ejecucion"] != segunda["id_ejecucion"]
    assert segunda["estado_final"] == "ok" and segunda["herramientas_usadas"] == ["buscar_politica"]


def test_flujo_de_otro_sin_implementar_termina_en_error_claro(ruta_fija, filas, monkeypatch):
    def sin_implementar(texto, thread_id):
        raise NotImplementedError("responder_consulta: pendiente")

    monkeypatch.setattr(modulo_consulta, "responder_consulta", sin_implementar)
    ruta_fija("consulta_politica")
    salida = _ejecutar("¿Cuál es el plazo para rendir?")
    assert salida["estado_final"] == "error"
    assert salida["respuesta"] == "Flujo consulta_politica todavía no implementado."
    assert filas[0]["estado_final"] == "error"


def test_falla_del_flujo_registra_la_ruta_elegida(ruta_fija, filas, monkeypatch):
    def falla(texto, thread_id):
        raise RuntimeError("No se pudo completar la búsqueda documental (Redis o embeddings).")

    monkeypatch.setattr(modulo_consulta, "responder_consulta", falla)
    ruta_fija("consulta_politica")
    with pytest.raises(modulo_grafo.ErrorDeEjecucion) as error:
        _ejecutar("¿Cuál es el plazo para rendir?")
    assert filas[0]["id_ejecucion"] == error.value.id_ejecucion
    assert (filas[0]["ruta"], filas[0]["estado_final"]) == ("consulta_politica", "error")


def test_revisar_gasto_sin_datos_los_pide_sin_inventarlos(ruta_fija, filas):
    ruta_fija("revisar_gasto")
    salida = _ejecutar("Revisa mi gasto de bencina")
    assert salida["estado_final"] == "ok" and "Faltan:" in salida["respuesta"]
    assert "monto" in salida["respuesta"] and "veredicto" not in salida


def test_revisar_gasto_sin_revisar_caso_termina_en_error(ruta_fija, filas, monkeypatch):
    ruta_fija("revisar_gasto")
    monkeypatch.delattr(modulo_react, "revisar_caso", raising=False)
    salida = _ejecutar("Revisa este gasto:\n" + json.dumps(GASTO))
    assert salida["estado_final"] == "error"
    assert salida["respuesta"].startswith("Flujo revisar_gasto todavía no implementado")


def _react_falso(monkeypatch, decision="aprobar", estado_final="ok"):
    recibido = {}

    def revisar_caso(agente, mensaje, hilo, gasto, fondo=None, verificacion=None):
        recibido.update(mensaje=mensaje, hilo=hilo, gasto=gasto, verificacion=verificacion)
        return {
            "respuesta": f"Decisión: {decision}.", "pasos": 3, "estado_final": estado_final,
            "herramientas_usadas": ["buscar_politica", "validar_gasto", "emitir_veredicto"],
            "veredicto": {"decision": decision, "motivo": "Cumple RG-01.", "politica_sugerida": "P02",
                          "categoria_sugerida": "Peaje", "cuenta_sugerida": "CTA-6100"},
        }

    monkeypatch.setattr(modulo_react, "revisar_caso", revisar_caso, raising=False)
    monkeypatch.setattr(modulo_grafo, "_agente_react", lambda modulo, checkpointer: object())
    return recibido


def _verificador_falso(monkeypatch, respuesta):
    from src.principal.herramientas import delegar_verificador as modulo_delegar

    llamadas = []

    async def delegar(imagen, declarado):
        llamadas.append((imagen, declarado))
        return respuesta

    monkeypatch.setattr(modulo_delegar, "delegar_verificador", delegar)
    return llamadas


def test_revisar_gasto_con_boleta_que_cuadra(ruta_fija, filas, monkeypatch):
    ruta_fija("revisar_gasto")
    recibido = _react_falso(monkeypatch)
    llamadas = _verificador_falso(monkeypatch, {
        "disponible": True, "leido": {}, "confianza": 0.9, "observaciones": "",
        "cuadra": {c: "sí" for c in ("monto", "fecha", "rut_emisor", "folio", "categoria")},
    })
    salida = _ejecutar("Revisa este gasto", gasto=GASTO, imagen=IMAGEN, thread_id="hilo-1")
    assert salida["estado_final"] == "ok" and salida["hubo_a2a"] is True
    assert salida["veredicto"]["decision"] == "aprobar"
    assert salida["herramientas_usadas"][0] == "delegar_verificador"
    imagen, declarado = llamadas[0]
    assert imagen == IMAGEN and declarado == {"monto": 7800, "fecha": "2026-10-06", "rut_emisor": "11.111.111-1",
                                              "folio": "000123", "categoria": "Peaje"}
    assert "rut_emisor" not in recibido["gasto"] and recibido["hilo"] == "hilo-1:revisar_gasto"
    assert filas[0]["hubo_a2a"] is True and filas[0]["pasos"] == 3


def test_boleta_que_no_cuadra_no_se_aprueba(ruta_fija, filas, monkeypatch):
    ruta_fija("revisar_gasto")
    _react_falso(monkeypatch, decision="aprobar")
    _verificador_falso(monkeypatch, {
        "disponible": True, "leido": {}, "confianza": 0.8, "observaciones": "",
        "cuadra": {"monto": "no", "fecha": "sí", "rut_emisor": "sí", "folio": "sí", "categoria": "sí"},
    })
    salida = _ejecutar("Revisa este gasto", gasto=GASTO, imagen=IMAGEN)
    assert salida["veredicto"]["decision"] == "observar"
    assert "no coincide con lo declarado en monto" in salida["respuesta"]


def test_verificador_caido_deja_observar_y_fallback(ruta_fija, filas, monkeypatch):
    ruta_fija("revisar_gasto")
    _react_falso(monkeypatch, decision="aprobar")
    _verificador_falso(monkeypatch, {"disponible": False, "tipo_fallo": "timeout", "motivo": "el verificador no respondió en 20 s"})
    salida = _ejecutar("Revisa este gasto", gasto=GASTO, imagen=IMAGEN)
    assert salida["estado_final"] == "fallback"
    assert salida["veredicto"]["decision"] == "observar"
    assert "No se pudo verificar la boleta" in salida["respuesta"]


def test_bloqueo_del_react_gana_sobre_todo(ruta_fija, filas, monkeypatch):
    ruta_fija("revisar_gasto")
    _react_falso(monkeypatch, decision="rechazar", estado_final="bloqueado")
    _verificador_falso(monkeypatch, {"disponible": False, "tipo_fallo": "timeout", "motivo": "x"})
    assert _ejecutar("Revisa este gasto", gasto=GASTO, imagen=IMAGEN)["estado_final"] == "bloqueado"


def test_la_imagen_no_queda_en_el_estado_guardado(ruta_fija, filas, monkeypatch):
    ruta_fija("revisar_gasto")
    _react_falso(monkeypatch)
    _verificador_falso(monkeypatch, {"disponible": False, "tipo_fallo": "forzado", "motivo": "x"})
    grafo = modulo_grafo.construir_grafo()
    modulo_grafo.ejecutar("hilo-img", "Revisa este gasto", imagen=IMAGEN, gasto=GASTO, grafo=grafo)
    guardado = json.dumps(grafo.get_state({"configurable": {"thread_id": "hilo-img"}}).values, default=str)
    assert IMAGEN["datos_base64"] not in guardado
    assert modulo_grafo._ADJUNTOS == {}


def test_respaldo_del_router_marca_fallback(ruta_fija, filas):
    ruta_fija("fuera_de_alcance", modelo="respaldo")
    assert _ejecutar("hola")["estado_final"] == "fallback"


def test_fila_de_ejecucion_tiene_las_columnas_del_contrato(ruta_fija, filas):
    ruta_fija("fuera_de_alcance")
    _ejecutar("hola")
    assert set(filas[0]) == {"id_ejecucion", "fecha", "ruta", "pasos", "herramientas_usadas", "hubo_a2a",
                             "estado_final", "duracion_ms"}


def test_registro_sin_implementar_no_rompe_el_chat(ruta_fija, monkeypatch, caplog):
    from src.comun import registro

    def no_implementado(fila):
        raise NotImplementedError("guardar_ejecucion: pendiente")

    monkeypatch.setattr(registro, "guardar_ejecucion", no_implementado)
    ruta_fija("fuera_de_alcance")
    assert _ejecutar("hola")["estado_final"] == "ok"


@pytest.mark.parametrize(("estados", "esperado"), [
    (("ok", "fallback"), "fallback"), (("fallback", "error"), "error"),
    (("error", "bloqueado"), "bloqueado"), (("ok", None), "ok"), ((), "ok"),
])
def test_combinar_estados(estados, esperado):
    assert modulo_grafo.combinar_estados(*estados) == esperado


# --- API -------------------------------------------------------------------


@pytest.fixture
def cliente(monkeypatch):
    from api.app import app

    monkeypatch.setattr(modulo_grafo, "_GRAFO", modulo_grafo.construir_grafo())
    return TestClient(app)


CABECERAS = {"X-API-Key": CLAVE_DE_PRUEBA}


def test_chat_mensaje_vacio_responde_422_claro_sin_llamar_al_router(cliente, monkeypatch):
    def no_llamar(*args, **kwargs):
        raise AssertionError("no debía llamar al router")

    monkeypatch.setattr(router, "clasificar", no_llamar)
    respuesta = cliente.post("/chat", json={"texto": "   "}, headers=CABECERAS)
    assert respuesta.status_code == 422 and "vacío" in respuesta.json()["detail"]
    respuesta = cliente.post("/chat", json={"texto": "x" * 4001}, headers=CABECERAS)
    assert respuesta.status_code == 422 and "4000" in respuesta.json()["detail"]


def test_chat_falla_del_router_responde_502_con_id(cliente, monkeypatch, filas):
    def falla(*args, **kwargs):
        raise RuntimeError("503 UNAVAILABLE")

    monkeypatch.setattr(router, "clasificar", falla)
    respuesta = cliente.post("/chat?esperar=true", json={"texto": "hola"}, headers=CABECERAS)
    assert respuesta.status_code == 502 and "id_ejecucion:" in respuesta.json()["detail"]
    assert filas[0]["ruta"] == "sin_ruta" and filas[0]["estado_final"] == "error"


def test_chat_sin_thread_id_crea_uno(cliente, ruta_fija, filas):
    ruta_fija("fuera_de_alcance")
    datos = cliente.post("/chat?esperar=true", json={"texto": "hola"}, headers=CABECERAS).json()
    assert datos["thread_id"] and datos["id_ejecucion"] and datos["ruta"] == "fuera_de_alcance"


def test_boleta_que_no_cuadra_chat_y_registro_dicen_observar(ruta_fija, filas, monkeypatch, revisar_gasto):  # noqa: F811
    """Punta a punta con el ReAct real de Matías (LLM guionado): el modelo propone aprobar, el
    verificador dice que el monto no cuadra, y tanto /chat como el registro quedan en «observar»."""
    from tests.test_revisar_gasto_c2 import _guion_aprobar_gs01
    from tests.test_seguridad import LLMFalso

    turno, pasos = _guion_aprobar_gs01()
    monkeypatch.setattr(revisar_gasto, "obtener_llm", lambda: LLMFalso(pasos))
    monkeypatch.setattr(modulo_grafo, "_AGENTE_REACT", None)  # compila el ReAct con el LLM guionado
    ruta_fija("revisar_gasto")
    no_cuadra = {"disponible": True, "leido": {"monto": 9800}, "confianza": 0.9, "observaciones": "",
                 "cuadra": {"monto": "no", "fecha": "sí", "rut_emisor": "sí", "folio": "sí", "categoria": "sí"}}
    llamadas = _verificador_falso(monkeypatch, no_cuadra)
    gasto = {**turno["gasto"], "rut_emisor": "11.111.111-1", "folio": "000123"}

    salida = _ejecutar("Revisa este gasto.", gasto=gasto, imagen=IMAGEN)

    assert len(llamadas) == 1 and salida["hubo_a2a"] is True
    assert salida["veredicto"]["decision"] == "observar"
    assert revisar_gasto.registros_de_prueba == [(gasto["id"], "observar")]  # no «aprobar»
    assert filas[0]["ruta"] == "revisar_gasto"
