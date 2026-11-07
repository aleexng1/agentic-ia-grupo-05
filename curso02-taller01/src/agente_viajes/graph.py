"""El agente de viajes: un grafo de LangGraph con modelo Gemini y dos herramientas."""

import asyncio
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver

from src.agente_viajes.prompts import SYSTEM_PROMPT
from src.agente_viajes.tools import HERRAMIENTAS

# El .env está en curso02-taller01/, sin importar desde dónde se corra el programa.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

TIMEOUT_MODELO = 60  # segundos que se espera cada llamada al modelo
TIMEOUT_RESPUESTA = 120  # segundos máximos para una respuesta completa

modelo = ChatGoogleGenerativeAI(
    model=os.getenv("MODELO", "gemini-3.5-flash-lite"),
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    timeout=TIMEOUT_MODELO,
    max_retries=2,
)

graph = create_agent(
    modelo,
    HERRAMIENTAS,
    system_prompt=SYSTEM_PROMPT,
    checkpointer=MemorySaver(),
)


def _texto_de(contenido):
    """Saca el texto de un mensaje: puede venir como texto o como lista de partes."""
    if isinstance(contenido, str):
        return contenido
    partes = []
    for parte in contenido:
        if isinstance(parte, str):
            partes.append(parte)
        elif isinstance(parte, dict) and parte.get("type") == "text":
            partes.append(parte.get("text", ""))
    return "".join(partes)


def _entrada(texto):
    return {"messages": [{"role": "user", "content": texto}]}


def _config(context_id):
    # thread_id es la "carpeta" donde el grafo guarda la memoria de esa conversación.
    return {"configurable": {"thread_id": context_id}}


async def responder(texto, context_id):
    """Contrato de todos los agentes: recibe texto y context_id, devuelve texto."""
    try:
        resultado = await asyncio.wait_for(
            graph.ainvoke(_entrada(texto), _config(context_id)),
            timeout=TIMEOUT_RESPUESTA,
        )
    except asyncio.TimeoutError:
        raise RuntimeError(f"el modelo no respondió en {TIMEOUT_RESPUESTA} segundos") from None
    return _texto_de(resultado["messages"][-1].content)


def saltos(texto):
    """Corre el agente mostrando por qué nodos y herramientas pasa. Devuelve la respuesta final."""
    total = 0
    respuesta = ""
    entrada = _entrada(texto)
    for actualizacion in graph.stream(
        entrada, _config(str(uuid.uuid4())), stream_mode="updates"
    ):
        for nodo, cambios in actualizacion.items():
            total += 1
            print(f"[salto {total}] nodo: {nodo}")
            for mensaje in (cambios or {}).get("messages", []):
                for llamada in getattr(mensaje, "tool_calls", None) or []:
                    print(f"    llama a la herramienta {llamada['name']} con {llamada['args']}")
                if getattr(mensaje, "type", "") == "tool":
                    resumen = _texto_de(mensaje.content)
                    resumen = resumen if len(resumen) <= 150 else resumen[:150] + "..."
                    print(f"    resultado de {mensaje.name}: {resumen}")
                elif getattr(mensaje, "type", "") == "ai" and not getattr(mensaje, "tool_calls", None):
                    respuesta = _texto_de(mensaje.content)
    print(f"Total: {total} saltos\n")
    return respuesta


def diagrama():
    """Devuelve la estructura del grafo en Mermaid, sin ejecutarlo."""
    return graph.get_graph().draw_mermaid()
