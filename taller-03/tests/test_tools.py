"""Guardrails de tools.py, sin LLM ni red."""
import asyncio
import logging

import pytest
from langchain_core.tools import StructuredTool

from src.colombia import tools
from src.colombia.tools import CONTADOR, MSG_LIMITE, envolver, filtrar_permitidas


def falsa(nombre: str, llamadas: list, demora: float = 0):
    async def corrutina(resource: str = "x", pageSize: int = 10, keyword: str = "") -> str:
        llamadas.append((resource, pageSize, keyword))
        await asyncio.sleep(demora)
        return "ok"

    return StructuredTool.from_function(coroutine=corrutina, name=nombre, description="falsa")


@pytest.fixture(autouse=True)
def limpiar():
    CONTADOR.reiniciar("default")


def test_tool_fuera_de_la_lista_se_filtra_y_se_registra(caplog):
    caplog.set_level(logging.INFO, logger="guardrails")
    lista = [falsa(n, []) for n in tools.TOOLS_PERMITIDAS] + [falsa("delete_item", [])]
    nombres = {h.name for h in filtrar_permitidas(lista)}
    assert "delete_item" not in nombres
    assert nombres == tools.TOOLS_PERMITIDAS
    assert any("tool_ignorada" in r.message and "delete_item" in r.message for r in caplog.records)


def test_page_size_500_se_rechaza_con_mensaje():
    llamadas = []
    tool = envolver(falsa("list_items_paged", llamadas))
    respuesta = asyncio.run(tool.ainvoke({"resource": "city", "pageSize": 500}))
    assert "50" in respuesta and "pageSize" in respuesta
    assert llamadas == []


def test_keyword_de_100_caracteres_se_rechaza_con_mensaje():
    llamadas = []
    tool = envolver(falsa("search_items", llamadas))
    respuesta = asyncio.run(tool.ainvoke({"resource": "city", "keyword": "a" * 100}))
    assert "60" in respuesta and "keyword" in respuesta
    assert llamadas == []


def test_argumentos_validos_llegan_a_la_tool():
    llamadas = []
    tool = envolver(falsa("list_items_paged", llamadas))
    assert asyncio.run(tool.ainvoke({"resource": "city", "pageSize": 50})) == "ok"
    assert llamadas == [("city", 50, "")]


def test_limite_de_seis_llamadas_y_reinicio():
    tool = envolver(falsa("get_country_info", []))
    respuestas = [asyncio.run(tool.ainvoke({})) for _ in range(7)]
    assert respuestas[:6] == ["ok"] * 6
    assert respuestas[6] == MSG_LIMITE
    CONTADOR.reiniciar("default")
    assert asyncio.run(tool.ainvoke({})) == "ok"


def test_timeout_devuelve_mensaje_corto(monkeypatch):
    monkeypatch.setattr(tools, "TIMEOUT_SEGUNDOS", 0.05)
    tool = envolver(falsa("get_country_info", [], demora=1))
    respuesta = asyncio.run(tool.ainvoke({}))
    assert "segundos" in respuesta
