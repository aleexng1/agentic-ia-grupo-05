"""Pruebas del verificador A2A y de delegar_verificador (Alex).

- Sin LLM: comparación y normalización, encargo inválido, FORZAR_FALLO_A2A=1, verificador
  apagado, y A2A de punta a punta por HTTP real (verificador levantado con uvicorn en un hilo)
  con el lector de imagen reemplazado: éxito, timeout, clave rechazada y la imagen fuera del log.
- Con LLM (necesita_llm): las 4 boletas ficticias de datos/boletas/ con Gemini.
"""

import asyncio
import base64
import json
import logging
import os
import socket
import threading
import time

import pytest
import uvicorn

from src.comun.config import CARPETA_PROYECTO
from src.principal.herramientas import delegar_verificador as modulo_delegar
from src.verificador import agente
from src.verificador.agente import EncargoInvalido, LecturaBoleta, comparar, leer_encargo

CARPETA_BOLETAS = CARPETA_PROYECTO / "datos" / "boletas"
DECLARADO = json.loads((CARPETA_BOLETAS / "declarado.json").read_text(encoding="utf-8"))["boletas"]


def _imagen(archivo: str) -> dict:
    return {"mime_type": "image/png", "datos_base64": base64.b64encode((CARPETA_BOLETAS / archivo).read_bytes()).decode()}


def _puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


# ---------------------------------------------------------------------------
# Comparación (sin LLM)
# ---------------------------------------------------------------------------

DECLARADO_01 = DECLARADO[0]["declarado"]


def test_todo_coincide():
    lectura = LecturaBoleta(legible=True, monto_total=45000, fecha_emision="02-10-2026", rut_emisor="11111111-1",
                            folio="123", categoria_gasto="combustible", categoria_compatible=True, confianza=0.95)
    respuesta = comparar(lectura, DECLARADO_01)
    assert respuesta["cuadra"] == {c: "sí" for c in ("monto", "fecha", "rut_emisor", "folio", "categoria")}
    assert respuesta["leido"]["fecha"] == "2026-10-02" and respuesta["leido"]["monto"] == 45000


def test_lo_no_leido_va_null_y_no_cuadra():
    lectura = LecturaBoleta(legible=True, monto_total=45000, fecha_emision=None, rut_emisor=None, folio=None,
                            categoria_gasto=None, categoria_compatible=None, confianza=0.6)
    respuesta = comparar(lectura, DECLARADO_01)
    assert respuesta["leido"]["fecha"] is None and respuesta["cuadra"]["fecha"] == "no"
    assert respuesta["cuadra"]["categoria"] == "no" and respuesta["cuadra"]["monto"] == "sí"


def test_ilegible_no_lee_nada_aunque_el_modelo_devuelva_valores():
    lectura = LecturaBoleta(legible=False, monto_total=45000, fecha_emision="2026-10-02", confianza=0.9,
                            categoria_compatible=True, categoria_gasto="combustible")
    respuesta = comparar(lectura, DECLARADO_01)
    assert all(valor is None for valor in respuesta["leido"].values())
    assert set(respuesta["cuadra"].values()) == {"no"} and respuesta["confianza"] <= 0.2


def test_sin_dato_declarado_no_cuadra():
    lectura = LecturaBoleta(legible=True, monto_total=45000, folio="000123", confianza=0.9)
    respuesta = comparar(lectura, {**DECLARADO_01, "folio": None})
    assert respuesta["cuadra"]["folio"] == "no" and "Sin dato declarado" in respuesta["observaciones"]


def test_encargo_sin_imagen_o_con_tipo_raro_es_invalido():
    partes = modulo_delegar._partes(b"x", "image/png", DECLARADO_01)
    with pytest.raises(EncargoInvalido, match="imagen"):
        leer_encargo(partes[1:])
    partes[0].media_type = "application/pdf"
    with pytest.raises(EncargoInvalido, match="no admitido"):
        leer_encargo(partes)
    imagen, tipo, declarado = leer_encargo(modulo_delegar._partes(b"x", "image/png", DECLARADO_01))
    assert imagen == b"x" and tipo == "image/png" and declarado["monto"] == 45000


# ---------------------------------------------------------------------------
# delegar_verificador sin red
# ---------------------------------------------------------------------------


def test_forzar_fallo_no_llama_al_verificador(monkeypatch):
    monkeypatch.setenv("FORZAR_FALLO_A2A", "1")

    async def no_llamar(*args, **kwargs):
        raise AssertionError("no debía llamar al verificador")

    monkeypatch.setattr("src.comun.cliente_a2a.enviar_partes", no_llamar)
    respuesta = asyncio.run(modulo_delegar.delegar_verificador(_imagen("boleta-01-cuadra.png"), DECLARADO_01))
    assert respuesta == {"disponible": False, "tipo_fallo": "forzado",
                         "motivo": "FORZAR_FALLO_A2A=1: se simuló que el verificador no responde"}


def test_verificador_apagado_da_sin_conexion(monkeypatch):
    monkeypatch.setenv("URL_VERIFICADOR", f"http://127.0.0.1:{_puerto_libre()}")
    monkeypatch.setenv("TIMEOUT_A2A_SEG", "3")
    respuesta = asyncio.run(modulo_delegar.delegar_verificador(_imagen("boleta-01-cuadra.png"), DECLARADO_01))
    assert respuesta["disponible"] is False and respuesta["tipo_fallo"] == "sin_conexion"
    assert set(respuesta) == {"disponible", "tipo_fallo", "motivo"}  # sin campos leídos


