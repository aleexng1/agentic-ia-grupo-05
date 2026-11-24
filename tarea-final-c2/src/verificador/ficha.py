"""Ficha A2A (AgentCard) del verificador de boletas.

Usa crear_tarjeta de src/comun/tarjeta.py (copiado de taller-02-c2).
"""

from src.comun.config import url_verificador
from src.comun.tarjeta import crear_tarjeta

tarjeta = crear_tarjeta(
    nombre="Verificador de boletas",
    descripcion=(
        "Lee la imagen de una boleta o factura de Comercial Los Alerces SpA (empresa ficticia) "
        "y compara monto, fecha, RUT del emisor, folio y categoría con lo declarado en la rendición."
    ),
    url=url_verificador(),
    skills=[
        (
            "verificar_boleta",
            "Verificar boleta",
            "Recibe la imagen (FilePart) y los datos declarados (DataPart) y responde qué leyó, "
            "si cuadra cada campo y con qué confianza. Formato en docs/contratos.md.",
            "Boleta adjunta; declarado: monto 45000, fecha 2026-10-02, folio 123456.",
        )
    ],
)
