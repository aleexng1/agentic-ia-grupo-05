"""Búsqueda en la política de gastos (RAG con el Redis del curso).

Dueño: rol Conocimiento y seguridad.
"""

from langchain_core.tools import tool

from src.contrato import Fragmento


@tool
def buscar_politica(consulta: str, k: int = 3) -> list[Fragmento]:
    """Busca en la política de gastos de la empresa los trozos más parecidos a la consulta.

    Úsala cuando necesites saber qué política, categoría o cuenta corresponde a
    un gasto, o qué dice una regla. NO la uses si la respuesta ya está en la
    conversación o si la pregunta no trata de gastos.

    Args:
        consulta: qué buscar, en palabras simples (por ejemplo "bencina auto de la empresa").
        k: cuántos trozos devolver (por defecto 3).
    """
    # TODO(conocimiento-seguridad): reemplazar stub por la búsqueda en Redis
    return [
        {
            "politica": "Vehículos Propios",
            "texto": "Combustible para vehículos de la empresa. Categoría Combustible, cuenta CTA-1001.",
            "fuente": "datos/politica_ficticia.md#vehiculos-propios",
            "puntaje": 0.9,
        }
    ]
