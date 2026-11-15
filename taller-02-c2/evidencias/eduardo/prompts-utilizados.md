# Prompts utilizados · Eduardo · LOCAL · 2026-11-13

## Solicitud real de Eduardo a OpenCode

Transcripción del pedido que dio origen a este aporte (sin credenciales):

```text
Soy Eduardo del Grupo 5. Implementa mi frontend del Taller 2 del Curso 2
en este repositorio, respetando la organización del equipo.

ESTADO ACTUAL
- Estoy en la raíz de agentic-ia-grupo-05.
- La rama es c2t2/eduardo-frontend.
- Ya incorporé origin/main mediante fast-forward hasta 18e7f7d.
- Existe una foto sin seguimiento del taller anterior:
  taller-01-c2/evidencias/eduardo/03-ficha-telefono.jpg
  Consérvala y exclúyela de los commits de este trabajo.

Antes de editar, comprueba el estado actual y lee:
- taller-02-c2/README.md
- taller-02-c2/proyecto/AGENTS.md

MI ALCANCE
- taller-02-c2/proyecto/src/comun/panel.html
- taller-02-c2/proyecto/src/comun/panel.py
- taller-02-c2/documento-Eduardo.md
- taller-02-c2/evidencias/eduardo/

Matías es responsable de la validación de acceso y los errores del
servidor. Alex integra los PR y Sebastián despliega en Heroku.
Explica cualquier dependencia que requiera intervenir archivos ajenos.

IMPLEMENTACIÓN
Reutiliza el panel existente y completa:
1. Pantalla de ingreso con clave enmascarada. Envía la clave ingresada
   mediante X-API-Key y consérvala únicamente en memoria del navegador.
   La autorización debe verificarse en el servidor.
2. Consulta mediante POST /panel/consultar, respetando el contrato actual.
3. Respuesta visible con el agente y motivo proporcionados por el backend.
4. Mensajes claros para 401, entrada inválida, falla del proveedor,
   desconexión, timeout y respuestas que no sean JSON.
5. Indicador de espera y prevención de envíos duplicados.
6. Nueva conversación con un context_id nuevo. Evita que una respuesta
   pendiente aparezca en la conversación nueva.
7. Uso cómodo por teclado y en celular.

Conserva cifras, unidades y condiciones de las respuestas.
Mantén GOOGLE_API_KEY en el servidor y evita exponer secretos en
código, registros, documentación o capturas.

Si la protección de Matías todavía está pendiente de integración,
avanza con el frontend y documenta esa dependencia. Una pantalla de
ingreso por sí sola no demuestra autorización efectiva.

VERIFICACIÓN
Ejecuta pytest desde taller-02-c2/proyecto y comprueba el frontend.
Identifica expresamente las pruebas realizadas con respuestas simuladas.

Prepara la validación real con una pregunta para cada agente,
acceso permitido, acceso rechazado y manejo de errores.
Si falta configuración local, indica qué debo configurar de forma
privada para realizar esas pruebas.

Documenta mi aporte, los prompts utilizados, los ajustes realizados
y cada caso con:
- Entorno LOCAL y fecha.
- Solicitud.
- Resultado esperado.
- Resultado obtenido y evidencia.
- Observaciones y pendientes.

Presenta los cambios y los resultados realmente verificados.
Al preparar un commit, selecciona explícitamente los archivos de mi
trabajo. Yo ejecutaré el push y abriré el PR para revisión de Alex.
```

## Reglas adicionales proporcionadas por el equipo

Se leyeron el README del Taller 2 y `proyecto/AGENTS.md` antes de editar.
El usuario también volvió a proporcionar este último durante la sesión.
Se aplicaron sus reglas de español, funciones de red asíncronas, timeouts explícitos,
errores entendibles sin trazas y separación de responsabilidades. No se modificaron
esas instrucciones. En la fase inicial no hubo un segundo prompt funcional ni solicitudes
a Gemini desde las comprobaciones. La continuación de cierre se transcribe más abajo;
las cuatro consultas manuales reales se distinguen de la automatización.

