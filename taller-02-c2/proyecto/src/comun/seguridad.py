"""Control de acceso: la API exige la clave CLAVE_API en la cabecera X-API-Key.

- Protege toda petición que modifica o envía datos (POST, PUT, PATCH, DELETE): la consulta
  del panel (/panel/consultar), el JSON-RPC A2A del coordinador (/) y el de cada agente
  (/agentes/{nombre}).
- Quedan públicas las lecturas (GET): la página del chat, las fichas A2A
  (/.well-known/agent-card.json) y /salud.
- Si falta la clave o no coincide responde 401 con {"detail": "mensaje"}; ese es el formato
  acordado con el frontend. Si el servidor no tiene CLAVE_API, no queda abierto: rechaza
  con 503 y lo avisa al arrancar.
- La clave nunca se escribe en el código, en la página ni en los registros.
"""

import os
import secrets

from fastapi import FastAPI
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from src.comun.registro import obtener_registro


CABECERA = "X-API-Key"
METODOS_PROTEGIDOS = frozenset({"POST", "PUT", "PATCH", "DELETE"})

MENSAJE_FALTA = "Falta la clave de acceso. Envíala en la cabecera X-API-Key."
MENSAJE_INCORRECTA = "La clave de acceso es incorrecta."
MENSAJE_SIN_CONFIGURAR = (
    "El servidor no tiene configurada la clave de acceso (CLAVE_API), así que no acepta "
    "consultas. Avisa a quien lo administra."
)

_REGISTRO = obtener_registro()


def clave_configurada() -> str:
    """Clave de acceso del servidor (CLAVE_API); vacía si no se configuró."""
    return os.getenv("CLAVE_API", "").strip()


def revisar_clave(recibida: bytes | str | None) -> tuple[int, str] | None:
    """Compara la clave recibida con CLAVE_API.

    Devuelve None si es correcta, o (código HTTP, mensaje) si hay que rechazar.
    La comparación usa secrets.compare_digest para no revelar la clave por el tiempo
    que tarda en fallar.
    """
    esperada = clave_configurada()
    if not esperada:
        return 503, MENSAJE_SIN_CONFIGURAR
    if isinstance(recibida, str):
        recibida = recibida.encode("utf-8")
    recibida = (recibida or b"").strip()
    if not recibida:
        return 401, MENSAJE_FALTA
    if not secrets.compare_digest(recibida, esperada.encode("utf-8")):
        return 401, MENSAJE_INCORRECTA
    return None


class ControlDeAcceso:
    """Middleware ASGI que rechaza las peticiones protegidas sin la clave correcta."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self._cabecera = CABECERA.lower().encode("latin-1")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope["method"] in METODOS_PROTEGIDOS:
            recibida = next(
                (valor for nombre, valor in scope["headers"] if nombre == self._cabecera),
                None,
            )
            rechazo = revisar_clave(recibida)
            if rechazo is not None:
                codigo, mensaje = rechazo
                # Solo se registra el motivo y la ruta: nunca la clave ni las cabeceras.
                motivo = {
                    503: "servidor sin CLAVE_API",
                    401: "sin clave" if recibida is None or not recibida.strip() else "clave incorrecta",
                }[codigo]
                _REGISTRO.warning(
                    "acceso rechazado · %s %s · %s", scope["method"], scope["path"], motivo
                )
                respuesta = JSONResponse(status_code=codigo, content={"detail": mensaje})
                await respuesta(scope, receive, send)
                return
        await self.app(scope, receive, send)


async def avisar_si_falta_clave() -> None:
    """Al arrancar, avisa con un error claro si CLAVE_API está vacía."""
    if not clave_configurada():
        _REGISTRO.error(
            "CLAVE_API está vacía: el servidor rechaza todas las consultas (503) hasta que se "
            "configure. Defínela en el .env (o en las Config Vars de Heroku) y reinicia."
        )


def proteger_app(app: FastAPI) -> FastAPI:
    """Activa el control de acceso en la app y el aviso de arranque."""
    app.add_middleware(ControlDeAcceso)
    app.router.on_startup.append(avisar_si_falta_clave)
    return app
