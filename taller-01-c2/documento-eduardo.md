# Documento de entrega · Taller A2A · Grupo 5

**Tema del grupo:** planificador de ferias y eventos.

| Integrante | Agente |
|------------|--------|
| Matias Muñoz | Programa, actividades y horarios |
| Alex Nail | Lugares y capacidad |
| Eduardo Basaure | Presupuesto y costos estimados |
| Sebastian Mardones | Comida y catering |

> Este documento cubre el agente de **Eduardo Basaure**. La ronda de preguntas se completa
> en la prueba grupal con el coordinador y los agentes de los compañeros.

## 1. Blueprint y alcance

Versión final: [`blueprint-Eduardo.md`](blueprint-Eduardo.md).

El agente estima presupuestos agregados simulados en CLP para eventos tecnológicos,
gastronómicos, culturales e infantiles, para 10–500 personas y duraciones de 30–480 minutos.
`estimar_presupuesto` informa partidas, subtotal, contingencia del 10 % y total; usa tarifas
ficticias y no modela impuestos. No genera cotizaciones ni autoriza compras, reservas,
pagos o contrataciones.

Derivaciones: menús, comida y catering → Sebastián; recintos y capacidad → Alex; actividades
y horarios → Matías. Las consultas ajenas se rechazan en una frase, se deriva al agente
correspondiente y no se ejecuta la herramienta de presupuesto.

## 2. Construcción y cambios

La herramienta usada para esta revisión fue **OpenCode**. No se dispone de un prompt original
auténtico ni de una transcripción de la construcción inicial; no se inventa ninguno.

El cambio funcional de `src/agente_eduardo/prompts.py` refuerza la derivación por
especialidad, evita presentaciones espontáneas y prohíbe llamar a `estimar_presupuesto` para
consultas ajenas. El cambio está incluido en el PR y fue validado con ejecuciones reales.

## 3. Pruebas y diagrama

Las siguientes comprobaciones fueron realizadas durante el desarrollo y la validación del agente. La suite automatizada se volvió a ejecutar sobre el código actualizado de `main`, con 96 pruebas aprobadas:

- **Pruebas automatizadas:** 96 aprobadas sobre el código actualizado de `main`, verificadas el 8 de noviembre de 2026.
- **Presupuesto:** feria tecnológica, 80 personas, 240 minutos. Resultado total
  **$2.173.600 CLP**, en 3 saltos: `model → tools (estimar_presupuesto) → model`.
- **Derivación de menú vegetariano:** Sebastián, 1 salto (`model`), sin herramienta.
- **Derivación de consulta sobre recintos:** Alex, 1 salto (`model`), sin herramienta.
- **Derivación de consulta sobre actividades y horarios:** Matías, 1 salto (`model`), sin herramienta. Validada mediante ejecución real.

Diagrama Mermaid generado directamente con el comando `python main.py eduardo --diagrama`:

```mermaid
---
config:
  flowchart:
    curve: linear
---
graph TD;
        __start__([<p>__start__</p>]):::first
        model(model)
        tools(tools<hr/><small><em>__tools = estimar_presupuesto</em></small>)
        __end__([<p>__end__</p>]):::last
        __start__ --> model;
        model -.-> __end__;
        model -.-> tools;
        tools -.-> model;
        classDef default fill:#f2f0ff,line-height:1.2
        classDef first fill-opacity:0
        classDef last fill:#bfb6fc
```


La captura [`evidencias/eduardo/01-saltos.png`](evidencias/eduardo/01-saltos.png) muestra la ejecución del presupuesto simulado de $2.173.600 CLP, con tres saltos y uso de `estimar_presupuesto`. También muestra el rechazo completo de una consulta sobre menú vegetariano, derivada a Sebastián en un salto y sin ejecutar herramientas. La evidencia no expone rutas personales ni credenciales.

La derivación a Alex fue verificada mediante una ejecución independiente. La derivación a Matías también fue verificada mediante ejecución real: Eduardo identificó correctamente su especialidad en un salto y sin invocar herramientas.


