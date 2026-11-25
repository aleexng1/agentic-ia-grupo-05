# Medición de tiempos de `/chat` y presupuesto para Heroku (30 s)

Medición: Alex, 2026-11-25, sobre `main` (`6659c4f`). **No se cambió código**: se midió desde
afuera, con la hora (en ms) de cada línea del log y de las trazas (`MOSTRAR_TRAZAS=1`), y con
la hora de envío y de respuesta de cada `POST /chat`.

## Cómo se midió

- **Entorno:** local (un PC, red doméstica).
  - `MODELO_PRINCIPAL=gemini-3.5-flash-lite` y `MODELO_RESPALDO=gemini-3.5-flash`.
  - Postgres temporal en Docker (puerto 5434) como `DATABASE_URL`.
  - Verificador en el puerto 8001, con `TIMEOUT_A2A_SEG=20`.
- **Casos:** `V-01` a `V-04` del golden set, cada uno con su boleta de `datos/boletas/`, más
  `R-01` (`consulta_politica`) y `X-01` (`fuera_de_alcance`). Hubo 5 s de pausa entre solicitudes.
- **Se hicieron 4 revisiones, no 5:** cada `revisar_gasto` usó entre 7 y 12 llamadas a Gemini
  (router 1 + verificador 1 + ReAct 5 a 10 + juez 0 o 1). Las 4 sumaron 39 llamadas y ya superaban
  el tope de ~30, así que no se hizo la quinta. En total fueron 41 llamadas.
- **Límites de lo medido:**
  - **No había acceso a Redis** (`REDIS_URL` de ejemplo): `buscar_politica` falló al instante en
    cada llamada. Con el RAG real hay que sumar el embedding y la consulta a Redis por búsqueda,
    y la cantidad de pasos del ReAct puede cambiar.
  - Por eso `consulta_politica` terminó en 502 después del router.
  - Los reintentos internos del SDK de Gemini se anotan en un nivel de log que la app no muestra,
    así que no se puede saber, sin tocar código, si algún paso lento incluyó un reintento silencioso.
  - **Todo es local:** en Heroku hay que medir de nuevo (Sebastián).

## Resultados

### Total por solicitud (desde que se envía hasta que llega la respuesta)

| Caso | Ruta | Total | Router | A2A (verificador) | ReAct (pasos) | Juez | Registro y cierre | Resultado |
|---|---|---|---|---|---|---|---|---|
| V-01 | revisar_gasto | **38,4 s** | 8,8 s | 7,4 s | 20,1 s (6) | 1,8 s | 0,1 s | ok · observar |
| V-02 | revisar_gasto | **52,5 s** | 6,0 s | 10,8 s | 27,1 s (5) | 8,5 s | 0,1 s | ok · observar |
| V-03 | revisar_gasto | **38,3 s** | 4,0 s | 3,6 s | 27,3 s (7) | 3,2 s | 0,1 s | ok · observar |
| V-04 | revisar_gasto | **31,2 s** | 1,7 s | 2,6 s | 26,7 s (10, `MAX_PASOS_REACT`) | — | — | error · sin veredicto |
| R-01 | consulta_politica | 5,2 s | 4,9 s | — | — | — | — | 502 (sin Redis) |
| X-01 | fuera_de_alcance | 11,9 s | 11,8 s | — | — | — | — | ok |

Las 6 ejecuciones quedaron en la tabla `ejecuciones`, y su `duracion_ms` coincide con el total
medido desde afuera (±0,1 s).

### Por etapa (las 4 revisiones)

