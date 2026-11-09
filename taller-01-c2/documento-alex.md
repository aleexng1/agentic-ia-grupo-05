## 1. Blueprint

Versión final (`blueprint-Alex.md`):

| Qué definir        | Mi agente |
|--------------------|-----------|
| Quién soy          | Alex · especialista en recintos y capacidad para ferias y eventos. |
| Hace               | Recomienda hasta tres recintos para ferias tecnológicas, gastronómicas, culturales o infantiles de 10 a 500 personas, según si se prefiere un espacio interior o exterior. Para cada uno indica la capacidad, el % de ocupación, los m² por persona, los stands estimados, el estacionamiento y la accesibilidad. |
| No hace            | No da precios ni arriendos, no arma el menú ni el catering, no arma el programa de actividades y no reserva recintos. |
| Herramientas       | `buscar_recintos(tipo_evento, personas, espacio)`: filtra un catálogo local de recintos inventados (sin precios). Descarta los que quedan chicos (exige un 10 % de holgura), avisa cuando un recinto queda demasiado grande, ordena por mejor ajuste y entrega las cuentas ya hechas. Si nada sirve, lo dice en una línea. |
| Decide solo        | Cómo presentar y comparar los recintos, usando solo lo que devuelve la herramienta. |
| Nunca sin persona  | No reserva ni confirma un recinto, no contacta administradores y no garantiza que se cumplan los permisos o el aforo legal. |
| Deriva a otro      | Cuando la pregunta es de costos o presupuesto, de comida o catering, o del programa y horario de actividades, lo dice en una frase y no responde. |
| Dónde se ejecuta   | `http://127.0.0.1:8004` · `src/agente_alex/` · `python main.py alex` |
| Dirección pública  | `https://jenny-regulated-airfare-possibilities.trycloudflare.com` (túnel de Cloudflare del 2026-11-07; cambia al reiniciarlo) |

**Por qué la herramienta hace las cuentas:** los modelos de lenguaje calculan mal (a Matias
le pasó con los minutos libres). Por eso `buscar_recintos` entrega ya calculados la
ocupación, los m² por persona y los stands, y el prompt le prohíbe al modelo recalcularlos.

Reglas de la herramienta:

- Rango: de 10 a 500 personas; fuera de eso responde una línea con el rango.
- Holgura: la capacidad debe ser al menos personas × 1,10. La cuenta se hace con enteros
  (`capacidad × 100 ≥ personas × 110`), porque en decimales `100 × 1,10` da
  `110,00000000000001` y descartaría por error un recinto de 110 personas.
- `ocupacion_pct` = personas ÷ capacidad × 100; `m2_por_persona` = m² ÷ personas;
  `stands_estimados` = 1 stand cada 9 m² usando el 40 % del área.
- Ocupación bajo el 35 % → aviso "queda grande".
- Orden: ocupación más cercana al 75 %; devuelve hasta 3.
- Sin resultados: una línea con qué cambiar (otro espacio o menos personas). Nunca lanza
  un error.
- Entiende formas libres: "tech" o "feria tecnológica" → tecnologico, "niños" → infantil,
  "afuera" o "aire libre" → exterior, "interior o exterior" → cualquiera.
- Catálogo: 8 recintos inventados en comunas ficticias (salón de hotel, centro de
  convenciones, gimnasio municipal, galpón cultural, explanada de parque, colegio, centro
  comunitario y carpa modular), de 40 a 600 personas, sin precios.

## 2. Cómo se construyó el agente

### Herramienta usada

El agente se construyó con **Claude Code** (asistente de programación de Anthropic) en
Linux Mint. Alex dio las instrucciones y revisó los resultados; el asistente escribió el
código copiando el molde del agente de Matias (`src/agente_matias/`), que ya estaba
adaptado a `a2a-sdk` 1.3.

### Instrucción (prompt) que dio Alex, textual

