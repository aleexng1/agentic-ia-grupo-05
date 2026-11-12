"""Construcción de la aplicación HTTP compartida por los agentes A2A."""

from fastapi import FastAPI

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import (
    add_a2a_routes_to_fastapi,
    create_agent_card_routes,
    create_jsonrpc_routes,
)
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard

from src.comun.executor import Executor
from src.comun.panel import crear_panel


def registrar_agente(app: FastAPI, tarjeta: AgentCard, responder, prefijo: str = "") -> None:
    """Publica la ficha y el JSON-RPC A2A de un agente bajo el prefijo indicado.

    Se registran como rutas de la misma app (y no como sub-aplicación montada) para
    que el JSON-RPC responda en la dirección exacta de la ficha, sin redirecciones.
    """
    manejador = DefaultRequestHandler(
        agent_executor=Executor(responder),
        task_store=InMemoryTaskStore(),
        agent_card=tarjeta,
    )
    add_a2a_routes_to_fastapi(
        app,
        agent_card_routes=create_agent_card_routes(
            tarjeta, card_url=f"{prefijo}/.well-known/agent-card.json"
        ),
        jsonrpc_routes=create_jsonrpc_routes(manejador, rpc_url=prefijo or "/"),
    )


def crear_app(tarjeta: AgentCard, responder, responder_panel=None) -> FastAPI:
    """Crea FastAPI con JSON-RPC A2A, la tarjeta pública, el panel y el chequeo de salud."""
    app = FastAPI()
    registrar_agente(app, tarjeta, responder)
    app.include_router(crear_panel(responder_panel or responder))

    @app.get("/salud")
    async def salud() -> dict[str, bool]:
        return {"ok": True}

    return app
