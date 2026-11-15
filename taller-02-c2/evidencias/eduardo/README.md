# Evidencias de Eduardo · LOCAL

## Vigente · 2026-11-15 · reproducibilidad de 2b754e2

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
comandos, versiones, resultados primarios y conservación. La tabla para la futura
validación **REMOTA**, toda pendiente (versión desplegada: ver
[`pruebas-remotas.md`](../sebastian/pruebas-remotas.md)), está en
[`documento-Eduardo.md`](../../documento-Eduardo.md#validación-remota-futura--todavía-no-ejecutada).
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
