"""Servidor A2A del agente de viajes: la ficha + la app, usando lo de src/comun."""

import os
from pathlib import Path

from dotenv import load_dotenv

from src.agente_viajes.graph import responder
from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

URL_VIAJES = os.getenv("URL_VIAJES", "http://127.0.0.1:8000")

tarjeta = crear_tarjeta(
    "Agente de viajes",
    "Busca vuelos y hoteles entre SCL, LIM, BOG y EZE con precios en CLP. No reserva ni cobra.",
    URL_VIAJES,
    [
        (
            "buscar_vuelos",
            "Buscar vuelos",
            "Busca vuelos entre SCL, LIM, BOG y EZE para una fecha, con aerolínea, horario y precio en CLP.",
            "Vuelo de Santiago a Lima el 2026-11-10",
        ),
        (
            "buscar_hoteles",
            "Buscar hoteles",
            "Busca hoteles en Santiago, Lima, Bogotá o Buenos Aires, con precio por noche y total en CLP.",
            "Hoteles en Bogotá por 3 noches",
        ),
    ],
)

app = crear_app(tarjeta, responder)
