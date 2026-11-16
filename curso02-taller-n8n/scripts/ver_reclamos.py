"""Lista los reclamos guardados en Postgres (tabla reclamos del esquema DB_SCHEMA).

    python scripts/ver_reclamos.py          # los últimos 20
    python scripts/ver_reclamos.py 50       # los últimos 50

Una sola conexión corta, en solo lectura. No imprime la URL, la clave ni el servidor.
"""

import sys
from pathlib import Path

import psycopg
from psycopg import sql

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.memoria import abrir_conexion, motivo_de, nombre_esquema  # noqa: E402
from src.router.reclamos import LISTAR, formato_ticket  # noqa: E402


def corto(texto: str | None, ancho: int) -> str:
    texto = " ".join((texto or "-").split())
    return texto if len(texto) <= ancho else texto[: ancho - 1] + "…"


def listar(conn, limite: int) -> None:
    esquema = nombre_esquema()
    filas = conn.execute(LISTAR.format(sql.Identifier(esquema)), [limite]).fetchall()
    print(f"Reclamos en el esquema '{esquema}': {len(filas)} (los más recientes primero)\n")
    for f in filas:
        creado = f["creado_en"].astimezone().strftime("%Y-%m-%d %H:%M")
        print(f"{formato_ticket(f['ticket'])}  pedido {f['numero_pedido']:<10} {creado}  hilo: {f['thread_id']}")
        print(f"    motivo : {corto(f['motivo'], 100)}")
        print(f"    detalle: {corto(f['detalle'], 100)}")


def main() -> None:
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and not sys.argv[1].isdigit()):
        sys.exit("Uso: python scripts/ver_reclamos.py [CANTIDAD]")
    limite = int(sys.argv[1]) if len(sys.argv) == 2 else 20
    try:
        with abrir_conexion(solo_lectura=True) as conn:
            listar(conn, limite)
    except psycopg.errors.UndefinedTable:
        sys.exit("Todavía no existe la tabla reclamos en ese esquema: se crea al arrancar la API o main.py.")
    except (psycopg.Error, RuntimeError, ValueError) as e:
        sys.exit(f"✘ {motivo_de(e)}")


if __name__ == "__main__":
    main()
