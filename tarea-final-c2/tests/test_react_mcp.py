"""Pruebas del ReAct de revisar_gasto (C2, Matías): las dos paradas y consultar_fondo por MCP.

No usan red, Gemini, Redis ni Postgres. El servidor MCP sí se levanta de verdad (proceso hijo
por stdio, ~4 s), porque es lo que hay que demostrar: consultar_fondo llamado desde el ReAct.
"""

import asyncio
import json

import pytest
from langchain_core.messages import ToolMessage
from langchain_core.tools import ToolException
from mcp import ClientSession
from mcp.client.stdio import stdio_client

from src.comun.config import CARPETA_PROYECTO
from src.mcp_fondos import servidor
from src.principal.herramientas import consultar_fondo as modulo_consultar
from tests.test_seguridad import LLMFalso, _pedir

FONDO_FR001 = {
    "id_fondo": "FR-001",
    "responsable": "Jefatura de Administración (ficticia)",
    "saldo_inicial": 200000,
    "saldo_actual": 200000,
    "gastos_aprobados": [],
}


def _caso(id_caso: str) -> dict:
    golden = json.loads((CARPETA_PROYECTO / "evaluacion" / "golden_set_c1.json").read_text(encoding="utf-8"))
    return next(c for c in golden["casos"] if c["id"] == id_caso)["turnos"][0]


# ---------------------------------------------------------------------------
# Servidor y cliente MCP
# ---------------------------------------------------------------------------


def test_la_logica_del_servidor_devuelve_el_fondo_y_falla_claro():
    assert servidor.consultar_fondo(" FR-001 ") == FONDO_FR001
    with pytest.raises(ValueError, match="no existe"):
        servidor.consultar_fondo("FR-999")


def test_el_servidor_mcp_publica_solo_consultar_fondo():
    async def listar():
        async with stdio_client(modulo_consultar._parametros_servidor()) as (lectura, escritura):
            async with ClientSession(lectura, escritura) as sesion:
                await sesion.initialize()
                return [h.name for h in (await sesion.list_tools()).tools]

    assert asyncio.run(listar()) == ["consultar_fondo"]


def test_el_servidor_mcp_hereda_el_entorno_del_proceso(monkeypatch):
    """En Heroku el Python hijo necesita LD_LIBRARY_PATH para cargar libpython (2026-11-27)."""
    monkeypatch.setenv("LD_LIBRARY_PATH", "/app/.heroku/python/lib")
    env = modulo_consultar._parametros_servidor().env
    assert env is not None
    assert env["LD_LIBRARY_PATH"] == "/app/.heroku/python/lib"


def test_consultar_fondo_por_mcp_devuelve_el_estado_del_fondo():
    assert modulo_consultar.consultar_fondo.invoke({"id_fondo": "FR-001"}) == FONDO_FR001


def test_fondo_inexistente_es_toolexception_sin_saldo_inventado():
    with pytest.raises(ToolException) as error:
        modulo_consultar.consultar_fondo.invoke({"id_fondo": "FR-999"})
    mensaje = str(error.value)
    assert "FR-999" in mensaje and "no existe" in mensaje
    assert "Error executing tool" not in mensaje
    assert "\n" not in mensaje


def test_si_el_mcp_no_responde_a_tiempo_avisa_en_una_linea(monkeypatch):
    monkeypatch.setattr(modulo_consultar, "TIEMPO_MAXIMO_MCP_SEG", 0.01)
    with pytest.raises(ToolException, match="no respondió en 0.01 s"):
        modulo_consultar.consultar_fondo.invoke({"id_fondo": "FR-001"})


def test_la_version_async_funciona_dentro_de_un_event_loop():
    """Así la llama el endpoint async /chat: no debe chocar con el loop que ya corre."""

    async def dentro_del_loop():
        return await modulo_consultar.consultar_fondo.ainvoke({"id_fondo": "FR-020"})

    assert asyncio.run(dentro_del_loop())["saldo_inicial"] == 20000


