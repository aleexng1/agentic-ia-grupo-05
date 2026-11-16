"""Mira la memoria guardada en Postgres (esquema DB_SCHEMA).

    python scripts/ver_memoria.py              # lista los hilos guardados
    python scripts/ver_memoria.py THREAD_ID    # imprime la conversación de ese hilo

Una sola conexión corta, en modo solo lectura. No imprime la URL, la clave ni el servidor.
"""

import sys
from datetime import datetime
from pathlib import Path

import psycopg

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from langgraph.checkpoint.postgres import PostgresSaver  # noqa: E402

from src.memoria import abrir_conexion, motivo_de, nombre_esquema  # noqa: E402

ROLES = {"human": "cliente", "ai": "agente", "system": "sistema"}


def fecha(ts: str | None) -> str:
    if not ts:
        return "-"
    try:
        return datetime.fromisoformat(ts).astimezone().strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return ts


def listar_hilos(conn: psycopg.Connection) -> None:
    filas = conn.execute(
        "SELECT thread_id, count(*) AS checkpoints, max(checkpoint->>'ts') AS ultimo "
        "FROM checkpoints WHERE checkpoint_ns = '' "
        "GROUP BY thread_id ORDER BY max(checkpoint->>'ts') DESC"
    ).fetchall()
    print(f"Hilos guardados en el esquema '{nombre_esquema()}': {len(filas)}\n")
    if not filas:
        return
    ancho = max(len("thread_id"), *(len(f["thread_id"]) for f in filas))
    print(f"{'thread_id':<{ancho}}  {'checkpoints':>11}  último")
    print("─" * (ancho + 38))
    for f in filas:
        print(f"{f['thread_id']:<{ancho}}  {f['checkpoints']:>11}  {fecha(f['ultimo'])}")


def mostrar_hilo(conn: psycopg.Connection, thread_id: str) -> None:
    ultimo = PostgresSaver(conn).get_tuple({"configurable": {"thread_id": thread_id}})
    if ultimo is None:
        sys.exit(f"No hay ningún hilo '{thread_id}'. Corre el script sin argumentos para ver los que existen.")
    valores = ultimo.checkpoint["channel_values"]
    mensajes = valores.get("messages", [])
    print(f"Hilo '{thread_id}' · {len(mensajes)} mensajes · último cambio {fecha(ultimo.checkpoint.get('ts'))}")
    if valores.get("ruta"):
        print(f"Última ruta: {valores['ruta']} — {valores.get('motivo', '')}")
    print()
    for i, m in enumerate(mensajes, 1):
        print(f"{i}. [{ROLES.get(m.type, m.type)}] {m.content}")


def main() -> None:
    if len(sys.argv) > 2:
        sys.exit("Uso: python scripts/ver_memoria.py [THREAD_ID]")
    try:
        with abrir_conexion(solo_lectura=True) as conn:
            if len(sys.argv) == 2:
                mostrar_hilo(conn, sys.argv[1])
            else:
                listar_hilos(conn)
    except psycopg.errors.UndefinedTable:
        sys.exit("Todavía no hay tablas de memoria en ese esquema: corre la API o main.py una vez para crearlas.")
    except (psycopg.Error, RuntimeError, ValueError) as e:
        sys.exit(f"✘ {motivo_de(e)}")


if __name__ == "__main__":
    main()
