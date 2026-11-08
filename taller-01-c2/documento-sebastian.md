# Documento de entrega · Taller A2A · Grupo 5 · Sección de Sebastian Mardones

**Tema del grupo:** planificador de ferias y eventos.
**Agente:** Agente de Sebastian · comida y opciones de catering · `src/agente_sebastian/` · puerto 8006.

> Sección para integrar en el documento del grupo (lo arma Alex). Sigue la misma
> estructura que la de Matias. Lo pendiente (capturas 01 y 03, catálogo y ronda) se
> completa a medida que se hace.

## 1. Blueprint

Ver `blueprint-Sebastian.md`. La herramienta es
`armar_catering(tipo_evento, personas, duracion_minutos, hora_inicio, restricciones)`.

Decisiones de diseño tomadas antes de programar:

- **Sin precios en los datos.** Los costos los responde el agente de Eduardo. Si la
  herramienta no tiene precios, el modelo no puede mezclarlos por error.
- **La herramienta hace todas las cuentas**: horarios, cantidades con 10 % de margen,
  agua y menús por dieta. Es la lección del agente de Matias, cuyo modelo calculaba mal
  los minutos.
- **Mismo vocabulario que Matias** para `tipo_evento` (tecnologico, gastronomico,
  cultural, infantil) y para la duración (30 a 480 minutos).

## 2. Cómo se construyó el agente

### Herramienta usada

Claude Code (asistente de programación de Anthropic), no OpenCode. Sebastian dio las
instrucciones y tomó las decisiones; el asistente escribió el código copiando el molde
de `agente_matias`, que a su vez sigue el agente de viajes de la clase.

### Instrucciones (prompts) que dio Sebastian, textuales

Se omite solo la clave de acceso de la dirección de la plataforma.

1. Plan y consultas:

   > #Rol: Experto en agentes de IA
   > ##Contexto: tarea [URL de la plataforma] en está ruta está el avance de matías D:\Certificate Agentic IA\grupo-5-matias-referencia
   > Para todo el desarrollo del producto usa esta carpeta : D:\Certificate Agentic IA\grupo-05-Sebastian
   > Output: Haz un plan en .md y hazme las consultas que sean necesarias

2. Respuestas a las consultas del plan: sin precios (los costos son de Eduardo), partir
   de una copia del proyecto de Matias, copiar la clave de Gemini del proyecto de la clase
   y entregarle a Matias una carpeta con la misma estructura que la suya.

3. Construcción del agente (pasos A a E del plan: proyecto, `.env`, blueprint, agente y tests):

   > Sí, empieza

4. Servidor, mensaje A2A y ficha mejorada:

   > Sí, sigue

5. Túnel de Cloudflare:

   > Sí, ábrelo hoy

6. Cierre del túnel y del agente, después de sacar las capturas:

   > Ya capturé, ciérralos

7. Capturas del túnel para el día siguiente:

   > Mañana, túnel nuevo

8. Paquete para el grupo:

   > Si cumple, empaquétalo en un .zip para compartirlo con Matías

9. Subida al repositorio del grupo: pegó los dos mensajes de Alex (las instrucciones y el
   prompt para el agente de código). Respondió que su rama se prepara en una carpeta aparte
   (para no tocar su rama `tf/herramientas`), confirmó que su avance está en
   `grupo-05-Sebastian` y pidió revisar el contenido antes de subir.

### Qué se cambió después de verlo funcionar

- A "¿Cuánto me cuesta el catering para 100 personas?" el agente no dijo que los costos
  no eran de su tema: pidió el tipo de evento y la duración para cotizar. Se movieron
  los límites al comienzo del prompt, con una regla explícita para precios. Ahora
  responde: "Los costos y presupuestos no son de mi especialidad, pero con gusto puedo
  armarte una propuesta de comida sin precios…".
- A una pregunta mixta (comida y recinto para una feria infantil) respondió bien la comida,
  pero ignoró la parte del recinto sin avisar. Se agregó la regla "responde solo la parte
  de comida y termina diciendo qué parte no respondes". Ahora termina con "Los recintos,
  lugares o capacidad no son de mi especialidad".
- Saludaba y se presentaba en cada respuesta: se agregó "no saludes ni te presentes,
  salvo que te pregunten quién eres".
