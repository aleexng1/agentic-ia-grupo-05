# Instrucciones de Alex a Claude Code · Taller 2 del Curso 2

Instrucciones dadas a Claude Code (en Linux Mint), en orden, copiadas tal cual. Los
prompts se prepararon con ayuda de Claude (claude.ai) y Alex los revisó, los ajustó
según los resultados de cada paso y los pegó en Claude Code. Las respuestas cortas de
continuación ("sigue", "arréglalo") también se incluyen.

---

## 1 · Base del proyecto (rama c2t2/alex-base)

```
Trabajamos en este repo (agentic-ia-grupo-05). Empezamos un taller nuevo del Curso 2:
"Implementa y entrega tu agente". La base es el taller anterior, que está en
taller-01-c2/proyecto (sistema A2A de un planificador de ferias: un coordinador y 4
agentes, cada uno con tools.py, prompts.py, graph.py y server.py, y código común en
src/comun). Léelo primero para entender cómo funciona. NO modifiques nada dentro de
taller-01-c2/ ni de las demás carpetas de talleres: ese taller ya fue entregado.

Opción elegida del taller nuevo: una página web con chat, servida por una API FastAPI
protegida con clave, que por detrás usa el mismo coordinador + 4 agentes por A2A.
Se entregará corriendo en local y además desplegado en Heroku (todo en UNA sola app).

1) RAMA. Desde main actualizado, crea la rama c2t2/alex-base y trabaja ahí.

2) CARPETA taller-02-c2/ con:
   - proyecto/: copia de taller-01-c2/proyecto, excluyendo .venv, __pycache__,
     src/agente_viajes, src/agente_restaurantes y requirements-crew.txt (eran ejemplos
     de la clase y este grupo no los usa). Actualiza main.py y toda referencia a ellos.
   - evidencias/ con subcarpetas matias, alex, eduardo y sebastian (con .gitkeep).
   - README.md inicial con: opción elegida, el problema que resuelve, qué se reutiliza
     del taller A2A, tabla de integrantes con su aporte (Alex: base e integración;
     Matías: seguridad y errores; Eduardo: frontend del chat; Sebastián: Heroku y
     operación), y secciones vacías: Preparación manual, Instalación, Configuración,
     Cómo iniciar / probar / detener, Operación en Heroku, Límites conocidos.

3) APP ÚNICA. Crea taller-02-c2/proyecto/app.py: UNA aplicación FastAPI que sirva todo:
   - El coordinador en la raíz: su panel web, su ficha y su JSON-RPC quedan igual que hoy.
   - Cada agente montado bajo /agentes/{nombre} (matias, alex, eduardo, sebastian), cada
     uno con su ficha en /agentes/{nombre}/.well-known/agent-card.json y su JSON-RPC.
   - Las tarjetas de los agentes se crean con URL = URL_BASE + "/agentes/{nombre}",
     donde URL_BASE viene del .env (por defecto http://127.0.0.1:8000). Así en Heroku
     basta cambiar URL_BASE y las fichas apuntan bien.
   - IMPORTANTE: el coordinador debe descubrir las fichas en la PRIMERA pregunta, no al
     arrancar la app (al arrancar, sus propias rutas todavía no responden y se quedaría
     pegado). Reutiliza el candado de inicialización que ya existe en el coordinador.
   - URLS_AGENTES: si viene vacía en el .env, usa por defecto las 4 rutas internas
     derivadas de URL_BASE; si viene con valores, respétalas (permite volver al modo
     distribuido del taller anterior, con un agente por computador).
   - GET /salud en la raíz responde {"ok": true}.
   - POST /panel/consultar debe devolver, además de "respuesta" y "context_id", los
     campos "agente" y "motivo" por separado (hoy van incrustados en el texto). El
     frontend los mostrará. No rompas el formato de main.py ni --saltos/--diagrama.

4) .env.example de taller-02-c2/proyecto con comentarios en español:
   GOOGLE_API_KEY= · MODELO=gemini-3.5-flash-lite · PUERTO=8000 ·
   URL_BASE=http://127.0.0.1:8000 · CLAVE_API= (clave de acceso que validará el
   servidor; la implementa Matías, aquí solo se declara) · URLS_AGENTES= (vacío = las
   rutas internas de la app única). Elimina las variables del taller anterior que ya
   no se usen (URL_COORDINADOR, URL_MATIAS, URL_PUBLICA, etc.).

5) ARCHIVOS DE HEROKU EN LA RAÍZ DEL REPO (Heroku solo lee la raíz):
   - Procfile:            web: cd taller-02-c2/proyecto && uvicorn app:app --host 0.0.0.0 --port $PORT
   - requirements.txt:    -r taller-02-c2/proyecto/requirements.txt
   - .python-version:     3.12
   - .slugignore: excluye las otras carpetas de talleres, evidencias, PDFs e imágenes.
   OJO: si alguno de esos archivos ya existe en la raíz, muéstramelo y pregúntame antes
   de tocarlo.

6) AGENTS.md de taller-02-c2/proyecto: parte de las reglas del taller anterior (todo en
   español, timeouts, errores en una línea, contrato responder(texto, context_id)) y
   agrega: la app única se levanta con `uvicorn app:app --reload --port 8000` desde
   taller-02-c2/proyecto; zona de cada persona (Matías: validación de acceso y manejo
   de errores en el servidor; Eduardo: src/comun/panel.py y panel.html; Sebastián:
   sección Operación del README); nadie toca la zona de otro sin avisar.

7) PRUEBAS. Las pruebas existentes de tests/ deben seguir pasando (no usan la clave de
   Gemini). Agrega tests/test_app.py con TestClient: /salud responde ok y cada una de
   las 4 fichas /agentes/*/.well-known/agent-card.json responde con el nombre correcto,
   sin llamar a Gemini.

8) CIERRE. Corre pytest. Después prueba el arranque igual que lo hará Heroku: desde la
   RAÍZ del repo, el mismo comando del Procfile con PORT=8000, y verifica que respondan
   /salud, el panel y una ficha de agente. Haz commit en la rama con un mensaje claro.
   NO hagas push: lo decido yo. Termina con un resumen de archivos creados y
   modificados, y los comandos exactos para que yo pruebe todo en mi máquina.
```

