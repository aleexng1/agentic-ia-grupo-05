# Prompts utilizados · Eduardo · registros LOCAL y REMOTO

Los pedidos LOCAL del 13 al 15-11-2026 se conservan con su alcance histórico.
Al final se añaden las solicitudes reales de validación REMOTA, seguimiento e
integración documental del 15-11-2026 y la nueva confirmación del despliegue
aportada por Eduardo, sin credenciales ni prompts reconstruidos. La consolidación
documental del 16-11-2026 registra por separado el guion remoto que no se pudo ejecutar.
Después se incorpora el complemento manual aportado por Eduardo, sin ejecutar ese
guion ni repetir consultas; su alcance vigente se registra al final.

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

**Registro histórico del corte previo a la confirmación de Sebastián.** Se conservan
sus referencias a v10, al despliegue pendiente y a la selección de entonces; la
[confirmación posterior para las cuatro consultas del 15/11](#confirmación-del-despliegue-manual)
se registra más abajo.

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

## Confirmación del despliegue manual

Nueva fuente aportada por Eduardo y solicitud real de actualización documental:

```text
Actualiza únicamente la documentación de Eduardo en c2t2/eduardo-frontend.

Nueva fuente aportada por Eduardo: Sebastián confirmó que Heroku ejecutaba la release v12, desplegada el 15/11/2026 a las 21:44, con identificador 4593bafb y código equivalente a main 96ebca4. Confirmó expresamente que las consultas manuales de 21:51 a 22:04 corrieron contra esa versión.

Registra estos datos como confirmación del responsable del despliegue, sin afirmar una verificación independiente de Heroku ni que ambos identificadores sean el mismo commit.

Actualiza el estado vigente en:
- taller-02-c2/documento-Eduardo.md
- taller-02-c2/evidencias/eduardo/README.md
- taller-02-c2/evidencias/eduardo/manual-autenticada-2026-11-15/README.md
- taller-02-c2/evidencias/eduardo/prompts-utilizados.md

Resuelve el pendiente de identificación del despliegue solo para las cuatro consultas manuales. Conserva los demás límites y la observación de Matías.

Las pruebas automáticas de 20:39–21:07 son anteriores a v12: conserva íntegros sus registros, su referencia histórica a v10 y los 0 POST autenticados. Evita reemplazos globales.

Revisa coherencia, enlaces y git diff --check. Prepara únicamente estos cambios documentales e informa las rutas exactas. Sin repetir pruebas, cambiar configuración, hacer commit ni push.
```

**Confirmación vigente solo para las cuatro consultas del 15/11:** por la nueva
fuente aportada por Eduardo, Sebastián, responsable
del despliegue, confirmó **v12**, desplegada el **15/11/2026 a las 21:44**, con
identificador informado **`4593bafb`** y **código equivalente al de `main` en `96ebca4`**,
y confirmó expresamente las cuatro consultas manuales de **21:51 a 22:04** contra
esa versión. Se resuelve **solo su pendiente de identificación**, por confirmación
del responsable, **sin verificación independiente de Heroku** y **sin afirmar que
`4593bafb` y `96ebca4` sean el mismo commit**.

Los **28 archivos automáticos de 20:39–21:07**, anteriores a v12, conservan íntegros
sus registros, **v10 reportada** y **0 POST autenticados**; no se les atribuye v12 ni
se convierten en aprobaciones. Se mantienen los PNG, los demás límites y la
observación de contenido de Matías (60/40 minutos), sin completar encuadres ausentes.
La lista y la revisión documental de la integración anterior quedan como históricas,
sin regenerarlas. Se preparan **únicamente los cuatro documentos solicitados**, con
revisión de coherencia, enlaces y `git diff --check`; sin consultas, suites, cambios
de configuración, commit ni push.

## Consolidación del cierre · solicitud y revisión documental del 16-11-2026

**Registro del corte anterior a recibir el complemento manual.** Se conserva su
limitación de acceso y su selección de entonces; la integración posterior se
documenta en el apartado siguiente, sin convertir aquel intento en una ejecución aprobada.

Solicitud real recibida, sin credenciales:

```text
Continúa en c2t2/eduardo-frontend. Necesito consolidar mi cierre antes de hacer otro commit. Conserva los cuatro documentos preparados y todas las evidencias anteriores.

Revisa README, AGENTS.md y los pendientes de mi documento. Trabaja únicamente en mi zona.

1. Completa una comprobación REMOTA breve en el panel de Heroku, con un máximo de tres consultas normales, sin reintentos automáticos:
   - Primera: “Estima el presupuesto ficticio en CLP para una feria de 80 personas y 4 horas”. Observa espera, controles bloqueados y cantidad de POST ante un segundo intento de envío desde la interfaz.
   - Segunda, en la misma conversación: “Para esa misma feria, cambia solo la duración a 3 horas y recalcula el presupuesto, indicando cuántos asistentes consideraste”. Comprueba la continuidad y que se conserva context_id.
   - Pulsa Nueva conversación y envía: “Estima el presupuesto ficticio en CLP para una feria de 20 personas y 2 horas”. Comprueba limpieza del historial y cambio de context_id. Esto acredita el cambio de conversación del panel, no aislamiento completo del servidor.

2. Comprueba la presentación de una respuesta autenticada a 390 y 320 px, sin volver a consultar al agente. Registra desborde, legibilidad y acceso a controles. Etiqueta correctamente “móvil emulado”, sin afirmar prueba en teléfono físico.

Utiliza una sesión autenticada disponible. Nunca leas, imprimas ni guardes la clave. Si no tienes acceso a mi navegador autenticado, entrega inmediatamente el guion manual mínimo; no inicies otra espera automática prolongada para ingresar la clave.

3. Si siguen disponibles los registros anteriores de Network, recupera únicamente Payload y Response para completar las preguntas que faltan en las capturas históricas. No exportes HAR ni cabeceras de solicitud. Si no están disponibles, conserva esa limitación sin reconstruir preguntas ni repetir las cuatro consultas anteriores.

4. Actualiza mi documento y los índices con resultados realmente observados y las cinco columnas acordadas. Conserva v12 y los identificadores confirmados por Sebastián exclusivamente para las cuatro consultas manuales del 15/11. Las nuevas comprobaciones deben llevar su propia fecha; no supongas que continúa desplegada la misma versión.

No provoques errores en Heroku ni cambies configuración. Mantén las pruebas locales de fallos como evidencia LOCAL. Si una comprobación falla, registra el resultado y su alcance, sin marcarla aprobada.

Prepara una única selección final de archivos de mi zona, revisa privacidad y git diff --cached --check. Evita duplicar evidencias y repetir suites completas si no cambia código. No hagas commit ni push.

Entrega un resumen breve: completado, limitaciones restantes y comandos para publicar todo junto.
```

Se revisaron el README raíz, el del Taller 2, `proyecto/AGENTS.md`, los pendientes
de Eduardo y Git. Se conservaron los cuatro documentos preparados en el índice y
se consolidan en **la misma selección de cuatro rutas**, sin copiar evidencias.

**Alcance real:** no hay acceso al navegador autenticado de Eduardo desde esta
sesión. Se entregó inmediatamente el guion manual, sin leer la clave, abrir otro
navegador, esperar autenticación ni enviar solicitudes a Heroku: **0 consultas nuevas**.
Continuidad, espera/duplicados con acceso aceptado, Nueva conversación autorizada
y respuesta a 390/320 px quedan **no ejecutados o no inspeccionados**, no aprobados
ni fallas observadas del servicio. Tampoco se recuperaron Payload/Response históricos;
no se reconstruyeron preguntas ni se repitieron las cuatro consultas del 15/11.

La fecha **16/11/2026** corresponde a revisión documental. El guion exige fecha/hora
con zona de una ejecución efectiva, cuya versión **no está identificada**; no se
extiende a ella la confirmación de Sebastián. Se conservan los registros automáticos,
los PNG, los límites, la observación de Matías y las fallas **LOCAL** con su alcance.
Matriz y [guion pendiente](../../documento-Eduardo.md#guion-manual-mínimo--no-ejecutado).
Sin cambios de código/configuración ni repetición de suites; revisión de privacidad,
enlaces y `git diff --cached --check`, sin commit ni push.

## Integración del complemento REMOTO MANUAL · 16-11-2026

Solicitud real recibida, sin credenciales:

```text
Integra la carpeta evidencias/eduardo/complemento-remoto-manual-2026-11-16/ y conserva los cuatro documentos ya preparados.

Actualiza documento-Eduardo.md, el índice de evidencias y prompts-utilizados.md. Lee el README del complemento y respeta su alcance:
- Continuidad observada: recuperó 80 asistentes y la duración actualizada de 180 minutos; presupuesto de $1.742.400 CLP y HTTP 200.
- Visualización del presupuesto y controles en móvil emulado.
- La barra acredita 390 × 844; la captura del paso de 320 está recortada y no confirma independientemente el ancho.
- La versión desplegada el 16/11 no está confirmada; conserva v12 únicamente para las cuatro consultas del 15/11.

Mantén los históricos y los demás límites. No ejecutes más consultas ni repitas suites; no modifiques código ni Heroku.

Revisa enlaces, privacidad y git diff --cached --check. Prepara exclusivamente los documentos de mi zona y los siete archivos del complemento. Muestra la selección final. Sin commit ni push.
```

Se leyó el [README del complemento](complemento-remoto-manual-2026-11-16/README.md)
y se revisaron visualmente sus seis PNG. Se conservan **los siete archivos originales
sin modificar sus bytes**, los cuatro documentos ya preparados y las evidencias
anteriores. Esta integración actualiza únicamente `documento-Eduardo.md`, el índice
de evidencias y este registro de prompts; mantiene sin nuevas ediciones el README
manual del 15/11 ya preparado.

**Alcance incorporado:** continuidad de contenido con **80 asistentes y 180 minutos**,
subtotal **$1.584.000 CLP**, contingencia **$158.400** y total **$1.742.400 CLP**;
la captura 03 muestra **POST 200 OK, application/json**, con `Date` del 16/11/2026,
**12:47:37 GMT / 09:47:37 UTC−03:00**, no latencia ni hora exacta de captura. Las dos
primeras respuestas piden el tipo de evento; la tercera pregunta lo completa sin
repetir asistentes o duración. No equivale al caso previsto de Nueva conversación
con 20 personas y 2 horas ni acredita la conservación de `context_id`.

La captura 04 acredita **390 × 844**; la 05 muestra presupuesto y controles sin
barra de dimensiones, asociados por la secuencia. La 06 corresponde al paso
declarado de 320 px, pero **el recorte no verifica independientemente ese ancho**.
La observación es visual, en **móvil emulado**, no una medición de `scrollWidth`,
ausencia de desborde global ni prueba de teléfono físico o teclado virtual.

**Versión del 16/11 no confirmada.** La confirmación de Sebastián sobre v12 y sus
identificadores se mantiene solo para las cuatro consultas del 15/11, sin equiparar
commits ni afirmar verificación independiente. Permanecen los demás límites, la
observación 60/40 de Matías, los 28 registros automáticos con **0 POST autenticados**
y las fallas **LOCAL**, sin reinterpretarlos como resultados de este complemento.

Se prepara una única selección de **11 rutas: cuatro documentos modificados y los
siete archivos nuevos del complemento**, enumeradas en
[`documento-Eduardo.md`](../../documento-Eduardo.md#preparación-documental-de-este-cierre).
Revisión de enlaces y privacidad de los textos y seis imágenes, sin claves ni
Request Headers visibles; los Remote Address son del servidor remoto. Sin HAR,
nuevas consultas, suites, cambios de código/configuración o Heroku, commit ni push.
