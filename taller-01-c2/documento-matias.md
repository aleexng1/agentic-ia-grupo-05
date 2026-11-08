# Documento de entrega · Taller A2A · Grupo 5

**Tema del grupo:** planificador de ferias y eventos.

| Integrante | Agente |
|------------|--------|
| Matias Muñoz | Programa, actividades y horarios |
| Alex Nail | Lugares y capacidad |
| Eduardo Basaure | Presupuesto y costos estimados |
| Sebastian Mardones | Comida y catering |

> Este documento cubre el agente de **Matias Muñoz**. Las secciones de cada compañero
> y la ronda de preguntas se completan cuando existan sus agentes.

## 1. Blueprint

Matias escribió el primer borrador y lo envió al grupo. Ese borrador definía la
herramienta `sugerir_actividades(tipo_evento, duracion_minutos, publico)`. Tras una
revisión se ajustó a `armar_programa(...)`, para que la herramienta calcule qué
actividades caben en el tiempo (los modelos de lenguaje suman mal los minutos), y se
precisó el campo "Deriva a otro". Versión final (`blueprint-Matias.md`):

| Qué definir        | Mi agente |
|--------------------|-----------|
| Quién soy          | Matias · especialista en programas y horarios de ferias y eventos. |
| Hace               | Arma el programa de actividades y su horario para ferias tecnológicas, gastronómicas, culturales o infantiles de 30 minutos a 8 horas, según el público (familiar, adulto o estudiantes). |
| No hace            | No recomienda lugares ni capacidad, no cotiza costos ni comida, y no reserva ni confirma el programa definitivo. |
| Herramientas       | `armar_programa(tipo_evento, duracion_minutos, publico, hora_inicio)`: filtra una lista local de actividades inventadas y devuelve las que caben en el tiempo, con nombre, duración, descripción y hora de inicio. Si no hay coincidencias, lo dice en una línea. |
| Decide solo        | El orden de las actividades y cómo presentarlas, usando solo lo que devuelve la herramienta. |
| Nunca sin persona  | No publica ni confirma el horario definitivo y no contacta a expositores ni artistas. |
| Deriva a otro      | Cuando la pregunta es de recintos o capacidad, comida, o costos, lo dice en una frase y no responde. |
| Dónde se ejecuta   | `http://127.0.0.1:8003` · `src/agente_matias/` · `python main.py matias` |
| Dirección pública  | `https://storm-consoles-marilyn-mistress.trycloudflare.com` (túnel del 2026-11-07; cambia al reiniciarlo) |

## 2. Cómo se construyó el agente

### Herramienta usada

El agente se construyó con **Claude Code** (asistente de programación de Anthropic),
no con OpenCode. Matias dio las instrucciones y revisó los resultados; el asistente
escribió el código siguiendo el molde del agente de viajes del proyecto de la clase.

### Instrucciones (prompts) que dio Matias, textuales

Se omite solo la clave de acceso de la dirección de la plataforma.

1. Lectura del proyecto base y del taller:

   > Quiero que leas la carpeta con el proyecto inicial de agentes que hice en mi clase. esa es la base del taller que tengo que entregar. Luego quiero que vayas a esta url: [URL de la plataforma] y leas la ventana Taller · tu skill es un agente y habla por A2A, lees todas las viñetas para entender el trabajo.

2. Carpeta del taller:

   > quiero que crees una carpeta que se llame Curso 2 Taller 1 en la cual configuremos todo el proyecto inicial con las mismas estructura del proyecto que leiste. de esa forma puedo dejar cargada mis credenciales en el .env etc... guiate por como se seteo el proyecto de ejemplo que te compartí instalando librerias, versión de phyton, saltos, diagrama, etc...
   > dudas dimelas

3. Creación del agente:

   > ya tengo la clave cargada en el .env pero ojo con las urls que pusiste porque son las del ejemplo que te di no de nuestro taller que tenemos que entregar. mis compañeros estuvieron de acuerdo con la idea del planificador de eventos.
   >
   > quiero que hagamos todo lo que podamos hacer hoy respecto a mi parte del agente. anda explicandome que vas haciendo para entender, hazme preguntas si lo vas necesitando. Lo más probable es que Alex de mi grupo haga un repo en github para fusionar nuestros trabajos pero por ahora no está.