## 4. Fichas del agente: antes y después

Las dos fichas se guardaron levantando el agente en `http://127.0.0.1:8005` y leyendo
`/.well-known/agent-card.json`. Las dos anuncian `http://127.0.0.1:8005`.

**De dónde sale `02-ficha-antes.json`.** Es la ficha real que publicaba el agente en `main`
el 8 de noviembre de 2026, justo antes del ajuste descrito abajo (era la misma que estaba
guardada como `02-ficha.json`). Hasta entonces `server.py` había tenido una sola versión de
la ficha, por eso no existía una ficha «antes». Ahora sí existe una versión anterior real.

Descripción antes ([`evidencias/eduardo/02-ficha-antes.json`](evidencias/eduardo/02-ficha-antes.json)):

> Estima presupuestos agregados y simulados para ferias y eventos usando únicamente tarifas
> ficticias. No prepara menús ni cotiza catering (Sebastián), ni recomienda recintos (Alex);
> tampoco autoriza compras, reservas, pagos o contrataciones.

Descripción después ([`evidencias/eduardo/02-ficha.json`](evidencias/eduardo/02-ficha.json)):

> Estima presupuestos agregados y simulados para ferias y eventos usando únicamente tarifas
> ficticias. Incluye un costo de alimentación genérica por persona, pero no prepara menús
> (Sebastián), ni recomienda recintos (Alex); tampoco autoriza compras, reservas, pagos o
> contrataciones.

**Por qué se cambió.** Es un ajuste hecho en la revisión del grupo, después del ensayo
general del 8 de noviembre. En el ensayo, el supervisor mandó «¿Cuánto cuesta el catering
para 100 personas?» a Eduardo porque es un costo, pero su prompt la rechazaba («corresponde
a Sebastián») y Sebastián no da precios, así que nadie la respondía. Además, la ficha decía
«no cotiza catering», aunque la herramienta sí calcula una partida de alimentación genérica.

Cambios:

- Ficha: ahora dice que incluye un costo de alimentación genérica por persona, pero que no
  prepara menús.
- Prompt: se agregó «Si preguntan cuánto cuesta la comida o el catering, es una consulta de
  costos: pide los datos que falten, usa estimar_presupuesto y destaca la partida de
  alimentación genérica. Solo deriva a Sebastián cuando pidan qué menú servir.» La regla
  anterior («Si preguntan por menús, comida o catering… corresponde a Sebastián») se acotó a
  «qué menú o qué comida servir», para que no contradiga la nueva.

Resultado después del cambio:

- «¿Cuánto cuesta el catering para 100 personas?»: pregunta el tipo de evento.
- Con «feria tecnológica de 4 horas» en la misma conversación: entrega el presupuesto con
  la alimentación genérica destacada ($180.000 CLP; total $2.497.000 CLP).
- «¿Qué menú sirvo para 80 personas?»: «Eso corresponde a Sebastián.»

La ficha pública disponible en
[`evidencias/eduardo/03-ficha-telefono.png`](evidencias/eduardo/03-ficha-telefono.png)
se ve en un teléfono con 4G y contiene la URL pública en `supportedInterfaces[0].url`.
El archivo original era JPEG y se convirtió a PNG para cumplir la pauta; el original se
conserva localmente fuera del PR. Las tildes aparecen mal interpretadas por el navegador en
la captura; no se corrige la imagen.

## 5. A2A y dirección pública

La respuesta guardada [`evidencias/eduardo/04-a2a-publico.json`](evidencias/eduardo/04-a2a-publico.json)
registra el presupuesto de $2.173.600 CLP. Es una respuesta archivada y no prueba por sí
sola que un servidor continúe activo. La respuesta está en `result.message.parts[0].text`.

