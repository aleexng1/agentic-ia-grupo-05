"""Flujo consulta_politica: responde preguntas sobre la política de gastos.

Dueño: Eduardo (c2tf/eduardo-conocimiento). No usa ReAct: busca y responde.
"""


def responder_consulta(texto: str, thread_id: str) -> dict:
    """Responde una pregunta sobre la política citando la fuente.

    Usa buscar_politica (RAG en Redis, src/conocimiento/rag) y, si la pregunta es de topes
    por cargo, el GraphRAG (src/conocimiento/grafo/consultar.py). Devuelve
    {"respuesta": str, "fuentes": list[str], "herramientas_usadas": list[str]}.
    Si no encuentra respaldo en la política, lo dice; nunca inventa un tope ni una regla.
    """
    raise NotImplementedError("responder_consulta: pendiente (Eduardo, c2tf/eduardo-conocimiento).")
