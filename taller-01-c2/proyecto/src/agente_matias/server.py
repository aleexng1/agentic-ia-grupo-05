"""Aplicación HTTP del agente de programa de Matias."""

import os

from dotenv import load_dotenv

from src.agente_matias.graph import responder
from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta


load_dotenv()
URL_MATIAS = os.getenv("URL_MATIAS", "http://127.0.0.1:8003")

tarjeta = crear_tarjeta(
    "Agente de Matias",
    "Arma el programa de actividades y el horario de ferias tecnológicas, gastronómicas, culturales o infantiles de 30 minutos a 8 horas, para público familiar, adulto o estudiantes. No responde sobre lugares ni capacidad, comida ni costos, y no reserva ni confirma el programa definitivo: entrega solo propuestas.",
    URL_MATIAS,
    [
        (
            "armar_programa",
            "Armar programa de feria",
            "Propone las actividades que caben en el tiempo disponible, con su hora de inicio y término, según tipo de evento, público y hora de inicio.",
            "Necesito armar el programa de una feria infantil de 3 horas que parta a las 15:00.",
        ),
    ],
)

app = crear_app(tarjeta, responder)
