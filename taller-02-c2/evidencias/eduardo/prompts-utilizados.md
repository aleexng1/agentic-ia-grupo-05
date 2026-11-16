# Prompts utilizados · Eduardo · registros LOCAL y REMOTO

Los pedidos LOCAL del 13 al 15-11-2026 se conservan con su alcance histórico.
Al final se añaden las solicitudes reales de validación REMOTA, seguimiento e
integración documental del 15-11-2026, sin credenciales ni prompts reconstruidos.

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

**Estado de preparación al cierre LOCAL (histórico):** el PR #82 está **fusionado en `main`** mediante
`71df3e8`. Se ejecutaron `git fetch origin` y `git merge --ff-only origin/main` en
`c2t2/eduardo-frontend`, conservando las 12 rutas, publicadas en `8a5bb9b`, PR #84.
La instalación limpia sigue referida a **`2b754e2`**, con sus fechas y resultados
originales. No se repitieron pruebas ni se modificó código.
En ese corte la validación REMOTA permanecía pendiente; el
[informe de Sebastián](../sebastian/pruebas-remotas.md) corresponde al día 14 y no
identifica la versión desplegada durante las capturas manuales posteriores del día 15.

## Validación REMOTA · solicitud real del 15-11-2026

Pedido recibido, sin credenciales:

```text
Continúa mi validación REMOTA del Taller 2 en c2t2/eduardo-frontend.

URL: https://grupo05-taller2-seba-94d12914f3eb.herokuapp.com/

Lee README.md, AGENTS.md y documento-Eduardo.md del taller. Revisa el estado de Git y conserva los cambios existentes.

Sebastián informó release v10. Regístrala como versión reportada; el commit desplegado sigue por confirmar. No equipares automáticamente origin/main con lo desplegado.

Prueba el panel real:
- Acceso rechazado sin clave y con una clave ficticia.
- Acceso permitido con la CLAVE_API vigente de Heroku.
- Una consulta a cada agente, comprobando respuesta, agente y motivo.
- Nueva conversación, estado de espera y ausencia de envíos duplicados.
- Visualización en escritorio y móvil; distingue emulación de dispositivo real.

La clave de Google nunca se ingresa en el panel. No asumas que la CLAVE_API local coincide con Heroku. Si falta la remota, detén únicamente las pruebas autenticadas y permite que yo la ingrese privadamente en el navegador, sin mostrarla en conversación, logs ni capturas.

Guarda evidencias nuevas en mi carpeta, con fecha, URL y alcance. Usa las cinco columnas: Entorno y fecha, Solicitud, Esperado, Obtenido y Observaciones. No marques pruebas pendientes como aprobadas.

Mientras el PR #83 siga pendiente, conserva el informe remoto en una carpeta nueva para evitar conflictos con los ajustes documentales de Alex.

No provoques fallas en Heroku ni cambies configuración. No repitas suites locales completas. Al terminar, informa resultados y archivos modificados, sin commit ni push.
```

Se conservaron los registros en
[`validacion-remota-2026-11-15-203522/`](validacion-remota-2026-11-15-203522/README.md).
Hubo panel/salud 200 y rechazos 401 reales. El ingreso privado no se completó:
la ejecución autenticada original terminó por `TimeoutError` y registró **0 POST
autenticados**, sin respuestas o capturas de agentes. No se reemplazó la clave
remota por la local ni se consultó Config Vars para obtenerla.

## Seguimiento REMOTO · solicitud real del 15-11-2026

```text
Continúa siguiendo las consultas autenticadas ya iniciadas, sin duplicarlas.

Para aprobar cada agente, comprueba: HTTP 200, respuesta útil, agente correcto y motivo visible. Conserva pregunta, respuesta y captura sin credenciales.

Completa únicamente lo pendiente del panel: Nueva conversación, estado de espera y ausencia de envíos duplicados. Mantén “móvil emulado” como tal.

Cierra el informe de validacion-remota-2026-11-15-203522/ con:
- Pruebas aprobadas, fallidas y pendientes.
- Evidencia correspondiente a cada resultado.
- Fecha y URL.
- Release v10 reportada por Sebastián; commit desplegado pendiente de confirmación.

Si alguna consulta falla o queda detenida, registra el error observado antes de decidir un reintento. No provoques fallas en Heroku.

Entrega el resumen final y la lista exacta de archivos modificados o nuevos. Conserva los archivos anteriores y las claves privadas. Sin commit ni push.
```

