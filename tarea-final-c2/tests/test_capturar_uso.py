"""Pruebas del script de evidencia A2A «uso del resultado» (evidencias/a2a/capturar_uso.py).

Solo prueban la lectura de trazas y la atribución de «dónde se usó»: la evidencia en sí se captura
contra los servicios reales (ver el docstring del script). Sin Gemini, sin red y sin Postgres.
"""

import importlib.util
import json
from pathlib import Path

import pytest

RUTA = Path(__file__).resolve().parents[1] / "evidencias" / "a2a" / "capturar_uso.py"


@pytest.fixture(scope="module")
def uso():
    especificacion = importlib.util.spec_from_file_location("capturar_uso_prueba", RUTA)
    modulo = importlib.util.module_from_spec(especificacion)
    especificacion.loader.exec_module(modulo)
    return modulo


def _bloque(evento, datos):
    return [f"── [{evento}] ──", *json.dumps(datos, ensure_ascii=False, indent=2).splitlines()]


CUADRA_TODO = {"disponible": True, "cuadra": dict.fromkeys(("monto", "fecha", "rut_emisor", "folio", "categoria"), "sí")}
NO_CUADRA_MONTO = {"disponible": True, "cuadra": {**CUADRA_TODO["cuadra"], "monto": "no"}}
PROPONE_APROBAR = {"paso": 5, "pide_herramientas": [{"name": "emitir_veredicto", "args": {"decision": "aprobar"}}]}


def test_extrae_trazas_entre_lineas_del_log(uso):
    lineas = [
        "2026-11-25 21:42:00 INFO    [tarea_final] a2a · encargo → http://127.0.0.1:8001",
        *_bloque("llm", PROPONE_APROBAR),
        "INFO:     127.0.0.1:5000 - \"GET /registro/x HTTP/1.1\" 200 OK",
        *_bloque("juez", {"valido": True, "evaluado": True}),
    ]
    trazas = uso.extraer_trazas(lineas)
    assert [evento for evento, _ in trazas] == ["llm", "juez"]
    assert uso.propuesta_del_react(trazas) == {"decision": "aprobar"}


def test_atribuye_el_cambio_al_piso_por_verificacion(uso):
    trazas = [("llm", PROPONE_APROBAR), ("juez", {"valido": True, "evaluado": True}),
              ("piso_verificacion", {"motivo": "la boleta no coincide con lo declarado en monto"})]
    linea = uso.donde_se_uso(NO_CUADRA_MONTO, {"decision": "aprobar"}, trazas, "")
    assert "piso por verificación de `nodo_cerrar`" in linea and "monto" in linea


def test_si_el_juez_bajo_antes_no_se_atribuye_al_verificador(uso):
    # Corrida real del 2026-11-25 sin Redis: el juez no validó y el piso no tuvo que actuar.
    trazas = [("llm", PROPONE_APROBAR), ("juez", {"valido": False, "evaluado": True, "razon": "sin fragmentos"})]
    linea = uso.donde_se_uso(CUADRA_TODO, {"decision": "aprobar"}, trazas, "")
    assert "NO fue lo que decidió" in linea and "sin fragmentos" in linea


def test_todo_cuadra_y_el_juez_valida(uso):
    trazas = [("llm", PROPONE_APROBAR), ("juez", {"valido": True, "evaluado": True})]
    linea = uso.donde_se_uso(CUADRA_TODO, {"decision": "aprobar"}, trazas, "")
    assert "no cambió nada" in linea and "aprobar" in linea


@pytest.mark.parametrize("valor,esperado", [
    ("", False),
    ("redis://usuario:contrasena@host-de-ejemplo:6379", False),
    ("redis://default:x@redis-12345.ejemplo.cloud:6379", True),
])
def test_redis_configurado(uso, monkeypatch, valor, esperado):
    monkeypatch.setenv("REDIS_URL", valor)
    assert uso.redis_configurado() is esperado
