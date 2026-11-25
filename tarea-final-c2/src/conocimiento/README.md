# src/conocimiento/

- `rag/`: RAG documental sobre la política con Redis. `rag.py` (`buscar_politica`) y
  `cargar_indice.py` vienen de tarea-final-c1. Índice del grupo: `REDIS_PREFIJO=grupo05_v15`.
- `grafo/`: GraphRAG en Neo4j, Cargo → Nivel → Categoría → Tope. Ver [modelo, plan
  offline y procedimiento de validación](grafo/README.md).

- **Dueño:** Eduardo.
- **Falta:** confirmar la instancia de Redis del curso; acordar el catálogo ficticio y validar
  GraphRAG en Neo4j; integrar ambas búsquedas en `flujos/consulta_politica.py` en otra fase.
