"""Pendientes del issue #100 (Matías): piso por verificación antes de registrar, "ok" solo con
veredicto y modelo de respaldo en el ReAct y el juez. Sin red, Gemini, Redis ni Postgres.
"""

import pytest
from langchain_core.messages import AIMessage

from src.principal import juez
from tests.test_react_mcp import _caso, revisar_gasto  # noqa: F401  (revisar_gasto es un fixture)
from tests.test_seguridad import LLMFalso, _pedir

CUADRA_TODO = {"monto": "sí", "fecha": "sí", "rut_emisor": "sí", "folio": "sí", "categoria": "sí"}


def _guion_aprobar_gs01():
    """El modelo valida GS-01 y propone aprobar (lo esperado sin verificación)."""
    turno = _caso("GS-01")
    gasto, esperado = turno["gasto"], turno["esperado"]
    pasos = [
        _pedir(("validar_gasto", {"gasto": gasto, "politica": esperado["politica"], "categoria": esperado["categoria"]})),
        _pedir(
            (
                "emitir_veredicto",
                {
                    "decision": "aprobar",
                    "politica": esperado["politica"],
                    "categoria": esperado["categoria"],
                    "cuenta": esperado["cuenta"],
                    "motivo": "Peaje de viaje interno con boleta y dentro de plazo (P02).",
                },
            )
        ),
    ]
    return turno, pasos


def _revisar(revisar_gasto, monkeypatch, verificacion, hilo):  # noqa: F811
    turno, pasos = _guion_aprobar_gs01()
    monkeypatch.setattr(revisar_gasto, "obtener_llm", lambda: LLMFalso(pasos))
    agente = revisar_gasto.construir_agente()
    resultado = revisar_gasto.revisar_caso(
        agente, turno["mensaje"], hilo, turno["gasto"], verificacion=verificacion
    )
    estado = agente.get_state({"configurable": {"thread_id": hilo}}).values
    return turno, resultado, estado


# ---------------------------------------------------------------------------
# 1. Piso por verificación ANTES de registrar_veredicto
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "verificacion, fragmento",
    [
        ({"disponible": True, "cuadra": {**CUADRA_TODO, "monto": "no"}, "confianza": 0.9}, "no coincide con lo declarado en monto"),
        ({"disponible": False, "motivo": "timeout"}, "no se pudo verificar la boleta"),
    ],
)
def test_boleta_que_no_cuadra_registra_observar_y_no_descuenta(revisar_gasto, monkeypatch, verificacion, fragmento):  # noqa: F811
    turno, resultado, estado = _revisar(revisar_gasto, monkeypatch, verificacion, f"hilo-piso-{fragmento[:6]}")

    assert resultado["veredicto"]["decision"] == "observar"
    assert fragmento in resultado["veredicto"]["motivo"]
    # Lo registrado es lo mismo que se responde (antes quedaba «aprobar» en el registro).
    assert revisar_gasto.registros_de_prueba == [(turno["gasto"]["id"], "observar")]
    assert estado["fondo"]["saldo_actual"] == estado["fondo"]["saldo_inicial"], "no se descuenta del fondo"
    assert resultado["respuesta"].startswith("Decisión: OBSERVAR")
    assert resultado["estado_final"] == "ok"


def test_boleta_que_cuadra_no_cambia_la_aprobacion(revisar_gasto, monkeypatch):  # noqa: F811
    verificacion = {"disponible": True, "cuadra": CUADRA_TODO, "confianza": 0.95}
    turno, resultado, _ = _revisar(revisar_gasto, monkeypatch, verificacion, "hilo-cuadra")
    assert resultado["veredicto"]["decision"] == "aprobar"
    assert revisar_gasto.registros_de_prueba == [(turno["gasto"]["id"], "aprobar")]


def test_sin_boleta_no_aplica_el_piso(revisar_gasto, monkeypatch):  # noqa: F811
    _, resultado, _ = _revisar(revisar_gasto, monkeypatch, None, "hilo-sin-boleta")
    assert resultado["veredicto"]["decision"] == "aprobar"


def test_la_verificacion_no_se_hereda_al_turno_siguiente(revisar_gasto, monkeypatch):  # noqa: F811
    turno, pasos = _guion_aprobar_gs01()
    _, pasos_2 = _guion_aprobar_gs01()
    monkeypatch.setattr(revisar_gasto, "obtener_llm", lambda: LLMFalso([*pasos, *pasos_2]))
    agente = revisar_gasto.construir_agente()
    mala = {"disponible": False, "motivo": "timeout"}
    revisar_gasto.revisar_caso(agente, "Revisa.", "hilo-h", turno["gasto"], verificacion=mala)
    segundo = revisar_gasto.revisar_caso(agente, "Revisa otra vez.", "hilo-h", {**turno["gasto"], "id": "G-0102"})
    assert segundo["veredicto"]["decision"] == "aprobar"


