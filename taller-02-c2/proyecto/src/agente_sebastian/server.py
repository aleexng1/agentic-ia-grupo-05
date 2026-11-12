"""Ficha A2A del agente de comida y catering de Sebastian; app.py lo publica en /agentes/sebastian."""

from src.agente_sebastian.graph import responder
from src.comun.config import url_agente
from src.comun.tarjeta import crear_tarjeta

# Ficha mejorada en el paso 5: la lee el supervisor de los compañeros para elegirme.
# La primera frase dice qué sé con temas concretos; la segunda, qué no hago.
tarjeta = crear_tarjeta(
    "Agente de Sebastian",
    "Propone la comida que se sirve a los asistentes de ferias tecnológicas, gastronómicas, culturales o infantiles de 10 a 500 personas y de 30 minutos a 8 horas: coffee break, cóctel, box lunch, almuerzo buffet, food trucks o colación infantil, con la hora de cada servicio, las cantidades y el agua calculadas, y menús vegetarianos, veganos, sin gluten y sin lactosa. No da precios ni presupuestos, no recomienda recintos ni capacidad, no arma el programa de actividades y no contrata proveedores: entrega solo propuestas.",
    url_agente("sebastian"),
    [
        (
            "armar_catering",
            "Armar catering del evento",
            "Propone qué servir y a qué hora, con cantidades y litros de agua calculados, según tipo de evento, personas, duración, hora de inicio y dietas especiales.",
            "Voy a hacer una feria infantil de 3 horas desde las 11:00 para 80 personas y 6 niños son celíacos, ¿qué les damos de comer?",
        ),
    ],
)
