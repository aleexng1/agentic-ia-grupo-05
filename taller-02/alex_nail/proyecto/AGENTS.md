# Reglas del proyecto

- Los agentes van en `src/{nombre_agente}/` con `graph.py`, `prompts.py` y `tools.py`. Este proyecto tiene además `src/rag/storage.py` con una función `get_vector_store(prefijo)` que devuelve Redis o FAISS según `VECTOR_STORE`.
- Se ejecutan desde la raíz: `python main.py {nombre_agente} "pregunta"`.
- Flag `--saltos`: imprime los nodos por los que pasó el grafo. Flag `--diagrama`: imprime el Mermaid del grafo sin ejecutarlo.
- Los scripts sueltos (demos, ingesta) van en `scripts/` y los índices FAISS en `data/`.
- El modelo de embeddings se lee SIEMPRE de `EMBEDDING_MODEL`, en un solo lugar.
- Todo el proyecto vive en `taller-02/alex_nail/proyecto/`; no se modifican archivos fuera de esa carpeta. Los secretos van solo en `.env` (que git ignora) y nunca se imprimen.
- La evidencia para la entrega (salidas de scripts y tablas) se guarda en `../pruebas/` y `../pruebas/capturas/`; es la única carpeta fuera de `proyecto/` donde se puede escribir.
