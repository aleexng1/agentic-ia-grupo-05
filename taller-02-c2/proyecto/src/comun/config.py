"""Direcciones de la app única, leídas una sola vez desde el .env."""

import os

from dotenv import load_dotenv


load_dotenv()

NOMBRES_AGENTES = ("matias", "alex", "eduardo", "sebastian")


def url_base() -> str:
    """Dirección pública de la app: local por defecto, la de Heroku al desplegar."""
    return (os.getenv("URL_BASE", "").strip() or "http://127.0.0.1:8000").rstrip("/")


def ruta_agente(nombre: str) -> str:
    """Ruta interna donde la app única publica a un agente."""
    return f"/agentes/{nombre}"


def url_agente(nombre: str) -> str:
    """Dirección completa de un agente; es la que publica su ficha."""
    return url_base() + ruta_agente(nombre)


def urls_agentes() -> list[str]:
    """Agentes que consultará el coordinador.

    Con URLS_AGENTES vacía son las cuatro rutas internas de la app única. Con valores
    (separados por comas) se respetan tal cual: es el modo distribuido del taller
    anterior, con un agente por computador.
    """
    configuradas = [
        direccion.strip().rstrip("/")
        for direccion in os.getenv("URLS_AGENTES", "").split(",")
        if direccion.strip()
    ]
    direcciones = configuradas or [url_agente(nombre) for nombre in NOMBRES_AGENTES]
    return list(dict.fromkeys(direcciones))
