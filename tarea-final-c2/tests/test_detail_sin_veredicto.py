"""El `detail` de GET /registro/{id} cuando la ejecución termina sin veredicto (Alex). Sin Gemini.

Cada caso que el código ya distingue tiene su mensaje: tope de pasos, hora límite, falla de una
herramienta, el modelo cerró sin veredicto, falla del modelo, tope global y flujo no implementado.
"""

import pytest

from src.comun import errores
from src.principal import en_segundo_plano
from src.principal import grafo as modulo_grafo
from src.principal.flujos import revisar_gasto as modulo_react
from tests.test_chat_async import CABECERAS, cliente, esperar_fin  # noqa: F401  (fixture del cliente)
from tests.test_grafo import filas, ruta_fija  # noqa: F401  (fixtures del grafo)
from tests.test_react_mcp import revisar_gasto  # noqa: F401  (fixture: ReAct con registro en memoria)

ID = "8f0c0000-0000-4000-8000-000000000000"
SIN_VEREDICTO = "No puedo cerrar esta revisión: no se emitió un veredicto estructurado válido para el gasto."
FALLA_FONDO = [{"herramienta": "consultar_fondo", "motivo": "consultar_fondo: el fondo FR-999 no existe."}]


def _error(respuesta, ruta="revisar_gasto", **extra):
    return {"ruta": ruta, "estado_final": "error", "veredicto": None, "respuesta": respuesta, **extra}


def _detail(resultado):
    return en_segundo_plano.detalle_sin_veredicto(resultado, ID, 90.0)


# --- Mensajes por caso (sin red) ------------------------------------------------


def test_tope_de_pasos():
    detail = _detail(_error("Me detuve: alcancé el máximo de 6 pasos sin una decisión final."))
    assert detail == (f"No se pudo completar la revisión: el agente llegó al máximo de 6 pasos sin emitir un "
                      f"veredicto. El gasto no fue registrado. (id_ejecucion: {ID})")


def test_hora_limite_del_react():
    detail = _detail(_error(modulo_react.MENSAJE_TIEMPO_AGOTADO))
    assert "se acabó el tiempo máximo de la ejecución (90 s)" in detail
    assert "El gasto no fue registrado. El fondo no cambió." in detail


def test_falla_de_una_herramienta():
    detail = _detail(_error(SIN_VEREDICTO, herramientas_con_error=FALLA_FONDO))
    assert detail == (f"No se pudo completar la revisión: la herramienta consultar_fondo falló (consultar_fondo: "
                      f"el fondo FR-999 no existe.). El gasto no fue registrado. (id_ejecucion: {ID})")


def test_falla_de_varias_herramientas_sin_motivo():
    fallidas = [{"herramienta": "buscar_politica", "motivo": None}, {"herramienta": "consultar_fondo", "motivo": None}]
    detail = _detail(_error(SIN_VEREDICTO, herramientas_con_error=fallidas))
    assert "las herramientas buscar_politica y consultar_fondo fallaron. El gasto no fue registrado." in detail


def test_tope_de_pasos_despues_de_una_herramienta_que_fallo():
    detail = _detail(_error("Me detuve: alcancé el máximo de 6 pasos…", herramientas_con_error=FALLA_FONDO))
    assert "llegó al máximo de 6 pasos sin emitir un veredicto. Antes, la herramienta consultar_fondo falló" in detail


def test_el_modelo_cerro_sin_veredicto():
    detail = _detail(_error(SIN_VEREDICTO))
    assert detail == (f"No se pudo completar la revisión: el modelo terminó sin emitir un veredicto. "
                      f"El gasto no fue registrado. (id_ejecucion: {ID})")


def test_tope_global_no_afirma_que_no_se_registro():
    # El ReAct pudo alcanzar a registrar justo antes del tope: no se dice que el gasto no quedó.
    detail = _detail(_error(modulo_grafo.mensaje_tope(90)))
    assert "superó el tiempo máximo de 90 s" in detail and "No se entrega ningún veredicto" in detail
    assert "no fue registrado" not in detail


