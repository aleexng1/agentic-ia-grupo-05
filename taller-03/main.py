import argparse
import asyncio
import importlib
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.errors import GraphRecursionError

RAIZ = Path(__file__).resolve().parent
MAX_LLAMADAS_TOOLS = 6
# cada vuelta (modelo -> tools) cuenta 2 pasos, más el paso final del modelo
RECURSION_LIMIT = MAX_LLAMADAS_TOOLS * 2 + 1
RESUMEN_CHARS = 200


def a_texto(contenido) -> str:
    if isinstance(contenido, str):
        return contenido
    if isinstance(contenido, list):
        return "\n".join(
            b["text"] if isinstance(b, dict) and "text" in b else str(b)
            for b in contenido
        )
    return str(contenido)


def imprimir_salto(nodo: str, mensajes: list, pendientes: dict) -> None:
    print(f"[nodo] {nodo}")
    for msg in mensajes:
        if isinstance(msg, AIMessage):
            for llamada in msg.tool_calls:
                pendientes[llamada["id"]] = llamada
        elif isinstance(msg, ToolMessage):
            texto = a_texto(msg.content)
            llamada = pendientes.get(msg.tool_call_id, {})
            args = llamada.get("args", {})
            resumen = texto[:RESUMEN_CHARS].replace("\n", " ")
            print(f"  tool: {msg.name}({args})")
            print(f"    resultado: {resumen}{'...' if len(texto) > RESUMEN_CHARS else ''}")
            print(f"    caracteres devueltos: {len(texto)}")


async def ejecutar(agente, mensaje: str, thread_id: str, saltos: bool) -> str | None:
    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": RECURSION_LIMIT}
    entrada = {"messages": [{"role": "user", "content": mensaje}]}
    pendientes: dict = {}
    respuesta = None
    if saltos:
        print("[nodo] __start__")
    async for paso in agente.astream(entrada, config, stream_mode="updates"):
        for nodo, update in paso.items():
            mensajes = (update or {}).get("messages", [])
            if saltos:
                imprimir_salto(nodo, mensajes, pendientes)
            for msg in mensajes:
                if isinstance(msg, AIMessage) and not msg.tool_calls:
                    respuesta = a_texto(msg.content)
    if saltos:
        print("[nodo] __end__")
    return respuesta


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
