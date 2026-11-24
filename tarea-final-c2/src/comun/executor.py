"""Puente entre las solicitudes A2A y la lógica de un agente.

Dos formas:
- responder(texto, context_id) -> str: mensajes de texto (agentes de los talleres).
- responder_partes(partes, context_id) -> dict: recibe TODAS las partes del mensaje (archivo,
  datos y texto) y su resultado se devuelve como DataPart (JSON). Lo usa el verificador.
"""

from collections.abc import Callable
from inspect import isawaitable
from uuid import uuid4

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import Message, Part, Role
from a2a.utils.errors import UnsupportedOperationError
from google.protobuf import struct_pb2

from src.comun.errores import traducir_error


class Executor(AgentExecutor):
    """Ejecuta la función responder y publica su resultado en A2A."""

    def __init__(self, responder: Callable | None, responder_partes: Callable | None = None):
        if responder is None and responder_partes is None:
            raise ValueError("Executor necesita responder o responder_partes.")
        self.responder = responder
        self.responder_partes = responder_partes

    async def _resultado(self, context: RequestContext, context_id: str) -> list[Part]:
        if self.responder_partes is not None:
            partes = list(context.message.parts) if context.message else []
            resultado = self.responder_partes(partes, context_id)
            if isawaitable(resultado):
                resultado = await resultado
            valor = struct_pb2.Value()
            valor.struct_value.update(resultado)
            return [Part(data=valor, media_type="application/json")]
        respuesta = self.responder(context.get_user_input(), context_id)
        if isawaitable(respuesta):
            respuesta = await respuesta
        return [Part(text=str(respuesta))]

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        context_id = context.context_id or str(uuid4())

        try:
            partes = await self._resultado(context, context_id)
        except Exception as error:
            # Un error no se presenta como respuesta: se informa como error A2A, con un
            # mensaje de una línea, sin traza ni claves.
            raise RuntimeError(traducir_error(error)) from None

        mensaje = Message(
            message_id=str(uuid4()),
            context_id=context_id,
            role=Role.ROLE_AGENT,
            parts=partes,
        )
        await event_queue.enqueue_event(mensaje)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Indica al protocolo que este agente no admite cancelaciones."""
        raise UnsupportedOperationError("La cancelación no está soportada.")
