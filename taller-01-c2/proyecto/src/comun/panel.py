"""Interfaz web sencilla para consultar y revisar el estado de los agentes."""

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel


_ARCHIVO_PANEL = Path(__file__).with_name("panel.html")
_ARCHIVO_ESTUDIO = Path(__file__).with_name("estudio.html")


class ConsultaPanel(BaseModel):
    """Pregunta enviada desde la página web."""

    texto: str
    context_id: str | None = None


def crear_panel(responder) -> APIRouter:
    """Crea la página y el endpoint de consulta para el agente activo."""
    router = APIRouter()

    @router.get("/", include_in_schema=False)
    async def mostrar_panel() -> FileResponse:
        return FileResponse(_ARCHIVO_PANEL, media_type="text/html; charset=utf-8")

    @router.get("/estudio", include_in_schema=False)
    async def mostrar_estudio() -> FileResponse:
        return FileResponse(_ARCHIVO_ESTUDIO, media_type="text/html; charset=utf-8")

    @router.post("/panel/consultar")
    async def consultar(solicitud: ConsultaPanel) -> dict[str, str]:
        texto = solicitud.texto.strip()
        if not texto:
            raise HTTPException(status_code=400, detail="Escribe una pregunta para continuar.")

        context_id = solicitud.context_id or str(uuid4())
        try:
            respuesta = await responder(texto, context_id)
        except Exception as error:
            detalle = str(error).replace("\r", " ").replace("\n", " ").strip()
            if not detalle:
                detalle = error.__class__.__name__
            raise HTTPException(
                status_code=502,
                detail=f"No se pudo consultar al agente: {detalle}",
            ) from None

        return {"respuesta": respuesta, "context_id": context_id}

    return router
