# Registro de prompts · Etapa 1

Taller 2 · Agente RAG · Alex Nail · Grupo 05

## Cómo se trabajó

- **Ayudante usado:** Claude Code (no OpenCode), en Linux Mint. El taller pide "solo prompts al ayudante, sin tocar el código a mano", y se cumplió: todo el código lo escribió Claude Code a partir de los prompts de abajo.
- **Los prompts no son los del deck tal cual.** Cada uno se adaptó (Linux, Claude Code, carpeta del repo del grupo, Redis compartido, cuota gratuita de Gemini). Por eso, en cada prompt hay tres partes:
  1. **Cambios respecto del prompt del deck** y por qué.
  2. **Prompt exacto usado.**
  3. **Qué hubo que corregir después**, o qué hizo el ayudante sin que se le pidiera.
- **Dónde vive el proyecto:** `taller-02/alex_nail/proyecto/` del repo del grupo, en la rama `alex/taller-02`, con su propio `.venv` y `.env`. El `.env` nunca se sube.

### Prompts al ayudante vs prompts del agente

Hay dos tipos de prompt y no son lo mismo:
- **Los prompts al ayudante** (este registro) son instrucciones para que Claude Code *escriba el código*. Si salen mal, se corrige el prompt y se vuelve a pedir.
- **Los prompts del agente** (`SYSTEM_PROMPT` y `USER_PROMPT` en `src/rag/prompts.py`) viven *dentro* del agente terminado y le dicen al modelo Gemini *cómo responder* cada pregunta. Esos se pulen en la Etapa 5.

---

## Prompt 1 · Entorno

**Cambios respecto del deck**
- Adaptado a Claude Code y Linux, con la ruta de la carpeta del taller y la regla de no tocar nada fuera de ella. El repo es compartido con el grupo.
- Agrega `CLAUDE.md`, porque Claude Code lee ese archivo y no `AGENTS.md`.
- Agrega un `.gitignore` propio, porque el repo es público: no deben subirse `.env`, `.venv` ni los índices.
- `requirements.txt` con versiones fijas.
- `src/rag/` queda como esqueletos. En un ensayo anterior, un `storage.py` vacío hizo fallar el Prompt 2, así que su implementación se pasó al Prompt 2.
- No crea el `.env`: las claves se pegan a mano.

**Prompt exacto usado**

```
Estoy en Linux Mint, dentro de taller-02/alex_nail/proyecto/ del repo del grupo (rama alex/taller-02). Esta carpeta ya tiene subcarpetas vacías: src/rag, scripts, tests, docs y data. Todo lo del proyecto (código, .venv y .env) debe quedar DENTRO de esta carpeta. No modifiques nada fuera de ella. No hagas commit ni push. No crees ni leas el archivo .env.

Genérame un proyecto RAG en Python 3.12 con entorno virtual .venv (python3.12 -m venv .venv, dentro de esta carpeta) e instala dentro de él: langgraph, langchain, langchain-google-genai, langchain-redis, redis, langchain-community, langchain-text-splitters, pypdf, faiss-cpu, numpy y python-dotenv. Genera requirements.txt con esas 11 librerías fijadas a la versión instalada (nombre==versión).

Crea un .env.example con estas variables (y nunca pongas valores reales en el código ni en este archivo):
- GOOGLE_API_KEY
- REDIS_URL (ej. redis://localhost:6379)
- VECTOR_STORE=redis   (alternativa: faiss)
- EMBEDDING_MODEL=models/gemini-embedding-001
- MODELO=gemini-3.5-flash-lite
- PREFIJO=equipo1   (prefijo del índice: cada equipo usa uno distinto)
- CHUNK_SIZE=800, CHUNK_OVERLAP=120, TOP_K=3, UMBRAL=0.65

Crea un .gitignore en esta carpeta que excluya: .env, .venv/, __pycache__/, .pytest_cache/, data/*.npy y data/*/ (los índices FAISS son subcarpetas de data/).

Crea la estructura: main.py, y en src/rag/ los archivos __init__.py, graph.py, prompts.py, tools.py y storage.py como esqueletos con un comentario de una línea que diga qué irá en cada uno (no implementes nada todavía). Deja intactas scripts/, tests/, docs/ y data/.

Crea un AGENTS.md con estas reglas:
- Los agentes van en src/{{nombre_agente}}/ con graph.py, prompts.py y tools.py; este proyecto tendrá además src/rag/storage.py con una función get_vector_store(prefijo) que devuelve Redis o FAISS según VECTOR_STORE.
- Se ejecutan desde la raíz: python main.py {{nombre_agente}} "pregunta".
- Flag --saltos: imprime los nodos por los que pasó el grafo. Flag --diagrama: imprime el Mermaid del grafo sin ejecutarlo.
- Los scripts sueltos (demos, ingesta) van en scripts/ y los índices FAISS en data/.
- El modelo de embeddings se lee SIEMPRE de EMBEDDING_MODEL, en un solo lugar.
- Todo el proyecto vive en taller-02/alex_nail/proyecto/; no se modifican archivos fuera de esa carpeta. Los secretos van solo en .env (que git ignora) y nunca se imprimen.

Crea también un CLAUDE.md que diga solo: "Lee y sigue AGENTS.md".

Al terminar, verifica que todas las librerías importen dentro del .venv, muéstrame el árbol de carpetas y `git status --short -uall`, y explícame en simple qué creaste y cómo activo el entorno.
```

