"""Ruta genérica y historial del router, con un modelo FALSO: no llama al modelo ni a la base."""

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from main import correr
from src.router import graph as grafo_mod
from src.router import prompts
from src.router.graph import construir_grafo
from tests.fakes import LLMFalso

RESPUESTA_MODELO = "¡Hola Ana! Este chat es de la tienda. ¿Te ayudo con productos o pedidos?"


def armar(monkeypatch, rutas, **kw):
    llm = LLMFalso(rutas=list(rutas), **kw)
    monkeypatch.setattr(grafo_mod, "crear_llm", lambda temperatura=0: llm)
    return llm, construir_grafo()


def hilo(nombre="t1"):
    return {"configurable": {"thread_id": nombre}}


# ── La ficha de la tienda ────────────────────────────────────────────────────

def test_tienda_md_tiene_lo_pedido():
    texto = grafo_mod.TIENDA_MD.read_text(encoding="utf-8").lower()
    for esperado in ("televisores", "celulares", "horario", "pedido", "reclamo", "productos y precios"):
        assert esperado in texto, esperado


# ── El nodo usa el modelo, con la tienda y el historial ──────────────────────

def test_generica_usa_el_modelo_con_la_tienda_y_el_historial(monkeypatch):
    llm, g = armar(monkeypatch, ["generica", "generica"], respuesta=RESPUESTA_MODELO)
    g.invoke({"mensaje": "hola, soy Ana"}, hilo())
    estado = g.invoke({"mensaje": "¿qué venden?"}, hilo())

    assert estado["ruta"] == "generica"
    assert estado["respuesta"] == RESPUESTA_MODELO  # sale del modelo, no de la frase fija

    segunda = llm.recibidos[1]
    assert isinstance(segunda[0], SystemMessage)
    assert "ElectroAndes" in segunda[0].content and "Televisores" in segunda[0].content  # contexto de tienda.md
    assert "{tienda}" not in segunda[0].content
    conversacion = segunda[1:]
    assert [type(m) for m in conversacion] == [HumanMessage, AIMessage, HumanMessage]
    assert conversacion[0].content == "hola, soy Ana"  # recibe el historial, no solo el último mensaje
    assert conversacion[-1].content == "¿qué venden?"  # y el último mensaje aparece una sola vez


def test_prompt_generica_trae_las_reglas():
    assert "{tienda}" in prompts.PROMPT_GENERICA
    p = prompts.PROMPT_GENERICA.lower()
    for regla in ("nombre", "ajeno a la tienda", "ignorar", "máximo 3 líneas"):
        assert regla in p, regla


# ── El historial no tiene huecos en ninguna ruta ─────────────────────────────

@pytest.mark.parametrize("ruta", ["preventa", "postventa", "generica"])
def test_historial_sin_huecos(monkeypatch, ruta):
    _, g = armar(monkeypatch, [ruta, ruta])
    g.invoke({"mensaje": "primer mensaje"}, hilo())
    estado = g.invoke({"mensaje": "segundo mensaje"}, hilo())

    mensajes = estado["messages"]
    assert [type(m) for m in mensajes] == [HumanMessage, AIMessage, HumanMessage, AIMessage]
    assert [m.content for m in mensajes[::2]] == ["primer mensaje", "segundo mensaje"]
    assert mensajes[-1].content == estado["respuesta"]


# ── Si el modelo falla ───────────────────────────────────────────────────────

def test_si_el_modelo_falla_devuelve_la_frase_fija(monkeypatch, caplog):
    _, g = armar(monkeypatch, ["generica"], falla=True)
    estado = g.invoke({"mensaje": "hola"}, hilo())

    assert estado["respuesta"] == prompts.RESPUESTA_GENERICA
    assert [type(m) for m in estado["messages"]] == [HumanMessage, AIMessage]  # el historial sigue completo
    assert "clave-secreta" not in caplog.text  # el detalle del proveedor no llega al log


def test_respuesta_vacia_devuelve_la_frase_fija(monkeypatch):
    _, g = armar(monkeypatch, ["generica"], respuesta="   ")
    assert g.invoke({"mensaje": "hola"}, hilo())["respuesta"] == prompts.RESPUESTA_GENERICA


# ── El resto no cambia ───────────────────────────────────────────────────────

def test_saltos_y_estado_final(monkeypatch):
    _, g = armar(monkeypatch, ["generica"])
    assert correr(g, "hola", hilo()) == ["router", "respuesta_generica"]
    estado = g.get_state(hilo()).values
    assert {"ruta", "motivo", "respuesta"} <= set(estado)
