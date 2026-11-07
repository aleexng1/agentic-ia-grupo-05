"""El agente de restaurantes hecho con CrewAI.

Cumple el mismo contrato que el de viajes (responder, saltos, diagrama), así que
el servidor de src/comun lo expone igual aunque use otro framework.
"""

import asyncio
import os
from pathlib import Path

# Antes de importar CrewAI: sin telemetría hacia afuera y sin avisos de trazas interactivos.
os.environ.setdefault("OTEL_SDK_DISABLED", "true")
os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")

from crewai import LLM, Agent, Crew, Task  # noqa: E402
from crewai.agents.parser import AgentAction, AgentFinish  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

from src.agente_restaurantes.prompts import HISTORIA, OBJETIVO, ROL  # noqa: E402
from src.agente_restaurantes.tools import HERRAMIENTAS  # noqa: E402

# El .env está en curso02-taller01/, sin importar desde dónde se corra el programa.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

TIMEOUT_MODELO = 60  # segundos que se espera cada llamada al modelo
TIMEOUT_AGENTE = 100  # segundos máximos que puede trabajar el agente en una tarea
TIMEOUT_RESPUESTA = 120  # segundos máximos para una respuesta completa
MAX_PASOS = 6  # veces que el agente puede pensar/usar herramientas antes de rendirse
TURNOS_EN_PROMPT = 6  # cuántos turnos anteriores se le muestran al agente
TURNOS_GUARDADOS = 20  # cuántos turnos se guardan por conversación

RESULTADO_ESPERADO = (
    "Una respuesta corta en español, basada solo en lo que devolvieron las herramientas."
)

# Memoria hecha a mano: CrewAI no recuerda entre llamadas.
# context_id -> lista de (lo que dijo el usuario, lo que respondió el agente)
HISTORIALES = {}


def _crear_llm():
    """Crea el modelo Gemini. Se hace al usarlo (no al importar) para que --diagrama no pida clave."""
    return LLM(
        model="gemini/" + os.getenv("MODELO", "gemini-3.5-flash-lite"),
        api_key=os.getenv("GOOGLE_API_KEY"),
        timeout=TIMEOUT_MODELO,
        max_retries=2,
    )


def _texto_historial(historial):
    if not historial:
        return "(no hay mensajes anteriores)"
    return "\n".join(f"Usuario: {u}\nAsesor: {a}" for u, a in historial[-TURNOS_EN_PROMPT:])


def _armar_crew(texto, historial, verbose=False, step_callback=None):
    """Arma el equipo: un agente con sus dos herramientas y una tarea con la pregunta y lo hablado antes."""
    agente = Agent(
        role=ROL,
        goal=OBJETIVO,
        backstory=HISTORIA,
        tools=HERRAMIENTAS,
        llm=_crear_llm(),
        allow_delegation=False,
        max_iter=MAX_PASOS,
        max_execution_time=TIMEOUT_AGENTE,
        verbose=verbose,
    )
    tarea = Task(
        description=(
            "Conversación anterior con el usuario:\n"
            f"{_texto_historial(historial)}\n\n"
            f"Pregunta actual del usuario: {texto}\n\n"
            "Responde usando solo las herramientas."
        ),
        expected_output=RESULTADO_ESPERADO,
        agent=agente,
    )
    return Crew(agents=[agente], tasks=[tarea], verbose=verbose, step_callback=step_callback)


def _texto_de(resultado):
    """Saca el texto del resultado de CrewAI."""
    texto = getattr(resultado, "raw", None)
    return str(texto if texto is not None else resultado).strip()


async def responder(texto, context_id):
    """Contrato de todos los agentes: recibe texto y context_id, devuelve texto."""
    historial = HISTORIALES.setdefault(context_id, [])
    crew = _armar_crew(texto, historial)
    try:
        resultado = await asyncio.wait_for(crew.kickoff_async(), timeout=TIMEOUT_RESPUESTA)
    except asyncio.TimeoutError:
        raise RuntimeError(f"el modelo no respondió en {TIMEOUT_RESPUESTA} segundos") from None
    respuesta = _texto_de(resultado)
    historial.append((texto, respuesta))
    del historial[:-TURNOS_GUARDADOS]
    return respuesta


def _resumir(valor, largo=160):
    linea = " ".join(str(valor).split())
    return linea if len(linea) <= largo else linea[:largo] + "..."


# Herramientas que el agente fue usando en la corrida actual de saltos().
_herramientas_usadas = []


def _mostrar_paso(paso):
    """Se llama en cada paso del agente. Va a nivel de módulo porque CrewAI no admite callbacks locales."""
    if isinstance(paso, AgentAction):
        _herramientas_usadas.append(paso.tool)
        print(f"[paso {len(_herramientas_usadas)}]")
        if paso.thought:
            print(f"    pensó: {_resumir(paso.thought)}")
        print(f"    llamó a la herramienta {paso.tool} con {_resumir(paso.tool_input)}")
        print(f"    le devolvió: {_resumir(paso.result)}")
    elif isinstance(paso, AgentFinish):
        if paso.thought:
            print(f"    pensó: {_resumir(paso.thought)}")
        print("    terminó: dio su respuesta final")
    # Otros objetos que CrewAI envía (como el resultado crudo de la herramienta) se ignoran:
    # lo mismo ya se muestra en el AgentAction.


def saltos(texto):
    """Corre el agente mostrando cada paso. Devuelve la respuesta final."""
    _herramientas_usadas.clear()
    crew = _armar_crew(texto, [], verbose=True, step_callback=_mostrar_paso)
    respuesta = _texto_de(crew.kickoff())
    print(f"\nHerramientas usadas: {len(_herramientas_usadas)}\n")
    return respuesta


def diagrama():
    """Estructura del crew en Mermaid, armada a mano (CrewAI no la dibuja solo)."""
    lineas = [
        "graph TD;",
        '    Tarea["Task: responder la pregunta<br/>(con el historial de la conversación)"]',
        f'    Agente["Agent: {ROL}"]',
        "    Tarea --> Agente;",
    ]
    for i, herramienta in enumerate(HERRAMIENTAS, start=1):
        lineas.append(f'    H{i}[["{herramienta.name}"]]')
        lineas.append(f"    Agente --> H{i};")
    return "\n".join(lineas)
