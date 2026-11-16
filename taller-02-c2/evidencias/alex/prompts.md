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

---

## 6 · Completar el documento y unir el PR #79

```
Ya pegué mis instrucciones en taller-02-c2/evidencias/alex/prompts.md. Completa la
sección 3 de documento-Alex.md citándolas (puedes resumir los prompts largos con
un enlace al archivo, pero sin cambiar su contenido). Revisa que prompts.md no
contenga claves ni rutas con mi usuario. Commit en c2t2/alex-integracion, push, y
une el PR #79 con gh pr merge 79 --merge sin borrar la rama. Actualiza main local
y confirma que pytest siga en 168.
```

---

## 7 · Revisión de los PR #80 (Matías), #81 (Sebastián) y #82 (Eduardo)

```
Pon c2t2/alex-integracion al día con main. Estamos en el repo agentic-ia-grupo-05,
taller en taller-02-c2. Hay PR de compañeros por revisar: usa gh pr list para
encontrarlos. Deberían ser: el de Matías (documento final, evidencia 08, capturas
LOCAL 15 y 16, y un cambio al catálogo de su agente), el #82 de Eduardo (texto del
503, eliminación de demo.html, evidencias de validación integrada) y el de Sebastián
(sección "Operación en Heroku" del README; si aún no lo abre, revisa directo la rama
origin/c2t2/sebastian-heroku y dime que falta el PR). DOS FASES: al terminar la
fase 1 te detienes hasta que yo escriba "sigue".

REGLAS: no leas ni imprimas mi .env; ninguna clave en archivos, commits ni en lo que
me muestres. Revisa cada PR en una copia temporal (git worktree en /tmp). Revisa
contra lo que pide el enunciado del taller, no más.

FASE 1 · INFORME (sin unir ni cambiar nada)
Para cada PR:
1) Alcance: solo archivos de su zona. Matías: su documento, sus evidencias y
   src/agente_matias/ (el catálogo). Eduardo: panel.html, panel.py, sus documentos y
   la eliminación de src/agente_eduardo/demo.html (verifica que nada lo use).
   Sebastián: la sección Operación del README y sus evidencias.
2) Secretos: ninguna clave, token ni .env en archivos ni en el historial de commits
   del PR. Abre CADA imagen nueva buscando la clave visible, correos, rutas con
   usuario, IP públicas o notificaciones. OJO con las capturas de Heroku: la
   CLAVE_API remota no debe verse en ningún lado (ni en curl, ni en el panel, ni en
   los logs de Heroku). La URL pública de Heroku sí puede aparecer.
3) Notas de asistente pegadas por error: busca en los documentos y en el README
   textos que no son parte del contenido y parecen comentarios de edición, por
   ejemplo "Cambios principales", "Lo que cambié", "Lo que quité", "Mantuve…",
   "tono de informe". Si aparecen, es un hallazgo ⚠️ (los quitarías tú).
4) Coherencia de los errores: en todo el README y los documentos, 502 = falla de
   Gemini, de la red o de un agente; 503 = servidor sin CLAVE_API configurada.
   Señala cualquier lugar que diga otra cosa.
5) Pruebas: pytest en cada PR y con los tres juntos (main + Matías + Eduardo +
   Sebastián, en ese orden). Corre también las comprobaciones del frontend de
   Eduardo. ¿Hay conflictos? ¿en qué archivos? El cambio de catálogo de Matías debe
   tener sus pruebas al día.
6) Evidencias según la pauta: tablas con Entorno y fecha, Solicitud, Resultado
   esperado, Resultado obtenido y Observaciones; las pruebas de Heroku rotuladas como
   REMOTO o HEROKU, nunca "producción"; lo inducido o simulado declarado como tal;
   acceso permitido y rechazado en local y en remoto. La sección Operación del README
   debe explicar: desplegar de nuevo, ver logs, DETENER la app, costo, por qué
   WEB_CONCURRENCY=1, y cómo dar acceso al evaluador (URL en el README, CLAVE_API por
   vía privada). Debe incluir también que la CLAVE_API se rota antes de entregar.
7) Revisa si la URL real de Heroku
   (https://grupo05-taller2-seba-94d12914f3eb.herokuapp.com) quedó escrita en el
   README de forma consistente, y que URL_BASE en la documentación diga que debe
   coincidir con el hostname real de Heroku.
Entrega una tabla ✅ / ⚠️ / ❌ por punto y PR, con propuesta concreta y quién la hace
(arreglo chico mío o de su dueño). Recomienda el orden para unir. DETENTE AQUÍ.

FASE 2 · UNIR (solo cuando yo escriba "sigue")
8) Si los arreglos son chicos (notas de asistente, textos, coherencia 502/503),
   hazlos en c2t2/alex-integracion después de unir, y abre un PR aparte con ellos.
   No modifiques las ramas de los compañeros.
9) Une los PR en el orden que recomendaste, con gh pr merge <n> --merge, sin borrar
   ramas. Si GitHub marca alguno como CONFLICTING sin conflictos reales de archivos,
   avísame antes de hacer nada.
10) Actualiza main local, corre pytest y las comprobaciones del frontend, y arranca
    la app igual que Heroku desde la raíz para verificar /salud. Termina con: commit
    final de main, resultado de pruebas, PR abiertos que queden y la lista de lo que
    Sebastián debe hacer para redesplegar.
```

