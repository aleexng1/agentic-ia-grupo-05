# Reparto: quién es dueño de qué

Cada persona trabaja **solo en su rama** y abre un PR hacia `main`. Si necesitas cambiar un
archivo de otra persona, avísale y acuérdenlo antes.

| Persona | Rama | Es dueña de |
|---|---|---|
| Alex | `c2tf/alex-integracion` | Caso y README · router (`src/principal/router.py`, `grafo.py`, `flujos/fuera_de_alcance.py`) · verificador A2A (`src/verificador/`, `herramientas/delegar_verificador.py`, `src/comun/cliente_a2a.py`, `src/comun/executor.py`) · golden set y evaluación (`evaluacion/`) · `evidencias/` · `n8n/` |
| Matías Muñoz | `c2tf/matias-react-seguridad` | Flujo `revisar_gasto` (`src/principal/flujos/revisar_gasto.py`: ReAct + condición de parada `MAX_PASOS_REACT`) · juez (`src/principal/juez.py`) · seguridad (`src/comun/seguridad.py`: acciones permitidas, bloqueo y `TOKEN_A2A`) · MCP de fondos (`src/mcp_fondos/`, `herramientas/consultar_fondo.py` y `herramientas/fondos.py`), porque `consultar_fondo` se usa dentro del ReAct |
| Eduardo Basaure | `c2tf/eduardo-conocimiento` | RAG (`src/conocimiento/rag/`) · GraphRAG (`src/conocimiento/grafo/` y `datos/cargos_niveles.json`) · flujo `consulta_politica` · chat web (`web/`) |
| Sebastián Mardones | `c2tf/sebastian-despliegue` | Heroku (`Procfile`, dos apps) · Postgres · tabla `ejecuciones` (`src/comun/registro.py`) · `registro_veredictos` a Postgres · resiliencia (`src/comun/modelos.py`: modelo de respaldo, timeouts) · memoria persistente (checkpointer en Postgres) |

## Qué demuestras para la nota

Criterios y puntos según [pauta.md](pauta.md). Cada evidencia muestra la **entrada**, la
**ejecución observada** (traza, log o registro con su `id_ejecucion`) y el **resultado**.

### Matías: ReAct, seguridad y MCP

| Criterio | Puntos | Evidencia | Carpeta |
|---|---|---|---|
| ReAct con parada explícita | parte del 1,0 (lo comparte con el router de Alex) | Un gasto que termina con un veredicto válido y otro que se detiene por `MAX_PASOS_REACT` (por ejemplo con `MAX_PASOS_REACT=2`). Se ve la traza de pasos (pensar → herramienta → observación) y cuántos fueron. | `evidencias/react/` |
| Seguridad | 0,5 | (a) `/chat` sin clave → 401. (b) Una acción no autorizada (por ejemplo `modificar_registro`, o una glosa con jailbreak como GS-27 de c1) se bloquea **sin ejecutarse**: `estado_final = "bloqueado"` y el registro queda igual antes y después. | `evidencias/seguridad/` |
| MCP | 0,5 | El servidor MCP levantado con su lista de herramientas, y `consultar_fondo` llamado **desde el ReAct** en una revisión real. | `evidencias/ampliacion-mcp/` |

- **Depende de:** `contratos.md` §3 (herramientas), §4 (tipos), §6 (seguridad) y §8 (parada);
  `buscar_politica` de Eduardo; `delegar_verificador` de Alex.
- **Entrega:** a **Alex**, el nodo `revisar_gasto`, que devuelve `pasos`, `herramientas_usadas`,
  `estado_final` y el `veredicto`. A **Sebastián**, el `estado_final` "bloqueado" para la tabla `ejecuciones`.

### Eduardo: RAG, GraphRAG y chat web