| Etapa | Mín | Mediana | Promedio | Máx | Comentario |
|---|---|---|---|---|---|
| Total `revisar_gasto` | 31,2 s | 38,3 s | 40,1 s | 52,5 s | **Las 4 superan los 30 s de Heroku, sin ninguna falla** |
| Router (6 solicitudes) | 1,7 s | 5,4 s | 6,2 s | 11,8 s | Una sola llamada; varía mucho (incluso para un poema) |
| A2A completo | 2,6 s | 5,5 s | 6,1 s | 10,8 s | Casi todo es Gemini leyendo la imagen (2,5–10,7 s); la red A2A suma <0,1 s |
| Un paso LLM del ReAct (28 pasos) | 0,8 s | 1,9 s | 3,3 s | 13,0 s | Lo que más pesa: entre 18 y 27 s por revisión |
| `consultar_fondo` (MCP, 4 llamadas) | 1,6 s | 1,8 s | 1,8 s | 2,0 s | Arranca un proceso MCP por llamada |
| Otras herramientas | 0,0 s | 0,0 s | 0,0 s | 0,0 s | Sin Redis, `buscar_politica` falla al instante |
| Juez (3 casos) | 1,8 s | 3,2 s | 4,5 s | 8,5 s | Corre siempre, también cuando la decisión ya es «observar» (V-03), aunque solo cambia algo si es «aprobar» |
| Registro (Postgres) y cierre | 0,1 s | 0,1 s | 0,1 s | 0,1 s | Despreciable |

**Conclusión:** sin fallas, `revisar_gasto` tarda hoy **31–52 s**. El 60–85 % se va en el ReAct
(5 a 10 llamadas seguidas a Gemini). Reducir reintentos ayuda solo cuando algo falla; para entrar
en 30 s hay que bajar las llamadas en serie.

## Configuración actual de reintentos y tiempos límite (leída del código)

| Pieza | Dónde | Reintentos | Tiempo límite por llamada | Respaldo |
|---|---|---|---|---|
| Router | `src/principal/router.py` (Alex) → `obtener_llm()` | 6 intentos (por defecto de `langchain-google-genai`) | **ninguno** (`timeout=None`) | Sí: `MODELO_RESPALDO`, 1 vez |
| ReAct | `src/principal/flujos/revisar_gasto.py` (Matías) | 6 intentos por paso | ninguno | Sí: en cada paso se prueba primero el principal |
| Juez | `src/principal/juez.py` (Matías) | `max_retries = 6`, explícito | ninguno | Sí |
| Verificador (lectura de la imagen) | `src/verificador/agente.py` (Alex) → `obtener_llm()` | 6 intentos | ninguno | No |
| A2A | `delegar_verificador` (Alex) | 0 | `TIMEOUT_A2A_SEG` = 20 s | Si vence: «observar» + `fallback` |
| `consultar_fondo` (MCP) | `herramientas/consultar_fondo.py` (Matías) | 0 | 20 s | No |
| `obtener_llm` / `obtener_llm_con_respaldo` | `src/comun/modelos.py` (Sebastián) | por defecto (6) | ninguno | — |

El SDK `google-genai` (2.34) reintenta 408, 429, 500, 502, 503 y 504. Espera 1, 2, 4, 8 y 16 s
entre intentos, más hasta 1 s de azar en cada espera. Con 6 intentos son **31–36 s de espera,
más el tiempo de las respuestas**, antes de que el error suba y entre el respaldo.

## Peor caso teórico con el modelo principal sin cuota (429)

Supuesto: el respaldo sí responde, en ~2–3 s por llamada.

| Etapa | Cálculo | Tiempo |
|---|---|---|
| Router | 6 intentos del principal (~33–38 s) + respaldo | ~36–41 s |
| A2A | El verificador no tiene respaldo; sus 6 intentos superan `TIMEOUT_A2A_SEG` | 20 s → `fallback` |
| ReAct | Cada paso vuelve a probar el principal (~35 s) + respaldo; 5–7 pasos | ~185–290 s |
| Juez | 6 intentos (~35 s) + respaldo | ~38 s |
| **Total** | | **~280–390 s (5–6 min)** |

Si **los dos** modelos están sin cuota, el router gasta ~70 s y la solicitud termina en 502.
Además, **ninguna llamada tiene tiempo límite**: una conexión que se cuelga (pasó una vez durante
estas pruebas, en una llamada de diagnóstico) puede retener `/chat` indefinidamente. Heroku corta a los 30 s (H12):
el usuario ve un error, mientras el servidor sigue trabajando y registra la ejecución después.

## Presupuesto propuesto (objetivo: ≤ 25 s, con 5 s de margen bajo los 30 s)

