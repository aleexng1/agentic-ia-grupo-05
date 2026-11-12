"""Punto de entrada para ejecutar los agentes desde la terminal."""

import asyncio
import importlib
import sys


AGENTES = {
    "coordinador": "src.coordinador",
    "matias": "src.agente_matias",
    "alex": "src.agente_alex",
    "eduardo": "src.agente_eduardo",
    "sebastian": "src.agente_sebastian",
}


def _cargar_agente(nombre):
    """Carga el grafo del agente, si ya está implementado."""
    paquete = AGENTES[nombre]
    try:
        return importlib.import_module(f"{paquete}.graph")
    except ModuleNotFoundError as error:
        if error.name not in (paquete, f"{paquete}.graph"):
            raise
        return None


def main(argumentos=None):
    """Interpreta el agente, la pregunta y el modo de ejecución."""
    argumentos = list(sys.argv[1:] if argumentos is None else argumentos)
    modo = None
    if "--saltos" in argumentos:
        modo = "saltos"
        argumentos.remove("--saltos")
    if "--diagrama" in argumentos:
        modo = "diagrama"
        argumentos.remove("--diagrama")

    if (
        not argumentos
        or argumentos[0] not in AGENTES
        or (len(argumentos) < 2 and modo != "diagrama")
    ):
        print('Uso: python main.py {coordinador|matias|alex|eduardo|sebastian} "pregunta" [--saltos|--diagrama]')
        return 1

    nombre = argumentos[0]
    texto = " ".join(argumentos[1:]) if len(argumentos) > 1 else ""
    agente = _cargar_agente(nombre)
    if agente is None:
        print("Ese agente todavía no existe.")
        return 0

    if modo == "saltos":
        agente.saltos(texto)
    elif modo == "diagrama":
        agente.diagrama()
    else:
        try:
            print(asyncio.run(agente.responder(texto, context_id=f"consola-{nombre}")))
        except Exception as error:
            detalle = str(error).replace("\r", " ").replace("\n", " ").strip()
            if not detalle:
                detalle = error.__class__.__name__
            print(f"No se pudo ejecutar el agente: {detalle}")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
