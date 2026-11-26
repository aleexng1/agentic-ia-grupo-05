# Mapa de evidencias (estado al 2026-11-26, tras #111, #112 y las capturas con Redis)

Revisión de Alex sobre los archivos que hay de verdad en `evidencias/` (`main` `6659c4f`).
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
| Router + worker (dos recorridos) | parte del 1,0 | `dos-recorridos/01-consulta-politica.md`, `02-fuera-de-alcance.md`, `03-revisar-gasto.md` | ✅ | ✅ | ✅ | ✅ | **lista** | 01 y 03 recapturados el 2026-11-26 con Redis y Postgres: `consulta_politica` responde RG-03 con su fuente; `revisar_gasto` da APROBAR P02 / Peaje. Los dos con `id_ejecucion` y `GET /registro/{id}` | Alex |
| ReAct con parada explícita | parte del 1,0 | `react/01-veredicto-gs01.txt` (veredicto), `react/02-parada-max-pasos-gs01.txt` (`MAX_PASOS_REACT=2`) | ✅ | ✅ | ✅ | ❌ | **parcial** | Corridas por CLI, sin `id_ejecucion`. Repetirlas por `/chat` con `GET /registro/{id}` (casilla del #100) | Matías |
| Delegación A2A | 0,5 | `a2a/05-uso-del-resultado-en-el-veredicto.md` (por `/chat`, con `id_ejecucion`: cómo cambia el veredicto) · `a2a/boleta-01…04-*.md` (encargo, respuesta y logs de los dos lados) · `a2a/seguridad-token-a2a.md` (canal con `TOKEN_A2A`) | ✅ | ✅ | ✅ | ✅ | **lista** (local) | Misma solicitud con la boleta 01 → **aprobar** y con la 05 (solo el monto distinto) → **observar** por el piso por verificación de `nodo_cerrar`, en `/chat` y en el registro. Si alcanza, repetirla contra Heroku | Alex |
| Seguridad (a) sin clave → 401 | parte del 0,5 | `seguridad/01-chat-sin-clave-401-local.txt` · `seguridad/01b-chat-sin-clave-401-heroku.txt` (#112, con extracto de `heroku logs`) | ✅ | ✅ | ✅ | — (un 401 no crea ejecución) | **lista** (local y Heroku) | — | Matías |
| Seguridad (b) acción no autorizada bloqueada sin ejecutarse | parte del 0,5 | `seguridad/02-bloqueo-accion-no-autorizada.md` (#109; modelo guionado, bloqueo real de `exigir_accion_permitida`, Postgres real) | ✅ | ✅ | ✅ | ✅ | **lista** (local) | Cumple los 5 controles: `bloqueado` en `/chat` y en `ejecuciones`, 0 llamadas a `registrar_veredicto`, registro igual antes y después | Matías |
| Resiliencia | 0,5 | `a2a/fallo-forzado-boleta-02-*.md` (`FORZAR_FALLO_A2A=1`) · `a2a/fallo-verificador-apagado-boleta-02-*.md` (`sin_conexion`) · `evidencias/fallo-controlado/` **vacía** | ✅ | ⚠️ | ✅ | ❌ | **parcial** | La pauta pide `estado_final = "fallback"` **en el registro**. Falta la falla provocada por `/chat` con `GET /registro/{id}`, y la caída del modelo principal (respaldo). Ver también el problema de los 30 s en `medicion-tiempos.md` | Sebastián (Alex aporta las capturas A2A) |
| Despliegue con registro | 0,5 | `evidencias/despliegue/` **vacía** | ❌ | ❌ | ❌ | ❌ | **pendiente** | URL pública, `/health`, `/chat` y `GET /registro/{id}`, más el extracto de `heroku logs`. **Riesgo:** hoy `revisar_gasto` tarda 31–52 s y Heroku corta a los 30 s | Sebastián |

## Ampliaciones declaradas (+3,0 como tope)

| Ampliación | Puntos | Archivo(s) de evidencia | E | O | R | id | Estado | Qué falta | Dueño |
|---|---|---|---|---|---|---|---|---|---|
| RAG documental | 0,5 | `ampliacion-rag/capturar_consultas.py` (#111, script listo) · `dos-recorridos/01-consulta-politica.md` (muestra el RAG con fuente) | ⚠️ | ⚠️ | ⚠️ | ⚠️ | **parcial** | Redis ya responde en local. Falta correr `capturar_consultas.py` y dejar la evidencia propia en `ampliacion-rag/` con su `id_ejecucion` | Eduardo |
| Evaluación con golden set | 0,5 | `ampliacion-evaluacion/informe-20261124T213858.md` (corrida vieja) · avance parcial de la corrida final (no se sube: `avance-parcial.json`) | ✅ | ✅ | ✅ | ✅ (por turno) | **parcial** | Corrida final con todo unido y Redis: **12 de 57 casos, 12 aciertos** (GS-01…GS-12) antes del tope de llamadas. Seguir con `python -m evaluacion.evaluar --retomar --url http://127.0.0.1:8000 --pausa 20` (principal y verificador levantados) | Alex |
| Memoria persistente | 0,5 | `evidencias/ampliacion-memoria/` **vacía** | ❌ | ❌ | ❌ | ❌ | **pendiente** | El mismo `thread_id` recuerda la conversación después de reiniciar (checkpointer en Postgres; el código ya está en `main`) | Sebastián |
| MCP | 0,5 | `ampliacion-mcp/01-servidor-y-herramientas.txt` (servidor y lista de herramientas) · `react/01-veredicto-gs01.txt` (`consultar_fondo` desde el ReAct) | ✅ | ✅ | ✅ | ❌ | **lista** (falta el id) | Cubre lo que pide la pauta. Conviene volver a capturar la revisión por `/chat` para que tenga `id_ejecucion` (sale junto con la del ReAct) | Matías |
| GraphRAG | 1,0 | `ampliacion-graphrag/README.md` · `ampliacion-rag/capturar_consultas.py` (caso GraphRAG) | ❌ | ❌ | ❌ | ❌ | **pendiente** | Neo4j responde (24 nodos, con `NEO4J_DATABASE`, #111). Falta aprobar el catálogo (respuesta de Alex) y capturar la consulta de tope por cargo por `/chat` | Eduardo |
| **De respaldo:** n8n A2A | 1,0 | `evidencias/ampliacion-n8n/` **vacía**; `n8n/` solo tiene su README | ❌ | ❌ | ❌ | ❌ | **pendiente** | Elegir el caso adicional (que no rehaga la delegación al verificador), exportar el flujo sin credenciales y capturarlo | Alex |

## Suma de puntos

Se cuenta como **demostrado** solo lo que está *lista*; lo *parcial* cuenta como «depende de algo
pendiente» si lo que falta está en manos del grupo, y como «en riesgo» si depende de un acceso
externo que todavía no existe o de algo que no se empezó.

| Grupo | Criterios | Puntos |
|---|---|---|
| **Demostrado** | MCP (0,5) + seguridad (a) y (b) (0,5) + A2A (0,5) | **≈ 1,5** (0,5 de ampliación + 1,0 de base) |
| **Depende de algo pendiente** (trabajo conocido, en manos del grupo) | Router + ReAct (1,0: el router ya está, falta el `id_ejecucion` del ReAct) · resiliencia (0,5) · despliegue (0,5: la app responde en Heroku) · evaluación (0,5: 12/57) · RAG (0,5: Redis responde) · GraphRAG (1,0: Neo4j responde, falta el catálogo) | **≈ 4,0** |
| **En riesgo** (no está empezado) | Memoria (0,5) · n8n de respaldo (1,0) | **≈ 1,5** (de ellos, 1,0 es el respaldo) |

Lectura:
- **Base (3,0 en criterios):** seguridad (local y Heroku) y A2A están completas. Router + ReAct espera
  el `id_ejecucion` del ReAct; resiliencia y despliegue esperan sus capturas.
- **Redis y Neo4j ya responden en local** (valores de desarrollo del grupo, solo lectura), así que
  RAG, GraphRAG y la evaluación dejaron de depender de un acceso externo.
- **Prioridad** (los extras solo cuentan con la base completa):
  1. despliegue y resiliencia por `/chat` con `GET /registro/{id}` (Sebastián);
  2. el `id_ejecucion` del ReAct (Matías);
  3. las evidencias de RAG y GraphRAG, con el catálogo aprobado (Eduardo);
  4. terminar la corrida del evaluador con `--retomar` (Alex).
- **Ampliaciones:** de los 3,0 declarados, MCP (0,5) está demostrado; RAG, GraphRAG y evaluación
  (2,0) ya tienen todo lo que necesitan. n8n (1,0) queda como respaldo.

## Cómo se revisó

Se listaron los archivos de cada carpeta de `evidencias/` y se buscó en cada uno la entrada,
la ejecución observada (log o traza), el resultado y el `id_ejecucion`. Las carpetas que solo
tienen `.gitkeep` cuentan como vacías.
