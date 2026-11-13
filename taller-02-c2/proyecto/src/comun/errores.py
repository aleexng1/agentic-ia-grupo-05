"""Traduce las fallas del proveedor (Gemini), de la red o de un agente a mensajes claros.

Un error nunca se presenta como respuesta exitosa: se convierte en ErrorDeServicio, que
el panel entrega como HTTP 502 con una sola línea entendible. Los mensajes no incluyen
trazas de Python ni claves.
"""

import os
import re

from src.comun.registro import una_linea


LARGO_MAXIMO_DETALLE = 200

MENSAJE_CLAVE_GEMINI = (
    "La clave de Gemini (GOOGLE_API_KEY) no es válida. Revísala en el .env o en las "
    "Config Vars de Heroku."
)
MENSAJE_SIN_CLAVE_GEMINI = (
    "Falta configurar la clave de Gemini (GOOGLE_API_KEY) en el .env o en las Config Vars."
)
MENSAJE_SIN_CUOTA = (
    "Gemini no tiene cuota disponible (límite de uso o créditos agotados). Espera unos "
    "minutos o revisa la cuenta en Google AI Studio."
)
MENSAJE_SIN_PERMISO = "La clave de Gemini no tiene permiso para usar el modelo configurado."
MENSAJE_MODELO = "El modelo de Gemini configurado (MODELO) no existe o no está disponible."
MENSAJE_TIEMPO = (
    "Se agotó el tiempo de espera: Gemini o un agente tardó demasiado en responder. "
    "Intenta de nuevo en un momento."
)
MENSAJE_SIN_CONEXION = (
    "No hay conexión con Gemini o con uno de los agentes. Revisa la conexión a internet e "
    "intenta de nuevo."
)
MENSAJE_NO_DISPONIBLE = "Gemini no está disponible en este momento. Intenta de nuevo en unos minutos."

# Los mensajes de arriba ya están pensados para la persona: si una capa los recibe de otra
# (por ejemplo, el coordinador de un agente), se dejan tal cual.
_MENSAJES_CONOCIDOS = (
    MENSAJE_CLAVE_GEMINI,
    MENSAJE_SIN_CLAVE_GEMINI,
    MENSAJE_SIN_CUOTA,
    MENSAJE_SIN_PERMISO,
    MENSAJE_MODELO,
    MENSAJE_TIEMPO,
    MENSAJE_SIN_CONEXION,
    MENSAJE_NO_DISPONIBLE,
)

_CLAVE_GOOGLE = re.compile(r"AIza[0-9A-Za-z_\-]{20,}")
_CLAVE_ASIGNADA = re.compile(
    r"(?i)(x-api-key|api[_-]?key|authorization)(\s*[:=]\s*)([^\s,;'\"]+)"
)
_PORTADOR = re.compile(r"(?i)(bearer)(\s+)([A-Za-z0-9._\-]{8,})")


class ErrorDeServicio(Exception):
    """Falla del proveedor de IA, de la red o de un agente; el mensaje ya es para la persona."""


def ocultar_secretos(texto: str) -> str:
    """Quita claves de un texto: la forma AIza…, «api_key=…» y los valores de las variables."""
    texto = _CLAVE_GOOGLE.sub("[clave oculta]", texto)
    for patron in (_CLAVE_ASIGNADA, _PORTADOR):
        texto = patron.sub(
            lambda coincidencia: f"{coincidencia.group(1)}{coincidencia.group(2)}[oculta]", texto
        )
    for variable in ("GOOGLE_API_KEY", "CLAVE_API"):
        valor = os.getenv(variable, "").strip()
        if len(valor) >= 8:
            texto = texto.replace(valor, "[clave oculta]")
    return texto


def detalle_tecnico(error: BaseException) -> str:
    """Detalle original del error, para el registro del servidor (no para la persona).

    Va en una sola línea, recortado y sin claves; sirve para diagnosticar en la terminal o
    en `heroku logs`, mientras la persona recibe el mensaje claro de traducir_error.
    """
    texto = una_linea(str(error)) or error.__class__.__name__
    texto = ocultar_secretos(texto)
    if len(texto) > 300:
        texto = texto[:299].rstrip() + "…"
    return texto


def _contiene(texto: str, *fragmentos: str) -> bool:
    return any(fragmento in texto for fragmento in fragmentos)


def traducir_error(error: BaseException) -> str:
    """Devuelve una sola línea, en español, que explica la falla sin trazas ni claves."""
    texto = una_linea(str(error)) or error.__class__.__name__
    for mensaje in _MENSAJES_CONOCIDOS:
        if mensaje in texto:
            return mensaje
    if isinstance(error, ErrorDeServicio):
        return ocultar_secretos(texto)

    crudo = f"{error.__class__.__name__} {texto}".lower()
    if _contiene(crudo, "api key not valid", "api_key_invalid", "invalid api key", "api key expired"):
        return MENSAJE_CLAVE_GEMINI
    if _contiene(
        crudo,
        "api key must be",
        "no api key",
        "api key is missing",
        "missing api key",
        "api key required",
        "provide api_key",
    ) or (
        "google_api_key" in crudo and _contiene(crudo, "not set", "missing", "must be")
    ):
        return MENSAJE_SIN_CLAVE_GEMINI
    if _contiene(crudo, "resource_exhausted", "quota", "rate limit", "rate_limit", "credits", " 429"):
        return MENSAJE_SIN_CUOTA
    if _contiene(crudo, "permission_denied", " 403"):
        return MENSAJE_SIN_PERMISO
    if _contiene(crudo, "not_found", "is not found", " 404") and "model" in crudo:
        return MENSAJE_MODELO
    if _contiene(crudo, "timeout", "timed out", "deadlineexceeded", "deadline exceeded"):
        return MENSAJE_TIEMPO
    if _contiene(
        crudo,
        "connecterror",
        "connectionerror",
        "connection error",
        "all connection attempts failed",
        "getaddrinfo",
        "name or service not known",
        "network is unreachable",
        "temporary failure in name resolution",
        "connect call failed",
        "ssl",
    ):
        return MENSAJE_SIN_CONEXION
    if _contiene(crudo, "unavailable", "overloaded", " 503"):
        return MENSAJE_NO_DISPONIBLE

    detalle = ocultar_secretos(texto)
    if len(detalle) > LARGO_MAXIMO_DETALLE:
        detalle = detalle[: LARGO_MAXIMO_DETALLE - 1].rstrip() + "…"
    return f"No se pudo completar la consulta: {detalle}"