Se inspeccionó la misma ejecución, sin iniciar otra ni reenviar consultas. Tras la
aclaración de Eduardo («No hay ventana o clave») y el `TimeoutError` registrado,
no se reintentó la autenticación. Se hizo solo un caso independiente del cliente
con clave ficticia y **401 esperado**: espera visible, cuatro intentos extra pero
**1 POST total**, recuperación y limpieza con Nueva conversación. No acredita
espera/duplicados durante una consulta aceptada ni una respuesta útil de agente.
El [cierre original](validacion-remota-2026-11-15-203522/README.md) y sus pendientes
se conservan íntegros, con su fecha y su alcance propios.

## Integración documental y capturas manuales · solicitud real del 15-11-2026

```text
Continúa en c2t2/eduardo-frontend. Lee las instrucciones del proyecto, revisa git status y trae origin/main. Integra sus cambios conservando mi trabajo; el PR #83 ya está fusionado.

Incorpora las cuatro capturas y el README de:
taller-02-c2/evidencias/eduardo/manual-autenticada-2026-11-15/

Actualiza documento-Eduardo.md, el índice de mis evidencias y mis prompts utilizados:

- Registra las cuatro consultas como pruebas REMOTAS MANUALES, con HTTP 200, respuesta, agente y motivo.
- Conserva el intento automático anterior: terminó esperando el ingreso privado y registró 0 POST autenticados. Es otra ejecución.
- Usa las cinco columnas de la pauta y conserva los resultados históricos.
- Mantén la observación de contenido de Matías: bloque de 60 minutos con descripción de unos 40.
- Incorpora las capturas del inicio de Eduardo, Alex y Sebastián si están disponibles. Si faltan, documenta esa limitación sin reconstruirlas.
- Mantén la versión desplegada por confirmar: v10 fue reportada previamente; el SHA de main no demuestra qué commit ejecutaba Heroku.
- Conserva pendientes los casos que estas capturas no acreditan.

Revisa enlaces y privacidad. No repitas consultas ni suites, ni cambies código o configuración.

Prepara en el índice únicamente mi aporte documental y sus evidencias, mediante una lista exacta. Ejecuta git diff --cached --check y entrega las rutas preparadas y los pendientes restantes. Sin commit ni push.
```

Se leyeron las instrucciones y se verificó Git. `git fetch origin` y
`git merge --ff-only origin/main` incorporaron el PR #83 mediante avance
**`8a5bb9b` → `96ebca4`**, sin conflictos ni commit nuevo y conservando los
archivos locales. No se reeditaron código/configuración ni se ejecutaron consultas
o suites. Los cambios de código/configuración que ya contenía `main` pertenecen
a esa integración, no a esta selección documental.

Se revisaron las cuatro capturas y su
[README original](manual-autenticada-2026-11-15/README.md): **cuatro pruebas REMOTAS
MANUALES con POST 200, respuesta, agente y motivo visibles**. Se preservan los PNG,
el README aportado y los 28 archivos del intento automático. El margen de Matías
(60 minutos frente a unos 40) sigue observado. No se localizaron los inicios
remotos de Eduardo/Alex/Sebastián; no se reconstruyeron preguntas o respuestas.
v10 sigue como reportada y el despliegue por confirmar. Los casos no acreditados
no se aprueban; el móvil anterior sigue rotulado como emulado.

La lista cerrada para `git add` está en
[`manual-autenticada-2026-11-15/archivos-para-indice.txt`](manual-autenticada-2026-11-15/archivos-para-indice.txt).
Solo contiene documentos y evidencias de Eduardo, incluidos los dos scripts
originales del instrumental anterior **sin cambios y sin ejecutarlos**. Excluye
claves, `.env`, `.venv`, la foto del Taller 1 y aportes de otras personas.
Se comprueban enlaces, privacidad y el índice con `git diff --cached --check`;
no se realiza commit ni push.
