"""Envía ejemplos al supervisor y muestra sus decisiones en una tabla."""

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


PREGUNTAS = [
    "Necesito un vuelo de SCL a LIM para 2026-12-10.",
    "Busca hoteles en Lima para dos noches.",
    "Recomiéndame restaurantes peruanos en Lima.",
    "Dame los detalles de Don Julio en Buenos Aires.",
    "Estoy en Buenos Aires, ¿qué me recomiendas?",
    "Explícame cómo resolver una integral cuadrática.",
]
ANCHOS_COLUMNAS = (2, 24, 22, 25, 36)


def _una_linea(texto: str) -> str:
    """Normaliza mensajes para mostrarlos en la tabla."""
    return " ".join(texto.replace("\r", " ").replace("\n", " ").split())


def _separador() -> str:
    """Crea el borde horizontal de la tabla."""
    return "+" + "+".join("-" * (ancho + 2) for ancho in ANCHOS_COLUMNAS) + "+"


def _imprimir_fila(celdas: tuple[str, ...]) -> None:
    """Imprime una fila, envolviendo celdas largas en varias líneas."""
    envueltas = [
        textwrap.wrap(_una_linea(texto), width=ancho) or [""]
        for texto, ancho in zip(celdas, ANCHOS_COLUMNAS)
    ]
    alto = max(len(celda) for celda in envueltas)
    for indice in range(alto):
        valores = [
            (celda[indice] if indice < len(celda) else "").ljust(ancho)
            for celda, ancho in zip(envueltas, ANCHOS_COLUMNAS)
        ]
        print("| " + " | ".join(valores) + " |")


def _analizar_respuesta(respuesta: str) -> tuple[str, str, str]:
    """Lee agente, motivo y comienzo de la respuesta del coordinador."""
    lineas = respuesta.splitlines()
    agente = "ninguno"
    motivo = "No informado"
    texto_respuesta = respuesta

    if lineas and lineas[0].startswith("[") and "]" in lineas[0]:
        agente = lineas[0][1 : lineas[0].find("]")]
        for indice, linea in enumerate(lineas[1:], start=1):
            if linea.startswith("Motivo:"):
                motivo = linea.partition(":")[2].strip()
            if linea.startswith("Respuesta:"):
                texto_respuesta = " ".join(lineas[indice:]).partition(":")[2].strip()
                break
    else:
        for linea in lineas:
            if linea.startswith("Motivo:"):
                motivo = linea.partition(":")[2].strip()
            if linea.startswith("Respuesta:"):
                texto_respuesta = linea.partition(":")[2].strip()

    inicio = _una_linea(texto_respuesta)
    if len(inicio) > 110:
        inicio = inicio[:107].rstrip() + "..."
    return agente, motivo, inicio


async def _probar() -> int:
    """Consulta seis casos independientes al servidor del coordinador."""
    load_dotenv()
    url = os.getenv("URL_COORDINADOR", "http://127.0.0.1:8002").strip().rstrip("/")
    filas = []

    try:
        cliente = await obtener_cliente(url)
        for numero, texto in enumerate(PREGUNTAS, start=1):
            context_id = str(uuid4())
            respuesta = await preguntar(cliente, texto, context_id)
            agente, motivo, inicio = _analizar_respuesta(respuesta)
            filas.append((str(numero), texto, agente, motivo, inicio))
    except Exception as error:
        detalle = _una_linea(str(error)) or error.__class__.__name__
        print(f"No se pudo probar el supervisor: {detalle}")
        return 1
    finally:
        await cerrar_clientes()

    print("\nDECISIONES DEL SUPERVISOR · 6 PREGUNTAS")
    print(_separador())
    _imprimir_fila(("#", "Pregunta", "Agente elegido", "Motivo", "Inicio de respuesta"))
    print(_separador())
    for fila in filas:
        _imprimir_fila(fila)
        print(_separador())
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_probar()))
