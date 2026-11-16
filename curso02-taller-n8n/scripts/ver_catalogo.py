"""Mira el catálogo (catalogo.productos_unicos), solo lectura.

    python scripts/ver_catalogo.py              # cuántos productos hay por categoría
    python scripts/ver_catalogo.py "samsung 55"  # hasta 10 productos cuyo nombre contiene el texto

Una conexión corta, de solo lectura, con parámetros. No imprime la URL, la clave ni el servidor.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.router import catalogo  # noqa: E402

TABLA = catalogo.TABLA


def clp(valor) -> str:
    return "-" if valor is None else "$" + f"{int(valor):,}".replace(",", ".")


def corto(texto: str | None, ancho: int) -> str:
    texto = texto or "-"
    return texto if len(texto) <= ancho else texto[: ancho - 1] + "…"


def contar_por_categoria() -> None:
    filas = catalogo.consultar(
        f"SELECT categoria, count(*) AS productos FROM {TABLA} GROUP BY categoria ORDER BY categoria"
    )
    total = sum(f["productos"] for f in filas)
    print(f"Productos en {TABLA}: {total}\n")
    for f in filas:
        print(f"  {f['categoria'] or '(sin categoría)':<14} {f['productos']:>6}")


def buscar(texto: str) -> None:
    filas = catalogo.consultar(
        f"SELECT sku_id, nombre, marca, categoria, precio_internet, descuento_pct, rating FROM {TABLA} "
        "WHERE strpos(lower(nombre), lower(%s)) > 0 "
        "ORDER BY rating DESC NULLS LAST, precio_internet ASC, sku_id ASC LIMIT %s",
        [texto, 10],
    )
    print(f"Productos cuyo nombre contiene {texto!r}: {len(filas)} (máximo 10, mejor rating primero)\n")
    if not filas:
        return
    print(f"{'sku_id':<34} {'nombre':<48} {'precio':>11} {'dto':>4} {'rating':>6}")
    print("─" * 108)
    for f in filas:
        dto = "-" if f["descuento_pct"] is None else f"{f['descuento_pct']}%"
        rating = "-" if f["rating"] is None else f"{float(f['rating']):.1f}"
        print(f"{f['sku_id']:<34} {corto(f['nombre'], 48):<48} {clp(f['precio_internet']):>11} {dto:>4} {rating:>6}")


def main() -> None:
    if len(sys.argv) > 2:
        sys.exit('Uso: python scripts/ver_catalogo.py ["texto"]')
    try:
        if len(sys.argv) == 2 and sys.argv[1].strip():
            buscar(sys.argv[1].strip())
        else:
            contar_por_categoria()
    except catalogo.CatalogoNoDisponible as e:
        sys.exit(f"✘ {catalogo.MENSAJE_NO_DISPONIBLE}: {e}")


if __name__ == "__main__":
    main()
