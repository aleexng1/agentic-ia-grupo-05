"""El "ejecutor": el puente entre el servidor A2A y la función responder del agente."""

import inspect
import uuid

from a2a.helpers import new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue


def _una_linea(texto):
    """Deja un texto en una sola línea (sin saltos ni espacios repetidos)."""
    return " ".join(str(texto).split())


class Executor(AgentExecutor):
    """Recibe el mensaje del usuario, llama a responder y encola la respuesta."""

    def __init__(self, responder):
        # responder(texto, context_id) -> texto. Puede ser normal o async.
        self.responder = responder

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        texto = context.get_user_input()
        # Si el cliente no manda identificador de conversación, se inventa uno.
        context_id = context.context_id or str(uuid.uuid4())
        try:
            respuesta = self.responder(texto, context_id)
            if inspect.isawaitable(respuesta):
                respuesta = await respuesta
        except Exception as error:
            # Un error del agente no debe romper el servidor: se avisa en una línea.
            respuesta = _una_linea(f"Error: el agente falló ({type(error).__name__}: {error})")
        await event_queue.enqueue_event(
            new_text_message(str(respuesta), context_id=context_id)
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        context_id = context.context_id or str(uuid.uuid4())
        await event_queue.enqueue_event(
            new_text_message("Cancelar no está soportado.", context_id=context_id)
        )
