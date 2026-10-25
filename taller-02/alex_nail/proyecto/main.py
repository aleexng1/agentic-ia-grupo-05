# Punto de entrada CLI: python main.py <nombre_agente> "pregunta" [--saltos] [--diagrama]
# Cada agente vive en src/<nombre_agente>/graph.py y expone construir_grafo() (y opcionalmente detalle_saltos(estado)).
import argparse
import importlib
import sys
import warnings
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))
warnings.filterwarnings("ignore", category=DeprecationWarning)


def cargar_agente(nombre: str):
    if not nombre.isidentifier() or not (RAIZ / "src" / nombre / "graph.py").is_file():
        disponibles = sorted(p.parent.name for p in (RAIZ / "src").glob("*/graph.py"))
        raise SystemExit(f"No existe el agente '{nombre}'. Disponibles: {', '.join(disponibles) or 'ninguno'}")
    return importlib.import_module(f"src.{nombre}.graph")


def main() -> int:
    parser = argparse.ArgumentParser(description="Ejecuta un agente LangGraph del proyecto")
    parser.add_argument("agente", help="nombre del agente (carpeta en src/)")
    parser.add_argument("pregunta", nargs="?", help="pregunta para el agente")
    parser.add_argument("--saltos", action="store_true", help="muestra los nodos por los que pasó el grafo")
    parser.add_argument("--diagrama", action="store_true", help="imprime el Mermaid del grafo sin ejecutarlo")
    parser.add_argument("--hilo", default="cli", help="thread_id de la memoria (por defecto: cli)")
    args = parser.parse_args()

    modulo = cargar_agente(args.agente)
    grafo = modulo.construir_grafo()

    if args.diagrama:
        print(grafo.get_graph().draw_mermaid())
        return 0
    if not args.pregunta:
        parser.error("falta la pregunta (o usa --diagrama)")

    config = {"configurable": {"thread_id": args.hilo}}
    ruta = []
    try:
        for paso in grafo.stream({"pregunta": args.pregunta}, config, stream_mode="updates"):
            ruta.extend(paso)
    except Exception as e:
        if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
            print("FALLÓ: Gemini respondió 429 (cuota agotada). Espera a que se reinicie la cuota y vuelve a intentar.")
        else:
            print(f"FALLÓ: {type(e).__name__}: {e}")
        return 1
    estado = grafo.get_state(config).values

    print(estado.get("respuesta", ""))
    if args.saltos:
        print("\n--- saltos ---")
        print("Ruta: " + " → ".join(ruta))
        if hasattr(modulo, "detalle_saltos"):
            for linea in modulo.detalle_saltos(estado):
                print(linea)
    return 0


if __name__ == "__main__":
    sys.exit(main())