Continuación tras el informe, que encontró IP públicas en los logs de Sebastián y la
barra de marcadores en capturas de Matías:

```
sigue, con este plan:
1) Une ya el #82 de Eduardo con gh pr merge 82 --merge, sin borrar la rama.
2) NO unas todavía #80 ni #81. Matías y Sebastián van a corregir sus archivos con
   un commit nuevo (sin reescribir historia). Cuando lo hagan, te aviso y los unes
   con gh pr merge <n> --squash (no --merge), para que los commits con las IP y
   los marcadores no entren a main. Antes de unir, verifica que el contenido final
   del PR ya no tenga las IP ni la barra de marcadores.
3) Mientras tanto, prepara en c2t2/alex-integracion (al día con main después del
   #82) todos tus arreglos chicos que no dependen de #80 y #81: notas de proceso
   falsas de Eduardo, rotar CLAVE_API en Operación del README, hostname de URL_BASE
   en Configuración y .env.example, el 503 HTML del router en Seguridad, y mi
   documento (texto nuevo del 503). El "502" de pruebas-remotas.md y la nota del
   catálogo en mi 04a los haces después, cuando #81 y #80 estén unidos.
   Commit, push y PR, pero no lo unas hasta que estén #80 y #81.
4) Dime si el repo aleexng1/agentic-ia-grupo-05 es privado o público (gh repo view).
```

---

## 8 · Revisión del PR #84 de Eduardo

```
Revisa el PR #84 de Eduardo (evidencias de instalación limpia y cierre documental)
en una copia temporal. Sin leer mi .env y sin claves en lo que me muestres. Dos
fases: informe primero; no unas nada hasta que yo escriba "sigue".

FASE 1 · INFORME
1) Alcance: confirma que solo toca documentos y evidencias de Eduardo, y que no
   cambia código de la app ni pruebas del proyecto.
2) Datos personales y secretos: en los archivos nuevos y en el historial de commits
   del PR busca claves o tokens, rutas absolutas con nombre de usuario
   (/home/..., C:\Users\...), nombres de equipo, correos, IP públicas y barras de
   marcadores o notificaciones en las imágenes. Abre cada imagen. Ojo con los logs
   de instalación: suelen traer rutas completas. El repo es público, así que
   cualquier dato personal en un commit queda visible aunque se corrija después.
3) Notas de asistente o de proceso: frases como "sin commit ni push", "queda local",
   "Cambios principales" o "Lo que cambié", que no sean contenido real.
4) Choque con mi PR #83: el #83 ya corrigió frases del documento de Eduardo y de los
   README de sus evidencias. Dime si #84 y #83 tocan las mismas líneas, si habrá
   conflicto y si #84 reintroduce alguna nota de proceso que el #83 ya corrigió.
5) Instalación limpia: resume qué probó (sistema operativo, pasos, comandos,
   resultados) y si cubre lo que hará el profesor: clonar, seguir el README,
   instalar, arrancar y hacer una consulta real. Señala lo que NO cubrió, para
   saber qué me falta en mi prueba de computador limpio. Indica si encontró algún
   paso del README que no funcionara tal cual.
6) Evidencias según la pauta: tabla con Entorno y fecha, Solicitud, Resultado
   esperado, Resultado obtenido y Observaciones; nada rotulado como producción; lo
   simulado declarado.
7) pytest en el PR (deberían seguir siendo 168).
Tabla ✅ / ⚠️ / ❌ por punto, con propuesta y quién la hace. Recomienda el orden de
unión entre #84 y #83. DETENTE AQUÍ.
```

