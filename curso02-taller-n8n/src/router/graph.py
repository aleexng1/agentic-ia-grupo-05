"""Agente router: clasifica el mensaje y lo deriva a preventa, postventa o genérica."""

from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from src.config import crear_llm
from src.router import prompts

# Cuántos mensajes previos del hilo se le muestran al router como contexto.
HISTORIAL_ROUTER = 6


class Decision(BaseModel):
    ruta: Literal["preventa", "postventa", "generica"] = Field(description="A qué agente va el mensaje.")
    motivo: str = Field(description="Una frase: por qué esa ruta.")


class Estado(TypedDict, total=False):
    mensaje: str
    ruta: str
    motivo: str
    respuesta: str
    messages: Annotated[list[AnyMessage], add_messages]


def construir_grafo(checkpointer=None):
    """Compila el grafo. Por defecto usa MemorySaver (memoria por thread_id)."""
    clasificador = crear_llm(temperatura=0).with_structured_output(Decision)

    def router(estado: Estado) -> dict:
        historial = estado.get("messages", [])[-HISTORIAL_ROUTER:]
        entrada = [SystemMessage(prompts.PROMPT_ROUTER), *historial, HumanMessage(estado["mensaje"])]
        decision: Decision = clasificador.invoke(entrada)
        return {
            "ruta": decision.ruta,
            "motivo": decision.motivo,
            "messages": [HumanMessage(estado["mensaje"])],
        }

    def responder(texto: str) -> dict:
        return {"respuesta": texto, "messages": [AIMessage(texto)]}

    def agente_preventa(estado: Estado) -> dict:
        return responder(prompts.PROMPT_PREVENTA.format(mensaje=estado["mensaje"]))

    def agente_postventa(estado: Estado) -> dict:
        return responder(prompts.PROMPT_POSTVENTA.format(mensaje=estado["mensaje"]))

    def respuesta_generica(estado: Estado) -> dict:
        return responder(prompts.RESPUESTA_GENERICA)

    def elegir_ruta(estado: Estado) -> str:
        return estado["ruta"]

    g = StateGraph(Estado)
    g.add_node("router", router)
    g.add_node("agente_preventa", agente_preventa)
    g.add_node("agente_postventa", agente_postventa)
    g.add_node("respuesta_generica", respuesta_generica)

    g.add_edge(START, "router")
    g.add_conditional_edges(
        "router",
        elegir_ruta,
        {
            "preventa": "agente_preventa",
            "postventa": "agente_postventa",
            "generica": "respuesta_generica",
        },
    )
    for nodo in ("agente_preventa", "agente_postventa", "respuesta_generica"):
        g.add_edge(nodo, END)

    return g.compile(checkpointer=checkpointer if checkpointer is not None else MemorySaver())
