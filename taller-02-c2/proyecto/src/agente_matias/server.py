"""Ficha A2A del agente de programa de Matias; app.py lo publica en /agentes/matias."""

from src.agente_matias.graph import responder
from src.comun.config import url_agente
from src.comun.tarjeta import crear_tarjeta

tarjeta = crear_tarjeta(
    "Agente de Matias",
    "Arma el programa de actividades y el horario de ferias tecnológicas, gastronómicas, culturales o infantiles de 30 minutos a 8 horas, para público familiar, adulto o estudiantes. No responde sobre lugares ni capacidad, comida ni costos, y no reserva ni confirma el programa definitivo: entrega solo propuestas.",
    url_agente("matias"),
    [
        (
            "armar_programa",
            "Armar programa de feria",
            "Propone las actividades que caben en el tiempo disponible, con su hora de inicio y término, según tipo de evento, público y hora de inicio.",
            "Necesito armar el programa de una feria infantil de 3 horas que parta a las 15:00.",
        ),
    ],
)
