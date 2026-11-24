"""Creación de tarjetas de capacidades para los agentes A2A."""

from collections.abc import Iterable

from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill


def crear_tarjeta(
    nombre: str,
    descripcion: str,
    url: str,
    skills: Iterable[tuple[str, str, str, str]],
    modos_entrada: list[str] | None = None,
    modos_salida: list[str] | None = None,
) -> AgentCard:
    """Construye la ficha del agente con capacidades y ejemplos.

    modos_entrada / modos_salida: tipos MIME que acepta y entrega (por defecto, solo texto).
    """
    entrada = modos_entrada or ["text/plain"]
    salida = modos_salida or ["text/plain"]
    habilidades = [
        AgentSkill(
            id=identificador,
            name=nombre_habilidad,
            description=descripcion_habilidad,
            tags=[identificador],
            examples=[ejemplo],
            input_modes=entrada,
            output_modes=salida,
        )
        for identificador, nombre_habilidad, descripcion_habilidad, ejemplo in skills
    ]

    return AgentCard(
        name=nombre,
        description=descripcion,
        supported_interfaces=[
            AgentInterface(
                url=url,
                protocol_binding="JSONRPC",
                protocol_version="1.0",
            )
        ],
        version="1.0.0",
        capabilities=AgentCapabilities(streaming=False),
        default_input_modes=entrada,
        default_output_modes=salida,
        skills=habilidades,
    )
