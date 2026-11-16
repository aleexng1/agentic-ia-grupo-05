"""Ejecuta un agente desde la terminal, con la misma memoria que la API.

    python main.py {nombre_agente} "mensaje"
    python main.py {nombre_agente} "mensaje" --hilo NOMBRE
    python main.py {nombre_agente} "mensaje" --saltos
    python main.py {nombre_agente} --diagrama

La memoria va a Postgres si hay DATABASE_URL (esquema DB_SCHEMA) y, si no, a RAM.
Cada ejecución abre su conexión y la cierra al terminar.
"""

import argparse
import importlib
import sys

from langgraph.pregel import Pregel

from src.memoria import abrir_memoria
from src.router import reclamos


def importar_agente(nombre_agente: str):
    try:
        return importlib.import_module(f"src.{nombre_agente}.graph")
    except ModuleNotFoundError:
        sys.exit(f"No existe el agente '{nombre_agente}' (se esperaba src/{nombre_agente}/graph.py).")


def correr(grafo, mensaje: str, config: dict) -> list[str]:
    """Ejecuta el grafo con un mensaje y devuelve los saltos: los nodos recorridos y, tras el nodo de un
    agente, las herramientas que usó (p. ej. router, agente_preventa, buscar_productos, ver_producto)."""
    saltos: list[str] = []
    herramientas: dict[str, list[str]] = {}  # nodo del grafo -> herramientas que usó
    for ruta_sub, paso in grafo.stream({"mensaje": mensaje}, config, stream_mode="updates", subgraphs=True):
        if ruta_sub:  # paso interno de un agente: interesa qué herramientas usó
            nodo = ruta_sub[0].split(":")[0]
            for resultado in (paso.get("tools") or {}).get("messages", []):
                herramientas.setdefault(nodo, []).append(getattr(resultado, "name", None) or "herramienta")
        else:
            for nodo in paso:  # el agente termina después de sus herramientas: se listan tras su nodo
                saltos.append(nodo)
                saltos.extend(herramientas.pop(nodo, []))
    return saltos


def main() -> None:
    p = argparse.ArgumentParser(description="Ejecuta un agente de src/.")
    p.add_argument("agente", help="nombre de la carpeta en src/, por ejemplo: router")
    p.add_argument("mensaje", nargs="?", help="mensaje del cliente")
    p.add_argument("--saltos", action="store_true", help="imprime los nodos recorridos")
    p.add_argument("--diagrama", action="store_true", help="imprime el diagrama Mermaid sin ejecutar")
    p.add_argument("--hilo", "--thread", dest="hilo", default="cli", metavar="NOMBRE",
                   help="thread_id de la conversación (por defecto: cli)")
    args = p.parse_args()

    agente = importar_agente(args.agente)

    if args.diagrama:  # no necesita memoria ni base de datos
        grafo = agente.construir_grafo()
        print(grafo.get_graph().draw_mermaid())
        # Los agentes internos (p. ej. agente_preventa, con su ciclo modelo <-> herramientas) se dibujan aparte.
        for nombre, nodo in grafo.nodes.items():
            if isinstance(nodo.bound, Pregel):
                print(f"\n%% Agente interno: {nombre}")
                print(nodo.bound.get_graph().draw_mermaid())
        return

    if not args.mensaje:
        p.error("falta el mensaje (o usa --diagrama)")

    memoria = abrir_memoria()
    try:
        if memoria.tipo == "ram":
            print(f"⚠ memoria en RAM (no se guarda): {memoria.motivo}", file=sys.stderr)
        reclamos.configurar(memoria)  # tabla de reclamos (si el agente los usa) con el pool de la memoria
        grafo = agente.construir_grafo(memoria.checkpointer)

        config = {"configurable": {"thread_id": args.hilo}}
        saltos = correr(grafo, args.mensaje, config)
        estado = grafo.get_state(config).values
    finally:
        reclamos.detener()
        memoria.cerrar()

    destino = f"postgres (esquema {memoria.esquema})" if memoria.tipo == "postgres" else "ram"
    print("hilo:     ", args.hilo)
    print("memoria:  ", destino)
    if args.saltos:
        print("saltos:   ", " → ".join(saltos))
    print("ruta:     ", estado.get("ruta"))
    print("motivo:   ", estado.get("motivo"))
    print("respuesta:", estado.get("respuesta"))


if __name__ == "__main__":
    main()