---

## 2 · Ajuste de la base, publicación y ramas del grupo

```
Seguimos con la base del taller nuevo, en la rama c2t2/alex-base del repo
agentic-ia-grupo-05. Esto va en DOS FASES. Al terminar la fase 1 te detienes y
esperas a que yo diga "sigue".

FASE 1 · Ajuste de la base (en c2t2/alex-base)
1) Llamada interna a los agentes. Cuando URLS_AGENTES está vacía, el coordinador
   debe consultar a los agentes por la dirección interna
   http://127.0.0.1:{puerto real}/agentes/{nombre} en vez de URL_BASE, para no salir
   y volver a entrar por el router de Heroku, que corta las peticiones a los 30
   segundos. El puerto real se toma de la variable PORT si existe; si no, de PUERTO
   del .env (por defecto 8000). Que PUERTO quede leído de verdad, no solo declarado.
   Las fichas públicas siguen mostrando URL_BASE + /agentes/{nombre}: solo cambia la
   dirección que usa el cliente interno del coordinador. El modo distribuido
   (URLS_AGENTES con valores) no cambia.
2) En el README de taller-02-c2, sección Límites conocidos, deja anotado: la memoria
   de la conversación vive en la RAM del servidor (se pierde al reiniciar o cuando
   Heroku duerme la app) y en Heroku debe usarse WEB_CONCURRENCY=1 para que haya una
   sola copia del programa y el chat no pierda el hilo.
3) Actualiza o agrega la prueba que corresponda, corre pytest y vuelve a probar el
   arranque igual que Heroku desde la RAÍZ del repo:
   PORT=8000 sh -c 'cd taller-02-c2/proyecto && uvicorn app:app --host 0.0.0.0 --port $PORT'
   Verifica /salud, el panel y una ficha de agente.
4) Commit en c2t2/alex-base con mensaje claro. Dame el resumen de lo cambiado y los
   comandos para que yo pruebe una pregunta real con mi clave de Gemini (un curl a
   /panel/consultar y el panel en el navegador).
DETENTE AQUÍ y espera a que yo escriba "sigue".

FASE 2 · Publicar la base y crear las ramas (solo cuando yo diga "sigue")
5) Antes de cada cambio de rama corre git status; si aparece modificado
   tarea-final-c1/agente.ipynb es un falso cambio del filtro nbstripout: cambia de
   rama con
   git -c filter.nbstripout.clean=cat -c filter.nbstripout.required=false switch <rama>
   No hagas commit de ese notebook.
6) git push -u origin c2t2/alex-base. Abre un PR hacia main con gh, título
   "Taller 2 C2: base del proyecto (app única + Heroku)" y una descripción corta de
   lo que trae. Únelo con gh pr merge --merge, SIN borrar la rama.
7) Actualiza main local (git switch main && git pull) y verifica que exista
   taller-02-c2/ y los archivos Procfile, .python-version y .slugignore en la raíz.
8) Desde ese main actualizado crea y sube estas cuatro ramas (git branch + git push
   -u origin, sin cambiar de rama entre una y otra si no hace falta):
   - c2t2/alex-integracion   (mía, para el README final y la entrega)
   - c2t2/matias-seguridad
   - c2t2/eduardo-frontend
   - c2t2/sebastian-heroku
9) Confirma con git branch -a que las cuatro existen en origin y apuntan al mismo
   commit que main. Déjame en la rama c2t2/alex-integracion.
10) Termina con una tabla: rama, commit al que apunta y si quedó en origin. No borres
   ninguna rama existente (las c2t1/* y alex/curso02-taller01 se quedan como están).
```