```text
Contexto: estoy en el repo del grupo (/home/alex-pc/Escritorio/agentic-ia-grupo-05), Linux Mint, rama c2t1/alex-lugares. Taller 1 EVALUADO del Curso 2 (A2A). Grupo 5, tema: planificador de ferias y eventos. Trabajamos en taller-01-c2/. Lee primero taller-01-c2/README.md, taller-01-c2/proyecto/AGENTS.md, blueprint-Matias.md y el agente de Matías (proyecto/src/agente_matias/): es el molde ya adaptado a a2a-sdk 1.3 y es el que tienes que seguir.

Mi agente: "Agente de Alex" · lugares y capacidad · puerto 8004 · proyecto/src/agente_alex/ · python main.py alex. Ya está registrado en main.py y URL_ALEX está en .env.example.

Reglas:
- Explícame en simple qué haces en cada paso; no soy programador.
- No cambies proyecto/main.py, .env.example, requirements*.txt, proyecto/README.md, src/comun/, src/coordinador/ ni scripts/. Si algo lo necesita, dime qué y por qué.
- Datos inventados (recintos y comunas ficticios); nada real de empresas.
- Antes de cada commit o push, muéstrame git status y espera mi OK. Nunca subas .env, .venv ni __pycache__.

PASO 1 · Blueprint
Crea taller-01-c2/blueprint-Alex.md con el mismo formato que el de Matías y este contenido:
- Quién soy: Alex · especialista en recintos y capacidad para ferias y eventos.
- Hace: Recomienda hasta tres recintos para ferias tecnológicas, gastronómicas, culturales o infantiles de 10 a 500 personas, según si se prefiere un espacio interior o exterior. Para cada uno indica la capacidad, el % de ocupación, los m² por persona, los stands estimados, el estacionamiento y la accesibilidad.
- No hace: No da precios ni arriendos, no arma el menú ni el catering, no arma el programa de actividades y no reserva recintos.
- Herramientas: buscar_recintos(tipo_evento, personas, espacio): filtra un catálogo local de recintos inventados (sin precios). Descarta los que quedan chicos (exige un 10 % de holgura), avisa cuando un recinto queda demasiado grande, ordena por mejor ajuste y entrega las cuentas ya hechas. Si nada sirve, lo dice en una línea.
- Decide solo: Cómo presentar y comparar los recintos, usando solo lo que devuelve la herramienta.
- Nunca sin persona: No reserva ni confirma un recinto, no contacta administradores y no garantiza que se cumplan los permisos o el aforo legal.
- Deriva a otro: Cuando la pregunta es de costos o presupuesto, de comida o catering, o del programa y horario de actividades, lo dice en una frase y no responde.
- Dónde se ejecuta: http://127.0.0.1:8004 · src/agente_alex/ · python main.py alex
- Dirección pública: (se completa en el paso 6 con la URL del túnel)

PASO 2 · El agente (copiando el molde de agente_matias)
1) tools.py
   - Catálogo de unos 8 recintos inventados en el archivo, variados: salón de hotel, centro de convenciones, gimnasio municipal, galpón cultural, parque con explanada, colegio, centro comunitario, carpa modular. Cada uno con: nombre, comuna (ficticia), espacio (interior/exterior), capacidad_maxima (de 40 a 600), m2, tipos_evento aptos (tecnologico, gastronomico, cultural, infantil: los mismos que usa Matías), estacionamientos, accesible (sí/no), permite_servicio_comida (sí/no). Sin precios.
   - @tool buscar_recintos(tipo_evento, personas, espacio="cualquiera"). Que la herramienta haga TODAS las cuentas:
     · normaliza el texto (tildes, mayúsculas, sinónimos simples como "tech" → tecnologico, "niños" → infantil, "afuera"/"aire libre" → exterior);
     · personas fuera de 10–500 → una línea explicando el rango;
     · descarta recintos cuya capacidad sea menor que personas × 1,10;
     · calcula ocupacion_pct, m2_por_persona y stands_estimados (1 stand cada 9 m² usando el 40 % del área);
     · si la ocupación queda bajo el 35 %, agrega el aviso "queda grande";
     · ordena por la ocupación más cercana al 75 % y devuelve hasta 3;
     · si no hay ninguno, lo dice en una línea y sugiere qué cambiar (otro espacio o menos personas). Nunca lanza un error.
   - El docstring tiene que explicar bien los parámetros: es lo que lee el modelo para decidir.
2) prompts.py: SYSTEM_PROMPT: eres Alex, especialista en recintos y capacidad para ferias y eventos. Responde solo sobre eso, en español y corto. Usa siempre buscar_recintos antes de recomendar, no inventes datos y no recalcules los números: copia los que entrega la herramienta. Si la pregunta es de costos, comida o programa de actividades, dilo en una frase e indica que eso lo ve otro agente, sin responderlo. Si te preguntan quién eres, di tu nombre y tu especialidad. Advierte que la disponibilidad y el aforo legal los confirma una persona con el recinto.
3) graph.py: igual que el de Matías (create_agent, Gemini, MemorySaver, responder, saltos y diagrama).
4) server.py: ficha con crear_tarjeta, nombre "Agente de Alex", lee URL_ALEX y URL_PUBLICA igual que el de Matías. Description de dos frases: la primera dice qué sé, con temas concretos; la segunda dice qué no hago, copiada de la fila "No hace" del blueprint. Una skill por herramienta con una pregunta de ejemplo escrita como la haría una persona. Antes de dejar la versión final, guarda una primera versión simple de la description para el "antes" del paso 5.
5) Tests: proyecto/tests/test_tools_alex.py con pytest, sin usar la clave: rango de personas, holgura del 10 %, "queda grande", sinónimos, sin resultados y que nunca lance un error.

PASO 3 · Ambiente y pruebas sin servidor
- En taller-01-c2/proyecto crea .venv con Python 3.12 e instala requirements.txt.
- Copia GOOGLE_API_KEY y MODELO del .env de mi práctica (curso02-taller01/.env o taller-02/alex_nail/proyecto/.env, el que exista) a taller-01-c2/proyecto/.env, con URL_ALEX=http://127.0.0.1:8004. No me muestres la clave.
- Corre python -m pytest tests -q.
- Corre y muéstrame:
  python main.py alex "Voy a hacer una feria tecnológica para 150 personas, ¿dónde la hago?" --saltos
  python main.py alex "¿Cuánto cuesta arrendar un salón?" --saltos   (tiene que rechazarla)
  python main.py alex --diagrama
- Si responde mal, ajusta prompts.py o el docstring y dime qué cambiaste. Lo anotamos en el documento.
- Dime cuándo sacar la captura evidencias/alex/01-saltos.png (las dos preguntas en pantalla).

PASO 4 · Servidor, ficha y mensaje A2A
- Dame los comandos para que yo levante uvicorn src.agente_alex.server:app --port 8004 en una terminal (no lo dejes corriendo tú).
- Con el servidor arriba, guarda con curl la ficha en evidencias/alex/02-ficha-antes.json (con la versión simple) y después en evidencias/alex/02-ficha.json (con la final).
- Manda un mensaje con SendMessage y la cabecera A2A-Version: 1.0 (como dice AGENTS.md) y guarda la respuesta en evidencias/alex/respuesta-a2a.json.

PASO 5 · Documento
Crea taller-01-c2/documento-alex.md con la misma estructura que documento-matias.md: blueprint; cómo se construyó (con Claude Code, pegando este prompt textual); qué cambié después de verlo funcionar; salida de --diagrama; ficha antes y después y por qué; respuesta A2A. Agrega una nota: con a2a-sdk 1.3 el método es SendMessage y no message/send, y el texto viene en result.message.parts y no en artifacts. Deja como pendientes 03-tunel.png, 04-catalogo.png, 05-ronda.png y la tabla de la ronda.

PASO 6 · Subir
Muéstrame git status (solo archivos dentro de taller-01-c2/ y ningún .env), espera mi OK, haz el commit "c2t1: agente de Alex (lugares y capacidad)" y el push. Después abre un PR hacia main con gh si está disponible; si no, dame el enlace de compare.

El túnel de Cloudflare (paso 6 del taller) lo vemos aparte: en Linux Mint hay que instalar cloudflared y usar scripts/tunel.sh.
```