Continuación: las correcciones las hice yo en lugar de pedírselas a Eduardo:

```
Cambio de plan: las correcciones del #84 las hago yo en mi #83, no Eduardo.
1) Une el #84 tal como está con gh pr merge 84 --merge, sin borrar la rama.
2) Pon c2t2/alex-integracion al día con main y resuelve los conflictos del #83 en
   los 3 archivos de Eduardo dejando SU versión (la del #84), como propusiste.
   Revisa a mano pendientes-locales…/README.md para que no quede contradictorio.
3) Encima de su versión, en un commit aparte con mensaje claro, corrige:
   - las 6 frases que dicen "quedan preparadas en el índice, sin commit ni push":
     que digan "publicado en 8a5bb9b, PR #84";
   - "carpeta temporal aprobada de OpenCode" → "carpeta temporal";
   - sus tablas de pruebas a las 5 columnas de la pauta (Entorno y fecha, Solicitud,
     Resultado esperado, Resultado obtenido, Observaciones), moviendo la fecha y el
     entorno que hoy están en el texto. No cambies resultados ni agregues datos que
     no estén ya escritos; si una fila no tiene observación, pon "—";
   - en su tabla "REMOTA futura", remite a evidencias/sebastian/pruebas-remotas.md
     en vez de "por confirmar por Sebastián".
   No toques los bloques "Histórico conservado".
4) Corre pytest (168), push a c2t2/alex-integracion y actualiza la descripción del
   PR #83 con lo nuevo. No lo unas: sigue esperando #80 y #81.
5) Dame la lista exacta de lo que cambié en los archivos de Eduardo, para avisarle.
```

---

## 9 · Unión de #80 (Matías), #81 (Sebastián) y #83 tras sus correcciones

