"""Control de acceso: la API exige la clave API_KEY_SERVICIO en la cabecera X-API-Key.

Origen: copiado de taller-02-c2 (allí la variable se llamaba CLAVE_API).

- Protege toda petición que modifica o envía datos (POST, PUT, PATCH, DELETE): POST /chat
  y el JSON-RPC A2A. Las lecturas sensibles (GET /registro/{id}) se protegen en api/app.py
  con revisar_clave, porque este middleware solo mira el método.
- Quedan públicas las otras lecturas (GET): la página del chat, las fichas A2A
  (/.well-known/agent-card.json) y /health.
- Si falta la clave o no coincide responde 401 con {"detail": "mensaje"}; ese es el formato
  acordado con el frontend. Si el servidor no tiene API_KEY_SERVICIO, no queda abierto: rechaza
  con 503 y lo avisa al arrancar.
- La clave nunca se escribe en el código, en la página ni en los registros.
"""

import os
import re
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
    "El servidor no tiene configurada la clave de acceso (API_KEY_SERVICIO), así que no acepta "
    "consultas. Avisa a quien lo administra."
)

_REGISTRO = obtener_registro()


def clave_configurada() -> str:
    """Clave de acceso del servidor (API_KEY_SERVICIO); vacía si no se configuró."""
    return os.getenv("API_KEY_SERVICIO", "").strip()


