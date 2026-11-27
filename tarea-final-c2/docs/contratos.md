# Contratos de tarea-final-c2

Este archivo es **la fuente de verdad** para trabajar en paralelo. Si tu código necesita
cambiar algo de aquí, primero se acuerda en el grupo y se cambia este archivo en el mismo PR.
Los tipos de Python que corresponden a estos contratos están en `src/comun/contrato.py`.

Caso: agente revisor de rendiciones de gastos de **Comercial Los Alerces SpA (empresa ficticia)**.

**Versión final (2026-11-26).** Se revisó contra el código de `main` y se dejó como definitiva. Los
agregados de Alex («§11, revisar») quedaron integrados en las secciones 2, 5, 7 y 8; §11 es ahora
un índice de dónde quedó cada uno. Lo que todavía no está implementado va marcado
**Abierto: pendiente de <dueño>** y está en el issue #100.

---

## 1. Rutas del router

`src/principal/router.py` → `clasificar(texto, tiene_imagen=False, trae_gasto=False, modelos=None)
-> {"ruta", "motivo", "modelo"}`. `modelo` es `"principal"` o `"respaldo"` (el que respondió).

| Ruta | Cuándo | Qué hace | Ejemplo |
|---|---|---|---|
| `consulta_politica` | Pregunta sobre reglas, topes o documentos | RAG + GraphRAG, responde citando la fuente | «¿Cuál es el tope de hotel para un jefe de tienda?» |
| `revisar_gasto` | Trae un gasto (texto y/o imagen de boleta) | ReAct con parada + delegación A2A al verificador | «Revisa este gasto: boleta de $45.000 de bencina…» |
| `fuera_de_alcance` | Nada de lo anterior | Explica qué sí puede hacer, sin herramientas | «Escríbeme un poema» |

- Si la salida del LLM no es una ruta válida, se usa `fuera_de_alcance` (nunca se inventa una ruta).
- Una falla del proveedor no se disfraza de `fuera_de_alcance`: se propaga como error.
- El largo de `texto` (1 a 4000) se revisa **antes** de llamar al modelo (§2, error 422).

---

## 2. API del principal (`api/app.py`)

### `GET /health` (público)
`200 {"ok": true}`

### `GET /` (público)
El chat web (`web/index.html`). La clave del servicio se ingresa en la página.

### `POST /chat` (exige cabecera `X-API-Key: <API_KEY_SERVICIO>`)

Solicitud:
```json
{
  "thread_id": "conv-123",
  "texto": "Revisa este gasto: bencina $45.000, 2026-10-02, folio 123456",
  "imagen": {"mime_type": "image/jpeg", "datos_base64": "<base64 de la imagen>"},
  "gasto": {"id": "G-0101", "monto": 45000, "…": "…", "rut_emisor": "76.123.456-7", "folio": "123456"}
}
```
- `thread_id`: **opcional**, hasta 100 caracteres. Si no viene (o viene vacío), se crea uno nuevo
  (uuid) y se devuelve. La memoria de la conversación va por este id.
- `texto`: 1 a 4000 caracteres. Lo revisa el router antes de llamar al modelo.
- `imagen`: **opcional**, mismo formato que la parte de archivo del encargo A2A (§5).
  `mime_type` ∈ `image/jpeg`, `image/png`, `image/webp`.
- `gasto`: **opcional**, un `Gasto` (§4) más `rut_emisor` y `folio` opcionales. Esos dos solo se
  usan en el encargo al verificador; el ReAct recibe únicamente los campos de `Gasto`.
  Si no viene, `revisar_gasto` busca un objeto JSON con `"monto"` dentro de `texto`. Si faltan
  campos obligatorios, el flujo los pide (no los completa) y el turno termina en `ok`.

