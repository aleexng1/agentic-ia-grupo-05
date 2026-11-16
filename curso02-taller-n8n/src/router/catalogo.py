"""Acceso de SOLO LECTURA al catálogo: catalogo.productos_unicos (misma base que la memoria).

El usuario de la base puede escribir en catalogo, así que este módulo se protege solo:
- consultar() rechaza cualquier SQL que no sea un SELECT simple sobre catalogo.productos_unicos
  (una sola sentencia, sin comentarios, sin literales de texto, sin funciones fuera de una lista corta);
- la consulta va siempre con parámetros (%s): el texto del cliente o del modelo nunca entra al SQL;
- la conexión es de SOLO LECTURA (BEGIN READ ONLY + default_transaction_read_only), se abre para cada
  consulta y se cierra al terminar;
- como máximo 1 conexión a la vez (la memoria usa hasta 2: nunca más de 3 en total).

La URL, la clave y el servidor no se imprimen ni se registran: los errores pasan por src.memoria.ocultar.
"""

import os
import re
import threading
from typing import Any, Mapping, Sequence

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

from src.memoria import motivo_de, registrar_secretos

load_dotenv()

TABLA = "catalogo.productos_unicos"
MENSAJE_NO_DISPONIBLE = "catálogo no disponible"

SEGUNDOS_CONEXION = 8   # tope para conectar
SEGUNDOS_CONSULTA = 8   # statement_timeout en el servidor
SEGUNDOS_ESPERA = 15    # tope para esperar el turno de la única conexión
MAX_FILAS = 50
MAX_LARGO_SQL = 2000


class SqlNoPermitido(ValueError):
    """El SQL no es un SELECT simple sobre catalogo.productos_unicos."""


class CatalogoNoDisponible(Exception):
    """No se pudo consultar el catálogo (sin URL, sin red, sin cupo de conexiones, etc.)."""


# ── Validación del SQL ───────────────────────────────────────────────────────

_PROHIBIDAS = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke|copy|call|do|execute|merge|"
    r"vacuum|analyze|refresh|lock|into|set|reset|listen|notify|comment|reindex|cluster|prepare|"
    r"deallocate|discard|load|import|explain|show|begin|commit|rollback|savepoint)\b",
    re.IGNORECASE,
)
_BLOQUEO_FILAS = re.compile(r"\bfor\s+(no\s+key\s+)?(update|share|key\s+share)\b", re.IGNORECASE)
_TABLAS = re.compile(r"\b(?:from|join)\s+([^\s,()]+)", re.IGNORECASE)
_LLAMADAS = re.compile(r"\b([a-z_][a-z0-9_]*)\s*\(", re.IGNORECASE)

# Funciones que se pueden usar. Cualquier otra (pg_read_file, pg_terminate_backend, dblink...) se rechaza.
FUNCIONES_PERMITIDAS = {"lower", "upper", "strpos", "count", "coalesce", "min", "max", "avg", "round", "sum",
                        "length", "trim"}
# Palabras de SQL que pueden ir seguidas de "(" sin ser una función.
_PALABRAS_SQL = {"and", "or", "not", "in", "from", "join", "on", "where", "exists", "select", "as", "any",
                 "all", "having", "when", "then", "else", "by", "limit", "offset", "between", "distinct",
                 "over", "filter", "union"}


def validar_select(sql: Any) -> str:
    """Devuelve el SQL listo para ejecutar, o lanza SqlNoPermitido. No toca la red."""
    if not isinstance(sql, str) or not sql.strip():
        raise SqlNoPermitido("el SQL está vacío")
    limpio = sql.strip().rstrip(";").rstrip()
    if len(limpio) > MAX_LARGO_SQL:
        raise SqlNoPermitido("el SQL es demasiado largo")
    if ";" in limpio:
        raise SqlNoPermitido("solo se permite una sentencia")
    if re.search(r"--|/\*|\*/", limpio):
        raise SqlNoPermitido("no se permiten comentarios")
    if re.search(r"['\"$\\\x00]", limpio):
        raise SqlNoPermitido("no se permiten literales de texto: el texto va en parámetros (%s)")
    if not re.match(r"select\b", limpio, re.IGNORECASE):
        raise SqlNoPermitido("solo se permite SELECT")
    prohibida = _PROHIBIDAS.search(limpio)
    if prohibida:
        raise SqlNoPermitido(f"palabra no permitida: {prohibida.group(1).upper()}")
    if _BLOQUEO_FILAS.search(limpio):
        raise SqlNoPermitido("no se permite bloquear filas (FOR UPDATE / FOR SHARE)")
    tablas = _TABLAS.findall(limpio)
    if not tablas:
        raise SqlNoPermitido(f"la consulta debe leer {TABLA}")
    for tabla in tablas:
        if tabla.lower() != TABLA:
            raise SqlNoPermitido(f"solo se puede leer {TABLA} (con su nombre completo)")
    for nombre in _LLAMADAS.findall(limpio):
        n = nombre.lower()
        if n not in _PALABRAS_SQL and n not in FUNCIONES_PERMITIDAS:
            raise SqlNoPermitido(f"función no permitida: {n}")
    return limpio


# ── Consulta ─────────────────────────────────────────────────────────────────

# Una sola conexión a la vez: las consultas hacen turno.
_TURNO = threading.Lock()


def consultar(sql: str, params: Sequence[Any] | Mapping[str, Any] = ()) -> list[dict]:
    """Ejecuta un SELECT con parámetros y devuelve las filas como diccionarios.

    Lanza SqlNoPermitido (antes de conectar) si el SQL no es un SELECT permitido, y
    CatalogoNoDisponible si no se pudo consultar la base.
    """
    limpio = validar_select(sql)

    url = (os.getenv("DATABASE_URL") or "").strip()
    if not url:
        raise CatalogoNoDisponible("DATABASE_URL no está definida")
    registrar_secretos(url)

    if not _TURNO.acquire(timeout=SEGUNDOS_ESPERA):
        raise CatalogoNoDisponible("hay otra consulta al catálogo en curso")
    try:
        with psycopg.connect(
            url,
            connect_timeout=SEGUNDOS_CONEXION,
            row_factory=dict_row,
            prepare_threshold=0,
            options=f"-c default_transaction_read_only=on -c statement_timeout={SEGUNDOS_CONSULTA * 1000}",
        ) as conn:
            conn.read_only = True  # BEGIN READ ONLY: la base rechaza cualquier escritura
            with conn.cursor() as cur:
                cur.execute(limpio, params)
                return cur.fetchmany(MAX_FILAS)
        # al salir del with, la conexión se cierra
    except (psycopg.Error, OSError) as e:
        # "from None": el error original puede traer el servidor en su mensaje.
        raise CatalogoNoDisponible(motivo_de(e)) from None
    finally:
        _TURNO.release()
