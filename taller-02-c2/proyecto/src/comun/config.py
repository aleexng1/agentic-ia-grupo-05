"""Direcciones de la app única, leídas una sola vez desde el .env."""

import os

from dotenv import load_dotenv


load_dotenv()

NOMBRES_AGENTES = ("matias", "alex", "eduardo", "sebastian")


def puerto() -> int:
    """Puerto real donde escucha la app: PORT (lo asigna Heroku), si no PUERTO, si no 8000."""
    for variable in ("PORT", "PUERTO"):
        valor = os.getenv(variable, "").strip()
        if valor:
            try:
                return int(valor)
            except ValueError:
                raise ValueError(f"{variable} debe ser un número de puerto; vale «{valor}».") from None
    return 8000


def url_base() -> str:
    """Dirección pública de la app: local por defecto, la de Heroku al desplegar."""
    return (os.getenv("URL_BASE", "").strip() or "http://127.0.0.1:8000").rstrip("/")


def ruta_agente(nombre: str) -> str:
    """Ruta interna donde la app única publica a un agente."""
    return f"/agentes/{nombre}"


def url_agente(nombre: str) -> str:
    """Dirección completa de un agente; es la que publica su ficha."""
    return url_base() + ruta_agente(nombre)


def url_interna(nombre: str) -> str:
    """Dirección local de un agente dentro de la misma app (no pasa por Internet).

    En Heroku evita salir y volver a entrar por su router, que corta a los 30 s.
    """
    return f"http://127.0.0.1:{puerto()}{ruta_agente(nombre)}"


def _urls_configuradas() -> list[str]:
    """Direcciones escritas en URLS_AGENTES, separadas por comas."""
    return [
        direccion.strip().rstrip("/")
        for direccion in os.getenv("URLS_AGENTES", "").split(",")
        if direccion.strip()
    ]


def modo_interno() -> bool:
    """True si URLS_AGENTES está vacía: el coordinador usa los agentes de esta app."""
    return not _urls_configuradas()


def urls_agentes() -> list[str]:
    """Direcciones por las que el coordinador consulta a los agentes.

    Con URLS_AGENTES vacía son las cuatro rutas internas (127.0.0.1 y el puerto real);
    las fichas públicas siguen mostrando URL_BASE. Con valores se respetan tal cual:
    es el modo distribuido del taller anterior, con un agente por computador.
    """
    direcciones = _urls_configuradas() or [url_interna(n) for n in NOMBRES_AGENTES]
    return list(dict.fromkeys(direcciones))