## Relación entre pedido y ajustes

- «Únicamente en memoria»: quitar persistencia previa del contexto y no almacenar clave.
- «La autorización debe verificarse en el servidor»: ingreso no presenta autorización
  ficticia; diagnósticos `xfail` y dependencia de Matías explícitos.
- «Conserva cifras, unidades y condiciones»: inicialmente texto literal; en el cierre,
  títulos, negritas y código en línea mediante nodos DOM, sin HTML ejecutable ni recálculos.
- «Respuesta pendiente»: aborto más verificación de vigencia, incluso durante lectura JSON.
- «Errores»: clasificación por HTTP y contenido; no reflejar detalles crudos del servidor.
- «Teclado y celular»: atajos, foco visible, tamaño táctil y chat primero en ancho pequeño.

Estos puntos explican decisiones de implementación; **no son prompts adicionales
inventados ni resultados reales de los agentes**.

## Continuación real: cierre del frontend

Pedido recibido el 13-11-2026, sin credenciales:

```text
Continuemos con el cierre del frontend en c2t2/eduardo-frontend.
Respeta README.md y AGENTS.md. Conserva los cambios actuales y la foto
sin seguimiento del taller anterior.

1. Corrige la presentación de Markdown: actualmente aparecen ** alrededor
de títulos y horarios. Usa formato básico seguro mediante nodos DOM.
No insertes respuestas del modelo como HTML sin sanitizar ni alteres
textos, cifras o unidades.

2. Reutiliza las comprobaciones existentes para verificar el cambio,
la vista móvil y Nueva conversación. Diferencia pruebas simuladas de reales.

3. Actualiza documento-Eduardo.md con las cuatro pruebas LOCAL del
13-11-2026, observadas manualmente y revisadas en capturas:
- Eduardo: presupuesto total $2.173.600 CLP.
- Matías: programa 16:00–18:00 y 60 minutos libres informados.
- Alex: tres recintos, características y advertencias correctas.
- Sebastián: servicios 11:00 y 13:30, dietas 65/10/5 y 88 L de agua.

Vincula únicamente capturas existentes. Recupera los logs A2A de estas
ejecuciones si están disponibles, sin secretos. Si faltan, indícalo.

4. Mantén pendiente la validación integrada de seguridad. El PR de
Matías sigue abierto; no marques los dos xfail como aprobados.

Limita las modificaciones a mi zona. No hagas commit ni push.
Entrega un resumen breve de cambios, comprobaciones y pendientes reales,
con los comandos para preparar exclusivamente mis archivos.
```

Aplicación del pedido: se reutilizó la suite existente, se separaron las nuevas
capturas simuladas de las seis originales y de las observaciones manuales comunicadas,
y se recuperaron únicamente fragmentos disponibles del registro real. Las capturas
manuales no se localizaron en aquella fase: no se inventaron archivos ni revisiones independientes.
Se mantuvieron los dos `xfail`, los cambios previos y la foto del Taller 1. Sin commit ni push.

## Continuación: ubicación real de capturas y preparación del índice

Eduardo indicó la ruta real `taller-02-c2/evidencias/eduardo/capturas-manuales-eduardo/`
y pidió corregir los enlaces y el índice de esa carpeta, conservar la aclaración de que
las capturas preceden al ajuste de Markdown, continuar la revisión de codificación A2A
sin inventar fragmentos y preparar solo sus archivos. También solicitó ejecutar
`git diff --cached --check`, mostrar `git diff --cached --stat`, no hacer commit/push
y no repetir pruebas si no cambia código.

En esta continuación se localizaron y revisaron las seis capturas originales, sin
modificarlas. Se corrigieron los enlaces y se documentaron los límites de recuperación
del registro real. No se cambió código ni se repitieron pruebas o consultas al proveedor.
La autorización integrada y los dos `xfail` siguen pendientes.

## Cierre integrado real · solicitud del 14-11-2026

El texto anterior es histórico. La solicitud siguiente reemplaza aquellos pendientes
como objetivo activo; no se inventaron instrucciones ni se incorporaron credenciales:

