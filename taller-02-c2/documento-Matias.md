# Documento · Matías Muñoz · Taller 2 · Control de acceso y manejo de errores

Grupo 5 · rama `c2t2/matias-seguridad`.

## 1. Mi tarea

Según el reparto del grupo: *«Control de acceso: el servidor exige la clave (cabecera
X-API-Key) y responde 401 si falta o es incorrecta. Manejo de errores: pregunta vacía,
falla de Gemini o sin conexión con mensajes claros, nunca como si hubiera funcionado.
Evidencias de acceso permitido y rechazado.»*

## 2. Qué hice

**Herramienta usada:** Claude Code (asistente de programación de Anthropic). Yo di las
instrucciones, aprobé los cambios y revisé los resultados; el asistente escribió el código y
corrió las pruebas.

### Archivos nuevos (mi zona)

| Archivo | Qué hace |
| --- | --- |
| `proyecto/src/comun/seguridad.py` | Middleware que exige la cabecera `X-API-Key` en toda petición que envía datos (POST, PUT, PATCH, DELETE), la compara con `CLAVE_API` usando `secrets.compare_digest` y responde `401` con `{"detail": "mensaje"}`. Deja públicas la página, las fichas y `/salud`. Si `CLAVE_API` está vacía, avisa al arrancar y responde `503` a toda consulta: la app no queda abierta. |
| `proyecto/src/comun/errores.py` | Traduce las fallas de Gemini, de la red o de un agente a un mensaje de una línea en español, sin traza ni claves. Oculta cualquier clave que aparezca en un mensaje. |
| `proyecto/tests/test_seguridad.py` | 52 pruebas de acceso y errores, sin llamar a Gemini. |
| `proyecto/tests/conftest.py` | Define una `CLAVE_API` falsa solo para pytest, para que las pruebas no dependan del `.env` de quien las corre. |

### Cambios mínimos en archivos de otras personas

La regla 3 pide avisar antes de tocar archivos de otra persona. El asistente me avisó de
estos cambios antes de hacerlos y yo los aprobé; no hay otra forma de cumplir la tarea.
Alex los revisa en el PR:

| Archivo | Cambio | Por qué |
| --- | --- | --- |
| `proyecto/app.py` | `proteger_app(app)`. | Activa el control de acceso. |
| `proyecto/src/coordinador/cliente.py` | Un gancho que agrega `X-API-Key` a las llamadas hacia `127.0.0.1` y el puerto de esta misma app. | El coordinador se llama a sí mismo por A2A y esas rutas ahora exigen la clave. **No se envía a ninguna otra dirección**, para que la clave nunca salga hacia los agentes de otros computadores (`URLS_AGENTES`). |
| `proyecto/src/coordinador/graph.py` | Un error del agente, de Gemini o la falta de agentes ya no se devuelve como respuesta: se levanta `ErrorDeServicio`. | Antes llegaba al panel como `200` con un texto como «No pude consultar al agente remoto…». |
| `proyecto/src/comun/executor.py` | Si el agente falla, se informa como error A2A y no como un mensaje normal. | Mismo motivo: un error no debe parecer una respuesta. |
| `proyecto/tests/test_app.py` | La prueba del panel envía la cabecera `X-API-Key`. | El panel ahora exige la clave. |
| `proyecto/tests/test_registro.py` | La prueba de error A2A espera `ErrorDeServicio`. | Cambió el comportamiento a propósito; sigue verificando la misma línea de registro. |
| `proyecto/.env.example` y `README.md` | Documentan `CLAVE_API`; completé la sección **Seguridad**. | Parte de mi tarea. |

No toqué `panel.py` ni `panel.html` (zona de Eduardo): el `502` lo entrega el `panel.py` que
ya existía, y el formato `{"detail": "mensaje"}` es el acordado con él.

## 3. Prompts que usé

La instrucción de la tarea es el texto del grupo que Alex preparó para cada integrante y que
yo pegué en Claude Code. Se cita completa, tal cual:

> Soy Matías del Grupo 5. Trabajamos un taller evaluado en el repo del grupo
> (agentic-ia-grupo-05), que ya tengo clonado. El proyecto está en
> taller-02-c2/proyecto: una app FastAPI única que sirve una página web con chat y,
> por detrás, un coordinador que delega por A2A a 4 agentes (planificador de ferias,
> del taller anterior). Cada agente está en /agentes/{nombre} dentro de la misma app.
>
> Reglas de trabajo:
> 1. Trae las ramas con git fetch y cámbiate a la mía: git switch c2t2/matias-seguridad
>    (ya existe en GitHub, la creó Alex; no la crees de nuevo). Trabajo solo ahí.
> 2. Lee taller-02-c2/README.md y taller-02-c2/proyecto/AGENTS.md antes de tocar nada
>    y respeta sus reglas.
> 3. Trabaja solo en los archivos de mi zona (validación de acceso y manejo de
>    errores en el servidor). Si necesitas tocar un archivo de otra persona, dímelo
>    primero.
> 4. Para probar en local: entra a taller-02-c2/proyecto, crea el entorno si no
>    existe (python3.12 -m venv .venv, actívalo, pip install -r requirements.txt),
>    copia .env.example a .env, pon mi GOOGLE_API_KEY y levanta la app con:
>    uvicorn app:app --reload --port 8000
> 5. Nunca escribas claves reales en el código ni en archivos del repo. Verifica con
>    git status que .env no aparezca antes de cada commit.
> 6. Mis evidencias van en taller-02-c2/evidencias/matias/ y mi documento en
>    taller-02-c2/documento-Matias.md: qué hice, los prompts que usé, qué cambié
>    después de probar y, por cada prueba, una tabla con Entorno y fecha (LOCAL),
>    Solicitud, Resultado esperado, Resultado obtenido y Observaciones. En las
>    capturas no deben verse claves, tokens ni datos personales.
> 7. Al terminar: corre pytest, haz commit en mi rama y dame los comandos para hacer
>    push y abrir el PR hacia main (los ejecuto yo). Alex revisa y une los PR.
>
> MI TAREA: control de acceso y manejo de errores en el servidor.
> - CLAVE_API (ya declarada en .env.example) es la clave de acceso. En cada
>   POST /panel/consultar el servidor exige la cabecera X-API-Key y la compara con
>   CLAVE_API. Si falta o no coincide responde 401 con {"detail": "mensaje claro en
>   español"}. Este formato está acordado con Eduardo, que hace el frontend: no lo
>   cambies.
> - Si CLAVE_API está vacía, la app no debe quedar abierta a cualquiera: que avise con
>   un error entendible al arrancar.
> - Los endpoints A2A de los agentes (/agentes/*) y del coordinador también deben
>   quedar protegidos con la misma clave, pero ojo: el coordinador se llama a sí mismo
>   por A2A, así que su cliente interno tiene que enviar la cabecera también. Las
>   fichas (/.well-known/agent-card.json) y /salud siguen públicas.
> - La clave nunca aparece en el código, el HTML ni los logs. Compárala de forma
>   segura (secrets.compare_digest).
> - Manejo de errores: pregunta vacía → 400 (ya existe, verificar); si Gemini falla o
>   no hay conexión → 502 con mensaje entendible, sin stack trace ni claves; nunca un
>   error presentado como respuesta exitosa. Pruébalo con una GOOGLE_API_KEY inválida a
>   propósito.
> - Actualiza la sección Configuración del README con CLAVE_API: qué es y cómo elegir
>   una.
> - Pruebas pytest sin llamar a Gemini: sin clave → 401, clave mala → 401, clave
>    correcta con texto vacío → 400, ficha y /salud sin clave → 200.
> - Evidencias: un curl autorizado y uno rechazado (con la clave tapada) y un caso de
>   falla del proveedor con su mensaje. Son las evidencias de "acceso permitido y
>   rechazado" que exige la pauta.

Después de que el asistente leyó el proyecto y me avisó que necesitaba tocar cuatro archivos
de Alex (`app.py`, `cliente.py`, `graph.py` y `executor.py`), mi instrucción fue:

> Sí, adelante

## 4. Qué cambié después de probar

- **Una prueba de Alex falló** (`test_registro_de_un_error_a2a`) porque esperaba que un error
  del agente se devolviera como texto. El cambio era intencional, así que la adapté: ahora
  espera el error y conserva la verificación de la línea de registro.
- **El mensaje de timeout decía «Gemini tardó demasiado»**, pero esa prueba era un timeout
  de la tarea A2A, no de Gemini. Lo cambié por un mensaje neutro («Gemini o un agente
  tardó demasiado en responder»).
- **El registro del servidor perdía el detalle técnico** al mostrar solo el mensaje claro.
  Ahora la persona recibe el mensaje claro y el registro conserva el original, sin claves.
- **Mi expresión para ocultar claves también reescribía frases normales** como «API key not
  valid». La limité a las formas `clave=valor` y `Bearer …`.
- **Detecté un caso más de error disfrazado de respuesta**: si ningún agente respondía al
  descubrirlos, el coordinador contestaba «No tengo un agente para eso». Ahora es un error
  `502` con «No hay agentes disponibles».
- **Una de mis pruebas tenía una aserción floja** (aceptaba 200 o 401, así que no probaba
  nada). La reescribí: la misma llamada da 401 sin el gancho del cliente y pasa el control
  de acceso con él.
- **Una clave de Gemini falsa en las pruebas tenía la forma de una real** (`AIza…`), y un
  escáner de secretos podría marcarla. Ahora se arma por partes y ese texto no aparece en
  el archivo.

## 5. Pruebas

Cada prueba se ejecutó sobre la app real levantada con `uvicorn app:app` (no solo en
memoria). Las salidas están guardadas en `evidencias/matias/`, con la clave de acceso
enmascarada. Los errores de las pruebas 7 y 8 se provocaron a propósito en instancias
aparte, con otro puerto.

### Prueba 1 · Acceso permitido

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| LOCAL · 2026-11-13 10:17 | `POST /panel/consultar` con `X-API-Key` correcta y la pregunta «Tengo una feria cultural de 3 horas desde las 16:00 para público familiar…» | `200` con `respuesta`, `agente` y `motivo` | `200`. El supervisor eligió al Agente de Matias y el programa llegó con tres actividades. | El registro muestra `POST /agentes/matias` → `200`: el coordinador se llamó a sí mismo por A2A, o sea que el cliente interno sí envía la clave. Evidencia: `01-acceso-permitido.txt`. |

### Prueba 2 · Sin clave

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| LOCAL · 2026-11-13 10:17 | `POST /panel/consultar` sin la cabecera `X-API-Key` | `401` con `{"detail": …}` en español | `401` `{"detail":"Falta la clave de acceso. Envíala en la cabecera X-API-Key."}` | El registro guarda `acceso rechazado · POST /panel/consultar · sin clave`, sin la clave. Evidencia: `02-acceso-rechazado.txt`. |

### Prueba 3 · Clave incorrecta

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| LOCAL · 2026-11-13 10:17 | `POST /panel/consultar` con `X-API-Key: clave-incorrecta` | `401` con `{"detail": …}` | `401` `{"detail":"La clave de acceso es incorrecta."}` | La respuesta no repite la clave enviada. Evidencia: `02-acceso-rechazado.txt`. |

### Prueba 4 · JSON-RPC A2A sin clave

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| LOCAL · 2026-11-13 10:17 | `POST /agentes/matias` y `POST /` (`SendMessage`, cabecera `A2A-Version: 1.0`) sin clave | `401`: también quedan protegidos el agente y el coordinador | `401` en ambos, con el mismo `{"detail": …}` | Cubre los endpoints A2A, no solo el panel. Evidencia: `02-acceso-rechazado.txt`. |

### Prueba 5 · Pregunta vacía

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| LOCAL · 2026-11-13 10:17 | `POST /panel/consultar` con clave correcta y `{"texto": "   "}` | `400` | `400` `{"detail":"Escribe una pregunta para continuar."}` | El `400` ya existía en `panel.py`; solo se verificó. Evidencia: `03-pregunta-vacia.txt`. |

### Prueba 6 · Rutas públicas

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| LOCAL · 2026-11-13 10:17 | `GET /salud`, `GET /agentes/matias/.well-known/agent-card.json` y `GET /.well-known/agent-card.json`, sin clave | `200` en las tres | `200` en las tres | Las lecturas siguen públicas. Evidencia: `04-rutas-publicas.txt`. |

### Prueba 7 · Falla del proveedor (clave de Gemini inválida a propósito)

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| LOCAL · 2026-11-13 10:18 | Instancia aparte en el puerto 8001 con `GOOGLE_API_KEY=clave-invalida-a-proposito`; `POST /panel/consultar` con la clave de acceso correcta | `502` con mensaje entendible, sin traza ni claves | `502` `{"detail":"No se pudo consultar al agente: La clave de Gemini (GOOGLE_API_KEY) no es válida. Revísala en el .env o en las Config Vars de Heroku."}` | No se presentó como respuesta exitosa. El registro conserva el detalle técnico (`INVALID_ARGUMENT … API key not valid`) sin ninguna clave. Evidencia: `05-falla-del-proveedor.txt`. |

### Prueba 8 · Sin conexión

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| LOCAL · 2026-11-13 10:19 | Instancia aparte en el puerto 8002 con un proxy inexistente solo para internet (`HTTPS_PROXY=http://127.0.0.1:9`, `NO_PROXY=127.0.0.1`); `POST /panel/consultar` con clave correcta | `502` con mensaje entendible | `502` `{"detail":"No se pudo consultar al agente: No hay conexión con Gemini o con uno de los agentes. Revisa la conexión a internet e intenta de nuevo."}` | La falla se simuló, no se desconectó el internet. Tardó unos 47 s en rendirse (reintentos del cliente de Gemini). Evidencia: `06-sin-conexion.txt`. |

### Prueba 9 · Servidor sin `CLAVE_API`

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| LOCAL · 2026-11-13 10:20 | Instancia aparte en el puerto 8003 con `CLAVE_API` vacía; `POST /panel/consultar` con `X-API-Key: cualquiera` | Aviso al arrancar y consulta rechazada: la app no queda abierta | Al arrancar: `ERROR … CLAVE_API está vacía: el servidor rechaza todas las consultas (503)…`. La consulta dio `503` con el detalle «El servidor no tiene configurada la clave de acceso (CLAVE_API)…». `/salud` siguió en `200`. | Se eligió avisar y rechazar, no impedir el arranque, para que `/salud` siga sirviendo al diagnosticar (por ejemplo en Heroku). Evidencia: `07-registro-del-servidor.txt`. |

### Prueba 10 · Pruebas automáticas

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| LOCAL · 2026-11-13 | `python -m pytest` desde `taller-02-c2/proyecto` | Todas pasan, sin usar la clave de Gemini | `166 passed` (114 existentes + 52 nuevas) | Incluye: sin clave → 401, clave mala → 401, clave correcta con texto vacío → 400, fichas y `/salud` sin clave → 200, la clave no sale hacia otras direcciones, y una falla de Gemini → 502. |

## 6. Evidencias

Salidas de `curl` guardadas tal cual en `evidencias/matias/`, con la clave de acceso
enmascarada (`********`):

- `01-acceso-permitido.txt`
- `02-acceso-rechazado.txt`
- `03-pregunta-vacia.txt`
- `04-rutas-publicas.txt`
- `05-falla-del-proveedor.txt`
- `06-sin-conexion.txt`
- `07-registro-del-servidor.txt`

Verifiqué que ninguna clave real, ni la de acceso ni la de Gemini, aparece en las
evidencias, en los registros ni en el código.

## 7. Límites y pendientes

- Hay una sola clave para todas las personas, sin límite de intentos ni bloqueo.
- La conexión en local es HTTP; en Heroku la plataforma entrega HTTPS.
- **Pendiente para la integración:** el frontend de Eduardo tiene que enviar la clave en la
  cabecera `X-API-Key` y mostrar el `detail` de los errores 400, 401, 502 y 503. Con la
  clave mala o ausente hoy recibiría `401`; con el servidor sin `CLAVE_API`, `503`.
- **Pendiente para Heroku (Sebastián):** definir `CLAVE_API` en las Config Vars. Sin ella, el
  servidor arranca pero rechaza toda consulta con `503`.
