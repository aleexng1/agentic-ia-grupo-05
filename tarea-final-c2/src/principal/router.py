"""Router del agente principal: decide a qué flujo va cada mensaje.

Dueño: Alex (c2tf/alex-integracion). Las rutas válidas están en docs/contratos.md.
"""

RUTAS = ("consulta_politica", "revisar_gasto", "fuera_de_alcance")


def clasificar(texto: str, tiene_imagen: bool = False) -> dict:
    """Clasifica el mensaje en una de RUTAS y explica por qué.

    Devuelve {"ruta": <una de RUTAS>, "motivo": <frase corta>}.
    Ejemplos: "¿cuál es el tope de hotel?" → consulta_politica; "revisa este gasto: ..."
    (o un mensaje con imagen de boleta) → revisar_gasto; "escríbeme un poema" →
    fuera_de_alcance. Debe usar el LLM con salida estructurada (Literal de RUTAS) y, si
    la salida no es válida, caer en "fuera_de_alcance" (nunca inventar una ruta).
    """
    raise NotImplementedError("clasificar: pendiente (Alex, c2tf/alex-integracion).")
