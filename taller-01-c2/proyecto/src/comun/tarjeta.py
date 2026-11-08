"""Creación de tarjetas de capacidades para los agentes A2A."""

import os
from collections.abc import Iterable

from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from dotenv import load_dotenv


def crear_tarjeta(
    nombre: str,
    descripcion: str,
    url: str,
    skills: Iterable[tuple[str, str, str, str]],
) -> AgentCard:
    """Construye la ficha del agente con capacidades y ejemplos de texto."""
    load_dotenv()
    direccion_publica = os.getenv("URL_PUBLICA", "").strip()
    habilidades = [
        AgentSkill(
            id=identificador,
            name=nombre_habilidad,
            description=descripcion_habilidad,
            tags=[identificador],
            examples=[ejemplo],
            input_modes=["text/plain"],
            output_modes=["text/plain"],
        )
        for identificador, nombre_habilidad, descripcion_habilidad, ejemplo in skills
    ]

    return AgentCard(
        name=nombre,
        description=descripcion,
        supported_interfaces=[
            AgentInterface(
                url=direccion_publica or url,
                protocol_binding="JSONRPC",
                protocol_version="1.0",
            )
        ],
        version="1.0.0",
        capabilities=AgentCapabilities(streaming=False),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        skills=habilidades,
    )
