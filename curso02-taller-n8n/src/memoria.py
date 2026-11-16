"""Memoria del agente (checkpointer de LangGraph).

- Con DATABASE_URL y una base que responde: PostgresSaver, en un esquema propio (DB_SCHEMA).
- Sin DATABASE_URL, o si Postgres no responde al arrancar: MemorySaver (RAM), con el motivo anotado.

Reglas de seguridad de este módulo:
- La base es compartida y el usuario puede escribir en todo, así que SOLO se trabaja en DB_SCHEMA
  (por defecto alex_nail). Nunca en public, catalogo ni alumnoNN.
- La URL, la clave y la dirección del servidor no se imprimen ni se registran nunca: todo mensaje
  de error y todo log de psycopg pasa por ocultar().
- Pool pequeño (1 a 2 conexiones): la base se queda sin cupo con facilidad.
"""

import logging
import os
import re
import traceback
from dataclasses import dataclass
from typing import Any

import psycopg
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

load_dotenv()

ESQUEMA_POR_DEFECTO = "alex_nail"
ESQUEMAS_PROHIBIDOS = {"public", "catalogo", "information_schema"}
POOL_MIN = 1
POOL_MAX = 2
SEGUNDOS_CONEXION = 10  # tope para conectar y para abrir el pool; si no, se usa RAM

# ── Ocultar secretos ─────────────────────────────────────────────────────────

_secretos: set[str] = set()
_RE_SERVIDOR = re.compile(r'(connection to server at )"[^"]*"')
_RE_URL = re.compile(r"postgres(?:ql)?://\S+")


def registrar_secretos(url: str) -> None:
    """Anota la URL, la clave y el servidor para taparlos en cualquier texto posterior."""
    candidatos = [url]
    try:
        info = conninfo_to_dict(url)
        candidatos += [info.get("password"), info.get("host"), info.get("hostaddr")]
    except psycopg.Error:
        pass
    _secretos.update(c for c in candidatos if c and len(c) >= 3)


def ocultar(texto: str) -> str:
    for secreto in sorted(_secretos, key=len, reverse=True):
        texto = texto.replace(secreto, "<oculto>")
    texto = _RE_SERVIDOR.sub(r'\1"<oculto>"', texto)
    return _RE_URL.sub("<url>", texto)


def motivo_de(e: BaseException) -> str:
    """Resumen de una línea de un error, sin secretos."""
    return " ".join(ocultar(f"{type(e).__name__}: {e}").split())


class _Redactor(logging.Filter):
    """Tapa secretos en los logs (mensaje y traceback), también los que escribe psycopg_pool."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            record.msg = ocultar(record.getMessage())
            if record.exc_info:
                record.exc_text = ocultar("".join(traceback.format_exception(*record.exc_info)))
            elif record.exc_text:
                record.exc_text = ocultar(record.exc_text)
        except Exception:
            record.msg = "<mensaje oculto>"
            record.exc_text = None
        record.args = ()
        record.exc_info = None
        return True


def proteger_logs(*nombres: str) -> None:
    for nombre in nombres:
        logger = logging.getLogger(nombre)
        if not any(isinstance(f, _Redactor) for f in logger.filters):
            logger.addFilter(_Redactor())


proteger_logs("psycopg", "psycopg.pool", "uvicorn.error")

# ── Esquema y conexiones ─────────────────────────────────────────────────────


def nombre_esquema() -> str:
    """Esquema propio donde van todas las tablas. Se rechazan los esquemas ajenos."""
    esquema = (os.getenv("DB_SCHEMA") or ESQUEMA_POR_DEFECTO).strip()
    if not re.fullmatch(r"[a-z_][a-z0-9_]{0,62}", esquema):
        raise ValueError("DB_SCHEMA debe ser un nombre simple en minúsculas (letras, números y _)")
    if esquema in ESQUEMAS_PROHIBIDOS or esquema.startswith("pg_") or re.fullmatch(r"alumno\d+", esquema):
        raise ValueError(f"DB_SCHEMA={esquema!r} no está permitido: es un esquema compartido o ajeno")
    return esquema


def _kwargs_conexion(esquema: str, solo_lectura: bool = False) -> dict[str, Any]:
    opciones = f"-c search_path={esquema}"
    if solo_lectura:
        opciones += " -c default_transaction_read_only=on"
    return {
        "autocommit": True,  # lo exige PostgresSaver
        "prepare_threshold": 0,
        "row_factory": dict_row,
        "options": opciones,  # todas las tablas se crean/leen en el esquema propio
        "connect_timeout": SEGUNDOS_CONEXION,
    }


def abrir_conexion(solo_lectura: bool = True) -> psycopg.Connection:
    """UNA conexión corta, fijada al esquema propio. Quien la pide la cierra (with ... as conn)."""
    url = (os.getenv("DATABASE_URL") or "").strip()
    if not url:
        raise RuntimeError("Falta DATABASE_URL en .env")
    registrar_secretos(url)
    return psycopg.connect(url, **_kwargs_conexion(nombre_esquema(), solo_lectura))


# ── Memoria ──────────────────────────────────────────────────────────────────


@dataclass
class Memoria:
    checkpointer: Any
    tipo: str  # "ram" | "postgres"
    esquema: str | None = None
    motivo: str | None = None  # por qué se usa RAM, si aplica
    pool: ConnectionPool | None = None

    def cerrar(self) -> None:
        if self.pool is not None:
            self.pool.close()
            self.pool = None


def abrir_memoria() -> Memoria:
    """Postgres si se puede; si no, RAM. Nunca lanza: la API no debe quedar caída por la base."""
    url = (os.getenv("DATABASE_URL") or "").strip()
    if not url:
        return Memoria(MemorySaver(), "ram", motivo="DATABASE_URL no está definida")

    registrar_secretos(url)
    pool = None
    try:
        esquema = nombre_esquema()
        kwargs = _kwargs_conexion(esquema)

        # 1) Una conexión corta: comprueba que la base responde y crea el esquema propio.
        #    Falla rápido (sin bucles de reintento) si no hay cupo o no hay red.
        with psycopg.connect(url, **kwargs) as conn:
            conn.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(esquema)))

        # 2) Pool pequeño, abierto una vez; cada conexión se comprueba antes de usarla.
        pool = ConnectionPool(
            url,
            min_size=POOL_MIN,
            max_size=POOL_MAX,
            kwargs=kwargs,
            check=ConnectionPool.check_connection,
            open=False,
            name="memoria",
            timeout=SEGUNDOS_CONEXION,
        )
        pool.open(wait=True, timeout=SEGUNDOS_CONEXION)

        saver = PostgresSaver(pool)
        saver.setup()  # crea checkpoints, checkpoint_blobs, checkpoint_writes... en el esquema propio
        return Memoria(saver, "postgres", esquema=esquema, pool=pool)
    except Exception as e:
        if pool is not None:
            try:
                pool.close()
            except Exception:
                pass
        return Memoria(MemorySaver(), "ram", motivo=motivo_de(e))