Durante el trabajo Alex respondió a las preguntas del asistente con mensajes cortos: avisó
cuando la captura estaba lista y que el servidor corría con `--reload`, y dio el OK antes
de cada commit.

### Qué se cambió después de verlo funcionar

Todos los cambios fueron en `prompts.py`; la herramienta y sus números estaban bien
desde la primera prueba.

1. **Se presentaba sin que se lo pidieran.** Respondía "Soy Alex, especialista en
   recintos..." antes de cada respuesta. Se agregó: "Si no te lo preguntan, no te
   presentes: ve directo a la respuesta". Al preguntarle "¿Quién eres?" sigue diciendo su
   nombre y especialidad.
2. **El rechazo sonaba a lista copiada.** A "¿Cuánto cuesta arrendar un salón?" respondía
   "Eso de costos, precios, arriendos o presupuesto lo ve otro agente del grupo" (repetía
   la lista del prompt). Se pidió nombrar solo el tema preguntado; ahora responde "El
   precio del arriendo lo ve otro agente del grupo".
3. **Inventaba el aviso "queda grande".** En el primer mensaje A2A (feria gastronómica al
   aire libre para 200 personas) puso "Aviso: queda grande" en la Explanada, que tiene
   40 % de ocupación. La herramienta **no** había mandado ese aviso (solo lo manda bajo el
   35 %): lo agregó el modelo por su cuenta. Se cambió la regla a "Menciona «queda grande»
   solo en los recintos que traen el campo aviso, copiando ese aviso; nunca lo agregues por
   tu cuenta". En tres envíos seguidos de la misma pregunta ya no apareció, y con 20 niños
   al aire libre (ocupación de 6,7 % y 4 %) el aviso sí aparece.

