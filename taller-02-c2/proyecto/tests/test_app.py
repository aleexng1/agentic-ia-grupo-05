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


@pytest.mark.parametrize(
    ("port", "puerto_env", "esperado"),
    [("5123", "9000", 5123), ("", "9000", 9000), ("", "", 8000)],
)
def test_puerto_real_port_luego_puerto(monkeypatch, port, puerto_env, esperado):
    from src.comun import config

    monkeypatch.setenv("PORT", port)
    monkeypatch.setenv("PUERTO", puerto_env)
    assert config.puerto() == esperado


def test_urls_agentes_vacia_usa_la_direccion_interna(monkeypatch):
    """Sin URLS_AGENTES el coordinador usa 127.0.0.1 y el puerto real, no URL_BASE."""
    from src.comun import config

    monkeypatch.setenv("URL_BASE", "https://ejemplo.herokuapp.com/")
    monkeypatch.setenv("URLS_AGENTES", "")
    monkeypatch.setenv("PORT", "5123")
    assert config.modo_interno()
    assert config.urls_agentes() == [
        f"http://127.0.0.1:5123/agentes/{nombre}" for nombre in NOMBRES_FICHAS
    ]
    # La ficha pública sigue mostrando URL_BASE.
    assert config.url_agente("alex") == "https://ejemplo.herokuapp.com/agentes/alex"


def test_descubrir_en_modo_interno_usa_la_direccion_interna(monkeypatch):
    """El coordinador descubre las 4 fichas y les envía el JSON-RPC por la ruta interna.

    Las peticiones van directo a la app en memoria (sin red ni Gemini).
    """
    import asyncio

    import httpx

    from src.comun import config
    from src.coordinador import catalogo, cliente as modulo_cliente

    monkeypatch.setenv("URL_BASE", "https://ejemplo.herokuapp.com")
    monkeypatch.setenv("URLS_AGENTES", "")
    monkeypatch.setenv("PORT", "5123")

    async def _probar():
        modulo_cliente._CLIENTE_HTTP = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=modulo_app.app)
        )
        try:
            encontrados = await catalogo.descubrir()
            return [
                (
                    elemento["nombre"],
                    modulo_cliente.tarjeta_del_cliente(elemento["cliente"])
                    .supported_interfaces[0]
                    .url,
                )
                for elemento in encontrados
            ]
        finally:
            await modulo_cliente.cerrar_clientes()

    resultado = asyncio.run(_probar())
    assert resultado == [
        (nombre_ficha, f"http://127.0.0.1:5123/agentes/{nombre}")
        for nombre, nombre_ficha in NOMBRES_FICHAS.items()
    ]


def test_urls_agentes_con_valores_se_respeta(monkeypatch):
    from src.comun import config

    monkeypatch.setenv("URLS_AGENTES", "https://uno.example/ , https://dos.example")
    assert not config.modo_interno()
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

    # El panel exige la clave de acceso (ver tests/test_seguridad.py).
    respuesta = cliente.post(
        "/panel/consultar",
        json={"texto": "¿Dónde hago la feria?", "context_id": "prueba"},
        headers={"X-API-Key": "clave-de-prueba-solo-para-pytest"},
    )
    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "respuesta": "Hay tres recintos disponibles.",
        "context_id": "prueba",
        "agente": "Agente de Alex",
        "motivo": "Pregunta por recintos.",
    }
