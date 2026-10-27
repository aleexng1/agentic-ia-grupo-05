import os
import re
from typing import Annotated, Literal

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel
from typing_extensions import TypedDict

from .prompts import BLOQUEOS, FUENTE, GUARDIA, SIN_FUENTE, SISTEMA
from .tools import cargar_herramientas

LINEA_FUENTE = re.compile(r"(?im)^[ \t>*_]*fuentes?\s*:.*$")
MENSAJES_DE_CONTEXTO = 2


class Veredicto(BaseModel):
    permitido: bool
    categoria: Literal["ok", "fuera_de_tema", "inyeccion", "datos_personales", "accion_no_soportada"]
    motivo: str


class Estado(TypedDict):
    messages: Annotated[list, add_messages]
    veredicto: dict | None


def mensajes_del_turno(mensajes: list) -> list:
    """Mensajes posteriores al último mensaje del usuario."""
    for i in range(len(mensajes) - 1, -1, -1):
        if isinstance(mensajes[i], HumanMessage):
            return mensajes[i + 1 :]
    return mensajes


def crear_guardia(modelo_guardia):
    clasificador = modelo_guardia.with_structured_output(Veredicto)

    async def guardia_entrada(estado: Estado) -> dict:
        humanos = [m.text for m in estado["messages"] if isinstance(m, HumanMessage)]
        previos = humanos[-1 - MENSAJES_DE_CONTEXTO : -1]
        contexto = "".join(f"Mensaje previo del usuario: {t}\n" for t in previos)
        pedido = f"{contexto}<mensaje>\n{humanos[-1]}\n</mensaje>"
        try:
            v = await clasificador.ainvoke(
                [SystemMessage(GUARDIA), HumanMessage(pedido)]
            )
            if v is None:
                raise ValueError("el clasificador no devolvió un veredicto")
            veredicto = v.model_dump()
            veredicto["permitido"] = veredicto["permitido"] and veredicto["categoria"] == "ok"
        except Exception as exc:
            veredicto = {
                "permitido": False,
                "categoria": "no_verificado",
                "motivo": f"falló la guardia: {type(exc).__name__}",
            }
        return {"veredicto": veredicto}

    return guardia_entrada


def decidir(estado: Estado) -> str:
    return "agente" if estado["veredicto"]["permitido"] else "respuesta_bloqueada"


def respuesta_bloqueada(estado: Estado) -> dict:
    return {"messages": [AIMessage(BLOQUEOS[estado["veredicto"]["categoria"]])]}


def agregar_fuente(estado: Estado) -> dict:
    turno = mensajes_del_turno(estado["messages"])
    usadas = list(dict.fromkeys(m.name for m in turno if isinstance(m, ToolMessage)))
    finales = [m for m in turno if isinstance(m, AIMessage) and not m.tool_calls]
    if not finales:
        return {}
    ultimo = finales[-1]
    texto = LINEA_FUENTE.sub("", ultimo.text).rstrip()
    linea = FUENTE.format(herramientas=", ".join(usadas)) if usadas else SIN_FUENTE
    # mismo id: add_messages reemplaza el mensaje del modelo por el corregido
    return {"messages": [AIMessage(f"{texto}\n\n{linea}", id=ultimo.id)]}


async def construir_agente(api_key: str | None = None):
    herramientas = await cargar_herramientas()
    clave = api_key or os.environ.get("GOOGLE_API_KEY")
    modelo = ChatGoogleGenerativeAI(model=os.environ["MODELO"], google_api_key=clave)
    modelo_guardia = ChatGoogleGenerativeAI(
        model=os.environ["MODELO"], google_api_key=clave, temperature=0
    )
    agente_react = create_agent(modelo, herramientas, system_prompt=SISTEMA)

    grafo = StateGraph(Estado)
    grafo.add_node("guardia_entrada", crear_guardia(modelo_guardia))
    grafo.add_node("agente", agente_react)
    grafo.add_node("agregar_fuente", agregar_fuente)
    grafo.add_node("respuesta_bloqueada", respuesta_bloqueada)
    grafo.add_edge(START, "guardia_entrada")
    grafo.add_conditional_edges(
        "guardia_entrada",
        decidir,
        {"agente": "agente", "respuesta_bloqueada": "respuesta_bloqueada"},
    )
    grafo.add_edge("agente", "agregar_fuente")
    grafo.add_edge("agregar_fuente", END)
    grafo.add_edge("respuesta_bloqueada", END)
    return grafo.compile(checkpointer=MemorySaver())