- Las respuestas decían "152 vasos de Vaso de fruta picada": el plato se renombró a
  "Fruta picada".

### Pruebas automáticas de la herramienta

`python -m pytest tests -q` → 12 pruebas pasan. Cubren horarios (coffee break, almuerzo
según tipo de evento, cóctel de noche, colación infantil, evento corto), cantidades con
margen sin errores de redondeo, agua, dietas con y sin cantidad, alias ("Feria
Tecnológica", "celíacos"), datos inválidos (responde con un motivo, sin error) y que los
datos no incluyan precios.

## 3. Prueba en terminal

### Diagrama (`python main.py sebastian --diagrama`)

```
graph TD;
	__start__([<p>__start__</p>]):::first
	model(model)
	tools(tools<hr/><small><em>__tools = armar_catering</em></small>)
	__end__([<p>__end__</p>]):::last
	__start__ --> model;
	model -.-> __end__;
	model -.-> tools;
	tools -.-> model;
```

### Saltos

Captura `evidencias/sebastian/01-saltos.png`, con estos dos comandos:

- `python main.py sebastian "Voy a hacer una feria tecnológica de 4 horas desde las 10:00 para 150 personas, 12 son veganas. ¿Qué les sirvo?" --saltos`
  (se ve `Herramienta: armar_catering` con sus argumentos; 3 saltos).
- `python main.py sebastian "¿Qué vuelos hay a Lima?" --saltos` (lo rechaza; 1 salto).

### Mensaje por A2A

Respuesta completa en `evidencias/sebastian/respuesta-a2a.json`; el texto está en
`result.message.parts[0].text`. Pregunta: "Voy a hacer una feria infantil de 3 horas
desde las 11:00 para 80 personas y 6 niños son celíacos, ¿qué les damos de comer?".
El agente propuso un almuerzo infantil a las 12:00 (82 porciones de menú general para
74 niños y 7 porciones sin gluten para 6) y 88 litros de agua, sin precios.

Comando (PowerShell, con el agente corriendo en el 8006):

```powershell
$cuerpo = @{ jsonrpc="2.0"; id="1"; method="SendMessage"; params=@{ message=@{ role="ROLE_USER"; messageId="m1"; contextId=[guid]::NewGuid().ToString(); parts=@(@{ text="Voy a hacer una feria infantil de 3 horas desde las 11:00 para 80 personas y 6 niños son celíacos, ¿qué les damos de comer?" }) } } } | ConvertTo-Json -Depth 10
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8006/ -ContentType "application/json; charset=utf-8" -Headers @{ "A2A-Version" = "1.0" } -Body ([System.Text.Encoding]::UTF8.GetBytes($cuerpo)) | ConvertTo-Json -Depth 10
```

> **Diferencia con la guía del taller:** igual que en el agente de Matias, el proyecto usa
> `a2a-sdk` 1.x: el método se llama `SendMessage` (no `message/send`), requiere la cabecera
> `A2A-Version: 1.0`, los roles son `ROLE_USER` / `ROLE_AGENT` y la respuesta llega en
> `message.parts`, no en `artifacts`.

## 4. Ficha del agente

Archivos: `evidencias/sebastian/02-ficha-antes.json` (primera versión) y `evidencias/sebastian/02-ficha.json`
(versión final, descargada del servidor con `/.well-known/agent-card.json`). Nombre en
ambas: **Agente de Sebastian**.

### Antes

- **Descripción:** Propone comida y catering para ferias y eventos según el tipo de
  evento, la cantidad de personas y la duración. No cotiza precios ni reserva proveedores.
- **Skill:** "Armar catering": Propone servicios de comida y sus cantidades para un evento.
- **Ejemplo:** "Necesito catering para una feria tecnológica de 4 horas para 150 personas."

### Después

- **Descripción:** Propone la comida que se sirve a los asistentes de ferias tecnológicas,
  gastronómicas, culturales o infantiles de 10 a 500 personas y de 30 minutos a 8 horas:
  coffee break, cóctel, box lunch, almuerzo buffet, food trucks o colación infantil, con la
  hora de cada servicio, las cantidades y el agua calculadas, y menús vegetarianos, veganos,
  sin gluten y sin lactosa. No da precios ni presupuestos, no recomienda recintos ni
  capacidad, no arma el programa de actividades y no contrata proveedores: entrega solo
  propuestas.
- **Skill:** "Armar catering del evento": Propone qué servir y a qué hora, con cantidades y
  litros de agua calculados, según tipo de evento, personas, duración, hora de inicio y
  dietas especiales.
- **Ejemplo:** "Voy a hacer una feria infantil de 3 horas desde las 11:00 para 80 personas
  y 6 niños son celíacos, ¿qué les damos de comer?"

### Por qué se cambió

El supervisor de los compañeros solo lee esta ficha para decidir si me deriva una pregunta.

- **Temas concretos:** "comida y catering" no decía qué se puede pedir. Ahora nombra los
  servicios, las dietas y que las cantidades vienen calculadas.
- **"Que se sirve a los asistentes":** separa mi tema del de Matias en una feria
  gastronómica: las actividades (cata, clase de cocina) son de él, la comida para el
  público es mía.
- **El "no hago" completo, como en el blueprint:** la primera versión solo decía "no cotiza
  precios ni reserva proveedores". Se agregaron recintos y capacidad (Alex), presupuestos
  (Eduardo) y el programa de actividades (Matias), para que no me lleguen sus preguntas.
- **Límites:** 10 a 500 personas y 30 minutos a 8 horas, los mismos que valida la
  herramienta.
- **Ejemplo:** una pregunta escrita como la haría una persona, con una dieta especial.

Cómo la usa el supervisor frente a, por ejemplo, un agente de viajes: lee el nombre y la
descripción de cada ficha y elige la que cubre el tema de la pregunta. Si la pregunta es
de comida para un evento, la mía es la única que lo nombra; si es de costos, de lugares o
de actividades, mi frase "no hago" lo lleva a otro agente o a "ninguno".

### Prueba previa con un solo agente (no es la ronda oficial)

Con solo el Agente de Sebastian en el catálogo del coordinador (`URLS_AGENTES` con
`http://127.0.0.1:8006`), `python main.py coordinador "…" --saltos`:

| Pregunta | Agente elegido | Motivo del supervisor (resumido) |
|---|---|---|
| ¿Qué comida doy en una feria cultural de 2 horas para 60 personas? | Agente de Sebastian | Pide una propuesta de comida para un evento cultural |
| ¿Cuánto cuesta arrendar un salón para 100 personas? | ninguno | Es el costo de arrendar un salón; ningún agente lo maneja |
| ¿Qué actividades pongo en una feria gastronómica de 3 horas? | ninguno | Programar actividades está fuera del alcance explícito del agente |

En la tercera, el supervisor citó la frase "no arma el programa de actividades" de la ficha.
Con el agente de Matias en el catálogo, esa pregunta debería ir a él.

## 5. Túnel de Cloudflare

- Dirección pública: `https://replace-earl-univ-robinson.trycloudflare.com` (túnel del 2026-11-08; cambia al reiniciarlo).
  El túnel del 2026-11-07 (`discussed-split-drink-derek`) se cerró antes de sacar las capturas, así que se abrió uno nuevo.
- Comando: `cloudflared tunnel --url http://127.0.0.1:8006`, con el agente corriendo en
  el 8006. La dirección se copió a `URL_PUBLICA` en el `.env` antes de levantar el agente,
  así que la ficha la publica desde el arranque.
- `cloudflared` conectó por QUIC y todas las comprobaciones previas (DNS, UDP, TCP y API) pasaron.
- Verificación desde fuera, por la URL pública: `/salud` responde `{"ok": true}` y la ficha
  (`evidencias/sebastian/02-ficha.json`, descargada por el túnel) publica la dirección https en
  `supportedInterfaces`. Es igual a la ficha del día anterior salvo por la URL.
- Capturas: `evidencias/sebastian/03-tunel.png` (la terminal de `cloudflared` con el aviso de
  túnel creado y la URL) y `evidencias/sebastian/03-ficha-telefono.png` (la ficha abierta desde
  el teléfono, con datos móviles).

## 6. Catálogo y ronda de preguntas

**PENDIENTE (domingo 8 de noviembre, 19:00).**