def test_la_version_sincronica_funciona_dentro_de_un_event_loop():
    """El grafo es síncrono; si alguien lo llama desde un endpoint async, invoke no debe romperse."""

    async def dentro_del_loop():
        return modulo_consultar.consultar_fondo.invoke({"id_fondo": "FR-050"})

    assert asyncio.run(dentro_del_loop())["saldo_inicial"] == 50000


def test_el_modo_listar_muestra_el_servidor_y_su_herramienta():
    resultado = asyncio.run(servidor.listar_por_mcp())
    assert resultado["servidor"] == servidor.NOMBRE_SERVIDOR
    assert [h["nombre"] for h in resultado["herramientas"]] == ["consultar_fondo"]


def test_construir_agente_acepta_otro_checkpointer(monkeypatch):
    from langgraph.checkpoint.memory import InMemorySaver

    from src.principal.flujos import revisar_gasto

    monkeypatch.setattr(revisar_gasto, "obtener_llm", lambda: LLMFalso([]))
    monkeypatch.setattr(revisar_gasto, "_obtener_respaldo", lambda: None)
    propio = InMemorySaver()
    assert revisar_gasto.construir_agente(checkpointer=propio).checkpointer is propio


# ---------------------------------------------------------------------------
# ReAct: parada por veredicto (con MCP) y parada por MAX_PASOS
# ---------------------------------------------------------------------------


@pytest.fixture
def revisar_gasto(monkeypatch):
    """Módulo revisar_gasto sin juez real (usa Gemini) ni registro real (archivo/Postgres)."""
    from src.principal.flujos import revisar_gasto as modulo

    registros = []

    def registrar_falso(gasto, veredicto):
        registros.append((gasto["id"], veredicto["decision"]))
        return {
            "antes": None,
            "despues": veredicto["decision"],
            "id_gasto": gasto["id"],
            "decision": veredicto["decision"],
            "operacion": "insertar",
        }

    monkeypatch.setattr(modulo, "_obtener_respaldo", lambda: None)  # sin depender del .env
    monkeypatch.setattr(modulo, "registrar_veredicto", registrar_falso)
    monkeypatch.setattr(
        modulo,
        "juzgar_con_validacion",
        lambda *_a: {"valido": True, "razon": "Coincide con la validación.", "evaluado": True},
    )
    monkeypatch.setattr(modulo, "registrar_traza", lambda *_a, **_k: None)
    modulo.registros_de_prueba = registros
    return modulo


def test_revision_completa_usa_consultar_fondo_por_mcp_y_cierra_ok(revisar_gasto, monkeypatch):
    turno = _caso("GS-01")
    gasto, esperado = turno["gasto"], turno["esperado"]
    llm = LLMFalso(
        [
            _pedir(("consultar_fondo", {"id_fondo": gasto["id_fondo"]})),
            _pedir(("validar_gasto", {"gasto": gasto, "politica": esperado["politica"], "categoria": esperado["categoria"]})),
            _pedir(
                (
                    "emitir_veredicto",
                    {
                        "decision": esperado["decision"],
                        "politica": esperado["politica"],
                        "categoria": esperado["categoria"],
                        "cuenta": esperado["cuenta"],
                        "motivo": "Peaje de viaje interno con boleta, dentro de plazo y con saldo (P02).",
                    },
                )
            ),
        ]
    )
    monkeypatch.setattr(revisar_gasto, "obtener_llm", lambda: llm)
    agente = revisar_gasto.construir_agente()

    resultado = revisar_gasto.revisar_caso(agente, turno["mensaje"], "hilo-ok", gasto)

    assert resultado["estado_final"] == "ok"
    assert resultado["herramientas_usadas"] == ["consultar_fondo", "validar_gasto", "emitir_veredicto"]
    assert resultado["pasos"] == 3
    assert resultado["veredicto"]["decision"] == esperado["decision"]
    assert resultado["veredicto"]["cuenta_sugerida"] == esperado["cuenta"]
    assert resultado["respuesta"].startswith(f"Decisión: {esperado['decision'].upper()}")
    assert revisar_gasto.registros_de_prueba == [(gasto["id"], esperado["decision"])]

    # La observación que vio el modelo es el fondo real que entregó el servidor MCP.
    estado = agente.get_state({"configurable": {"thread_id": "hilo-ok"}}).values
    observacion = next(m for m in estado["messages"] if isinstance(m, ToolMessage) and m.name == "consultar_fondo")
    assert json.loads(observacion.content) == FONDO_FR001
    assert estado["fondo"]["saldo_actual"] == FONDO_FR001["saldo_actual"] - gasto["monto"]