Continuación tras probar una pregunta real:

```
sigue
```

---

## 3 · Registro A2A y README

```
Estoy en la rama c2t2/alex-integracion del repo agentic-ia-grupo-05 (taller en
taller-02-c2). Dos tareas:

1) LOG DE A2A. En el coordinador, agrega un registro legible con el módulo logging
   (no print) en cada consulta, una línea por paso:
   - "pregunta recibida · context_id=..." (sin el texto completo si es muy largo:
     máximo 80 caracteres)
   - "supervisor eligió <agente> · motivo: <motivo>"
   - "A2A → <url del agente> · enviando"
   - "A2A ← <agente> · respuesta recibida en X,X s" o "A2A ✗ <agente> · error: <una línea>"
   Nunca registres claves ni cabeceras. Que se vea en la terminal de uvicorn en
   local y en los logs de Heroku (salida estándar). Configura el formato con hora.
   Agrega una prueba sin Gemini si es posible y corre pytest.

2) README de taller-02-c2: completa las secciones que no dependen de otros:
   - Instalación (Linux, macOS y Windows, Python 3.12, desde taller-02-c2/proyecto).
   - Configuración: cada variable del .env.example explicada en una línea (CLAVE_API
     la detalla Matías, deja solo su nombre y un "ver más abajo").
   - Cómo iniciar, probar y detener en local: comando de uvicorn, URL del panel,
     curl de /salud, python main.py con --saltos, pytest, y Ctrl+C para detener.
   - Cómo funciona: un diagrama simple en texto de la app única (panel → coordinador
     → A2A → /agentes/{nombre}) y la explicación de por qué es una sola app.
   - Dependencias externas: Gemini (requiere internet y una clave propia).
   Deja intactas las secciones de otros (Operación en Heroku, seguridad) con un
   "pendiente: <nombre>".
   Sin rutas absolutas de mi computador.

Haz commit en la rama, dame los comandos para push y PR (los ejecuto yo) y un
ejemplo de cómo se ven las líneas del log con una pregunta real.
```