URL verificada en la sesión del **8 de noviembre de 2026**:
<https://breaking-rid-bestsellers-juvenile.trycloudflare.com>.
Es un túnel rápido de Cloudflare **temporal**: puede dejar de funcionar y la URL puede
cambiar al reiniciar el túnel. La captura [`evidencias/eduardo/03-tunel.png`](evidencias/eduardo/03-tunel.png)
muestra a `cloudflared` anunciando esa URL y la configuración de origen local en el puerto
8005; la captura telefónica muestra la ficha publicada con esa URL.

## 6. Evidencias disponibles y validación de archivos

- `01-saltos.png`: captura de terminal; PNG válido. Se ve la ejecución de presupuesto con
  `estimar_presupuesto` y 3 saltos; aparece también el inicio de la derivación vegetariana.
- `03-tunel.png`: captura de la terminal de Cloudflare; PNG válido. Muestra la URL temporal,
  fecha/hora de la sesión y el origen local `127.0.0.1:8005`.
- `03-ficha-telefono.png`: captura de la ficha en Safari móvil por 4G, convertida del JPEG
  original para cumplir la pauta. El original JPEG se conserva localmente fuera del PR.
- `02-ficha-antes.json` y `02-ficha.json`: ficha local antes y después del ajuste de la
  revisión del grupo (sección 4).
- `04-a2a-publico.json` y `respuesta-a2a.json`: respuestas guardadas; no equivalen a una
  repetición actual de A2A.

No se tomó la captura de `01-saltos.png` como prueba visual de todas las consultas; los
 resultados de las tres derivaciones provienen de ejecuciones reales validadas por Eduardo.

## 7. Resultados de la prueba grupal A2A

La ronda grupal se ejecutó el 8 de noviembre de 2026,
utilizando el coordinador y las fichas de los cuatro
agentes especializados.

El coordinador mostró `Supervisor con 4 agentes`.

| # | Pregunta | A quién fue | Motivo del supervisor | ¿Estuvo bien? |
|---|---|---|---|---|
| 1 | Presupuesto de feria infantil para 60 personas y 2 horas | Agente de Eduardo | El usuario solicita la estimación de un presupuesto simulado para un evento. | Sí. Entregó un presupuesto ficticio de $927.300 CLP. |
| 2 | Alimentación para 80 niños, incluidos 6 celíacos | Agente de Sebastian | El usuario pregunta sobre comida y menús específicos para una feria infantil. | Sí. Propuso alimentación general y opciones sin gluten. |
| 3 | ¿Cuál es la capital de Australia? | ninguno | La pregunta no corresponde a las funciones de ningún agente especializado del catálogo. | Sí. El coordinador no delegó la consulta. |

### Resultado

Las tres selecciones fueron correctas (3 de 3).

Cada consulta recorrió dos nodos del coordinador.

En las primeras dos consultas se utilizó el nodo
`agente_remoto` para delegar mediante A2A.

La tercera consulta utilizó `sin_agente`, al estar
fuera de las especialidades disponibles.

### Evidencias

- `evidencias/eduardo/04-catalogo.png`:
  supervisor con los cuatro agentes descubiertos.
- `evidencias/eduardo/05-ronda.png`:
  resultados de las tres preguntas, agente elegido
  y motivo de selección.

## 8. Estado de Git y seguridad

## 8. Estado de Git y seguridad

El agente de Eduardo fue integrado en el repositorio grupal
mediante los PR #57, #58, #61, #62, #63 y #64.

Las correcciones incluyen validación de datos obligatorios,
memoria conversacional por context_id, mejoras en las
responsabilidades del agente y evidencias individuales.

Se ejecutaron 96 pruebas automatizadas, todas aprobadas,
utilizando el código actualizado de main.

Durante la prueba grupal del 8 de noviembre de 2026,
el coordinador descubrió cuatro agentes y realizó
correctamente las tres selecciones de la ronda de Eduardo.

Las conexiones públicas utilizaron túneles temporales
de Cloudflare. Estas direcciones pueden dejar de funcionar
al finalizar la sesión.

Las evidencias de la ronda se incorporarán mediante un
PR de cierre independiente.

No deben incluirse archivos .env, claves de Gemini,
credenciales ni rutas personales en las evidencias
publicadas.
