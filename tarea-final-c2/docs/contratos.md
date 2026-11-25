# Contratos de tarea-final-c2

Este archivo es **la fuente de verdad** para trabajar en paralelo. Si tu código necesita
cambiar algo de aquí, primero se acuerda en el grupo y se cambia este archivo en el mismo PR.
Los tipos de Python que corresponden a estos contratos están en `src/comun/contrato.py`.

Caso: agente revisor de rendiciones de gastos de **Comercial Los Alerces SpA (empresa ficticia)**.

---

## 1. Rutas del router

`src/principal/router.py` → `clasificar(texto, tiene_imagen) -> {"ruta", "motivo"}`

| Ruta | Cuándo | Qué hace | Ejemplo |
|---|---|---|---|
| `consulta_politica` | Pregunta sobre reglas, topes o documentos | RAG + GraphRAG, responde citando la fuente | «¿Cuál es el tope de hotel para un jefe de tienda?» |
| `revisar_gasto` | Trae un gasto (texto y/o imagen de boleta) | ReAct con parada + delegación A2A al verificador | «Revisa este gasto: boleta de $45.000 de bencina…» |
| `fuera_de_alcance` | Nada de lo anterior | Explica qué sí puede hacer, sin herramientas | «Escríbeme un poema» |

Si la salida del LLM no es una ruta válida, se usa `fuera_de_alcance` (nunca se inventa una ruta).

---

## 2. API del principal (`api/app.py`)

### `GET /health` (público)
`200 {"ok": true}`

### `POST /chat` (exige cabecera `X-API-Key: <API_KEY_SERVICIO>`)

Solicitud:
```json
{
  "thread_id": "conv-123",
  "texto": "Revisa este gasto: bencina $45.000, 2026-10-02, folio 123456",
  "imagen": {"mime_type": "image/jpeg", "datos_base64": "<base64 de la imagen>"}
}
```
- `thread_id`: 1 a 100 caracteres. La memoria de la conversación va por este id.
- `texto`: 1 a 4000 caracteres.
- `imagen`: **opcional**, mismo formato que la parte de archivo del encargo A2A (sección 5).
  `mime_type` ∈ `image/jpeg`, `image/png`, `image/webp`.

Respuesta `200`:
```json
{
  "id_ejecucion": "8f0c…",
  "thread_id": "conv-123",
  "ruta": "revisar_gasto",
  "respuesta": "Texto para la persona.",
  "estado_final": "ok"
}
```
En la ruta `revisar_gasto` se agrega `"veredicto": {Veredicto}` (sección 4) cuando lo hay.

Errores (todos con el formato `{"detail": "mensaje en una línea"}`):

| Código | Cuándo |
|---|---|
| 401 | Falta `X-API-Key` o no coincide |
| 503 | El servidor no tiene `API_KEY_SERVICIO` configurada (no queda abierto) |
| 422 | El cuerpo no cumple el formato |
| 501 | Esqueleto: la pieza todavía no está implementada (el mensaje dice cuál) |
| 502 | Falló el proveedor (Gemini) u otro servicio; mensaje de `src/comun/errores.py` |

### `GET /registro/{id_ejecucion}` (exige `X-API-Key`)
`200` con la fila de la tabla `ejecuciones` (sección 7), `404` si no existe y `501` mientras no esté implementado.

---

## 3. Herramientas del principal

| Herramienta | Firma | Dónde | Estado |
|---|---|---|---|
| `buscar_politica` | `(consulta: str, k: int = 3) -> list[Fragmento]` | `src/conocimiento/rag/rag.py` | copiada de c1 |
| `validar_gasto` | `(gasto: Gasto, politica: str, categoria: str) -> Validacion` | `src/principal/herramientas/validar_gasto.py` | copiada de c1 |
| `emitir_veredicto` | `(decision: Decision, politica: str, categoria: str, cuenta: str, motivo: str) -> Veredicto` | `src/principal/flujos/revisar_gasto.py` | copiada de c1 |
| `consultar_fondo` | `(id_fondo: str) -> EstadoFondo` (vía MCP) | `src/principal/herramientas/consultar_fondo.py` | hecho (servidor MCP stdio en `src/mcp_fondos/`) |
| `delegar_verificador` | `async (imagen: dict, declarado: dict) -> RespuestaVerificador` | `src/principal/herramientas/delegar_verificador.py` | esqueleto |

