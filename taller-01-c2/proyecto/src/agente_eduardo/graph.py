"""Grafo LangGraph del agente de presupuestos de Eduardo."""

import os
from uuid import uuid4

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver

from src.agente_eduardo.prompts import SYSTEM_PROMPT
from src.agente_eduardo.tools import estimar_presupuesto

load_dotenv()
_MODELO = os.getenv("MODELO", "gemini-3.5-flash-lite")
_modelo = init_chat_model(
    model=None,
    model_provider="google_genai",
    configurable_fields=("model",),
    timeout=45,
).with_config(configurable={"model": _MODELO})

graph = create_agent(
    model=_modelo,
    tools=[estimar_presupuesto],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=MemorySaver(),
)


def _texto_mensaje(mensaje) -> str:
    """Extrae texto de mensajes simples o bloques de contenido."""
    contenido = getattr(mensaje, "content", "")
    if isinstance(contenido, str):
        return contenido
    if isinstance(contenido, list):
        return "".join(
            bloque.get("text", "")
            for bloque in contenido
            if isinstance(bloque, dict) and bloque.get("type") == "text"
        )
    return str(contenido)


async def responder(texto: str, context_id: str) -> str:
    """Ejecuta el agente para el contexto indicado."""
    resultado = await graph.ainvoke(
        {"messages": [{"role": "user", "content": texto}]},
        config={"configurable": {"thread_id": context_id or str(uuid4())}},
    )
    return _texto_mensaje(resultado["messages"][-1])


def saltos(texto: str) -> None:
    """Imprime nodos y herramientas recorridos en una sola línea por evento."""
    saltos_totales = 0
    respuesta_final = ""
    try:
        for actualizacion in graph.stream(
            {"messages": [{"role": "user", "content": texto}]},
            config={"configurable": {"thread_id": f"saltos-{uuid4()}"}},
            stream_mode="updates",
        ):
            for nodo, datos in actualizacion.items():
                saltos_totales += 1
                print(f"Nodo: {nodo}")
                for mensaje in datos.get("messages", []):
                    for llamada in getattr(mensaje, "tool_calls", []):
                        print(f"Herramienta: {llamada.get('name', 'desconocida')}")
                    if nodo == "model" and not getattr(mensaje, "tool_calls", []):
                        respuesta_final = _texto_mensaje(mensaje)
    except Exception as error:
        detalle = str(error).replace("\r", " ").replace("\n", " ").strip() or error.__class__.__name__
        print(f"No se pudo completar la consulta: {detalle}")
    if respuesta_final:
        print(f"Respuesta: {respuesta_final}")
    print(f"Saltos totales: {saltos_totales}")


def diagrama() -> None:
    """Imprime el grafo en formato Mermaid sin invocar el modelo."""
    print(graph.get_graph().draw_mermaid())
