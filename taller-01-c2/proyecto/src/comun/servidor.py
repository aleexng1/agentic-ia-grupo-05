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


def crear_app(tarjeta: AgentCard, responder) -> FastAPI:
    """Crea FastAPI con JSON-RPC A2A, la tarjeta pública y el chequeo de salud."""
    app = FastAPI()
    manejador = DefaultRequestHandler(
        agent_executor=Executor(responder),
        task_store=InMemoryTaskStore(),
        agent_card=tarjeta,
    )

    add_a2a_routes_to_fastapi(
        app,
        agent_card_routes=create_agent_card_routes(tarjeta),
        jsonrpc_routes=create_jsonrpc_routes(manejador, rpc_url="/"),
    )
    app.include_router(crear_panel(responder))

    @app.get("/salud")
    async def salud() -> dict[str, bool]:
        return {"ok": True}

    return app
