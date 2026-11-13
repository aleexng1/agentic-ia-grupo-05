# Evidencias de Eduardo · LOCAL · 2026-11-13

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
