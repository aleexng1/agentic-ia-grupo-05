"""Aplicación HTTP del agente de restaurantes."""

import os

from dotenv import load_dotenv

from src.agente_restaurantes.crew import responder
from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta


load_dotenv()
URL_RESTAURANTES = os.getenv("URL_RESTAURANTES", "http://127.0.0.1:8001")

tarjeta = crear_tarjeta(
    "Agente de restaurantes",
    "Recomienda restaurantes en LIM, BOG y EZE por zona y tipo de comida. No reserva.",
    URL_RESTAURANTES,
    [
        (
            "buscar_restaurantes",
            "Buscar restaurantes",
            "Filtra restaurantes ficticios en Lima, Bogotá y Buenos Aires por tipo de comida.",
            "Busca comida peruana en Lima.",
        ),
        (
            "detalle_restaurante",
            "Ver detalle de restaurante",
            "Entrega zona, tipo de comida, precio medio y horario de un restaurante conocido.",
            "Dame los detalles de Don Julio.",
        ),
    ],
)

app = crear_app(tarjeta, responder)
