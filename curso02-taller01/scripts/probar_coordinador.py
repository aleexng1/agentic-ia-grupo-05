"""Le hace dos preguntas seguidas al coordinador con el mismo context_id y muestra si recuerda.

Antes hay que tener corriendo el agente de viajes (puerto 8000) y el coordinador (puerto 8002).

Uso, desde curso02-taller01/:
    python scripts/probar_coordinador.py
"""

import asyncio
import os
import sys
import uuid
from pathlib import Path

# Permite correrlo como "python scripts/probar_coordinador.py" desde curso02-taller01/.
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from dotenv import load_dotenv  # noqa: E402

from src.coordinador.cliente import ErrorRemoto, cerrar_clientes, obtener_cliente, preguntar  # noqa: E402

load_dotenv(RAIZ / ".env")

PREGUNTA_1 = "Busca vuelos de Santiago a Lima el 2026-11-10"
PREGUNTA_2 = "¿Cuál de esos vuelos es el más barato?"
# En los datos inventados, el vuelo más barato de SCL a LIM es JetSMART a 99.000 CLP.
PISTAS_MEMORIA = ("jetsmart", "99.000", "99000", "99 000")


async def principal():
    url = os.getenv("URL_COORDINADOR", "http://127.0.0.1:8002")
    context_id = str(uuid.uuid4())
    print(f"Coordinador: {url}\ncontext_id:   {context_id}\n")
    try:
        cliente = await obtener_cliente(url)
        print(f"Pregunta 1: {PREGUNTA_1}")
        respuesta_1 = await preguntar(cliente, PREGUNTA_1, context_id)
        print(f"Respuesta 1:\n{respuesta_1}\n")
        print(f"Pregunta 2: {PREGUNTA_2}")
        respuesta_2 = await preguntar(cliente, PREGUNTA_2, context_id)
        print(f"Respuesta 2:\n{respuesta_2}\n")
    except ErrorRemoto as error:
        print(f"Error: {error}")
        return 1
    finally:
        await cerrar_clientes()

    if any(pista in respuesta_2.lower() for pista in PISTAS_MEMORIA):
        print("OK: la segunda respuesta habla del vuelo más barato de la primera (JetSMART, 99.000 CLP): hay memoria.")
        return 0
    print("No pude confirmar la memoria: la segunda respuesta no menciona el vuelo más barato (JetSMART, 99.000 CLP).")
    print("Revisa la respuesta 2 a ojo; el modelo puede haberla escrito distinto.")
    return 2


if __name__ == "__main__":
    sys.exit(asyncio.run(principal()))
