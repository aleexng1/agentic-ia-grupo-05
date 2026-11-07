"""Punto de entrada para correr un agente desde la terminal, sin servidor.

Uso:
    python main.py viajes "pregunta"
    python main.py viajes "pregunta" --saltos
    python main.py viajes --diagrama
"""

import argparse
import asyncio
import importlib
import inspect
import sys
import uuid

# Nombre que escribe el usuario -> paquete donde vive el agente.
AGENTES = {
    "viajes": "src.agente_viajes",
    "restaurantes": "src.agente_restaurantes",
    "coordinador": "src.coordinador",
}


def cargar_modulo(agente):
    """Importa graph.py o crew.py del agente. Devuelve None si todavía no existe."""
    paquete = AGENTES[agente]
    for archivo in ("graph", "crew"):
        nombre = f"{paquete}.{archivo}"
        try:
            return importlib.import_module(nombre)
        except ModuleNotFoundError as error:
            # Solo significa "no existe" si falta ese archivo; si falta otra
            # librería dentro de él, el error es otro y se deja subir.
            if error.name != nombre:
                raise
    return None


async def ejecutar(funcion, *argumentos):
    """Llama a la función del agente, sea normal o async."""
    resultado = funcion(*argumentos)
    if inspect.isawaitable(resultado):
        resultado = await resultado
    return resultado


def main():
    parser = argparse.ArgumentParser(description="Corre un agente desde la terminal.")
    parser.add_argument("agente", choices=sorted(AGENTES), help="agente a correr")
    parser.add_argument("pregunta", nargs="?", default="", help="pregunta para el agente")
    parser.add_argument("--saltos", action="store_true", help="muestra por qué nodos y herramientas pasó")
    parser.add_argument("--diagrama", action="store_true", help="imprime su estructura en Mermaid sin ejecutarlo")
    args = parser.parse_args()

    try:
        modulo = cargar_modulo(args.agente)
    except Exception as error:  # Por ejemplo, falta la clave o una librería.
        detalle = " ".join(f"{type(error).__name__}: {error}".split())
        print(f"Error: no se pudo cargar el agente '{args.agente}' ({detalle})")
        return 1
    if modulo is None:
        print(f"Error: el agente '{args.agente}' todavía no existe.")
        return 1

    try:
        if args.diagrama:
            print(modulo.diagrama())
        elif not args.pregunta:
            print("Error: falta la pregunta. Uso: python main.py {agente} \"pregunta\"")
            return 1
        elif args.saltos:
            print(asyncio.run(ejecutar(modulo.saltos, args.pregunta)))
        else:
            context_id = str(uuid.uuid4())
            print(asyncio.run(ejecutar(modulo.responder, args.pregunta, context_id)))
    except Exception as error:  # Una sola línea entendible, sin stack trace.
        print(f"Error: {type(error).__name__}: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
