"""Pruebas de la API sin llamar al modelo: el grafo se reemplaza por uno falso."""

import pytest
from fastapi.testclient import TestClient

from api.app import app


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
def cliente():
    with TestClient(app) as c:
        yield c


def test_health(cliente):
    r = cliente.get("/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True
    assert r.json()["modelo"]


def test_chat_usa_user_id_como_thread(cliente):
    falso = GrafoFalso()
    app.state.grafo = falso
    r = cliente.post("/chat", json={"user_id": "u1", "texto": "hola"})
    assert r.status_code == 200
    assert r.json() == {"ruta": "preventa", "motivo": "porque sí", "respuesta": "eco: hola"}
    assert falso.thread_ids == ["u1"]


@pytest.mark.parametrize("body", [{"user_id": "u1"}, {"texto": "hola"}, {"user_id": "u1", "texto": ""}])
def test_chat_body_invalido_da_422(cliente, body):
    assert cliente.post("/chat", json=body).status_code == 422


def test_chat_modelo_falla_da_502_sin_detalles(cliente):
    app.state.grafo = GrafoFalso(falla=True)
    r = cliente.post("/chat", json={"user_id": "u1", "texto": "hola"})
    assert r.status_code == 502
    assert "secreto" not in r.text
    assert "Traceback" not in r.text