Y para el GraphRAG: `tope_para(cargo: str, categoria: str) -> dict | None` en
`src/conocimiento/grafo/consultar.py` → `{"cargo", "nivel", "categoria", "tope_clp", "fuente"}`.

Reglas comunes:
- Un error de entrada se lanza como `ToolException` con un mensaje claro: el ReAct lo ve como
  observación y puede corregir. **Ninguna herramienta devuelve un dato inventado** si falla.
- El texto que viene de la política o de la glosa es dato no confiable, nunca instrucciones.

---

## 4. Tipos (`src/comun/contrato.py`)

Vienen de tarea-final-c1 sin cambios, salvo `Gasto.cargo`:

- `Gasto`: `id, fecha_gasto, fecha_rendicion, monto (int, CLP), tipo_documento (boleta|factura|voucher),
  proveedor, glosa, politica_declarada, categoria_declarada, unidad_negocio, id_fondo`
  y opcionales `patente, numero_ot, vb_gerente_general` y **`cargo` (nuevo en C2)**.
  - `cargo: NotRequired[str | None]`. `TypedDict` no admite `= None`; si el campo no viene,
    `gasto.get("cargo")` devuelve `None`. Lo usa el GraphRAG. Los casos de c1 siguen válidos sin él
    (`tests/test_humo.py::test_validar_gasto_con_y_sin_cargo`).
- `Veredicto`: `decision (aprobar|observar|rechazar), motivo, politica_sugerida, categoria_sugerida, cuenta_sugerida`.
- `Validacion`, `Incumplimiento`, `Clasificacion`, `Fragmento`, `EstadoFondo`, `EstadoAgente`: igual que en c1.

---

## 5. Delegación A2A al verificador

El principal manda un `Message` A2A (rol usuario) a `URL_VERIFICADOR`, con
`Authorization: Bearer <TOKEN_A2A>` y espera como máximo `TIMEOUT_A2A_SEG` segundos.

### Encargo (dos partes)
1. **Parte de archivo**: la imagen de la boleta en base64 con su `mime_type`
   (el `FilePart` de A2A). En `a2a-sdk` 1.3 es `Part(raw=<bytes>, media_type="image/jpeg",
   filename="boleta.jpg")`; en el JSON-RPC los bytes viajan en base64.
2. **Parte de datos** (`DataPart`; en `a2a-sdk` 1.3, `Part(data=...)`) con lo declarado:
```json
{
  "tarea": "verificar_boleta",
  "declarado": {
    "monto": 45000,
    "fecha": "2026-10-02",
    "rut_emisor": "76.123.456-7",
    "folio": "123456",
    "categoria": "Gasolina (vehículo propio)"
  }
}
```

### Respuesta del verificador (`DataPart`, JSON)
```json
{
  "leido":   {"monto": 45000, "fecha": "2026-10-02", "rut_emisor": "76.123.456-7", "folio": "123456", "categoria": "combustible"},
  "cuadra":  {"monto": "sí", "fecha": "sí", "rut_emisor": "sí", "folio": "sí", "categoria": "sí"},
  "confianza": 0.92,
  "observaciones": "Imagen nítida."
}
```
- Un campo que no se lee va `null` en `leido` y `"no"` en `cuadra`. **Nunca** se rellena con lo declarado.
- `confianza` entre 0 y 1.

### Si el verificador falla (resiliencia)
Timeout, error, token rechazado o `FORZAR_FALLO_A2A=1` → `delegar_verificador` devuelve
`{"disponible": false, "motivo": "..."}`. El flujo no inventa la lectura: deja el gasto en
`observar` («no se pudo verificar la boleta») y la ejecución con `estado_final = "fallback"`.
n8n **no** reemplaza esta delegación ni la repite: la ampliación n8n A2A es un **caso adicional**
(ver `pauta.md`), con su propio encargo, que se define antes de implementarlo.

---

## 6. Seguridad