```
Une el PR #75 a main con gh pr merge 75 --merge, sin borrar la rama. Después
actualiza main local y confirma que c2t2/alex-integracion y main apuntan al mismo
commit.
```

---

## 4 · Revisión de los PR de Matías (#76) y Eduardo (#77)

```
Estamos en el repo agentic-ia-grupo-05, taller en taller-02-c2. Hay dos PR de
compañeros por revisar: #76 (Matías, seguridad, rama c2t2/matias-seguridad) y #77
(Eduardo, frontend, rama c2t2/eduardo-frontend). Esto va en DOS FASES. Al terminar
la fase 1 te detienes y esperas a que yo escriba "sigue".

CONTEXTO DEL CONTRATO ACORDADO ENTRE AMBOS
- El servidor exige la cabecera X-API-Key (valor de CLAVE_API) en todo POST: el chat
  /panel/consultar y el JSON-RPC A2A del coordinador y de cada agente.
- Errores como {"detail": "mensaje"}: 400 pregunta vacía, 401 falta o incorrecta la
  clave, 502 falla de Gemini/red/agente, 503 servidor sin CLAVE_API.
- La página, las fichas (/.well-known/agent-card.json) y /salud siguen públicas.

REGLAS PARA TODO EL TRABAJO
- No leas ni imprimas mi archivo .env, ni pongas claves reales en archivos, commits
  ni en lo que me muestres. Para probar con la app levantada, pasa CLAVE_API solo
  como variable de entorno del proceso con un valor generado al momento
  (python -c "import secrets; print(secrets.token_urlsafe(32))"), sin escribirla en
  ningún archivo.
- Revisa cada PR en una copia temporal (git worktree en /tmp), sin mover mi
  directorio de trabajo ni tocar las ramas de los compañeros.
- Revisa contra lo que pide el enunciado del taller, no más. No te pongas a mejorar
  estilo ni a reescribir lo que funciona.

FASE 1 · INFORME (sin cambiar nada, sin unir nada)
Para cada PR (gh pr view y gh pr diff) y para el resultado de juntarlos:
1) Alcance: que solo toquen archivos de su zona. Matías avisó que tocó app.py,
   coordinador/cliente.py, coordinador/graph.py y comun/executor.py (son de la base):
   revisa que esos cambios sean mínimos y correctos. Eduardo: src/comun/panel.html y
   panel.py, y qué hizo con demo.html.
2) Seguridad:
   - Ninguna clave, token ni .env en los archivos del PR ni en su historial de
     commits (git log -p sobre los commits del PR).
   - Abre CADA imagen de evidencias/ del PR buscando: la clave visible (en el campo de
     ingreso, en un curl, en un log), correos, rutas con nombre de usuario, IP
     públicas, notificaciones del sistema.
   - La comparación de la clave usa secrets.compare_digest y la clave no se escribe en
     logs ni en mensajes de error.
   - IMPORTANTE: revisa a qué direcciones envía el coordinador la cabecera X-API-Key.
     Debe enviarla SOLO a la propia app (las rutas internas). Si URLS_AGENTES tiene
     direcciones de terceros (modo distribuido), NO debe mandarles nuestra
     CLAVE_API. Si hoy la manda a cualquier URL, es un hallazgo ⚠️ a corregir.
   - En el frontend la clave vive solo en una variable de JavaScript: sin localStorage,
     sin sessionStorage, sin quedar escrita en el HTML.
3) Contrato frontend ↔ servidor: el frontend manda X-API-Key y muestra el campo
   "detail". Verifica que muestre un mensaje claro para CADA código: 400, 401 (vuelve
   a la pantalla de ingreso), 502, 503 y falta de conexión. Los 503 en particular:
   Eduardo no los listó, confírmalo en el código.
4) Pruebas: encuentra los dos xfail de seguridad (grep xfail en tests/ y en las
   comprobaciones del frontend de Eduardo). Explica qué esperan y qué parte los hace
   pasar. Corre pytest en cada PR por separado en su copia temporal y cuenta los
   resultados. Cuenta también cómo se corren las 44 comprobaciones del frontend (está
   en el documento de Eduardo) y córrelas.
5) Junta ambos en una copia temporal (merge de main + #76 + #77, en ese orden) y
   dime: ¿hay conflictos? ¿en qué archivos? ¿pasan las pruebas juntas? ¿los xfail
   pasan a pasar?
6) Evidencias según la pauta: cada integrante tiene su documento-NOMBRE.md y su
   carpeta evidencias/NOMBRE/ con la tabla (Entorno y fecha LOCAL, Solicitud,
   Resultado esperado, Resultado obtenido, Observaciones); aparece el acceso permitido
   y el rechazado; ninguna ejecución local rotulada como producción; lo simulado está
   declarado como simulado. En el README, la sección Seguridad (Matías) está escrita y
   explica cómo generar CLAVE_API; el .env.example la explica; no hay rutas absolutas
   del computador de nadie.
7) Revisa también que el estado de #75 (mi PR) esté unido a main; si no, dímelo.
Entrega un informe en tabla con ✅ / ⚠️ / ❌ por punto y PR, con la propuesta concreta
para cada ⚠️ y ❌ (y si es un arreglo chico que harías tú o algo que debe rehacer su
dueño). Termina con una recomendación clara. DETENTE AQUÍ.

FASE 2 · INTEGRAR Y ARREGLAR (solo cuando yo escriba "sigue")
8) Trabaja en la rama c2t2/alex-integracion (no en las ramas de los compañeros). Trae
   los últimos cambios de main y luego une, en este orden: origin/c2t2/matias-seguridad
   y origin/c2t2/eduardo-frontend. Si hay conflictos, resuélvelos conservando lo de
   ambos y explícame cada resolución.
9) Aplica solo los arreglos chicos del informe (textos, el mensaje del 503, que la
   clave no se envíe a terceros, quitar la marca xfail de las pruebas que ya pasan,
   detalles de redacción). Lo que sea grande o de diseño: no lo hagas, déjalo
   anotado.
10) Corre pytest completo y las comprobaciones del frontend. Después arranca la app
    igual que Heroku desde la RAÍZ del repo:
    PORT=8000 CLAVE_API=<valor temporal> sh -c 'cd taller-02-c2/proyecto && uvicorn app:app --host 0.0.0.0 --port $PORT'
    y prueba: /salud responde; POST /panel/consultar sin clave → 401; con clave
    incorrecta → 401; con clave correcta y texto vacío → 400; y UNA pregunta real con
    mi GOOGLE_API_KEY (máximo 4 preguntas reales en total, cada una a un agente
    distinto). Muéstrame las líneas del registro A2A de esas preguntas.
11) Commit en c2t2/alex-integracion con un mensaje claro, push y abre UN PR hacia main
    con título "Taller 2 C2: integración seguridad + frontend" y una descripción corta
    (qué trae, qué arreglé, qué quedó pendiente). NO lo unas: lo decido yo. No cierres
    ni toques los PR #76 y #77 y no borres ninguna rama.
12) Termina con: el link del PR, los commits creados, el resultado de las pruebas y
    una lista de lo que Sebastián necesita para desplegar (Config Vars exactas).
```

