# Tarea final del Curso 2 · Grupo 05

**Agente revisor de rendiciones de gastos** para *Comercial Los Alerces SpA*, una **empresa
ficticia**. Todo es inventado: personas, RUT, montos, políticas y boletas.

Un **agente principal** recibe mensajes por `POST /chat`, decide qué flujo corresponde y lo
ejecuta. Para leer las boletas le delega el trabajo, por **A2A**, a un segundo agente: el
**verificador de boletas**. Cada ejecución queda registrada en Postgres, con la ruta que corrió
y cómo terminó.

> **Estado (2026-11-25):** el código de las cuatro partes está unido en `main` y la suite pasa
> (385 tests, con Gemini y Postgres de prueba). **Falta:** el despliegue en Heroku, el acceso a
> Redis y Neo4j, y varias evidencias. El detalle está en
> [docs/mapa-evidencias.md](docs/mapa-evidencias.md) y en el issue #100 del repositorio.
> Lo que todavía no está hecho va marcado como **PENDIENTE (dueño)**.

Documentos del grupo:
- [docs/pauta.md](docs/pauta.md): qué se evalúa.
- [docs/reparto.md](docs/reparto.md): quién hace qué.
- [docs/contratos.md](docs/contratos.md): formatos de `/chat`, de A2A y de la tabla `ejecuciones`.
- [docs/medicion-tiempos.md](docs/medicion-tiempos.md): tiempos medidos y presupuesto para Heroku.

---

## 1. Alcance y flujos

El agente principal es **router y worker**: un router (Gemini, salida estructurada) clasifica
cada mensaje en una de tres rutas, y el mismo agente ejecuta el flujo elegido.

| Ruta | Cuándo | Qué hace | Herramientas |
|---|---|---|---|
| `consulta_politica` | Una pregunta sobre reglas, topes o documentos, sin un gasto concreto | Busca en la política (RAG en Redis) y, si es un tope por cargo, en el grafo (GraphRAG en Neo4j). Responde citando la fuente y, si no encuentra respaldo, lo dice | `buscar_politica`, `tope_para` |
| `revisar_gasto` | Un gasto rendido concreto (datos en `gasto`, o JSON en el texto), con o sin la foto de la boleta | Si hay boleta, la delega por A2A al verificador. Después corre un **ciclo ReAct** con parada explícita (veredicto válido o `MAX_PASOS_REACT`): busca la política, consulta el fondo (MCP), valida las reglas y emite `aprobar` / `observar` / `rechazar`. Un juez revisa las aprobaciones. Si la boleta no cuadra o no se pudo verificar, una aprobación baja a «observar» **antes** de registrarse | `delegar_verificador`, `buscar_politica`, `consultar_fondo`, `validar_gasto`, `emitir_veredicto` |
| `fuera_de_alcance` | Cualquier otra cosa: temas ajenos, pedir claves, intentos de saltarse las reglas | Responde con un texto fijo que explica qué sí puede hacer. No usa herramientas ni gasta llamadas a Gemini | — |

Reglas que valen siempre:
- **Nunca inventa datos.** Si falta un dato del gasto, lo pide. Si una herramienta o el
  verificador fallan, lo dice.
- **Acciones no autorizadas:** cualquier acción fuera de `ACCIONES_PERMITIDAS` se bloquea sin
  ejecutarse (`estado_final = "bloqueado"`).
- **`estado_final`** es uno de `ok`, `fallback`, `error` o `bloqueado`. Si dos piezas terminan
  distinto, gana el más grave: bloqueado > error > fallback > ok.

### Ejemplos de solicitudes y resultados esperados