def revisar_clave(recibida: bytes | str | None) -> tuple[int, str] | None:
    """Compara la clave recibida con API_KEY_SERVICIO.

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
                    503: "servidor sin API_KEY_SERVICIO",
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
    """Al arrancar, avisa con un error claro si API_KEY_SERVICIO está vacía."""
    if not clave_configurada():
        _REGISTRO.error(
            "API_KEY_SERVICIO está vacía: el servidor rechaza todas las consultas (503) hasta que se "
            "configure. Defínela en el .env (o en las Config Vars de Heroku) y reinicia."
        )


def proteger_app(app: FastAPI) -> FastAPI:
    """Activa el control de acceso en la app y el aviso de arranque."""
    app.add_middleware(ControlDeAcceso)
    app.router.on_startup.append(avisar_si_falta_clave)
    return app


# ---------------------------------------------------------------------------
# Acciones permitidas y token A2A (C2, dueño: Matías). Ver docs/contratos.md §6.
# ---------------------------------------------------------------------------

# Acciones que el agente principal puede ejecutar. Cualquier otra se bloquea y la
# ejecución queda con estado_final = "bloqueado". Se mantiene igual a docs/contratos.md.
ACCIONES_PERMITIDAS = frozenset(
    {
        "buscar_politica",
        "validar_gasto",
        "consultar_fondo",
        "emitir_veredicto",
        "delegar_verificador",
    }
)


class AccionNoAutorizada(Exception):
    """Se pidió una acción que no está en ACCIONES_PERMITIDAS. No se ejecuta."""

    def __init__(self, accion: str) -> None:
        self.accion = accion
        super().__init__(
            f"Acción bloqueada: «{accion}» no está autorizada para este agente; no se ejecutó."
        )


def _nombre_para_log(accion: object) -> str:
    """Nombre de la acción apto para el log: una línea, corto y sin caracteres raros."""
    texto = re.sub(r"[^\w.-]", "_", str(accion))[:60]
    return texto or "(vacía)"


def exigir_accion_permitida(accion: str) -> None:
    """Bloquea una acción que no está en ACCIONES_PERMITIDAS.

    Lanza AccionNoAutorizada si `accion` no está en la lista (comparación exacta) y deja
    una línea en el log con el nombre de la acción, sin argumentos ni datos del gasto.
    El flujo que la llama marca la ejecución como "bloqueado" y NO ejecuta la acción.
    Ejemplo de acción a bloquear (caso GS-30 del golden set de c1): "modificar_registro".
    """
    if isinstance(accion, str) and accion in ACCIONES_PERMITIDAS:
        return
    _REGISTRO.warning("acción bloqueada · %s · no está en ACCIONES_PERMITIDAS", _nombre_para_log(accion))
    raise AccionNoAutorizada(str(accion))


CABECERA_A2A = "Authorization"
MENSAJE_A2A_FALTA = "Falta el token A2A. Envíalo en la cabecera Authorization: Bearer <token>."
MENSAJE_A2A_INCORRECTO = "El token A2A es incorrecto."
MENSAJE_A2A_SIN_CONFIGURAR = (
    "El verificador no tiene configurado el token A2A (TOKEN_A2A), así que no acepta encargos. "
    "Avisa a quien lo administra."
)


def token_a2a_configurado() -> str:
    """Token compartido del canal A2A (TOKEN_A2A); vacío si no se configuró."""
    return os.getenv("TOKEN_A2A", "").strip()


def revisar_token_a2a(recibido: bytes | str | None) -> tuple[int, str] | None:
    """Comprueba el token que el principal envía al verificador por A2A.

    `recibido` es el valor completo de la cabecera Authorization ("Bearer <token>").
    Devuelve None si es correcto, o (código HTTP, mensaje) para rechazar: 503 si el
    verificador no tiene TOKEN_A2A, 401 si falta, no es Bearer o no coincide.
    Compara bytes con secrets.compare_digest (no revela el token por el tiempo de respuesta).
    """
    esperado = token_a2a_configurado()
    if not esperado:
        return 503, MENSAJE_A2A_SIN_CONFIGURAR
    if isinstance(recibido, bytes):
        recibido = recibido.decode("latin-1")
    partes = (recibido or "").strip().split(None, 1)
    if not partes:
        return 401, MENSAJE_A2A_FALTA
    if len(partes) != 2 or partes[0].lower() != "bearer" or not partes[1].strip():
        return 401, MENSAJE_A2A_FALTA
    if not secrets.compare_digest(partes[1].strip().encode("utf-8"), esperado.encode("utf-8")):
        return 401, MENSAJE_A2A_INCORRECTO
    return None


class ControlTokenA2A:
    """Middleware ASGI del verificador: exige Authorization: Bearer <TOKEN_A2A> en POST/PUT/PATCH/DELETE.

    Las lecturas (GET /health y la ficha /.well-known/agent-card.json) quedan públicas.
    Nunca registra el token ni las cabeceras: solo la ruta y el motivo del rechazo.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self._cabecera = CABECERA_A2A.lower().encode("latin-1")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope["method"] in METODOS_PROTEGIDOS:
            recibido = next(
                (valor for nombre, valor in scope["headers"] if nombre == self._cabecera),
                None,
            )
            rechazo = revisar_token_a2a(recibido)
            if rechazo is not None:
                codigo, mensaje = rechazo
                motivo = {
                    503: "verificador sin TOKEN_A2A",
                    401: "token incorrecto" if mensaje == MENSAJE_A2A_INCORRECTO else "sin token",
                }[codigo]
                _REGISTRO.warning("encargo A2A rechazado · %s %s · %s", scope["method"], scope["path"], motivo)
                respuesta = JSONResponse(status_code=codigo, content={"detail": mensaje})
                await respuesta(scope, receive, send)
                return
        await self.app(scope, receive, send)


async def avisar_si_falta_token_a2a() -> None:
    """Al arrancar el verificador, avisa con un error claro si TOKEN_A2A está vacío."""
    if not token_a2a_configurado():
        _REGISTRO.error(
            "TOKEN_A2A está vacío: el verificador rechaza todos los encargos (503) hasta que se "
            "configure. Defínelo en el .env (o en las Config Vars de Heroku) y reinicia."
        )


def proteger_con_token_a2a(app: FastAPI) -> FastAPI:
    """Protege la app del verificador con TOKEN_A2A (reemplaza a proteger_app en src/verificador/app.py)."""
    app.add_middleware(ControlTokenA2A)
    app.router.on_startup.append(avisar_si_falta_token_a2a)
    return app
