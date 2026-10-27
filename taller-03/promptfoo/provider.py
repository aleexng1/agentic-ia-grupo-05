"""Provider de promptfoo: ejecuta el agente colombia completo (guardias + agente + tools)."""
import os
import sys
import uuid
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(RAIZ / ".env")

from langgraph.errors import GraphRecursionError  # noqa: E402

from src.colombia.graph import construir_agente  # noqa: E402
from src.ejecucion import MAX_LLAMADAS_TOOLS, ejecutar_grafo  # noqa: E402


async def call_api(prompt, options, context):
    """Async: promptfoo la corre con asyncio.run, o sea un event loop nuevo por caso.

    Por eso el agente se construye dentro de cada llamada: los clientes del modelo y del
    MCP quedan atados al loop que los creó, y así tampoco se arrastra estado entre casos.
    """
    if not os.getenv("GOOGLE_API_KEY"):
        return {"error": "Falta GOOGLE_API_KEY en el .env de taller-03/."}
    try:
        agente = await construir_agente()
        resultado = await ejecutar_grafo(agente, prompt, thread_id=str(uuid.uuid4()))
    except GraphRecursionError:
        return {"error": f"El agente necesitó más de {MAX_LLAMADAS_TOOLS} consultas y se detuvo."}
    except Exception as exc:
        # solo el tipo de error: el mensaje original podría traer datos de la petición
        texto = str(exc)
        if "429" in texto or "RESOURCE_EXHAUSTED" in texto:
            return {"error": "Se agotó la cuota del modelo (429). Espera un momento o baja la concurrencia."}
        return {"error": f"No se pudo ejecutar el agente ({type(exc).__name__})."}
    if not resultado.respuesta:
        return {"error": "El agente terminó sin dar una respuesta."}

    veredicto = resultado.veredicto or {}
    revision = resultado.revision
    return {
        "output": resultado.respuesta,
        "metadata": {
            "ruta": " > ".join(resultado.ruta),
            "tools": resultado.tools,
            "veredicto_entrada": veredicto.get("permitido"),
            "categoria": veredicto.get("categoria"),
            "revision_salida": revision,
            "reintento": resultado.reintento,
            "caracteres_guardia": revision["chars_enviados"] if revision else None,
        },
    }
