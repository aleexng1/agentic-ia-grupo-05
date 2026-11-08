"""Comprueba el contexto compartido entre dos mensajes al coordinador."""

import asyncio
import os
import sys
import textwrap
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv


_RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
if str(_RAIZ_PROYECTO) not in sys.path:
    sys.path.insert(0, str(_RAIZ_PROYECTO))

from src.coordinador.cliente import cerrar_clientes, obtener_cliente, preguntar


def _una_linea(texto: str) -> str:
    """Reduce errores a una línea, sin imprimir trazas."""
    return " ".join(texto.replace("\r", " ").replace("\n", " ").split())


def _imprimir_bloque(titulo: str, texto: str) -> None:
    """Imprime una pregunta o respuesta en un bloque fácil de leer."""
    print(f"\n{titulo}")
    for parrafo in texto.splitlines() or [""]:
        if parrafo:
            print(
                textwrap.fill(
                    parrafo,
                    width=72,
                    initial_indent="  ",
                    subsequent_indent="  ",
                )
            )
        else:
            print()


async def _probar() -> int:
    """Envía dos preguntas A2A consecutivas dentro del mismo contexto."""
    load_dotenv()
    url = os.getenv("URL_COORDINADOR", "http://127.0.0.1:8002").strip().rstrip("/")
    context_id = str(uuid4())

    try:
        cliente = await obtener_cliente(url)
        print("\n" + "=" * 76)
        print(" PRUEBA DE CONTEXTO · COORDINADOR A2A")
        print("=" * 76)
        print(f"URL del coordinador: {url}")
        print(f"Contexto compartido: {context_id}")

        preguntas = [
            "Estoy planificando un viaje de SCL a LIM para el 2026-12-10. ¿Qué vuelos hay?",
            "¿Y qué hoteles me recomiendas allí para dos noches?",
        ]
        for numero, texto in enumerate(preguntas, start=1):
            print(f"\n{'-' * 76}\nCONSULTA {numero}\n{'-' * 76}")
            _imprimir_bloque("Pregunta:", texto)
            respuesta = await preguntar(cliente, texto, context_id)
            _imprimir_bloque("Respuesta:", respuesta)

        print(f"\n{'=' * 76}")
        print("Prueba completada: ambas preguntas usaron el mismo contexto.")
        print("=" * 76)
        return 0
    except Exception as error:
        detalle = _una_linea(str(error)) or error.__class__.__name__
        print(f"No se pudo probar el coordinador: {detalle}")
        return 1
    finally:
        await cerrar_clientes()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_probar()))