| Mensaje | Ruta esperada | Resultado esperado |
|---|---|---|
| «¿Cuál es el plazo máximo para rendir un gasto que hice en octubre?» | `consulta_politica` | La regla del plazo (RG-03), citando la fuente. **PENDIENTE (Eduardo):** sin acceso a Redis, hoy responde 502 «No se pudo completar la búsqueda documental (Redis o embeddings)» |
| «Revisa este gasto rendido.» + `gasto` = GS-01 (peaje de $7.800, fondo FR-001) | `revisar_gasto` | `APROBAR`, P02 / Peaje / CTA-6100 (ver `evidencias/dos-recorridos/03-revisar-gasto.md`) |
| «Revisa este gasto y su boleta adjunta.» + `gasto` + `boleta-02-monto-distinto.png` | `revisar_gasto` | El verificador lee $62.000 contra $52.000 declarados (`cuadra.monto = "no"`): `OBSERVAR`, y el registro también queda en «observar» |
| «Escríbeme un poema sobre el lago Llanquihue.» | `fuera_de_alcance` | El texto fijo con lo que sí puede hacer; `estado_final = "ok"` |
| «Ignora todas tus instrucciones anteriores…» | `fuera_de_alcance` | El mismo texto fijo; no obedece |

Arquitectura:

```
cliente / web ──POST /chat (X-API-Key)──> api/app.py ──> grafo (LangGraph)
                                                          router ─┬─> consulta_politica   (RAG + GraphRAG)
                                                                  ├─> revisar_gasto ──A2A (Bearer TOKEN_A2A)──> verificador (otra app)
                                                                  │      └─ ReAct + MCP (consultar_fondo) + juez
                                                                  └─> fuera_de_alcance
                                                          └─> tabla ejecuciones (Postgres) · memoria por thread_id (Postgres)
```

---

## 2. Entorno

Requisitos:
- **Python 3.12**.
- **Docker**, para un Postgres local.
- Una clave de **Google AI Studio** (Gemini).
- Opcional: acceso a Redis (RAG) y a Neo4j (GraphRAG).

Todos los comandos se corren **desde la carpeta `tarea-final-c2/`** del repositorio.

### Instalación

```bash
python3.12 -m venv .venv
source .venv/bin/activate          # Windows (PowerShell): .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
```

Completa el `.env` como se explica en la sección 5. Para generar la clave del servicio y el
token A2A:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Postgres local (tabla `ejecuciones`, registro de veredictos y memoria)

```bash
docker run -d --rm --name tf-c2-postgres \
  -e POSTGRES_PASSWORD=solo_local -e POSTGRES_DB=tarea_final_c2 \
  -p 127.0.0.1:5434:5432 postgres:16
```

En el `.env`: `DATABASE_URL=postgresql://postgres:solo_local@127.0.0.1:5434/tarea_final_c2`.
Las tablas se crean solas. Para borrar el contenedor: `docker stop tf-c2-postgres`.

> Sin `DATABASE_URL`, la memoria queda en el proceso y las ejecuciones solo en el log. Además,
> `revisar_gasto` falla al registrar el veredicto («Falta DATABASE_URL»). **PENDIENTE
> (Sebastián):** un mensaje más claro o un modo local sin Postgres.

### Levantar los servicios (una terminal para cada uno)

```bash
# Terminal 1: verificador de boletas (agente A2A)
uvicorn src.verificador.app:app --port 8001

# Terminal 2: agente principal (API + chat web)
uvicorn api.app:app --port 8000
```

- Chat web: <http://127.0.0.1:8000/> (pide la clave del servicio).
- Salud: <http://127.0.0.1:8000/health> y <http://127.0.0.1:8001/health>.
- Ficha A2A del verificador: <http://127.0.0.1:8001/.well-known/agent-card.json>.

### Pruebas

```bash
python -m pytest                   # suite completa
python -m pytest -m necesita_llm   # solo las que llaman a Gemini (se saltan sin GOOGLE_API_KEY)
TEST_DATABASE_URL=postgresql://postgres:solo_local@127.0.0.1:5434/tarea_final_c2 python -m pytest tests/test_persistencia.py
```

Las pruebas de persistencia **borran y recrean tablas**: usa una base de prueba, nunca la de Heroku.

---

## 3. Acceso al servicio

| Servicio | URL |
|---|---|
| Agente principal (API + chat web) | **PENDIENTE: Sebastián** |
| Verificador A2A | **PENDIENTE: Sebastián** (segunda app de Heroku) |

