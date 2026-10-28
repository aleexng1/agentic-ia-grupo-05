"""Ciclo ReAct del agente con historial de conversación (LangGraph).

Dueño: rol Núcleo. Esta es una versión mínima que ya funciona; el Núcleo la completa.

El ciclo es:
    LLM ──(pide herramienta)──> herramientas ──(observación)──> LLM ...
    LLM ──(responde sin pedir herramientas)──> FIN
    si se llega a MAX_PASOS ──> parada ──> FIN
"""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from src.config import obtener_llm, registrar_traza
from src.contrato import MAX_PASOS, EstadoAgente
from src.herramientas import validar_gasto
from src.rag import buscar_politica
from src.seguridad import PROMPT_SISTEMA

# Herramientas que el LLM puede pedir.
HERRAMIENTAS = [buscar_politica, validar_gasto]


def _trazar_observaciones(mensajes: list) -> None:
    """Muestra los resultados de herramientas que llegaron desde la última respuesta del LLM."""
    for mensaje in reversed(mensajes):
        if not isinstance(mensaje, ToolMessage):
            break
        registrar_traza("observacion", {"herramienta": mensaje.name, "resultado": mensaje.content})


def construir_agente():
    """Arma y devuelve el grafo compilado, con memoria de conversación por hilo."""
    # TODO(nucleo): reemplazar stub (nodos de clasificar/validar, guardar gasto y veredicto en el estado)
    llm = obtener_llm().bind_tools(HERRAMIENTAS)

    def nodo_llm(estado: EstadoAgente) -> dict:
        # Una vuelta del ciclo: el LLM lee el historial y decide (pensar → actuar).
        _trazar_observaciones(estado["messages"])
        pasos = estado.get("pasos", 0) + 1
        respuesta = llm.invoke([SystemMessage(PROMPT_SISTEMA), *estado["messages"]])
        registrar_traza(
            "llm",
            {"paso": pasos, "pide_herramientas": respuesta.tool_calls, "texto": respuesta.text},
        )
        return {"messages": [respuesta], "pasos": pasos}

    def nodo_parada(estado: EstadoAgente) -> dict:
        # Se llegó al máximo de pasos: se cierran las llamadas pendientes y se avisa.
        pendientes = estado["messages"][-1].tool_calls
        cierres = [
            ToolMessage("No ejecutada: se alcanzó el máximo de pasos.", tool_call_id=llamada["id"])
            for llamada in pendientes
        ]
        aviso = AIMessage(f"Me detuve: alcancé el máximo de {MAX_PASOS} pasos sin una decisión final.")
        registrar_traza("parada", {"motivo": "MAX_PASOS", "pasos": estado.get("pasos", 0)})
        return {"messages": [*cierres, aviso]}

    def elegir_siguiente(estado: EstadoAgente) -> str:
        # Condición de parada: sin herramientas pedidas → fin; demasiados pasos → parada.
        if not estado["messages"][-1].tool_calls:
            return END
        if estado.get("pasos", 0) >= MAX_PASOS:
            return "parada"
        return "herramientas"

    grafo = StateGraph(EstadoAgente)
    grafo.add_node("llm", nodo_llm)
    grafo.add_node("herramientas", ToolNode(HERRAMIENTAS))
    grafo.add_node("parada", nodo_parada)
    grafo.add_edge(START, "llm")
    grafo.add_conditional_edges("llm", elegir_siguiente, ["herramientas", "parada", END])
    grafo.add_edge("herramientas", "llm")
    grafo.add_edge("parada", END)
    return grafo.compile(checkpointer=InMemorySaver())


def conversar(agente, mensaje: str, hilo: str) -> str:
    """Envía un mensaje al agente y devuelve su respuesta en texto.

    El mismo `hilo` mantiene el historial entre turnos (segundo turno, tercero, ...).
    """
    # TODO(nucleo): reemplazar stub si hace falta (por ejemplo devolver también el veredicto)
    # recursion_limit es un freno de respaldo de LangGraph, por si falla la parada propia.
    configuracion = {"configurable": {"thread_id": hilo}, "recursion_limit": 3 * MAX_PASOS}
    # pasos vuelve a 0 en cada turno: el límite es por turno, no por conversación.
    entrada = {"messages": [HumanMessage(mensaje)], "pasos": 0}
    resultado = agente.invoke(entrada, configuracion)
    return resultado["messages"][-1].text