```text
Continúa el cierre de mi aporte en c2t2/eduardo-frontend.

Lee README.md y AGENTS.md. Comprueba el estado de Git y conserva
cualquier cambio local y la foto del Taller 1. Ejecuta git fetch origin
e incorpora origin/main con git merge --ff-only origin/main.
Si no puede avanzar así, informa la causa sin descartar trabajo.

Revisa los cambios integrados de Alex. Corrige únicamente el mensaje
genérico del 503: cuando no exista un detail JSON válido debe indicar
indisponibilidad temporal, sin afirmar que falta CLAVE_API. Conserva
el detail válido como texto seguro. Ajusta la prueba de 503 con HTML
y conserva la comprobación del 503 JSON del backend.

Ejecuta las pruebas del proyecto y del frontend. Configura
CARPETA_CAPTURAS en una carpeta nueva para conservar las evidencias
anteriores. Registra los resultados reales, sin asumir conteos.

Ejecuta R05, R06, R07 y R09 contra la app LOCAL integrada, con capturas
y registros sanitizados. Para R09 usa un proceso aislado con configuración
temporal; conserva intacto mi .env y no modifiques Heroku.
No muestres claves en comandos, salidas, capturas ni documentos.

Actualiza documento-Eduardo.md con el estado vigente, commit probado,
fecha, resultados y pendientes reales. Conserva las pruebas antiguas
como históricas y diferencia simulaciones de llamadas reales.

Comprueba las referencias funcionales de src/agente_eduardo/demo.html.
Si está sin uso, retira solo esa copia del Taller 2 y documenta la decisión.

Limita los cambios a mi zona. No hagas commit ni push todavía.
Entrega el resumen y la selección exacta de archivos para el nuevo PR.
```

También se volvió a proporcionar `proyecto/AGENTS.md`; sus reglas no se cambiaron.
Resultados medidos, capturas y límites de cada caso:
[`cierre-integrado-2026-11-14/README.md`](cierre-integrado-2026-11-14/README.md).
Se hizo una sola consulta funcional real R05, sin reintentos; R06/R07 son rechazos
reales y R09 es un error real de configuración en otro proceso. No se modificaron
prompts de agentes ni archivos de otras personas. Sin commit ni push.

## Continuación real · pendientes locales y PR #82 · 14-11-2026

Solicitud recibida, sin credenciales:

```text
Continúa en c2t2/eduardo-frontend. El commit d8cce13 ya está publicado y el PR #82 está abierto.

Lee las instrucciones aplicables y taller-02-c2/documento-Eduardo.md. Revisa el estado de Git y conserva cualquier cambio existente.

Completa los pendientes locales documentados:
- R08: con autorización válida, comprobar 400 para texto de espacios y 422 cuando falta texto.
- R10: comprobar el mensaje de desconexión deteniendo únicamente el servidor LOCAL de ensayo; restaurarlo después.
- R11: comprobar el timeout con más de 65 segundos reales de espera en un entorno aislado.
- R12: comprobar una respuesta HTML mediante un servidor de ensayo.

Clasifica R11 y R12 como fallas inducidas en un entorno controlado, sin presentarlas como fallas reales de Gemini o Heroku.

Realiza una consulta real a los agentes de Matías, Alex y Sebastián con el panel actual. Guarda pregunta, respuesta, agente, motivo y capturas sin secretos.

Usa una carpeta nueva para las evidencias. Actualiza mi documento con entorno, fecha, solicitud, resultado esperado, obtenido y observaciones. Corrige también la nota vigente que todavía deja commit/push pendientes: ahora existe el PR #82.

Trabaja solo en mi zona. Conserva .env, capturas históricas y la foto del Taller 1. No modifiques Heroku ni muestres credenciales.

Si no cambia código, no repitas las suites completas ya aprobadas. Si detectas un defecto y lo corriges, ejecuta las pruebas pertinentes. No hagas commit ni push todavía; entrega el resultado y la lista exacta de archivos modificados.
```