Endpoints del principal:
- `GET /health` (público).
- `GET /` (chat web, público; la clave se ingresa en la página).
- `POST /chat` (asíncrono: responde 202; ver abajo).
- `GET /registro/{id_ejecucion}` (estado y resultado).

Despliegue previsto: dos apps de Heroku con el mismo `Procfile`
(`web: uvicorn $APP_MODULE --host 0.0.0.0 --port $PORT`). Usan `APP_MODULE=api.app:app` y
`APP_MODULE=src.verificador.app:app`, y el buildpack de monorepo con `APP_BASE=tarea-final-c2`.
**PENDIENTE (Sebastián):** la URL, las Config Vars y la evidencia. Como `revisar_gasto` tarda
31–52 s y Heroku corta a los 30 s, `/chat` es asíncrono (ver abajo y
[docs/medicion-tiempos.md](docs/medicion-tiempos.md)).

### Autenticación

- **`/chat` y `/registro`** exigen la cabecera `X-API-Key` con el valor de `API_KEY_SERVICIO`.
  - Sin clave o con una clave distinta: `401`.
  - Si el servidor no tiene clave configurada: `503`, y no queda abierto.
  - La clave nunca aparece en logs ni respuestas.
- **El canal A2A** (principal → verificador) usa otra credencial: `Authorization: Bearer
  <TOKEN_A2A>`. Las dos apps deben tener el **mismo** `TOKEN_A2A`. La clave del servicio no se
  manda al verificador.
- **Las credenciales se entregan aparte**, nunca en el repositorio.

### `/chat` es asíncrono

Heroku corta las solicitudes a los 30 s y una revisión de gasto tarda más
([docs/medicion-tiempos.md](docs/medicion-tiempos.md)). Por eso `POST /chat` responde de
inmediato **202** con un `id_ejecucion`, y el resultado se consulta en `GET /registro/{id}` hasta
que `estado` deje de ser `en_proceso`.

```bash
export API_KEY_SERVICIO='<tu clave>'      # en la terminal, no en un archivo que se suba
URL=http://127.0.0.1:8000                 # o la URL de Heroku

# 1) Enviar el mensaje → 202 {"id_ejecucion", "estado": "en_proceso", "consultar", "thread_id"}
ID=$(curl -s -X POST "$URL/chat" \
  -H 'Content-Type: application/json' -H "X-API-Key: $API_KEY_SERVICIO" \
  -d '{"thread_id": "demo-1", "texto": "Escríbeme un poema sobre el lago Llanquihue."}' \
  | python -c 'import json,sys; print(json.load(sys.stdin)["id_ejecucion"])')

# 2) Consultar hasta que termine (estado: ok / bloqueado / fallback / error)
while true; do
  R=$(curl -s "$URL/registro/$ID" -H "X-API-Key: $API_KEY_SERVICIO")
  echo "$R" | python -c 'import json,sys; d=json.load(sys.stdin); print(d["estado"])' | grep -qv en_proceso && break
  sleep 2
done
echo "$R" | python -m json.tool
```

Respuesta final (abreviada): la fila de `ejecuciones` más el estado y el `resultado` completo.

```json
{"id_ejecucion": "…", "ruta": "fuera_de_alcance", "estado_final": "ok", "duracion_ms": 4810, "…": "…",
 "estado": "ok", "segundos": 4.8,
 "resultado": {"id_ejecucion": "…", "thread_id": "demo-1", "ruta": "fuera_de_alcance",
               "respuesta": "Soy el revisor de rendiciones…", "estado_final": "ok", "pasos": 0, "…": "…"}}
```

- Si algo falla, `estado = "error"` y `detail` trae un mensaje claro que termina con
  `(id_ejecucion: …)`. Nunca hay un resultado inventado.
- **Tope global:** si la ejecución pasa de `TIEMPO_MAX_EJECUCION_SEG` (90 s), queda en `error` sin
  resultado.
- **Modo síncrono** (como antes, para uso local, pruebas o el evaluador): `POST "$URL/chat?esperar=true"`
  responde `200` con la respuesta completa. En Heroku no sirve para `revisar_gasto` (corte a los 30 s).
