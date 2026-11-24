# Reparto: quién es dueño de qué

Cada persona trabaja **solo en su rama** y abre un PR hacia `main`. Si necesitas cambiar un
archivo de otra persona, avísale y acuérdenlo antes.

| Persona | Rama | Es dueña de |
|---|---|---|
| Alex | `c2tf/alex-integracion` | Caso y README · router (`src/principal/router.py`, `grafo.py`, `flujos/fuera_de_alcance.py`) · verificador A2A (`src/verificador/`, `herramientas/delegar_verificador.py`, `src/comun/cliente_a2a.py`, `src/comun/executor.py`) · golden set y evaluación (`evaluacion/`) · `evidencias/` · `n8n/` |
| Matías Muñoz | `c2tf/matias-react-seguridad` | Flujo `revisar_gasto` (`src/principal/flujos/revisar_gasto.py`: ReAct + condición de parada `MAX_PASOS_REACT`) · juez (`src/principal/juez.py`) · seguridad (`src/comun/seguridad.py`: acciones permitidas, bloqueo y `TOKEN_A2A`) · MCP de fondos (`src/mcp_fondos/`, `herramientas/consultar_fondo.py` y `herramientas/fondos.py`), porque `consultar_fondo` se usa dentro del ReAct |
| Eduardo Basaure | `c2tf/eduardo-conocimiento` | RAG (`src/conocimiento/rag/`) · GraphRAG (`src/conocimiento/grafo/` y `datos/cargos_niveles.json`) · flujo `consulta_politica` · chat web (`web/`) |
| Sebastián Mardones | `c2tf/sebastian-despliegue` | Heroku (`Procfile`, dos apps) · Postgres · tabla `ejecuciones` (`src/comun/registro.py`) · `registro_veredictos` a Postgres · resiliencia (`src/comun/modelos.py`: modelo de respaldo, timeouts) · memoria persistente (checkpointer en Postgres) |

## Archivos compartidos (se cambian solo por acuerdo, en un PR propio o avisando)
`docs/contratos.md`, `src/comun/contrato.py`, `src/comun/config.py`, `requirements.txt`,
`.env.example`, `api/app.py`, `tests/test_humo.py`.

## Pendientes que cruzan áreas
- **Antes del despliegue (Sebastián):** `registro_veredictos` (hoy SQLite en
  `src/principal/registro_veredictos.py`) pasa a Postgres, porque en Heroku el disco se borra al
  reiniciar. Lo mismo para la tabla `ejecuciones` y la memoria por `thread_id`.
- **Despliegue (Sebastián):** opción preferida, buildpack de monorepo con `APP_BASE=tarea-final-c2`,
  en dos apps de Heroku con el mismo `Procfile`:
  `APP_MODULE=api.app:app` (principal) y `APP_MODULE=src.verificador.app:app` (verificador).
  Alternativa: `git subtree push --prefix tarea-final-c2 heroku main`.
  **No tocar** el `Procfile`, el `requirements.txt` ni el `.slugignore` de la raíz (son del taller 02).
- **Verificador (Alex + Matías):** hoy está protegido con X-API-Key de forma provisoria; pasa a
  `TOKEN_A2A` cuando exista `revisar_token_a2a`.
- **`tests/test_humo.py::test_chat_sin_router_responde_501`:** se borra o se cambia a 200 cuando el router exista (Alex).
