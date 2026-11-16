# Eduardo Basaure · Frontend · Taller 2 del Curso 2 · Grupo 5

**Informe de entrega · 16/11/2026.** Mi aporte es el panel web: ingreso de la clave, envío al coordinador, presentación fiel de la respuesta, manejo de errores y uso en escritorio/móvil emulado.

**Resultado acreditado:** recorrido LOCAL real con los cuatro agentes y registros A2A; acceso permitido y rechazado; cuatro respuestas REMOTAS MANUALES con HTTP 200; continuidad de contenido y visualización móvil emulada. Las pruebas automatizadas registradas el 14/11 son **168 del proyecto y 68 del frontend, sin `xfail`**; no se presentan como una ejecución sobre la versión actual de `main`.

Para evaluar el aporte, comenzar por este informe y la [selección de evidencias](evidencias/eduardo/README.md). El [anexo histórico](anexo-Eduardo-historico.md) conserva cortes anteriores, incidencias y guiones no ejecutados; sus pendientes antiguos no describen por sí solos el cierre actual.

## 1. Aporte y reutilización

Reutilicé FastAPI, el coordinador y los cuatro agentes A2A del equipo. Mi zona de código fue [panel.html](proyecto/src/comun/panel.html) y [panel.py](proyecto/src/comun/panel.py). La autorización y traducción de errores se integraron con Matías; Alex integró el conjunto y Sebastián lo desplegó.

- **Acceso:** campo enmascarado; clave solo en memoria y cabecera `X-API-Key`, sin almacenamiento del navegador ni URL. Ingresarla no acredita autorización: el servidor valida cada consulta. La clave de Gemini permanece en el servidor.
- **Contrato:** `POST /panel/consultar` con `texto` y `context_id`; se muestran `respuesta`, `agente` y `motivo`. El coordinador elige un agente por pregunta.
- **Fidelidad:** Markdown básico mediante nodos DOM y texto, sin ejecutar HTML ni recalcular/resumir cifras, unidades o supuestos.
- **Errores:** avisos comprensibles, detalles válidos del servidor como texto seguro, pregunta conservada y reintento manual. Corregí el mensaje genérico del 503 cuando falta un `detail` válido.
- **Interacción:** espera, bloqueo de envíos repetidos, nueva conversación y descarte de respuestas antiguas en el cliente; ajustes de teclado, foco y disposición móvil.
- **Limpieza:** retirada de la demo sin uso del Taller 2. Este cierre documental no cambia código ni configuración.

## 2. Pruebas LOCAL

Fechas de 2026 en America/Santiago. Las consultas funcionales usaron A2A/Gemini reales con datos ficticios de ferias. Los fallos inducidos se identifican expresamente.

| Entorno y fecha | Solicitud | Esperado | Obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| LOCAL real · 14/11 | R05: presupuesto tecnológico, 80 personas, 4 horas; clave válida | 200, presupuesto, Eduardo y motivo | **200; $2.173.600 CLP** | [Captura][r05] y [log A2A][a2a-eduardo]. |
| LOCAL real · 14/11 | R01: programa cultural familiar, 3 horas desde las 16:00 | 200, programa, Matías y motivo | **200**; 60 minutos libres | [Intercambio íntegro][r01-json], [captura][r01]. Anterior al catálogo ampliado. |
| LOCAL real · 14/11 | R02: recinto interior, feria tecnológica de 80 personas | 200, recintos, Alex y motivo | **200**; tres opciones y advertencias | [Intercambio íntegro][r02-json], [captura][r02]. |
| LOCAL real · 14/11 | R04: catering para 80 personas/4 horas; 10 vegetarianas y 5 sin gluten | 200, servicios, dietas, Sebastián y motivo | **200**; servicios 11:00/13:30 y **88 L** | [Intercambio íntegro][r04-json], [captura][r04]. |
| LOCAL real · 14/11 | R06: consultar sin clave | Rechazar antes del coordinador | **401** | [Captura][r06]; sin envío A2A. |
| LOCAL real · 14/11 | R07: clave incorrecta en el panel | Rechazar y conservar pregunta | **401**, retorno al ingreso | [Captura][r07]; sin envío A2A. |
| LOCAL real · 14/11 | R08: espacios / falta de `texto`, con autorización | Validar antes del coordinador | **400 / 422** | [Evidencia HTTP][r08]. El 422 mantiene el formato estándar de FastAPI. |
| LOCAL aislado · 14/11 | R09: proveedor sin configuración válida | Error claro, sin falso éxito | **502**, pregunta conservada | [Captura][r09]. No prueba una caída remota de Gemini. |
| LOCAL de ensayo · 14/11 | R10: detener/restaurar servidor propio | Aviso de conexión y recuperación | Conexión rechazada; servidor restaurado | [Resultado][r10]. Heroku no intervenido. |
| LOCAL controlado · 14/11 | R11: inducir 70 segundos de demora | Timeout y descarte de respuesta antigua | Aviso a los **65,472 s**; conversación nueva sin respuesta vieja | [Medición][r11]. No es latencia de Gemini/Heroku. |
| LOCAL controlado · 14/11 | R12: devolver HTTP 200 con HTML deliberado | Rechazo sin ejecutar HTML | Aviso seguro; HTML no insertado ni ejecutado | [Resultado][r12]. Respuesta inducida. |