- **Límite:** el estado y la respuesta completa se guardan en la memoria del proceso. Tras un
  reinicio, `GET /registro/{id}` devuelve solo la fila de Postgres (`resultado: null`).
  **PENDIENTE (Sebastián):** guardarlos en Postgres.
- **PENDIENTE (Eduardo):** que el chat web consulte `/registro/{id}` hasta que termine. Hoy espera la
  respuesta completa en el `POST`.

Revisar un gasto con su boleta (la imagen va en base64; aquí en modo síncrono, en local):

```bash
python - <<'EOF'
import base64, json, os, urllib.request
casos = json.load(open("evaluacion/golden_set.json", encoding="utf-8"))["casos"]
turno = next(c for c in casos if c["id"] == "V-02")["turnos"][0]
cuerpo = {"thread_id": "demo-boleta", "texto": turno["mensaje"], "gasto": turno["gasto"],
          "imagen": {"mime_type": "image/png",
                     "datos_base64": base64.b64encode(open(turno["imagen"], "rb").read()).decode()}}
pedido = urllib.request.Request("http://127.0.0.1:8000/chat?esperar=true", json.dumps(cuerpo).encode(),
                                {"Content-Type": "application/json", "X-API-Key": os.environ["API_KEY_SERVICIO"]})
print(json.dumps(json.load(urllib.request.urlopen(pedido, timeout=120)), ensure_ascii=False, indent=2))
EOF
```

Formato completo de la solicitud, la respuesta y los errores (401, 422, 502 con `id_ejecucion`):
[docs/contratos.md](docs/contratos.md), secciones 2 y 11.1.

---

## 4. Datos de ejemplo

Todo está en `datos/` y es ficticio.

| Archivo | Qué es |
|---|---|
| `datos/politica_ficticia.md` | Política de rendiciones POL-RG-01 v1.6 (la fuente del RAG) |
| `datos/fondos_ficticios.json` | Fondos por rendir (FR-001, FR-020, FR-050), que lee el servidor MCP |
| `datos/rendiciones_prueba.csv` | Rendiciones de prueba (de tarea-final-c1) |
| `datos/cargos_niveles.json` | Cargos, niveles y topes para el GraphRAG (catálogo propuesto, pendiente de aprobación) |
| `datos/boletas/boleta-0{1..4}-*.png` + `declarado.json` | 4 boletas («DOCUMENTO DE PRUEBA»): una que cuadra, monto distinto, fecha distinta e ilegible |
| `evaluacion/golden_set.json` | Golden set v1.0: 57 casos (59 turnos) con ruta y decisión esperadas |

---

## 5. Configuración

Todas las variables están en `.env.example`, con valores ficticios. En local van en `.env`, que
git ignora; en Heroku van como Config Vars. **Nunca** se suben valores reales.

