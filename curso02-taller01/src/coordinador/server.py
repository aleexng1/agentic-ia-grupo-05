"""Servidor A2A del coordinador: la ficha + la app, usando lo de src/comun."""

import os
from pathlib import Path

from dotenv import load_dotenv

from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta
from src.coordinador.graph import responder

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

URL_COORDINADOR = os.getenv("URL_COORDINADOR", "http://127.0.0.1:8002")

tarjeta = crear_tarjeta(
    "Coordinador",
    "Delega consultas de viajes al agente de viajes; no responde por sí mismo.",
    URL_COORDINADOR,
    [
        (
            "delegar_viajes",
            "Delegar consultas de viajes",
            "Reenvía la pregunta al agente de viajes por A2A y devuelve su respuesta tal cual.",
            "Vuelo de Santiago a Lima el 2026-11-10",
        ),
    ],
)

app = crear_app(tarjeta, responder)