| Etapa | Hoy (mediana / máx) | Presupuesto | Cómo llegar | Dueño |
|---|---|---|---|---|
| Router | 5,4 / 11,8 s | ≤ 3 s, con tope de 6 s | Principal con **1 intento** y tiempo límite de **5 s** por llamada, luego el respaldo con lo mismo | Alex (`router.py`) + Sebastián (parámetros en `obtener_llm`) |
| A2A | 5,5 / 10,8 s | **0 s en serie** (en paralelo con el ReAct), con tope de 12 s | Empezar el A2A al entrar a `revisar_gasto` y esperar su resultado recién en `nodo_cerrar`, donde se aplica el piso. Si no se paraleliza: `TIMEOUT_A2A_SEG=12` (con 8 s, 1 de las 4 boletas medidas habría caído en `fallback`) | Alex (`grafo.py`) + Matías (que `revisar_caso` acepte la verificación como «futuro» o callable) |
| Lectura de la imagen (verificador) | 5,4 / 10,7 s | ≤ 10 s | Tiempo límite de 10 s y 1–2 intentos en `leer_imagen` | Alex |
| ReAct | 25 / 27 s, en 5–10 pasos | ≤ 12 s, en ≤ 5 pasos | Pedir en un solo paso las herramientas independientes (política, fondo y validación). No repetir `buscar_politica` cuando falla. `MAX_PASOS_REACT=6` para `/chat`. Una vez que el principal falló en un turno, seguir con el respaldo («cortocircuito») en vez de pagar la falla en cada paso. 1 intento y 8 s de tiempo límite por llamada | Matías |
| `consultar_fondo` (MCP) | 1,8 s | ≤ 1 s | Reusar la sesión MCP dentro del turno, en vez de un proceso nuevo por llamada | Matías |
| Juez | 3,2 / 8,5 s | ≤ 3 s, y **0 s** si no hay «aprobar» | El juez solo puede bajar una aprobación: no llamarlo cuando la decisión ya es observar o rechazar. `max_retries` 1–2 cuando hay respaldo | Matías |
| Registro y cierre | 0,1 s | 0,1 s | — | — |
| **Total** | 38 / 52 s | **~16–22 s típico, ≤ 25 s tope** | | |

Reglas para todo `/chat`:

- **Reintentos:** a lo más **1 reintento por llamada a Gemini cuando no hay respaldo, y ninguno
  cuando lo hay** (el respaldo *es* el reintento). Sin las esperas de 4, 8 y 16 s del SDK.
  Propuesta: que `obtener_llm()` acepte `intentos` y `tiempo_limite`, y que se configuren por
  variable (`LLM_INTENTOS=1`, `LLM_TIMEOUT_SEG=8`).
- **`TIMEOUT_A2A_SEG`:** 12 s si el A2A corre en paralelo con el ReAct. Si sigue en serie, hay
  que elegir entre más `fallback` (8 s) o pasarse de 30 s.
- **Tope global:** que `/chat` corte a los **25 s** con una respuesta clara (`estado_final =
  "error"` o `"fallback"` y su `id_ejecucion`), en vez de dejar que Heroku corte con un H12. Dueño:
  Alex (`api/app.py` y `grafo.py`), coordinado con Sebastián.
- **Si aun así no alcanza:** cambiar `/chat` a asíncrono. Respondería `202` con el `id_ejecucion`, y
  la web consultaría `GET /registro/{id}` hasta tener el resultado. Es un cambio más grande
  (Sebastián, Eduardo en `web/` y Alex) y conviene decidirlo en grupo después de medir en Heroku.

**Margen:** con el presupuesto típico (~16–22 s) quedan 8–14 s bajo los 30 s. Con el tope de 25 s
quedan 5 s para la red de Heroku y el arranque en frío del dyno.

## Cómo repetir la medición

1. Levantar el Postgres temporal y el verificador como en el README.
2. Levantar el principal con `MOSTRAR_TRAZAS=1 PYTHONUNBUFFERED=1`, ponerle la hora a cada línea de
   su salida y mandar `POST /chat` con los casos `V-0x` del golden set.
3. Comparar la hora de cada evento: `router ·`, `a2a · encargo` / `respuesta`, las trazas `[llm]`,
   `[observacion]` y `[juez]`, y la línea final `ejecución … ms`.

Los scripts de esta medición no se subieron, porque son de un solo uso. Esta medición no dejó
claves, imágenes ni logs crudos en el repositorio.
