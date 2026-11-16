"""Modelo FALSO para probar el grafo sin llamar al modelo real ni a la base."""

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field

from src.router.graph import Decision


def llamada(nombre: str, args: dict, id: str = "c1") -> AIMessage:
    """Un mensaje del modelo que pide usar una herramienta."""
    return AIMessage(content="", tool_calls=[{"name": nombre, "args": args, "id": id, "type": "tool_call"}])


class Clasificador:
    """Lo que devuelve with_structured_output(Decision): decide la ruta según una lista de rutas."""

    def __init__(self, rutas: list, vistos: list):
        self.rutas = rutas
        self.vistos = vistos

    def invoke(self, mensajes):
        self.vistos.append(list(mensajes))
        return Decision(ruta=self.rutas.pop(0), motivo="motivo de prueba")


class LLMFalso(BaseChatModel):
    """Hace de clasificador del router, de conversador de la ruta genérica y de modelo del agente."""

    rutas: list = Field(default_factory=list)  # una ruta por cada vez que corre el router
    guion: list = Field(default_factory=list)  # respuestas en orden (texto o AIMessage); si se acaba, `respuesta`
    respuesta: str = "respuesta del modelo"
    falla: bool = False
    recibidos: list = Field(default_factory=list)  # entradas del conversador / agente
    clasificaciones: list = Field(default_factory=list)  # entradas del router

    @property
    def _llm_type(self) -> str:
        return "falso"

    def bind_tools(self, tools, **kwargs):
        return self

    def with_structured_output(self, schema, **kwargs):
        return Clasificador(self.rutas, self.clasificaciones)

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        self.recibidos.append(list(messages))
        if self.falla:
            raise RuntimeError("detalle interno con clave-secreta")
        item = self.guion.pop(0) if self.guion else self.respuesta
        mensaje = item if isinstance(item, AIMessage) else AIMessage(item)
        return ChatResult(generations=[ChatGeneration(message=mensaje)])