Pruebas extra que salieron bien sin cambios: 800 personas (responde el rango de 10 a 500)
y una pregunta mixta ("¿Dónde hago una feria cultural de 100 personas y qué menú sirvo?":
recomienda recintos y deriva el menú a otro agente).

## 3. Prueba en terminal

### Pruebas de la herramienta (`python -m pytest tests -q`)

`tests/test_tools_alex.py`: 41 pruebas que pasan sin usar la clave. Revisan el rango de
personas (y sus bordes 10 y 500), la holgura del 10 % (36 personas caben en un recinto de
40; 37 ya no), el aviso "queda grande", el orden por ocupación cercana al 75 %, los
sinónimos de tipo y de espacio, los casos sin resultados (sugiere otro espacio o menos
personas) y que nunca lance un error aunque reciba datos raros (`None`, texto, listas).

### Diagrama (`python main.py alex --diagrama`)

Archivo: `evidencias/alex/diagrama.txt`.

```
graph TD;
	__start__([<p>__start__</p>]):::first
	model(model)
	tools(tools<hr/><small><em>__tools = buscar_recintos</em></small>)
	__end__([<p>__end__</p>]):::last
	__start__ --> model;
	model -.-> __end__;
	model -.-> tools;
	tools -.-> model;
```

### Saltos

Captura `evidencias/alex/01-saltos.png`:

- "Voy a hacer una feria tecnológica para 150 personas, ¿dónde la hago?" → pasa por
  `model → tools (buscar_recintos) → model` (3 saltos) y recomienda el Salón Cumbre
  (83,3 % de ocupación, 13 stands), el Galpón Cultural Rinconada Azul (60 %) y la Carpa
  Modular Bahía Pizarra (50 %).
- "¿Cuánto cuesta arrendar un salón?" → solo `model` (1 salto), sin usar la herramienta:
  "El precio del arriendo lo ve otro agente del grupo."

### Mensaje por A2A

Pregunta: "Hola, quiero hacer una feria gastronómica al aire libre para 200 personas. ¿Qué
recinto me recomiendas?". Respuesta completa en `evidencias/alex/respuesta-a2a.json`; el
texto está en `result.message.parts[0].text`. Recomienda la Carpa Modular Bahía Pizarra
(66,7 %) y la Explanada del Parque Lomas de Arrayán (40 %), con la advertencia de que la
disponibilidad y el aforo legal los confirma una persona.

> **Diferencia con la guía del taller:** con `a2a-sdk` 1.3 el método es `SendMessage` y
> no `message/send`, y el texto de la respuesta viene en `result.message.parts` y no en
> `artifacts`. Además requiere la cabecera `A2A-Version: 1.0` y los roles son
> `ROLE_USER` / `ROLE_AGENT`.

Comando usado:

```bash
curl -s http://127.0.0.1:8004/ \
  -H 'Content-Type: application/json' -H 'A2A-Version: 1.0' \
  -d '{"jsonrpc":"2.0","id":"1","method":"SendMessage","params":{"message":{"messageId":"alex-prueba-1","role":"ROLE_USER","parts":[{"text":"Hola, quiero hacer una feria gastronómica al aire libre para 200 personas. ¿Qué recinto me recomiendas?"}]}}}'
```

## 4. Ficha del agente

Archivos: `evidencias/alex/02-ficha-antes.json` (primera versión) y
`evidencias/alex/02-ficha.json` (versión final), los dos descargados del servidor con
`curl http://127.0.0.1:8004/.well-known/agent-card.json`.

Nombre en ambas: **Agente de Alex**.

### Antes

- **Descripción:** Recomienda lugares para eventos. No da precios.
- **Skill:** "Buscar recintos": Busca recintos según tipo de evento y personas.
- **Ejemplo:** "buscar_recintos tecnologico 150"

### Después

