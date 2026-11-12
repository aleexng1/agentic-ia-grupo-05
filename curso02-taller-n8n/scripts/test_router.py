"""Evalúa el router contra tests/casos_router.json e imprime una tabla.

    python scripts/test_router.py
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.router.graph import construir_grafo  # noqa: E402

CASOS = RAIZ / "tests" / "casos_router.json"


def cargar_casos() -> list[dict]:
    return json.loads(CASOS.read_text(encoding="utf-8"))


def evaluar(casos: list[dict] | None = None) -> list[dict]:
    """Clasifica cada caso en un hilo propio y devuelve los resultados."""
    casos = casos if casos is not None else cargar_casos()
    grafo = construir_grafo()
    resultados = []
    for i, caso in enumerate(casos):
        estado = grafo.invoke(
            {"mensaje": caso["mensaje"]},
            {"configurable": {"thread_id": f"eval-{i}"}},
        )
        resultados.append({
            **caso,
            "obtenido": estado["ruta"],
            "motivo": estado["motivo"],
            "ok": estado["ruta"] == caso["esperado"],
        })
    return resultados


def corto(texto: str, ancho: int) -> str:
    return texto if len(texto) <= ancho else texto[: ancho - 1] + "…"


def imprimir(resultados: list[dict]) -> None:
    fila = "{:<46}  {:<9}  {:<9}  {:<2}  {}"
    print(fila.format("mensaje", "esperado", "obtenido", "", "motivo"))
    print("─" * 120)
    for r in resultados:
        print(fila.format(
            corto(r["mensaje"], 46), r["esperado"], r["obtenido"],
            "✔" if r["ok"] else "✘", corto(r["motivo"], 60),
        ))

    aciertos = sum(r["ok"] for r in resultados)
    total = len(resultados)
    print("─" * 120)
    print(f"Aciertos: {aciertos}/{total} ({aciertos / total:.0%})")
    fallados = [r for r in resultados if not r["ok"]]
    if fallados:
        print("Fallados:")
        for r in fallados:
            print(f"  ✘ {r['mensaje']!r}: esperado {r['esperado']}, obtenido {r['obtenido']} — {r['motivo']}")
    else:
        print("Fallados: ninguno")


if __name__ == "__main__":
    imprimir(evaluar())