| Criterio | Puntos | Evidencia | Carpeta |
|---|---|---|---|
| RAG documental | 0,5 | Una pregunta sobre la política → los fragmentos recuperados con su fuente → la respuesta que los cita. | `evidencias/ampliacion-rag/` |
| GraphRAG | 1,0 | La carga del grafo (cantidad de nodos y relaciones), la consulta del camino Cargo → Nivel → Categoría → Tope y una pregunta en el chat que **solo** se responde bien con el grafo (tope según el cargo). Así se distingue del RAG. | `evidencias/ampliacion-graphrag/` |
| Chat web | sin puntos propios (lo necesita el despliegue) | El chat desplegado mandando `POST /chat` con clave y mostrando `ruta`, `estado_final` e `id_ejecucion`. | `evidencias/despliegue/` (junto con Sebastián) |

- **Depende de:** `contratos.md` §2 (formato de `/chat`, que usa el chat web), §3 (`buscar_politica`,
  `tope_para`) y §4 (`Gasto.cargo`); Redis y Neo4j configurados (variables en `.env.example`).
- **Entrega:** a **Alex**, `responder_consulta` para la ruta `consulta_politica`. A **Matías**,
  `buscar_politica` funcionando. A **Sebastián**, `web/index.html` listo para desplegar.

### Sebastián: despliegue, resiliencia y memoria

| Criterio | Puntos | Evidencia | Carpeta |
|---|---|---|---|
| Despliegue con registro | 0,5 | La URL pública, `/health`, una llamada a `/chat` y `GET /registro/{id_ejecucion}` mostrando la `ruta` que corrió y su `estado_final`, más el extracto de `heroku logs` (sin claves). | `evidencias/despliegue/` |
| Resiliencia | 0,5 | Una falla provocada (`FORZAR_FALLO_A2A=1`, timeout o caída del modelo principal) → fallback o mensaje claro, **sin datos inventados**, con un número limitado de reintentos y `estado_final = "fallback"` en el registro. | `evidencias/fallo-controlado/` |
| Memoria persistente | 0,5 | El mismo `thread_id` recuerda la conversación **después de reiniciar** el servicio (checkpointer en Postgres). No basta con el registro de ejecuciones: el mismo trabajo no se acredita dos veces. | `evidencias/ampliacion-memoria/` |

- **Depende de:** `contratos.md` §2 (`/registro`), §7 (tabla `ejecuciones`) y §9 (persistencia y despliegue);
  el fallback de `delegar_verificador` de Alex (para la falla de A2A); `web/` de Eduardo.
- **Entrega:** a **todos**, la URL desplegada y la tabla `ejecuciones`, donde se buscan los `id_ejecucion`
  de las evidencias. A **Alex**, `guardar_ejecucion` y `obtener_llm_con_respaldo` para usarlos en `responder`.

### Alex: router, A2A, evaluación, n8n e integración

| Criterio | Puntos | Evidencia | Carpeta |
|---|---|---|---|
| Router + worker | parte del 1,0 (lo comparte con el ReAct de Matías) | Dos recorridos por rutas distintas (`consulta_politica` y `revisar_gasto`), con la `ruta` visible en la respuesta y en el registro. | `evidencias/dos-recorridos/` |
| Delegación A2A | 0,5 | La ficha del verificador, el encargo (imagen + datos declarados), su respuesta (`leido`, `cuadra`, `confianza`) y cómo cambia el veredicto. | `evidencias/a2a/` |
| Evaluación con golden set | 0,5 | El golden set versionado y una corrida con su % de aciertos, separada por ruta. | `evidencias/ampliacion-evaluacion/` |
| n8n A2A (respaldo) | 1,0 | Un **caso adicional** con n8n que **no** rehace la delegación al verificador de la base. | `evidencias/ampliacion-n8n/` |
| README e integración | sin puntos propios (es requisito de entrega) | El README con la ficha mínima completa, todos los PR unidos y los tests pasando en main. | — |

- **Depende de:** todos. `revisar_gasto` de Matías, `responder_consulta` de Eduardo y el registro y los modelos de Sebastián.
- **Entrega:** a **Matías**, `delegar_verificador` y el router que lo llama. A **todos**, el
  README y el orden de unión de los PR.

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
