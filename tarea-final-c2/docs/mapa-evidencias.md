# Mapa de evidencias (estado al 2026-11-26, tras #115 y la traza del ReAct)

Revisión de Alex sobre los archivos que hay de verdad en `evidencias/` (`main` `20a9aa5`).
Puntos según [pauta.md](pauta.md). La pauta pide que **cada prueba muestre tres cosas**:

- la **entrada**;
- la **ejecución observada**, con su `id_ejecucion` (traza, log o registro);
- el **resultado**.

Columnas E / O / R / id: ✅ está · ⚠️ a medias · ❌ falta.

Estados:
- **lista:** la evidencia cubre lo que pide la pauta.
- **parcial:** hay evidencia, pero le falta algo.
- **pendiente:** no hay evidencia.

## Base (obligatoria: los extras solo cuentan con la base completa)

| Criterio | Puntos | Archivo(s) de evidencia | E | O | R | id | Estado | Qué falta | Dueño |
|---|---|---|---|---|---|---|---|---|---|
| Router + worker (dos recorridos) | parte del 1,0 | `dos-recorridos/01-consulta-politica.md`, `02-fuera-de-alcance.md`, `03-revisar-gasto.md` | ✅ | ✅ | ✅ | ✅ | **lista** | 01 y 03 recapturados el 2026-11-26 con Redis y Postgres: `consulta_politica` responde RG-03 con su fuente; `revisar_gasto` da APROBAR P02 / Peaje (03 recapturado otra vez con la traza paso a paso del ReAct). Los dos con `id_ejecucion` y `GET /registro/{id}` | Alex |
| ReAct con parada explícita | parte del 1,0 | `react/README.md` (#115: las cuatro paradas) · veredicto válido por `/chat` en `dos-recorridos/03-revisar-gasto.md` · `react/02-parada-max-pasos-gs01.txt` (`MAX_PASOS_REACT=2`) + `test_se_detiene_por_max_pasos_con_estado_error` | ✅ | ✅ | ✅ | ✅ | **lista** | 03 muestra, con su `id_ejecucion`, cada paso (herramienta y argumentos, resultado, decisión siguiente), la parada por veredicto válido en el paso 4 y el cierre (juez, fondo, registro), más una sección «Condición de parada» con las dos paradas. El tope de pasos va por terminal y prueba automática | Matías (03: Alex) |
| Delegación A2A | 0,5 | `a2a/05-uso-del-resultado-en-el-veredicto.md` (por `/chat`, con `id_ejecucion`: cómo cambia el veredicto) · `a2a/boleta-01…04-*.md` (encargo, respuesta y logs de los dos lados) · `a2a/seguridad-token-a2a.md` (canal con `TOKEN_A2A`) | ✅ | ✅ | ✅ | ✅ | **lista** (local) | Misma solicitud con la boleta 01 → **aprobar** y con la 05 (solo el monto distinto) → **observar** por el piso por verificación de `nodo_cerrar`, en `/chat` y en el registro. Si alcanza, repetirla contra Heroku | Alex |
| Seguridad (a) sin clave → 401 | parte del 0,5 | `seguridad/01-chat-sin-clave-401-local.txt` · `seguridad/01b-chat-sin-clave-401-heroku.txt` (#112, con extracto de `heroku logs`) | ✅ | ✅ | ✅ | — (un 401 no crea ejecución) | **lista** (local y Heroku) | — | Matías |
| Seguridad (b) acción no autorizada bloqueada sin ejecutarse | parte del 0,5 | `seguridad/02-bloqueo-accion-no-autorizada.md` (#109; modelo guionado, bloqueo real de `exigir_accion_permitida`, Postgres real) | ✅ | ✅ | ✅ | ✅ | **lista** (local) | Cumple los 5 controles: `bloqueado` en `/chat` y en `ejecuciones`, 0 llamadas a `registrar_veredicto`, registro igual antes y después | Matías |
| Resiliencia | 0,5 | `a2a/fallo-forzado-boleta-02-*.md` (`FORZAR_FALLO_A2A=1`) · `a2a/fallo-verificador-apagado-boleta-02-*.md` (`sin_conexion`) · `evidencias/fallo-controlado/` **vacía** | ✅ | ⚠️ | ✅ | ❌ | **parcial** | La pauta pide `estado_final = "fallback"` **en el registro**. Falta la falla provocada por `/chat` con `GET /registro/{id}`, y la caída del modelo principal (respaldo). Ver también el problema de los 30 s en `medicion-tiempos.md` | Sebastián (Alex aporta las capturas A2A) |
| Despliegue con registro | 0,5 | `evidencias/despliegue/` **vacía** | ❌ | ❌ | ❌ | ❌ | **pendiente** | URL pública, `/health`, `/chat` y `GET /registro/{id}`, más el extracto de `heroku logs`. **Riesgo:** hoy `revisar_gasto` tarda 31–52 s y Heroku corta a los 30 s | Sebastián |

## Ampliaciones declaradas (+3,0 como tope)

| Ampliación | Puntos | Archivo(s) de evidencia | E | O | R | id | Estado | Qué falta | Dueño |
|---|---|---|---|---|---|---|---|---|---|
| RAG documental | 0,5 | `ampliacion-rag/capturar_consultas.py` (#111, script listo) · `dos-recorridos/01-consulta-politica.md` (muestra el RAG con fuente) | ⚠️ | ⚠️ | ⚠️ | ⚠️ | **parcial** | Redis ya responde en local. Falta correr `capturar_consultas.py` y dejar la evidencia propia en `ampliacion-rag/` con su `id_ejecucion` | Eduardo |
| Evaluación con golden set | 0,5 | `ampliacion-evaluacion/informe-20261126T193234.md` / `.json` (corrida final) | ✅ | ✅ | ✅ | ✅ (por turno) | **lista** | **57/57 casos (100 %)**, router 59/59, 0 fallos, con todo unido, Redis y verificador; armada en 3 corridas con `gemini-3.5-flash-lite` (respaldo `gemini-3.5-flash`). `MAX_PASOS_REACT=6` no cortó ningún caso | Alex |
| Memoria persistente | 0,5 | `evidencias/ampliacion-memoria/` **vacía** | ❌ | ❌ | ❌ | ❌ | **pendiente** | El mismo `thread_id` recuerda la conversación después de reiniciar (checkpointer en Postgres; el código ya está en `main`) | Sebastián |
| MCP | 0,5 | `ampliacion-mcp/01-servidor-y-herramientas.txt` (servidor y lista de herramientas) · `react/01-veredicto-gs01.txt` (`consultar_fondo` desde el ReAct) · `dos-recorridos/03-revisar-gasto.md` (`consultar_fondo` por `/chat`) | ✅ | ✅ | ✅ | ✅ | **lista** | Cubre lo que pide la pauta; el `id_ejecucion` sale de la captura por `/chat` | Matías |
| GraphRAG | 1,0 | `ampliacion-graphrag/README.md` · `ampliacion-rag/capturar_consultas.py` (caso GraphRAG) | ❌ | ❌ | ❌ | ❌ | **pendiente** | Neo4j responde (24 nodos, con `NEO4J_DATABASE`, #111). Falta aprobar el catálogo (respuesta de Alex) y capturar la consulta de tope por cargo por `/chat` | Eduardo |
| **De respaldo:** n8n A2A | 1,0 | `evidencias/ampliacion-n8n/` **vacía**; `n8n/` solo tiene su README | ❌ | ❌ | ❌ | ❌ | **pendiente** | Elegir el caso adicional (que no rehaga la delegación al verificador), exportar el flujo sin credenciales y capturarlo | Alex |

## Suma de puntos

Se cuenta como **demostrado** solo lo que está *lista*; lo *parcial* cuenta como «depende de algo
pendiente» si lo que falta está en manos del grupo, y como «en riesgo» si depende de un acceso
externo que todavía no existe o de algo que no se empezó.

| Grupo | Criterios | Puntos |
|---|---|---|
| **Demostrado** | Router + ReAct (1,0) + seguridad (a) y (b) (0,5) + A2A (0,5) + MCP (0,5) + evaluación (0,5) | **≈ 3,0** (2,0 de base + 1,0 de ampliación) |
| **Depende de algo pendiente** (trabajo conocido, en manos del grupo) | Resiliencia (0,5) · despliegue (0,5: la app responde en Heroku) · RAG (0,5: Redis responde) · GraphRAG (1,0: Neo4j responde, falta el catálogo) | **≈ 2,5** |
| **En riesgo** (no está empezado) | Memoria (0,5) · n8n de respaldo (1,0) | **≈ 1,5** (de ellos, 1,0 es el respaldo) |

Lectura:
- **Base (3,0 en criterios):** router + ReAct, seguridad (local y Heroku) y A2A están completas.
  Resiliencia y despliegue esperan sus capturas.
- **Redis y Neo4j ya responden en local** (valores de desarrollo del grupo, solo lectura), así que
  RAG, GraphRAG y la evaluación dejaron de depender de un acceso externo.
- **Prioridad** (los extras solo cuentan con la base completa):
  1. despliegue y resiliencia por `/chat` con `GET /registro/{id}` (Sebastián);
  2. las evidencias de RAG y GraphRAG, con el catálogo aprobado (Eduardo);
  3. n8n como respaldo, si sobra tiempo (Alex).
- **Ampliaciones:** de los 3,0 declarados, MCP y evaluación (1,0) están demostrados; RAG y GraphRAG
  (1,5) ya tienen los accesos que necesitan (GraphRAG además necesita una pregunta que de verdad conecte datos). n8n (1,0) queda como respaldo.

## Cómo se revisó

Se listaron los archivos de cada carpeta de `evidencias/` y se buscó en cada uno la entrada,
la ejecución observada (log o traza), el resultado y el `id_ejecucion`. Las carpetas que solo
tienen `.gitkeep` cuentan como vacías.