def test_flujo_no_implementado():
    detail = _detail(_error("Flujo consulta_politica todavía no implementado.", ruta="consulta_politica"))
    assert detail.startswith("No se pudo completar: el flujo consulta_politica todavía no está implementado.")


def test_otra_ruta_usa_la_respuesta_sin_hablar_de_gastos():
    detail = _detail(_error("No encontré respaldo en la política para esa pregunta.\nDetalle", ruta="consulta_politica"))
    assert detail.startswith("No se pudo completar la solicitud: No encontré respaldo en la política para esa pregunta.")
    assert "gasto" not in detail


@pytest.mark.parametrize("resultado", [
    {"estado_final": "ok", "veredicto": {"decision": "aprobar"}},
    {"estado_final": "fallback", "veredicto": {"decision": "observar"}},
    {"estado_final": "bloqueado", "veredicto": None, "respuesta": "Bloqueé la solicitud…"},
    {"estado_final": "ok", "veredicto": None, "respuesta": "Para revisar el gasto necesito sus datos…"},
])
def test_sin_detail_si_no_termino_en_error_sin_veredicto(resultado):
    assert _detail({"ruta": "revisar_gasto", **resultado}) is None


def test_falla_del_modelo_en_la_revision():
    error = modulo_grafo.ErrorDeEjecucion(errores.MENSAJE_SIN_CUOTA, ID, ruta="revisar_gasto", del_modelo=True)
    detail = en_segundo_plano.detalle_de_falla(error, ID)
    assert detail.startswith("No se pudo completar la revisión: el modelo no respondió. Gemini no tiene cuota")
    assert detail.endswith(f"El gasto no fue registrado. (id_ejecucion: {ID})")


def test_falla_del_modelo_antes_de_elegir_ruta():
    error = modulo_grafo.ErrorDeEjecucion(errores.MENSAJE_NO_DISPONIBLE, ID, ruta=None, del_modelo=True)
    detail = en_segundo_plano.detalle_de_falla(error, ID)
    assert detail.startswith("No se pudo completar la solicitud: el modelo no respondió.") and "gasto" not in detail


def test_falla_de_otro_servicio_en_la_revision_no_afirma_que_no_se_registro():
    error = modulo_grafo.ErrorDeEjecucion("No se pudo completar la consulta: Falta DATABASE_URL", ID, ruta="revisar_gasto")
    detail = en_segundo_plano.detalle_de_falla(error, ID)
    assert detail == f"No se pudo completar la revisión: Falta DATABASE_URL. No se entregó ningún veredicto. (id_ejecucion: {ID})"


def test_el_motivo_de_la_herramienta_no_trae_claves_ni_el_envoltorio():
    contenido = ("Error: ToolException('consultar_fondo (MCP): falló con la clave AIzaSyA1234567890abcdefghijklmnop')"
                 "\n Please fix your mistakes.")
    motivo = modulo_grafo._motivo_de_herramienta(contenido)
    assert "AIza" not in motivo and "Please fix" not in motivo and motivo.startswith("consultar_fondo (MCP): falló")


@pytest.mark.parametrize(("mensaje", "del_modelo"), [
    (errores.MENSAJE_SIN_CUOTA, True), (errores.MENSAJE_CLAVE_GEMINI, True), (errores.MENSAJE_NO_DISPONIBLE, True),
    (errores.MENSAJE_TIEMPO, False), (errores.MENSAJE_SIN_CONEXION, False), ("No se pudo completar la consulta: x", False),
])
def test_solo_los_mensajes_de_gemini_cuentan_como_falla_del_modelo(mensaje, del_modelo):
    # «Tiempo agotado» y «sin conexión» también los dan Postgres o un agente: no se culpa al modelo.
    assert (mensaje in modulo_grafo._MENSAJES_DEL_MODELO) is del_modelo


# --- Punta a punta: /chat asíncrono con el ReAct real y un modelo guionado ---------