Continuación tras leer el informe:

```
sigue, incluyendo el cambio del frontend (mostrar detail y el texto correcto del 503).
Dos agregados:
- Las comprobaciones del frontend de Eduardo necesitan Playwright y Chrome, que no
  están en requirements.txt. No los agregues ahí (Heroku no los necesita): crea
  taller-02-c2/proyecto/requirements-dev.txt con lo que haga falta para correrlas y
  agrega al README, en la sección de pruebas, cómo instalarlo y el comando exacto
  (pytest ../evidencias/eduardo/test_panel_eduardo.py -v -rx desde
  taller-02-c2/proyecto). Declara que son opcionales y que necesitan Chrome.
- En la nota de "estado tras la integración" del documento de Eduardo, deja claro
  qué cambié yo en panel.html y por qué, para que él lo revise al volver a probar.
```

---

## 5 · Unir los PR, evidencias y documento de Alex

```
Estamos en el repo agentic-ia-grupo-05, taller en taller-02-c2. Tres fases. Al
terminar la fase 1 te detienes hasta que yo escriba "listas las capturas".

REGLAS: no leas ni imprimas mi .env; ninguna clave en archivos, commits ni en lo que
me muestres. Si necesitas CLAVE_API para probar, genera una temporal que viva solo
en el entorno del comando, sin escribirla en ningún archivo (ni temporal).

FASE 1 · Unir los PR y preparar
1) Une los PR en este orden, con gh pr merge <n> --merge y sin borrar ninguna rama:
   primero #76 (Matías), después #77 (Eduardo) y al final #78 (integración con los
   arreglos de la revisión). Antes de cada uno confirma que no tenga conflictos; si
   alguno los tuviera, detente y avísame. Después actualiza main local, corre pytest
   y confirma que pase igual que en el #78 (168 pruebas). Deja c2t2/alex-integracion
   al día con main.
2) Mi rol en el taller fue la base y la integración. Escribe en
   taller-02-c2/evidencias/alex/GUION.md un guion de capturas, numerado, para
   demostrar que la base funciona de punta a punta en LOCAL. Para cada captura:
   nombre de archivo, qué hacer exactamente y qué debe verse. Que cubra:
   - 01 el arranque igual que Heroku (comando del Procfile desde la raíz) y /salud
   - 02 una pregunta a cada uno de los 4 agentes desde el panel: la respuesta, el
     agente y el motivo (una captura por agente)
   - 03 una pregunta que no es de nadie (va a "ninguno")
   - 04 una pregunta con datos faltantes (por ejemplo "¿dónde hago una feria?" sin
     cantidad de personas): el agente pide el dato antes de concluir
   - 05 la terminal con las líneas del registro A2A de esas preguntas
   Máximo 6 preguntas reales a Gemini en total. Incluye las preguntas exactas a
   escribir, con datos de prueba, y cómo levantar la app con una CLAVE_API temporal
   que yo genere en esa terminal.
   Recomendaciones para capturar en mi Linux Mint (ponlas al inicio del guion):
   usar la Terminal de Mint y no la de VS Code (la de VS Code muestra mi correo);
   ejecutar clear antes de cada captura; capturar la ventana con
   gnome-screenshot -w -d 3 -f ruta.png; en el navegador, que no se vea la clave
   (el campo es de tipo password) ni pestañas con datos personales.
3) Crea taller-02-c2/evidencias/alex/prompts.md vacío, solo con un título y la
   nota "pegar aquí, textuales, las instrucciones que Alex dio a Claude Code".
DETENTE y espera "listas las capturas".

FASE 2 · Revisar mis capturas (cuando yo escriba "listas las capturas")
4) Abre cada imagen de taller-02-c2/evidencias/alex/ y revisa que se vea lo que
   pide el guion y que NO aparezcan claves, correos, rutas con mi nombre de usuario,
   IP públicas ni notificaciones. Dime qué captura repetir, si alguna. Si están
   todas bien, sigue con la fase 3.

FASE 3 · Documento
5) Escribe taller-02-c2/documento-Alex.md, con el mismo formato que los documentos
   de mis compañeros:
   - Mi rol: base del proyecto e integración (revisión de los PR #76 y #77,
     arreglos en el #78).
   - Cómo se construyó: con Claude Code en Linux Mint. Las instrucciones que di
     están en evidencias/alex/prompts.md; cítalas tal cual. Si el archivo sigue
     vacío, deja la sección como "pendiente" y no inventes ningún prompt.
   - Decisiones de la base y por qué: una sola app con el coordinador y los 4
     agentes en rutas (/agentes/{nombre}); rutas en vez de sub-apps (el 307 que no
     sigue el cliente A2A); el descubrimiento de fichas en la primera pregunta; la
     llamada interna por 127.0.0.1 para no pasar dos veces por el router de Heroku,
     que corta a los 30 segundos; WEB_CONCURRENCY=1 para no perder la memoria del
     chat; los archivos de la raíz para desplegar desde una subcarpeta; el registro
     A2A legible.
   - La revisión de integración: lo que se encontró y se arregló (detail en el
     frontend, el texto del 503, el error de GOOGLE_API_KEY en español, el registro
     en consolas cp1252, requirements-dev.txt, quitar los xfail).
   - Una tabla por cada captura con: Entorno y fecha (LOCAL, fecha real de la
     captura), Solicitud, Resultado esperado, Resultado obtenido (con el nombre de la
     imagen) y Observaciones.
   - Lo pendiente o simulado, dicho tal cual. Nada rotulado como producción.
6) En taller-02-c2/README.md completa la sección "Preparación manual" con cómo
   obtener una clave de Gemini (Google AI Studio) y cómo generar CLAVE_API; deja la
   parte de Heroku a Sebastián. Revisa que la tabla de integrantes y aportes esté al
   día.
7) Commit en c2t2/alex-integracion, push y abre un PR hacia main titulado
   "Taller 2 C2: documento y evidencias de Alex". No lo unas. Dame el link.
```

