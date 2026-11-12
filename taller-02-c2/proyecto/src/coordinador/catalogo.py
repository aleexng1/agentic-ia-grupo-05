"""Descubrimiento de agentes disponibles mediante sus tarjetas A2A."""

from src.comun.config import modo_interno, urls_agentes
from src.comun.registro import obtener_registro
from src.coordinador.cliente import obtener_cliente, tarjeta_del_cliente


_REGISTRO = obtener_registro()


def _una_linea(texto: str) -> str:
    """Reduce un error de red a una línea entendible."""
    return " ".join(texto.replace("\r", " ").replace("\n", " ").split())


async def descubrir() -> list[dict]:
    """Descarga tarjetas y crea el catálogo de los agentes que respondan."""
    catalogo = []
    # En la app única las fichas publican URL_BASE (pública); el coordinador las
    # consulta por la dirección interna para no pasar por el router de Heroku.
    interno = modo_interno()

    for url in urls_agentes():
        try:
            cliente = await obtener_cliente(url, usar_esta_direccion=interno)
            tarjeta = tarjeta_del_cliente(cliente)
            catalogo.append(
                {
                    "nombre": tarjeta.name,
                    "descripcion": tarjeta.description,
                    "cliente": cliente,
                    "url": tarjeta.supported_interfaces[0].url
                    if tarjeta.supported_interfaces
                    else url,
                }
            )
        except Exception as error:
            detalle = _una_linea(str(error)) or error.__class__.__name__
            _REGISTRO.warning("No se pudo descubrir el agente en %s: %s", url, detalle)

    return catalogo
