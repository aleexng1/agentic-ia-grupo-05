"""Herramienta de validación: revisa un gasto con reglas exactas de la política.

Dueño: rol Herramientas y estado.
"""

from langchain_core.tools import tool

from src.contrato import Gasto, Validacion


@tool
def validar_gasto(gasto: Gasto, politica: str, categoria: str) -> Validacion:
    """Revisa un gasto con las reglas exactas de la política de gastos.

    Usa esta herramienta DESPUÉS de decidir la política y la categoría correctas.
    Revisa: tipo de documento permitido, plazo de rendición, campos obligatorios
    (por ejemplo la patente en vehículos) y si la política es exclusiva de una
    unidad de negocio. Devuelve si cumple, la lista de reglas incumplidas y la
    cuenta contable que corresponde.

    Args:
        gasto: el gasto rendido, con todos sus campos.
        politica: nombre de la política que corresponde al gasto.
        categoria: nombre de la categoría dentro de esa política.
    """
    # TODO(herramientas): reemplazar stub por las reglas leídas de datos/politica_ficticia.md
    return {"cumple": True, "incumplimientos": [], "cuenta": "CTA-5100"}
