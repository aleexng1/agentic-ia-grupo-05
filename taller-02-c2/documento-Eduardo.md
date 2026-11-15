# Eduardo Basaure · Frontend · Taller 2 del Curso 2 · Grupo 5

**Estado vigente: LOCAL · 2026-11-14 · Rama `c2t2/eduardo-frontend` ·
publicado en los commits `d8cce13` y `2b754e2` · [PR #82](https://github.com/aleexng1/agentic-ia-grupo-05/pull/82) unido a `main` el 2026-11-15.**

## 1. Continuación vigente: pendientes locales completados

Se comprobó la rama, `HEAD`, el índice y el estado de trabajo antes de editar.
`git ls-remote origin refs/heads/c2t2/eduardo-frontend` confirmó **`d8cce13` publicado**.
El PR #82 ya existe, según la actualización de Eduardo: **no está pendiente abrirlo
ni hacer commit/push del cierre integrado anterior**. Esta continuación se publicó
después en el commit `2b754e2` del mismo PR, que se unió a `main` el 2026-11-15.

**Resultado:** R08 y R10 aprobados con la app LOCAL real; R11 y R12 aprobados como
**fallas inducidas en un entorno controlado**, sin proveedor y sin Heroku. Además se
hicieron **tres consultas funcionales reales**, una a cada agente de Matías, Alex y
Sebastián, desde el panel actual protegido. Las tres devolvieron 200, agente y motivo.
No se reenviaron esas preguntas ni se sustituyeron respuestas HTTP.

**Entorno de estas comprobaciones:** Windows, Python **3.12.10**, Playwright **1.65.1**,
httpx **0.28.1**, Chrome **157.0.8103.78** sin ventana, vista de 1280 × 960 y procesos
propios en loopback. Casos ejecutados entre **14:50:56 y 15:05:37, UTC−03:00**, del
**14-11-2026**, en tres fases con incidencias instrumentales descritas en la sección 4.
Se reutilizó `.venv`, sin cambiar dependencias. El código de producción no cambió;
**no se repitieron las suites completas** de 168 y 68 pruebas ya aprobadas.

Carpeta nueva, sin sobrescribir evidencias anteriores:
[`pendientes-locales-2026-11-14-144554/`](evidencias/eduardo/pendientes-locales-2026-11-14-144554/README.md).
El [índice consolidado](evidencias/eduardo/pendientes-locales-2026-11-14-144554/resultados-consolidados.json)
identifica la procedencia de cada resultado; no se presenta como un registro primario
generado por la primera ejecución incompleta.

Al inicio solo existía la foto sin seguimiento del Taller 1. Se conservaron `.env`,
esa foto, la demo del Taller 1 y todas las capturas históricas. Había un servidor previo
en **127.0.0.1:8000, PID 3772**, iniciado el 13-11-2026: **no se detuvo ni reinició** y
siguió escuchando con el mismo PID al terminar. La configuración de puertos, direcciones
internas y clave temporal se pasó solo a procesos hijos, sin editar `.env` ni Heroku.

## 2. R08, R10, R11 y R12 · resultados vigentes

Todas las fechas de esta tabla son **2026-11-14, UTC−03:00**. Los valores de las claves
no se guardaron; se usó autorización temporal válida en los servidores propios.

| Caso / entorno / fecha | Solicitud | Resultado esperado | Resultado obtenido y evidencia | Observaciones |
| --- | --- | --- | --- | --- |
| **R08 · app LOCAL integrada · 14:50:56** | POST autorizado con `{"texto":"   ","context_id":"r08-espacios-protegido"}`; luego `{"context_id":"r08-sin-texto-protegido"}` | **400** para espacios y **422** sin `texto`, antes del coordinador | **400**, `Escribe una pregunta para continuar.`; **422**, validación estándar en `body.texto`. Antes de las consultas reales: **0 preguntas al coordinador y 0 envíos A2A**. [Captura](evidencias/eduardo/pendientes-locales-2026-11-14-144554/r08-entrada-protegida.png), [log](evidencias/eduardo/pendientes-locales-2026-11-14-144554/servidor-integrado-consultas.txt) | HTTP real con httpx; el formulario impide enviar espacios. La imagen rotula la visualización del cliente HTTP, **no un aviso nativo del panel**. La consolidación transcribe el cuerpo visible de esa captura; el primer ejecutor no guardó su JSON final. El 422 incluye `Field required`, sin traza. |
| **R10 · app LOCAL de ensayo propia · 15:05:17–15:05:33** | Cargar el panel; detener solo su servidor propio; enviar «Comprobación LOCAL R10: ¿puedes recibir esta pregunta?» | Aviso de conexión, pregunta conservada y controles recuperados; restaurar el servidor después | **`net::ERR_CONNECTION_REFUSED`** y «No se pudo conectar con el servidor. Revisa tu conexión y que la aplicación esté encendida.»; pregunta conservada y envío/sugerencias habilitados. [Desconexión](evidencias/eduardo/pendientes-locales-2026-11-14-144554/finalizacion/r10-desconexion-real.png), [restauración](evidencias/eduardo/pendientes-locales-2026-11-14-144554/finalizacion/r10-restaurado.png), [resultado](evidencias/eduardo/pendientes-locales-2026-11-14-144554/finalizacion/r10-resultado.json) | Se detuvo únicamente el árbol del PID propio **25448**, servidor **25892**, puerto **54738**. Se restauró en **el mismo puerto**, servidor **21636**: `/salud` 200, panel 200 y POST autorizado con espacios 400. Después de comprobar la restauración se cerraron solo los procesos propios. No se cortó la red del equipo ni se tocó el puerto 8000. |
| **R11 · ensayo LOCAL aislado · 15:00:08–15:01:18** | Mantener pendiente «Ensayo aislado R11: mantener esta consulta pendiente durante 70 segundos reales.»; tras el aviso, iniciar otra conversación y consultar al ensayo | Timeout tras **más de 65 s reales**, recuperación y ausencia de la respuesta anterior en la conversación nueva | Aviso «La consulta superó los 65 segundos de espera…» tras **65,471770 s reales**; servidor demoró **70,009151 s**. Pregunta conservada, controles recuperados, contexto nuevo y respuesta vieja ausente. [Espera](evidencias/eduardo/pendientes-locales-2026-11-14-144554/complemento/r11-espera-real-inducida.png), [timeout](evidencias/eduardo/pendientes-locales-2026-11-14-144554/complemento/r11-timeout-real-inducido.png), [conversación nueva](evidencias/eduardo/pendientes-locales-2026-11-14-144554/complemento/r11-nueva-sin-respuesta-vieja.png), [mediciones](evidencias/eduardo/pendientes-locales-2026-11-14-144554/complemento/r11-resultado.json) | **Falla inducida en entorno controlado, no falla real de Gemini ni Heroku**. Sin reloj virtual, interceptación HTTP ni cambio del límite de 65 s. El navegador abortó; el servidor generó la respuesta vieja a los 70 s, pero no se entregó a la conversación nueva. No se obligó a `fetch` a ignorar `AbortSignal`. |
| **R12 · ensayo LOCAL aislado · 15:05:35–15:05:37** | «Ensayo aislado R12: devolver HTML deliberadamente, sin consultar proveedores.»; el servidor devuelve **200 `text/html`**, con un título y un script de ensayo | Aviso no JSON, sin insertar ni ejecutar el HTML; conservar pregunta y recuperar controles | «El servidor devolvió una respuesta que no es JSON. Inténtalo de nuevo; si persiste, avisa al equipo.»; marcador HTML ausente y script no ejecutado. [Captura](evidencias/eduardo/pendientes-locales-2026-11-14-144554/finalizacion/r12-html-controlado.png), [resultado](evidencias/eduardo/pendientes-locales-2026-11-14-144554/finalizacion/r12-resultado.json), [log](evidencias/eduardo/pendientes-locales-2026-11-14-144554/finalizacion/servidor-r12-html.txt) | **Falla inducida en entorno controlado, no falla real de Gemini ni Heroku**. Se sirve el panel intacto por HTTP real. El HTML crudo se conserva mediante **una segunda solicitud httpx** al mismo ensayo, identificada por separado; no se atribuye a una lectura del cuerpo del navegador. No es una prueba del router público de Heroku. |

## 3. Matías, Alex y Sebastián · consultas reales con el panel actual

**Esperado común:** una conversación nueva por caso, autorización válida, HTTP 200,
contrato `respuesta/context_id/agente/motivo`, agente correcto y respuesta/motivo visibles.
**Obtenido común:** aprobado en los tres casos, **un envío y una recepción A2A por agente**;
las respuestas completas, sin resumir ni recalcular, están en los JSON enlazados. Las
capturas muestran Markdown básico del panel actual, pregunta, respuesta, agente y motivo.
Los datos siguen siendo ficticios: «real» describe la llamada a coordinador/A2A/Gemini,
no una reserva, cotización ni contratación real.

### R01-actual · Matías · LOCAL · 14-11-2026 · 14:50:56

- **Solicitud exacta:** «Necesito un programa para una feria cultural familiar de 3 horas,
  desde las 16:00. Indica actividades, horarios y cualquier tiempo libre, con las
  condiciones de demostración.»
- **Obtenido:** **200**, `Agente de Matias`; programa 16:00–18:00 y **60 minutos libres**
  informados, conservados tal como llegaron. Motivo: «El usuario solicita un programa
  detallado de actividades y horarios para una feria cultural.»
- **Evidencias:** [pregunta y respuesta completas](evidencias/eduardo/pendientes-locales-2026-11-14-144554/r01-actual-intercambio.json),
  [captura actual](evidencias/eduardo/pendientes-locales-2026-11-14-144554/r01-actual-consulta-real.png).

### R02-actual · Alex · LOCAL · 14-11-2026 · 14:51:04

- **Solicitud exacta:** «Necesito un recinto interior para una feria tecnológica de 80
  personas. Recomienda opciones con aforo, características, accesibilidad y advertencias
  de disponibilidad; no reserves nada.»
- **Obtenido:** **200**, `Agente de Alex`; **tres recintos**, aforos 120/180/250,
  características, accesibilidad y advertencias de demostración. Motivo: «El usuario
  solicita la recomendación de recintos para una feria, incluyendo capacidad y características.»
- **Evidencias:** [pregunta y respuesta completas](evidencias/eduardo/pendientes-locales-2026-11-14-144554/r02-actual-intercambio.json),
  [captura actual](evidencias/eduardo/pendientes-locales-2026-11-14-144554/r02-actual-consulta-real.png).

### R04-actual · Sebastián · LOCAL · 14-11-2026 · 14:51:13

- **Solicitud exacta:** «Necesito catering para una feria tecnológica de 80 personas,
  de 10:00 a 14:00 (4 horas), con 10 vegetarianas y 5 sin gluten. Indica servicios,
  horarios, dietas y litros de agua; datos simulados, sin contratar nada.»
- **Obtenido:** **200**, `Agente de Sebastian`; servicios **11:00 y 13:30**, dietas
  **65/10/5**, **88 litros de agua**, unidades y advertencias completas. Motivo: «El usuario
  solicita propuestas de comida, horarios, dietas especiales y cantidades de agua para un evento.»
- **Evidencias:** [pregunta y respuesta completas](evidencias/eduardo/pendientes-locales-2026-11-14-144554/r04-actual-intercambio.json),
  [captura actual](evidencias/eduardo/pendientes-locales-2026-11-14-144554/r04-actual-consulta-real.png).

Registro común: [servidor integrado](evidencias/eduardo/pendientes-locales-2026-11-14-144554/servidor-integrado-consultas.txt).
No se guardaron cabeceras de petición, HAR, trazas de navegador ni claves. Las capturas
añaden una franja de procedencia y amplían la altura del chat, sin editar las respuestas.
Las seis capturas del 13-11-2026 permanecen como históricas anteriores al Markdown.
R05 de Eduardo, con el panel actual, ya está documentado en el cierre integrado anterior
y **no se repitió** en esta continuación.

## 4. Instrumental, conservación y comprobaciones

- La primera ejecución terminó por el límite de **360 s del comando**, sin generar su
  `resultados-locales.json`. Se conservaron sus tres intercambios reales, capturas y logs.
  R08 queda respaldado por su captura completa y por el log, con esa limitación explícita.
- En el complemento, R10 se detuvo en un **`ConnectTimeout` del chequeo auxiliar**, antes
  de enviar desde el panel. R12 alcanzó HTTP 200 HTML, pero el instrumental quedó esperando
  `response.text()` sobre un cuerpo que el panel descarta. Esos resultados **no aprobados**
  se conservan en [resultados-complemento.json](evidencias/eduardo/pendientes-locales-2026-11-14-144554/complemento/resultados-complemento.json);
  no se reinterpretan como fallas del panel, de Gemini o de Heroku.
- Se ajustó solo el **instrumental nuevo de evidencias**: control del árbol del PID
  propio en Windows, guardado inmediato por caso, aceptación de los dos errores de
  conexión en el chequeo auxiliar y lectura del HTML por un cliente HTTP adicional.
  R10/R12 se completaron en una fase dirigida; R11 se repitió para conservar también
  mediciones JSON completas. **No se repitieron las tres consultas a los agentes**.
- No se detectó un defecto del frontend y no se editaron `panel.html`, `panel.py`, los
  agentes, seguridad ni archivos de otras personas. No se ejecutaron pytest ni las suites
  completas: se mantienen sus resultados anteriores, identificados por su propia fecha.
- [Revisión final](evidencias/eduardo/pendientes-locales-2026-11-14-144554/revision-final.json):
  conservación de los **90 archivos protegidos** de la línea base, incluido `.env`,
  capturas/logs históricos, foto y demo del Taller 1 y código de producción; comprobación
  de alcance, secretos, enlaces y ausencia de cambios en el índice. No es una auditoría
  integral de seguridad. La línea base con huellas privadas quedó fuera del repositorio.

## 5. Publicación y pendientes que sí permanecen

- El **PR #82 se unió a `main` el 2026-11-15**, después de la revisión de Alex, con el
  cierre integrado (`d8cce13`) y esta continuación (`2b754e2`).
- R08/R10/R11/R12 y las tres consultas con formato actual **ya no están pendientes**.
  R11/R12 solo acreditan manejo del frontend ante fallas **inducidas y controladas**.
- Heroku/HTTPS, su router y el despliegue público siguen fuera del alcance de esta
  validación LOCAL. No se cambiaron Config Vars, despliegues ni procesos remotos.
- Se conserva la observación previa para Matías: un `detail` seguro para el DOM no
  equivale a sanitizar secretos; revisar futuros responders y el `str(error)` genérico
  del backend y las cabeceras de no caché de errores. No se amplió ese alcance.
- La [lista exacta de archivos de esta continuación](evidencias/eduardo/pendientes-locales-2026-11-14-144554/archivos-modificados.txt)
  separa los documentos modificados y las evidencias nuevas. Excluye la foto previa,
  `.env`, `.venv` y cualquier archivo ajeno. No sustituye la selección histórica del commit
  ya publicado. La solicitud real se añadió a [prompts-utilizados.md](evidencias/eduardo/prompts-utilizados.md).

## Histórico conservado · cierre integrado del 14-11-2026

**El siguiente bloque registra la ejecución anterior a esta continuación.** Sus resultados
se publicaron después en **`d8cce13`, PR #82**. Las menciones originales a «sin commit/push»,
«nuevo PR» y pendientes R08/R10/R11/R12 describen ese corte temporal, **no el estado vigente**.
No se sobrescribieron los archivos de sus evidencias.

<details>
<summary>Abrir registro del cierre integrado anterior (13:55, UTC−03:00)</summary>

## 1. Cierre integrado previo (registro original)

Se ejecutaron `git fetch origin` y `git merge --ff-only origin/main`: avance sin
conflictos desde `7047ab8` hasta **`741305bf0fed986b523898114bb1d851d28d063b`**
(PR #79). Esa es la **base probada**, junto con los cambios locales de este cierre,
todavía **sin commit ni push**. No se presenta como si los ajustes ya formaran parte
de ese commit. Las huellas del HTML, la suite y el ejecutor efectivamente probados
están en los dos JSON de resultados de la carpeta nueva.

**Resultado real de esta ejecución:** 168 pruebas del proyecto aprobadas y 68 del
frontend aprobadas, sin fallos ni `xfail`; R05, R06, R07 y R09 aprobados contra
`app:app` LOCAL integrada. Las simulaciones del frontend y las llamadas reales se
identifican por separado más abajo. Los conteos provienen de los registros de pytest,
no de los resultados anteriores ni de la nota de Alex.

Al inicio solo estaba sin seguimiento la foto
`taller-01-c2/evidencias/eduardo/03-ficha-telefono.jpg`: conserva su contenido y queda
fuera de la selección del PR. También se conservan byte por byte `.env`, la demo del
Taller 1 y todas las capturas y registros históricos. No se modificó Heroku ni se
detuvo una app previa: las instancias de validación usaron puertos libres en loopback
y sus propios procesos, que terminaron al finalizar.

## 2. Revisión de Alex y cambios propios

- Se revisó la integración de autorización de Matías, el envío interno de la clave
  por A2A de Alex y sus cambios en `panel.html` y `test_panel_eduardo.py`.
  **La protección ya está integrada**: POST sin clave o con clave incorrecta devuelve
  401 antes del coordinador. V22/V23 ya no son `xfail`; las dos variantes de
  `test_autorizacion_real_en_app` pasaron en esta ejecución.
- Se conserva `detalleDelServidor`: solo acepta `detail` JSON de tipo texto, corto
  (hasta 300 caracteres tras normalizar espacios) y lo muestra como texto inerte,
  no como HTML. Se mantienen los detalles de 400/401/502/503, las comprobaciones de
  solicitud vigente y el resto del comportamiento integrado por Alex.
- **Único cambio funcional del panel:** el fallback del 503 dice
  «El servicio no está disponible temporalmente. Inténtalo más tarde; si persiste,
  avisa al equipo». Un HTML de proxy o un JSON sin `detail` válido no permite concluir
  que falte `CLAVE_API`. Un 503 JSON válido del backend **sí conserva su explicación**
  de configuración: no se reemplaza por el mensaje genérico.
- Se ajustó la prueba del 503 HTML, se cubrieron detalles vacíos, nulos, de tipo
  incorrecto, demasiado largos y JSON roto/nulo, y se comprobó texto seguro también
  en 503. Se conservan tanto la variante JSON 503 del frontend como
  `tests/test_seguridad.py::test_servidor_sin_clave_no_queda_abierto`, sin editar
  las pruebas de Matías.
- **Demo retirada solo del Taller 2:** `proyecto/src/agente_eduardo/demo.html` no
  tiene referencias funcionales. La app sirve `src/comun/panel.html`; el servidor de
  Eduardo solo publica la ficha y su responder. No hay montaje estático ni ruta demo;
  las referencias encontradas en Taller 2 son documentales. El HTML antiguo tampoco
  enviaba `X-API-Key`. Se eliminó únicamente esa copia, no la demo funcional `/demo`
  ni la foto del Taller 1. La búsqueda, el inventario y las comprobaciones 404 quedan
  en [referencias-demo.txt](evidencias/eduardo/cierre-integrado-2026-11-14/referencias-demo.txt).

No se editaron `panel.py`, agentes/grafos, seguridad, configuración, dependencias,
README grupales ni despliegue en este cierre. Además del HTML y la retirada indicada,
los cambios se limitan a este documento y las evidencias de Eduardo.

## 3. Pruebas automatizadas · 2026-11-14

Entorno: Windows, Python **3.12.10**, pytest **9.2.0**, Playwright **1.65.1**, Chrome
instalado en modo sin ventana. Se reutilizó `.venv`, sin instalar ni cambiar dependencias.

| Suite | Resultado medido | Código de salida | Evidencia |
| --- | --- | --- | --- |
| Proyecto, desde `proyecto` | **168 passed in 10.88s** | 0 | [pytest-proyecto.txt](evidencias/eduardo/cierre-integrado-2026-11-14/pytest-proyecto.txt) |
| Frontend de Eduardo | **68 passed in 69.11s** | 0 | [pytest-frontend.txt](evidencias/eduardo/cierre-integrado-2026-11-14/pytest-frontend.txt) |

[Resultados y huellas](evidencias/eduardo/cierre-integrado-2026-11-14/resultados-pruebas.json).
Las suites usan dobles o interceptación para las respuestas/proveedor; **no llaman a
Gemini con credenciales reales**. Los dos casos de autorización ejercitan la app real
con el grafo sustituido, y no se confunden con R06/R07 reales. El timeout sigue probado
con reloj virtual; móvil es emulación Chrome, no teléfono físico ni Safari.

`CARPETA_CAPTURAS` se configuró en
`evidencias/eduardo/cierre-integrado-2026-11-14/capturas-regresion/`, carpeta nueva.
Las capturas anteriores no se sobrescribieron. La
[captura 09](evidencias/eduardo/cierre-integrado-2026-11-14/capturas-regresion/09-503-html-simulado.png)
es **503 HTML SIMULADO**, no una avería real de Heroku o Gemini.

### Repetición sin sobrescribir evidencias

Desde `taller-02-c2/proyecto`, crear un destino distinto para cada repetición:

```powershell
$destino = Join-Path "../evidencias/eduardo" ("cierre-integrado-" + (Get-Date -Format "yyyyMMdd-HHmmss") + "-" + [guid]::NewGuid().ToString("N"))
.\.venv\Scripts\python.exe ../evidencias/eduardo/validar_cierre_local.py pruebas --carpeta $destino
# Fase separada: R05 sí consume una consulta real al proveedor configurado.
.\.venv\Scripts\python.exe ../evidencias/eduardo/validar_cierre_local.py casos --carpeta $destino
```

El [ejecutor](evidencias/eduardo/validar_cierre_local.py) configura `CARPETA_CAPTURAS`
solo en el entorno del hijo de pytest. Rechaza sobrescribir sus registros; no agrega
claves a los argumentos, no crea archivos de configuración y sanitiza antes de guardar.

## 4. R05, R06, R07 y R09 · app LOCAL integrada · 2026-11-14

Ejecución entre **13:55:05 y 13:55:50, UTC−03:00**. Se usó una `CLAVE_API` temporal
aleatoria, válida para las instancias hijas y nunca publicada. R05 tomó la configuración
privada del proveedor existente; `PORT`, `PUERTO`, `URL_BASE` y `URLS_AGENTES` se
ajustaron **solo en el entorno de esos procesos**, para usar los cuatro agentes internos
en loopback. No se alteró `.env` ni se usaron direcciones de Heroku.

Pregunta exacta en los cuatro casos:
«¿Cuál es el presupuesto simulado de una feria tecnológica para 80 personas y 4 horas?».
El orden fue R06 → R07 → R05 → R09 para observar los rechazos antes de cualquier consulta
al grafo. No hubo dobles, sustitución de respuestas HTTP ni reintentos automáticos.

| Caso y hora local de inicio | Solicitud / resultado esperado | Resultado real y evidencia | Alcance |
| --- | --- | --- | --- |
| **R05 · 13:55:32** | Panel con clave válida; 200, contrato de cuatro campos, agente y motivo | **200**, `Agente de Eduardo`, motivo recibido, total **$2.173.600 CLP**, supuestos y advertencias completos; [captura](evidencias/eduardo/cierre-integrado-2026-11-14/r05-acceso-permitido.png) | **Consulta real al coordinador, A2A y Gemini**. Se conserva el cuerpo completo, no se deduce del fixture anterior ni se recalculan importes. Los precios siguen siendo ficticios. |
| **R06 · 13:55:29** | Cliente HTTP sin `X-API-Key`; 401 antes del coordinador | **401**, `detail` de clave ausente; **0 preguntas y 0 envíos A2A** registrados hasta ese punto; [captura](evidencias/eduardo/cierre-integrado-2026-11-14/r06-sin-clave.png) | HTTP real con httpx. La imagen rotula una visualización del estado/cuerpo realmente recibidos, no un aviso nativo del panel ni una respuesta simulada. |
| **R07 · 13:55:31** | Clave incorrecta en el panel; 401, volver al ingreso y conservar pregunta | **401**, aviso con `detail`, campo de clave vacío y pregunta conservada; todavía **0 preguntas y 0 envíos A2A**; [captura](evidencias/eduardo/cierre-integrado-2026-11-14/r07-clave-incorrecta.png) | Rechazo real del middleware, sin invocar proveedor/agentes. |
| **R09 · 13:55:42** | Otro proceso LOCAL autorizado, sin configuración válida del proveedor; error 502/503 sanitizado | **502**, «No se pudo consultar al agente: Falta configurar la clave de Gemini (GOOGLE_API_KEY) en el .env o en las Config Vars.»; pregunta conservada, envío habilitado, sin secretos ni traza en el aviso; [captura](evidencias/eduardo/cierre-integrado-2026-11-14/r09-proveedor-sin-configuracion.png) | **Error HTTP real de configuración** del SDK. `GOOGLE_API_KEY` y `GEMINI_API_KEY` vacías, dotenv deshabilitado y Vertex desactivado solo en ese hijo. No es una respuesta simulada ni una prueba de rechazo remoto, cuota agotada o caída de Gemini. |

Evidencia común: [resultados-locales.json](evidencias/eduardo/cierre-integrado-2026-11-14/resultados-locales.json),
[registro integrado](evidencias/eduardo/cierre-integrado-2026-11-14/servidor-integrado.txt) y
[registro de R09 aislado](evidencias/eduardo/cierre-integrado-2026-11-14/servidor-r09-aislado.txt).
Los registros nuevos conservan las flechas A2A en UTF-8. R05 tiene un envío y una recepción
A2A; R09 falla en el supervisor antes de enviar al agente. Las capturas contienen una
franja de procedencia y amplían solo la altura del chat, sin editar las respuestas.
No se guardaron cabeceras de petición, HAR, trazas de navegador ni valores de claves.

## 5. Pendientes reales y límites

- **R08, R10, R11 y R12 no se ejecutaron como casos reales en este cierre.** Validación
  protegida de entrada tiene cobertura automatizada del proyecto; desconexión, timeout
  y no JSON mantienen cobertura simulada, no evidencia de fallo real del servicio.
- R01–R04 del 13-11-2026 permanecen como históricos: capturas anteriores al Markdown.
  No se repitieron los otros tres agentes con el formato actual; R05 sí vuelve a validar
  a Eduardo con acceso protegido y Markdown integrado.
- Heroku/HTTPS y sus límites de router siguen fuera de esta validación LOCAL, a cargo
  de operación. No se ha comprobado este ajuste en el despliegue público.
- `detail` seguro para el DOM no equivale a sanitizar secretos. El frontend confía en
  los mensajes traducidos del backend; el `except` genérico de `panel.py` sigue usando
  `str(error)`. Revisar con Matías cualquier responder futuro que no traduzca errores y
  las cabeceras de no caché de errores. No se amplió ese alcance aquí.
- Falta revisión humana del nuevo PR y, después, el commit/push que autorice Eduardo.
  No quedan pendientes de integración de Matías ni `xfail` activos en esta base.

## 6. Selección exacta para el nuevo PR

La lista cerrada de **29 rutas: 5 archivos modificados, 23 nuevos y 1 eliminación** está en
[archivos-para-pr.txt](evidencias/eduardo/cierre-integrado-2026-11-14/archivos-para-pr.txt):
rutas relativas a la raíz, incluida la retirada de la demo. Solo contiene archivos de
Eduardo; excluye `.env`, `.venv`, la foto del Taller 1 y los archivos de otras personas.
**No se ejecutó `git add`, commit ni push.** Para preparar más adelante únicamente esa
selección, desde la raíz y tras revisarla:

```powershell
$archivos = Get-Content -Encoding UTF8 -LiteralPath "taller-02-c2/evidencias/eduardo/cierre-integrado-2026-11-14/archivos-para-pr.txt"
git add -- $archivos
git diff --cached --name-only
git diff --cached --check
git diff --cached --stat
git status --short
```

No usar `git add .` ni `git add -A`. El nuevo PR parte de `origin/main` ya integrado;
no debe volver a incluir como novedades la implementación original o los archivos
ajenos incorporados por fast-forward. Comprobaciones finales de conservación y alcance:
[revision-final.json](evidencias/eduardo/cierre-integrado-2026-11-14/revision-final.json).
La solicitud de este cierre se añadió a
[prompts-utilizados.md](evidencias/eduardo/prompts-utilizados.md).
La revisión final confirmó 14 capturas históricas binarias idénticas, huellas probadas
vigentes, índice vacío, ningún valor privado detectado en la selección y ningún enlace
local roto. Se revisaron visualmente las 12 capturas nuevas; esto no sustituye una
auditoría integral de seguridad.

</details>

## Histórico conservado · 2026-11-13

**Lo siguiente no describe el estado vigente.** Se conservan íntegros los resultados
iniciales, la nota de integración de Alex y el cierre anterior. Las menciones a protección
pendiente, `xfail` o selección antigua corresponden a aquellas bases, no a este cierre.

<details>
<summary>Abrir registro histórico completo del 13-11-2026</summary>

**Entorno: LOCAL · Fecha: 2026-11-13 · Rama: `c2t2/eduardo-frontend` · Base: `18e7f7d`.**

## Estado tras la integración (nota de Alex · 2026-11-13 · rama `c2t2/alex-integracion`)

Eduardo: esta nota va **antes** de tu texto. Lo que sigue describe tu rama *antes* de
integrar y se conserva como registro, así que dice cosas que ya cambiaron (por ejemplo,
«el PR de Matías sigue abierto» o los dos `xfail`). Revísala y vuelve a probar.

**Integración.** Se unieron main + `c2t2/matias-seguridad` + `c2t2/eduardo-frontend` sin
conflictos. Resultados LOCAL de esta rama: `pytest` del proyecto **168 aprobadas**;
comprobaciones del frontend **55 aprobadas**. Los dos diagnósticos `xfail` (V22 y V23)
**pasan**: con el control de acceso de Matías, un POST sin clave o con clave incorrecta da
401 antes de ejecutar al coordinador. Quité la marca `xfail` y renombré la prueba a
`test_autorizacion_real_en_app` (antes `..._pendiente_en_app`).

**Qué cambié yo en `panel.html` (tu zona) y por qué.** Revísalo:

| Cambio | Por qué |
| --- | --- |
| Nueva función `detalleDelServidor`: si la respuesta es JSON y trae `detail` como texto de hasta 300 caracteres, ese texto se muestra (siempre con `textContent`, en una línea). Si no cumple, se usa el texto fijo de antes. | El contrato acordado con Matías dice que el servidor responde `{"detail": "mensaje"}` y que el frontend lo muestra. Tu código elegía un texto por código y no leía `detail`, así que la persona no veía, por ejemplo, «La clave de Gemini no es válida» o «Falta configurar GOOGLE_API_KEY». |
| Se aplica a 400, 502 y 503. Los demás códigos (429, 500, 504, 404…) siguen con tus textos fijos, y un `detail` que no sea texto (por ejemplo la lista de un 422) también. | Matías solo garantiza mensajes claros y sin claves ni trazas en esos tres códigos. Tu criterio de no mostrar cuerpos crudos se mantiene para todo lo demás. |
| En el 401 el `detail` se agrega al aviso de la pantalla de ingreso: «Acceso rechazado (401). La clave de acceso es incorrecta. Ingresa una clave válida…». | Distingue «clave incorrecta» de otros rechazos. Sigue volviendo al ingreso y conservando la pregunta. |
| El texto fijo del 503 ya no es el del 502. Ahora: «El servidor no está configurado para recibir consultas (falta su clave de acceso). Avisa a quien lo administra.» | Un 503 del servidor significa que falta `CLAVE_API`. Es un problema de configuración de quien administra, no una falla del proveedor o de un agente como decía el texto compartido con el 502. |
| Después de leer el cuerpo se vuelve a comprobar que la solicitud sigue vigente. | Para no pisar una conversación nueva con una respuesta tardía; es la misma regla que ya usabas. |

**Cambios en tu archivo de comprobaciones** (`evidencias/eduardo/test_panel_eduardo.py`):
el 503 espera ahora «no está configurado»; se quitó la marca `xfail`; y se agregaron 9
comprobaciones: el `detail` se muestra en 400/502/503 (3), un `detail` inválido o largo
usa el texto fijo (4), el `detail` se muestra como texto y no como HTML (1) y el 401 con
`detail` vuelve al ingreso (1). Esas 9 más tus 44 anteriores dan las 55 aprobadas.

**Verificación mía** (LOCAL, Chrome real contra la app real, con una clave temporal): con
clave incorrecta aparece el 401 con su `detail`; con clave correcta, una pregunta real
mostró «Agente: Agente de Matias» y su motivo; un servidor sin `CLAVE_API` mostró el
`detail` del 503; y uno sin `GOOGLE_API_KEY`, el 502 ya traducido.

**Lo que te toca (no lo hice yo):**

1. Revisar mis cambios de `panel.html` y repetir tus comprobaciones.
2. Ejecutar de verdad R05, R06, R07 y R09 (secciones 3 y 5) contra la app integrada y
   con evidencia real; sigue sin existir evidencia real del frontend con acceso permitido y
   rechazado. Las capturas 04 y 05 son simuladas.
3. Actualizar las secciones 3 y 5, que todavía dicen que la protección de Matías no está
   integrada y que los `xfail` siguen pendientes.
4. Decidir sobre `src/agente_eduardo/demo.html`: ya no se sirve desde la app única y su
   `fetch` no envía la clave, así que daría 401 si se sirviera.
5. Cuidado al repetir las comprobaciones: por defecto regeneran tus capturas 01–08. Usa
   `CARPETA_CAPTURAS` (ver el README del taller).

## 1. Aporte y límites

Reutilicé el panel de la app única para consultar al coordinador desde un navegador.
El alcance de este aporte es `proyecto/src/comun/panel.html`,
`proyecto/src/comun/panel.py`, este documento y `evidencias/eduardo/`.
No modifiqué agentes, coordinador, configuración, dependencias de producción,
README grupal ni archivos de despliegue.

Al comenzar, el único archivo sin seguimiento era
`taller-01-c2/evidencias/eduardo/03-ficha-telefono.jpg`. Se conserva fuera de este trabajo;
no se incluye en la selección de archivos para el commit.

**Resultado del cierre:** 114 pruebas del proyecto aprobadas; 44 comprobaciones de
frontend aprobadas y **2 `xfail` de autorización pendiente**, no aprobados. Las respuestas
de la regresión automatizada son **SIMULADAS**, sin Gemini ni A2A. Se conservan también
los resultados iniciales (39 aprobadas y 2 `xfail`), sin sobrescribirlos.

Además se registran **cuatro consultas reales LOCAL del 13-11-2026**, observadas
manualmente y revisadas en capturas por Eduardo según su confirmación al cierre.
Se recuperaron fragmentos del registro de esas cuatro ejecuciones y se localizaron y
revisaron las seis [capturas manuales originales](evidencias/eduardo/capturas-manuales-eduardo/INDICE.md).
**Son anteriores al ajuste de Markdown**: acreditan los resultados funcionales visibles,
no el aspecto posterior al ajuste ni un acceso protegido. No se sustituyen por simulaciones.

## 2. Implementación y ajustes

- Ingreso mediante un campo `password`, con etiqueta visible y autocompletado desactivado.
  La clave se conserva en una variable privada del script; el campo se vacía al continuar.
  No se escribe en `localStorage`, `sessionStorage`, cookies, URL ni registros.
  Cambiar clave, recargar o abandonar la página elimina el estado del panel.
- La clave de la aplicación viaja en `X-API-Key`, nunca en el cuerpo. **`GOOGLE_API_KEY`
  permanece en el servidor y no debe ingresarse en esta pantalla.** El autocompletado es
  una indicación al navegador: no controla extensiones ni decisiones del usuario de
  guardar contraseñas.
- Se conserva el contrato: `POST /panel/consultar`, JSON `{texto, context_id}`; respuesta
  JSON con `respuesta`, `context_id`, `agente`, `motivo`. No se agrega una consulta
  ficticia al ingresar: el servidor debe autorizar la primera consulta y las siguientes.
- La respuesta admite un **subconjunto básico de Markdown seguro**: títulos `#` a `######`,
  negritas `**…**` / `__…__` y código en línea. Se crean únicamente nodos DOM conocidos
  y nodos de texto; no se usan `innerHTML`, HTML del modelo ni dependencias externas.
  Solo se retiran delimitadores reconocidos: se conservan textos, cifras, unidades,
  espacios, saltos y condiciones, sin resumir ni recalcular. Las numeraciones y viñetas
  quedan literales para no renumerar datos; enlaces, imágenes, HTML y bloques cercados
  quedan como texto, sin ejecutarse. No es un intérprete completo de Markdown.
- Preguntas del usuario, agente, motivo y avisos siguen usando texto literal. `ninguno`
  se muestra como lo entrega el backend; agente/motivo vacíos dicen «No informado».
- Se distinguen 401/403, 400/422, 413, 429, 502/503, otros errores del servidor,
  desconexión, timeout, contenido no JSON, JSON inválido y contrato incompleto.
  Se clasifica primero por estado HTTP, incluso ante HTML de un proxy. No se muestran
  cuerpos de error ni trazas crudos. La pregunta se conserva para reintentar, sin pisar
  un borrador escrito mientras se esperaba. No hay reintentos automáticos.
- Se mantiene el límite de espera de **65 segundos** y se agrega un estado anunciado,
  indicador visual y bloqueo de enviar/sugerencias durante la consulta.
- Nueva conversación genera un UUID nuevo, limpia el historial y aborta la espera.
  Cada respuesta se aplica solo si pertenece a la solicitud aún vigente; tampoco el
  `finally` de una solicitud anterior cambia los controles o el foco de una nueva.
  El aborto del navegador **no garantiza** cancelar el trabajo ya iniciado en el servidor.
- Se retiró la persistencia anterior del `context_id` en `sessionStorage`: también vive
  en memoria. Recargar inicia otra conversación. Un `context_id` devuelto por el servidor
  se conserva para los siguientes turnos de esa conversación.
- Se corrigió el título heredado «Panel de viaje». Se reutilizaron tarjetas, colores y
  sugerencias; en celular el chat se presenta antes de la lista de agentes.
- Teclado: Enter envía, Mayús + Enter agrega línea, se respeta composición de texto;
  foco visible, enlace para saltar al contenido, log accesible y avisos de estado/error.
  Botones de al menos 44 px, entrada de 16 px y respeto por movimiento reducido.
- `panel.py` conserva la adaptación de respuestas simples/detalladas. Solo se agregaron
  cabeceras de no caché para la página y consultas exitosas, `nosniff`, política sin
  referente y una aclaración sobre la responsabilidad de autorización.

## 3. Dependencias del equipo: no confundir ingreso con autorización

**La protección de Matías NO está integrada en esta base; su PR sigue abierto.** Cargar una clave no la valida.
El panel evita mensajes como «autorizado» o «conectado» sin una comprobación efectiva.
Configurar `CLAVE_API` por sí solo tampoco protege la implementación actual.

| Responsable | Dependencia / archivos que podrían requerir coordinación |
| --- | --- |
| Matías, coordinando con Alex | Validar `X-API-Key` contra `CLAVE_API` en el servidor, antes de ejecutar al coordinador. Clave ausente/incorrecta debe devolver 401; sin configuración debe fallar de forma segura. La integración central puede afectar `src/comun/servidor.py`, `src/comun/config.py` o `app.py`, que no se editaron aquí. No hace falta otro endpoint para el flujo actual; si se quiere validar inmediatamente al ingresar, hará falta acordar uno de autenticación sin ejecutar una pregunta. |
| Matías | Sanitizar errores del servidor, incluida la rama de excepción existente en `panel.py`, que todavía usa `str(error)`. Este aporte **no modificó esa rama**. Ocultar un detalle en pantalla no impide que llegue en la respuesta HTTP o que un servidor lo registre. Revisar también cabeceras de no caché de los errores. |
| Matías y Alex | Acordar estados de error estables (por ejemplo, 502/503 proveedor y 504 timeout). `src/coordinador/graph.py` puede transformar fallas A2A en texto dentro de un 200 y registrar el detalle de la excepción: el frontend no puede distinguir eso con fiabilidad de una respuesta válida. No se alteró ese comportamiento ni los registros del equipo. |
| Alex | Integrar los PR y mantener el contrato de cuatro campos. Si se protegen también las rutas A2A, coordinar el acceso interno en `src/coordinador/cliente.py`/catálogo sin trasladar secretos al navegador. |
| Alex / operación | Revisión de codificación: UTF-16 del archivo y reversión cp850/cp1252 comprobadas sin reemplazos; 29 líneas del extracto coinciden con la fuente. Ocho `UnicodeEncodeError` impidieron escribir las líneas A2A normales (envío y recepción de cada agente); sus prefijos/horas no pueden recuperarse. Se conservan `Message/Arguments` y cuatro HTTP 200. Coordinar salida UTF-8 para próximas evidencias; no se modificó `registro.py` ni se reinició el servidor. Detalle y límites en el extracto A2A. |
| Sebastián | Despliegue y HTTPS. El frontend usa rutas relativas y no contiene URL de Heroku. El timeout de 65 s **no elimina** el límite del router de Heroku; un 503/HTML puede venir del despliegue. La validación desplegada corresponde a su integración, no se hizo aquí. |

El estado inicial sin configuración quedó superado: `proyecto/.env` ya existe y se confirmó
que **ambas variables están configuradas**, sin publicar sus valores. La aplicación se
inició con `.venv` y `/salud` respondió 200 con `{"ok": true}`. Las cuatro consultas reales
se distinguen de los dobles automatizados en la sección 5. Antes de provocar errores reales
o validar acceso protegido, integrar la sanitización y autorización pendientes.

## 4. Verificación reproducible

Desde `taller-02-c2/proyecto`, reutilizando `.venv` (Python 3.12.10, pytest 9.2):

```powershell
# Playwright ya está instalado como dependencia SOLO de verificación.
# Separar las capturas de cada repetición para conservar las originales:
$env:CARPETA_CAPTURAS = Join-Path $env:TEMP ("opencode/cierre-eduardo-" + [guid]::NewGuid())
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m pytest ../evidencias/eduardo/test_panel_eduardo.py -v -rx --tb=short --xfail-tb --show-capture=no -p no:cacheprovider
Remove-Item Env:CARPETA_CAPTURAS
```

La suite de interfaz usa Chrome instalado, en modo sin ventana. Para Edge, definir
`$env:CANAL_NAVEGADOR="msedge"`. No necesita claves. Sirve el **router/panel real** con
FastAPI en loopback y usa interceptación/dobles para las respuestas; no contacta internet.
Los dos diagnósticos `xfail` utilizan las rutas reales de `app.py`, pero sustituyen el grafo
para no invocar Gemini. **Se mantienen ambas marcas `xfail`**: revisar su retiro únicamente
después de integrar y comprobar la protección de Matías, nunca por un 200 funcional.
La ejecución registrada usa pytest 9.2; `--xfail-tb` permite ver el 200 obtenido frente
al 401 esperado (si una versión anterior no reconoce esa opción, omitir solo esa opción).

Evidencias del cierre: [114 pruebas del proyecto](evidencias/eduardo/pytest-cierre-proyecto.txt),
[44 aprobadas y 2 `xfail` del frontend](evidencias/eduardo/pytest-cierre-frontend.txt) y
[código de comprobación ampliado](evidencias/eduardo/test_panel_eduardo.py).
Se conservan los registros [inicial del proyecto](evidencias/eduardo/pytest-proyecto.txt) e
[inicial del frontend](evidencias/eduardo/pytest-frontend.txt), las seis capturas originales
y los cambios previos de `panel.py`. La foto del Taller 1 conserva su contenido y sigue sin seguimiento.
Esta actualización de enlaces y revisión de codificación **no cambió código ni repitió
pruebas**: los resultados automatizados anteriores se mantienen, incluidos los dos `xfail`.

### Casos ejecutados

En la columna «Observaciones», **simulado** se refiere a la respuesta o condición de
prueba, no a una ejecución real de un agente. Las capturas contienen una banda de
procedencia añadida por la prueba y no contienen claves.

| Caso | Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido y evidencia | Observaciones / pendientes |
| --- | --- | --- | --- | --- | --- |
| V01 | LOCAL · 2026-11-13 | Ejecutar `pytest` desde `proyecto` | Suite existente aprobada sin Gemini | **114 passed**, `pytest-cierre-proyecto.txt` | Incluye dobles; no demuestra integración con proveedor. |
| V02 | LOCAL · 2026-11-13 | GET `/` y POST con contexto `prueba` | Página real, no caché y contrato de cuatro campos | Aprobado, `test_contrato_http_y_cache_sin_proveedor` | Respuesta del proveedor simulada. |
| V03 | LOCAL · 2026-11-13 | POST con espacios, sin `texto` o con número | 400, 422 y 422, respectivamente | Aprobado, `test_entrada_invalida_servidor_actual` | Validación HTTP real del router; no usa proveedor. |
| V04 | LOCAL · 2026-11-13 | POST sin contexto a un responder de texto | Crear contexto, adaptar sin alterar texto | Aprobado, `test_adaptacion_respuesta_simple_y_contexto_opcional` | Responder simulado; contrato anterior conservado. |
| V05 | LOCAL · 2026-11-13 | Ingreso con espacios y luego valor efímero | Campo enmascarado, no consultar ni fingir autorización | Aprobado, `test_ingreso_enmascarado_sin_validacion_ficticia`; [captura 01](evidencias/eduardo/01-ingreso-local.png) | No es prueba de autorización. |
| V06 | LOCAL · 2026-11-13 | Dos consultas, recarga e ingreso otra vez | POST con clave solo en cabecera, contexto conservado y luego nuevo; sin almacenamiento | Aprobado, `test_cabecera_contrato_memoria_y_recarga` | Cabecera comprobada sin guardar su valor; respuestas simuladas. |
| V07 | LOCAL · 2026-11-13 | Respuestas con Matías, Alex, Eduardo, Sebastián y `ninguno` | Mostrar literalmente agente, motivo, cifras y condiciones | Cinco variantes aprobadas; [captura 02](evidencias/eduardo/02-respuesta-simulada-escritorio.png) | **Todas simuladas**: no prueban el enrutamiento real. |
| V08 | LOCAL · 2026-11-13 | Respuesta con HTML, `**10 %**` y espacios | Negrita DOM; conservar `10 %`, espacios y HTML literal | Aprobado, `test_no_interpreta_html_ni_altera_espacios` | Respuesta adversa simulada; agente/motivo también inertes. |
| V09 | LOCAL · 2026-11-13 | Recibir 401 JSON, 401 HTML y 403 HTML | Volver al ingreso, borrar clave y conservar pregunta | Tres variantes aprobadas; [captura 04](evidencias/eduardo/04-acceso-rechazado-simulado.png) | **Estados simulados**, no rechazo real del servidor actual. |
| V10 | LOCAL · 2026-11-13 | Recibir 400/422 o 413 | Mensaje de entrada inválida o demasiado larga | Tres variantes aprobadas, `test_errores_http_simulados_sin_detalles_crudos` | HTTP simulado. |
| V11 | LOCAL · 2026-11-13 | Recibir 429 | Explicar límite, permitir reintento manual | Aprobado, mismo test | HTTP simulado. |
| V12 | LOCAL · 2026-11-13 | Recibir 502/503 o 500 con HTML y detalle interno | Aviso de proveedor/agente o servidor, sin detalle crudo | Tres variantes aprobadas; [captura 05](evidencias/eduardo/05-proveedor-fallido-simulado.png) | Fallas **simuladas**; no se provocó una falla real de Gemini. |
| V13 | LOCAL · 2026-11-13 | Recibir 408/504 o 404 | Aviso de timeout del servidor o estado HTTP | Tres variantes aprobadas, mismo test | HTTP simulado. |
| V14 | LOCAL · 2026-11-13 | Recibir 200 HTML, JSON roto, `null` o contrato incompleto | Error entendible, no mostrar el cuerpo crudo | Cuatro variantes aprobadas, `test_respuesta_no_json_o_incompleta_simulada` | Respuestas simuladas. |
| V15 | LOCAL · 2026-11-13 | Abortar red como desconectada | Mensaje de conexión y controles recuperados | Aprobado, `test_desconexion_simulada` | Desconexión simulada, no se cortó la red del equipo. |
| V16 | LOCAL · 2026-11-13 | Mantener petición pendiente y avanzar 65.001 ms virtuales | Abortar espera, avisar y conservar pregunta | Aprobado, `test_timeout_simulado_con_reloj_virtual` | **Reloj virtual**, no se midieron 65 s reales. |
| V17 | LOCAL · 2026-11-13 | Enter y envío programático durante una petición pendiente | Solo una solicitud, indicador y sugerencias bloqueadas | Aprobado; [captura 06](evidencias/eduardo/06-espera-simulada.png) | Petición retenida por la prueba; conserva borrador nuevo. |
| V18 | LOCAL · 2026-11-13 | Nueva conversación antes de resolver fetch o JSON anteriores | UUID nuevo; respuesta vieja no altera texto, contexto ni bloqueo de la nueva | Dos variantes aprobadas, `test_nueva_conversacion_descarta_respuesta_tardia_aun_sin_abort` | Dobles ignoran deliberadamente `AbortSignal` para probar la carrera. |
| V19 | LOCAL · 2026-11-13 | Cambiar clave durante una petición pendiente | Cancelar espera y limpiar historial/entrada | Aprobado, `test_cambiar_clave_cancela_pendiente_y_limpia_historial` | Respuesta pendiente simulada. |
| V20 | LOCAL · 2026-11-13 | Espacios, Mayús + Enter, Enter y sugerencia con teclado | Validación local, salto de línea y envío por teclado | Aprobado, `test_teclado_validacion_local_y_sugerencias` | Sin auditoría con lector de pantalla. |
| V21 | LOCAL · 2026-11-13 | Vista de 320 y 390 px con Markdown | Sin desborde de página/burbuja, texto exacto, chat primero y botones ≥44 px | Dos variantes aprobadas; captura inicial [03](evidencias/eduardo/03-respuesta-simulada-movil.png) y regresión [08](evidencias/eduardo/08-markdown-simulado-movil.png) | Respuesta simulada mixta, revisada visualmente; emulación en Chrome, no teléfono físico/Safari. |
| V22 | LOCAL · 2026-11-13 | POST sin cabecera con `CLAVE_API` configurada solo para el test | **401 antes del coordinador** | **Obtenido 200; `xfail`**, `test_autorizacion_real_pendiente_en_app[ausente]` | Brecha real de la ruta actual; grafo simulado. **Pendiente Matías.** |
| V23 | LOCAL · 2026-11-13 | POST con cabecera incorrecta | **401 antes del coordinador** | **Obtenido 200; `xfail`**, variante `[incorrecta]` | Misma dependencia. No se presenta como seguridad aprobada. |
| V24 | LOCAL · 2026-11-13 | Cuatro fixtures Markdown con títulos, horarios, CLP y unidades | Negritas/títulos por DOM, contenido exacto sin `**`; pregunta literal; Nueva conversación limpia también nodos formateados | Cuatro variantes aprobadas, `test_markdown_basico_seguro_sin_cambiar_datos`; [captura 07](evidencias/eduardo/07-markdown-simulado-escritorio.png) | **Simuladas**, no transcripciones ni reejecuciones de R01–R04. Captura revisada visualmente. |
| V25 | LOCAL · 2026-11-13 | Código en línea, CRLF, marcadores incompletos, bloques cercados y enlaces/imágenes con contenido adverso | Código literal, `88 L` en negrita, espacios/saltos exactos; ningún enlace, imagen o script ejecutable | Aprobado, `test_codigo_y_sintaxis_no_admitida_quedan_inertes` | Payload simulado. No sustituye la sanitización de errores del servidor. |

## 5. Validación real LOCAL y pendientes de integración

### Configuración privada y repetición

1. Antes de validar seguridad o publicar, integrar con Matías/Alex la autorización y la
   sanitización descritas arriba. Las cuatro comprobaciones funcionales ya realizadas
   no sustituyen esa integración. No publicar esta base como si ya estuviera protegida.
2. `proyecto/.env` ya existe: **no sobrescribirlo ni documentar valores**. Para otra
   instalación, crearlo desde `.env.example` solo si no existe y editarlo en privado:
   `GOOGLE_API_KEY` válida exclusivamente para el servidor; `CLAVE_API` robusta,
   distinta, para la aplicación; `MODELO` disponible para la cuenta; `PUERTO` coincidente
   con uvicorn; `URL_BASE` local y `URLS_AGENTES` vacía para los cuatro agentes internos.
   Revisar `PORT` si ya está definido, porque tiene prioridad sobre `PUERTO`.
3. Desde `proyecto`, iniciar por ejemplo:
   `.\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000`.
   Abrir `http://127.0.0.1:8000/` e ingresar **solo `CLAVE_API`** en el campo enmascarado.
4. Usar nueva conversación para cada caso de agentes. Revisar respuesta íntegra, agente,
   motivo y registros sanitizados. No capturar `.env`, cabeceras, pestaña Network ni claves;
   no usar `curl -v`, HAR o trazas con credenciales. Capturar solo la interfaz y resultados
   revisados. No escribir claves en preguntas ni en comandos que queden en el historial.

### Cuatro pruebas reales LOCAL · 13-11-2026

Resultados **observados manualmente y revisados en capturas por Eduardo**, comunicados
en el pedido de cierre y contrastados ahora con las seis imágenes originales de
[`evidencias/eduardo/capturas-manuales-eduardo/`](evidencias/eduardo/capturas-manuales-eduardo/INDICE.md).
No se repitieron consultas a Gemini ni se modificaron los píxeles. **Estas capturas son
anteriores al ajuste de presentación de Markdown**: todavía muestran sus delimitadores
literales y no prueban el formato posterior. Las capturas automatizadas 01–08 de la carpeta
superior siguen siendo evidencias distintas; sus respuestas de prueba son simuladas.

Se recuperaron [fragmentos A2A de las cuatro ejecuciones](evidencias/eduardo/a2a-local-2026-11-13.txt),
sin secretos: pregunta truncada por el registro, selección con motivo, POST al agente
HTTP 200 y argumentos de recepción. La revisión confirmó ocho errores de escritura de
flechas: faltan las dos líneas A2A normales de cada consulta con sus prefijos y horas,
no recuperables desde ese archivo. No se reconstruyeron. Las cuatro preguntas del registro
están truncadas y las respuestas completas no se registraban: **las cifras siguientes se
contrastan con las capturas manuales**, no se deducen de HTTP 200 ni de fixtures.
Los datos de los agentes siguen siendo de demostración:
«real» describe la llamada a la aplicación/proveedor, no una reserva, cotización o pago real.

| Caso | Entorno y fecha | Solicitud (tema; registro truncado) | Resultado esperado | Resultado obtenido y evidencia | Observaciones / pendientes |
| --- | --- | --- | --- | --- | --- |
| R01 · Matías | LOCAL · 13-11-2026 · 10:57:56 | Programa de feria cultural familiar de 3 horas | Agente de Matias; programa y condiciones íntegros | **Programa 16:00–18:00 y 60 minutos libres informados**; [captura manual 02](evidencias/eduardo/capturas-manuales-eduardo/02-matias-programa.png); registro A2A común | Anterior al ajuste de Markdown. No se rellenan ni recalculan horarios. |
| R02 · Alex | LOCAL · 13-11-2026 · 11:04:25 | Recinto interior para feria tecnológica de 80 personas | Agente de Alex; conservar recintos, características y advertencias | **Tres recintos, características y advertencias correctas**; capturas manuales [03: inicio](evidencias/eduardo/capturas-manuales-eduardo/03-alex-recintos-inicio.png) y [04: final](evidencias/eduardo/capturas-manuales-eduardo/04-alex-recintos-final.png); registro A2A común | Anteriores al ajuste de Markdown. Se conserva la advertencia y la confirmación humana de disponibilidad/aforo. |
| R03 · Eduardo | LOCAL · 13-11-2026 · 10:47:10 | Presupuesto simulado para feria tecnológica de 80 personas y 4 horas | Agente de Eduardo; conservar partidas, CLP y advertencias | **Presupuesto total $2.173.600 CLP**; [captura manual 01](evidencias/eduardo/capturas-manuales-eduardo/01-eduardo-presupuesto.png); registro A2A común | Anterior al ajuste de Markdown. No se deduce del fixture que comparte la cifra ni se recalcula. |
| R04 · Sebastián | LOCAL · 13-11-2026 · 11:10:46 | Catering para feria tecnológica de 80 personas | Agente de Sebastian; conservar horarios, dietas y unidades | **Servicios 11:00 y 13:30, dietas 65/10/5 y 88 L de agua**; capturas manuales [05: inicio](evidencias/eduardo/capturas-manuales-eduardo/05-sebastian-catering-inicio.png) y [06: final](evidencias/eduardo/capturas-manuales-eduardo/06-sebastian-catering-final.png); registro A2A común | Anteriores al ajuste de Markdown. Sin reinterpretar categorías ni cantidades. |

### Seguridad integrada y errores reales: pendientes

**El PR de Matías sigue abierto.** R05–R12 no se consideran aprobados por R01–R04 ni
por las simulaciones. V22/V23 siguen como `xfail`, con 200 obtenido frente al 401 esperado.

| Caso | Entorno y fecha de preparación | Solicitud | Resultado esperado | Resultado obtenido y evidencia | Observaciones / pendientes |
| --- | --- | --- | --- | --- | --- |
| R05 · Permitido | LOCAL · 2026-11-13 | Clave válida y pregunta R03 | 200 con contrato válido; solo después de autorizar en servidor | **No ejecutado; sin evidencia real** | Comprobar también R06/R07: un 200 aislado no demuestra protección. |
| R06 · Sin clave | LOCAL · 2026-11-13 | Cliente HTTP, POST válido sin `X-API-Key` | 401 antes de invocar coordinador/proveedor | **Pendiente; diagnóstico actual V22 devuelve 200 con grafo simulado** | No usar la ausencia de botón en el frontend como prueba. |
| R07 · Clave incorrecta | LOCAL · 2026-11-13 | Clave distinta ingresada en el panel; enviar R03 | 401; vuelta al ingreso sin perder pregunta | **Pendiente; diagnóstico actual V23 devuelve 200 con grafo simulado** | Revisar que el backend no invoque agentes ni registre la clave. |
| R08 · Entrada inválida | LOCAL · 2026-11-13 | Con clave válida, POST con texto de espacios y luego sin `texto` | 400 y 422; mensaje claro y sin trazas | **Pendiente con protección; V03 probado solo en router actual** | Usar cliente HTTP con ingreso privado de clave; no incluirla en un comando. |
| R09 · Proveedor | LOCAL · 2026-11-13 | En instancia LOCAL aislada, con autorización activa y proveedor sin configuración válida | Error sanitizado 502/503 acordado; mensaje claro sin secretos | **No ejecutado; sin evidencia real** | Matías debe sanitizar antes. Modificar configuración solo en privado, restaurarla y reiniciar; no usar una cuenta real para agotar cuotas. |
| R10 · Desconexión | LOCAL · 2026-11-13 | Tras cargar la página, detener el servidor e intentar consultar | Aviso de conexión y reintento manual disponible | **No ejecutado; V15 es simulado** | Reiniciar después. |
| R11 · Timeout | LOCAL · 2026-11-13 | Entorno LOCAL controlado que mantenga una consulta pendiente más de 65 s | Aviso de timeout y recuperación; una nueva conversación no recibe respuesta vieja | **No ejecutado; V16 usa reloj virtual** | Coordinar retardo controlado con Matías, sin cambiar tiempos del proveedor de producción. |
| R12 · No JSON | LOCAL · 2026-11-13 | Servidor/proxy de ensayo devuelve HTML en vez de JSON | Aviso claro; nunca insertar HTML crudo | **No ejecutado en servicio real; V14 es simulado** | No provocar fallas del despliegue público. |

## 6. Prompts y asistencia

Herramienta de asistencia: **OpenCode**. El prompt real de Eduardo se conserva en
[`prompts-utilizados.md`](evidencias/eduardo/prompts-utilizados.md), junto con las reglas
del equipo aplicadas. No se inventaron prompts retrospectivos. No se modificaron prompts
de los agentes. La regresión automatizada y la recuperación de registros no enviaron
preguntas a Gemini; las cuatro consultas manuales se documentan por separado.

## 7. Selección para commit y entrega

Se prepararon únicamente frontend, documento y evidencias de Eduardo mediante selección
explícita; **sin commit ni push**. La foto del Taller 1 queda fuera del índice, sin seguimiento.
Desde la raíz, la selección utilizada y sus comprobaciones son:

```powershell
$evidenciasEduardo = @(
  "README.md", "prompts-utilizados.md", "test_panel_eduardo.py",
  "pytest-proyecto.txt", "pytest-frontend.txt",
  "pytest-cierre-proyecto.txt", "pytest-cierre-frontend.txt", "a2a-local-2026-11-13.txt",
  "01-ingreso-local.png", "02-respuesta-simulada-escritorio.png",
  "03-respuesta-simulada-movil.png", "04-acceso-rechazado-simulado.png",
  "05-proveedor-fallido-simulado.png", "06-espera-simulada.png",
  "07-markdown-simulado-escritorio.png", "08-markdown-simulado-movil.png",
  "capturas-manuales-eduardo/INDICE.md",
  "capturas-manuales-eduardo/01-eduardo-presupuesto.png",
  "capturas-manuales-eduardo/02-matias-programa.png",
  "capturas-manuales-eduardo/03-alex-recintos-inicio.png",
  "capturas-manuales-eduardo/04-alex-recintos-final.png",
  "capturas-manuales-eduardo/05-sebastian-catering-inicio.png",
  "capturas-manuales-eduardo/06-sebastian-catering-final.png"
) | ForEach-Object { "taller-02-c2/evidencias/eduardo/$_" }
git add -- taller-02-c2/proyecto/src/comun/panel.html taller-02-c2/proyecto/src/comun/panel.py taller-02-c2/documento-Eduardo.md $evidenciasEduardo
git diff --cached --name-only
git diff --cached --check
git diff --cached --stat
git status --short
```

No usar `git add .` ni `git add -A`. Comprobar que la foto del Taller 1 siga como `??`
y no aparezca en `git diff --cached --name-only`. `.venv` y `.env` nunca se seleccionan.
Eduardo realizará el push y abrirá el PR; Alex revisa e integra. El PR debe indicar
**frontend con regresión simulada y cuatro consultas LOCAL reales documentadas con capturas
anteriores al ajuste de Markdown; fragmentos A2A recuperados con límites explícitos;
autorización integrada pendiente**.

</details>
