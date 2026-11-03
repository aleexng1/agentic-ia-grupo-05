"""La "ficha" (Agent Card) de un agente: quién es, qué hace y dónde vive."""

from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from a2a.utils.constants import PROTOCOL_VERSION_CURRENT, TransportProtocol

VERSION = "1.0.0"
MODO_TEXTO = "text/plain"


def crear_tarjeta(nombre, descripcion, url, skills):
    """Arma la ficha del agente.

    skills es una lista de tuplas (id, nombre, descripcion, ejemplo).
    En la versión 1.3.0 de a2a-sdk la dirección no es un campo suelto: va
    dentro de supported_interfaces, junto con el protocolo que se habla.
    """
    habilidades = [
        AgentSkill(
            id=id_skill,
            name=nombre_skill,
            description=descripcion_skill,
            tags=[id_skill],
            examples=[ejemplo],
        )
        for id_skill, nombre_skill, descripcion_skill, ejemplo in skills
    ]
    return AgentCard(
        name=nombre,
        description=descripcion,
        version=VERSION,
        supported_interfaces=[
            AgentInterface(
                url=url,
                protocol_binding=TransportProtocol.JSONRPC,
                protocol_version=PROTOCOL_VERSION_CURRENT,
            )
        ],
        capabilities=AgentCapabilities(streaming=False),
        default_input_modes=[MODO_TEXTO],
        default_output_modes=[MODO_TEXTO],
        skills=habilidades,
    )