def test_consultar_fondo_no_pisa_el_saldo_vigente_del_hilo(revisar_gasto, monkeypatch):
    """Si el hilo ya descontó gastos, el modelo ve ese saldo y no el inicial del MCP (RG-08)."""
    gasto = _caso("GS-01")["gasto"]
    fondo_con_descuento = {**FONDO_FR001, "saldo_actual": 5000, "gastos_aprobados": ["G-0001"]}
    llm = LLMFalso([_pedir(("consultar_fondo", {"id_fondo": "FR-001"})), _pedir(("modificar_registro", {}))])
    monkeypatch.setattr(revisar_gasto, "obtener_llm", lambda: llm)
    agente = revisar_gasto.construir_agente()

    revisar_gasto.revisar_caso(agente, "Revisa este gasto.", "hilo-saldo", gasto, fondo_con_descuento)

    estado = agente.get_state({"configurable": {"thread_id": "hilo-saldo"}}).values
    observacion = next(m for m in estado["messages"] if isinstance(m, ToolMessage) and m.name == "consultar_fondo")
    assert json.loads(observacion.content)["saldo_actual"] == 5000
    assert estado["fondo"] == fondo_con_descuento


def test_se_detiene_por_max_pasos_con_estado_error(revisar_gasto, monkeypatch):
    turno = _caso("GS-01")
    gasto, esperado = turno["gasto"], turno["esperado"]
    validar = ("validar_gasto", {"gasto": gasto, "politica": esperado["politica"], "categoria": esperado["categoria"]})
    llm = LLMFalso([_pedir(validar) for _ in range(5)])  # nunca emite veredicto
    monkeypatch.setattr(revisar_gasto, "obtener_llm", lambda: llm)
    monkeypatch.setattr(revisar_gasto, "MAX_PASOS", 2)
    agente = revisar_gasto.construir_agente()

    resultado = revisar_gasto.revisar_caso(agente, turno["mensaje"], "hilo-parada", gasto)

    assert resultado["estado_final"] == "error"
    assert resultado["pasos"] == 2
    assert llm.llamadas == 2
    assert resultado["herramientas_usadas"] == ["validar_gasto"]
    assert resultado["veredicto"] is None
    assert "máximo de 2 pasos" in resultado["respuesta"]
    assert revisar_gasto.registros_de_prueba == []


def test_un_turno_nuevo_reinicia_pasos_herramientas_y_estado(revisar_gasto, monkeypatch):
    turno = _caso("GS-01")
    gasto, esperado = turno["gasto"], turno["esperado"]
    validar = ("validar_gasto", {"gasto": gasto, "politica": esperado["politica"], "categoria": esperado["categoria"]})
    llm = LLMFalso([_pedir(validar), _pedir(validar), _pedir(("modificar_registro", {}))])
    monkeypatch.setattr(revisar_gasto, "obtener_llm", lambda: llm)
    monkeypatch.setattr(revisar_gasto, "MAX_PASOS", 2)
    agente = revisar_gasto.construir_agente()

    assert revisar_gasto.revisar_caso(agente, "Revisa.", "hilo-x", gasto)["estado_final"] == "error"
    segundo = revisar_gasto.revisar_caso(agente, "Revisa otra vez.", "hilo-x", gasto)
    assert segundo["estado_final"] == "bloqueado"
    assert segundo["pasos"] == 1
    assert segundo["herramientas_usadas"] == []