**Modo asíncrono (por defecto).** Heroku corta una solicitud a los 30 s y `revisar_gasto` tarda
31–52 s (`docs/medicion-tiempos.md`). Por eso `POST /chat` responde **`202`** de inmediato:
```json
{"id_ejecucion": "8f0c…", "estado": "en_proceso", "consultar": "/registro/8f0c…", "thread_id": "conv-123"}
```
El grafo corre en segundo plano, en un grupo de hilos del mismo proceso
(`src/principal/en_segundo_plano.py`). El resultado se consulta en `GET /registro/{id_ejecucion}`.
Un texto vacío o de más de 4000 caracteres responde `422` **antes** de aceptarse.

**Modo síncrono: `POST /chat?esperar=true`.** Responde `200` con la respuesta completa. Es para el
uso local, las pruebas y el evaluador. También respeta el tope global (más abajo).

Respuesta completa (el `200` síncrono, y el `resultado` de `GET /registro/{id}`):
```json
{
  "id_ejecucion": "8f0c…",
  "thread_id": "conv-123",
  "ruta": "revisar_gasto",
  "motivo": "Motivo del router.",
  "respuesta": "Texto para la persona.",
  "estado_final": "ok",
  "hubo_a2a": true,
  "herramientas_usadas": ["delegar_verificador", "buscar_politica", "validar_gasto", "emitir_veredicto"],
  "pasos": 4
}
```
En la ruta `revisar_gasto` se agrega `"veredicto": {Veredicto}` (§4) cuando lo hay y, si hubo
boleta, `"verificacion"` (lo que devolvió `delegar_verificador`, §5).

Errores (todos con el formato `{"detail": "mensaje en una línea"}`):

| Código | Cuándo |
|---|---|
| 401 | Falta `X-API-Key` o no coincide |
| 503 | El servidor no tiene `API_KEY_SERVICIO` configurada (no queda abierto) |
| 422 | El cuerpo no cumple el formato, o el texto está vacío o pasa de 4000 caracteres («El mensaje está vacío…», «…tiene N caracteres y el máximo es 4000…») |
| 500 | Solo en modo asíncrono: configuración no válida (por ejemplo `TIEMPO_MAX_EJECUCION_SEG` o `MAX_EJECUCIONES_SIMULTANEAS`) |
| 501 | Solo en modo síncrono: una pieza lanza `NotImplementedError` (el mensaje dice cuál) |
| 502 | Solo en modo síncrono: falló el proveedor (Gemini) u otro servicio. El mensaje viene de `src/comun/errores.py` y termina con `(id_ejecucion: …)` |

En modo asíncrono, una falla durante la ejecución no cambia el `202`: queda en `GET /registro/{id}`
con `"estado": "error"` y su `detail`.

**Tope global, `TIEMPO_MAX_EJECUCION_SEG`** (90 s por defecto, en los dos modos):
- si la ejecución no termina a tiempo, queda en `"estado": "error"`, sin resultado, con el mensaje
  «La ejecución superó el tiempo máximo de N s…», y su fila se registra como `error` en ese momento;
- Python no puede matar un hilo: si el turno termina después, su resultado se descarta y su
  registro se ignora (mismo `id_ejecucion`, `ON CONFLICT DO NOTHING`);
- en modo síncrono, si termina después del tope, responde `estado_final = "error"`;
- el ReAct recibe la hora límite (`hora_limite`, §8) para no registrar un veredicto pasado el tope.

Hasta `MAX_EJECUCIONES_SIMULTANEAS` ejecuciones (4 por defecto) corren a la vez; las demás esperan
su turno, dentro del mismo tope.

### `GET /registro/{id_ejecucion}` (exige `X-API-Key`)
`200`:
- **en proceso:** `{"id_ejecucion", "estado": "en_proceso", "thread_id", "inicio", "segundos", "resultado": null}`;
- **terminada:** los campos de la fila de `ejecuciones` (§7) más:
  - `"estado"` (`ok` / `bloqueado` / `fallback` / `error`);
  - `"resultado"` (la respuesta completa) o `"detail"` (el mensaje de error, que termina con
    `(id_ejecucion: …)`);
  - `"inicio"`, `"fin"` y `"segundos"`;
