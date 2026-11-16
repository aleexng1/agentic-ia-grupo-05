# Complemento REMOTO MANUAL: continuidad y vistas móviles

Fecha de la sesión: 16 de noviembre de 2026, Chile (America/Santiago).
Aplicación: https://grupo05-taller2-seba-94d12914f3eb.herokuapp.com/

Fuente: capturas aportadas por Eduardo desde su navegador. Este paquete organiza seis imágenes originales, sin editar sus píxeles. No representa una nueva ejecución automática ni una nueva consulta al proveedor.

## Resultados observados

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| REMOTO MANUAL, Heroku, Chrome, 16/11/2026 | Presupuesto para 80 personas y 4 horas; luego cambiar a 3 horas; finalmente aclarar que la feria es tecnológica, sin repetir asistentes ni duración. | Recuperar los 80 asistentes, aplicar la última duración de 3 horas y calcular después de completar el tipo de evento. | La respuesta muestra 80 asistentes, 180 minutos (3 horas), evento tecnológico, subtotal $1.584.000 CLP, contingencia $158.400 y total $1.742.400. La solicitud seleccionada en la captura 03 muestra POST /panel/consultar, 200 OK y application/json. | Continuidad conversacional observada en este caso. El tipo de evento faltaba en el guion inicial y fue solicitado por el agente. No se han comparado los context_id ni verificado aislamiento entre sesiones. |
| REMOTO MANUAL, Heroku, visualización con móvil emulado, 16/11/2026 | Mostrar la conversación existente en el ancho de 390 px previsto en el guion. | Leer mensajes y acceder al campo de texto y al botón Enviar. | La captura 04 acredita el ajuste 390 × 844 y muestra parte de la conversación. La captura 05, recortada posteriormente durante esta secuencia, muestra el presupuesto y los controles. No se aprecia recorte lateral de estos elementos en las zonas visibles. | Observación visual. La captura 05 no incluye la barra de dimensiones; por sí sola no mide el viewport. No se midió scrollWidth ni se probó un teléfono físico. |
| REMOTO MANUAL, Heroku, visualización estrecha, 16/11/2026 | Reducir a 320 × 844 según el guion, conservando la respuesta. | Mantener legibles el presupuesto y los controles en la vista estrecha. | La captura 06 muestra el presupuesto, texto ajustado a varias líneas, campo de entrada y botón Enviar dentro de la zona visible. | Corresponde al paso de 320 px de la secuencia, pero la barra de dimensiones quedó fuera del recorte: ancho exacto no verificado en la imagen. No se afirma una medición independiente de 320 × 844 ni ausencia de desborde fuera de lo visible. |

La cabecera Date de la respuesta seleccionada en la captura 03 es `Mon, 16 Nov 2026 12:47:37 GMT`, equivalente a las 09:47:37 de Chile. Es la fecha HTTP observada, no una medición de latencia ni la hora exacta de captura.

## Secuencia de la conversación

1. «Estima el presupuesto ficticio en CLP para una feria de 80 personas y 4 horas.»
2. El agente solicita el tipo de evento.
3. «Para esa misma feria, cambia solo la duración a 3 horas y recalcula el presupuesto, indicando cuántos asistentes consideraste.»
4. El agente vuelve a solicitar el tipo de evento, que aún no había sido indicado.
5. «Es una feria tecnológica. Calcula el presupuesto e indica cuántos asistentes y qué duración estás considerando.»
6. La respuesta utiliza 80 asistentes y 180 minutos y muestra el presupuesto.

Las respuestas de aclaración no se contabilizan como presupuestos calculados ni como errores HTTP. La captura 02 muestra la secuencia, pero tiene seleccionada una solicitud anterior en Network; para el 200 del presupuesto final se utiliza la captura 03.

## Archivos

| Archivo del paquete | Original aportado | Qué muestra |
| --- | --- | --- |
| [01-tipo-de-evento-pendiente.png](01-tipo-de-evento-pendiente.png) | image(20261116-124527).png | Primeras dos preguntas y solicitudes del tipo de evento. |
| [02-secuencia-aclaracion.png](02-secuencia-aclaracion.png) | Captura de pantalla 2026-11-16 094922.png | Las tres preguntas de la secuencia; el último envío completa el tipo. |
| [03-continuidad-presupuesto-200.png](03-continuidad-presupuesto-200.png) | Captura de pantalla 2026-11-16 095008.png | 80 asistentes, 180 minutos, presupuesto y HTTP 200 del resultado seleccionado. |
| [04-movil-390-dimensiones.png](04-movil-390-dimensiones.png) | image(20261116-130043).png | Barra 390 × 844 y conversación en emulación. |
| [05-movil-390-presupuesto-controles.png](05-movil-390-presupuesto-controles.png) | image(20261116-130533).png | Detalle de presupuesto y controles; tamaño asociado por la secuencia, no visible en el recorte. |
| [06-movil-320-declarado-presupuesto-controles.png](06-movil-320-declarado-presupuesto-controles.png) | image(20261116-130742).png | Vista estrecha aportada después del paso de 320 px; barra de dimensiones no visible. |

## Límites y versión

- Estas capturas no acreditan nuevos resultados sobre duplicados durante consultas autorizadas, respuesta tardía, cambio de context_id, aislamiento de conversaciones o fallos inducidos en Heroku. Se conservan las evidencias locales de esos comportamientos con su alcance original.
- Las filas acumuladas de Network no permiten deducir por sí solas duplicación de una solicitud. La lista vacía en la vista móvil no invalida la observación visual ni demuestra cuántos POST hubo anteriormente.
- No se probó un dispositivo móvil físico ni el teclado virtual. Los recortes no prueban la ausencia de desborde en toda la página.
- La identificación de la release y del commit para esta sesión del 16/11 no se verificó. La confirmación de Sebastián sobre v12, identificador Heroku 4593bafb y código equivalente a main 96ebca4 corresponde a las cuatro consultas manuales del 15/11; no se extiende automáticamente a estas capturas.
- El intento automático histórico con 0 POST autenticados permanece separado. Este complemento no altera ese resultado.
- La observación anterior sobre los 60/40 minutos en la respuesta de Matías permanece sin cambios.
- No se incluyen claves, Request Headers, exportaciones HAR ni credenciales. Los Remote Address visibles corresponden al servidor remoto. La preparación del paquete no modifica la aplicación, Heroku ni los archivos del repositorio en el notebook.

## Incorporación

Extraer la carpeta `complemento-remoto-manual-2026-11-16` dentro de `taller-02-c2/evidencias/eduardo/`. Enlazar este README desde el documento y el índice de Eduardo. Mantener las evidencias históricas y los límites descritos; no sustituirlos por una afirmación de validación remota completa.