4. Limpieza de variables:

   > necesito que borres del .env y del .env example las url que no vamos a usar, por ahora ponle el nombre de las url del resto de mis compañeros.

### Qué se cambió después de verlo funcionar

- Pedir un programa de 4 horas devolvía solo 90 minutos y no lo avisaba: se ampliaron las
  actividades del catálogo y el prompt ahora obliga a indicar los minutos libres.
- El modelo enviaba `publico='infantil'` (confundía el tipo de evento con el público) y
  la herramienta devolvía una lista vacía: se agregaron alias de público y una regla en el prompt.
- El puerto `8004` que se había puesto en el blueprint se cambió a `8003`, que es el que
  asigna el taller al primer integrante.
- El coordinador ahora toma al agente de Matias de `URL_MATIAS` (antes tomaba viajes y
  restaurantes de la clase, que este grupo no usa).
- Al probar el proyecto descomprimido desde el zip, el modelo informó "105 minutos libres"
  cuando eran 45 (calculaba mal). Ahora la herramienta devuelve `minutos_usados` y
  `minutos_libres`, y el prompt indica usar esos valores sin recalcularlos. En tres corridas
  seguidas de la misma pregunta, la respuesta dijo 45 las tres veces.

## 3. Prueba en terminal

### Diagrama (`python main.py matias --diagrama`)

```
graph TD;
	__start__([<p>__start__</p>]):::first
	model(model)
	tools(tools<hr/><small><em>__tools = armar_programa</em></small>)
	__end__([<p>__end__</p>]):::last
	__start__ --> model;
	model -.-> __end__;
	model -.-> tools;
	tools -.-> model;
```

### Saltos

Captura `evidencias/matias/01-saltos.png`: una pregunta de su tema (se ve la herramienta
`armar_programa`) y otra de viajes, que el agente rechaza. Captura del diagrama:
`evidencias/matias/01-diagrama.png`.

### Mensaje por A2A

Respuesta completa en `evidencias/matias/respuesta-a2a.json`; el texto está en
`result.message.parts[0].text`.

> **Diferencia con la guía del taller:** el proyecto usa `a2a-sdk` 1.x. El método se llama
> `SendMessage` (no `message/send`), requiere la cabecera `A2A-Version: 1.0`, los roles son
> `ROLE_USER` / `ROLE_AGENT` y la respuesta llega en `message.parts`, no en `artifacts`.

## 4. Ficha del agente

Archivos: `evidencias/matias/02-ficha-antes.json` (primera versión) y
`evidencias/matias/02-ficha.json` (versión final, descargada del servidor).

Nombre en ambas: **Agente de Matias**.

### Antes

- **Descripción:** Arma programas y horarios para ferias tecnológicas, gastronómicas,
  culturales e infantiles, según duración y público. No cotiza lugares, comida ni costos,
  y no confirma el programa definitivo.
- **Skill:** Sugiere actividades y un horario para un evento según tipo, duración, público
  y hora de inicio.
- **Ejemplo:** "Arma un programa de 4 horas para una feria tecnológica con público familiar
  desde las 10:00."

### Después

- **Descripción:** Arma el programa de actividades y el horario de ferias tecnológicas,
  gastronómicas, culturales o infantiles de 30 minutos a 8 horas, para público familiar,
  adulto o estudiantes. No responde sobre lugares ni capacidad, comida ni costos, y no
  reserva ni confirma el programa definitivo: entrega solo propuestas.
- **Skill:** Propone las actividades que caben en el tiempo disponible, con su hora de
  inicio y término, según tipo de evento, público y hora de inicio.
- **Ejemplo:** "Necesito armar el programa de una feria infantil de 3 horas que parta a las
  15:00."

### Por qué se cambió

Matias decidió mejorar la ficha y el cambio se hizo con el asistente. El supervisor de los
compañeros solo lee esta descripción para decidir si deriva una pregunta, así que:

- **Capacidad:** el blueprint dice que Matias no responde sobre "lugares ni capacidad", pero
  la ficha solo decía "lugares". Se agregó "capacidad" para que la ficha coincida con el
  blueprint y no le lleguen preguntas del agente de Lugares.
