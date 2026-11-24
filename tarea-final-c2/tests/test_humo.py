"""Pruebas de humo: el esqueleto arranca y la seguridad básica funciona. Sin red ni Gemini."""

import json

import pytest
from fastapi.testclient import TestClient

from api.app import app
from tests.conftest import CLAVE_DE_PRUEBA

CHAT = {"thread_id": "humo-1", "texto": "¿Cuál es el tope de hotel?"}


@pytest.fixture
def cliente():
    return TestClient(app)


def test_health_responde_200(cliente):
    respuesta = cliente.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"ok": True}


def test_chat_sin_clave_responde_401(cliente):
    respuesta = cliente.post("/chat", json=CHAT)
    assert respuesta.status_code == 401
    assert "X-API-Key" in respuesta.json()["detail"]


def test_chat_con_clave_incorrecta_responde_401(cliente):
    respuesta = cliente.post("/chat", json=CHAT, headers={"X-API-Key": "otra-clave"})
    assert respuesta.status_code == 401


def test_chat_sin_router_responde_501(cliente):
    """BORRAR o cambiar cuando exista el router (Alex): entonces /chat responde 200."""
    respuesta = cliente.post("/chat", json=CHAT, headers={"X-API-Key": CLAVE_DE_PRUEBA})
    assert respuesta.status_code == 501
    assert "router" in respuesta.json()["detail"]


def test_registro_sin_clave_responde_401(cliente):
    assert cliente.get("/registro/cualquiera").status_code == 401


def test_max_pasos_por_defecto_y_desde_entorno(monkeypatch):
    from src.comun.config import max_pasos_react

    monkeypatch.delenv("MAX_PASOS_REACT", raising=False)
    assert max_pasos_react() == 10
    monkeypatch.setenv("MAX_PASOS_REACT", "4")
    assert max_pasos_react() == 4


@pytest.mark.parametrize("cargo", [None, "Jefe de tienda"])
def test_validar_gasto_con_y_sin_cargo(cargo):
    """El campo opcional cargo (nuevo en C2) no cambia la validación de c1 (caso GS-01)."""
    from src.comun.config import CARPETA_PROYECTO
    from src.principal.herramientas.validar_gasto import validar_gasto

    golden = json.loads((CARPETA_PROYECTO / "evaluacion" / "golden_set_c1.json").read_text(encoding="utf-8"))
    turno = next(c for c in golden["casos"] if c["id"] == "GS-01")["turnos"][0]
    gasto = dict(turno["gasto"])
    if cargo is not None:
        gasto["cargo"] = cargo
    resultado = validar_gasto.invoke(
        {"gasto": gasto, "politica": turno["esperado"]["politica"], "categoria": turno["esperado"]["categoria"]}
    )
    assert resultado["cumple"] is True
    assert resultado["cuenta"] == turno["esperado"]["cuenta"]


def test_modulos_copiados_importan():
    """El ReAct de c1, el juez, el RAG y la app del verificador importan sin llamar a servicios."""
    import src.conocimiento.rag.rag  # noqa: F401
    import src.principal.flujos.revisar_gasto  # noqa: F401
    import src.principal.juez  # noqa: F401
    from src.verificador.app import app as app_verificador

    assert TestClient(app_verificador).get("/health").status_code == 200