- **Descripción:** Recomienda hasta tres recintos para ferias tecnológicas, gastronómicas,
  culturales o infantiles de 10 a 500 personas, en espacio interior o exterior, e indica
  para cada uno la capacidad, el % de ocupación, los m² por persona, los stands estimados,
  el estacionamiento y la accesibilidad. No da precios ni arriendos, no arma el menú ni el
  catering, no arma el programa de actividades y no reserva recintos.
- **Skill:** "Buscar recintos para una feria": Busca recintos donde cabe el evento con un
  10 % de holgura, según el tipo de feria, la cantidad de personas y si se prefiere un
  espacio interior o exterior, y avisa cuando un lugar queda demasiado grande.
- **Ejemplo:** "Voy a hacer una feria tecnológica para 150 personas, ¿dónde la puedo hacer?"

### Por qué se cambió

El supervisor del grupo solo lee la ficha para decidir a quién derivar cada pregunta, así
que la ficha tiene que decir con claridad qué entra y qué no:

- **Temas concretos:** "lugares para eventos" era muy vago. Ahora nombra los cuatro tipos
  de feria, el rango de 10 a 500 personas, interior o exterior, y qué datos entrega
  (capacidad, ocupación, m², stands, estacionamiento, accesibilidad).
- **Límites completos:** "No da precios" dejaba fuera la comida y el programa, que son de
  Sebastian y de Matias. La segunda frase ahora es la fila "No hace" del blueprint, para
  que el supervisor no le mande a Alex preguntas de catering ni de horarios.
- **Ejemplo humano:** "buscar_recintos tecnologico 150" parecía una orden técnica; se
  cambió por una frase como la escribiría una persona.

## 5. Túnel de Cloudflare

- Dirección pública: `https://jenny-regulated-airfare-possibilities.trycloudflare.com`
  (túnel rápido de trycloudflare del 2026-11-07, sin cuenta; cambia al reiniciarlo).
- `evidencias/alex/03-tunel.png`: ventana de la Terminal de Mint con el túnel corriendo
  (`pgrep` muestra `cloudflared tunnel --url http://127.0.0.1:8004`), la dirección que
  informa `cloudflared` en `127.0.0.1:20241/quicktunnel` y la ficha pública respondiendo
  con esa dirección. Se sacó así porque el recuadro verde de `tunel.sh` quedó tapado por
  los registros de `cloudflared` en la terminal de VS Code.
- `evidencias/alex/03-ficha-telefono.png`: la ficha abierta desde el teléfono, con la URL
  pública. Se abrió con datos móviles (arriba se ve "5G"), es decir, desde fuera de la red
  del computador.

> **Nota sobre las tildes en el teléfono:** en la captura del teléfono las tildes se ven
> mal ("tecnolÃ³gicas" en vez de "tecnológicas") porque el servidor responde
> `content-type: application/json` sin declarar `charset=utf-8`, y el navegador del
> teléfono interpreta el texto en otro formato. La ficha es correcta: los bytes que envía
> el servidor son UTF-8 válido y dicen "tecnológicas", como se ve en `02-ficha.json` y
> `03-ficha-publica.json`. No se cambió `src/comun/`, que es el código compartido que arma
> la respuesta.
- `evidencias/alex/03-ficha-publica.json`: la ficha descargada con `curl` desde la URL
  pública. Es igual a `02-ficha.json` salvo la dirección, que ahora es la del túnel
  (`supportedInterfaces[0].url`).

Cómo se hizo en Linux Mint 22.3 (basado en Ubuntu 24.04):