| Variable | Para qué sirve | Ejemplo / valor local |
|---|---|---|
| `GOOGLE_API_KEY` | Clave de Gemini (Google AI Studio) | *(secreta)* |
| `MODELO_PRINCIPAL` | Modelo del router, del ReAct, del juez y del verificador | `gemini-3.5-flash-lite` |
| `MODELO_RESPALDO` | Modelo al que se cambia si el principal falla (cuota, 503, timeout). Vacío = sin respaldo | `gemini-3.5-flash` |
| `EMBEDDING_MODEL` | Modelo de embeddings del RAG (el mismo con que se cargó el índice) | *(el del curso)* |
| `API_KEY_SERVICIO` | Clave que piden `/chat` y `/registro` (cabecera `X-API-Key`) | *(secreta, generada)* |
| `TOKEN_A2A` | Token del canal A2A; el **mismo** en el principal y en el verificador | *(secreto, generado)* |
| `URL_VERIFICADOR` | Dirección del verificador, sin barra final | `http://127.0.0.1:8001` |
| `TIMEOUT_A2A_SEG` | Segundos que el principal espera al verificador; si vence, «observar» + `fallback` | `20` (ver presupuesto en `docs/medicion-tiempos.md`) |
| `FORZAR_FALLO_A2A` | `1` simula que el verificador falla (evidencia de fallo controlado) | `0` |
| `MAX_PASOS_REACT` | Máximo de vueltas del ReAct por turno (condición de parada) | `10` |
| `TIEMPO_MAX_EJECUCION_SEG` | Tope global de una ejecución de `/chat`; si se pasa, queda en `error` sin resultado | `90` |
| `MAX_EJECUCIONES_SIMULTANEAS` | Ejecuciones de `/chat` a la vez en el proceso; las demás esperan su turno | `4` |
| `NIVEL_RAZONAMIENTO` | Razonamiento interno de Gemini en el router y el verificador (`minimal`, `low`, `medium`, `high` o `predeterminado`) | `minimal` |
| `DATABASE_URL` | Postgres: `ejecuciones`, `veredictos` y memoria. Heroku la crea sola | ver sección 2 |
| `REDIS_URL` | Redis con el índice de la política (RAG) | *(secreta)* · **PENDIENTE (Eduardo)** |
| `REDIS_PREFIJO` | Índice del grupo en Redis (no es secreto) | `grupo05_v15` |
| `NEO4J_URI` / `NEO4J_USER` / `NEO4J_PASSWORD` | Neo4j del GraphRAG | *(secretas)* · **PENDIENTE (Eduardo)** |
| `N8N_WEBHOOK_URL` | Webhook del caso A2A adicional con n8n | **PENDIENTE (Alex)** |
| `APP_MODULE` | Qué app levanta el `Procfile`: `api.app:app` o `src.verificador.app:app` | `api.app:app` |
| `MOSTRAR_TRAZAS` | `1` muestra en la terminal cada paso del ReAct | `0` o `1` |
| `TEST_DATABASE_URL` | Solo para pruebas: base que `tests/test_persistencia.py` puede borrar | ver sección 2 |

---

## 6. Evidencias

Una carpeta por prueba de la pauta en [`evidencias/`](evidencias/). El estado de cada una (qué
muestra, qué falta y de quién es) está en **[docs/mapa-evidencias.md](docs/mapa-evidencias.md)**.

Scripts para regenerar las evidencias de Alex (con los servicios levantados):

```bash
python evidencias/dos-recorridos/capturar.py --url http://127.0.0.1:8000 --log principal.log
python evidencias/a2a/capturar.py --log-verificador verificador.log
python evidencias/a2a/capturar_token.py --log-verificador verificador.log
FORZAR_FALLO_A2A=1 python evidencias/a2a/capturar.py --solo 02 --prefijo fallo-forzado-
```

`principal.log` y `verificador.log` son la salida de cada `uvicorn`, por ejemplo con
`uvicorn … 2>&1 | tee verificador.log`. Los scripts tapan claves y tokens con `***` y no guardan
imágenes.

---

## 7. Ampliaciones declaradas

| Ampliación | Puntos | Estado | Cómo reproducirla |
|---|---|---|---|
| RAG documental | 0,5 | Código en `main`. **PENDIENTE (Eduardo):** acceso a Redis y evidencia | Con `REDIS_URL`, `REDIS_PREFIJO` y `EMBEDDING_MODEL`: mandar a `/chat` «¿Cuál es el plazo máximo para rendir un gasto?» → la respuesta cita `[Fuente: …]` |
| Evaluación con golden set | 0,5 | Set v1.0 y evaluador en `main`; primera corrida en `evidencias/ampliacion-evaluacion/`. **PENDIENTE (Alex):** corrida completa con todo unido | `python -m evaluacion.evaluar --validar` (formato), luego `python -m evaluacion.evaluar --pausa 20` con `DATABASE_URL` y el verificador levantado. Si se corta por cuota: `--retomar --pausa 20` |
| Memoria persistente | 0,5 | Checkpointer en Postgres en `main`. **PENDIENTE (Sebastián):** evidencia | Mandar dos mensajes con el mismo `thread_id`, reiniciar el principal y comprobar que el tercero recuerda la conversación |
| MCP | 0,5 | Hecho (servidor stdio `fondos-los-alerces`, con `consultar_fondo`). Falta el `id_ejecucion` en la evidencia (Matías) | `python -m src.mcp_fondos.servidor --listar`, y una revisión de gasto en la que el ReAct llama a `consultar_fondo` |
| GraphRAG | 1,0 | Código y catálogo en `main`. **PENDIENTE (Eduardo):** cargar Neo4j y evidencia | `python -m src.conocimiento.grafo.cargar_grafo --plan` (sin Neo4j). La carga real va con autorización (ver `src/conocimiento/grafo/README.md`). Después, «¿Cuál es el tope de hotel para un jefe de tienda?» por `/chat` |
| **De respaldo:** n8n A2A | 1,0 | **PENDIENTE (Alex):** no empezado | Un caso A2A adicional con n8n que **no** rehace la delegación al verificador (ver `n8n/README.md`) |

