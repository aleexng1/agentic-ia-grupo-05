"""Página local para ver y consultar a los agentes A2A.

El navegador solo habla con este servidor; este servidor habla con los agentes.
Así no hay problemas de CORS y el navegador nunca ve las URLs ni el .env.

Arranque (solo en local):
    uvicorn src.web.app:app --host 127.0.0.1 --port 8080
"""

import asyncio
import os
import uuid
from pathlib import Path
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

CARPETA_WEB = Path(__file__).resolve().parent
load_dotenv(CARPETA_WEB.parents[1] / ".env")

# Nombre que ve el navegador -> (variable del .env, dirección por defecto).
AGENTES = {
    "viajes": ("URL_VIAJES", "http://127.0.0.1:8000"),
    "restaurantes": ("URL_RESTAURANTES", "http://127.0.0.1:8001"),
    "coordinador": ("URL_COORDINADOR", "http://127.0.0.1:8002"),
}

TIMEOUT_CONEXION = 5.0  # segundos para lograr conectar con un agente
TIMEOUT_FICHA = 5.0  # segundos para leer una ficha
TIMEOUT_MENSAJE = 120.0  # segundos para una respuesta (el coordinador puede encadenar agentes)
LARGO_MAX_TEXTO = 2000
LARGO_MAX_LINEA = 300
HOSTS_PERMITIDOS = {"127.0.0.1", "localhost"}

# Las pruebas ponen aquí un transporte falso para no usar la red.
_transporte = None


def _cliente(timeout):
    return httpx.AsyncClient(
        timeout=httpx.Timeout(timeout, connect=TIMEOUT_CONEXION),
        transport=_transporte,
    )


def _url(agente):
    variable, por_defecto = AGENTES[agente]
    return (os.getenv(variable) or por_defecto).rstrip("/")


def _una_linea(texto):
    linea = " ".join(str(texto).split())
    return linea if len(linea) <= LARGO_MAX_LINEA else linea[:LARGO_MAX_LINEA] + "..."


def _motivo(error):
    """Explica en una línea por qué falló una llamada, sin mostrar direcciones."""
    if isinstance(error, httpx.ConnectError):
        return "no responde (¿está levantado?)"
    if isinstance(error, httpx.TimeoutException):
        return "tardó demasiado en responder"
    if isinstance(error, httpx.HTTPError):
        return f"falló la conexión ({type(error).__name__})"
    return f"falló ({type(error).__name__})"


def verificar_local(request: Request):
    """Solo acepta peticiones que vienen de esta misma máquina y de esta misma página."""
    host = request.headers.get("host", "")
    if urlparse("//" + host).hostname not in HOSTS_PERMITIDOS:
        raise HTTPException(403, "Solo se acepta acceso local (127.0.0.1).")
    origen = request.headers.get("origin")
    if origen and urlparse(origen).netloc != host:
        raise HTTPException(403, "Origen no permitido.")


app = FastAPI(
    title="Agentes A2A (página local)",
    dependencies=[Depends(verificar_local)],
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


async def _leer_ficha(cliente, agente):
    """Lee la ficha de un agente. Si no está disponible, lo dice en vez de fallar."""
    no_disponible = {"id": agente, "disponible": False}
    try:
        respuesta = await cliente.get(_url(agente) + "/.well-known/agent-card.json")
        if respuesta.status_code != 200:
            return {**no_disponible, "motivo": f"respondió HTTP {respuesta.status_code}"}
        ficha = respuesta.json()
        skills = [
            {
                "nombre": str(s.get("name", "")),
                "descripcion": str(s.get("description", "")),
                "ejemplo": str((s.get("examples") or [""])[0]),
            }
            for s in ficha.get("skills", [])
        ]
        return {
            "id": agente,
            "disponible": True,
            "nombre": str(ficha.get("name", agente)),
            "descripcion": str(ficha.get("description", "")),
            "skills": skills,
        }
    except httpx.HTTPError as error:
        return {**no_disponible, "motivo": _motivo(error)}
    except (ValueError, AttributeError, TypeError):
        return {**no_disponible, "motivo": "su ficha no tiene el formato esperado"}


@app.get("/")
async def pagina():
    return FileResponse(CARPETA_WEB / "static" / "index.html", headers={"Cache-Control": "no-store"})


@app.get("/api/agentes")
async def listar_agentes():
    async with _cliente(TIMEOUT_FICHA) as cliente:
        return await asyncio.gather(*(_leer_ficha(cliente, agente) for agente in AGENTES))


class Mensaje(BaseModel):
    agente: str
    texto: str = Field(max_length=LARGO_MAX_TEXTO)
    contextId: str | None = Field(default=None, max_length=100)


async def _enviar(agente, texto, context_id):
    """Manda SendMessage al agente. Devuelve {"texto", "contextId"} o {"error", "contextId"}."""
    peticion = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "SendMessage",
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "contextId": context_id,
                "role": "ROLE_USER",
                "parts": [{"text": texto}],
            }
        },
    }
    cabeceras = {"A2A-Version": "1.0", "Content-Type": "application/json"}
    fallo = {"contextId": context_id}
    try:
        async with _cliente(TIMEOUT_MENSAJE) as cliente:
            respuesta = await cliente.post(_url(agente) + "/", json=peticion, headers=cabeceras)
    except httpx.HTTPError as error:
        return {**fallo, "error": f"El agente {_motivo(error)}."}

    try:
        cuerpo = respuesta.json()
    except ValueError:
        return {**fallo, "error": f"El agente respondió algo que no es JSON (HTTP {respuesta.status_code})."}

    # Los errores de A2A pueden venir con HTTP 200: se mira siempre el cuerpo.
    if isinstance(cuerpo, dict) and cuerpo.get("error"):
        error = cuerpo["error"]
        if isinstance(error, dict):
            detalle = f"{error.get('code', '?')}: {error.get('message', '')}"
        else:
            detalle = str(error)
        return {**fallo, "error": _una_linea(f"El agente respondió con error {detalle}")}

    try:
        mensaje = cuerpo["result"]["message"]
        return {
            "texto": str(mensaje["parts"][0]["text"]),
            "contextId": mensaje.get("contextId") or context_id,
        }
    except (KeyError, IndexError, TypeError):
        return {**fallo, "error": "La respuesta del agente no trae result.message.parts[0].text."}


@app.post("/api/mensaje")
async def mandar_mensaje(mensaje: Mensaje):
    if mensaje.agente not in AGENTES:
        return JSONResponse({"error": "Ese agente no existe."}, status_code=404)
    texto = mensaje.texto.strip()
    if not texto:
        return JSONResponse({"error": "Escribe un mensaje."}, status_code=400)
    # Si la conversación es nueva, el servidor inventa el contextId; la página lo recuerda.
    context_id = mensaje.contextId or str(uuid.uuid4())
    return await _enviar(mensaje.agente, texto, context_id)
