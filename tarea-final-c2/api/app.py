"""API del agente principal (FastAPI).

Se levanta con (desde tarea-final-c2/):  uvicorn api.app:app --port 8000
En Heroku: APP_MODULE=api.app:app (ver Procfile y docs/reparto.md).

- GET  /                          chat web (web/index.html), público
- GET  /health                    chequeo de salud, público
- POST /chat                      {thread_id?, texto, imagen?, gasto?}; exige X-API-Key.
                                  202 {id_ejecucion, estado: "en_proceso", consultar, thread_id} y el
                                  grafo corre en segundo plano (src/principal/en_segundo_plano.py).
                                  Con ?esperar=true responde como antes, síncrono (200 / 422 / 502).
- GET  /registro/{id_ejecucion}   estado de la ejecución (en_proceso / ok / bloqueado / fallback /
                                  error) y, al terminar, la respuesta completa; exige X-API-Key

Formatos exactos en docs/contratos.md (§2 y §11). /chat corre el grafo del agente principal
(src/principal/grafo.py). Una pieza que todavía no existe responde estado_final="error" con un
mensaje claro, o 501 si es la API misma: nunca una respuesta inventada.
"""

from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from src.comun.config import CARPETA_PROYECTO
from src.comun.errores import traducir_error
from src.comun.registro import configurar_registro, leer_ejecucion, obtener_registro
from src.comun.seguridad import CABECERA, proteger_app, revisar_clave
from src.principal import en_segundo_plano
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


@app.post("/chat", status_code=202)
async def chat(solicitud: SolicitudChat, esperar: bool = False):
    """202 + id_ejecucion (el grafo sigue en segundo plano), o la respuesta completa con ?esperar=true.

    Heroku corta a los 30 s y una revisión de gasto tarda más (docs/medicion-tiempos.md); el modo
    síncrono queda para uso local, el evaluador y las pruebas.
    """
    imagen = solicitud.imagen.model_dump() if solicitud.imagen else None
    if not esperar:
        try:
            aceptado = en_segundo_plano.lanzar(solicitud.thread_id, solicitud.texto, imagen, solicitud.gasto)
        except MensajeInvalido as error:
            raise HTTPException(status_code=422, detail=str(error)) from None
        except ValueError as error:  # configuración no válida (TIEMPO_MAX_EJECUCION_SEG, ...)
            raise HTTPException(status_code=500, detail=str(error)) from None
        return JSONResponse(status_code=202, content=aceptado)
    try:
        return JSONResponse(status_code=200, content=await responder(solicitud.thread_id, solicitud.texto, imagen, solicitud.gasto))
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
    """Estado de una ejecución: la de este proceso (memoria) más su fila de `ejecuciones` (Postgres).

    - En proceso: {id_ejecucion, estado: "en_proceso", thread_id, inicio, segundos}.
    - Terminada: los campos de la fila (ruta, pasos, estado_final, ...) + estado + resultado (la
      respuesta completa de /chat) o detail (el mensaje de error). Si el proceso se reinició, solo
      queda la fila: estado = estado_final y resultado = null.
    """
    actual = en_segundo_plano.consultar(id_ejecucion)
    fila, error_registro = None, None
    if actual is None or actual["estado"] != "en_proceso":
        try:
            fila = leer_ejecucion(id_ejecucion)
        except NotImplementedError as error:
            error_registro = f"Todavía no implementado: {error}"
        except Exception as error:  # noqa: BLE001 (sin DATABASE_URL o base caída: se dice, no se inventa)
            error_registro = traducir_error(error)
    if actual is None:
        if fila is None and error_registro:
            raise HTTPException(status_code=503, detail=f"El registro de ejecuciones no está disponible: {error_registro}")
        if fila is None:
            raise HTTPException(status_code=404, detail="No existe una ejecución con ese id.")
        return {**fila, "estado": fila["estado_final"], "resultado": None}
    return {**(fila or {}), **actual}


# Todo POST exige la clave API_KEY_SERVICIO en la cabecera X-API-Key (src/comun/seguridad.py).
proteger_app(app)
