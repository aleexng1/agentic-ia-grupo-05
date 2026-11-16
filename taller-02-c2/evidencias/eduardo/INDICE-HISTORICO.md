> **Índice histórico, conservado el 16/11/2026.** Para evaluar el cierre, comenzar por la [guía breve](README.md). Se conserva el índice anterior de `main` en `09c6328`, con sus enlaces de secciones redirigidos al anexo histórico. Los estados y guiones de cada corte no son nuevas pruebas ni pendientes del resumen actual.

---

# Evidencias de Eduardo · REMOTO y LOCAL

## Vigente · complemento REMOTO MANUAL · 2026-11-16

**Fuente:** [README y seis capturas originales aportados por Eduardo](complemento-remoto-manual-2026-11-16/README.md),
revisados sin modificar sus bytes. Son evidencias de su sesión manual; esta
integración no ejecuta consultas ni suites. **Release y commit del 16/11 no
confirmados**: v12 y sus identificadores siguen limitados a las cuatro consultas del 15/11.

| Entorno y fecha | Solicitud | Esperado | Obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| REMOTO MANUAL · Heroku · Chrome · 16/11/2026 · respuesta HTTP 09:47:37 UTC−03:00 | 80 personas y 4 horas; cambiar a 3 horas; aclarar feria tecnológica sin repetir asistentes ni duración | Recuperar 80 asistentes y la duración actualizada al completar el tipo | **Continuidad de contenido observada:** 80 asistentes, **180 minutos**, subtotal **$1.584.000**, contingencia **$158.400**, total **$1.742.400 CLP**; **POST 200 OK, application/json** | [03](complemento-remoto-manual-2026-11-16/03-continuidad-presupuesto-200.png). La secuencia y aclaraciones están en [01](complemento-remoto-manual-2026-11-16/01-tipo-de-evento-pendiente.png) y [02](complemento-remoto-manual-2026-11-16/02-secuencia-aclaracion.png); 02 tiene seleccionada una petición anterior. **No se compararon los `context_id` ni se verificó aislamiento.** |
| REMOTO MANUAL · Heroku · móvil emulado · 16/11/2026 · paso de 390 px | Mostrar la conversación y el presupuesto existente | Lectura de mensajes y controles visibles | [04](complemento-remoto-manual-2026-11-16/04-movil-390-dimensiones.png) acredita **390 × 844**; [05](complemento-remoto-manual-2026-11-16/05-movil-390-presupuesto-controles.png) muestra presupuesto, entrada y Enviar sin recorte lateral apreciable en la zona visible | 05 no incluye la barra: tamaño asociado por la secuencia, no medido por ese recorte. Sin `scrollWidth`, prueba física ni garantía sobre toda la página. |
| REMOTO MANUAL · Heroku · móvil emulado · 16/11/2026 · paso declarado de 320 px | Conservar el presupuesto en una vista más estrecha | Texto y controles legibles | [06](complemento-remoto-manual-2026-11-16/06-movil-320-declarado-presupuesto-controles.png) muestra presupuesto ajustado, entrada y Enviar dentro del recorte | **La barra no es visible: 320 × 844 no está verificado independientemente.** No acredita ausencia de desborde fuera de lo visible. |

