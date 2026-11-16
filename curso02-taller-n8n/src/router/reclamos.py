"""Reclamos de postventa: se guardan en Postgres, en el esquema propio (DB_SCHEMA), o en memoria si no hay base.

- Usa el POOL de la memoria (src/memoria.py): no abre conexiones nuevas. Con el catálogo (1 conexión a la vez)
  el total nunca pasa de 3.
- La tabla `reclamos` se crea al arrancar si no existe, siempre con el esquema por delante
  ("alex_nail".reclamos): nunca en public, catalogo ni alumnoNN.
- El número de ticket lo genera la base (serial) y se muestra como R-0001, R-0002...
- Consultas siempre con parámetros (%s). La URL, la clave y el servidor no se imprimen ni se registran.
"""

import logging
import threading
from datetime import datetime, timezone

from psycopg import sql

from src.memoria import motivo_de

log = logging.getLogger("uvicorn.error")

CREAR_TABLA = sql.SQL(
    "CREATE TABLE IF NOT EXISTS {}.reclamos ("
    "ticket serial PRIMARY KEY, "
    "numero_pedido text NOT NULL, "
    "motivo text NOT NULL, "
    "detalle text, "
    "thread_id text NOT NULL, "
    "creado_en timestamptz NOT NULL DEFAULT now())"
)
INSERTAR = sql.SQL(
    "INSERT INTO {}.reclamos (numero_pedido, motivo, detalle, thread_id) VALUES (%s, %s, %s, %s) RETURNING ticket"
)
LISTAR = sql.SQL(
    "SELECT ticket, numero_pedido, motivo, detalle, thread_id, creado_en FROM {}.reclamos "
    "ORDER BY ticket DESC LIMIT %s"
)


class ReclamoNoGuardado(Exception):
    """No se pudo guardar el reclamo en la base (el motivo viene sin secretos)."""


def formato_ticket(numero: int) -> str:
    return f"R-{int(numero):04d}"


# ── Estado del almacén ───────────────────────────────────────────────────────

_pool = None  # pool de la memoria, si hay Postgres
_esquema: str | None = None
_en_memoria: list[dict] = []  # respaldo cuando no hay base
_candado = threading.Lock()


def configurar(memoria) -> str:
    """Prepara el almacén al arrancar. Devuelve 'postgres' o 'memoria'. Nunca lanza."""
    global _pool, _esquema
    _pool, _esquema = None, None
    if memoria is None or memoria.tipo != "postgres" or memoria.pool is None:
        motivo = getattr(memoria, "motivo", None) or "la memoria del agente no usa Postgres"
        log.warning("Reclamos solo en memoria (se pierden al reiniciar): %s", motivo)
        return "memoria"
    try:
        with memoria.pool.connection() as conn:
            conn.execute(CREAR_TABLA.format(sql.Identifier(memoria.esquema)))
    except Exception as e:
        log.warning("Reclamos solo en memoria (se pierden al reiniciar): no pude preparar la tabla (%s)", motivo_de(e))
        return "memoria"
    _pool, _esquema = memoria.pool, memoria.esquema
    log.info("Reclamos en Postgres (esquema %s, tabla reclamos).", memoria.esquema)
    return "postgres"


def detener() -> None:
    """Suelta el pool (lo cierra la memoria) y vacía el respaldo en memoria."""
    global _pool, _esquema
    _pool, _esquema = None, None
    with _candado:
        _en_memoria.clear()


def donde_se_guarda() -> str:
    return "postgres" if _pool is not None else "memoria"


def en_memoria() -> list[dict]:
    with _candado:
        return [dict(r) for r in _en_memoria]


# ── Crear ────────────────────────────────────────────────────────────────────

def crear(numero_pedido: str, motivo: str, detalle: str, thread_id: str) -> str:
    """Guarda un reclamo y devuelve su ticket (R-0001...). Lanza ReclamoNoGuardado si falla la base."""
    if _pool is not None:
        try:
            with _pool.connection() as conn:
                fila = conn.execute(
                    INSERTAR.format(sql.Identifier(_esquema)), [numero_pedido, motivo, detalle, thread_id]
                ).fetchone()
            return formato_ticket(fila["ticket"])
        except Exception as e:
            # "from None": el error original puede traer el servidor en su mensaje.
            raise ReclamoNoGuardado(motivo_de(e)) from None

    with _candado:
        numero = len(_en_memoria) + 1
        _en_memoria.append({
            "ticket": numero, "numero_pedido": numero_pedido, "motivo": motivo, "detalle": detalle,
            "thread_id": thread_id, "creado_en": datetime.now(timezone.utc),
        })
    log.warning("Reclamo %s guardado solo en memoria (se pierde al reiniciar).", formato_ticket(numero))
    return formato_ticket(numero)
