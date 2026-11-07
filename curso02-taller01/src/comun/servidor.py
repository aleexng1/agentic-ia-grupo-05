"""El servidor A2A común: recibe mensajes por red, se los pasa al agente y devuelve su respuesta."""

from contextlib import asynccontextmanager

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import (
    create_agent_card_routes,
    create_jsonrpc_routes,
)
from a2a.server.routes.fastapi_routes import add_a2a_routes_to_fastapi
from a2a.server.tasks import InMemoryTaskStore
from fastapi import FastAPI

from src.comun.executor import Executor


def crear_app(tarjeta, responder, al_iniciar=None):
    """Arma la aplicación FastAPI lista para correr con uvicorn.

    Rutas que publica:
      - POST /                              recibe los mensajes A2A (JSON-RPC)
      - GET  /.well-known/agent-card.json   la ficha del agente
      - GET  /salud                         {"ok": true} si el servidor está vivo

    al_iniciar (opcional): función async que se ejecuta una sola vez cuando arranca
    el servidor, antes de aceptar mensajes (por ejemplo, para leer las fichas de otros agentes).
    """
    # DefaultRequestHandler es, en la 1.3.0, la implementación vigente (V2):
    # coordina al ejecutor, el almacén de tareas y la ficha.
    manejador = DefaultRequestHandler(
        agent_executor=Executor(responder),
        task_store=InMemoryTaskStore(),
        agent_card=tarjeta,
    )

    @asynccontextmanager
    async def ciclo_de_vida(_app):
        # "lifespan" es el mecanismo de inicio vigente en FastAPI (on_event está en desuso).
        if al_iniciar is not None:
            await al_iniciar()
        yield

    app = FastAPI(title=tarjeta.name, lifespan=ciclo_de_vida)
    add_a2a_routes_to_fastapi(
        app,
        agent_card_routes=create_agent_card_routes(tarjeta),
        jsonrpc_routes=create_jsonrpc_routes(manejador, rpc_url="/"),
    )

    @app.get("/salud")
    async def salud():
        return {"ok": True}

    return app
