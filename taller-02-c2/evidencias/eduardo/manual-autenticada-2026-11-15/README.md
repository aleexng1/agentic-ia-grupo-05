# Consultas manuales autenticadas · Heroku · 15/11/2026

Estas cuatro capturas fueron aportadas por Eduardo durante la validación manual del panel. Se incluyen sin modificar sus píxeles ni sus bytes. Cada imagen muestra una petición POST a `/panel/consultar` con **200 OK**, una respuesta en el panel, el agente identificado y el motivo de selección.

**URL observada:** https://grupo05-taller2-seba-94d12914f3eb.herokuapp.com/

## Identificación del despliegue · confirmación del responsable

Según la [nueva fuente aportada por Eduardo](../prompts-utilizados.md#confirmación-del-despliegue-manual), **Sebastián, responsable del despliegue, confirmó** que Heroku ejecutaba la **release v12**, desplegada el **15/11/2026 a las 21:44**, con identificador informado **`4593bafb`** y **código equivalente al de `main` en `96ebca4`**. Confirmó expresamente que las cuatro consultas manuales de **21:51 a 22:04** corrieron contra esa versión.

Queda resuelto **solo el pendiente de identificación del despliegue para estas cuatro consultas**, por confirmación del responsable. **No es una verificación independiente de Heroku ni se afirma que `4593bafb` y `96ebca4` sean el mismo commit.** La equivalencia de código es la comunicada por Sebastián; no se deduce de `main` ni de las capturas, que no identifican por sí solas release o commit.

## Resultados observables

Las horas siguientes proceden de la cabecera HTTP `Date` visible, convertida de UTC a America/Santiago (UTC−03). Son horas de respuesta del servidor, no mediciones de duración ni horas de creación de los PNG.

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
|---|---|---|---|---|
| REMOTO · Heroku · 15/11/2026 · 21:51:58 UTC−03 | Consulta de presupuesto de feria; pregunta exacta fuera del encuadre. | 200, respuesta de presupuesto, agente Eduardo y motivo visibles. | **Comprobado en captura:** POST 200 OK; Agente de Eduardo; subtotal $1.976.000, contingencia $197.600 y total $2.173.600. | [01-eduardo-remoto-200.png](01-eduardo-remoto-200.png). Se muestra el final de la respuesta. Falta adjuntar la vista del inicio con la pregunta, si se conserva. |
| REMOTO · Heroku · 15/11/2026 · 21:59:03 UTC−03 | «Propón un programa para una feria cultural familiar de 3 horas, comenzando a las 16:00. Indica los horarios y los minutos libres.» | 200, programa, agente Matías y motivo visibles. | **Comprobado en captura:** POST 200 OK; Agente de Matias; bloques 16:00–17:00, 17:00–17:30, 17:30–18:00 y 18:00–19:00; informa cero minutos libres. | [02-matias-remoto-200.png](02-matias-remoto-200.png). Pregunta y respuesta visibles. Observación de contenido: la visita tiene un bloque de 60 minutos y una descripción de unos 40 minutos; el margen no se explica. No se atribuye esa diferencia al frontend. |
| REMOTO · Heroku · 15/11/2026 · 22:01:15 UTC−03 | Consulta de recintos para una feria; pregunta exacta fuera del encuadre. | 200, recomendaciones, agente Alex y motivo visibles. | **Comprobado en captura:** POST 200 OK; Agente de Alex; recintos con capacidad, accesibilidad, servicio de comida y observaciones. | [03-alex-remoto-200.png](03-alex-remoto-200.png). Se ve parte de la lista y el final de la respuesta. Falta adjuntar el inicio con la pregunta, si se conserva. |
| REMOTO · Heroku · 15/11/2026 · 22:03:25 UTC−03 | Consulta de catering y menús especiales; pregunta exacta fuera del encuadre. | 200, propuesta de catering, agente Sebastián y motivo visibles. | **Comprobado en captura:** POST 200 OK; Agente de Sebastian; box lunch de 13:30, menús diferenciados y 88 litros de agua con 10 % de margen. | [04-sebastian-remoto-200.png](04-sebastian-remoto-200.png). Se ve el final de la respuesta. Falta adjuntar el inicio con la pregunta, si se conserva. |

## Relación con las evidencias anteriores

- Esta ejecución manual es posterior y distinta de la [validación automática y del cliente](../validacion-remota-2026-11-15-203522/README.md) de **20:39–21:07**, anterior a v12 (21:44). Su fase autenticada terminó esperando el ingreso privado y registró **0 POST autenticados**. Sus **28 archivos originales** y su referencia histórica a **v10 reportada** se conservan íntegros; no se les atribuye v12 ni se transforma el intento en una prueba automática aprobada.
- Los rechazos 401, panel/salud, visualización móvil emulada y controles observados durante un 401 pertenecen a sus evidencias anteriores. Estas cuatro capturas no vuelven a ejecutar ni amplían automáticamente ese alcance.
- Las capturas acreditan la respuesta HTTP y la salida visible del panel. No contienen trazas internas que demuestren por sí solas cada salto A2A ni la llamada al proveedor.
- El uso de «Nueva conversación» en el procedimiento no demuestra por sí solo aislamiento de memoria del servidor. Tampoco se acreditan aquí pruebas de móvil físico, fallas remotas inducidas ni ausencia de respuestas tardías.
- No se han repetido suites de pruebas ni se han modificado código o configuración como parte de este empaquetado.

## Incorporación al documento

1. Colocar esta carpeta en `taller-02-c2/evidencias/eduardo/`.
2. Conservar los 28 archivos del intento automático y las evidencias históricas.
3. Incorporar las capturas adicionales del inicio si ya se guardaron. No reconstruir una pregunta o un encuadre ausente ni repetir consultas solo para inventar evidencia retrospectiva.
4. Actualizar la sección remota de `documento-Eduardo.md` con el alcance observado y las cinco columnas de la pauta. Mantener pendientes los casos que no cuentan con evidencia suficiente.
5. **Identificación resuelta solo para estas cuatro consultas** mediante la confirmación de Sebastián registrada arriba; no quedan aprobados otros casos ni se acredita una verificación independiente de Heroku. El documento remoto de Sebastián del 14/11/2026 corresponde a otra ejecución y no se debe copiar su versión como si fuera la de estas pruebas.

**Referencia de integración comprobada:** el [PR #83](https://github.com/aleexng1/agentic-ia-grupo-05/pull/83) fue fusionado el 15/11/2026 a las 20:58:11 UTC−03, con commit `96ebca4391f1591933b39790c985142fe1908128`. Eso permite incorporar sus ajustes documentales desde `main`, pero por sí solo no identifica el código desplegado en Heroku. La correlación de estas consultas con v12 procede de la confirmación de Sebastián.

## Seguimiento documental · 16/11/2026

No se dispone de acceso al navegador autenticado ni a su Network histórico desde
esta sesión. **No se recuperaron Payload/Response nuevos** para Eduardo, Alex o
Sebastián; sus preguntas exactas y los inicios de respuesta siguen sin documentar.
Esto no demuestra que los registros hayan desaparecido del navegador de Eduardo.
No se reconstruyeron preguntas, repitieron consultas ni modificaron los PNG.

La [consolidación y el guion pendiente](../../../anexo-Eduardo-historico.md#consolidación-del-cierre--2026-11-16)
registran por separado las nuevas comprobaciones **no ejecutadas**. La fecha de
este seguimiento es documental: no añade resultados remotos ni extiende v12 o sus
identificadores a una ejecución posterior. Permanecen los demás límites y la
observación de contenido de Matías.