def test_imagen_mal_formada_no_sale(monkeypatch):
    respuesta = asyncio.run(modulo_delegar.delegar_verificador({"mime_type": "image/png", "datos_base64": "%%%"}, DECLARADO_01))
    assert respuesta["tipo_fallo"] == "encargo_invalido"


def test_respuesta_que_dice_cuadra_sin_leer_es_invalida():
    from a2a.types import Part
    from google.protobuf import struct_pb2

    valor = struct_pb2.Value()
    valor.struct_value.update({"leido": dict.fromkeys(agente.CAMPOS_COMPARADOS), "confianza": 0.9,
                               "cuadra": dict.fromkeys(agente.CAMPOS_COMPARADOS, "sí"), "observaciones": ""})
    assert modulo_delegar.validar_respuesta([Part(data=valor)]) is None


# ---------------------------------------------------------------------------
# A2A de punta a punta por HTTP (verificador real, lector de imagen falso)
# ---------------------------------------------------------------------------


@pytest.fixture
def verificador(monkeypatch):
    """Levanta src.verificador.app en un puerto libre y apunta URL_VERIFICADOR a él."""
    from src.verificador.app import app

    puerto = _puerto_libre()
    servidor = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=puerto, log_level="warning"))
    hilo = threading.Thread(target=servidor.run, daemon=True)
    hilo.start()
    for _ in range(100):
        if servidor.started:
            break
        time.sleep(0.05)
    monkeypatch.setenv("URL_VERIFICADOR", f"http://127.0.0.1:{puerto}")
    monkeypatch.setenv("TIMEOUT_A2A_SEG", "10")
    yield
    servidor.should_exit = True
    hilo.join(timeout=5)


def _lector_falso(monkeypatch, lectura: LecturaBoleta, demora: float = 0):
    def leer(imagen, tipo, categoria):
        time.sleep(demora)
        assert isinstance(imagen, bytes) and tipo == "image/png"
        return lectura

    monkeypatch.setattr(agente, "leer_imagen", leer)


@pytest.fixture
def lineas_log():
    lineas = []

    class Captura(logging.Handler):
        def emit(self, registro):
            lineas.append(registro.getMessage())

    manejador = Captura()
    logging.getLogger("tarea_final").addHandler(manejador)
    yield lineas
    logging.getLogger("tarea_final").removeHandler(manejador)


def test_a2a_de_punta_a_punta(verificador, monkeypatch, lineas_log):
    _lector_falso(monkeypatch, LecturaBoleta(legible=True, monto_total=62000, fecha_emision="2026-10-14",
                                             rut_emisor="22.222.222-2", folio="004512", categoria_gasto="hotel",
                                             categoria_compatible=True, confianza=0.9))
    imagen = _imagen("boleta-02-monto-distinto.png")
    respuesta = asyncio.run(modulo_delegar.delegar_verificador(imagen, DECLARADO[1]["declarado"]))
    assert respuesta["disponible"] is True
    assert respuesta["cuadra"] == DECLARADO[1]["esperado_cuadra"]
    assert respuesta["leido"]["monto"] == 62000 and isinstance(respuesta["leido"]["monto"], int)
    texto_log = "\n".join(lineas_log)
    assert "verificador · encargo" in texto_log and "sha256:" in texto_log
    assert imagen["datos_base64"][:40] not in texto_log  # la imagen nunca va al log


def test_a2a_timeout_devuelve_error_estructurado(verificador, monkeypatch):
    monkeypatch.setenv("TIMEOUT_A2A_SEG", "1")
    _lector_falso(monkeypatch, LecturaBoleta(legible=True, confianza=0.5), demora=3)
    inicio = time.monotonic()
    respuesta = asyncio.run(modulo_delegar.delegar_verificador(_imagen("boleta-01-cuadra.png"), DECLARADO_01))
    assert respuesta["tipo_fallo"] == "timeout" and time.monotonic() - inicio < 2.5


def test_a2a_con_clave_incorrecta_es_rechazado(verificador, monkeypatch):
    monkeypatch.setattr(modulo_delegar, "_cabeceras", lambda: {"X-API-Key": "clave-equivocada"})
    respuesta = asyncio.run(modulo_delegar.delegar_verificador(_imagen("boleta-01-cuadra.png"), DECLARADO_01))
    assert respuesta["disponible"] is False and respuesta["tipo_fallo"] == "rechazado"


def test_ficha_publica_la_skill(verificador):
    import httpx

    ficha = httpx.get(os.environ["URL_VERIFICADOR"] + "/.well-known/agent-card.json").json()
    assert ficha["skills"][0]["id"] == "verificar_boleta"
    assert "application/json" in ficha["defaultOutputModes"]


# ---------------------------------------------------------------------------
# Con Gemini: las 4 boletas ficticias
# ---------------------------------------------------------------------------


@pytest.mark.necesita_llm
@pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY", "").strip(), reason="falta GOOGLE_API_KEY (pendiente)")
@pytest.mark.parametrize("boleta", DECLARADO, ids=[b["caso"] for b in DECLARADO])
def test_boletas_ficticias_con_gemini(boleta):
    respuesta = agente.verificar_boleta(_imagen(boleta["archivo"]), boleta["declarado"])
    print(boleta["archivo"], json.dumps(respuesta, ensure_ascii=False))
    if boleta["caso"] == "ilegible":
        assert respuesta["cuadra"]["monto"] == "no" and respuesta["cuadra"]["fecha"] == "no"
    else:
        assert respuesta["cuadra"] == boleta["esperado_cuadra"]