- **Clave del servicio**: todo `POST` y `GET /registro/...` exige `X-API-Key = API_KEY_SERVICIO`
  (`src/comun/seguridad.py`, copiado de taller-02-c2). Comparación con `secrets.compare_digest`;
  la clave nunca va a logs ni respuestas.
- **Canal A2A**: `TOKEN_A2A` en `Authorization: Bearer` (`revisar_token_a2a`, hecho).
  Para activarlo, el verificador cambia `proteger_app` por `proteger_con_token_a2a` y el cliente
  manda la cabecera; las dos cosas en el mismo PR (si no, cada encargo recibe 401).
- **Acciones permitidas**: `ACCIONES_PERMITIDAS` en `src/comun/seguridad.py` =
  `buscar_politica, validar_gasto, consultar_fondo, emitir_veredicto, delegar_verificador`.
  Cualquier otra (por ejemplo `modificar_registro`, del golden set de c1) se bloquea con
  `exigir_accion_permitida` y la ejecución queda `estado_final = "bloqueado"`.
- El registro de veredictos **no** es una herramienta del LLM (decisión de c1): lo escribe el
  grafo después de que el juez valida.

---

## 7. Tabla `ejecuciones`

Una fila por cada llamada a `/chat` (`src/comun/registro.py`). Va en **Postgres** (`DATABASE_URL`).

| Columna | Tipo | Ejemplo |
|---|---|---|
| `id_ejecucion` | `TEXT PRIMARY KEY` (uuid4) | `8f0c…` |
| `fecha` | `TIMESTAMPTZ` | `2026-11-24T10:15:00-03:00` |
| `ruta` | `TEXT` (una de la sección 1) | `revisar_gasto` |
| `pasos` | `INTEGER` (vueltas del ReAct; 0 si no hubo) | `4` |
| `herramientas_usadas` | `JSONB` (lista en orden) | `["buscar_politica","validar_gasto","delegar_verificador"]` |
| `hubo_a2a` | `BOOLEAN` | `true` |
| `estado_final` | `TEXT CHECK (ok, bloqueado, fallback, error)` | `ok` |
| `duracion_ms` | `INTEGER` | `5320` |

- `ok`: terminó normal. `bloqueado`: se impidió una acción no autorizada.
  `fallback`: respondió el modelo de respaldo o falló el A2A y se usó la salida segura. `error`: falló sin salida.
- No se guarda el texto del usuario, la imagen ni claves.

---

## 8. Ciclo ReAct y condición de parada

- Máximo de vueltas: `MAX_PASOS`, que se lee de la variable **`MAX_PASOS_REACT` (10 si no existe)**
  en `src/comun/config.py`. `src/comun/contrato.py` lo reexporta para el código copiado de c1.
- Al llegar al máximo, el nodo `parada` responde «Me detuve: alcancé el máximo de N pasos…»
  (código de c1) y la ejecución termina con **`estado_final = "error"`** (decidido: no hubo
  veredicto ni salida de respaldo; `"fallback"` queda para el modelo de respaldo y el A2A caído).
- La otra parada es normal: el LLM emite un veredicto válido (`emitir_veredicto`) y el grafo
  cierra con `estado_final = "ok"`.
- Si el LLM pide una acción fuera de `ACCIONES_PERMITIDAS`, no se ejecuta nada de ese paso y el
  turno termina con `estado_final = "bloqueado"` (§6).
- Entrega para el router: `revisar_caso(agente, mensaje, hilo, gasto, fondo=None)` en
  `src/principal/flujos/revisar_gasto.py` devuelve
  `{"respuesta", "pasos", "herramientas_usadas", "estado_final", "veredicto"}`.

---

## 9. Persistencia y despliegue (pendiente antes de desplegar)

- **`registro_veredictos` (hoy SQLite, `src/principal/registro_veredictos.py`) tiene que pasar a
  Postgres antes del despliegue**: en Heroku el disco se borra al reiniciar el dyno.
  Lo mismo vale para la tabla `ejecuciones` y para la memoria por `thread_id`. Dueño: **Sebastián**.