**Qué hubo que corregir**
- El ayudante lo hizo bien a la primera: las 11 librerías importaron.
- La terminal tenía activo otro entorno (el `.venv` de la raíz del repo, que usa el grupo para los notebooks). El ayudante lo detectó y creó el entorno del proyecto con el Python del sistema, para no depender de ese.
- Por su cuenta, borró `src/rag/.gitkeep`, que ya no hacía falta.
- **Error mío, no del ayudante:** al pegar las claves en el `.env` quedó la línea `REDIS_URL=REDIS_URL=redis://...` (el nombre repetido). Lo detectó el ayudante en el Prompt 2 sin leer ni mostrar la clave.

---

## Prompt 2 · Demos de embeddings y prueba del almacén

**Cambios respecto del deck**
- **Implementa `storage.py`** (`get_embeddings`, `get_vector_store`, `guardar_faiss`), que el Prompt 1 dejó vacío. El deck lo da por hecho, pero ningún prompt anterior lo pide.
- Agrega `a_parecido()`. Redis y FAISS no entregan "parecido" sino distancias, y cada uno a su manera. Sin convertirlas, no se pueden comparar con `UMBRAL`.
- El Redis del curso es compartido entre grupos. La prueba usa un índice desechable (`{PREFIJO}_test`), lo borra al terminar y nunca recorre todas las claves del servidor.
- Las frases por argumentos y `--pregunta`, para la Etapa 2.

**Prompt exacto usado**

