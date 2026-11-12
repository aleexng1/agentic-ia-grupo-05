"""Ficha A2A del agente de recintos y capacidad de Alex; app.py lo publica en /agentes/alex."""

from src.agente_alex.graph import responder
from src.comun.config import url_agente
from src.comun.tarjeta import crear_tarjeta

tarjeta = crear_tarjeta(
    "Agente de Alex",
    "Recomienda hasta tres recintos para ferias tecnológicas, gastronómicas, culturales o infantiles de 10 a 500 personas, en espacio interior o exterior, e indica para cada uno la capacidad, el % de ocupación, los m² por persona, los stands estimados, el estacionamiento y la accesibilidad. No da precios ni arriendos, no arma el menú ni el catering, no arma el programa de actividades y no reserva recintos.",
    url_agente("alex"),
    [
        (
            "buscar_recintos",
            "Buscar recintos para una feria",
            "Busca recintos donde cabe el evento con un 10 % de holgura, según el tipo de feria, la cantidad de personas y si se prefiere un espacio interior o exterior, y avisa cuando un lugar queda demasiado grande.",
            "Voy a hacer una feria tecnológica para 150 personas, ¿dónde la puedo hacer?",
        ),
    ],
)
