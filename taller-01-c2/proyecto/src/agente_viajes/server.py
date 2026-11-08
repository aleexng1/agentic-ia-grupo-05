"""Aplicación HTTP del agente de viajes."""

import os

from dotenv import load_dotenv

from src.agente_viajes.graph import responder
from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta


load_dotenv()
URL_VIAJES = os.getenv("URL_VIAJES", "http://127.0.0.1:8000")

tarjeta = crear_tarjeta(
    "Agente de viajes",
    "Busca vuelos y hoteles entre SCL, LIM, BOG y EZE con precios en CLP. No reserva ni cobra.",
    URL_VIAJES,
    [
        (
            "buscar_vuelos",
            "Buscar vuelos",
            "Consulta horarios y precios ficticios de vuelos entre SCL, LIM, BOG y EZE.",
            "Busca un vuelo de SCL a LIM para el 2026-12-10.",
        ),
        (
            "buscar_hoteles",
            "Buscar hoteles",
            "Consulta hoteles ficticios y su precio total según la cantidad de noches.",
            "Busca hoteles en Lima para 3 noches.",
        ),
    ],
)

app = crear_app(tarjeta, responder)