- **si el proceso se reinició:** solo queda la fila: `"estado" = estado_final` y `"resultado": null`.

`404` si no existe. `503` si la ejecución no está en la memoria del proceso y la base no responde.

**El estado y la respuesta completa viven en la memoria del proceso** (las últimas 500), porque la
tabla `ejecuciones` no admite `en_proceso` ni guarda la respuesta. Con más de un proceso o dyno no
se comparten.
- **Abierto: pendiente de Sebastián.** Guardarlos en Postgres: una columna `respuesta JSONB` y
  admitir `estado_final = "en_proceso"` (insertar al aceptar y actualizar al terminar), o una tabla
  aparte `resultados_chat (id_ejecucion, estado, respuesta, actualizado_en)`.
- Mientras tanto, **en Heroku el principal corre con un solo proceso** (1 dyno `web`, `uvicorn` sin
  `--workers`, como el `Procfile` actual). **Abierto: pendiente de Sebastián** (confirmarlo en
  Heroku).

*(Las partes de solicitud, respuesta, asíncrono y tope estaban en §11.1 y §11.1 bis, «agregado por
Alex, revisar».)*

---

## 3. Herramientas del principal

| Herramienta | Firma | Dónde | Estado |
|---|---|---|---|
| `buscar_politica` | `(consulta: str, k: int = 3) -> list[Fragmento]` | `src/conocimiento/rag/rag.py` | copiada de c1 |
| `validar_gasto` | `(gasto: Gasto, politica: str, categoria: str) -> Validacion` | `src/principal/herramientas/validar_gasto.py` | copiada de c1 |
| `emitir_veredicto` | `(decision: Decision, politica: str, categoria: str, cuenta: str, motivo: str) -> Veredicto` | `src/principal/flujos/revisar_gasto.py` | copiada de c1 |
| `consultar_fondo` | `(id_fondo: str) -> EstadoFondo` (vía MCP) | `src/principal/herramientas/consultar_fondo.py` | hecho (servidor MCP stdio en `src/mcp_fondos/`) |
| `delegar_verificador` | `async (imagen: dict, declarado: dict) -> RespuestaVerificador` | `src/principal/herramientas/delegar_verificador.py` | hecho (verificador A2A en `src/verificador/`; formato en §5) |

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
`Authorization: Bearer <TOKEN_A2A>`, y espera como máximo `TIMEOUT_A2A_SEG` segundos.
- Esa cabecera va **solo** hacia `URL_VERIFICADOR`. La clave del servicio (`X-API-Key`) no se manda
  al verificador.
- Si el principal no tiene `TOKEN_A2A`, no llama al verificador y devuelve `tipo_fallo = "rechazado"`.
- `GET /health` y la ficha del verificador son públicos.

### Encargo (dos partes)
1. **Parte de archivo**: la imagen de la boleta en base64 con su `mime_type`
   (el `FilePart` de A2A). En `a2a-sdk` 1.3 es `Part(raw=<bytes>, media_type="image/jpeg",
   filename="boleta.jpg")`; en el JSON-RPC los bytes viajan en base64. `image/jpeg|png|webp`,
   hasta 5 MB (lo revisa el verificador).
2. **Parte de datos** (`DataPart`; en `a2a-sdk` 1.3, `Part(data=..., media_type="application/json")`)
   con lo declarado:
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
`fecha` es `gasto.fecha_gasto` y `categoria` es `gasto.categoria_declarada`.

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
- Una respuesta que diga `cuadra = "sí"` en un campo con `leido = null` se trata como
  `respuesta_invalida`.

`delegar_verificador` devuelve, si todo sale bien,
`{"disponible": true, "leido", "cuadra", "confianza", "observaciones"}`.

### Si el verificador falla (resiliencia)
`delegar_verificador` devuelve `{"disponible": false, "tipo_fallo", "motivo"}`. Nunca trae campos
leídos. `tipo_fallo` es uno de:

| `tipo_fallo` | Cuándo |
|---|---|
| `forzado` | `FORZAR_FALLO_A2A=1` |
| `encargo_invalido` | Tipo de imagen no admitido, base64 no válido o imagen vacía |
| `timeout` | No respondió en `TIMEOUT_A2A_SEG` |
| `sin_conexion` | El verificador no está levantado o `URL_VERIFICADOR` es incorrecta |
| `rechazado` | 401/403/503 del canal, o el principal no tiene `TOKEN_A2A` |
| `respuesta_invalida` | La respuesta no tiene el formato de arriba |
| `error_verificador` | Cualquier otro error del verificador |

El flujo no inventa la lectura:
- si la decisión era «aprobar», baja a «observar» («no se pudo verificar la boleta»), antes de
  registrar (§8); un «observar» o «rechazar» queda igual;
- la ejecución termina con `estado_final = "fallback"`.

Lo mismo vale si el verificador responde pero algún campo no cuadra: una aprobación baja a
«observar» («la boleta no coincide con lo declarado en …»), aunque ahí el estado sigue en `ok`.

### Ficha del verificador
Skill `verificar_boleta`. Modos de entrada `image/png, image/jpeg, image/webp, application/json`
y de salida `application/json`. En `/.well-known/agent-card.json`.

n8n **no** reemplaza esta delegación ni la repite: la ampliación n8n A2A es un **caso adicional**
(ver `pauta.md`), con su propio encargo, que se define antes de implementarlo.

*(El canal, `tipo_fallo` y la ficha estaban en §11.2, «agregado por Alex, revisar».)*

---

## 6. Seguridad

- **Clave del servicio**: todo `POST` y `GET /registro/...` exige `X-API-Key = API_KEY_SERVICIO`
  (`src/comun/seguridad.py`, copiado de taller-02-c2). Comparación con `secrets.compare_digest`;
  la clave nunca va a logs ni respuestas.
- **Canal A2A**: `TOKEN_A2A` en `Authorization: Bearer`. El verificador usa `proteger_con_token_a2a`
  (`revisar_token_a2a`) y `delegar_verificador` manda el Bearer.
  - Sin token, con un token incorrecto o sin «Bearer» → 401.
  - Si el verificador no tiene `TOKEN_A2A` → 503.
  - Las dos apps de Heroku necesitan el **mismo** `TOKEN_A2A`.
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
| `ruta` | `TEXT CHECK (consulta_politica, revisar_gasto, fuera_de_alcance)` | `revisar_gasto` |
| `pasos` | `INTEGER` (vueltas del ReAct; 0 si no hubo) | `4` |
| `herramientas_usadas` | `JSONB` (lista en orden) | `["buscar_politica","validar_gasto","delegar_verificador"]` |
| `hubo_a2a` | `BOOLEAN` | `true` |
| `estado_final` | `TEXT CHECK (ok, bloqueado, fallback, error)` | `ok` |
| `duracion_ms` | `INTEGER` | `5320` |

Estados finales:
- `ok`: terminó normal.
- `bloqueado`: se impidió una acción no autorizada.
- `fallback`: respondió el modelo de respaldo (router, ReAct o juez), o falló el A2A y se usó la
  salida segura.
- `error`: falló sin salida (también el tope de pasos, el tope de tiempo y un flujo que todavía
  no existe, que responde «Flujo <nombre> todavía no implementado.»).

Reglas:
- Orden cuando dos piezas terminan distinto: `bloqueado` > `error` > `fallback` > `ok`.
- No se guarda el texto del usuario, la imagen ni claves.
- Si la base no responde, `guardar_ejecucion` deja una línea de error en el log y **no** rompe la
  respuesta de `/chat`. Un id repetido no duplica la fila.
