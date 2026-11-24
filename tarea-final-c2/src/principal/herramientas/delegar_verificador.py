"""Delegación A2A al verificador de boletas.

Dueño: Alex (c2tf/alex-integracion). Encargo y respuesta en docs/contratos.md.
El cliente A2A ya existe (src/comun/cliente_a2a.py, copiado de taller-02-c2).
"""


async def delegar_verificador(imagen: dict, declarado: dict) -> dict:
    """Envía la boleta y los datos declarados al verificador y devuelve su respuesta.

    `imagen` = {"mime_type", "datos_base64"}; `declarado` = {"monto", "fecha", "rut_emisor",
    "folio", "categoria"}. Manda un Message A2A con un FilePart (la imagen) y un DataPart
    (lo declarado) a URL_VERIFICADOR con TOKEN_A2A, esperando como máximo TIMEOUT_A2A_SEG.
    Si FORZAR_FALLO_A2A=1, o si hay timeout o error, NO inventa la lectura: devuelve
    {"disponible": False, "motivo": ...} y el flujo deja el gasto como "observar"
    con estado_final = "fallback".
    """
    raise NotImplementedError("delegar_verificador: pendiente (Alex, c2tf/alex-integracion).")