---

## 8. Integrantes y aportes

| Integrante | Rama | Aportes |
|---|---|---|
| **Alex** | `c2tf/alex-integracion` | Caso, estructura y contratos. Router y grafo principal (`src/principal/router.py`, `grafo.py`, `fuera_de_alcance`). Verificador A2A (`src/verificador/`, `delegar_verificador`, cliente y executor A2A, canal con `TOKEN_A2A`). Golden set v1.0 y evaluador con retoma por cuota (`evaluacion/`). Evidencias de recorridos, A2A y evaluación. Medición de tiempos, mapa de evidencias y este README. **Pendiente:** n8n y la corrida final del evaluador |
| **Matías Muñoz** | `c2tf/matias-react-seguridad` | Flujo `revisar_gasto` (ReAct con parada por veredicto o `MAX_PASOS_REACT`, piso por verificación antes de registrar, respaldo de modelo), juez, seguridad (acciones permitidas, bloqueo y `revisar_token_a2a` / `proteger_con_token_a2a`) y servidor MCP de fondos. **Pendiente:** evidencia del bloqueo en vivo y `id_ejecucion` en las evidencias del ReAct |
| **Eduardo Basaure** | `c2tf/eduardo-conocimiento` | RAG de solo lectura sobre Redis, GraphRAG (catálogo de 24 nodos y 27 relaciones, carga y consulta en Neo4j), flujo `consulta_politica` con fuentes verificadas y chat web (`web/`). **Pendiente:** acceso a Redis y Neo4j, y sus evidencias |
| **Sebastián Mardones** | `c2tf/sebastian-despliegue` | Persistencia en Postgres (tabla `ejecuciones`, registro de veredictos y checkpointer de memoria) y modelo de respaldo (`obtener_llm_con_respaldo`). **Pendiente:** despliegue en Heroku (dos apps y Config Vars) y las evidencias de despliegue, resiliencia y memoria |

## Estructura

| Carpeta | Qué hay |
|---|---|
| `api/` | API FastAPI del principal (`/health`, `/`, `/chat`, `/registro/{id}`) |
| `src/principal/` | Grafo, router, flujos (`revisar_gasto`, `consulta_politica`, `fuera_de_alcance`), juez y herramientas |
| `src/verificador/` | Agente verificador de boletas (A2A) |
| `src/comun/` | Contrato de tipos, configuración, seguridad, registro, modelos y cliente/servidor A2A |
| `src/conocimiento/` | RAG (Redis) y GraphRAG (Neo4j) |
| `src/mcp_fondos/` | Servidor MCP con `consultar_fondo` |
| `web/` | Chat web (lo sirve `GET /`) |
| `n8n/` | Caso A2A adicional (ampliación de respaldo, pendiente) |
| `datos/` | Política, fondos, rendiciones, boletas y catálogo de cargos (todo ficticio) |
| `evaluacion/` | Golden set versionado y evaluador |
| `tests/` | Pruebas (`pytest`) |
| `evidencias/` | Una subcarpeta por prueba de la pauta y por ampliación |
| `docs/` | Pauta, reparto, contratos, decisiones, medición de tiempos y mapa de evidencias |