- Si el turno falla **antes** de que el router elija, el grafo manda la fila con
  `ruta = "sin_ruta"` y `estado_final = "error"`. Si el router alcanzó a elegir, la fila lleva
  esa ruta. **Abierto: pendiente de Sebastián.** El `CHECK` de `ruta` todavía no admite
  `"sin_ruta"`, así que esa fila se rechaza y queda solo la línea del log. Hay que agregarlo al
  `CHECK` (y un `ALTER TABLE` si la tabla ya existe en Heroku).

*(`sin_ruta`, el orden de estados y el flujo no implementado estaban en §11.1.)*

---

## 8. Ciclo ReAct y condición de parada

- Máximo de vueltas: `MAX_PASOS`, que se lee de la variable **`MAX_PASOS_REACT` (10 si no existe)**
  en `src/comun/config.py`. `src/comun/contrato.py` lo reexporta para el código copiado de c1.
  En `.env.example` y en Heroku va `MAX_PASOS_REACT=6` (una revisión normal cierra en 4 o 5 vueltas).
- Al llegar al máximo, el nodo `parada` responde «Me detuve: alcancé el máximo de N pasos…»
  (código de c1) y la ejecución termina con **`estado_final = "error"`**. Se decidió así porque no
  hubo veredicto ni salida de respaldo; `"fallback"` queda para el modelo de respaldo y el A2A
  caído. Lo prueba `tests/test_react_mcp.py::test_se_detiene_por_max_pasos_con_estado_error`.
- La otra parada es normal: el LLM emite un veredicto válido (`emitir_veredicto`) y el grafo
  cierra con `estado_final = "ok"`. **«ok» exige veredicto**: si el modelo cierra sin
  `emitir_veredicto` (por ejemplo, boleta ilegible), el turno es `"error"`.
- Si respondió `MODELO_RESPALDO` (en el ReAct o en el juez) y hubo veredicto, el turno es `"fallback"`.
- Si el LLM pide una acción fuera de `ACCIONES_PERMITIDAS`, no se ejecuta nada de ese paso y el
  turno termina con `estado_final = "bloqueado"` (§6).
- El juez solo se consulta si la decisión es «aprobar» (solo puede bajar una aprobación); con
  «observar» o «rechazar» no se gasta esa llamada.

Entrega para el router, en `src/principal/flujos/revisar_gasto.py`:
```
revisar_caso(agente, mensaje, hilo, gasto, fondo=None, verificacion=None, hora_limite=None)
  -> {"respuesta", "pasos", "herramientas_usadas", "estado_final", "veredicto"}
```
- `verificacion` es la respuesta de `delegar_verificador` (§5). Si no cuadra o no se pudo
  verificar, una aprobación baja a «observar» **antes** de tocar el fondo y de `registrar_veredicto`
  (`motivo_piso_verificacion` en `nodo_cerrar`).
- `hora_limite` es un `datetime` **en UTC**: inicio de la ejecución + `TIEMPO_MAX_EJECUCION_SEG`.
  - En el modo asíncrono se cuenta desde que `/chat` aceptó el mensaje.
  - Se calcula en **toda** ejecución, también con `?esperar=true`.
  - Si viene sin zona, se asume UTC.
  - Se revisa antes de cada llamada al modelo y justo antes de registrar.
  - **Si ya pasó, no se llama a `registrar_veredicto` ni se toca el fondo.** El turno es `"error"`,
    sin veredicto, con un mensaje claro. Así lo registrado coincide con lo que `/chat` ya informó.
- El grafo pasa cada argumento opcional **solo si la firma de `revisar_caso` lo acepta** (lo
  revisa con `inspect`). Si no, deja una vez en el log «revisar_caso no acepta «…» todavía».
  Así un argumento nuevo no rompe el grafo antes de que el ReAct lo implemente.

*(`hora_limite` estaba en §11.1 ter, «agregado por Alex, revisar».)*

---

## 9. Persistencia y despliegue

- **Persistencia (Sebastián): hecha, en Postgres (`DATABASE_URL`).**
  - La tabla `ejecuciones` (§7) está en `src/comun/registro.py`.
  - El registro de veredictos (tabla `veredictos`) está en `src/principal/registro_veredictos.py`.
  - La memoria por `thread_id` es el checkpointer de LangGraph, en `src/comun/memoria.py`.
  - Las tablas se crean solas.