Continuación cuando GitHub marcó el #78 con conflictos (por la doble unión de los
mismos commits, sin archivos en conflicto):

```
arréglalo: git merge origin/main dentro de c2t2/alex-integracion y push. Después
confirma que GitHub ya no marque el #78 como CONFLICTING, únelo con
gh pr merge 78 --merge sin borrar la rama, actualiza main local, corre pytest
(deberían ser 168) y deja c2t2/alex-integracion al día con main. Los archivos
sin commit (GUION.md y prompts.md) no los toques ni los pierdas: si el merge lo
exige, guárdalos con git stash y recupéralos al final. Después quedo con las
capturas.
```

Cambio de plan para las capturas:

```
Cambio de plan: en vez de que yo tome las capturas, tómalas tú, siguiendo el mismo
GUION.md (mismas 6 preguntas reales a Gemini como máximo).

- Crea taller-02-c2/evidencias/alex/capturar_evidencias.py, que use Playwright
  (requirements-dev.txt) con Chrome sin ventana visible, a 1280x900.
- Levanta la app igual que Heroku desde la raíz del repo, con una CLAVE_API temporal
  que viva solo en el entorno del proceso (no la escribas en ningún archivo, ni
  temporal), y redirige la salida del servidor a
  taller-02-c2/evidencias/alex/registro-local.txt.
- Capturas: /salud; la pantalla de ingreso (con la clave tapada, el campo es
  password); un intento con clave incorrecta; las 4 preguntas a cada agente; la
  pregunta que va a "ninguno"; la pregunta con datos faltantes. Que en cada captura
  se vea la pregunta, la respuesta completa, el agente y el motivo (haz scroll o
  captura la página completa si hace falta).
- En cada imagen agrega una franja arriba con: "LOCAL · captura automática
  (Playwright) contra la app real · <fecha y hora>". No uses la palabra SIMULADO:
  no lo es.
- Cuando termine, detén la app y revisa registro-local.txt: que la clave aparezca
  0 veces, que no haya rutas con mi nombre de usuario y que se vean las líneas A2A
  de cada pregunta. Si aparece alguna ruta con mi usuario, reemplázala por
  <carpeta-del-repo>.
- Actualiza GUION.md para que diga que las capturas se tomaron automáticamente y
  cómo repetirlas (comando exacto).

Después sigue directo con la fase 2 (revisa cada imagen) y la fase 3 (documento,
README y PR). En el documento, la tabla de cada caso debe decir en Entorno y fecha:
"LOCAL · <fecha> · captura automática con Playwright contra la app real". Y en
"Resultado obtenido" cita la imagen y las líneas del registro que le corresponden.
```