```
Sigue AGENTS.md. Antes de escribir código, lee AGENTS.md, .env.example y los esqueletos de src/rag/. No leas ni imprimas el .env; si necesitas saber una variable, dime solo si está definida (y para REDIS_URL, tapa la contraseña).

PASO 0 · Implementa src/rag/storage.py (quedó como esqueleto en el prompt anterior):
- get_embeddings(): devuelve GoogleGenerativeAIEmbeddings con EMBEDDING_MODEL del .env. Es el ÚNICO lugar del proyecto donde se crea el modelo de embeddings; todo lo demás lo importa de aquí.
- get_vector_store(prefijo): según VECTOR_STORE devuelve:
  · faiss: un FAISS cargado desde data/{prefijo}/ si existe (load_local con allow_dangerous_deserialization=True), o uno vacío listo para agregar documentos si no existe.
  · redis: un RedisVectorStore de langchain-redis con índice llamado {prefijo}, métrica COSINE, usando REDIS_URL. Si REDIS_URL no está o el servidor no tiene búsqueda vectorial, lanza un error claro que explique que se necesita Redis 8 o redis-stack (no el redis-server de apt).
- guardar_faiss(store, prefijo): guarda con save_local en data/{prefijo}/.
- a_parecido(puntaje): convierte el puntaje de cada motor a parecido entre 0 y 1 (mayor = más parecido). Redis COSINE entrega distancia = 1 − parecido; FAISS con vectores normalizados entrega distancia euclídea al cuadrado = 2·(1 − parecido). Verifica empíricamente qué entrega cada uno antes de dar la fórmula por buena.

Después genérame dos scripts de demostración en scripts/, siguiendo AGENTS.md:

1) scripts/demo_embeddings.py
- Usa get_embeddings() de storage.py.
- Toma tres frases: dos que dicen lo mismo con otras palabras y una de un tema distinto (permite pasarlas por argumentos: python scripts/demo_embeddings.py "frase 1" "frase 2" "frase 3"; si no, usa unas de ejemplo: "¿Cómo reinicio el router?", "El router no da internet", "Receta de pan amasado").
- Imprime cuántos números tiene cada vector y los primeros 5.
- Calcula el parecido coseno entre cada par y muéstralo en una tabla ordenada de mayor a menor, marcando el par más parecido.
- Luego embebe una "pregunta" (permite pasarla con --pregunta; por defecto "no tengo internet") y muestra cuál de las tres frases queda más cerca.

2) scripts/test_storage.py
- Usa get_vector_store() de src/rag/storage.py.
- El Redis es COMPARTIDO con otros grupos: usa un índice de prueba aparte llamado {PREFIJO}_test (nunca el índice PREFIJO real) y bórralo al terminar junto con sus documentos (FT.DROPINDEX con DD), aunque el script falle a la mitad. Nunca recorras todas las claves del servidor (SCAN completo): es lento y toca datos de otros.
- Si VECTOR_STORE=redis: conecta con REDIS_URL, hace PING y crea el índice vectorial si no existe. Si es faiss: crea uno en memoria (sin guardar en disco).
- Guarda las tres frases de ejemplo de demo_embeddings.py como documentos con metadata {"fuente": "demo"}.
- Busca con la pregunta "no tengo internet" y muestra los 2 fragmentos más cercanos con su puntaje original y su parecido (con a_parecido), aclarando qué significa cada número.
- Termina diciendo claramente OK o qué falló (sin REDIS_URL debe explicar cómo ponerla, no romperse).

Al final ejecuta:
- python scripts/demo_embeddings.py
- python scripts/test_storage.py   (con mi .env, que dice VECTOR_STORE=redis)
- VECTOR_STORE=faiss python scripts/test_storage.py   (la variable solo para ese comando; no edites el .env)
Confirma que el índice {PREFIJO}_test ya no existe en Redis, muéstrame `git status --short -uall` y explícame en simple los resultados. No hagas commit ni push.
```

**Qué hubo que corregir**
- El código salió bien a la primera. `test_storage.py` dio **OK en Redis y en FAISS**, y el índice de prueba quedó borrado (`FT.INFO` respondió "no such index").
- Detectó la línea mal escrita del `.env` (ver Prompt 1). No editó el archivo: avisó, y para probar quitó el texto repetido solo en memoria.
- Verificó las fórmulas de `a_parecido()` contra el coseno calculado a mano. Redis entrega `1 − parecido` (0,2298 → 0,7702) y FAISS el doble (0,4596 → 0,7702). Las dos dan el mismo parecido.
- **Hallazgo:** dos frases sin relación (router ↔ pan amasado) dieron 0,788, por encima del `UMBRAL=0.65` del deck. Con este modelo el "piso" de parecido es alto, y se retoma en la Etapa 4.

---

