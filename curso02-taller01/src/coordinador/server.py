"""Servidor A2A del coordinador (supervisor): la ficha + la app, usando lo de src/comun."""

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import HTTPException

from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta
from src.coordinador import graph as supervisor

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

URL_COORDINADOR = os.getenv("URL_COORDINADOR", "http://127.0.0.1:8002")

tarjeta = crear_tarjeta(
    "Coordinador",
    "Supervisor: elige entre el agente de viajes y el de restaurantes y les delega la consulta; no responde por sí mismo.",
    URL_COORDINADOR,
    [
        (
            "consultas_de_viajes",
            "Consultas de viajes",
            "Reenvía las preguntas sobre vuelos y hoteles al agente de viajes.",
            "Vuelo de Santiago a Lima el 2026-11-10",
        ),
        (
            "consultas_de_restaurantes",
            "Consultas de restaurantes",
            "Reenvía las preguntas sobre dónde comer al agente de restaurantes.",
            "Algo peruano en Lima, zona Miraflores",
        ),
    ],
)

# supervisor.iniciar lee las fichas de los agentes una sola vez, cuando arranca el servidor.
app = crear_app(tarjeta, supervisor.responder, al_iniciar=supervisor.iniciar)


@app.get("/decision/{context_id}")
async def ultima_decision(context_id: str):
    """Ruta auxiliar (fuera del contrato A2A): qué agente eligió el supervisor y por qué, en esa conversación.

    La usa scripts/probar_supervisor.py para mostrar el motivo. Solo guarda lo último y en memoria.
    """
    decision = supervisor.DECISIONES.get(context_id)
    if decision is None:
        raise HTTPException(404, "No hay una decisión guardada para ese context_id.")
    return decision
