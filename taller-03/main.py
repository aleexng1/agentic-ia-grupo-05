import argparse
import asyncio
import importlib
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.errors import GraphRecursionError

from src.ejecucion import MAX_LLAMADAS_TOOLS, a_texto, ejecutar_grafo

RAIZ = Path(__file__).resolve().parent
RESUMEN_CHARS = 200


def imprimir_salto(ruta: str, nodo: str, update: dict, pendientes: dict) -> None:
    sangria = "  " if "/" in ruta else ""
    print(f"{sangria}[nodo] {ruta}")
    veredicto = update.get("veredicto")
    if veredicto:
        print(f"{sangria}  veredicto: permitido={veredicto['permitido']} categoria={veredicto['categoria']}")
        print(f"{sangria}    motivo: {veredicto['motivo']}")
    revision = update.get("revision")
    if revision:
        print(f"{sangria}  revisión: aprobada={revision['aprobada']} problemas={revision['problemas']}")
        print(f"{sangria}    detalle: {revision['detalle']}")
        aviso = "  ¡SUPERA 100.000!" if revision["chars_enviados"] > 100_000 else ""
        print(f"{sangria}    caracteres enviados a la guardia: {revision['chars_enviados']}{aviso}")
        if revision["accion"] == "reintentar":
            reintento = "pedido ahora"
        else:
            reintento = "ya usado antes en esta pregunta" if revision["reintento_previo"] else "no hubo"
        print(f"{sangria}    reintento: {reintento}")
    if "/" not in ruta and nodo not in ("guardia_entrada",):
        # el nodo exterior de un subgrafo repite los mensajes del interior: solo se imprimen en el interior
        return
    for msg in update.get("messages", []):
        if isinstance(msg, AIMessage):
            for llamada in msg.tool_calls:
                pendientes[llamada["id"]] = llamada
        elif isinstance(msg, ToolMessage):
            texto = a_texto(msg.content)
            args = pendientes.get(msg.tool_call_id, {}).get("args", {})
            resumen = texto[:RESUMEN_CHARS].replace("\n", " ")
            print(f"{sangria}  tool: {msg.name}({args})")
            print(f"{sangria}    resultado: {resumen}{'...' if len(texto) > RESUMEN_CHARS else ''}")
            print(f"{sangria}    caracteres devueltos: {len(texto)}")


async def ejecutar(agente, mensaje: str, thread_id: str, saltos: bool) -> str | None:
    pendientes: dict = {}
    al_paso = None
    if saltos:
        print("[nodo] __start__")
        al_paso = lambda ruta, nodo, update: imprimir_salto(ruta, nodo, update, pendientes)
    resultado = await ejecutar_grafo(agente, mensaje, thread_id, al_paso)
    if saltos:
        print("[nodo] __end__")
    return resultado.respuesta


async def principal(args) -> int:
    load_dotenv(RAIZ / ".env")
    if not args.diagrama and not os.getenv("GOOGLE_API_KEY"):
        print("Falta GOOGLE_API_KEY en el archivo .env de taller-03/. Agrégala y vuelve a intentar.")
        return 1
    try:
        modulo = importlib.import_module(f"src.{args.agente}.graph")
    except ModuleNotFoundError:
        print(f"No existe el agente '{args.agente}' en src/.")
        return 1

    try:
        # para el diagrama no se llama al modelo, así que basta una clave de relleno
        agente = await modulo.construir_agente(api_key="sin-uso" if args.diagrama else None)
    except Exception as exc:
        print(f"No se pudo preparar el agente: {type(exc).__name__}: {exc}")
        return 1

    if args.diagrama:
        print(agente.get_graph().draw_mermaid())
        return 0
    if not args.mensaje:
        print("Escribe un mensaje para el agente.")
        return 1

    try:
        respuesta = await ejecutar(agente, args.mensaje, args.thread, args.saltos)
    except GraphRecursionError:
        print(
            f"La pregunta necesitó más de {MAX_LLAMADAS_TOOLS} consultas y la detuve para no "
            "dar vueltas. Prueba con una pregunta más específica."
        )
        return 1
    except Exception as exc:
        print(f"Ocurrió un error al responder: {type(exc).__name__}: {exc}")
        return 1
    print(f"\n{respuesta}" if args.saltos else respuesta)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("agente")
    parser.add_argument("mensaje", nargs="?")
    parser.add_argument("--saltos", action="store_true")
    parser.add_argument("--diagrama", action="store_true")
    parser.add_argument("--thread", default="demo")
    sys.exit(asyncio.run(principal(parser.parse_args())))