def test_motivo_piso_verificacion_solo_endurece():
    motivo = revisar_gasto_modulo().motivo_piso_verificacion
    assert motivo(None) is None
    assert motivo({"disponible": True, "cuadra": CUADRA_TODO}) is None
    assert "fecha" in motivo({"disponible": True, "cuadra": {**CUADRA_TODO, "fecha": "no"}})
    assert "no se pudo verificar" in motivo({"disponible": False})


def revisar_gasto_modulo():
    from src.principal.flujos import revisar_gasto as modulo

    return modulo


# ---------------------------------------------------------------------------
# 2. "ok" solo con veredicto
# ---------------------------------------------------------------------------


def test_cerrar_sin_veredicto_es_error_y_no_ok(revisar_gasto, monkeypatch):  # noqa: F811
    """Caso V-04 (boleta ilegible): el modelo responde texto sin emitir_veredicto."""
    gasto = _caso("GS-01")["gasto"]
    llm = LLMFalso([AIMessage("No puedo leer la boleta, ¿me envías una foto más nítida?")])
    monkeypatch.setattr(revisar_gasto, "obtener_llm", lambda: llm)
    agente = revisar_gasto.construir_agente()

    resultado = revisar_gasto.revisar_caso(agente, "Revisa este gasto.", "hilo-v04", gasto)

    assert resultado["veredicto"] is None
    assert resultado["estado_final"] == "error"
    assert revisar_gasto.registros_de_prueba == []


# ---------------------------------------------------------------------------
# 3. Modelo de respaldo → "fallback"
# ---------------------------------------------------------------------------


class LLMCaido:
    """Modelo principal que falla siempre (como una cuota agotada)."""

    def __init__(self):
        self.llamadas = 0

    def bind_tools(self, _herramientas):
        return self

    def invoke(self, _mensajes):
        self.llamadas += 1
        raise RuntimeError("429 RESOURCE_EXHAUSTED")


def test_si_responde_el_respaldo_el_turno_es_fallback(revisar_gasto, monkeypatch):  # noqa: F811
    turno, pasos = _guion_aprobar_gs01()
    caido, respaldo = LLMCaido(), LLMFalso(pasos)
    monkeypatch.setattr(revisar_gasto, "obtener_llm", lambda: caido)
    monkeypatch.setattr(revisar_gasto, "_obtener_respaldo", lambda: respaldo)
    agente = revisar_gasto.construir_agente()

    resultado = revisar_gasto.revisar_caso(agente, turno["mensaje"], "hilo-respaldo", turno["gasto"])

    assert resultado["estado_final"] == "fallback"
    assert resultado["veredicto"]["decision"] == "aprobar", "el respaldo trabaja igual, no inventa"
    assert caido.llamadas == 2 and respaldo.llamadas == 2


def test_si_fallan_los_dos_modelos_el_error_sube(revisar_gasto, monkeypatch):  # noqa: F811
    monkeypatch.setattr(revisar_gasto, "obtener_llm", lambda: LLMCaido())
    monkeypatch.setattr(revisar_gasto, "_obtener_respaldo", lambda: LLMCaido())
    agente = revisar_gasto.construir_agente()
    with pytest.raises(RuntimeError, match="RESOURCE_EXHAUSTED"):
        revisar_gasto.revisar_caso(agente, "Revisa.", "hilo-caidos", _caso("GS-01")["gasto"])


def test_juez_usa_el_respaldo_y_lo_avisa(monkeypatch):
    class Estructurado:
        def __init__(self, falla):
            self.falla = falla

        def invoke(self, _mensajes):
            if self.falla:
                raise RuntimeError("503")
            return {"valido": True, "razon": "Coincide con la validación."}

    class Modelo:
        def __init__(self, falla):
            self.falla = falla

        def with_structured_output(self, *_a, **_k):
            return Estructurado(self.falla)

    monkeypatch.setattr(juez, "_modelos_juez", lambda: [lambda: Modelo(True), lambda: Modelo(False)])
    resultado = juez.juzgar_con_validacion({}, {}, {}, {})
    assert resultado == {"valido": True, "razon": "Coincide con la validación.", "evaluado": True, "uso_respaldo": True}

    monkeypatch.setattr(juez, "_modelos_juez", lambda: [lambda: Modelo(True), lambda: Modelo(True)])
    assert juez.juzgar_con_validacion({}, {}, {}, {})["evaluado"] is False


def test_el_juez_con_respaldo_marca_fallback(revisar_gasto, monkeypatch):  # noqa: F811
    monkeypatch.setattr(
        revisar_gasto,
        "juzgar_con_validacion",
        lambda *_a: {"valido": True, "razon": "ok", "evaluado": True, "uso_respaldo": True},
    )
    turno, resultado, _ = _revisar(revisar_gasto, monkeypatch, None, "hilo-juez-respaldo")
    assert resultado["estado_final"] == "fallback"
