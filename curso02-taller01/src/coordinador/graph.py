"""El coordinador: un grafo de LangGraph con un solo nodo que le pregunta al agente de viajes por A2A.

No sabe nada de viajes: reenvía la pregunta y repite la respuesta.
"""

import asyncio
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

from src.coordinador import cliente as remoto

# El .env está en curso02-taller01/, sin importar desde dónde se corra el programa.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

TIMEOUT_RESPUESTA = 150  # segundos máximos por respuesta (más que la espera al agente remoto)


def _url_viajes():
    # Se lee en cada uso para que un cambio en el entorno (o en las pruebas) se note.
    return os.getenv("URL_VIAJES", "http://127.0.0.1:8000")


def _texto_de(contenido):
    """Texto de un mensaje: puede venir como texto o como lista de partes."""
    if isinstance(contenido, str):
        return contenido
    return "".join(
        p if isinstance(p, str) else p.get("text", "")
        for p in contenido
        if isinstance(p, str) or (isinstance(p, dict) and p.get("type") == "text")
    )


def _ultimo_del_usuario(mensajes):
    for mensaje in reversed(mensajes):
        if getattr(mensaje, "type", "") == "human":
            return _texto_de(mensaje.content)
    return ""


async def delegar(state: MessagesState, config: RunnableConfig) -> dict:
    """El único nodo: reenvía el último mensaje del usuario al agente de viajes y devuelve su respuesta."""
    texto = _ultimo_del_usuario(state["messages"])
    # El identificador de la conversación del grafo se usa también como context_id remoto.
    context_id = (config.get("configurable") or {}).get("thread_id") or str(uuid.uuid4())
    url = _url_viajes()
    try:
        agente = await remoto.obtener_cliente(url)
        respuesta = await remoto.preguntar(agente, texto, context_id)
        ficha = remoto.FICHAS.get(url.rstrip("/"))
        origen = {"agente_remoto": ficha.name if ficha else "desconocido", "context_id": context_id}
    except remoto.ErrorRemoto as error:
        respuesta = f"Error: no pude consultar al agente de viajes ({error})."
        origen = {"agente_remoto": None, "context_id": context_id}
    return {"messages": [AIMessage(content=respuesta, additional_kwargs=origen)]}


_constructor = StateGraph(MessagesState)
_constructor.add_node("delegar", delegar)
_constructor.add_edge(START, "delegar")
_constructor.add_edge("delegar", END)

graph = _constructor.compile(checkpointer=MemorySaver())


def _entrada(texto):
    return {"messages": [{"role": "user", "content": texto}]}


def _config(context_id):
    # thread_id es la "carpeta" donde el grafo guarda la memoria de esa conversación.
    return {"configurable": {"thread_id": context_id}}


async def responder(texto, context_id):
    """Contrato de todos los agentes: recibe texto y context_id, devuelve texto."""
    try:
        resultado = await asyncio.wait_for(
            graph.ainvoke(_entrada(texto), _config(context_id)), timeout=TIMEOUT_RESPUESTA
        )
    except asyncio.TimeoutError:
        raise RuntimeError(f"no hubo respuesta en {TIMEOUT_RESPUESTA} segundos") from None
    return _texto_de(resultado["messages"][-1].content)


async def saltos(texto):
    """Corre el coordinador mostrando por qué nodo pasa y a quién le preguntó. Devuelve la respuesta final."""
    total = 0
    respuesta = ""
    async for actualizacion in graph.astream(
        _entrada(texto), _config(str(uuid.uuid4())), stream_mode="updates"
    ):
        for nodo, cambios in actualizacion.items():
            total += 1
            print(f"[salto {total}] nodo: {nodo}")
            for mensaje in (cambios or {}).get("messages", []):
                if getattr(mensaje, "type", "") != "ai":
                    continue
                datos = getattr(mensaje, "additional_kwargs", {}) or {}
                if datos.get("agente_remoto"):
                    print(f"    llamó por A2A a '{datos['agente_remoto']}' en {_url_viajes()}")
                    print(f"    con el context_id {datos['context_id']}")
                else:
                    print(f"    NO pudo hablar con el agente remoto (context_id {datos.get('context_id')})")
                respuesta = _texto_de(mensaje.content)
    print(f"Total: {total} saltos\n")
    return respuesta


def diagrama():
    """Devuelve la estructura del grafo en Mermaid, sin ejecutarlo."""
    return graph.get_graph().draw_mermaid()