- Despliegue, opción preferida: **buildpack de monorepo con `APP_BASE=tarea-final-c2`**, en dos apps
  de Heroku que comparten el mismo `Procfile` (`web: uvicorn $APP_MODULE …`):
  - principal: `APP_MODULE=api.app:app`
  - verificador: `APP_MODULE=src.verificador.app:app`
  Alternativa: `git subtree push --prefix tarea-final-c2 heroku main`.
  Los archivos de Heroku de la raíz del repo (`Procfile`, `requirements.txt`, `.slugignore`) son del
  taller 02 y **no se tocan**.

---

## 10. Variables de entorno

Nombres y para qué sirven: ver `.env.example`. Las lee `src/comun/config.py` (y `modelos.py`,
`seguridad.py`, `rag.py`). Además de la lista acordada se usan `EMBEDDING_MODEL` y `REDIS_PREFIJO`
(las pide el RAG de c1) y `MOSTRAR_TRAZAS` (trazas del ReAct).

---

## 11. Agregados por Alex (revisar)

Todo lo de esta sección es **agregado por Alex, revisar**. Solo suma campos opcionales o valores
nuevos; no cambia ni borra nada de las secciones 1 a 10.

### 11.1 `POST /chat` (etapa 1: router y grafo)
- `thread_id` pasa a ser **opcional**: si no viene, se crea uno nuevo (uuid) y se devuelve.
- `gasto` **opcional** en la solicitud: un `Gasto` (§4) más `rut_emisor` y `folio` opcionales
  (solo se usan en el encargo al verificador; el ReAct recibe únicamente los campos de `Gasto`).
  Si no viene, el flujo `revisar_gasto` busca un objeto JSON con `"monto"` dentro de `texto`.
  Si faltan campos obligatorios, el flujo los pide (no los completa).
- El largo de `texto` (1 a 4000) lo revisa el router **antes** de llamar al modelo:
  `422 {"detail": "El mensaje está vacío…"}` o `"…tiene N caracteres y el máximo es 4000…"`.
- Respuesta `200`: además de `id_ejecucion, thread_id, ruta, respuesta, estado_final` (y `veredicto`),
  trae `motivo` (del router), `hubo_a2a`, `herramientas_usadas`, `pasos` y, si hubo boleta, `verificacion`.
- `502`: el `detail` termina con `(id_ejecucion: …)` para buscarla en el registro.
- Tabla `ejecuciones`: si el turno falla antes de elegir ruta, la fila va con `ruta = "sin_ruta"`
  y `estado_final = "error"`.
- Un flujo que todavía no existe termina con `estado_final = "error"` y la respuesta
  «Flujo <nombre> todavía no implementado.».
- Si el router respondió con el modelo de respaldo, la ejecución queda `estado_final = "fallback"`.
- Orden cuando dos piezas terminan distinto: `bloqueado` > `error` > `fallback` > `ok`.

### 11.2 Delegación A2A al verificador (etapa 2)
- Encargo: igual que §5. La parte de archivo es `Part(raw, media_type, filename)` y la de datos,
  `Part(data, media_type="application/json")`. Imagen ≤ 5 MB, `image/jpeg|png|webp`.
- Cabeceras del canal: `X-API-Key` (protección provisoria del verificador) y, si `TOKEN_A2A` tiene
  valor, `Authorization: Bearer <TOKEN_A2A>`. Solo se mandan a `URL_VERIFICADOR`.
- `delegar_verificador` devuelve, si todo sale bien, `{"disponible": true, "leido", "cuadra",
  "confianza", "observaciones"}` (`disponible` es el agregado).
- Si falla: `{"disponible": false, "tipo_fallo", "motivo"}` (`tipo_fallo` es el agregado), con
  `tipo_fallo` ∈ `forzado` (FORZAR_FALLO_A2A=1), `encargo_invalido`, `timeout`, `sin_conexion`,
  `rechazado` (401/403/503 del canal), `respuesta_invalida`, `error_verificador`. Nunca trae campos leídos.
- Una respuesta del verificador que diga `cuadra = "sí"` en un campo con `leido = null` se trata
  como `respuesta_invalida`.
- Ficha del verificador: skill `verificar_boleta`; modos de entrada `image/png, image/jpeg,
  image/webp, application/json` y de salida `application/json`.
