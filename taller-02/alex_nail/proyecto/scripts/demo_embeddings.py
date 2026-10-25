# Demo: qué es un embedding y cómo el parecido coseno detecta frases que dicen lo mismo.
# Uso: python scripts/demo_embeddings.py ["frase 1" "frase 2" "frase 3"] [--pregunta "texto"]
import argparse
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.rag.storage import get_embeddings  # noqa: E402

FRASES_EJEMPLO = ["¿Cómo reinicio el router?", "El router no da internet", "Receta de pan amasado"]


def coseno(a, b) -> float:
    a, b = np.asarray(a), np.asarray(b)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def main():
    parser = argparse.ArgumentParser(description="Demo de embeddings y parecido coseno")
    parser.add_argument("frases", nargs="*", help="tres frases (opcional)")
    parser.add_argument("--pregunta", default="no tengo internet")
    args = parser.parse_args()

    if args.frases and len(args.frases) != 3:
        parser.error("pasa exactamente tres frases, o ninguna para usar las de ejemplo")
    frases = args.frases or FRASES_EJEMPLO

    embeddings = get_embeddings()
    vectores = embeddings.embed_documents(frases)

    print("== Vectores ==")
    for i, (frase, v) in enumerate(zip(frases, vectores), 1):
        primeros = ", ".join(f"{x:+.4f}" for x in v[:5])
        print(f"[{i}] {frase!r}\n    {len(v)} números · primeros 5: [{primeros}, ...]")

    pares = sorted(
        ((coseno(vectores[i], vectores[j]), i, j) for i, j in combinations(range(len(frases)), 2)),
        reverse=True,
    )
    print("\n== Parecido coseno entre pares (1 = idénticas; importa la comparación entre pares, no el valor absoluto) ==")
    print(f"{'par':<8}{'parecido':>10}")
    for k, (sim, i, j) in enumerate(pares):
        marca = "  ← más parecido" if k == 0 else ""
        print(f"[{i + 1}]-[{j + 1}]  {sim:>10.4f}{marca}")

    vp = embeddings.embed_query(args.pregunta)
    cercanias = sorted(((coseno(vp, v), i) for i, v in enumerate(vectores)), reverse=True)
    print(f"\n== Pregunta: {args.pregunta!r} ==")
    for sim, i in cercanias:
        print(f"  {sim:.4f}  [{i + 1}] {frases[i]}")
    sim, i = cercanias[0]
    print(f"\nLa frase más cercana a la pregunta es [{i + 1}] {frases[i]!r} (parecido {sim:.4f}).")


if __name__ == "__main__":
    main()