El [log de los otros tres agentes][a2a-otros] registra envíos/recepciones A2A y HTTP 200. Las preguntas y respuestas íntegras están enlazadas por caso.

**Regresión del 14/11:** [168 pruebas del proyecto][pytest-proyecto] y [68 del frontend][pytest-frontend], sin `xfail`. Incluyen dobles y comprobaciones de Markdown, memoria, teclado, espera y conversación; no son 236 consultas reales. Los dos `xfail` del 13/11 quedaron superados tras integrar la seguridad.

**Instalación limpia del 15/11:** copia de `2b754e2`, Python 3.12.10 y entorno virtual nuevo. Instalación/`pip check`: salida 0; arranque y panel/salud 200; rechazos 401; vacío/espacios 400. Comprobación HTTP, sin Gemini ni interacción visual. [Informe reproducible][instalacion].

## 3. Pruebas REMOTAS MANUALES

**URL:** [Planifica tu feria en Heroku](https://grupo05-taller2-seba-94d12914f3eb.herokuapp.com/).

Las cuatro consultas del **15/11** corresponden a **v12**, según Sebastián: despliegue a las 21:44, identificador Heroku `4593bafb`, código equivalente a `main` en `96ebca4`. Es confirmación del responsable, no verificación independiente ni identidad entre commits. **No identifica la versión del 16/11.**

| Entorno y fecha | Solicitud | Esperado | Obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| REMOTO manual · 15/11, 21:51 | Presupuesto; pregunta exacta fuera del encuadre | 200, respuesta, Eduardo y motivo | **200; $2.173.600 CLP** | [Captura][rem-eduardo]. Inicio no disponible; no reconstruido. |
| REMOTO manual · 15/11, 21:59 | Programa cultural familiar, 3 horas desde las 16:00 | 200, programa, Matías y motivo | **200**, 16:00–19:00, cero minutos libres | [Captura][rem-matias]. Bloque de 60 minutos con descripción de unos 40; margen sin explicar. |
| REMOTO manual · 15/11, 22:01 | Recintos; pregunta exacta fuera del encuadre | 200, recomendaciones, Alex y motivo | **200**, capacidad, accesibilidad y advertencias | [Captura][rem-alex]. Inicio no disponible; no reconstruido. |
| REMOTO manual · 15/11, 22:03 | Catering; pregunta exacta fuera del encuadre | 200, propuesta, Sebastián y motivo | **200**, menús diferenciados y **88 L** | [Captura][rem-seba]. Inicio no disponible; no reconstruido. |
| REMOTO manual · 16/11, 09:47 | 80 personas/4 h; cambiar a 3 h; completar tipo tecnológico | Pedir dato faltante y usar parámetros actualizados | **200; 80 asistentes, 180 min, $1.742.400 CLP** | [Secuencia][continuidad]. Continuidad de contenido; sin comparar `context_id`. |
| REMOTO · móvil emulado · 16/11 | Mostrar conversación a 390 × 844 | Lectura y controles accesibles | Dimensiones acreditadas; presupuesto/entrada/Enviar visibles | [Dimensiones][movil-dimensiones] y [controles][movil-controles]. Sin medición global de desborde. |
| REMOTO · vista estrecha · 16/11 | Paso declarado de 320 × 844 | Lectura y controles accesibles | Texto ajustado y controles dentro del recorte | [Captura][movil-320]. **Ancho exacto no verificado**: barra fuera del encuadre. |

Las horas proceden de cabeceras HTTP convertidas a UTC−03; no miden latencia. [Detalle del 15/11][manual-15] y [complemento del 16/11][manual-16].

La [ejecución remota anterior][rem-auto] acreditó panel/salud 200 y rechazos 401. Su fase autenticada terminó por timeout del instrumental esperando el ingreso privado: **0 POST autenticados**. Permanece separada de las consultas manuales, con su referencia histórica a v10 reportada.

## 4. Alcance y límites

- Hay evidencia del recorrido funcional, acceso, errores locales, presentación y reproducibilidad. No se declara auditoría completa de seguridad ni aprobación de todo escenario remoto.
- No se acreditaron en remoto aislamiento, respuestas tardías o bloqueo de duplicados durante consultas autorizadas. Hay comprobaciones locales; la espera/bloqueo remota observada ocurrió durante un 401.
- Permanecen sin acreditar la versión del 16/11, los tres inicios remotos ausentes, el ancho exacto de 320 px y un teléfono físico. Se conserva la observación 60/40 de Matías.
- Los **65 s** son el límite del cliente. Heroku puede cortar antes, a los **30 s** sin respuesta inicial; el navegador no amplía ese límite. Ver [límites operacionales](README.md#límites-conocidos).
- El equipo debe facilitar al evaluador la **`CLAVE_API` vigente por un canal privado** y mantener la app disponible hasta la corrección. La clave no forma parte de las evidencias.

## 5. Uso de IA y material de apoyo

Utilicé asistencia de IA para implementar/revisar el panel, diseñar comprobaciones y ordenar evidencias. El [registro de prompts](evidencias/eduardo/prompts-utilizados.md) conserva solicitudes y decisiones sobre Markdown seguro, acceso/errores, ensayos aislados, instalación limpia y documentación remota. Distingue instrucciones, ejecuciones y resultados.

La preparación, dependencias, inicio y detención están en el [README del taller](README.md). Se conservan el [código de comprobación](evidencias/eduardo/test_panel_eduardo.py), el [índice breve](evidencias/eduardo/README.md) y el [anexo histórico](anexo-Eduardo-historico.md). No se convierten guiones no ejecutados en pruebas aprobadas.

[r05]: evidencias/eduardo/cierre-integrado-2026-11-14/r05-acceso-permitido.png
[a2a-eduardo]: evidencias/eduardo/cierre-integrado-2026-11-14/servidor-integrado.txt
[r01-json]: evidencias/eduardo/pendientes-locales-2026-11-14-144554/r01-actual-intercambio.json
[r01]: evidencias/eduardo/pendientes-locales-2026-11-14-144554/r01-actual-consulta-real.png
[r02-json]: evidencias/eduardo/pendientes-locales-2026-11-14-144554/r02-actual-intercambio.json
[r02]: evidencias/eduardo/pendientes-locales-2026-11-14-144554/r02-actual-consulta-real.png
[r04-json]: evidencias/eduardo/pendientes-locales-2026-11-14-144554/r04-actual-intercambio.json
[r04]: evidencias/eduardo/pendientes-locales-2026-11-14-144554/r04-actual-consulta-real.png
[r06]: evidencias/eduardo/cierre-integrado-2026-11-14/r06-sin-clave.png
[r07]: evidencias/eduardo/cierre-integrado-2026-11-14/r07-clave-incorrecta.png
[r08]: evidencias/eduardo/pendientes-locales-2026-11-14-144554/r08-entrada-protegida.png
[r09]: evidencias/eduardo/cierre-integrado-2026-11-14/r09-proveedor-sin-configuracion.png
[r10]: evidencias/eduardo/pendientes-locales-2026-11-14-144554/finalizacion/r10-resultado.json
[r11]: evidencias/eduardo/pendientes-locales-2026-11-14-144554/complemento/r11-resultado.json
[r12]: evidencias/eduardo/pendientes-locales-2026-11-14-144554/finalizacion/r12-resultado.json
[a2a-otros]: evidencias/eduardo/pendientes-locales-2026-11-14-144554/servidor-integrado-consultas.txt
[pytest-proyecto]: evidencias/eduardo/cierre-integrado-2026-11-14/pytest-proyecto.txt
[pytest-frontend]: evidencias/eduardo/cierre-integrado-2026-11-14/pytest-frontend.txt
[instalacion]: evidencias/eduardo/reproducibilidad-2b754e2-2026-11-15/README.md
[rem-eduardo]: evidencias/eduardo/manual-autenticada-2026-11-15/01-eduardo-remoto-200.png
[rem-matias]: evidencias/eduardo/manual-autenticada-2026-11-15/02-matias-remoto-200.png
[rem-alex]: evidencias/eduardo/manual-autenticada-2026-11-15/03-alex-remoto-200.png
[rem-seba]: evidencias/eduardo/manual-autenticada-2026-11-15/04-sebastian-remoto-200.png
[continuidad]: evidencias/eduardo/complemento-remoto-manual-2026-11-16/README.md
[movil-dimensiones]: evidencias/eduardo/complemento-remoto-manual-2026-11-16/04-movil-390-dimensiones.png
[movil-controles]: evidencias/eduardo/complemento-remoto-manual-2026-11-16/05-movil-390-presupuesto-controles.png
[movil-320]: evidencias/eduardo/complemento-remoto-manual-2026-11-16/06-movil-320-declarado-presupuesto-controles.png
[manual-15]: evidencias/eduardo/manual-autenticada-2026-11-15/README.md
[manual-16]: evidencias/eduardo/complemento-remoto-manual-2026-11-16/README.md
[rem-auto]: evidencias/eduardo/validacion-remota-2026-11-15-203522/README.md
