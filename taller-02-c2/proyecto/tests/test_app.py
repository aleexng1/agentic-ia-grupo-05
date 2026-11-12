"""Pruebas de la app única: salud, panel y fichas, sin llamar a Gemini."""

import pytest
from fastapi.testclient import TestClient

import app as modulo_app
from src.comun.config import url_agente, url_base


NOMBRES_FICHAS = {
    "matias": "Agente de Matias",
    "alex": "Agente de Alex",
    "eduardo": "Agente de Eduardo",
    "sebastian": "Agente de Sebastian",
}


@pytest.fixture
def cliente():
    """Cliente HTTP en memoria; no se entra al ciclo de arranque ni se usa la red."""
    return TestClient(modulo_app.app)


def _url_de_ficha(ficha: dict) -> str:
    return ficha["supportedInterfaces"][0]["url"]


def test_salud_responde_ok(cliente):
    respuesta = cliente.get("/salud")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"ok": True}


def test_panel_del_coordinador_en_la_raiz(cliente):
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    assert "text/html" in respuesta.headers["content-type"]


def test_ficha_del_coordinador_en_la_raiz(cliente):
    respuesta = cliente.get("/.well-known/agent-card.json")
    assert respuesta.status_code == 200
    ficha = respuesta.json()
    assert ficha["name"] == "Coordinador"
    assert _url_de_ficha(ficha) == url_base()


@pytest.mark.parametrize(("nombre", "nombre_ficha"), NOMBRES_FICHAS.items())
def test_ficha_de_cada_agente(cliente, nombre, nombre_ficha):
    respuesta = cliente.get(f"/agentes/{nombre}/.well-known/agent-card.json")
    assert respuesta.status_code == 200
    ficha = respuesta.json()
    assert ficha["name"] == nombre_ficha
    assert _url_de_ficha(ficha) == url_agente(nombre)


def test_urls_agentes_vacia_usa_las_rutas_internas(monkeypatch):
    from src.comun import config

    monkeypatch.setenv("URL_BASE", "https://ejemplo.herokuapp.com/")
    monkeypatch.setenv("URLS_AGENTES", "")
    assert config.urls_agentes() == [
        f"https://ejemplo.herokuapp.com/agentes/{nombre}" for nombre in NOMBRES_FICHAS
    ]


def test_urls_agentes_con_valores_se_respeta(monkeypatch):
    from src.comun import config

    monkeypatch.setenv("URLS_AGENTES", "https://uno.example/ , https://dos.example")
    assert config.urls_agentes() == ["https://uno.example", "https://dos.example"]


def test_panel_consultar_entrega_agente_y_motivo(cliente, monkeypatch):
    """El panel devuelve agente y motivo por separado; el grafo se reemplaza por un doble."""
    from src.coordinador import graph as modulo_graph

    async def _sin_descubrir(imprimir=False):
        return None

    class _GrafoFalso:
        async def ainvoke(self, entrada, config):
            return {
                "messages": [],
                "agente": "Agente de Alex",
                "motivo": "Pregunta por recintos.",
                "respuesta": "Hay tres recintos disponibles.",
            }

    monkeypatch.setattr(modulo_graph, "inicializar_supervisor", _sin_descubrir)
    monkeypatch.setattr(modulo_graph, "graph", _GrafoFalso())

    respuesta = cliente.post(
        "/panel/consultar", json={"texto": "¿Dónde hago la feria?", "context_id": "prueba"}
    )
    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "respuesta": "Hay tres recintos disponibles.",
        "context_id": "prueba",
        "agente": "Agente de Alex",
        "motivo": "Pregunta por recintos.",
    }
