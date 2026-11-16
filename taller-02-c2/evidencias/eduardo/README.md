# Evidencias de Eduardo · guía de lectura

El [informe individual](../../documento-Eduardo.md) contiene el aporte y los resultados seleccionados en tablas de cinco columnas. Esta guía enlaza la evidencia necesaria para revisarlos; los registros completos se conservan como respaldo.

## 1. Recorrido LOCAL real: pregunta → A2A → respuesta visible

| Qué revisar | Evidencia |
| --- | --- |
| Presupuesto, acceso válido y respuesta de Eduardo | [Captura R05](cierre-integrado-2026-11-14/r05-acceso-permitido.png) y [registro A2A](cierre-integrado-2026-11-14/servidor-integrado.txt). |
| Programa de Matías | [Pregunta y respuesta](pendientes-locales-2026-11-14-144554/r01-actual-intercambio.json) y [captura](pendientes-locales-2026-11-14-144554/r01-actual-consulta-real.png). |
| Recintos de Alex | [Pregunta y respuesta](pendientes-locales-2026-11-14-144554/r02-actual-intercambio.json) y [captura](pendientes-locales-2026-11-14-144554/r02-actual-consulta-real.png). |
| Catering de Sebastián | [Pregunta y respuesta](pendientes-locales-2026-11-14-144554/r04-actual-intercambio.json) y [captura](pendientes-locales-2026-11-14-144554/r04-actual-consulta-real.png). |
| Envíos y recepciones A2A de los tres casos anteriores | [Registro integrado del 14/11](pendientes-locales-2026-11-14-144554/servidor-integrado-consultas.txt). |

Son consultas reales con datos de demostración, no reservas, pedidos ni precios reales.

## 2. Acceso, errores y comprobaciones LOCAL

- [Cierre integrado del 14/11](cierre-integrado-2026-11-14/README.md): R05 autorizado 200; R06/R07 rechazados 401; R09 configuración del proveedor 502; registros de **168 pruebas del proyecto y 68 del frontend, sin xfail**.
- [Casos locales complementarios](pendientes-locales-2026-11-14-144554/README.md): R08 entradas inválidas 400/422; R10 desconexión/restauración; R11 demora inducida y timeout real; R12 HTML controlado no ejecutado. La carpeta conserva su nombre histórico, pero esos resultados finales están documentados.
- [Instalación limpia del 15/11](reproducibilidad-2b754e2-2026-11-15/README.md): copia de `2b754e2`, Python 3.12.10, entorno nuevo y comprobaciones HTTP, sin Gemini ni prueba visual.
- [Suite del frontend](test_panel_eduardo.py): comprobaciones automatizadas con dobles; no equivalen a consultas reales al proveedor.

## 3. Uso REMOTO MANUAL

| Sesión | Evidencia y alcance |
| --- | --- |
| 15/11: cuatro agentes | [Índice y cuatro capturas con HTTP 200](manual-autenticada-2026-11-15/README.md). v12 confirmada por Sebastián solo para esa sesión; tres preguntas/inicios quedan fuera del encuadre. Se conserva la observación 60/40 de Matías. |
| 16/11: aclaración y continuidad | [Secuencia y presupuesto](complemento-remoto-manual-2026-11-16/README.md): 80 asistentes, 180 minutos, **$1.742.400 CLP**, HTTP 200. Versión desplegada no confirmada; no demuestra aislamiento entre conversaciones. |
| 16/11: móvil emulado | [390 × 844](complemento-remoto-manual-2026-11-16/04-movil-390-dimensiones.png) y [presupuesto/controles](complemento-remoto-manual-2026-11-16/05-movil-390-presupuesto-controles.png). [Vista declarada de 320 px](complemento-remoto-manual-2026-11-16/06-movil-320-declarado-presupuesto-controles.png): ancho exacto no verificado por el recorte. No es teléfono físico. |

La [ejecución remota automática anterior](validacion-remota-2026-11-15-203522/README.md) acredita panel/salud y rechazos, pero terminó esperando el ingreso privado con **0 POST autenticados**. No sustituye a la sesión manual ni se le atribuye v12.

## 4. Trazabilidad y material histórico

- [Prompts utilizados](prompts-utilizados.md): solicitudes, decisiones y límites del trabajo asistido.
- [Anexo histórico del documento](../../anexo-Eduardo-historico.md) e [índice histórico](INDICE-HISTORICO.md): cortes anteriores, guiones no ejecutados e incidencias; no son el resumen vigente.
- [Capturas originales del 13/11](capturas-manuales-eduardo/INDICE.md): anteriores al ajuste de Markdown; se mantienen con esa procedencia.

Las imágenes, JSON, logs y scripts conservan sus resultados originales. La reorganización documental no repite pruebas ni convierte fallos inducidos o intentos incompletos en aprobaciones remotas. Las credenciales se facilitan al evaluador por privado; no pertenecen a esta carpeta.
