"""API del agente principal (FastAPI).

Se levanta con (desde tarea-final-c2/):  uvicorn api.app:app --port 8000
En Heroku: APP_MODULE=api.app:app (ver Procfile y docs/reparto.md).

- GET  /                          chat web (web/index.html), público
- GET  /health                    chequeo de salud, público
- POST /chat                      {thread_id?, texto, imagen?, gasto?}; exige X-API-Key
- GET  /registro/{id_ejecucion}   una fila de la tabla ejecuciones; exige X-API-Key

Formatos exactos en docs/contratos.md (§2 y §11). /chat corre el grafo del agente principal
(src/principal/grafo.py). Una pieza que todavía no existe responde estado_final="error" con un
mensaje claro, o 501 si es la API misma: nunca una respuesta inventada.
"""

from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from src.comun.config import CARPETA_PROYECTO
from src.comun.errores import traducir_error
from src.comun.registro import configurar_registro, leer_ejecucion, obtener_registro
from src.comun.seguridad import CABECERA, proteger_app, revisar_clave
from src.principal.grafo import ErrorDeEjecucion, responder
from src.principal.router import MensajeInvalido

configurar_registro()
_REGISTRO = obtener_registro()

ARCHIVO_CHAT = CARPETA_PROYECTO / "web" / "index.html"

app = FastAPI(title="Revisor de rendiciones · Comercial Los Alerces SpA (ficticia)")


class Imagen(BaseModel):
    """Imagen de la boleta, igual que el FilePart del encargo A2A (docs/contratos.md)."""

    mime_type: Literal["image/jpeg", "image/png", "image/webp"]
    datos_base64: str = Field(min_length=1)


class SolicitudChat(BaseModel):
    # thread_id opcional (agregado por Alex): si no viene, se crea uno nuevo por turno.
    thread_id: str | None = Field(default=None, max_length=100)
    # El largo (1 a 4000) lo revisa el router antes de llamar al modelo, con un mensaje claro.
    texto: str
    imagen: Imagen | None = None
    # gasto opcional (agregado por Alex): un Gasto (contrato §4) + rut_emisor y folio opcionales.
    gasto: dict | None = None


def exigir_clave(x_api_key: str | None = Header(default=None, alias=CABECERA)) -> None:
    """Protege una ruta GET con la misma regla que el middleware usa para los POST."""
    rechazo = revisar_clave(x_api_key)
    if rechazo is not None:
        codigo, mensaje = rechazo
        raise HTTPException(status_code=codigo, detail=mensaje)


@app.get("/", include_in_schema=False)
async def chat_web() -> FileResponse:
    return FileResponse(ARCHIVO_CHAT, media_type="text/html; charset=utf-8", headers={"Cache-Control": "no-store"})


@app.get("/health")
async def health() -> dict[str, bool]:
    return {"ok": True}


@app.post("/chat")
async def chat(solicitud: SolicitudChat) -> dict:
    imagen = solicitud.imagen.model_dump() if solicitud.imagen else None
    try:
        return await responder(solicitud.thread_id, solicitud.texto, imagen, solicitud.gasto)
    except MensajeInvalido as error:
        raise HTTPException(status_code=422, detail=str(error)) from None
    except ErrorDeEjecucion as error:
        raise HTTPException(status_code=502, detail=f"{error} (id_ejecucion: {error.id_ejecucion})") from None
    except NotImplementedError as error:
        raise HTTPException(status_code=501, detail=f"Todavía no implementado: {error}") from None
    except Exception as error:
        _REGISTRO.error("falla en /chat · %s", traducir_error(error))
        raise HTTPException(status_code=502, detail=traducir_error(error)) from None


@app.get("/registro/{id_ejecucion}", dependencies=[Depends(exigir_clave)])
async def registro(id_ejecucion: str) -> dict:
    try:
        fila = leer_ejecucion(id_ejecucion)
    except NotImplementedError as error:
        raise HTTPException(status_code=501, detail=f"Todavía no implementado: {error}") from None
    if fila is None:
        raise HTTPException(status_code=404, detail="No existe una ejecución con ese id.")
    return fila


# Todo POST exige la clave API_KEY_SERVICIO en la cabecera X-API-Key (src/comun/seguridad.py).
proteger_app(app)