1. Instalación de `cloudflared` con apt, desde el repositorio oficial de Cloudflare
   (https://pkg.cloudflare.com/), con la clave `cloudflare-main.gpg` y la línea
   `deb [...] https://pkg.cloudflare.com/cloudflared any main`. Versión instalada: 2026.10.7.
2. Terminal 1: `uvicorn src.agente_alex.server:app --port 8004` (sin `--reload`).
3. Terminal 2: `bash scripts/tunel.sh 8004`. Muestra la dirección en verde. Si se pierde
   entre los registros, `curl -s http://127.0.0.1:20241/quicktunnel` la devuelve.
4. La dirección se copió en `URL_PUBLICA` del `.env` (sin `/` final) y se reinició la
   terminal 1, porque el `.env` solo se lee al arrancar.

Problemas encontrados:

- El primer intento no mostró ninguna dirección porque el túnel no quedó corriendo. Una
  prueba de 30 segundos confirmó que la red estaba bien (chequeos de DNS, QUIC y HTTP/2
  en "PASS"); al volver a lanzar `tunel.sh` funcionó.
- Tras pegar la URL en el `.env`, la ficha seguía publicando `http://127.0.0.1:8004`:
  el agente no se había reiniciado. Después de reiniciarlo publica la dirección del túnel.
- `scripts/tunel.sh` solo sugería `brew install cloudflared` (macOS). Alex, como
  integrador, agregó al mensaje las instrucciones para Linux.

Mientras el túnel está abierto, cualquiera con la dirección puede usar el agente y
gastar la clave de Gemini, así que se cierra con Ctrl+C al terminar.

## 6. Catálogo y ronda de preguntas

Prueba grupal del 8 de noviembre de 2026. Mi coordinador corrió en mi computador
(puerto 8002) con mi agente local (`http://127.0.0.1:8004`) y los túneles de Matias,
Eduardo y Sebastian en `URLS_AGENTES`. Las fichas descargadas ese día están en
`evidencias/alex/fichas-companeros/` y en `compañeros.md`.

**Catálogo:** [`evidencias/alex/04-catalogo.png`](evidencias/alex/04-catalogo.png). Al
arrancar, el coordinador leyó las 4 fichas y mostró **«Supervisor con 4 agentes»**.

**Ronda:** [`evidencias/alex/05-ronda.png`](evidencias/alex/05-ronda.png). Las 3 preguntas
se hicieron con `python main.py coordinador "…" --saltos`.

| # | Pregunta | A quién fue | Motivo del supervisor | ¿Estuvo bien? |
|---|----------|-------------|-----------------------|---------------|
| 1 | Voy a hacer una feria tecnológica para 150 personas, ¿dónde la hago? | Agente de Alex | El usuario solicita una recomendación de recinto para una feria tecnológica. | Sí |
| 2 | ¿Cuánta plata necesito más o menos para una feria gastronómica de 120 personas que dura 3 horas? | Agente de Eduardo | La pregunta solicita una estimación de presupuesto y costos para un evento. | Sí |
| 3 | ¿Qué vuelos hay a Lima? | ninguno | La pregunta sobre vuelos a Lima no corresponde a las funciones de ningún agente disponible. | Sí |

Comentarios:

1. Fue a mi agente, que recomendó 3 recintos con ocupación de 83,3 %, 60 % y 50 %,
   m² por persona y stands estimados. Esos números salen de `buscar_recintos`: al repetir
   la pregunta con `python main.py alex "…" --saltos` se ve `Herramienta: buscar_recintos`.
2. Pregunta escrita como alguien que no conoce el tema («cuánta plata», sin decir
   «presupuesto»). El supervisor igual la mandó a Eduardo, que usó su herramienta y
   devolvió las partidas con un total simulado de $2.059.200 CLP.
3. Ningún agente sabe de vuelos. El supervisor eligió «ninguno» y el coordinador respondió
   con la lista de agentes disponibles, sin inventar una respuesta.

### Qué cambiaría de mi ficha después de la ronda

La ficha funcionó: el supervisor me mandó las preguntas de recintos, incluida la de una feria con food trucks del ensayo, en la que el agente pidió la cantidad de personas antes de recomendar. Cambiaría dos cosas. Agregaría a la descripción que necesito tres datos (tipo de feria, cantidad de personas y si se prefiere interior o exterior), para que quien pregunta los dé de entrada. Y haría que el agente indique si un recinto permite servicio de comida (el dato ya está en mi catálogo, pero hoy no lo muestra), aclarando que qué servir es tema de Sebastián, porque esa es la frontera más cercana entre nuestros agentes.

El análisis del grupo está en la sección 6.

## 7. Notas técnicas

- Ambiente: Python 3.12.3 en Linux Mint, `a2a-sdk` 1.3.0, `langchain` 1.4.9,
  `langgraph` 1.2.20, modelo `gemini-3.5-flash-lite`.
- El servidor se levantó con `uvicorn src.agente_alex.server:app --port 8004 --reload`,
  así que al cambiar `server.py` o `prompts.py` se recarga solo.
- No fue necesario cambiar archivos compartidos (`main.py`, `.env.example`,
  `requirements*.txt`, `src/comun/`, `src/coordinador/`, `scripts/`). El agente ya estaba
  registrado en `main.py` y `URL_ALEX` en `.env.example`. La ficha toma `URL_PUBLICA` desde
  `src/comun/tarjeta.py`, igual que la de Matias.
- Para la ronda, el coordinador lee la dirección de Alex desde `URLS_AGENTES` (no hay que
  cambiar código).
