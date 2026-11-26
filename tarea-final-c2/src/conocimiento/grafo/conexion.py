"""Configuración explícita del proceso para Neo4j; no abre ni carga .env."""

import os
import re
from contextlib import contextmanager
from dataclasses import dataclass
from urllib.parse import urlsplit

from neo4j import GraphDatabase
from neo4j.exceptions import (
    AuthError,
    ConnectionAcquisitionTimeoutError,
    DriverError,
    Forbidden,
    Neo4jError,
    ServiceUnavailable,
    SessionExpired,
)

_BASE_PREDETERMINADA = "neo4j"
# Los identificadores de base asignados por Aura también pueden empezar por un dígito.
_NOMBRE_BASE = re.compile(r"[A-Za-z0-9][A-Za-z0-9.-]{2,62}")


class ErrorGrafo(RuntimeError):
    """Falla operativa de GraphRAG con un mensaje seguro."""


@dataclass(frozen=True, repr=False)
class Conexion:
    uri: str
    usuario: str
    clave: str
    base: str
    destino: str


def configuracion() -> Conexion:
    uri = os.getenv("NEO4J_URI", "").strip()
    usuario = os.getenv("NEO4J_USER", "").strip()
    clave = os.getenv("NEO4J_PASSWORD", "")
    if not (uri and usuario and clave.strip()):
        raise ErrorGrafo("Falta configurar la conexión a Neo4j en el entorno del proceso.")
    base = os.getenv("NEO4J_DATABASE", _BASE_PREDETERMINADA)
    if not _NOMBRE_BASE.fullmatch(base):
        raise ErrorGrafo("NEO4J_DATABASE no contiene un nombre de base válido para GraphRAG.")
    try:
        url = urlsplit(uri)
        puerto = 7687 if url.port is None else url.port
        if (
            url.scheme not in {"neo4j", "neo4j+s", "neo4j+ssc", "bolt", "bolt+s", "bolt+ssc"}
            or not url.hostname or not puerto or "@" in url.netloc or url.path or url.query or url.fragment
            or any(c.isspace() for c in uri)
        ):
            raise ValueError
        host = f"[{url.hostname}]" if ":" in url.hostname else url.hostname
    except ValueError:
        raise ErrorGrafo("La URI de Neo4j no es válida para GraphRAG.") from None
    return Conexion(uri, usuario, clave, base, f"{url.scheme}://{host}:{puerto}/{base}")


def _mensaje(error: Exception) -> str:
    codigo = (error.code or "") if isinstance(error, Neo4jError) else ""
    if isinstance(error, (AuthError, Forbidden)):
        return "Neo4j rechazó la autenticación o los permisos de GraphRAG."
    if (
        isinstance(error, (TimeoutError, ConnectionAcquisitionTimeoutError))
        or isinstance(error.__cause__, TimeoutError)
        or codigo.rsplit(".", 1)[-1] in {"TransactionTimedOut", "TransactionTimedOutClientConfiguration"}
    ):
        return "Se agotó el tiempo de espera de Neo4j para GraphRAG."
    if isinstance(error, (ServiceUnavailable, SessionExpired, OSError)):
        return "Neo4j no está disponible para GraphRAG."
    return "Neo4j no pudo ejecutar la operación de GraphRAG."


@contextmanager
def sesion_neo4j(ajustes: Conexion, modo: str):
    try:
        with GraphDatabase.driver(
            ajustes.uri,
            auth=(ajustes.usuario, ajustes.clave),
            connection_timeout=3,
            connection_write_timeout=5,
            connection_acquisition_timeout=5,
            max_transaction_retry_time=0,
        ) as driver, driver.session(database=ajustes.base, default_access_mode=modo) as sesion:
            yield sesion
    except (Neo4jError, DriverError, OSError, ValueError) as error:
        raise ErrorGrafo(_mensaje(error)) from None
