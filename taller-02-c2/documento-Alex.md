# Documento · Alex · Taller 2 · Base del proyecto e integración

Grupo 5 · ramas `c2t2/alex-base` e `c2t2/alex-integracion`.

**Entorno: LOCAL · Fecha: 2026-11-13.** Todo lo de este documento se probó en mi computador,
en LOCAL. **Nada se probó ni se desplegó en Heroku**, y nada está rotulado como producción.

## 1. Mi rol

Según el reparto del grupo: **la base del proyecto y la integración.**

- **Base** (PR #74): la carpeta `taller-02-c2/`, la app única FastAPI que sirve al coordinador
  y a los cuatro agentes, `.env.example`, `AGENTS.md`, las pruebas de la app, la llamada
  interna del coordinador a los agentes y los archivos de la raíz del repositorio para
  desplegar en Heroku (`Procfile`, `.python-version`, `.slugignore`, `requirements.txt`).
- **Registro y README** (PR #75): el registro A2A legible y el README (instalación,
  configuración, cómo iniciar, probar y detener, cómo funciona).
- **Integración**: revisé los PR #76 (Matías, seguridad y errores) y #77 (Eduardo, frontend),
  los junté en una rama aparte, comprobé que juntos pasan las pruebas, hice los arreglos
  chicos que salieron de la revisión (PR #78) y uní los tres en ese orden: #76, #77 y #78.
- **Mis evidencias**: este documento, el script que toma las capturas, las nueve capturas y
  el registro del servidor, en `evidencias/alex/`.

## 2. Cómo se construyó

**Herramienta usada:** Claude Code (asistente de programación de Anthropic), en Linux Mint.
Yo di las instrucciones, aprobé los cambios y revisé los resultados; el asistente escribió el
código, corrió las pruebas y redactó los borradores de los documentos. También escribió el
script de capturas (`capturar_evidencias.py`) a partir de mi instrucción de tomarlas de forma
automática.

## 3. Prompts que usé

**Pendiente.** Las instrucciones que di a Claude Code deben quedar en
[`evidencias/alex/prompts.md`](evidencias/alex/prompts.md), pegadas textuales, y hoy ese
archivo está **vacío** (solo tiene el título y la nota). **No se inventó ningún prompt.** Esta
sección se completa citándolos tal cual cuando el archivo esté lleno.

## 4. Decisiones de la base y por qué

| Decisión | Por qué |
| --- | --- |
| **Una sola app** con el coordinador en la raíz y los cuatro agentes en rutas `/agentes/{nombre}` (matias, alex, eduardo, sebastian), cada uno con su ficha en `/agentes/{nombre}/.well-known/agent-card.json` y su JSON-RPC. | Heroku entrega a cada aplicación **un solo proceso web y un solo puerto público**. Cinco servidores, como en el taller anterior, habrían exigido cinco apps, cinco despliegues y cinco direcciones sincronizadas. Con una sola hay un despliegue, una variable `URL_BASE` y un solo lugar donde mirar los registros. El protocolo A2A no cambia: el coordinador sigue leyendo fichas y hablando JSON-RPC con cada agente. |
| **Rutas registradas en la misma app, no sub-apps montadas** (`registrar_agente` en `src/comun/servidor.py`). | Con una sub-app montada, el POST a `/agentes/alex` (la dirección exacta que publica la ficha) respondía **307**, una redirección a `/agentes/alex/`, y el cliente A2A **no la sigue**. Con rutas propias responde 200 directamente. |
| **El coordinador descubre las fichas en la primera pregunta, no al arrancar.** Reutiliza el candado de inicialización que ya tenía. | Las fichas las sirve esta misma app; durante el arranque sus rutas todavía no responden y el coordinador se habría quedado pegado. Si en esa primera pregunta no responde ningún agente, no se marca como inicializado y la siguiente pregunta lo reintenta. |
| **Llamada interna por `http://127.0.0.1:{puerto}/agentes/{nombre}`** cuando `URLS_AGENTES` está vacía. Las fichas públicas siguen mostrando `URL_BASE`. El puerto sale de `PORT` (lo asigna Heroku) o, si no existe, de `PUERTO` del `.env` (por defecto 8000). | Si el coordinador llamara a los agentes por la dirección pública, cada pregunta saldría a Internet y volvería a entrar **dos veces por el router de Heroku, que corta las peticiones a los 30 segundos**. Por dentro no hay ese límite. Con `URLS_AGENTES` con valores se vuelve al modo distribuido del taller anterior, sin tocar el código. |
| **`WEB_CONCURRENCY=1`** en Heroku. | La memoria de la conversación y el almacén de tareas A2A viven en la **RAM de cada proceso**. Con varios procesos, cada pregunta podría caer en una copia con otra memoria y el chat perdería el hilo. |
| **Archivos de despliegue en la raíz del repositorio**: `Procfile` (`cd taller-02-c2/proyecto && uvicorn app:app --host 0.0.0.0 --port $PORT`), `requirements.txt` (`-r taller-02-c2/proyecto/requirements.txt`), `.python-version` (3.12) y `.slugignore`. | Heroku **solo lee la raíz** del repositorio, y el proyecto vive en una subcarpeta. El `.slugignore` deja fuera las otras carpetas de talleres, las evidencias, los PDF y las imágenes. Ese `requirements.txt` de la raíz ya existía del Curso 1 (con `jupyter` y `nbstripout`); lo reemplacé con mi autorización, porque Heroku instala lo que diga ese archivo. |
| **Registro A2A legible** con `logging`, en la salida estándar y con fecha y hora: una línea por paso de cada consulta. | Permite seguir en la terminal de uvicorn, y en `heroku logs`, qué pasó con cada pregunta: pregunta recibida (máximo 80 caracteres), agente elegido y su motivo, envío A2A y respuesta con su tiempo, o el error en una línea. Nunca registra claves ni cabeceras. |

## 5. La revisión de integración

Revisé #76 y #77 en copias temporales, sin tocar las ramas de mis compañeros, y los junté (main +
#76 + #77) para ver si convivían. **No hubo conflictos** y juntos pasaron las pruebas.

**Lo que estaba bien** (lo comprobé, no lo supuse):

- La clave `CLAVE_API` solo se envía a la propia app (`127.0.0.1` y el puerto real), nunca a
  direcciones de terceros del modo distribuido: probado con ocho destinos distintos.
- La clave se compara con `secrets.compare_digest` y aparece **0 veces** en los registros.
- En el navegador la clave vive solo en una variable de JavaScript: sin `localStorage`, sin
  `sessionStorage`, sin cookies y sin quedar escrita en el HTML.
- Las 14 imágenes de evidencias de Eduardo no muestran claves, correos, rutas de usuario, IP
  públicas ni notificaciones; ni el historial de los dos PR tiene secretos.

**Lo que se encontró y se arregló** (PR #78):

| Hallazgo | Arreglo |
| --- | --- |
| El frontend **no leía el campo `detail`** del servidor: mostraba un texto fijo por código, así que la persona no veía, por ejemplo, «La clave de Gemini no es válida». | `panel.html` muestra el `detail` en los errores 400, 502 y 503, y en el aviso del 401, solo si la respuesta es JSON y un texto de hasta 300 caracteres, siempre como texto (nunca como HTML). Si no, usa el texto fijo. Agregué 9 comprobaciones nuevas. |
| El 503 decía «No se pudo consultar al proveedor o al agente». Un 503 significa que **falta `CLAVE_API` en el servidor**: es un problema de configuración, no del proveedor. | Texto propio del 503: «El servidor no está configurado para recibir consultas (falta su clave de acceso)…». |
| Si falta `GOOGLE_API_KEY` (el error típico al desplegar), Gemini respondía en inglés y salía un texto largo sin traducir. | `errores.py` reconoce esa frase y muestra «Falta configurar la clave de Gemini (GOOGLE_API_KEY) en el .env o en las Config Vars.». |
| El registro A2A (mío) **perdía líneas** en consolas de Windows con la salida redirigida: «→», «←» y «✗» no caben en cp1252 y fallaban con `UnicodeEncodeError`. Lo detectó Eduardo y lo reproduje. | La salida se tolera: los caracteres que no caben se escapan en vez de perder la línea. Con una prueba. |
| Las comprobaciones del frontend de Eduardo necesitan Playwright y Chrome, que no estaban declarados en ninguna parte. | `requirements-dev.txt` (opcional; Heroku no lo usa) y, en el README, cómo instalarlo y el comando exacto. |
| Dos pruebas de autorización estaban marcadas `xfail` («pendiente de Matías»). | Con el control de acceso integrado pasan; quité la marca y renombré la prueba. |
| El modo distribuido no funciona con agentes remotos que exijan su propia clave: no les enviamos la nuestra, a propósito. | No es un fallo: lo anoté en «Límites conocidos» del README. |

También hubo un tropiezo de proceso: tras unir #76 y #77, GitHub marcó el #78 como
«con conflictos» aunque en local la unión era limpia (las dos ramas traían uniones distintas
de los mismos commits). Se resolvió trayendo `main` a la rama de integración, y después se unió.

Resultado: `pytest` pasó de 166 a **168** pruebas, y las comprobaciones del frontend, de 44
más 2 `xfail` a **55** aprobadas.

## 6. Pruebas

Las capturas **se tomaron automáticamente**, no a mano. El script
[`evidencias/alex/capturar_evidencias.py`](evidencias/alex/capturar_evidencias.py) levantó la
app igual que Heroku (desde la raíz del repositorio, con el comando del `Procfile` y
`PORT=8000`), con una `CLAVE_API` temporal que vivió solo en el entorno del proceso, y con
Chrome sin ventana visible (Playwright, 1280x900) tomó las capturas **contra la app real**.
Cómo repetirlas: [`evidencias/alex/GUION.md`](evidencias/alex/GUION.md).

**Qué es real y qué no.** Las seis preguntas son **reales a Gemini**; la app, el coordinador,
la comunicación A2A y el registro son los de verdad. **Nada está simulado.** Los datos que
devuelven los agentes (recintos, programas, menús y costos) son ficticios por diseño, y las
respuestas del modelo pueden variar si se repite la corrida.

**Qué agrega el script a las imágenes** (no es parte de la app): una franja arriba con la
fecha y la hora de cada captura, y la expansión del área de conversación (solo estilo, sin
cambiar el contenido) para que la respuesta completa, con el agente y el motivo, quepa en la
imagen. La hora de la franja es la de la captura, después de recibir la respuesta.

Cada prueba cita las líneas del registro del servidor
([`registro-local.txt`](evidencias/alex/registro-local.txt)) que le corresponden.

### Prueba 1 · La app responde: `/salud`

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| LOCAL · 2026-11-13 · captura automática con Playwright contra la app real | `GET http://127.0.0.1:8000/salud`, sin clave, con la app levantada con el comando del `Procfile` desde la raíz del repositorio. | `200` y `{"ok": true}`: la ruta es pública. | `{"ok":true}`. Imagen `01-salud.png`. Registro: `INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)` y `INFO:     127.0.0.1:45994 - "GET /salud HTTP/1.1" 200 OK`. | Franja de las 19:57:07. El primer `GET /salud` del registro (puerto 45978) es la comprobación con que el script espera a que la app esté lista. |

### Prueba 2 · Pantalla de ingreso

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| LOCAL · 2026-11-13 · captura automática con Playwright contra la app real | `GET /` y escribir la `CLAVE_API` temporal en el campo de ingreso, sin enviarla. | El panel carga y pide la clave; **la clave no se ve** (el campo es de tipo *password*). | La pantalla «Ingresa tu clave de acceso» con el campo lleno de puntos y «Sin clave cargada» arriba a la derecha. Imagen `02-ingreso.png`. Registro: `INFO:     127.0.0.1:45994 - "GET / HTTP/1.1" 200 OK`. | Franja de las 19:57:08. La clave es temporal, solo existió en el entorno del proceso y no aparece en ningún archivo. |

### Prueba 3 · Intento con clave incorrecta

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| LOCAL · 2026-11-13 · captura automática con Playwright contra la app real | Ingresar `clave-incorrecta-de-prueba` y enviar la pregunta de la prueba 4a. | `401` antes de llamar a ningún agente; el panel vuelve al ingreso y muestra el `detail` del servidor. | «Acceso rechazado (401). La clave de acceso es incorrecta. Ingresa una clave válida. Tu pregunta se conserva para reintentar.» Imagen `03-clave-incorrecta.png`. Registro: `2026-11-13 19:57:08 WARNING [coordinador] acceso rechazado · POST /panel/consultar · clave incorrecta` y `INFO:     127.0.0.1:46002 - "POST /panel/consultar HTTP/1.1" 401 Unauthorized`. | Franja de las 19:57:08. No se llamó a Gemini. La clave incorrecta enviada no aparece en el registro (0 veces). El texto del `detail` es el arreglo del frontend del PR #78. |

### Prueba 4a · Pregunta al agente de Matías (programa)

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| LOCAL · 2026-11-13 · captura automática con Playwright contra la app real | `Necesito armar el programa de una feria infantil de 3 horas desde las 15:00.` con la clave correcta, en una conversación nueva. | El supervisor elige al agente de Matías y responde un programa con horas desde las 15:00; se ven la pregunta, la respuesta, el agente y el motivo. | **Agente: Agente de Matias.** Motivo: «El usuario solicita armar el programa de actividades para una feria infantil.» Programa de 15:00 a 17:25 (Pintacuentos, Taller de globoflexia, Show de magia y Carrera de sacos), «hay 35 minutos libres» y el aviso de que es solo una propuesta. Imagen `04a-matias-programa.png`. Registro: `19:57:08 INFO [coordinador] pregunta recibida · context_id=793ff1ce-e573-495e-a602-5db88ed86757 · «Necesito armar el programa de una feria infantil de 3 horas desde las 15:00.»`; `19:57:08 … catálogo listo · 4 agente(s): Agente de Matias, Agente de Alex, Agente de Eduardo, Agente de Sebastian`; `19:57:10 … supervisor eligió Agente de Matias · motivo: El usuario solicita armar el programa de actividades para una feria infantil.`; `19:57:10 … A2A → http://127.0.0.1:8000/agentes/matias · enviando`; `19:57:14 … A2A ← Agente de Matias · respuesta recibida en 4,1 s`. | Franja de las 19:57:15. La línea `catálogo listo` aparece en esta primera pregunta: el coordinador descubrió las fichas ahí y no al arrancar. El envío A2A va a `127.0.0.1`, no a Internet, y la respuesta fue `POST /agentes/matias … 200 OK`: la clave sí llegó a la ruta interna. |

### Prueba 4b · Pregunta al agente de Alex (recintos)

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| LOCAL · 2026-11-13 · captura automática con Playwright contra la app real | `Necesito un recinto interior para una feria tecnológica de 80 personas.` | Se elige al agente de Alex; hasta tres recintos con sus cifras y el aviso de que la disponibilidad la confirma una persona. | **Agente: Agente de Alex.** Motivo: «El usuario solicita la recomendación de un recinto interior con capacidad para 80 personas.» Tres recintos: Colegio Villa Cuarzo (120 personas, ocupación 66,7 %, 450 m², accesible), Salón Cumbre del Hotel Alto Quillay (180, 44,4 %, 300 m², accesible) y Galpón Cultural Rinconada Azul (250, 32,0 %, 600 m², no accesible, con el aviso «queda grande»). Cierra con «Datos ficticios. La disponibilidad y el aforo legal los confirma una persona con el recinto.» Imagen `04b-alex-recintos.png`. Registro: `19:57:15 … pregunta recibida · context_id=9b949a99-180e-4e03-a9fa-3f61091c9e75 · «Necesito un recinto interior para una feria tecnológica de 80 personas.»`; `19:57:17 … supervisor eligió Agente de Alex · motivo: El usuario solicita la recomendación de un recinto interior con capacidad para 80 personas.`; `19:57:17 … A2A → http://127.0.0.1:8000/agentes/alex · enviando`; `19:57:21 … A2A ← Agente de Alex · respuesta recibida en 4,6 s`. | Franja de las 19:57:22. Los recintos y las cifras son datos ficticios del agente. |

### Prueba 4c · Pregunta al agente de Eduardo (presupuesto)

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| LOCAL · 2026-11-13 · captura automática con Playwright contra la app real | `¿Cuál es el presupuesto simulado de una feria tecnológica para 80 personas y 4 horas?` | Se elige al agente de Eduardo; partidas en CLP, contingencia, total y la advertencia de que son importes ficticios. | **Agente: Agente de Eduardo.** Motivo: «Se encarga de estimar presupuestos simulados para ferias y eventos.» Partidas (recinto referencial $800.000, personal $768.000, equipamiento $200.000, alimentación genérica $144.000 y logística $64.000), subtotal $1.976.000, contingencia del 10 % ($197.600) y **total $2.173.600 CLP**; supuestos y la advertencia «importes completamente ficticios… Impuestos no modelados». Imagen `04c-eduardo-presupuesto.png`. Registro: `19:57:22 … pregunta recibida · context_id=b9e239c8-6712-4297-ae63-040792bbd6a9 · «¿Cuál es el presupuesto simulado de una feria tecnológica para 80 personas y 4…»`; `19:57:24 … supervisor eligió Agente de Eduardo · motivo: Se encarga de estimar presupuestos simulados para ferias y eventos.`; `19:57:24 … A2A → http://127.0.0.1:8000/agentes/eduardo · enviando`; `19:57:28 … A2A ← Agente de Eduardo · respuesta recibida en 4,4 s`. | Franja de las 19:57:28. En el registro la pregunta aparece recortada a 80 caracteres, por diseño. El total coincide con el de las pruebas reales anteriores de Eduardo. |

### Prueba 4d · Pregunta al agente de Sebastián (catering)

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| LOCAL · 2026-11-13 · captura automática con Playwright contra la app real | `Necesito una propuesta de catering para una feria tecnológica de 80 personas, de 4 horas, comenzando a las 10:00. Hay 10 personas vegetarianas y otras 5 que requieren comida sin gluten.` | Se elige al agente de Sebastián; servicios con su hora, cantidades por dieta y agua. | **Agente: Agente de Sebastian.** Motivo: «La solicitud pide una propuesta de catering con especificaciones de alimentación y restricciones dietéticas.» Coffee break a las 11:00 y box lunch a las 13:30, con menús general (65 personas), vegetariano (10) y sin gluten (5), **88 litros de agua** y una nota de que es una propuesta orientativa, sin precios, que no contrata proveedores. Imagen `04d-sebastian-catering.png`. Registro: `19:57:28 … pregunta recibida · context_id=a5ea21d7-fe2c-4792-bfec-5b66598cf832 · «Necesito una propuesta de catering para una feria tecnológica de 80 personas, d…»`; `19:57:30 … supervisor eligió Agente de Sebastian · motivo: La solicitud pide una propuesta de catering con especificaciones de alimentación y restricciones dietéticas.`; `19:57:30 … A2A → http://127.0.0.1:8000/agentes/sebastian · enviando`; `19:57:35 … A2A ← Agente de Sebastian · respuesta recibida en 4,4 s`. | Franja de las 19:57:35. Las cantidades son datos ficticios del agente. |

### Prueba 5 · Pregunta que no es de nadie («ninguno»)

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| LOCAL · 2026-11-13 · captura automática con Playwright contra la app real | `¿Cómo resuelvo una integral cuadrática?` | El supervisor responde «ninguno» y **no delega** a ningún agente. | «No tengo un agente para eso. Puedo ayudarte con: Agente de Matias, Agente de Alex, Agente de Eduardo, Agente de Sebastian.» **Agente: ninguno.** Motivo: «La pregunta es sobre matemáticas y no corresponde a las funciones de ningún agente del catálogo.» Imagen `05-ninguno.png`. Registro: `19:57:35 … pregunta recibida · context_id=3143281b-4d4c-4b84-a189-3442cca1e945 · «¿Cómo resuelvo una integral cuadrática?»` y `19:57:37 … supervisor eligió ninguno · motivo: La pregunta es sobre matemáticas y no corresponde a las funciones de ningún agente del catálogo.` | Franja de las 19:57:37. **No hay líneas `A2A →` ni `A2A ←`** para esta pregunta, como corresponde: no se llamó a ningún agente. |

### Prueba 6 · Pregunta con datos faltantes

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| LOCAL · 2026-11-13 · captura automática con Playwright contra la app real | `¿Dónde hago una feria?` (sin tipo de feria ni cantidad de personas). | El agente **pide el dato antes de concluir**: no recomienda ningún recinto todavía. | **Agente: Agente de Alex.** Motivo: «El usuario solicita recomendaciones de lugares para hacer una feria.» Respuesta: «Para poder buscarte los mejores recintos, dime de qué tipo será la feria (por ejemplo: tecnológica, gastronómica, cultural o infantil) y cuántas personas esperas que asistan.» Imagen `06-datos-faltantes.png`. Registro: `19:57:38 … pregunta recibida · context_id=53fdda0f-b2db-4bf7-8801-7e54f727f50b · «¿Dónde hago una feria?»`; `19:57:39 … supervisor eligió Agente de Alex · motivo: El usuario solicita recomendaciones de lugares para hacer una feria.`; `19:57:39 … A2A → http://127.0.0.1:8000/agentes/alex · enviando`; `19:57:41 … A2A ← Agente de Alex · respuesta recibida en 1,6 s`. | Franja de las 19:57:41. Es el comportamiento que pide la regla del agente de Alex: si falta el tipo de evento o la cantidad de personas, pregunta antes de consultar. El registro no dice si se llamó a la herramienta de recintos; lo que se ve es la respuesta. No se contestó esa pregunta: habría sido una séptima pregunta real. |

### Prueba 7 · El registro del servidor (`registro-local.txt`)

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| LOCAL · 2026-11-13 · captura automática con Playwright contra la app real | Revisar `registro-local.txt` al detener la app. | El arranque; las líneas A2A de cada pregunta; la clave **0** veces; ninguna ruta con mi usuario; ninguna IP pública. | Arranque con `Started server process`, `Application startup complete.` y `Uvicorn running on http://0.0.0.0:8000`. **10 líneas A2A** (`A2A →` y `A2A ←` de las 5 preguntas que se delegaron a un agente) más las del supervisor de las 6. Clave: **0** apariciones. Rutas con el usuario: **0** (el script no tuvo que reemplazar ninguna por `<carpeta-del-repo>`). IP distintas de `127.0.0.1` y `0.0.0.0`: **0**. Además, `POST /agentes/{nombre} … 200 OK` para cada agente. Archivo `registro-local.txt`. | Las primeras líneas (con `#`) las escribe el script: el comando y la fecha. El resto es la salida del servidor tal cual. Aparece un `GET /favicon.ico … 404`: el navegador lo pide y la app no tiene ícono; es inofensivo. |

### Prueba 8 · Pruebas automáticas

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| LOCAL · 2026-11-13 (no son capturas) | `python -m pytest` desde `taller-02-c2/proyecto`, sin la clave de Gemini; y `pytest ../evidencias/eduardo/test_panel_eduardo.py -v -rx` con `requirements-dev.txt` instalado. | Todas pasan. | `168 passed` en el proyecto y `55 passed` en las comprobaciones del frontend. | Las del proyecto no usan Gemini. Las del frontend usan Chrome real, pero con **respuestas del servidor simuladas** (así lo declara Eduardo en su documento); no sustituyen a las capturas de arriba. Las comprobaciones del frontend son opcionales. |

## 7. Evidencias

En `taller-02-c2/evidencias/alex/`:

- `01-salud.png`, `02-ingreso.png`, `03-clave-incorrecta.png`
- `04a-matias-programa.png`, `04b-alex-recintos.png`, `04c-eduardo-presupuesto.png`,
  `04d-sebastian-catering.png`
- `05-ninguno.png`, `06-datos-faltantes.png`
- `registro-local.txt`: la salida completa del servidor de esa corrida
- `capturar_evidencias.py` y `GUION.md`: cómo se tomaron y cómo repetirlas
- `prompts.md`: **vacío**, pendiente (ver la sección 3)

Revisé cada imagen a tamaño completo: se ve lo que pide el guion y no aparecen claves (el
campo de ingreso se ve con puntos), correos, rutas con mi nombre de usuario, direcciones IP
públicas ni notificaciones.

## 8. Límites y pendientes

**Dicho tal cual:**

- **Todo es LOCAL.** No se probó ni se desplegó nada en Heroku; **la sección «Operación en
  Heroku» del README y el despliegue siguen pendientes (Sebastián).** Que la app arranque con
  el comando del `Procfile` en mi computador no demuestra que funcione en Heroku.
- **Las capturas son automáticas**, no las tomó una persona. Llevan la franja y el área de
  conversación expandida que agrega el script. El script solo funciona en Linux y macOS.
- **`prompts.md` está vacío**: la sección 3 queda pendiente hasta que yo pegue mis
  instrucciones, textuales.
- **Las respuestas de Gemini varían** entre corridas, y los datos de los agentes son ficticios.
- **Eduardo tiene pendientes suyos:** ejecutar de verdad el acceso permitido y rechazado desde
  su frontend contra la app integrada (R05–R07 y R09 de su documento), actualizar sus
  secciones 3 y 5 (aún describen la protección de Matías como no integrada) y decidir qué hacer
  con `src/agente_eduardo/demo.html`, que ya no se sirve. Mis capturas 02 y 03 muestran el
  ingreso y el rechazo con la app real, pero no reemplazan su validación.
- **Límites de la base:** la memoria del chat vive en la RAM del servidor (se pierde al
  reiniciar o cuando Heroku duerme la app y obliga a `WEB_CONCURRENCY=1`); hay una sola clave
  de acceso para todas las personas; el modo distribuido no funciona con agentes remotos que
  exijan su propia clave. Están anotados en «Límites conocidos» del README.
