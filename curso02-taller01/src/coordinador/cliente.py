"""Cliente para hablar con otro agente por A2A, usando el cliente de a2a-sdk."""

import asyncio

import httpx
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.client.errors import A2AClientTimeoutError, AgentCardResolutionError
from a2a.helpers import get_artifact_text, get_message_text, new_text_message
from a2a.types import Role, SendMessageRequest, TaskState
from a2a.utils.constants import TransportProtocol
from a2a.utils.errors import A2AError

TIMEOUT_CONEXION = 5.0  # segundos para lograr conectar con el agente
TIMEOUT_FICHA = 10.0  # segundos para descargar su ficha
TIMEOUT_MENSAJE = 120.0  # segundos para esperar su respuesta (puede estar usando un modelo)
LARGO_MAX_LINEA = 300

# Cliente ya armado por dirección. Se guarda junto al ciclo de eventos (event loop) donde se
# creó, porque la conexión HTTP no se puede reutilizar desde otro ciclo.
CLIENTES = {}  # url -> (ciclo, cliente)
FICHAS = {}  # url -> ficha del agente (para saber cómo se llama quién respondió)

# Las pruebas ponen aquí un transporte falso para no usar la red.
_transporte = None

ESTADOS_FALLIDOS = {
    TaskState.TASK_STATE_FAILED: "falló",
    TaskState.TASK_STATE_REJECTED: "rechazó la tarea",
    TaskState.TASK_STATE_CANCELED: "canceló la tarea",
}


class ErrorRemoto(Exception):
    """Un problema al hablar con otro agente, explicado en una sola línea."""


def _una_linea(texto):
    linea = " ".join(str(texto).split())
    return linea if len(linea) <= LARGO_MAX_LINEA else linea[:LARGO_MAX_LINEA] + "..."


def _explicar(error):
    """Convierte cualquier falla de red o del protocolo en una línea entendible."""
    # El SDK suele envolver el error de red original dentro de uno propio: se mira también la causa.
    for candidato in (error, error.__cause__):
        if isinstance(candidato, (A2AClientTimeoutError, asyncio.TimeoutError, httpx.TimeoutException)):
            return f"el agente no respondió a tiempo (más de {TIMEOUT_MENSAJE:.0f} s)"
        if isinstance(candidato, httpx.ConnectError):
            return "el agente no responde (¿está levantado?)"
    if isinstance(error, AgentCardResolutionError) and error.status_code:
        return f"su ficha respondió HTTP {error.status_code}"
    if isinstance(error, A2AError):
        # Incluye los errores JSON-RPC, que llegan con HTTP 200 pero el SDK convierte en excepción.
        return _una_linea(f"el agente respondió con error: {error}")
    return _una_linea(f"falló la comunicación con el agente ({type(error).__name__}: {error})")


def _cliente_http():
    return httpx.AsyncClient(
        timeout=httpx.Timeout(TIMEOUT_MENSAJE, connect=TIMEOUT_CONEXION),
        transport=_transporte,
    )


async def obtener_cliente(url):
    """Descarga la ficha del agente que vive en `url` y arma un cliente (sin streaming, JSONRPC)."""
    url = url.rstrip("/")
    ciclo = asyncio.get_running_loop()
    guardado = CLIENTES.get(url)
    if guardado and guardado[0] is ciclo:
        return guardado[1]

    http = _cliente_http()
    try:
        ficha = await A2ACardResolver(http, url).get_agent_card(http_kwargs={"timeout": TIMEOUT_FICHA})
        config = ClientConfig(
            streaming=False,
            supported_protocol_bindings=[TransportProtocol.JSONRPC],
            httpx_client=http,  # el SDK le agrega la cabecera A2A-Version
        )
        cliente = ClientFactory(config).create(ficha)
    except Exception as error:
        await http.aclose()
        raise ErrorRemoto(f"no pude leer la ficha del agente: {_explicar(error)}") from None
    CLIENTES[url] = (ciclo, cliente)
    FICHAS[url] = ficha
    return cliente


def _texto_de_tarea(tarea):
    """Si el agente responde con una tarea: junta el texto de sus artifacts."""
    if tarea.status.state in ESTADOS_FALLIDOS:
        raise ErrorRemoto(f"el agente {ESTADOS_FALLIDOS[tarea.status.state]}")
    textos = [get_artifact_text(a) for a in tarea.artifacts]
    texto = "\n".join(t for t in textos if t).strip()
    if not texto and tarea.status.HasField("message"):
        texto = get_message_text(tarea.status.message).strip()
    if not texto:
        estado = TaskState.Name(tarea.status.state).replace("TASK_STATE_", "").lower()
        raise ErrorRemoto(f"el agente dejó la tarea en estado {estado} y sin texto (no se espera a tareas largas)")
    return texto


async def preguntar(cliente, texto, context_id):
    """Manda `texto` como mensaje de usuario con ese context_id y devuelve el texto de la respuesta."""
    mensaje = new_text_message(texto, context_id=context_id, role=Role.ROLE_USER)
    respuesta = None
    try:
        async with asyncio.timeout(TIMEOUT_MENSAJE):
            async for evento in cliente.send_message(SendMessageRequest(message=mensaje)):
                if evento.HasField("message"):
                    respuesta = get_message_text(evento.message).strip()
                elif evento.HasField("task"):
                    respuesta = _texto_de_tarea(evento.task)
    except ErrorRemoto:
        raise
    except Exception as error:
        raise ErrorRemoto(_explicar(error)) from None
    if not respuesta:
        raise ErrorRemoto("el agente respondió sin texto")
    return respuesta


async def cerrar_clientes():
    """Cierra las conexiones abiertas (para scripts y pruebas)."""
    guardados = list(CLIENTES.values())
    CLIENTES.clear()
    FICHAS.clear()
    for ciclo, cliente in guardados:
        if ciclo is asyncio.get_running_loop():
            try:
                await cliente.close()
            except Exception:
                pass
