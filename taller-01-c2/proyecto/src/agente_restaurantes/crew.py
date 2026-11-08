"""CrewAI del agente de restaurantes y memoria por contexto."""

import asyncio
import os
from uuid import uuid4

from crewai import Agent, Crew, LLM, Task
from crewai.agents.parser import AgentAction, AgentFinish
from dotenv import load_dotenv

from src.agente_restaurantes.prompts import HISTORIA, OBJETIVO, ROL
from src.agente_restaurantes.tools import buscar_restaurantes, detalle_restaurante


load_dotenv()
MODELO = os.getenv("MODELO", "gemini-3.5-flash-lite")
HISTORIAL: dict[str, list[dict[str, str]]] = {}
_CANDADOS: dict[str, asyncio.Lock] = {}


def _una_linea(texto: str) -> str:
    """Reduce un mensaje a una sola línea entendible."""
    return " ".join(texto.replace("\r", " ").replace("\n", " ").split())


def _crear_llm() -> LLM:
    """Crea el LLM Gemini y exige la clave sin imprimirla."""
    clave = os.getenv("GOOGLE_API_KEY", "").strip()
    if not clave:
        raise RuntimeError("Falta configurar GOOGLE_API_KEY en el archivo .env.")
    return LLM(model=f"gemini/{MODELO}", api_key=clave, timeout=45)


def _texto_historial(historial: list[dict[str, str]]) -> str:
    """Convierte intercambios anteriores en contexto para la tarea."""
    if not historial:
        return "No hay mensajes anteriores en esta conversación."
    return "\n".join(
        f"Usuario: {intercambio['usuario']}\nAgente: {intercambio['agente']}"
        for intercambio in historial
    )


def _crear_crew(
    texto: str,
    historial: list[dict[str, str]],
    verbose: bool = False,
    step_callback=None,
) -> Crew:
    """Arma agente, tarea y crew para una pregunta y su contexto."""
    agente = Agent(
        role=ROL,
        goal=OBJETIVO,
        backstory=HISTORIA,
        llm=_crear_llm(),
        tools=[buscar_restaurantes, detalle_restaurante],
        verbose=verbose,
        allow_delegation=False,
        max_iter=8,
    )
    tarea = Task(
        description=(
            "Responde únicamente sobre restaurantes y usa las herramientas para verificar los datos. "
            "No inventes resultados; si no hay coincidencias, indícalo brevemente.\n\n"
            f"Conversación previa:\n{_texto_historial(historial)}\n\n"
            f"Pregunta actual del usuario:\n{texto}"
        ),
        expected_output="Una recomendación o detalle breve en español, basado en las herramientas.",
        agent=agente,
    )
    return Crew(
        agents=[agente],
        tasks=[tarea],
        verbose=verbose,
        step_callback=step_callback,
        share_crew=False,
    )


async def _kickoff(crew: Crew):
    """Ejecuta CrewAI de forma asíncrona con compatibilidad de versiones."""
    metodo_async = getattr(crew, "kickoff_async", None)
    if metodo_async is not None:
        return await metodo_async()
    return await asyncio.to_thread(crew.kickoff)


def _texto_salida(salida) -> str:
    """Extrae el texto final del objeto devuelto por CrewAI."""
    contenido = getattr(salida, "raw", salida)
    return str(contenido)


async def responder(texto: str, context_id: str) -> str:
    """Responde con un Crew y conserva el historial por context_id."""
    identificador = context_id or str(uuid4())
    candado = _CANDADOS.setdefault(identificador, asyncio.Lock())

    async with candado:
        historial = list(HISTORIAL.get(identificador, []))
        crew = _crear_crew(texto, historial)
        salida = await _kickoff(crew)
        respuesta = _texto_salida(salida)
        HISTORIAL.setdefault(identificador, []).append(
            {"usuario": texto, "agente": respuesta}
        )
        return respuesta


def _callback_pasos(conteo: dict[str, int]):
    """Construye el callback que describe acciones y resultados del agente."""
    def imprimir_paso(paso) -> None:
        if isinstance(paso, AgentAction):
            conteo["herramientas"] += 1
            print(f"Pensamiento: {_una_linea(paso.thought)}")
            print(f"Herramienta llamada: {paso.tool}")
            print(f"Argumentos: {_una_linea(str(paso.tool_input))}")
        elif isinstance(paso, AgentFinish):
            print(f"Respuesta del agente: {_una_linea(str(paso.output))}")
        elif hasattr(paso, "result"):
            print(f"Resultado de herramienta: {_una_linea(str(paso.result))}")
        else:
            print(f"Paso del agente: {_una_linea(str(paso))}")

    return imprimir_paso


def saltos(texto: str) -> None:
    """Ejecuta el crew en modo detallado y cuenta las herramientas usadas."""
    identificador = "consola-restaurantes"
    historial = list(HISTORIAL.get(identificador, []))
    conteo = {"herramientas": 0}
    try:
        crew = _crear_crew(
            texto,
            historial,
            verbose=True,
            step_callback=_callback_pasos(conteo),
        )
        salida = asyncio.run(_kickoff(crew))
        respuesta = _texto_salida(salida)
        HISTORIAL.setdefault(identificador, []).append(
            {"usuario": texto, "agente": respuesta}
        )
        print(f"Respuesta final: {respuesta}")
    except Exception as error:
        detalle = _una_linea(str(error)) or error.__class__.__name__
        print(f"No se pudo completar la consulta: {detalle}")
    finally:
        print(f"Herramientas usadas: {conteo['herramientas']}")


def diagrama() -> None:
    """Imprime el diagrama Mermaid manual del crew, sin llamar al modelo."""
    print(
        "flowchart TD\n"
        '    tarea["Task: recomendar restaurantes"] --> agente["Agent: agente de restaurantes"]\n'
        '    agente --> buscar["Tool: buscar_restaurantes"]\n'
        '    agente --> detalle["Tool: detalle_restaurante"]'
    )