## Prompt 3 · Índice vectorial vs coseno a mano

**Cambios respecto del deck**
- `--store redis|faiss` para elegir la base en cada corrida.
- En Redis, A y B usan **los mismos HASH**, en vez de guardar los vectores dos veces. Así se gasta la mitad de memoria en el servidor compartido.
- Antes de guardar en Redis revisa la memoria libre, y se niega si ocuparía más de la mitad.
- Claves `{PREFIJO}_bench`, que se borran al terminar aunque falle.
- n = 20.000 solo en FAISS y con vectores simulados, para no pagar 20.000 embeddings.
- La salida se guarda en `../pruebas/capturas/` como evidencia.

**Prompt exacto usado**

```
Sigue AGENTS.md. No leas ni imprimas el .env. No toques storage.py salvo que sea necesario (si lo es, dime qué y por qué antes). No hagas commit ni push.

Genérame scripts/indice_vs_coseno.py para comparar las dos formas de buscar con los MISMOS datos. Uso: python scripts/indice_vs_coseno.py --n 2000 [--store redis|faiss] (por defecto, el VECTOR_STORE del .env).

- Genera n fragmentos de texto sintéticos (frases cortas variadas sobre 5 temas) y embébelos UNA vez con get_embeddings(); guarda los vectores en data/vectores_demo.npy y los textos en data/textos_demo.json para no volver a pagar embeddings si se repite (si el archivo ya tiene suficientes vectores, reutilízalos). Embebe en lotes y, si Gemini responde por límite de uso (error 429), espera y reintenta mostrando el avance.
- Para n mayor que los vectores reales guardados (por ejemplo 20000), NO pagues más embeddings: genera vectores simulados copiando los reales con un pequeño ruido aleatorio y renormalizando a largo 1. Avisa en pantalla que esa escala es simulada.
- Forma A, "coseno a mano": trae TODOS los vectores a Python y calcula el coseno con numpy contra el vector de la pregunta; ordena y toma top-3. En redis, los vectores se leen desde los HASH del servidor (cada fragmento un HASH); en faiss, desde un arreglo numpy en memoria.
- Forma B, "índice vectorial": busca los top-3 con el índice (en redis, FT.SEARCH KNN sobre un índice FLAT con métrica COSINE; en faiss, el índice FAISS). En redis, el índice debe apuntar a los MISMOS HASH de la forma A: no guardes los vectores dos veces.
- REDIS COMPARTIDO: usa claves e índice con prefijo {PREFIJO}_bench y bórralos al terminar (FT.DROPINDEX con DD), aunque el script falle a la mitad. Nunca recorras todas las claves del servidor. Antes de guardar, estima los MB que vas a ocupar y compáralos con la memoria libre del servidor (INFO memory: maxmemory y used_memory); si ocuparías más de la mitad de lo libre, no guardes y explica por qué.
- Para 5 preguntas, imprime una tabla: pregunta, top-3 de A, top-3 de B, ¿coinciden?, tiempo de A en ms, tiempo de B en ms, cuántos vectores viajaron a Python en cada caso.
- Repite para n = 200, 2000 y (si --n lo permite) 20000, y muestra cómo crece el tiempo de A frente a B. En redis, 20000 no se corre (memoria del servidor compartido): dilo en pantalla.
- Al final imprime una conclusión de dos líneas generada por el propio script a partir de los números (no la escribas fija), incluyendo con los números de n = 200 cuándo conviene la forma A.
- Guarda toda la salida también en ../pruebas/capturas/indice_vs_coseno_{store}.txt (evidencia para la entrega).

Después ejecuta, en este orden:
1) python scripts/indice_vs_coseno.py --n 20000 --store faiss
2) python scripts/indice_vs_coseno.py --n 2000 --store redis
Confirma que no quedó ningún índice ni clave {PREFIJO}_bench en Redis, muéstrame `git status --short -uall` y explícame en simple los resultados.
```

