# Reglas del proyecto (taller-03)

- Los agentes van en `src/{nombre_agente}/` con `graph.py`, `prompts.py` y `tools.py`. Cada nodo tiene su propio prompt en `prompts.py`; no se escriben reglas dentro de `graph.py`.
- Se ejecutan desde la raíz de `taller-03/`: `python main.py {nombre_agente} "mensaje"`.
  - `--saltos`: imprime los nodos por los que pasó el grafo y, si hubo llamadas a herramientas, el nombre de cada tool con sus argumentos y un resumen del resultado.
  - `--diagrama`: imprime el Mermaid del grafo sin ejecutarlo.
- Las herramientas MCP se cargan desde la URL de `.env` en `tools.py` con `langchain-mcp-adapters` (`MultiServerMCPClient`, transporte `streamable_http`). Nunca se escriben a mano herramientas que el MCP ya ofrece.
- Los scripts sueltos van en `scripts/` y las pruebas en `tests/` (pytest). Las pruebas de promptfoo van en `promptfoo/`.
- Todo se ejecuta con el Python de `taller-03/.venv`.
