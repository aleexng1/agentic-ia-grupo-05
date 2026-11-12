"""API del router del ecommerce.

    uvicorn api.app:app --reload --port 8000
"""

import logging
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from src.config import MODELO
from src.router.graph import construir_grafo

log = logging.getLogger("uvicorn.error")

VERSION = "0.1.0"

DESCRIPCION = """
Recibe el mensaje de un cliente de la tienda y lo deriva a uno de tres agentes:

- **preventa**: intención de compra, productos, precios, tallas, stock, promociones y formas de pago antes de comprar.
- **postventa**: quejas, reclamos, seguimiento de un pedido ya hecho, devoluciones, cambios, garantía o producto dañado.
- **generica**: mensajes sin relación con la tienda o saludos sin un pedido concreto.

La conversación se recuerda por `user_id`: cada usuario tiene su propio hilo de memoria.
"""

TAGS = [
    {"name": "salud", "description": "Estado del servicio."},
    {"name": "chat", "description": "Clasificación y respuesta de mensajes de clientes."},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # El grafo se compila una sola vez, al arrancar.
    app.state.grafo = construir_grafo()
    log.info("Grafo del router compilado (modelo: %s)", MODELO)
    yield


app = FastAPI(
    title="Ecommerce Router API",
    version=VERSION,
    description=DESCRIPCION,
    openapi_tags=TAGS,
    lifespan=lifespan,
)


# ── Modelos ──────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Mensaje de un cliente."""

    user_id: str = Field(
        min_length=1,
        description="Identificador del cliente. Se usa como hilo de memoria de la conversación.",
        examples=["cliente-123"],
    )
    texto: str = Field(
        min_length=1,
        description="Mensaje que escribió el cliente.",
        examples=["¿tienen la polera azul en talla M?"],
    )

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"user_id": "cliente-123", "texto": "¿tienen la polera azul en talla M?"}]}
    )


class ChatResponse(BaseModel):
    """Decisión del router y respuesta del agente elegido."""

    ruta: Literal["preventa", "postventa", "generica"] = Field(
        description="Agente al que se derivó el mensaje.",
        examples=["preventa"],
    )
    motivo: str = Field(
        description="Una frase que explica por qué se eligió esa ruta.",
        examples=["El cliente consulta por talla y color de un producto antes de comprar."],
    )
    respuesta: str = Field(
        description="Respuesta del agente para el cliente.",
        examples=["Soy el agente de preventa. Recibí: ¿tienen la polera azul en talla M?. "
                  "Pronto podré ayudarte con productos y compras."],
    )


class HealthResponse(BaseModel):
    ok: bool = Field(description="true si el servicio está arriba.", examples=[True])
    modelo: str = Field(description="Modelo configurado en MODELO.", examples=[MODELO])


class ErrorResponse(BaseModel):
    detail: str = Field(
        description="Mensaje de error para el cliente (sin detalles internos).",
        examples=["El modelo no respondió. Intenta de nuevo en unos segundos."],
    )


# ── Rutas ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["salud"], response_model=HealthResponse, summary="Estado del servicio")
def health() -> HealthResponse:
    return HealthResponse(ok=True, modelo=MODELO)


@app.post(
    "/chat",
    tags=["chat"],
    response_model=ChatResponse,
    summary="Clasifica un mensaje y responde",
    responses={
        200: {"description": "Mensaje clasificado y respondido."},
        422: {"description": "Body inválido: falta `user_id` o `texto`, o vienen vacíos."},
        502: {"model": ErrorResponse, "description": "El modelo de lenguaje falló o no respondió."},
    },
)
def chat(body: ChatRequest, request: Request) -> ChatResponse:
    grafo = request.app.state.grafo
    try:
        estado = grafo.invoke(
            {"mensaje": body.texto},
            {"configurable": {"thread_id": body.user_id}},
        )
    except Exception:
        # El detalle (y el stack trace) queda solo en el log del servidor.
        log.exception("Falló el grafo del router para user_id=%s", body.user_id)
        raise HTTPException(status_code=502, detail="El modelo no respondió. Intenta de nuevo en unos segundos.")

    return ChatResponse(ruta=estado["ruta"], motivo=estado["motivo"], respuesta=estado["respuesta"])
