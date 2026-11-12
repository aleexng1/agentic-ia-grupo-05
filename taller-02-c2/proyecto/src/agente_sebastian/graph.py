"""Grafo LangGraph del agente de comida y catering de Sebastian."""

import os
from uuid import uuid4

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver

from src.agente_sebastian.prompts import SYSTEM_PROMPT
from src.agente_sebastian.tools import armar_catering


load_dotenv()
_MODELO = os.getenv("MODELO", "gemini-3.5-flash-lite")

# La inicialización diferida permite importar el grafo y ver su diagrama sin clave.
_modelo = init_chat_model(
    model=None,
    model_provider="google_genai",
    configurable_fields=("model",),
    timeout=45,
).with_config(configurable={"model": _MODELO})

graph = create_agent(
    model=_modelo,
    tools=[armar_catering],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=MemorySaver(),
)


def _texto_mensaje(mensaje) -> str:
    """Extrae texto tanto de respuestas simples como de bloques de contenido."""
    contenido = getattr(mensaje, "content", "")
    if isinstance(contenido, str):
        return contenido
    if isinstance(contenido, list):
        partes = [
            bloque.get("text", "")
            for bloque in contenido
            if isinstance(bloque, dict) and bloque.get("type") == "text"
        ]
        return "".join(partes)
    return str(contenido)


async def responder(texto: str, context_id: str) -> str:
    """Ejecuta el grafo y devuelve el texto de su último mensaje."""
    identificador = context_id or str(uuid4())
    resultado = await graph.ainvoke(
        {"messages": [{"role": "user", "content": texto}]},
        config={"configurable": {"thread_id": identificador}},
    )
    return _texto_mensaje(resultado["messages"][-1])


def saltos(texto: str) -> None:
    """Muestra los nodos y herramientas usados al procesar una pregunta."""
    cantidad_saltos = 0
    respuesta_final = ""
    configuracion = {"configurable": {"thread_id": f"saltos-{uuid4()}"}}

    try:
        for actualizacion in graph.stream(
            {"messages": [{"role": "user", "content": texto}]},
            config=configuracion,
            stream_mode="updates",
        ):
            for nodo, datos in actualizacion.items():
                cantidad_saltos += 1
                print(f"Nodo: {nodo}")
                for mensaje in datos.get("messages", []):
                    for llamada in getattr(mensaje, "tool_calls", []):
                        print(f"Herramienta: {llamada.get('name', 'desconocida')}")
                        print(f"Argumentos: {llamada.get('args', {})}")
                    if nodo == "model" and not getattr(mensaje, "tool_calls", []):
                        respuesta_final = _texto_mensaje(mensaje)
    except Exception as error:
        detalle = str(error).replace("\r", " ").replace("\n", " ").strip()
        if not detalle:
            detalle = error.__class__.__name__
        print(f"No se pudo completar la consulta: {detalle}")

    if respuesta_final:
        print(f"Respuesta: {respuesta_final}")
    print(f"Saltos totales: {cantidad_saltos}")


def diagrama() -> None:
    """Imprime la estructura del grafo en formato Mermaid."""
    print(graph.get_graph().draw_mermaid())
