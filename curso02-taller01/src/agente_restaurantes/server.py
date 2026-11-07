"""Servidor A2A del agente de restaurantes: la ficha + la app, usando lo de src/comun."""

import os
from pathlib import Path

from dotenv import load_dotenv

from src.agente_restaurantes.crew import responder
from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

URL_RESTAURANTES = os.getenv("URL_RESTAURANTES", "http://127.0.0.1:8001")

tarjeta = crear_tarjeta(
    "Agente de restaurantes",
    "Recomienda restaurantes en LIM, BOG y EZE por zona y tipo de comida. No reserva.",
    URL_RESTAURANTES,
    [
        (
            "buscar_restaurantes",
            "Buscar restaurantes",
            "Recomienda restaurantes en Lima, Bogotá o Buenos Aires por zona y tipo de comida, con precio medio en CLP.",
            "Algo peruano en Lima, zona Miraflores",
        ),
        (
            "detalle_restaurante",
            "Detalle de un restaurante",
            "Da el horario, la zona, el precio medio y el plato estrella de un restaurante concreto.",
            "Cuéntame más de Brasa Zona G",
        ),
    ],
)

app = crear_app(tarjeta, responder)