```
Pon c2t2/alex-integracion al día con main. Matías y Sebastián subieron correcciones
a sus PR #80 y #81. Revísalos en copias temporales y, si las correcciones que falten
son puntuales, hazlas tú en c2t2/alex-integracion (no en las ramas de ellos). No
leas mi .env ni muestres claves. DOS FASES: informe y te detienes hasta que yo
escriba "sigue".

FASE 1 · INFORME
1) #80 Matías:
   - Abre las capturas local-*.png nuevas: que ya no se vea la barra de marcadores ni
     ningún otro dato personal; la clave tapada.
   - tests/test_tools_matias.py: qué prueba, que esté en su zona, y que pytest
     completo dé 254 (o di cuántas da).
   - Confirma que el contenido final del PR no tiene datos personales. Las imágenes
     viejas siguen en el historial de su rama (commit normal, sin force): solo
     anótalo, ya lo sabemos.
2) #81 Sebastián:
   - Contenido final: que logs-heroku.txt y cualquier otro archivo ya no tengan IP
     públicas, que la frase del 502 esté corregida y que no quede el detalle de la
     otra app de su cuenta en ningún archivo.
   - Historial: ¿reescribió el commit 999fc22 (push --force) o hizo un commit nuevo?
     Dime si las IP o el nombre de la otra app siguen visibles en algún commit de su
     rama o del PR.
   - Sigue vigente lo de antes: sección Operación completa, rótulos REMOTO/HEROKU,
     tablas de 5 columnas. Revisa si su documento menciona la release desplegada
     (v10) y anota que habrá un despliegue final después de unir #80.
3) Junta main + #80 + #81 + #83 en una copia temporal: conflictos, pytest y
   comprobaciones del frontend.
4) Lista lo que falta en el #83 que ya dejaste anotado (línea de rotar CLAVE_API en
   Operación, el 502 de pruebas-remotas.md si Seba no lo corrigió del todo, la nota
   de mi captura 04a por el catálogo nuevo) más cualquier arreglo puntual nuevo.
Tabla ✅ / ⚠️ / ❌ por punto y PR, con propuesta. DETENTE AQUÍ.

FASE 2 · UNIR (cuando escriba "sigue")
5) Une #80 con gh pr merge 80 --squash y #81 con gh pr merge 81 --squash, sin
   borrar las ramas. Si GitHub marca alguno como CONFLICTING sin conflictos reales,
   avísame antes de hacer nada.
6) Pon c2t2/alex-integracion al día con main, agrega al #83 los arreglos pendientes
   y los puntuales, corre pytest y las comprobaciones del frontend, push, y une el
   #83 con --merge.
7) Termina con: commit final de main, resultado de pruebas, PR abiertos (deberían ser
   cero) y un mensaje corto para Sebastián con lo que necesita para el despliegue
   final (rama main, mismo procedimiento, y qué probar).
```

---

## 10 · Revisión del PR #85 de Eduardo (validación remota del panel)

```
Pon c2t2/alex-integracion al día con main. Revisa el PR #85 de Eduardo (validación
remota del panel en Heroku) en una copia temporal. No leas mi .env ni muestres
claves. DOS FASES: informe y te detienes hasta que yo escriba "sigue". Si hay
arreglos puntuales, los hacemos nosotros en c2t2/alex-integracion, no en su rama.

FASE 1 · INFORME
1) Alcance: solo documento-Eduardo.md y evidencias/eduardo/. Dice que agrega
   "scripts de validación": dime dónde quedan y confirma que no tocan la app, las
   pruebas del proyecto ni el README general.
2) Secretos y datos personales: abre CADA imagen nueva (escritorio y móvil
   emulado). Que no se vea la CLAVE_API remota (ni en el campo, ni en la URL, ni en
   un log), correos, rutas con usuario, IP públicas, barras de marcadores,
   pestañas personales ni notificaciones. Los scripts no deben tener la clave
   escrita: deben leerla de una variable de entorno. Revisa también el historial
   de commits del PR (el repo es público).
3) Notas de proceso o de asistente: frases como "sin commit ni push", "queda
   local", "carpeta aprobada de OpenCode" o comentarios de edición.
4) Formato según la pauta: tablas de 5 columnas; entorno rotulado HEROKU (no
   producción) con fecha y hora; release v12 y su commit; lo no comprobado
   declarado.
5) Coherencia con lo que dijo Sebastián: la v12 es el commit 4593bafb de Heroku y
   él afirma que tiene el mismo código que main (96ebca4). Revisa cómo lo cita
   Eduardo. Si el commit 4593bafb existe en algún lugar del repo de GitHub, compara
   su código con 96ebca4 (git diff --stat); si no existe, anótalo como dato que
   solo puede confirmar Sebastián.
6) pytest (254) y las comprobaciones del frontend (68) en el PR.
7) Revisa si hay algún PR mío abierto (la prueba desde cero) o de Sebastián, y si
   choca con el #85.
Tabla ✅ / ⚠️ / ❌ por punto con propuesta. DETENTE AQUÍ.

FASE 2 · (cuando escriba "sigue")
8) Si el contenido final está limpio, une el #85 con gh pr merge 85 --merge sin
   borrar la rama (si tuviera datos personales en su historial, usa --squash y
   avísame). Pon c2t2/alex-integracion al día con main y haz ahí los arreglos
   puntuales, en un PR aparte que no unes. Dame el estado final: commit de main,
   pruebas y PR abiertos.
```