La hora corresponde al `Date` de la respuesta seleccionada en 03 (`12:47:37 GMT`),
no a latencia ni hora exacta de captura. Las dos respuestas que piden el tipo de
evento no son presupuestos calculados ni errores HTTP. La tercera pregunta completa
ese tipo: **no ejecuta el caso de 20 personas y 2 horas tras Nueva conversación**.
No se amplían espera/bloqueo, duplicados, `context_id`, aislamiento, respuestas
tardías ni las preguntas incompletas del 15/11. Las fallas inducidas siguen siendo
**LOCAL** y la observación de Matías se conserva. Detalle:
[`documento-Eduardo.md`](../../anexo-Eduardo-historico.md#complemento-remoto-manual--2026-11-16--vigente).

## Consolidación documental previa · 2026-11-16 · histórico

El siguiente corte precede a la recepción del complemento; sus pendientes describen
aquella revisión sin navegador, no el alcance visible aportado después.

<details>
<summary>Abrir revisión previa y guion, conservados</summary>

**No hubo una nueva ejecución remota.** Esta sesión no tiene acceso al navegador
autenticado de Eduardo; se entregó el guion manual inmediatamente, sin otra espera
de ingreso, sin leer claves y con **0 consultas nuevas enviadas**. La fecha anterior
es la de revisión documental; una ejecución futura deberá llevar su propia fecha,
hora y zona, y su versión desplegada **no está identificada**.

| Entorno y fecha | Solicitud | Esperado | Obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| REMOTO previsto · Heroku · revisión documental 16/11/2026 | Hasta tres consultas: presupuesto, continuidad y Nueva conversación | Espera/bloqueo, un POST ante segundo intento, continuidad y cambio de `context_id` | **NO EJECUTADAS:** sin acceso al navegador autenticado | No es una falla observada de Heroku ni demuestra aislamiento completo del servidor. |
| REMOTO previsto · Heroku · móvil emulado · revisión documental 16/11/2026 | Misma respuesta autenticada a 390 y 320 px, sin otra consulta | Sin desborde, legibilidad y acceso a controles | **NO INSPECCIONADA** en ambos anchos | No acredita teléfono físico, teclado virtual ni Safari. |
| Network histórico del 15/11 · revisión documental 16/11/2026 | Recuperar solo Payload/Response de los tres casos sin inicio | Preguntas y respuestas exactas, correlacionadas con sus capturas | **NO RECUPERADO:** sin acceso a ese Network | Se conserva la limitación; no se afirma que los registros hayan desaparecido ni se reconstruyen preguntas. |

Textos exactos, matriz de cinco columnas y
[guion manual mínimo](../../anexo-Eduardo-historico.md#guion-manual-mínimo--no-ejecutado)
en [`documento-Eduardo.md`](../../anexo-Eduardo-historico.md#consolidación-del-cierre--2026-11-16).
No se generaron evidencias remotas nuevas ni se duplicaron las anteriores. Las
fallas inducidas del 14/11 siguen siendo evidencia **LOCAL**, no de Heroku.

</details>

## REMOTO MANUAL · 2026-11-15 · resultados conservados

**URL:** https://grupo05-taller2-seba-94d12914f3eb.herokuapp.com/

Cuatro capturas manuales aportadas por Eduardo, revisadas sin modificar sus bytes:
**POST 200 OK, respuesta, agente correcto y motivo visibles**. Fuente e imágenes:
[`manual-autenticada-2026-11-15/README.md`](manual-autenticada-2026-11-15/README.md).
Se aprueba el alcance visible, no una transcripción íntegra de los tres casos sin
inicio. **Matías conserva una observación de contenido:** bloque de 60 minutos con
descripción de unos 40, sin explicación del margen.

| Entorno y fecha | Solicitud | Esperado | Obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| REMOTO MANUAL · Heroku · 2026-11-15 · 21:51:58 UTC−03:00 | Presupuesto; pregunta exacta fuera del encuadre | 200, respuesta útil, Eduardo y motivo visibles | **200 OK**, presupuesto con total **$2.173.600**, `Agente de Eduardo` y motivo | [01](manual-autenticada-2026-11-15/01-eduardo-remoto-200.png). Falta el inicio y la pregunta; no reconstruidos. |
| REMOTO MANUAL · Heroku · 2026-11-15 · 21:59:03 UTC−03:00 | Programa cultural familiar de 3 horas desde las 16:00 | 200, programa útil, Matías y motivo visibles | **200 OK**, programa **16:00–19:00**, informa cero minutos libres, `Agente de Matias` y motivo | [02](manual-autenticada-2026-11-15/02-matias-remoto-200.png). Pregunta y respuesta visibles; **observación 60/40 minutos pendiente**. |
| REMOTO MANUAL · Heroku · 2026-11-15 · 22:01:15 UTC−03:00 | Recintos; pregunta exacta fuera del encuadre | 200, recomendaciones útiles, Alex y motivo visibles | **200 OK**, recintos con capacidad/accesibilidad y advertencias, `Agente de Alex` y motivo | [03](manual-autenticada-2026-11-15/03-alex-remoto-200.png). Falta el inicio y la pregunta; no reconstruidos. |
| REMOTO MANUAL · Heroku · 2026-11-15 · 22:03:25 UTC−03:00 | Catering; pregunta exacta fuera del encuadre | 200, propuesta útil, Sebastián y motivo visibles | **200 OK**, menús diferenciados, box lunch **13:30** y **88 L**, `Agente de Sebastian` y motivo | [04](manual-autenticada-2026-11-15/04-sebastian-remoto-200.png). Falta el inicio y la pregunta; no reconstruidos. |

Las horas son las cabeceras HTTP `Date` visibles convertidas desde UTC, no duraciones.
**Despliegue identificado por confirmación de Sebastián, su responsable, según la
[nueva fuente aportada por Eduardo](prompts-utilizados.md#confirmación-del-despliegue-manual):**
Heroku ejecutaba la **release v12**, desplegada el **15/11/2026 a las 21:44**, con
identificador informado **`4593bafb`** y **código equivalente al de `main` en `96ebca4`**.
Sebastián confirmó expresamente que las cuatro consultas manuales de **21:51 a 22:04**
corrieron contra esa versión. Se cierra **solo su pendiente de identificación**,
**sin verificación independiente de Heroku** ni afirmar que `4593bafb` y `96ebca4`
sean el mismo commit. La base Git documental `96ebca4` y el PR #83 fusionado no
identifican por sí solos el despliegue. El informe de Sebastián del día 14 es otra ejecución.

### Automático anterior y comprobaciones del cliente · conservados

Las pruebas de **20:39–21:07 del 15/11/2026** son **anteriores a v12 (21:44)**;
conservan la referencia histórica a **v10 reportada**, sin verificarla ni atribuirles
v12 o la equivalencia de código comunicada para las consultas manuales.

[`validacion-remota-2026-11-15-203522/README.md`](validacion-remota-2026-11-15-203522/README.md)
conserva sus **28 archivos originales**. La fase autenticada terminó esperando el
ingreso privado (`TimeoutError`, 20:54:51) y registró **0 POST autenticados**. Los
cuatro 200 manuales posteriores no son resultados de ese ejecutor ni convierten su
intento fallido en una aprobación automática.

Panel/salud, 401 sin clave/ficticia y visualización móvil **emulada** corresponden a
aquella fase. Espera, guardia de **1 POST pese a cuatro intentos extra** y Nueva
conversación se comprobaron durante un rechazo 401, no una consulta autorizada.

**Pendientes:** capturas iniciales remotas de Eduardo/Alex/Sebastián (no disponibles),
observación de contenido de Matías, contexto/aislamiento/respuestas tardías, espera
y bloqueo/duplicados con acceso aceptado, Nueva conversación autorizada y caso de
20 personas y 2 horas, confirmación independiente del ancho de 320 px, medición de
desborde global y pruebas interactivas en móvil, teléfono físico/teclado virtual/Safari,
R08 remoto vacío autorizado, errores/router y versión desplegada del 16/11. El
complemento acredita continuidad de contenido y visualización, **no comparación de
`context_id`**. Las capturas de
«inicio» del histórico LOCAL no se reutilizan para completar huecos remotos.
Detalle vigente y límites: [`documento-Eduardo.md`](../../documento-Eduardo.md).

**Selección final:** los cuatro Markdown ya preparados y **los siete archivos del
complemento**, 11 rutas enumeradas en
[`documento-Eduardo.md`](../../anexo-Eduardo-historico.md#preparación-documental-de-este-cierre).
Se mantienen los cambios previos y los siete originales sin editar ni duplicar.
La [lista anterior](manual-autenticada-2026-11-15/archivos-para-indice.txt) y la
[revisión documental anterior](manual-autenticada-2026-11-15/revision-documental.json)
son registros históricos previos a esta confirmación, no la selección ni la revisión
actuales; se conservan sin regenerarlos. Sin nuevas consultas, suites, cambios en
código/configuración, commit o push. Se conservan los registros, los PNG y la foto
ajena al alcance.

## Registro LOCAL · 2026-11-15 · reproducibilidad de 2b754e2

**`2b754e2e2bb8b035888f281ced1b3c36d6b1bab4` publicado**, tanto en
`c2t2/eduardo-frontend` como en `refs/pull/82/head`. Las evidencias de la continuación
del 14-11-2026 **ya están publicadas dentro del PR #82, fusionado en `main`** mediante
**`71df3e80adea7ec675db73eefe884cb82eeffc9a`**. La rama local incorporó `origin/main`
mediante `git fetch origin` y `git merge --ff-only origin/main`, conservando las 12 rutas.
**`2b754e2` sigue siendo la versión utilizada en la instalación limpia**, no el commit
de fusión; no se cambiaron las fechas ni los resultados de las pruebas.

Comprobación nueva en una copia temporal de ese commit, Python **3.12.10** y `.venv`
nueva, sin paquetes del entorno actual: instalación **0**, `pip check` **0**, arranque
correcto en **58569**, panel/salud **200**, rechazos **401/401** y vacío/espacios
autorizados **400/400**. No se detectaron dependencias faltantes para este alcance.
**Sin Gemini, suites completas, navegador ni Heroku.** El panel se comprobó por HTTP,
incluida la igualdad de su HTML con el commit, no mediante una regresión visual nueva.

[`reproducibilidad-2b754e2-2026-11-15/README.md`](reproducibilidad-2b754e2-2026-11-15/README.md):
comandos, versiones, resultados primarios y conservación. La tabla de planificación
**REMOTA de aquel corte LOCAL**, todavía pendiente entonces, se conserva como
[registro histórico](../../anexo-Eduardo-historico.md#plan-remoto-del-cierre-local--histórico).
Los resultados manuales posteriores y el despliegue confirmado por su responsable
se describen arriba;
el [informe de Sebastián](../sebastian/pruebas-remotas.md) es otra ejecución del día 14.
Solo las 12 rutas del manifiesto de este cierre se publicaron en `8a5bb9b`, PR #84. No cambió código de producción ni se repitieron pruebas.

## Pendientes locales completados · 2026-11-14 · publicados en 2b754e2

Base probada **`d8cce1337b7caf0bcd63df2d9ce21d9dc96a3f91`**; publicación posterior
en **`2b754e2`, PR #82 ya fusionado**. No se cambia la fecha ni la base de aquellas comprobaciones.
Carpeta: [`pendientes-locales-2026-11-14-144554/`](pendientes-locales-2026-11-14-144554/README.md).
Contiene R08 (400/422 con autorización válida), R10 (desconexión y restauración del
servidor propio), R11 (65,472 s reales hasta el aviso; demora de 70,009 s) y R12 (200 HTML).
**R11/R12 son fallas inducidas en un entorno controlado, no fallas reales de Gemini ni
Heroku.** Incluye también una consulta real por agente de Matías, Alex y Sebastián, con
el panel actual: pregunta, respuesta íntegra, agente, motivo, capturas y registro A2A.

Se conservan los intentos instrumentales incompletos/no aprobados, separados de los
resultados finales. Las tres consultas reales no se repitieron. `.env`, todas las capturas
históricas, foto y demo del Taller 1 y servidor previo del puerto 8000 se conservaron.
La selección exacta de aquella continuación publicada está en
[`archivos-modificados.txt`](pendientes-locales-2026-11-14-144554/archivos-modificados.txt).

## Cierre integrado anterior · 2026-11-14 · publicado en d8cce13

Base probada `741305bf0fed986b523898114bb1d851d28d063b` más ajustes publicados
posteriormente en `d8cce13`, PR #82; no es trabajo todavía pendiente de commit/push.
**168 pruebas del proyecto y 68 del frontend aprobadas, sin `xfail`.** R05 real con
coordinador/A2A/Gemini devuelve 200; R06 y R07 reales, 401; R09 aislado sin configuración
del proveedor, 502. Este último no acredita una caída remota ni cuota agotada de Gemini.

Las evidencias de aquel cierre se encuentran en
[`cierre-integrado-2026-11-14/README.md`](cierre-integrado-2026-11-14/README.md), con
capturas separadas de regresión **simulada** y casos HTTP **reales**, registros
sanitizados, huellas de archivos probados y selección histórica del PR #82.
`validar_cierre_local.py` reproduce ambas fases sin modificar `.env` ni Heroku.

Las capturas y logs antiguos no se regeneraron. Los documentos de aquella ejecución
conservan su corte temporal anterior a la publicación; el estado vigente está arriba.
El apartado inferior y los prompts
anteriores describen sus propias fechas; no representan pendientes actuales.

## Histórico · 2026-11-13

<details>
<summary>Abrir índice y límites de las evidencias anteriores, conservados</summary>

Entrega y matriz de casos: [`../../documento-Eduardo.md`](../../documento-Eduardo.md).

| Archivo | Procedencia y límite |
| --- | --- |
| `pytest-proyecto.txt` | Ejecución desde `proyecto`: 114 pruebas existentes aprobadas, sin Gemini. |
| `pytest-frontend.txt` | Registro inicial conservado: 39 comprobaciones aprobadas y 2 `xfail` de autorización ausente. |
| `pytest-cierre-proyecto.txt` | Regresión de cierre: 114 aprobadas, reutilizando `.venv`; sin Gemini. |
| `pytest-cierre-frontend.txt` | Regresión de cierre: 44 aprobadas y **2 `xfail`**, incluidos Markdown, móvil y Nueva conversación. Chrome real; respuestas/demoras/errores **simulados**. |
| `a2a-local-2026-11-13.txt` | Fragmentos recuperados de las cuatro consultas reales LOCAL: selección, HTTP 200, `Message/Arguments`. Sin secretos ni cuerpos completos; faltan líneas A2A normales con hora por codificación de consola. |
| `test_panel_eduardo.py` | Pruebas reproducibles del router y navegador, sin claves reales ni llamadas al proveedor. Ubicadas aquí para respetar el alcance de Eduardo. |
| `01-ingreso-local.png` | Página real con campo vacío; no demuestra autorización. |
| `02-respuesta-simulada-escritorio.png` | Respuesta, agente y motivo **simulados**, vista de escritorio. |
| `03-respuesta-simulada-movil.png` | Respuesta **simulada**, ancho de 390 px; no teléfono físico. También se verificaron 320 px. |
| `04-acceso-rechazado-simulado.png` | 401 **simulado**. El servidor actual todavía no lo impone. |
| `05-proveedor-fallido-simulado.png` | 502 **simulado**, sin provocar una falla de Gemini. |
| `06-espera-simulada.png` | Petición retenida por la prueba; indicador y controles bloqueados. |
| `07-markdown-simulado-escritorio.png` | Regresión Markdown **simulada**, revisada visualmente: título y horario en negrita sin `**`. La pregunta sigue literal. |
| `08-markdown-simulado-movil.png` | Regresión Markdown **simulada**, revisada visualmente a 390 px. Fixture mixto con horarios, dietas, agua y CLP; no corresponde a una respuesta real de un agente. |
| [`capturas-manuales-eduardo/INDICE.md`](capturas-manuales-eduardo/INDICE.md) | Seis capturas manuales originales de las cuatro consultas reales LOCAL, revisadas y enlazadas en R01–R04. **Anteriores al ajuste de Markdown**; no prueban el aspecto posterior ni la integración de seguridad. |
| `prompts-utilizados.md` | Solicitud real de implementación y reglas aplicadas. |

Las capturas 01–08 fueron obtenidas con Playwright sobre el HTML real, no generadas ni
retocadas para cambiar resultados. La prueba añade una banda visible de entorno, fecha
y procedencia. No se guardaron claves, cabeceras, HAR, trazas ni archivos `.env`.
El timeout se comprobó con **reloj virtual**, no esperando 65 segundos reales.
Los `xfail` significan una dependencia de seguridad sin resolver, no dos pruebas de
seguridad aprobadas. El PR de Matías sigue abierto; Heroku y errores reales siguen pendientes.

Las cuatro consultas reales del 13-11-2026 se documentan en R01–R04 del documento:
observación manual y revisión en capturas **comunicadas por Eduardo**, respaldadas
parcialmente por los registros recuperados. Ahora se localizaron y revisaron las seis
imágenes de [`capturas-manuales-eduardo/`](capturas-manuales-eduardo/INDICE.md), sin retocarlas.
**Son anteriores al ajuste de Markdown**, no una verificación visual posterior al cambio.
Las capturas automatizadas 01–08 de esta carpeta no se usan como prueba de esas consultas
reales. Los HTTP 200 no certifican su texto completo ni prueban autorización.

Revisión de codificación de los logs: 29 líneas del extracto contrastadas con la fuente;
conversión UTF-16 y reversión cp850/cp1252 estrictas, sin reemplazos. Ocho errores al
escribir las flechas impidieron conservar las líneas A2A normales con sus prefijos/horas.
El detalle de estos fragmentos no recuperables y los límites de preguntas/respuestas
está en `a2a-local-2026-11-13.txt`; no se reconstruyeron eventos. Esta revisión solo
actualiza documentación: no cambia código, repite pruebas ni vuelve a invocar Gemini.

Para repetir, consultar los comandos de la sección 4 del documento. Los logs de esta
carpeta corresponden a cada ejecución registrada. Definir `CARPETA_CAPTURAS` permite
guardar otra ejecución fuera del repositorio: así se conservaron las seis capturas y
los dos registros originales en este cierre. Se incorporaron solo las capturas nuevas
07–08 tras revisar los resultados. Repetir pytest no reemplaza automáticamente los logs
y, sin esa variable, escribe las capturas en esta carpeta. Revisar resultados y fechas
antes de archivar otra ejecución. Las rutas personales de los encabezados de pytest se sustituyeron
por `<REPOSITORIO>`; no se alteraron resultados ni mensajes de prueba.

</details>