- **Límites concretos:** se agregó el rango de duración (30 minutos a 8 horas) y los tres
  públicos (familiar, adulto, estudiantes), para que el supervisor sepa qué consultas caben.
- **Propuestas:** se aclaró que entrega solo propuestas y que no reserva ni confirma.
- **Ejemplo:** se cambió por una frase como la escribiría una persona, en lugar de una orden
  técnica.

## 5. Túnel de Cloudflare

- Dirección pública: `https://storm-consoles-marilyn-mistress.trycloudflare.com` (2026-11-07).
- `evidencias/matias/03-tunel.png`: terminal de `cloudflared` con la dirección.
- `evidencias/matias/03-ficha-telefono.png`: la ficha abierta desde el teléfono, con la URL pública.
La red mostró una advertencia (puerto TCP 7844 bloqueado), pero `cloudflared` conectó por
QUIC y la ficha fue accesible desde el teléfono.

## 6. Catálogo y ronda de preguntas

Prueba grupal del domingo 8 de noviembre de 2026, con los cuatro agentes en computadores
distintos conectados por túneles de Cloudflare. Túnel de Matias en esa prueba:
`https://plugin-telescope-termination-riverside.trycloudflare.com`.

- Catálogo: `evidencias/matias/04-catalogo.png` (`Supervisor con 4 agentes`).
- Ronda: `evidencias/matias/05-ronda.png` y la tabla siguiente.

| # | Pregunta | A quién fue | Motivo del supervisor | ¿Estuvo bien? |
|---|----------|-------------|-----------------------|---------------|
| 1 | Tengo una feria cultural de 3 horas desde las 16:00 para público familiar, ¿qué actividades pongo y a qué hora? | Agente de Matias | El usuario solicita un programa de actividades y horarios para una feria cultural. | Sí. Armó tres actividades entre las 16:00 y las 18:00 e informó 60 minutos libres. |
| 2 | Vamos a hacer una feria gastronómica para unas 250 personas y queremos que sea al aire libre, ¿qué lugar nos sirve? | Agente de Alex | La pregunta solicita recomendaciones de recintos para una feria, lo cual corresponde a las funciones del agente de Alex. | Sí. Recomendó dos recintos exteriores con capacidad para 300 y 500 personas. |
| 3 | ¿Quién ganó el mundial de 1962? | ninguno | La pregunta sobre la Copa Mundial de 1962 no corresponde a las funciones de ningún agente especializado del catálogo. | Sí. Respondió que no tiene un agente para eso y listó los cuatro agentes. |

Análisis del grupo (qué ficha eligió mejor el supervisor y si hubo preguntas que dos agentes
podían responder): lo escribe Alex en el documento de entrega.

**Qué cambiaría de mi ficha.** En la ronda el supervisor eligió bien a mi agente, pero mi
descripción usa la palabra «horario» sin precisar que es el de las actividades, y la ficha
del agente de Sebastián también habla de «la hora de cada servicio» de comida. Precisaría
«horario de las actividades». También agregaría un ejemplo con público de estudiantes, porque
el único que tengo es de una feria infantil.

### Prueba previa con un solo agente (no es la ronda oficial)

Con solo el agente de Matias en el catálogo, el coordinador derivó una pregunta de feria
gastronómica a "Agente de Matias", y respondió `ninguno` a una pregunta sobre arriendo de
salones y a otra sobre el mundial de 1962.

## 7. Notas técnicas

- `sse-starlette` faltaba en `requirements.txt` y el servidor A2A no arrancaba sin ella.
  Se agregó a `requirements.txt` y `requirements-crew.txt`.
- En la consola de Windows las tildes salen mal sin `PYTHONIOENCODING=utf-8`.
- Los agentes de viajes y restaurantes de la clase siguen en el proyecto, pero no están en
  el catálogo del coordinador de este grupo.
- Al conectar el coordinador con los túneles, el antivirus Avast (que revisa el HTTPS) hacía
  fallar la verificación con `CERTIFICATE_VERIFY_FAILED`, porque firma con su propio
  certificado. En `src/coordinador/cliente.py` se usan ahora los certificados del sistema
  operativo en lugar de los de `certifi`.
