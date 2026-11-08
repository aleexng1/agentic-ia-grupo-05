"""Descubrimiento de agentes disponibles mediante sus tarjetas A2A."""

import os

from dotenv import load_dotenv

from src.coordinador.cliente import obtener_cliente, tarjeta_del_cliente


load_dotenv()


def _una_linea(texto: str) -> str:
    """Reduce un error de red a una línea entendible."""
    return " ".join(texto.replace("\r", " ").replace("\n", " ").split())


async def descubrir() -> list[dict]:
    """Descarga tarjetas y crea el catálogo de los agentes que respondan."""
    direcciones = [
        os.getenv("URL_MATIAS", "http://127.0.0.1:8003").strip(),
    ]
    direcciones.extend(
        direccion.strip()
        for direccion in os.getenv("URLS_AGENTES", "").split(",")
        if direccion.strip()
    )
    direcciones = list(dict.fromkeys(url.rstrip("/") for url in direcciones if url))
    catalogo = []

    for url in direcciones:
        if not url:
            continue
        try:
            cliente = await obtener_cliente(url)
            tarjeta = tarjeta_del_cliente(cliente)
            catalogo.append(
                {
                    "nombre": tarjeta.name,
                    "descripcion": tarjeta.description,
                    "cliente": cliente,
                }
            )
        except Exception as error:
            detalle = _una_linea(str(error)) or error.__class__.__name__
            print(f"No se pudo descubrir el agente en {url}: {detalle}")

    return catalogo
