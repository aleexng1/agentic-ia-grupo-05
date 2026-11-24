"""Lógica del verificador: lee la boleta con Gemini (visión) y la compara con lo declarado.

Dueño: Alex (c2tf/alex-integracion). Encargo y respuesta en docs/contratos.md.
"""

CAMPOS_COMPARADOS = ("monto", "fecha", "rut_emisor", "folio", "categoria")


def verificar_boleta(imagen: dict, declarado: dict) -> dict:
    """Lee la imagen y compara cada campo de CAMPOS_COMPARADOS con lo declarado.

    `imagen` = {"mime_type", "datos_base64"}. Devuelve la respuesta de docs/contratos.md:
    {"leido": {...}, "cuadra": {campo: "sí" | "no"}, "confianza": 0..1, "observaciones": str}.
    Si un campo no se lee en la imagen, va como null en "leido" y "no" en "cuadra":
    nunca se completa con lo declarado.
    """
    raise NotImplementedError("verificar_boleta: pendiente (Alex, c2tf/alex-integracion).")


async def responder(texto: str, context_id: str) -> str:
    """Puente con src/comun/executor.py (que hoy solo pasa el texto del mensaje A2A).

    Pendiente: extender el Executor para leer el FilePart y el DataPart del encargo,
    llamar a verificar_boleta y devolver la respuesta como DataPart (JSON).
    """
    raise NotImplementedError("el verificador todavía no está implementado (Alex, c2tf/alex-integracion).")