**Qué hubo que corregir**
- **Cuota diaria de Gemini agotada a mitad de la corrida.** El plan gratuito permite unos 1.000 textos por día, y se alcanzaron a guardar 900 vectores reales. El ayudante agregó `--max-reales 900`: completa cada n con vectores simulados y lo avisa en pantalla. En n = 2.000 hay 900 reales y 1.100 simulados. Los tiempos no cambian, porque el cálculo cuesta lo mismo con vectores reales o simulados.
- Por la misma causa agregó: detención inmediata cuando el error 429 es de cuota diaria (no tiene sentido esperar), y caché de las 5 preguntas.
- **Redis 8.4 responde en otro formato.** `FT.INFO` y `FT.SEARCH` devolvían algo distinto de lo esperado, así que esas llamadas pasaron a la API de búsqueda de redis-py.
- Agregó `data/*_demo.json` al `.gitignore`.
- **Conflicto con `AGENTS.md`:** escribió la evidencia en `../pruebas/capturas/`, fuera de `proyecto/`, porque el prompt lo pedía, y avisó que eso contradecía la regla. Se agregó una excepción a `AGENTS.md` en el Prompt 4.
- El top-3 de A y de B coincidió en las 25 búsquedas. Redis: B fue 4 veces más rápido en n = 200 y 16 veces en n = 2.000. FAISS plano: numpy le ganó al índice. Es esperable, porque un índice plano también recorre todos los vectores.

---

## Prompt 4 · Ingesta

**Cambios respecto del deck**
- Excepción en `AGENTS.md` para escribir evidencia en `../pruebas/`.
- **El PDF:** es un TFG de una autora externa (Pulkowska, 2025) y el repo es público. El ayudante arma `docs/humor-computacional.pdf` desde el original quitando la portada y el índice y **conservando el resumen**, que es el fragmento que responde "¿de qué trata el documento?". Quedan 29 páginas. Los PDF van en `.gitignore` y la cita en el README.
- **Caché de embeddings** en `storage.py`, por la cuota diaria: un texto ya convertido no se vuelve a pagar.
- **Limpieza del texto:** este PDF se extrae con cada palabra separada por saltos de línea y espacios. Sin limpiar, alrededor de un 23% de cada fragmento es relleno.
- `--solo-cortar` corta y mide sin gastar cuota, y además estima cuánta cuota se gastaría.
- `--reset` borra solo el índice propio (Redis compartido).
- Solape mostrado entre fragmentos de la **misma página**, porque el cortador trabaja página por página.
- Detenerse y esperar OK antes de gastar.

**Prompt exacto usado**