También se proporcionaron otra vez las reglas de `proyecto/AGENTS.md`; se conservaron.
Se verificó `d8cce13` en la rama remota. No se modificó el código de producción ni se
repitieron suites completas. Se hicieron una sola consulta funcional a cada uno de los
tres agentes y comprobaciones dirigidas de R08/R10/R11/R12. R11/R12 son condiciones
inducidas sin proveedor; no se presentan como fallas remotas. Las incidencias del
instrumental se conservaron y se completaron sin repetir las consultas reales.

Resultados, procedencia y capturas:
[`pendientes-locales-2026-11-14-144554/README.md`](pendientes-locales-2026-11-14-144554/README.md).
Esta continuación queda sin `git add`, commit ni push; **el PR #82 anterior ya está abierto**.

**Nota de publicación · 15-11-2026:** el párrafo anterior conserva el cierre de aquella
ejecución. Sus evidencias se publicaron después en **`2b754e2`, dentro del PR #82**;
la mención histórica a «sin commit/push» no es un pendiente vigente.

## Comprobación de reproducibilidad · solicitud del 15-11-2026

Solicitud real recibida, sin credenciales:

```text
Comprueba la reproducibilidad de mi entrega y corrige su estado documental.

Lee las instrucciones aplicables y revisa Git. Conserva mi instalación, .env, servidores existentes y archivos ajenos.

1. Usa una copia temporal del commit publicado 2b754e2 y un entorno virtual nuevo con Python 3.12. Sigue la instalación del README sin reutilizar paquetes de mi .venv actual. Registra versiones, comandos y resultados.

2. Comprueba instalación de dependencias, pip check, arranque, panel y /salud. Usa un puerto libre y configura coherentemente el puerto interno de la app. Comprueba rechazo sin clave y con clave incorrecta, y entrada vacía con autorización válida. Usa una clave temporal privada. No consultes Gemini en esta comprobación.

3. Si falta una dependencia o instrucción, documenta el problema y su responsable; no modifiques archivos ajenos ni amplíes el alcance.

4. Corrige en mis documentos las referencias vigentes a “sin commit/push”: las evidencias ya se publicaron en 2b754e2 dentro del PR #82. Conserva las bases probadas, fechas, resultados y registros históricos.

5. Prepara una tabla breve para la futura validación REMOTA, con resultados todavía pendientes y versión desplegada por confirmar.

Guarda únicamente evidencias útiles en mi zona. No repitas las suites completas por rutina, no modifiques Heroku y no hagas commit ni push. Entrega hallazgos, alcance realmente comprobado y lista exacta de cambios.
```

Se leyeron README y `proyecto/AGENTS.md`. Git confirmó el commit en `HEAD`, rama remota
y cabecera del PR #82. Se usaron `git archive`, Python 3.12.10 y una `.venv` nueva fuera
del repositorio, inicialmente solo con pip 25.0.1. Instalación y `pip check`: salida 0;
arranque correcto, panel/salud 200, rechazos 401/401 y vacío/espacios autorizados 400/400.
No se detectó dependencia faltante para estas comprobaciones. No hubo preguntas al
proveedor, suites completas ni pruebas remotas. No se modificaron producción, `.env`,
instalación existente ni archivos ajenos. Las referencias vigentes se corrigieron sin
reescribir los registros históricos; se añadió una tabla REMOTA enteramente pendiente.

Comandos, versiones, resultados y alcance:
[`reproducibilidad-2b754e2-2026-11-15/README.md`](reproducibilidad-2b754e2-2026-11-15/README.md).

**Estado vigente de preparación:** el PR #82 está **fusionado en `main`** mediante
`71df3e8`. Se ejecutaron `git fetch origin` y `git merge --ff-only origin/main` en
`c2t2/eduardo-frontend`, conservando las 12 rutas, publicadas en `8a5bb9b`, PR #84.
La instalación limpia sigue referida a **`2b754e2`**, con sus fechas y resultados
originales. No se repitieron pruebas ni se modificó código.
La validación REMOTA permanece pendiente; versión desplegada: ver
[`pruebas-remotas.md`](../sebastian/pruebas-remotas.md).
