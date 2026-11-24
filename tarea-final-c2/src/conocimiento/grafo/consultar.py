"""Consultas GraphRAG sobre Neo4j. Dueño: Eduardo (c2tf/eduardo-conocimiento)."""


def tope_para(cargo: str, categoria: str) -> dict | None:
    """Devuelve el tope que aplica a ese cargo en esa categoría, o None si no hay camino.

    {"cargo", "nivel", "categoria", "tope_clp", "fuente"}. Si el cargo no existe en el
    grafo devuelve None (el flujo lo informa); no supone un nivel por defecto.
    """
    raise NotImplementedError("tope_para: pendiente (Eduardo, c2tf/eduardo-conocimiento).")
