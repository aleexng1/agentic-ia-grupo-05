# Mapa de evidencias (estado al 2026-11-25, actualizado tras #108 y #109)

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
| Router + worker (dos recorridos) | parte del 1,0 | `dos-recorridos/01-consulta-politica.md`, `02-fuera-de-alcance.md`, `03-revisar-gasto.md` | ✅ | ✅ | ✅ | ✅ | **parcial** | El 03 (`revisar_gasto`) está completo, con `GET /registro/{id}`. El 01 muestra la ruta en el log y en el registro, pero el flujo responde **502 por falta de Redis**: hay que volver a capturarlo con `REDIS_URL` real | Alex (captura) · Eduardo (Redis) |
| ReAct con parada explícita | parte del 1,0 | `react/01-veredicto-gs01.txt` (veredicto), `react/02-parada-max-pasos-gs01.txt` (`MAX_PASOS_REACT=2`) | ✅ | ✅ | ✅ | ❌ | **parcial** | Corridas por CLI, sin `id_ejecucion`. Repetirlas por `/chat` con `GET /registro/{id}` (casilla del #100) | Matías |
| Delegación A2A | 0,5 | `a2a/boleta-01…04-*.md` (encargo, respuesta y logs de los dos lados) · `a2a/seguridad-token-a2a.md` (canal con `TOKEN_A2A`, ficha pública) · `a2a/capturar_uso.py` (script de «cómo cambia el veredicto», listo) | ✅ | ✅ | ✅ | ❌ | **parcial** | Falta **cómo cambia el veredicto**: `capturar_uso.py` manda por `/chat` la misma solicitud con la boleta 01 («aprobar») y la 02 («observar» por el piso de `nodo_cerrar`), con `id_ejecucion` y la fila del registro. La corrida de prueba sin Redis dio «observar» en las dos **por el juez** (sin fragmentos de política no valida ninguna aprobación): se captura cuando haya Redis | Alex (captura) · Eduardo (Redis) |
| Seguridad (a) sin clave → 401 | parte del 0,5 | `seguridad/01-chat-sin-clave-401-local.txt` | ✅ | ✅ | ✅ | — (un 401 no crea ejecución) | **lista** (local) | Si alcanza, repetirla contra Heroku | Matías |
| Seguridad (b) acción no autorizada bloqueada sin ejecutarse | parte del 0,5 | `seguridad/02-bloqueo-accion-no-autorizada.md` (#109; modelo guionado, bloqueo real de `exigir_accion_permitida`, Postgres real) | ✅ | ✅ | ✅ | ✅ | **lista** (local) | Cumple los 5 controles: `bloqueado` en `/chat` y en `ejecuciones`, 0 llamadas a `registrar_veredicto`, registro igual antes y después | Matías |
| Resiliencia | 0,5 | `a2a/fallo-forzado-boleta-02-*.md` (`FORZAR_FALLO_A2A=1`) · `a2a/fallo-verificador-apagado-boleta-02-*.md` (`sin_conexion`) · `evidencias/fallo-controlado/` **vacía** | ✅ | ⚠️ | ✅ | ❌ | **parcial** | La pauta pide `estado_final = "fallback"` **en el registro**. Falta la falla provocada por `/chat` con `GET /registro/{id}`, y la caída del modelo principal (respaldo). Ver también el problema de los 30 s en `medicion-tiempos.md` | Sebastián (Alex aporta las capturas A2A) |
| Despliegue con registro | 0,5 | `evidencias/despliegue/` **vacía** | ❌ | ❌ | ❌ | ❌ | **pendiente** | URL pública, `/health`, `/chat` y `GET /registro/{id}`, más el extracto de `heroku logs`. **Riesgo:** hoy `revisar_gasto` tarda 31–52 s y Heroku corta a los 30 s | Sebastián |

## Ampliaciones declaradas (+3,0 como tope)

| Ampliación | Puntos | Archivo(s) de evidencia | E | O | R | id | Estado | Qué falta | Dueño |
|---|---|---|---|---|---|---|---|---|---|
| RAG documental | 0,5 | `evidencias/ampliacion-rag/` **vacía** | ❌ | ❌ | ❌ | ❌ | **pendiente** | Acceso a Redis (`REDIS_URL`, `EMBEDDING_MODEL`) y una consulta por `/chat` que cite la fuente. Sin Redis, `consulta_politica` da 502 | Eduardo |
| Evaluación con golden set | 0,5 | `ampliacion-evaluacion/informe-20261124T213858.md` / `.json` | ✅ | ✅ | ✅ | ✅ (por turno) | **parcial** | Esa corrida es de antes de unir los flujos: 17/17 evaluables y 40 pendientes. Falta la corrida completa con todo unido, idealmente con Redis (`--pausa 20`; se corta y retoma sola por cuota) | Alex |
| Memoria persistente | 0,5 | `evidencias/ampliacion-memoria/` **vacía** | ❌ | ❌ | ❌ | ❌ | **pendiente** | El mismo `thread_id` recuerda la conversación después de reiniciar (checkpointer en Postgres; el código ya está en `main`) | Sebastián |
| MCP | 0,5 | `ampliacion-mcp/01-servidor-y-herramientas.txt` (servidor y lista de herramientas) · `react/01-veredicto-gs01.txt` (`consultar_fondo` desde el ReAct) | ✅ | ✅ | ✅ | ❌ | **lista** (falta el id) | Cubre lo que pide la pauta. Conviene volver a capturar la revisión por `/chat` para que tenga `id_ejecucion` (sale junto con la del ReAct) | Matías |
| GraphRAG | 1,0 | `evidencias/ampliacion-graphrag/` **vacía** | ❌ | ❌ | ❌ | ❌ | **pendiente** | Cargar Neo4j con el catálogo y capturar una consulta de tope por cargo (cargo → nivel → categoría → tope) por `/chat` | Eduardo |
| **De respaldo:** n8n A2A | 1,0 | `evidencias/ampliacion-n8n/` **vacía**; `n8n/` solo tiene su README | ❌ | ❌ | ❌ | ❌ | **pendiente** | Elegir el caso adicional (que no rehaga la delegación al verificador), exportar el flujo sin credenciales y capturarlo | Alex |

## Suma de puntos

Se cuenta como **demostrado** solo lo que está *lista*; lo *parcial* cuenta como «depende de algo
pendiente» si lo que falta está en manos del grupo, y como «en riesgo» si depende de un acceso
externo que todavía no existe o de algo que no se empezó.

| Grupo | Criterios | Puntos |
|---|---|---|
| **Demostrado** | MCP (0,5) + seguridad (a) y (b) (0,5, en local) | **≈ 1,0** (0,5 de ampliación + 0,5 de base) |
| **Depende de algo pendiente** (trabajo conocido, en manos del grupo) | Router + ReAct (1,0) · A2A (0,5, espera Redis) · resiliencia (0,5) · evaluación (0,5) | **≈ 2,5** |
| **En riesgo** (falta un acceso externo, no está empezado o choca con el límite de 30 s) | Despliegue (0,5) · RAG (0,5, sin Redis) · GraphRAG (1,0, sin Neo4j) · memoria (0,5, sin empezar) · n8n de respaldo (1,0, sin empezar) | **≈ 3,5** (de ellos, 1,0 es el respaldo) |

Lectura:
- **Base (3,0 en criterios):** seguridad (a) y (b) está completa en local (falta repetirla en Heroku si
  alcanza). Los otros 4 criterios todavía no.
- **El riesgo principal es el despliegue,** porque además es requisito de entrega y choca con el
  límite de 30 s.
- **Como los extras solo cuentan con la base completa,** la prioridad es:
  1. despliegue y resiliencia (Sebastián);
  2. el `id_ejecucion` del ReAct (Matías);
  3. Redis para el recorrido 01, el RAG y la captura A2A de «cómo cambia el veredicto» (Eduardo);
  4. la captura A2A por `/chat` y la corrida final del evaluador (Alex).
- **Ampliaciones:** de los 3,0 declarados, solo MCP (0,5) está demostrado. RAG y GraphRAG (1,5)
  dependen de Redis y Neo4j. Si alguno no llega, n8n (1,0) es el respaldo.

## Cómo se revisó

Se listaron los archivos de cada carpeta de `evidencias/` y se buscó en cada uno la entrada,
la ejecución observada (log o traza), el resultado y el `id_ejecucion`. Las carpetas que solo
tienen `.gitkeep` cuentan como vacías.