```
Sigue AGENTS.md. No leas ni imprimas el .env. No hagas commit ni push.

PASO 0 · AGENTS.md: agrega esta regla: "La evidencia para la entrega (salidas de scripts y tablas) se guarda en ../pruebas/ y ../pruebas/capturas/; es la única carpeta fuera de proyecto/ donde se puede escribir."

PASO 1 · El PDF. En docs/original-completo.pdf está un TFG de 31 páginas. Con pypdf crea docs/humor-computacional.pdf quitando la página 1 (portada) y la página 3 (índice), y conservando la página 2 (resumen) y de la 4 a la 31 (29 páginas en total). Verifica que todas las páginas tengan texto. El documento es de una autora externa: agrega docs/*.pdf al .gitignore (el PDF va en el zip de entrega, no en el repo público) y en el README.md del proyecto (créalo si no existe) agrega una sección "Documento usado" con: "Pulkowska, W. (2025). Detección automática del humor: los algoritmos aplicados a ambigüedad, incongruencia y rasgos complementarios. Trabajo de Fin de Grado, Grado en Filología Hispánica. Tutor: Francisco J. Salguero Lamillar. Se usó una versión sin portada ni índice."

PASO 2 · Caché de embeddings. La cuota gratuita de Gemini es de unos 1000 textos por día, así que en src/rag/storage.py haz que get_embeddings() guarde en caché lo que ya convirtió: envuelve el modelo con CacheBackedEmbeddings y un LocalFileStore en data/cache_embeddings/ (git ya ignora data/*/), usando EMBEDDING_MODEL como namespace para no mezclar modelos, y activa también la caché de preguntas (query_embedding_cache). Explícame en una línea qué cambiaste. No cambies nada más de storage.py.

PASO 3 · Genérame scripts/ingest.py. Uso: python scripts/ingest.py ruta/al/archivo.pdf [--reset] [--solo-cortar]
- Carga el PDF con PyPDFLoader (un Document por página).
- Limpia el texto de cada página antes de cortar: este PDF se extrae con cada palabra separada por saltos de línea y espacios, así que reemplaza cualquier secuencia de espacios en blanco por un solo espacio. Informa cuántos caracteres había antes y después de limpiar.
- Corta con RecursiveCharacterTextSplitter usando CHUNK_SIZE y CHUNK_OVERLAP del .env y separadores ["\n\n", ". ", " ", ""].
- Cada fragmento lleva metadata: fuente (nombre del archivo), pagina (número de página del visor, desde 1) y fragmento (número).
- --solo-cortar: corta y muestra las estadísticas sin embeber ni guardar nada (sirve para comparar configuraciones sin gastar cuota).
- Antes de embeber, cuenta cuántos fragmentos NO están en la caché (esos son los que gastan cuota) y muéstralo. Si Gemini responde que se agotó la cuota diaria, detente con un mensaje claro y explica que al reintentar mañana la caché evita volver a pagar lo ya convertido.
- Embebe con get_embeddings() y guarda en la base que devuelve get_vector_store(PREFIJO):
  · redis: índice vectorial llamado PREFIJO, métrica COSINE. El Redis es COMPARTIDO: --reset borra SOLO el índice PREFIJO y sus documentos (FT.DROPINDEX con DD); nunca recorras todas las claves del servidor.
  · faiss: índice en data/PREFIJO/ guardado con guardar_faiss.
- Sin --reset, agrega; si ese mismo archivo ya está ingestado (misma fuente), avisa y pregunta si quiero continuar, para no duplicar.
- Al final imprime: páginas leídas, fragmentos generados, tamaño promedio de fragmento, y muestra lado a lado el fragmento 1 y el 2. Como el cortador trabaja página por página, el solape solo existe entre fragmentos de la MISMA página: si 1 y 2 están en páginas distintas, dilo, y muestra además el primer par de fragmentos consecutivos de una misma página, marcando el texto que se repite.
- Si el PDF no existe o no tiene texto (PDF escaneado), dilo claro y termina sin romperse.
- Guarda toda la salida también en ../pruebas/capturas/ingesta_{CHUNK_SIZE}_{CHUNK_OVERLAP}.txt.

PASO 4 · Ejecuta SOLO esto:
python scripts/ingest.py docs/humor-computacional.pdf --solo-cortar
Dime cuántos fragmentos salen, cuántos embeddings gastaría la ingesta real, y DETENTE. No hagas la ingesta real hasta que yo te dé el OK.

Al final muéstrame `git status --short -uall` (el PDF no debe aparecer) y explícame en simple qué hiciste.
```

**Prompt de seguimiento (OK para la ingesta real)**

```
OK, adelante con la ingesta real, con estos ajustes:

1) Agrega langchain-classic==1.0.8 a requirements.txt.

2) Ejecuta CON --reset, porque mi índice AlexNail en Redis todavía tiene fragmentos de otro documento (devoluciones.pdf) de una sesión anterior y no quiero mezclarlos:
python scripts/ingest.py docs/humor-computacional.pdf --reset

3) Después confirma cuántos documentos quedaron en el índice AlexNail (con FT.INFO, sin recorrer claves) y que ninguno tiene fuente distinta de humor-computacional.pdf. No hagas búsquedas de prueba (quiero ahorrar cuota de Gemini para el agente).

4) Si la cuota diaria se agota, detente, dime cuántos fragmentos quedaron en la caché y qué comando debo correr mañana.

No hagas commit ni push. Muéstrame `git status --short -uall` al final.
```

