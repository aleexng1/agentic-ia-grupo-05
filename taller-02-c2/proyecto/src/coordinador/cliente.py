"""Cliente A2A para descubrir y consultar agentes remotos."""

import asyncio
import ssl
from uuid import uuid4

import httpx

from a2a.client import (
    A2ACardResolver,
    Client,
    ClientCallContext,
    ClientConfig,
    create_client,
)
from a2a.types import (
    GetTaskRequest,
    Message,
    Part,
    Role,
    SendMessageRequest,
    AgentCard,
    Task,
    TaskState,
)


TIEMPO_LIMITE = 10.0
TIEMPO_MAXIMO_TAREA = 60.0
_CLIENTES = {}
_TARJETAS_CLIENTES: dict[int, AgentCard] = {}
_CLIENTE_HTTP: httpx.AsyncClient | None = None
_CANDADO = asyncio.Lock()


async def obtener_cliente(url: str, usar_esta_direccion: bool = False):
    """Descarga la tarjeta A2A una vez y reutiliza el cliente por URL.

    Con usar_esta_direccion=True el JSON-RPC se envía a la misma dirección por la que
    se descargó la ficha, aunque la ficha publique otra (la pública de URL_BASE).
    Solo cambia la copia local del coordinador; la ficha publicada queda igual.
    """
    global _CLIENTE_HTTP

    direccion = url.strip().rstrip("/")
    if direccion in _CLIENTES:
        return _CLIENTES[direccion]

    async with _CANDADO:
        if direccion in _CLIENTES:
            return _CLIENTES[direccion]

        if _CLIENTE_HTTP is None or _CLIENTE_HTTP.is_closed:
            # Se usan los certificados del sistema operativo (no solo los de certifi):
            # un antivirus que revisa el HTTPS (por ejemplo Avast) firma con su propio
            # certificado, que solo está en el almacén del sistema.
            _CLIENTE_HTTP = httpx.AsyncClient(
                timeout=TIEMPO_LIMITE,
                verify=ssl.create_default_context(),
            )

        resolver = A2ACardResolver(
            httpx_client=_CLIENTE_HTTP,
            base_url=direccion,
        )
        tarjeta = await resolver.get_agent_card(
            http_kwargs={"timeout": TIEMPO_LIMITE}
        )
        if usar_esta_direccion:
            for interfaz in tarjeta.supported_interfaces:
                interfaz.url = direccion
        configuracion = ClientConfig(
            streaming=False,
            polling=True,
            httpx_client=_CLIENTE_HTTP,
            supported_protocol_bindings=["JSONRPC"],
            accepted_output_modes=["text/plain"],
        )
        cliente = await create_client(
            agent=tarjeta,
            client_config=configuracion,
        )
        _CLIENTES[direccion] = cliente
        _TARJETAS_CLIENTES[id(cliente)] = tarjeta
        return cliente


def tarjeta_del_cliente(cliente: Client) -> AgentCard:
    """Devuelve la tarjeta ya descargada para un cliente almacenado en caché."""
    tarjeta = _TARJETAS_CLIENTES.get(id(cliente))
    if tarjeta is None:
        raise ValueError("No se encontró la tarjeta asociada al cliente A2A.")
    return tarjeta


def _texto_partes(partes) -> str:
    """Junta las partes de texto de un mensaje o artefacto A2A."""
    return "\n".join(
        parte.text
        for parte in partes
        if parte.WhichOneof("content") == "text" and parte.text
    )


def _texto_tarea(tarea: Task) -> str:
    """Extrae texto de los artefactos de una tarea completada."""
    textos = [
        _texto_partes(artefacto.parts)
        for artefacto in tarea.artifacts
    ]
    respuesta = "\n".join(texto for texto in textos if texto)
    if respuesta:
        return respuesta

    # Algunos agentes mantienen la respuesta final en el historial de la tarea.
    for mensaje in reversed(tarea.history):
        if mensaje.role == Role.ROLE_AGENT:
            respuesta = _texto_partes(mensaje.parts)
            if respuesta:
                return respuesta
    return ""


async def _esperar_tarea(cliente, tarea: Task) -> Task:
    """Consulta una tarea hasta completar, fallar o superar el tiempo límite."""
    reloj = asyncio.get_running_loop()
    limite = reloj.time() + TIEMPO_MAXIMO_TAREA
    estados_fallidos = {
        TaskState.TASK_STATE_FAILED,
        TaskState.TASK_STATE_CANCELED,
        TaskState.TASK_STATE_REJECTED,
        TaskState.TASK_STATE_INPUT_REQUIRED,
        TaskState.TASK_STATE_AUTH_REQUIRED,
    }

    while tarea.status.state != TaskState.TASK_STATE_COMPLETED:
        if tarea.status.state in estados_fallidos:
            estado = TaskState.Name(tarea.status.state)
            raise RuntimeError(f"El agente remoto terminó con estado {estado}.")
        if reloj.time() >= limite:
            raise TimeoutError(
                f"La tarea A2A no terminó en {TIEMPO_MAXIMO_TAREA:g} segundos."
            )

        await asyncio.sleep(0.5)
        tarea = await cliente.get_task(
            GetTaskRequest(id=tarea.id),
            context=ClientCallContext(timeout=TIEMPO_LIMITE),
        )
    return tarea


async def preguntar(cliente, texto: str, context_id: str) -> str:
    """Envía un mensaje de usuario y devuelve texto de mensaje o tarea A2A."""
    identificador = context_id or str(uuid4())
    mensaje = Message(
        message_id=str(uuid4()),
        context_id=identificador,
        role=Role.ROLE_USER,
        parts=[Part(text=texto)],
    )
    solicitud = SendMessageRequest(message=mensaje)
    contexto_llamada = ClientCallContext(timeout=TIEMPO_LIMITE)
    respuesta = None

    async for evento in cliente.send_message(
        solicitud,
        context=contexto_llamada,
    ):
        respuesta = evento

    if respuesta is None:
        raise RuntimeError("El agente A2A no devolvió ninguna respuesta.")

    tipo_respuesta = respuesta.WhichOneof("payload")
    if tipo_respuesta == "message":
        return _texto_partes(respuesta.message.parts)
    if tipo_respuesta == "task":
        tarea = await _esperar_tarea(cliente, respuesta.task)
        texto_tarea = _texto_tarea(tarea)
        if texto_tarea:
            return texto_tarea
        raise RuntimeError("La tarea A2A terminó sin texto en sus artefactos.")

    raise RuntimeError("El agente A2A devolvió una respuesta no reconocida.")


async def cerrar_clientes() -> None:
    """Cierra los clientes y la conexión HTTP compartida al apagar el proceso."""
    global _CLIENTE_HTTP
    async with _CANDADO:
        for cliente in _CLIENTES.values():
            await cliente.close()
        _CLIENTES.clear()
        _TARJETAS_CLIENTES.clear()
        if _CLIENTE_HTTP is not None and not _CLIENTE_HTTP.is_closed:
            await _CLIENTE_HTTP.aclose()
        _CLIENTE_HTTP = None
