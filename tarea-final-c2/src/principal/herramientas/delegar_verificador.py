"""Delegación A2A al verificador de boletas.

Dueño: Alex (c2tf/alex-integracion). Encargo y respuesta en docs/contratos.md (§5 y §11.2).

Usa src/comun/cliente_a2a.enviar_partes con URL_VERIFICADOR, TIMEOUT_A2A_SEG y la cabecera
del canal: Authorization: Bearer <TOKEN_A2A> (el verificador usa proteger_con_token_a2a). La
cabecera solo va a URL_VERIFICADOR; la clave del servicio (X-API-Key) no sale del principal.
Si el principal no tiene TOKEN_A2A, no se llama al verificador: el encargo sería rechazado.

Nunca devuelve datos inventados. Ante cualquier falla devuelve un error estructurado:
    {"disponible": False, "tipo_fallo": <TIPOS_FALLO>, "motivo": "frase clara"}
y el grafo deja el gasto en «observar» con estado_final = "fallback".
"""

import asyncio
import base64

import httpx

from src.comun import config, seguridad
from src.comun.errores import traducir_error
from src.comun.registro import obtener_registro

CAMPOS = ("monto", "fecha", "rut_emisor", "folio", "categoria")
TIPOS_IMAGEN = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
TIPOS_FALLO = ("forzado", "encargo_invalido", "timeout", "sin_conexion", "rechazado", "respuesta_invalida", "error_verificador")

_REGISTRO = obtener_registro()


def fallo(tipo: str, motivo: str) -> dict:
    """Error estructurado: nunca trae campos leídos."""
    _REGISTRO.warning("a2a · verificador no disponible · %s · %s", tipo, motivo)
    return {"disponible": False, "tipo_fallo": tipo, "motivo": motivo}


def _cabeceras() -> dict[str, str]:
    """Cabecera del canal A2A (vacía si falta TOKEN_A2A). Nunca se registra en el log."""
    token = seguridad.token_a2a_configurado()
    return {seguridad.CABECERA_A2A: f"Bearer {token}"} if token else {}


def _partes(datos: bytes, tipo: str, declarado: dict) -> list:
    from a2a.types import Part
    from google.protobuf import struct_pb2

    valor = struct_pb2.Value()
    valor.struct_value.update({"tarea": "verificar_boleta", "declarado": declarado})
    return [
        Part(raw=datos, media_type=tipo, filename=f"boleta{TIPOS_IMAGEN[tipo]}"),
        Part(data=valor, media_type="application/json"),
    ]


def validar_respuesta(partes: list) -> dict | None:
    """La respuesta del verificador con el formato del contrato, o None si no lo cumple."""
    from google.protobuf import json_format

    datos = next((json_format.MessageToDict(p.data) for p in partes if p.WhichOneof("content") == "data"), None)
    if not isinstance(datos, dict):
        return None
    leido, cuadra, confianza = datos.get("leido"), datos.get("cuadra"), datos.get("confianza")
    if not isinstance(leido, dict) or not isinstance(cuadra, dict) or set(cuadra) != set(CAMPOS):
        return None
    if any(valor not in ("sí", "no") for valor in cuadra.values()):
        return None
    if not isinstance(confianza, (int, float)) or not 0 <= confianza <= 1:
        return None
    # Regla dura del contrato: un campo no leído no puede «cuadrar».
    if any(leido.get(campo) is None and cuadra[campo] == "sí" for campo in CAMPOS):
        return None
    if isinstance(leido.get("monto"), float):  # el JSON de A2A trae los números como float
        leido["monto"] = int(leido["monto"])
    return {
        "leido": {campo: leido.get(campo) for campo in CAMPOS},
        "cuadra": {campo: cuadra[campo] for campo in CAMPOS},
        "confianza": float(confianza),
        "observaciones": str(datos.get("observaciones", "")),
    }


def _clasificar_error(error: BaseException, segundos: float) -> dict:
    texto = f"{error.__class__.__name__} {error}".lower()
    if isinstance(error, (asyncio.TimeoutError, TimeoutError, httpx.TimeoutException)) or "timeout" in texto or "timed out" in texto:
        return fallo("timeout", f"el verificador no respondió en {segundos:g} s")
    if isinstance(error, (httpx.ConnectError, ConnectionError)) or "connect" in texto or "unreachable" in texto:
        return fallo("sin_conexion", "no hay conexión con el verificador (¿está levantado y URL_VERIFICADOR es correcta?)")
    if any(codigo in texto for codigo in (" 401", " 403", "401 ", "403 ", "unauthorized", "forbidden", " 503", "503 ")):
        return fallo("rechazado", "el verificador rechazó el encargo (clave o token del canal A2A)")
    mensaje = traducir_error(error)
    prefijo = "No se pudo completar la consulta: "
    while mensaje.count(prefijo) > 1:  # el verificador ya tradujo su error: no repetir el prefijo
        mensaje = mensaje.replace(prefijo, "", 1)
    return fallo("error_verificador", f"el verificador respondió con un error: {mensaje}")


async def delegar_verificador(imagen: dict, declarado: dict) -> dict:
    """Envía la boleta y los datos declarados al verificador y devuelve su respuesta.

    `imagen` = {"mime_type", "datos_base64"}; `declarado` = {"monto", "fecha", "rut_emisor",
    "folio", "categoria"}. Si todo sale bien devuelve {"disponible": True, "leido", "cuadra",
    "confianza", "observaciones"}; si no, el error estructurado de `fallo`.
    """
    from src.comun.cliente_a2a import enviar_partes

    if config.forzar_fallo_a2a():
        return fallo("forzado", "FORZAR_FALLO_A2A=1: se simuló que el verificador no responde")

    tipo = str((imagen or {}).get("mime_type", "")).lower()
    if tipo not in TIPOS_IMAGEN:
        return fallo("encargo_invalido", f"tipo de imagen no admitido: «{tipo or 'sin tipo'}»")
    try:
        datos = base64.b64decode((imagen or {}).get("datos_base64", ""), validate=True)
    except (ValueError, TypeError):
        return fallo("encargo_invalido", "la imagen no es base64 válido")
    if not datos:
        return fallo("encargo_invalido", "la imagen está vacía")
    declarado = {campo: (declarado or {}).get(campo) for campo in CAMPOS}
    cabeceras = _cabeceras()
    if not cabeceras:
        return fallo("rechazado", "el principal no tiene TOKEN_A2A configurado: el verificador rechazaría el encargo")

    url = config.url_verificador()
    segundos = config.timeout_a2a_seg()
    _REGISTRO.info("a2a · encargo → %s · imagen %s %d bytes · tiempo límite %g s", url, tipo, len(datos), segundos)
    try:
        partes = await asyncio.wait_for(
            enviar_partes(url, _partes(datos, tipo, declarado), cabeceras=cabeceras, tiempo_limite=segundos),
            timeout=segundos,
        )
    except Exception as error:  # noqa: BLE001 (toda falla se clasifica, ninguna se convierte en datos)
        return _clasificar_error(error, segundos)

    respuesta = validar_respuesta(partes)
    if respuesta is None:
        return fallo("respuesta_invalida", "la respuesta del verificador no tiene el formato del contrato")
    _REGISTRO.info(
        "a2a · respuesta ← verificador · confianza=%.2f · no cuadra: %s",
        respuesta["confianza"], ",".join(c for c, v in respuesta["cuadra"].items() if v != "sí") or "-",
    )
    return {"disponible": True, **respuesta}
