"""Agente router: clasifica el mensaje y lo deriva a preventa, postventa o genérica."""

import logging
from pathlib import Path
from typing import Annotated, Literal, TypedDict

from langchain.agents import create_agent
from langchain.agents.middleware import AgentState, after_agent
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, RemoveMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from src.config import crear_llm
from src.router import prompts
from src.router.tools import TOOLS_POSTVENTA, TOOLS_PREVENTA

log = logging.getLogger("uvicorn.error")

# Cuántos mensajes previos del hilo se le muestran al router como contexto.
HISTORIAL_ROUTER = 4
# Cuántos mensajes del hilo ve respuesta_generica para conversar.
HISTORIAL_GENERICA = 12

TIENDA_MD = Path(__file__).resolve().parents[2] / "data" / "tienda.md"


class Decision(BaseModel):
    ruta: Literal["preventa", "postventa", "generica"] = Field(description="A qué agente va el mensaje.")
    motivo: str = Field(description="Una frase: por qué esa ruta.")


class Estado(TypedDict, total=False):
    mensaje: str
    ruta: str
    motivo: str
    respuesta: str
    messages: Annotated[list[AnyMessage], add_messages]


class EstadoAgente(AgentState):
    """Estado de un agente ReAct (preventa, postventa): el de LangChain más la respuesta final del turno."""

    respuesta: str


def cierre_de_turno(respuesta_vacia: str):
    """Middleware que corre al terminar un agente: fija `respuesta` y deja en el historial solo el mensaje
    del cliente y la respuesta final. Las llamadas a herramientas y sus resultados no se guardan en la memoria."""

    @after_agent(state_schema=EstadoAgente, name="cierre")
    def cerrar_turno(state: EstadoAgente, runtime) -> dict:
        mensajes = state["messages"]
        inicio = max((i for i, m in enumerate(mensajes) if isinstance(m, HumanMessage)), default=-1)
        turno = mensajes[inicio + 1:]  # lo que se generó después del mensaje del cliente
        finales = [m for m in turno if isinstance(m, AIMessage) and not m.tool_calls]
        texto = ((finales[-1].text if finales else "") or "").strip() or respuesta_vacia
        quitar = [RemoveMessage(id=m.id) for m in turno if m.id]
        return {"respuesta": texto, "messages": [*quitar, AIMessage(texto)]}

    return cerrar_turno


def crear_agente(nombre: str, prompt: str, herramientas: list, respuesta_vacia: str):
    """Agente ReAct (create_agent) para un nodo del grafo. checkpointer=False: no guarda checkpoints propios;
    la memoria del hilo la lleva el grafo padre, con solo los mensajes limpios."""
    return create_agent(
        crear_llm(temperatura=0.2),
        herramientas,
        system_prompt=prompt,
        middleware=[cierre_de_turno(respuesta_vacia)],
        state_schema=EstadoAgente,
        checkpointer=False,
        name=nombre,
    )


def construir_grafo(checkpointer=None):
    """Compila el grafo. Por defecto usa MemorySaver (memoria por thread_id)."""
    clasificador = crear_llm(temperatura=0).with_structured_output(Decision)
    conversador = crear_llm(temperatura=0.3)  # sin herramientas: solo conversa
    preventa = crear_agente("agente_preventa", prompts.PROMPT_PREVENTA, TOOLS_PREVENTA,
                            prompts.RESPUESTA_PREVENTA_VACIA)
    postventa = crear_agente("agente_postventa", prompts.PROMPT_POSTVENTA, TOOLS_POSTVENTA,
                             prompts.RESPUESTA_POSTVENTA_VACIA)
    prompt_generica = prompts.PROMPT_GENERICA.format(tienda=TIENDA_MD.read_text(encoding="utf-8").strip())

    def router(estado: Estado) -> dict:
        textos = [m for m in estado.get("messages", []) if isinstance(m, (HumanMessage, AIMessage)) and m.text]
        historial = textos[-HISTORIAL_ROUTER:]
        # Con la ruta anterior (la del turno previo del hilo), "Samsung" o "sí" siguen la conversación.
        sistema = prompts.PROMPT_ROUTER + prompts.contexto_ruta(estado.get("ruta"))
        entrada = [SystemMessage(sistema), *historial, HumanMessage(estado["mensaje"])]
        decision: Decision = clasificador.invoke(entrada)
        return {
            "ruta": decision.ruta,
            "motivo": decision.motivo,
            "messages": [HumanMessage(estado["mensaje"])],
        }

    def responder(texto: str) -> dict:
        return {"respuesta": texto, "messages": [AIMessage(texto)]}

    def respuesta_generica(estado: Estado) -> dict:
        # El router ya agregó el mensaje del usuario a messages: el historial llega completo.
        entrada = [SystemMessage(prompt_generica), *estado["messages"][-HISTORIAL_GENERICA:]]
        try:
            texto = (conversador.invoke(entrada).text or "").strip()
        except Exception as e:
            # Solo el tipo de error: el mensaje del proveedor no debe llegar a los logs.
            log.warning("respuesta_generica: falló el modelo (%s); se usa la frase fija.", type(e).__name__)
            texto = ""
        return responder(texto or prompts.RESPUESTA_GENERICA)

    def elegir_ruta(estado: Estado) -> str:
        return estado["ruta"]

    g = StateGraph(Estado)
    g.add_node("router", router)
    g.add_node("agente_preventa", preventa)
    g.add_node("agente_postventa", postventa)
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
