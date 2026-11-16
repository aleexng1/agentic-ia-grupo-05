# Consultas manuales autenticadas · Heroku · 15/11/2026

Estas cuatro capturas fueron aportadas por Eduardo durante la validación manual del panel. Se incluyen sin modificar sus píxeles ni sus bytes. Cada imagen muestra una petición POST a `/panel/consultar` con **200 OK**, una respuesta en el panel, el agente identificado y el motivo de selección.

**URL observada:** https://grupo05-taller2-seba-94d12914f3eb.herokuapp.com/

**Versión:** Sebastián había reportado la release v10 antes de estas pruebas. Las capturas no identifican la release ni el commit desplegado durante esta ejecución; ambos requieren correlación con el despliegue. No se deduce el commit de Heroku a partir de `main`.

## Resultados observables

Las horas siguientes proceden de la cabecera HTTP `Date` visible, convertida de UTC a America/Santiago (UTC−03). Son horas de respuesta del servidor, no mediciones de duración ni horas de creación de los PNG.

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
|---|---|---|---|---|
| REMOTO · Heroku · 15/11/2026 · 21:51:58 UTC−03 | Consulta de presupuesto de feria; pregunta exacta fuera del encuadre. | 200, respuesta de presupuesto, agente Eduardo y motivo visibles. | **Comprobado en captura:** POST 200 OK; Agente de Eduardo; subtotal $1.976.000, contingencia $197.600 y total $2.173.600. | [01-eduardo-remoto-200.png](01-eduardo-remoto-200.png). Se muestra el final de la respuesta. Falta adjuntar la vista del inicio con la pregunta, si se conserva. |
| REMOTO · Heroku · 15/11/2026 · 21:59:03 UTC−03 | «Propón un programa para una feria cultural familiar de 3 horas, comenzando a las 16:00. Indica los horarios y los minutos libres.» | 200, programa, agente Matías y motivo visibles. | **Comprobado en captura:** POST 200 OK; Agente de Matias; bloques 16:00–17:00, 17:00–17:30, 17:30–18:00 y 18:00–19:00; informa cero minutos libres. | [02-matias-remoto-200.png](02-matias-remoto-200.png). Pregunta y respuesta visibles. Observación de contenido: la visita tiene un bloque de 60 minutos y una descripción de unos 40 minutos; el margen no se explica. No se atribuye esa diferencia al frontend. |
| REMOTO · Heroku · 15/11/2026 · 22:01:15 UTC−03 | Consulta de recintos para una feria; pregunta exacta fuera del encuadre. | 200, recomendaciones, agente Alex y motivo visibles. | **Comprobado en captura:** POST 200 OK; Agente de Alex; recintos con capacidad, accesibilidad, servicio de comida y observaciones. | [03-alex-remoto-200.png](03-alex-remoto-200.png). Se ve parte de la lista y el final de la respuesta. Falta adjuntar el inicio con la pregunta, si se conserva. |
| REMOTO · Heroku · 15/11/2026 · 22:03:25 UTC−03 | Consulta de catering y menús especiales; pregunta exacta fuera del encuadre. | 200, propuesta de catering, agente Sebastián y motivo visibles. | **Comprobado en captura:** POST 200 OK; Agente de Sebastian; box lunch de 13:30, menús diferenciados y 88 litros de agua con 10 % de margen. | [04-sebastian-remoto-200.png](04-sebastian-remoto-200.png). Se ve el final de la respuesta. Falta adjuntar el inicio con la pregunta, si se conserva. |

## Relación con las evidencias anteriores

- Esta ejecución manual es posterior y distinta del intento automático registrado en `validacion-remota-2026-11-15-203522/`, que terminó esperando el ingreso privado y registró **0 POST autenticados**. Se conserva ese resultado histórico; no se transforma en una prueba automática aprobada.
- Los rechazos 401, panel/salud, visualización móvil emulada y controles observados durante un 401 pertenecen a sus evidencias anteriores. Estas cuatro capturas no vuelven a ejecutar ni amplían automáticamente ese alcance.
- Las capturas acreditan la respuesta HTTP y la salida visible del panel. No contienen trazas internas que demuestren por sí solas cada salto A2A ni la llamada al proveedor.
- El uso de «Nueva conversación» en el procedimiento no demuestra por sí solo aislamiento de memoria del servidor. Tampoco se acreditan aquí pruebas de móvil físico, fallas remotas inducidas ni ausencia de respuestas tardías.
- No se han repetido suites de pruebas ni se han modificado código o configuración como parte de este empaquetado.

## Incorporación al documento

1. Colocar esta carpeta en `taller-02-c2/evidencias/eduardo/`.
2. Conservar los 28 archivos del intento automático y las evidencias históricas.
3. Incorporar las capturas adicionales del inicio si ya se guardaron. No reconstruir una pregunta o un encuadre ausente ni repetir consultas solo para inventar evidencia retrospectiva.
4. Actualizar la sección remota de `documento-Eduardo.md` con el alcance observado y las cinco columnas de la pauta. Mantener pendientes los casos que no cuentan con evidencia suficiente.
5. Confirmar con Sebastián qué release y commit correspondían a estas horas de ejecución. El documento remoto de Sebastián del 14/11/2026 corresponde a otra ejecución y no se debe copiar su versión como si fuera la de estas pruebas.

**Referencia de integración comprobada:** el [PR #83](https://github.com/aleexng1/agentic-ia-grupo-05/pull/83) fue fusionado el 15/11/2026 a las 20:58:11 UTC−03, con commit `96ebca4391f1591933b39790c985142fe1908128`. Eso permite incorporar sus ajustes documentales desde `main`, pero no identifica el código desplegado en Heroku.