- **Sin `DATABASE_URL`** (uso local):
  - la memoria queda en el proceso y las ejecuciones, solo en el log;
  - `revisar_gasto` falla al registrar el veredicto («Falta DATABASE_URL en .env…»).
  - **Abierto: pendiente de Sebastián:** un mensaje más claro o documentar el Postgres local. El
    README ya trae el comando de Docker.
- **Despliegue (Sebastián):** dos apps de Heroku con el `Procfile` de `tarea-final-c2/`
  (`web: uvicorn $APP_MODULE --host 0.0.0.0 --port $PORT`):
  - principal: `APP_MODULE=api.app:app`;
  - verificador: `APP_MODULE=src.verificador.app:app`.

  La opción preferida es el buildpack de monorepo con `APP_BASE=tarea-final-c2`; la alternativa,
  `git subtree push --prefix tarea-final-c2 heroku main`. Los archivos de Heroku de la raíz del
  repo (`Procfile`, `requirements.txt`, `.slugignore`) son del taller 02 y **no se tocan**.
- **Abierto: pendiente de Sebastián.** Config Vars de Heroku:
  - el mismo `TOKEN_A2A` en las dos apps;
  - `MAX_PASOS_REACT=6`;
  - `REDIS_URL`, `REDIS_PREFIJO` y `EMBEDDING_MODEL`;
  - `NEO4J_*`, con `NEO4J_DATABASE`;
  - un solo proceso (§2).

  También la evidencia de despliegue.

---

## 10. Variables de entorno

Nombres, para qué sirven y valores de ejemplo: ver `.env.example`. Las lee `src/comun/config.py`
(y `modelos.py`, `seguridad.py`, `rag.py`, `src/conocimiento/grafo/conexion.py`,
`src/principal/grafo.py` y `en_segundo_plano.py`).
- Además de la lista acordada se usan:
  - `EMBEDDING_MODEL` y `REDIS_PREFIJO`, que pide el RAG de c1;
  - `MOSTRAR_TRAZAS`, para las trazas del ReAct;
  - `NIVEL_RAZONAMIENTO`, para el router y el verificador;
  - `TIEMPO_MAX_EJECUCION_SEG` y `MAX_EJECUCIONES_SIMULTANEAS`, para `/chat` (§2);
  - `NEO4J_DATABASE`, el nombre de la base en Aura.
- Las variables `*_REMOTO` y `REMOTO_*` de `.env.example` no las lee el código de las apps: son para
  probar contra Heroku.
- `N8N_WEBHOOK_URL` todavía no la lee nada. **Abierto: pendiente de Alex** (ampliación n8n).

---

## 11. Agregados por Alex: dónde quedaron

Esta sección era «agregado por Alex, revisar». El 2026-11-26 se comparó cada punto con el código
de `main` y se integró en la sección principal. Se dejan los números porque el código y otros
documentos los citan:

| Antes | Ahora | Estado |
|---|---|---|
| §11.1 `POST /chat` (`thread_id` y `gasto` opcionales, largo del texto, campos de la respuesta, 502 con id) | §2 | definitiva |
| §11.1 (`sin_ruta`, flujo no implementado, respaldo del router, orden de estados) | §7 | definitiva, salvo `sin_ruta` en el `CHECK`: **Abierto: pendiente de Sebastián** |
| §11.1 bis `/chat` asíncrono, `GET /registro/{id}`, tope global, un solo proceso | §2 | definitiva; guardar `en_proceso` y la respuesta en Postgres: **Abierto: pendiente de Sebastián** |
| §11.1 ter `hora_limite` | §8 | definitiva (implementada en #108) |
| §11.2 Delegación A2A (canal, `tipo_fallo`, `respuesta_invalida`, ficha) | §5 | definitiva |
