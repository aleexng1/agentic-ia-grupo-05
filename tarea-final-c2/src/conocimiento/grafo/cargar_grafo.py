"""Carga el grafo de la política en Neo4j: Cargo → Nivel → Categoría → Tope.

Dueño: Eduardo (c2tf/eduardo-conocimiento). Datos: datos/cargos_niveles.json (falta crearlo,
todo ficticio). Conexión: NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD.
"""


def cargar_grafo(ruta_datos: str) -> dict:
    """Crea (con MERGE, para poder repetirla) los nodos y relaciones del grafo.

    (:Cargo)-[:TIENE_NIVEL]->(:Nivel)-[:PUEDE_RENDIR]->(:Categoria)-[:TIENE_TOPE]->(:Tope).
    Las categorías y topes deben coincidir con datos/politica_ficticia.md.
    Devuelve {"nodos": int, "relaciones": int}.
    """
    raise NotImplementedError("cargar_grafo: pendiente (Eduardo, c2tf/eduardo-conocimiento).")
