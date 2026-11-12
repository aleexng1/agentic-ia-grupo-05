"""Ejecuta un agente desde la terminal.

    python main.py {nombre_agente} "mensaje"
    python main.py {nombre_agente} "mensaje" --saltos
    python main.py {nombre_agente} --diagrama
"""

import argparse
import importlib
import sys


def cargar_grafo(nombre_agente: str):
    try:
        modulo = importlib.import_module(f"src.{nombre_agente}.graph")
    except ModuleNotFoundError:
        sys.exit(f"No existe el agente '{nombre_agente}' (se esperaba src/{nombre_agente}/graph.py).")
    return modulo.construir_grafo()


def main() -> None:
    p = argparse.ArgumentParser(description="Ejecuta un agente de src/.")
    p.add_argument("agente", help="nombre de la carpeta en src/, por ejemplo: router")
    p.add_argument("mensaje", nargs="?", help="mensaje del cliente")
    p.add_argument("--saltos", action="store_true", help="imprime los nodos recorridos")
    p.add_argument("--diagrama", action="store_true", help="imprime el diagrama Mermaid sin ejecutar")
    p.add_argument("--thread", default="cli", help="thread_id para la memoria (por defecto: cli)")
    args = p.parse_args()

    grafo = cargar_grafo(args.agente)

    if args.diagrama:
        print(grafo.get_graph().draw_mermaid())
        return

    if not args.mensaje:
        p.error("falta el mensaje (o usa --diagrama)")

    config = {"configurable": {"thread_id": args.thread}}
    saltos = []
    for paso in grafo.stream({"mensaje": args.mensaje}, config, stream_mode="updates"):
        saltos.extend(paso.keys())

    estado = grafo.get_state(config).values
    if args.saltos:
        print("saltos:   ", " → ".join(saltos))
    print("ruta:     ", estado.get("ruta"))
    print("motivo:   ", estado.get("motivo"))
    print("respuesta:", estado.get("respuesta"))


if __name__ == "__main__":
    main()