**Qué hubo que corregir**
- **Nombre del PDF original:** el prompt decía `docs/original-completo.pdf`, pero el archivo se llamaba `El humor computacional.pdf`. El ayudante comprobó que era el mismo documento (portada en p. 1, índice en p. 3) y lo usó sin renombrarlo.
- **Caché de preguntas separada,** no compartida como decía el prompt. Gemini convierte distinto un mismo texto según sea pregunta o documento, así que compartir la caché habría devuelto vectores equivocados. Es una mejora del ayudante.
- **`batch_size=100`:** sin esto, si la cuota se cortaba a mitad de la llamada, se perdía todo lo ya pagado.
- **Metadata:** descartó la que trae PyPDF, porque incluye la ruta completa del computador y no conviene subirla al Redis compartido.
- **Faltaba una librería:** la caché usa `langchain-classic`, que no estaba en `requirements.txt`. Se agregó con el prompt de seguimiento.
- **Comando sin `--reset`:** el ayudante propuso la ingesta real sin `--reset`. Se corrigió en el prompt de seguimiento, porque el índice tenía fragmentos de otro documento.
- **La ingesta real falló por cuota,** que seguía agotada desde el Prompt 3. **Error de diseño encontrado:** `--reset` borraba el índice *antes* de embeber, así que el corte lo dejó vacío. El ayudante cambió el orden: ahora borra solo cuando todos los embeddings están listos.
- **Datos del corte (800/120):** 29 páginas, 96 fragmentos, 614 caracteres en promedio. La limpieza bajó el texto de 73.295 a 56.299 caracteres. Los fragmentos 1 y 2 están en la misma página pero **no repiten texto**: el cortador solo repite oraciones completas que quepan en 120 caracteres, y solo 33 de los 67 pares de una misma página comparten texto. El script muestra el par 10–11 (p. 4), que sí repite 111 caracteres.

---

## Prompt 5 · Agente rag

**Cambios respecto del deck**
- `buscar` usa `buscar_fragmentos()` de `tools.py` y convierte el puntaje con `a_parecido()`.
- Si el índice no existe, el agente avisa que hay que ingestar, en vez de caerse.
- `--saltos` muestra también el `UMBRAL`.
- Escrito con la cuota agotada: se pidió no ejecutar nada que llamara a Gemini y probar solo `--diagrama`, las importaciones y el texto de los prompts.

**Prompt exacto usado**

