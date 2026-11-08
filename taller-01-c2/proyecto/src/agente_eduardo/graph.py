"""Grafo LangGraph del agente de presupuestos de Eduardo."""

import os
import re
import unicodedata
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


def _normalizar(texto: str) -> str:
    """Normaliza tildes para comprobar los datos escritos por el usuario."""
    sin_tildes = unicodedata.normalize("NFKD", texto.casefold())
    return "".join(caracter for caracter in sin_tildes if not unicodedata.combining(caracter))


def _dato_faltante(texto: str) -> str | None:
    """Valida solicitudes de presupuesto de un solo turno mediante patrones limitados.

    El reconocimiento léxico no cubre todas las paráfrasis posibles; las consultas
    no reconocidas se dejan al agente y esta validación no acumula turnos.
    """
    solicitud = _normalizar(texto)
    solicita_presupuesto = bool(
        re.search(
            r"\b(presupuest\w*|cost\w*|cotiz\w*|cuanto\s+(?:cuesta|sale|costaria)|"
            r"estim\w*\s+(?:el\s+)?gast\w*)\b",
            solicitud,
        )
    )
    if not solicita_presupuesto:
        return None
    if not re.search(r"\b(tecnolog\w*|gastronom\w*|cultur\w*|infantil\w*|ninos)\b", solicitud):
        return "tipo de evento"
    if not re.search(r"\b\d+\s*(?:personas?|asistentes|participantes)\b", solicitud):
        return "cantidad de personas"
    if not re.search(r"\b\d+(?:[.,]\d+)?\s*(?:minutos?|mins?|horas?|hrs?|h)\b", solicitud):
        return "duración en minutos (o en horas)"
    return None


def _pregunta_dato(faltante: str) -> str:
    """Pregunta por el dato pendiente y solicita los tres datos en un solo turno."""
    preguntas = {
        "tipo de evento": "¿Qué tipo de evento es?",
        "cantidad de personas": "¿Cuántas personas asistirán?",
        "duración en minutos (o en horas)": "¿Cuál será la duración, en minutos u horas?",
    }
    return (
        f"{preguntas[faltante]} Para estimar, envíame una sola solicitud completa con "
        "tipo de evento, cantidad de personas y duración."
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
    """Ejecuta el agente; solicita presupuestos completos en un único turno.

    Los datos faltantes se preguntan sin ejecutar el grafo. No se conserva ese
    turno para combinarlo con seguimientos posteriores.
    """
    faltante = _dato_faltante(texto)
    if faltante:
        return _pregunta_dato(faltante)
    resultado = await graph.ainvoke(
        {"messages": [{"role": "user", "content": texto}]},
        config={"configurable": {"thread_id": context_id or str(uuid4())}},
    )
    return _texto_mensaje(resultado["messages"][-1])


def saltos(texto: str) -> None:
    """Imprime nodos y herramientas recorridos en una sola línea por evento."""
    faltante = _dato_faltante(texto)
    if faltante:
        print(f"Respuesta: {_pregunta_dato(faltante)}")
        print("Saltos totales: 0")
        return
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
