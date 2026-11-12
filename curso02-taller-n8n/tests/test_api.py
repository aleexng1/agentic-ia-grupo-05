"""Pruebas de la API sin llamar al modelo: el grafo se reemplaza por uno falso.

La clave se fija con monkeypatch, así que no se usa la API_KEY real de .env.
"""

import pytest
from fastapi.testclient import TestClient

from api.app import app

CLAVE = "clave-de-prueba"
CON_CLAVE = {"X-API-Key": CLAVE}
BODY = {"user_id": "u1", "texto": "hola"}


class GrafoFalso:
    def __init__(self, falla: bool = False):
        self.falla = falla
        self.thread_ids = []

    def invoke(self, entrada, config):
        self.thread_ids.append(config["configurable"]["thread_id"])
        if self.falla:
            raise RuntimeError("detalle interno con GOOGLE_API_KEY=secreto")
        return {"ruta": "preventa", "motivo": "porque sí", "respuesta": f"eco: {entrada['mensaje']}"}


@pytest.fixture
def cliente(monkeypatch):
    monkeypatch.setenv("API_KEY", CLAVE)
    with TestClient(app) as c:
        app.state.grafo = GrafoFalso()
        yield c


# ── /health ──────────────────────────────────────────────────────────────────

def test_health_sin_clave(cliente):
    r = cliente.get("/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True
    assert r.json()["modelo"]


# ── /chat: autenticación ─────────────────────────────────────────────────────

def test_chat_sin_clave_da_401(cliente):
    falso = app.state.grafo
    r = cliente.post("/chat", json=BODY)
    assert r.status_code == 401
    assert "X-API-Key" in r.json()["detail"]
    assert falso.thread_ids == []  # no llegó al modelo


def test_chat_con_clave_da_200(cliente):
    r = cliente.post("/chat", json=BODY, headers=CON_CLAVE)
    assert r.status_code == 200
    assert set(r.json()) == {"ruta", "motivo", "respuesta"}


def test_chat_con_clave_incorrecta_da_401(cliente):
    r = cliente.post("/chat", json=BODY, headers={"X-API-Key": "otra-clave"})
    assert r.status_code == 401


def test_chat_sin_api_key_en_servidor_rechaza_todo(cliente, monkeypatch):
    monkeypatch.delenv("API_KEY")
    r = cliente.post("/chat", json=BODY, headers=CON_CLAVE)
    assert r.status_code == 401


# ── /chat: contrato ──────────────────────────────────────────────────────────

def test_chat_usa_user_id_como_thread(cliente):
    falso = app.state.grafo
    r = cliente.post("/chat", json=BODY, headers=CON_CLAVE)
    assert r.status_code == 200
    assert r.json() == {"ruta": "preventa", "motivo": "porque sí", "respuesta": "eco: hola"}
    assert falso.thread_ids == ["u1"]


@pytest.mark.parametrize("body", [{"user_id": "u1"}, {"texto": "hola"}, {"user_id": "u1", "texto": ""}])
def test_chat_body_invalido_da_422(cliente, body):
    assert cliente.post("/chat", json=body, headers=CON_CLAVE).status_code == 422


def test_chat_modelo_falla_da_502_sin_detalles(cliente):
    app.state.grafo = GrafoFalso(falla=True)
    r = cliente.post("/chat", json=BODY, headers=CON_CLAVE)
    assert r.status_code == 502
    assert "secreto" not in r.text
    assert "Traceback" not in r.text
