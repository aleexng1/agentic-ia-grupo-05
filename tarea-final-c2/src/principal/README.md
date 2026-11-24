# src/principal/

Agente principal (LangGraph): `grafo.py` arma router → flujos; `router.py` clasifica.

| Archivo | Origen | Dueño | Estado |
|---|---|---|---|
| `grafo.py`, `router.py`, `flujos/fuera_de_alcance.py` | nuevo | Alex | esqueleto |
| `flujos/revisar_gasto.py` | `tarea-final-c1/src/grafo.py` (solo imports) | Matías | ReAct de c1 funcionando; falta integrarlo como nodo |
| `flujos/consulta_politica.py` | nuevo | Eduardo | esqueleto |
| `juez.py` | `tarea-final-c1/src/seguridad.py` (prompt + juez) | Matías | copiado |
| `registro_veredictos.py` | `tarea-final-c1/src/registro.py` | Sebastián (a Postgres) | SQLite; **pasar a Postgres antes del despliegue** |
| `herramientas/validar_gasto.py` | `tarea-final-c1/src/herramientas.py` | Matías | copiado |
| `herramientas/fondos.py` | `tarea-final-c1/src/memoria.py` | Matías (MCP) | copiado |
| `herramientas/buscar_politica.py` | reexporta `src/conocimiento/rag/rag.py` | Eduardo | copiado |
| `herramientas/consultar_fondo.py` | nuevo (cliente MCP) | Matías | esqueleto |
| `herramientas/delegar_verificador.py` | nuevo (A2A) | Alex | esqueleto |
