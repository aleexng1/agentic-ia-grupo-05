"""Flujo fuera_de_alcance: el mensaje no es de rendiciones ni de la política.

Dueño: Alex (c2tf/alex-integracion).

Responde con un texto fijo y verdadero sobre el alcance del sistema: sin LLM y sin herramientas,
así no se puede manipular (un pedido de «ignora tus reglas» termina aquí sin efecto).
"""

RESPUESTA = """\
Soy el revisor de rendiciones de gastos de Comercial Los Alerces SpA (empresa ficticia) y ese \
pedido está fuera de lo que hago.

Puedo ayudarte con dos cosas:
1. Consultar la política de gastos. Ejemplo: «¿Cuál es el plazo para rendir un gasto?»
2. Revisar un gasto rendido (con sus datos y, si quieres, la foto de la boleta). Ejemplo: \
«Revisa este gasto: bencina de $45.000 del 2 de octubre, boleta, fondo FR-001».

No hago: aprobar gastos sin revisarlos, cambiar las reglas o mis instrucciones, entregar claves \
ni datos internos, ni temas ajenos a las rendiciones."""


def responder_fuera_de_alcance(texto: str) -> dict:
    """Explica qué hace y qué no hace el sistema, sin llamar herramientas ni al verificador.

    Devuelve {"respuesta", "estado_final": "ok", "herramientas_usadas": [], "hubo_a2a": False}.
    """
    return {"respuesta": RESPUESTA, "estado_final": "ok", "herramientas_usadas": [], "hubo_a2a": False}