@pytest.fixture
def react_guionado(monkeypatch, revisar_gasto, ruta_fija):  # noqa: F811
    """El ReAct de Matías tal cual, con el LLM guionado y sin modelo de respaldo."""
    from tests.test_seguridad import LLMFalso

    def preparar(pasos, llm=None):
        monkeypatch.setattr(revisar_gasto, "obtener_llm", lambda: llm or LLMFalso(pasos))
        monkeypatch.setattr(revisar_gasto, "_obtener_respaldo", lambda: None)
        monkeypatch.setattr(modulo_grafo, "_AGENTE_REACT", None)  # se compila con el LLM guionado
        ruta_fija("revisar_gasto")

    return preparar


def _gasto():
    from tests.test_react_mcp import _caso

    return dict(_caso("GS-01")["gasto"])


def _correr(cliente, gasto):  # noqa: F811
    aceptado = cliente.post("/chat", json={"texto": "Revisa este gasto.", "gasto": gasto}, headers=CABECERAS).json()
    return aceptado["id_ejecucion"], esperar_fin(cliente, aceptado["id_ejecucion"], segundos=30)


def test_chat_herramienta_que_falla_explica_cual(cliente, filas, react_guionado, revisar_gasto):  # noqa: F811
    from langchain_core.messages import AIMessage

    from tests.test_seguridad import _pedir

    # consultar_fondo con un fondo que no existe (MCP real) y después el modelo cierra sin veredicto.
    react_guionado([_pedir(("consultar_fondo", {"id_fondo": "FR-999"})), AIMessage("No pude revisar el fondo.")])
    id_ejecucion, datos = _correr(cliente, _gasto())

    assert datos["estado"] == "error" and not datos["resultado"].get("veredicto")
    assert datos["resultado"]["herramientas_con_error"][0]["herramienta"] == "consultar_fondo"
    assert datos["detail"].startswith("No se pudo completar la revisión: la herramienta consultar_fondo falló (")
    assert "FR-999" in datos["detail"] and "Please fix" not in datos["detail"]
    assert datos["detail"].endswith(f"El gasto no fue registrado. (id_ejecucion: {id_ejecucion})")
    assert revisar_gasto.registros_de_prueba == []  # de verdad no se registró


def test_chat_tope_de_pasos(cliente, filas, react_guionado, revisar_gasto, monkeypatch):  # noqa: F811
    from tests.test_seguridad import _pedir

    gasto = _gasto()
    monkeypatch.setattr(revisar_gasto, "MAX_PASOS", 2)
    validar = ("validar_gasto", {"gasto": gasto, "politica": "P02", "categoria": "Peaje"})
    react_guionado([_pedir(validar) for _ in range(3)])  # nunca emite veredicto
    id_ejecucion, datos = _correr(cliente, gasto)

    assert datos["estado"] == "error"
    assert datos["detail"] == (f"No se pudo completar la revisión: el agente llegó al máximo de 2 pasos sin emitir "
                               f"un veredicto. El gasto no fue registrado. (id_ejecucion: {id_ejecucion})")
    assert "herramientas_con_error" not in datos["resultado"]  # validar_gasto respondió bien
    assert revisar_gasto.registros_de_prueba == []


def test_chat_falla_del_modelo_en_el_react(cliente, filas, react_guionado, revisar_gasto):  # noqa: F811
    class SinCuota:
        def bind_tools(self, _herramientas):
            return self

        def invoke(self, _mensajes):
            raise RuntimeError("429 RESOURCE_EXHAUSTED: quota exceeded")

    react_guionado([], llm=SinCuota())
    id_ejecucion, datos = _correr(cliente, _gasto())

    assert datos["estado"] == "error" and datos["resultado"] is None
    assert datos["detail"].startswith("No se pudo completar la revisión: el modelo no respondió. Gemini no tiene cuota")
    assert datos["detail"].endswith(f"El gasto no fue registrado. (id_ejecucion: {id_ejecucion})")
    assert revisar_gasto.registros_de_prueba == []
