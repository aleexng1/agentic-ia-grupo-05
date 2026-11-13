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
