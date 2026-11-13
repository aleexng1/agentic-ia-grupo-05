"""Interfaz web sencilla para consultar y revisar el estado de los agentes."""

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel


_ARCHIVO_PANEL = Path(__file__).with_name("panel.html")


class ConsultaPanel(BaseModel):
    """Pregunta enviada desde la página web."""

    texto: str
    context_id: str | None = None


def crear_panel(responder) -> APIRouter:
    """Crea la página y el endpoint de consulta para el agente activo.

    responder(texto, context_id) puede devolver un texto o un diccionario con
    "respuesta", "agente" y "motivo" (así lo hace el coordinador).
    La autorización de X-API-Key corresponde al servidor (aporte de Matías),
    no a la pantalla de ingreso. Este router no sustituye esa protección.
    """
    router = APIRouter()

    @router.get("/", include_in_schema=False)
    async def mostrar_panel() -> FileResponse:
        return FileResponse(
            _ARCHIVO_PANEL,
            media_type="text/html; charset=utf-8",
            headers={
                "Cache-Control": "no-store",
                "Referrer-Policy": "no-referrer",
                "X-Content-Type-Options": "nosniff",
            },
        )

    @router.post("/panel/consultar")
    async def consultar(solicitud: ConsultaPanel, respuesta_http: Response) -> dict[str, str]:
        respuesta_http.headers["Cache-Control"] = "no-store"
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

        if not isinstance(respuesta, dict):
            respuesta = {"respuesta": str(respuesta)}
        return {
            "respuesta": str(respuesta.get("respuesta", "")),
            "context_id": context_id,
            "agente": str(respuesta.get("agente", "")),
            "motivo": str(respuesta.get("motivo", "")),
        }

    return router