```
Sigue AGENTS.md. No leas ni imprimas el .env. No toques storage.py ni ingest.py (si crees que hace falta, dime qué y por qué antes). No hagas commit ni push.

IMPORTANTE: hoy la cuota diaria de Gemini está agotada. No ejecutes nada que llame a Gemini (ni embeddings ni el modelo). Solo escribe el código y prueba lo que no gasta cuota.

Nuevo agente
Nombre: rag
Agente en LangGraph (src/rag/) que responde preguntas usando SOLO los fragmentos guardados por scripts/ingest.py. Se ejecuta con: python main.py rag "pregunta".

Estado: pregunta, fragmentos (lista con texto, fuente, pagina, parecido), mejor_parecido, respuesta y messages (memoria con MemorySaver por thread_id).

Nodos:
- buscar: usa una función buscar_fragmentos() en tools.py que consulta get_vector_store(PREFIJO) y trae TOP_K fragmentos con su puntaje; convierte el puntaje a parecido con a_parecido() de storage.py (mayor = más parecido) y guarda el mejor parecido en el estado. El embedding de la pregunta lo hace el store con get_embeddings() (no embebas dos veces). Si el índice no existe o está vacío, termina con un mensaje claro que diga que primero hay que correr scripts/ingest.py, sin romperse.
- ¿evidencia? (arista condicional): si mejor_parecido >= UMBRAL va a responder; si no, va a no_se.
- responder: llama a MODELO con un SYSTEM_PROMPT en prompts.py con estas reglas: (1) responde SOLO con lo que está en el contexto; (2) cita cada afirmación como [archivo p.N]; (3) si el contexto no alcanza para una parte, dilo en vez de inventar; (4) español, breve. El USER_PROMPT lleva el contexto y la pregunta entre etiquetas <contexto> y <pregunta>.
- no_se: devuelve "No encontré evidencia en los documentos para responder eso" sin llamar al modelo.

main.py (según AGENTS.md): carga el agente por nombre desde src/{agente}/graph.py.
- --saltos: muestra la ruta (buscar → responder o buscar → no_se), el UMBRAL usado y los fragmentos recuperados con su parecido y página.
- --diagrama: imprime el Mermaid del grafo sin ejecutarlo (sin llamar a Gemini).
- Los prompts van en prompts.py; nada de reglas dentro de graph.py.

Pruebas permitidas hoy (sin cuota):
1) python main.py rag --diagrama   → guarda la salida también en ../pruebas/capturas/diagrama_antes.txt (será el "antes" de la etapa 6).
2) Verifica que todos los módulos importen y que el grafo compile.
3) Revisa que el SYSTEM_PROMPT y el USER_PROMPT de prompts.py tengan exactamente las 4 reglas y las etiquetas pedidas, y muéstramelos completos.

Al final explícame en simple qué hace cada archivo y muéstrame `git status --short -uall`.
```

**Qué hubo que corregir o qué hizo sin que se le pidiera**
- Corrió las pruebas con `GOOGLE_API_KEY` vacía, para que fuera imposible gastar cuota.
- **Agregó `--hilo` sin que se le pidiera.** Sirve para elegir el `thread_id`. No cambia el comportamiento.
- **El grafo tiene una tercera salida, `fin`,** para cuando el índice está vacío. El deck dibuja solo dos. Existe porque, sin ella, `get_vector_store()` crearía un índice vacío y gastaría una consulta solo para medir la dimensión. Se comprobó que `AlexNail` siguió sin existir después de la prueba.
- Probó el grafo con una búsqueda y un modelo falsos: con parecido 0,80 va a `responder`, con 0,50 va a `no_se`, con 0,65 (justo el umbral) responde, y dos preguntas en el mismo hilo dejan 4 mensajes en la memoria.
- El `SYSTEM_PROMPT` y el `USER_PROMPT` quedaron con las 4 reglas y las etiquetas `<contexto>` y `<pregunta>`.

---

## Revisión de seguridad antes del primer commit

El repo del grupo es público. Antes de subir, se le pidió al ayudante revisar los archivos versionados en busca de URLs con contraseña, claves de Google, los valores reales del `.env` (comparados sin imprimirlos) y rutas locales.

- **Hallazgo:** un texto de ayuda de `storage.py` tenía una URL redis:// de ejemplo con usuario y contraseña de relleno. Era un ejemplo, no la contraseña real, pero se cambió por "Si tu Redis pide contraseña, inclúyela en la URL (mira .env.example)." para que el repo no tuviera nada con forma de secreto.
- La revisión repetida dio 0 hallazgos. Commit `04b968e` subido a `alex/taller-02`, sin `.env`, `.venv`, cachés ni PDF.

---

## Pendiente para cerrar la Etapa 1

- [ ] `python scripts/test_storage.py` (repetir en el orden del deck)
- [ ] `python scripts/ingest.py docs/humor-computacional.pdf --reset` con la cuota nueva
- [ ] `python main.py rag "¿De qué trata el documento?" --saltos` y **captura de pantalla** con la ruta y una respuesta citada
- [ ] Anotar aquí si alguno de esos comandos necesitó corrección