---

## 11 · Revisión del PR #87 de Sebastián (release v12 y pruebas remotas)

```
Pon c2t2/alex-integracion al día con main. Revisa el PR #87 de Sebastián (release
v12 y pruebas remotas) en una copia temporal. No leas mi .env ni muestres claves.
DOS FASES: informe y te detienes hasta que yo escriba "sigue". Arreglos puntuales
los hacemos nosotros en c2t2/alex-integracion, no en su rama.

FASE 1 · INFORME
1) La resolución de conflictos: Sebastián unió main en su rama. Compara el PR
   contra main (gh pr diff 87 y git diff main...): confirma que SOLO cambia su
   documento y evidencias/sebastian/, que no revierte ningún archivo de otros
   (documentos de Eduardo, Matías o míos, README, código) y que no quedan marcas
   de conflicto (<<<<<<<, =======, >>>>>>>) en ningún archivo del repo.
2) Secretos y datos personales en el contenido final y en el historial de sus
   commits (el repo es público): CLAVE_API o GOOGLE_API_KEY con valor, IP públicas
   de clientes (Heroku las registra en los logs; las del router de Heroku sí
   pueden quedar), el nombre de su otra app de Heroku, correos, rutas con
   usuario. Abre cada imagen nueva.
3) Lo que le pedimos:
   - la release v12 y su commit en la línea pendiente de su documento;
   - la confirmación de que 4593bafb tiene el mismo código que 96ebca4 (resultado
     de git diff --stat o de heroku releases:info). Si no está, ❌;
   - si rotó la CLAVE_API: cuándo, y si eso generó una release nueva (v13 o más)
     con el mismo código; que quede anotado;
   - pruebas remotas sobre esa versión: una pregunta a cada uno de los 4 agentes,
     una que va a "ninguno", 401 sin clave y con clave incorrecta, 400 con texto
     vacío, y en el log el envío A2A a http://127.0.0.1:…;
   - la pregunta de Matías ("feria infantil de 3 horas desde las 15:00"): ¿trae
     "Función de títeres" y 0 minutos libres? Si dio otra cosa, anótalo, no lo
     corrijas.
4) Formato: tablas de 5 columnas, rótulo HEROKU con fecha y hora, nada como
   "producción", lo no comprobado declarado. Notas de asistente o de proceso
   ("Cambios principales", "Lo que quité", "sin commit ni push").
5) pytest (254) y comprobaciones del frontend (68) en el PR.
Tabla ✅ / ⚠️ / ❌ por punto con propuesta y quién la hace. Recomienda --merge o
--squash según su historial. DETENTE AQUÍ.

FASE 2 · (cuando escriba "sigue")
6) Une el #87 con la opción que recomendaste, sin borrar la rama. Pon
   c2t2/alex-integracion al día con main, haz los arreglos puntuales, corre las
   pruebas, abre un PR y únelo con --merge. Dame el commit final de main y
   confirma que no quedan PR abiertos.
```

Continuación tras el informe (versión acotada a lo que pide la pauta):

```
sigue, pero en versión corta:
1) Une el #87 con --squash, sin borrar la rama.
2) En c2t2/alex-integracion haz solo: 127.0.0.1 de vuelta en las 6 líneas A2A de
   logs-heroku.txt; la columna "Entorno y fecha" de vuelta en la tabla principal;
   las 3 tablas nuevas a 5 columnas con lo que ya está escrito; "en producción" →
   "en Heroku". Para la fecha de sus pruebas en v12 pon "HEROKU · release v12 ·
   fecha por confirmar (Sebastián)" y agrega que las pruebas de Eduardo del 15/11
   son de la misma release. La pregunta de la feria infantil no hace falta: no la
   agregues.
3) pytest, PR y únelo con --merge. Dame el commit final de main y confirma que no
   quedan PR abiertos.
```
