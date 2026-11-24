"""Flujo fuera_de_alcance: el mensaje no es de rendiciones ni de la política.

Dueño: Alex (c2tf/alex-integracion).
"""


def responder_fuera_de_alcance(texto: str) -> dict:
    """Explica con amabilidad qué sí puede hacer el agente, sin llamar herramientas.

    Devuelve {"respuesta": str, "herramientas_usadas": []}. La respuesta debe nombrar las
    dos cosas que el agente sí hace (consultar la política y revisar un gasto) con un ejemplo
    de cada una. No ejecuta ninguna acción ni llama al verificador.
    """
    raise NotImplementedError("responder_fuera_de_alcance: pendiente (Alex, c2tf/alex-integracion).")
