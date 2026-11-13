# Eduardo Basaure · Frontend · Taller 2 del Curso 2 · Grupo 5

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
