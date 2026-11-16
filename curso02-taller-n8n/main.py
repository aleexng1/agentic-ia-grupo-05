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

from src.memoria import abrir_memoria


def importar_agente(nombre_agente: str):
    try:
        return importlib.import_module(f"src.{nombre_agente}.graph")
    except ModuleNotFoundError:
        sys.exit(f"No existe el agente '{nombre_agente}' (se esperaba src/{nombre_agente}/graph.py).")


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
        print(agente.construir_grafo().get_graph().draw_mermaid())
        return

    if not args.mensaje:
        p.error("falta el mensaje (o usa --diagrama)")

    memoria = abrir_memoria()
    try:
        if memoria.tipo == "ram":
            print(f"⚠ memoria en RAM (no se guarda): {memoria.motivo}", file=sys.stderr)
        grafo = agente.construir_grafo(memoria.checkpointer)

        config = {"configurable": {"thread_id": args.hilo}}
        saltos = []
        for paso in grafo.stream({"mensaje": args.mensaje}, config, stream_mode="updates"):
            saltos.extend(paso.keys())
        estado = grafo.get_state(config).values
    finally:
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
