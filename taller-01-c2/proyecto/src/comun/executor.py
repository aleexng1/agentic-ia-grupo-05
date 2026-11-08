"""Puente entre las solicitudes A2A y la lógica de un agente."""

from collections.abc import Callable
from inspect import isawaitable
from uuid import uuid4

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import Message, Part, Role
from a2a.utils.errors import UnsupportedOperationError


class Executor(AgentExecutor):
    """Ejecuta la función responder y publica su resultado en A2A."""

    def __init__(self, responder: Callable):
        self.responder = responder

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        texto = context.get_user_input()
        context_id = context.context_id or str(uuid4())

        try:
            respuesta = self.responder(texto, context_id)
            if isawaitable(respuesta):
                respuesta = await respuesta
            texto_respuesta = str(respuesta)
        except Exception as error:
            detalle = str(error).replace("\r", " ").replace("\n", " ").strip()
            if not detalle:
                detalle = error.__class__.__name__
            texto_respuesta = f"No pude procesar el mensaje: {detalle}"

        mensaje = Message(
            message_id=str(uuid4()),
            context_id=context_id,
            role=Role.ROLE_AGENT,
            parts=[Part(text=texto_respuesta)],
        )
        await event_queue.enqueue_event(mensaje)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Indica al protocolo que este agente no admite cancelaciones."""
        raise UnsupportedOperationError("La cancelación no está soportada.")
