"""Carga la política de gastos en Redis: un fragmento por política.

Dueño: rol Conocimiento y seguridad.
Uso (desde tarea-final-c1):  python scripts/cargar_indice.py
"""

import sys
from pathlib import Path

CARPETA_PROYECTO = Path(__file__).resolve().parents[1]
RUTA_POLITICA = CARPETA_PROYECTO / "datos" / "politica_ficticia.md"


def separar_politicas(texto: str) -> list[dict]:
    """Corta el documento en un trozo por cada título '## ...' (una política o las reglas)."""
    trozos = []
    for bloque in texto.split("\n## ")[1:]:
        titulo = bloque.splitlines()[0].replace("Política:", "").strip()
        trozos.append({"politica": titulo, "texto": "## " + bloque.strip()})
    return trozos


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    trozos = separar_politicas(RUTA_POLITICA.read_text(encoding="utf-8"))
    for trozo in trozos:
        print(f"- {trozo['politica']}: {len(trozo['texto'])} caracteres")
    # TODO(conocimiento-seguridad): reemplazar stub: guardar los trozos en Redis
    # (REDIS_URL y REDIS_PREFIJO del .env, embeddings con EMBEDDING_MODEL).
    print(f"(stub) {len(trozos)} trozos listos; todavía no se cargan en Redis.")


if __name__ == "__main__":
    main()
