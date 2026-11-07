"""Le manda 6 preguntas al coordinador (cada una en una conversación nueva) y muestra qué agente eligió.

Antes hay que tener corriendo: agente de viajes (8000), agente de restaurantes (8001) y coordinador (8002).

Uso, desde curso02-taller01/:
    python scripts/probar_supervisor.py

El agente elegido se ve en el prefijo "[Agente ...]" de la respuesta A2A. El motivo no viaja en A2A:
se lee de la ruta auxiliar GET /decision/{context_id} del coordinador (si no está, se muestra "-").
"""

import asyncio
import os
import re
import sys
import uuid
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import httpx  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

from src.coordinador.cliente import ErrorRemoto, cerrar_clientes, obtener_cliente, preguntar  # noqa: E402

load_dotenv(RAIZ / ".env")

PREGUNTAS = [
    ("viajes", "Busca vuelos de Santiago a Lima el 2026-11-10"),
    ("viajes", "Hoteles en Bogotá por 3 noches"),
    ("restaurantes", "Algo peruano en Lima, zona Miraflores"),
    ("restaurantes", "¿Dónde puedo comer parrilla en Buenos Aires?"),
    ("ambigua", "Voy a Buenos Aires la próxima semana, ¿qué me recomiendas?"),
    ("ninguno", "¿Cuál es la capital de Francia?"),
]
ANCHOS = (10, 24, 34, 40)  # esperado, agente elegido, motivo, inicio de la respuesta
TIMEOUT_MOTIVO = 5.0


def _recortar(texto, largo):
    texto = " ".join(str(texto).split())
    return texto if len(texto) <= largo else texto[: largo - 3] + "..."


def _agente_del_prefijo(respuesta):
    coincidencia = re.match(r"\[(.+?)\]", respuesta)
    if coincidencia:
        return coincidencia.group(1)
    return "(ninguno)" if respuesta.startswith("No tengo") else "(?)"


async def _motivo(http, url, context_id):
    try:
        r = await http.get(f"{url.rstrip('/')}/decision/{context_id}", timeout=TIMEOUT_MOTIVO)
        return r.json().get("motivo") or "-" if r.status_code == 200 else "-"
    except (httpx.HTTPError, ValueError):
        return "-"


def _fila(columnas):
    return " | ".join(_recortar(c, a).ljust(a) for c, a in zip(columnas, ANCHOS))


async def principal():
    url = os.getenv("URL_COORDINADOR", "http://127.0.0.1:8002")
    print(f"Coordinador: {url}\n")
    filas = []
    try:
        cliente = await obtener_cliente(url)
        async with httpx.AsyncClient() as http:
            for esperado, pregunta in PREGUNTAS:
                context_id = str(uuid.uuid4())  # conversación nueva para cada pregunta
                print(f"Preguntando: {pregunta}")
                respuesta = await preguntar(cliente, pregunta, context_id)
                filas.append((pregunta, esperado, _agente_del_prefijo(respuesta),
                              await _motivo(http, url, context_id), respuesta))
    except ErrorRemoto as error:
        print(f"Error: {error}")
        return 1
    finally:
        await cerrar_clientes()

    print("\nCada pregunta (P:) va seguida de su fila. 'Esperado' es lo que debería elegir el supervisor.")
    print("-" * 120)
    print(_fila(("Esperado", "Agente elegido", "Motivo", "Inicio de la respuesta")))
    print("-" * 120)
    for pregunta, esperado, agente, motivo, respuesta in filas:
        print(f"P: {pregunta}")
        sin_prefijo = re.sub(r"^\[.+?\]\s*", "", respuesta)
        print(_fila((esperado, agente, motivo, sin_prefijo)))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(principal()))
