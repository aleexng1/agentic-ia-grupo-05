"""Aplicación HTTP del agente de recintos y capacidad de Alex."""

import os

from dotenv import load_dotenv

from src.agente_alex.graph import responder
from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta


load_dotenv()
URL_ALEX = os.getenv("URL_ALEX", "http://127.0.0.1:8004")

tarjeta = crear_tarjeta(
    "Agente de Alex",
    "Recomienda hasta tres recintos para ferias tecnológicas, gastronómicas, culturales o infantiles de 10 a 500 personas, en espacio interior o exterior, e indica para cada uno la capacidad, el % de ocupación, los m² por persona, los stands estimados, el estacionamiento y la accesibilidad. No da precios ni arriendos, no arma el menú ni el catering, no arma el programa de actividades y no reserva recintos.",
    URL_ALEX,
    [
        (
            "buscar_recintos",
            "Buscar recintos para una feria",
            "Busca recintos donde cabe el evento con un 10 % de holgura, según el tipo de feria, la cantidad de personas y si se prefiere un espacio interior o exterior, y avisa cuando un lugar queda demasiado grande.",
            "Voy a hacer una feria tecnológica para 150 personas, ¿dónde la puedo hacer?",
        ),
    ],
)

app = crear_app(tarjeta, responder)
