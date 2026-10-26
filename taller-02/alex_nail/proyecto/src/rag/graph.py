# Grafo LangGraph del agente RAG: reformular → buscar → (¿evidencia?) → responder | no_se.
import os
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from src.rag import tools
from src.rag.prompts import FRAGMENTO, NO_SE, PROMPT_REFORMULAR, SYSTEM_PROMPT, USER_PROMPT


class Estado(TypedDict, total=False):
    pregunta: str
    pregunta_reformulada: str  # la que usa buscar para el embedding; responder usa la original
    fragmentos: list[dict]  # cada uno: texto, fuente, pagina, parecido
    mejor_parecido: float
    respuesta: str
    messages: Annotated[list[AnyMessage], add_messages]  # memoria de la conversación (por thread_id)


def umbral() -> float:
    return float(os.getenv("UMBRAL", "0.65"))


def crear_modelo():
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(model=os.getenv("MODELO"))


def reformular(estado: Estado) -> dict:
    salida = crear_modelo().invoke([HumanMessage(PROMPT_REFORMULAR.format(pregunta=estado["pregunta"]))])
    return {"pregunta_reformulada": salida.text.strip() or estado["pregunta"]}


def buscar(estado: Estado) -> dict:
    try:
        fragmentos = tools.buscar_fragmentos(estado.get("pregunta_reformulada") or estado["pregunta"])
    except tools.IndiceVacio as e:
        # Sin índice no hay nada que buscar: la respuesta es el aviso y el grafo termina aquí.
        return {"fragmentos": [], "mejor_parecido": 0.0, "respuesta": str(e),
                "messages": [HumanMessage(estado["pregunta"]), AIMessage(str(e))]}
    mejor = max((f["parecido"] for f in fragmentos), default=0.0)
    return {"fragmentos": fragmentos, "mejor_parecido": mejor, "respuesta": ""}


def evidencia(estado: Estado) -> str:
    if estado.get("respuesta"):
        return "fin"  # buscar ya respondió (índice vacío)
    return "responder" if estado["mejor_parecido"] >= umbral() else "no_se"


def responder(estado: Estado) -> dict:
    contexto = "\n\n".join(FRAGMENTO.format(**f) for f in estado["fragmentos"])
    mensaje = USER_PROMPT.format(contexto=contexto, pregunta=estado["pregunta"])
    salida = crear_modelo().invoke([SystemMessage(SYSTEM_PROMPT), HumanMessage(mensaje)])
    return {"respuesta": salida.text, "messages": [HumanMessage(estado["pregunta"]), AIMessage(salida.text)]}


def no_se(estado: Estado) -> dict:
    return {"respuesta": NO_SE, "messages": [HumanMessage(estado["pregunta"]), AIMessage(NO_SE)]}


def construir_grafo(checkpointer=None):
    grafo = StateGraph(Estado)
    grafo.add_node("reformular", reformular)
    grafo.add_node("buscar", buscar)
    grafo.add_node("responder", responder)
    grafo.add_node("no_se", no_se)
    grafo.add_edge(START, "reformular")
    grafo.add_edge("reformular", "buscar")
    grafo.add_conditional_edges("buscar", evidencia, {"responder": "responder", "no_se": "no_se", "fin": END})
    grafo.add_edge("responder", END)
    grafo.add_edge("no_se", END)
    return grafo.compile(checkpointer=checkpointer or MemorySaver())


def detalle_saltos(estado: dict) -> list[str]:
    """Líneas extra que main.py muestra con --saltos."""
    lineas = [
        f"Pregunta original:  {estado.get('pregunta', '')}",
        f"Pregunta reescrita: {estado.get('pregunta_reformulada', '')}",
        f"UMBRAL: {umbral():.2f} · mejor parecido: {estado.get('mejor_parecido', 0):.3f}",
    ]
    fragmentos = estado.get("fragmentos", [])
    lineas.append(f"Fragmentos recuperados: {len(fragmentos)}")
    for i, f in enumerate(fragmentos, 1):
        inicio = f["texto"][:90] + ("…" if len(f["texto"]) > 90 else "")
        marca = "✓" if f["parecido"] >= umbral() else "✗"
        lineas.append(f"  {i}. {marca} parecido {f['parecido']:.3f} · {f['fuente']} p.{f['pagina']} · {inicio!r}")
    return lineas
