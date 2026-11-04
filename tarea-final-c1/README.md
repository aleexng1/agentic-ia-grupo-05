# Agente revisor de rendiciones de gastos — Tarea Final Curso 1 (Grupo 05)

Agente hecho con LangGraph y Gemini que revisa gastos rendidos de **Comercial Los Alerces SpA**, una
empresa ficticia. Busca en la política (RAG con Redis), valida las reglas exactas con código y decide
aprobar, observar o rechazar. Empresa, personas, cuentas y montos son **ficticios**.

- Caso completo: [docs/caso_y_criterio.md](docs/caso_y_criterio.md)
- Matriz de evidencias de la pauta: [docs/evidencias_pauta.md](docs/evidencias_pauta.md)

## Caso y criterio de éxito

En **Comercial Los Alerces SpA** (ficticia), cada colaborador elige la política y la categoría de
sus gastos, y es común que elija mal: una misma categoría, como peaje o almuerzo, existe en varias
políticas. Cada una tiene un tratamiento contable distinto, así que clasificar mal genera cuentas
equivocadas y reprocesos.

El agente ayuda al analista de Control de Gestión en la primera revisión. Recibe un gasto, busca en
la política (RAG con Redis), valida las reglas exactas con código y decide **aprobar**, **observar**
o **rechazar**, con la política, categoría y cuenta correctas, los códigos de las reglas y el motivo.
Trata lo que declaró el colaborador como una pista, no como la respuesta. No paga, no aprueba sin
validar y no responde temas ajenos a las rendiciones.

**Comprobación:** un peaje con auto propio declarado en Viajes Internos (P02) debe quedar observado y
reclasificado a P01 / Peajes / CTA-5100, citando RG-09. El criterio general es el golden set de 34
casos: el evaluador los corre con Gemini real, y la corrida final debe pasar todos.

Detalle completo en [docs/caso_y_criterio.md](docs/caso_y_criterio.md).

## Bonos declarados

- Memoria avanzada: fondo por rendir.
- RAG: Redis, índice `grupo05_v15`.
- Acción avanzada: registro SQLite.
- Golden set.
- Juez LLM.
- Guardrail "piso de reglas", con detección de campos alterados por el LLM.

Dónde se ejecuta cada uno, sus casos, su evidencia y su estado:
[docs/evidencias_pauta.md](docs/evidencias_pauta.md).

## Ficha de reproducción

### Modelo

| Elemento | Valor |
|---|---|
| Proveedor | Google Gemini, con `langchain-google-genai` |
| Modelo | `gemini-3.5-flash-lite` (`MODELO_DEL_CURSO` en `src/config.py`) |
| Temperatura | 0. **Este modelo la ignora:** usa sus propios valores de muestreo, así que sus respuestas pueden variar entre corridas |
| Reintentos | 6 intentos para el agente (valor por defecto) y 6 para el juez (`src/seguridad.py`) |
| Máximo de pasos ReAct | 10 (`MAX_PASOS` en `src/contrato.py`) |

### Embeddings e índice

| Elemento | Valor |
|---|---|
| Modelo de embeddings | `models/gemini-embedding-001` (clase-05) |
| Almacén vectorial | Redis del curso |
| Nombre del índice | `grupo05_v15` (viene de `REDIS_PREFIJO`). El sufijo es el nombre acordado, no la versión: guarda la política v1.6 |
| Documentos | 20: uno por política (P01 a P10) y uno por regla general (RG-01 a RG-10) |
| Texto que se busca | La política sin su apartado "Cuándo NO usarla", que sí va en el texto que lee el LLM |
| Campos del índice | `text`, `embedding`, `_index_name`, `_metadata_json` |
| Datos de cada documento | `politica`, `codigo`, `fuente`, `texto_completo`, `contenido_sha256` |
| Dimensiones | 3.072, fijadas en el código (`src/rag.py` y `scripts/cargar_indice.py`) |
| Métrica | COSINE, fijada en el código |
| Algoritmo | FLAT, fijado en el código |
| Llaves | `grupo05_v15:P01` a `grupo05_v15:P10` y `grupo05_v15:RG-01` a `grupo05_v15:RG-10`, con un solo prefijo |

La configuración se comprobó en el índice real después de la carga del 2026-11-03: 20 documentos, con el
contenido idéntico a la política v1.6 local. El índice anterior, `grupo05` (10 documentos, política v1.4),
se conserva sin cambios: para volver a él basta cambiar `REDIS_PREFIJO`.

### Entorno

| Elemento | Valor |
|---|---|
| Python | 3.12.3 |
| Dependencias | versiones fijas en `requirements.txt` (langgraph 1.2.16, langchain 1.4.6, langchain-google-genai 4.4.2, langchain-redis 0.2.6, redis 8.1.0, redisvl 0.28.0) |

### Variables de entorno

Van en un archivo `.env`, que Git ignora. El modelo `.env.example` no trae valores.

| Variable | Para qué sirve |
|---|---|
| `GOOGLE_API_KEY` | Clave de Gemini, para el LLM y los embeddings |
| `GEMINI_MODEL` | Modelo de lenguaje |
| `EMBEDDING_MODEL` | Modelo de embeddings |
| `REDIS_URL` | Conexión a Redis |
| `REDIS_PREFIJO` | Nombre del índice y prefijo de las llaves |
| `MOSTRAR_TRAZAS` | 1 muestra las trazas del agente, 0 las oculta |

Valores para tu `.env` que no son secretos:

```
GEMINI_MODEL=gemini-3.5-flash-lite
EMBEDDING_MODEL=models/gemini-embedding-001
REDIS_PREFIJO=grupo05_v15
MOSTRAR_TRAZAS=1
```

**Cómo obtener las credenciales:**

- **Clave de Gemini:** gratis en [Google AI Studio](https://aistudio.google.com/apikey). El plan
  gratuito tiene límites diarios y por minuto.
- **Redis:** se usa el Redis del curso, con búsqueda vectorial; la coordinación entrega la URL. El
  servidor es compartido: usa solo tu `REDIS_PREFIJO`. Con otro Redis con búsqueda vectorial debería
  funcionar igual, pero no está probado.

### Datos

Todo es ficticio. Los casos se construyeron con patrones agregados; ningún registro real está incluido.

| Archivo | Versión | Contenido |
|---|---|---|
| `datos/politica_ficticia.md` | 1.6 | Política POL-RG-01: 10 políticas y reglas RG-01 a RG-10 |
| `datos/fondos_ficticios.json` | 1.0 | Fondos por rendir FR-001, FR-020 y FR-050 |
| `datos/rendiciones_prueba.csv` | — | 5 gastos de ejemplo |
| `pruebas/golden_set.json` | 1.3 | 34 casos con su respuesta correcta |

## Ejecución paso a paso

Comandos comprobados en Linux con Python 3.12.3, salvo los marcados como **no probado**. Los que usan
Gemini o Redis lo indican. El informe de la prueba desde cero está en
[docs/ensayo_revisor.md](docs/ensayo_revisor.md).

### 1. Crear el entorno

**Linux**
```bash
git clone https://github.com/aleexng1/agentic-ia-grupo-05.git
cd agentic-ia-grupo-05/tarea-final-c1
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

**Windows (PowerShell)**, no probado:
```powershell
git clone https://github.com/aleexng1/agentic-ia-grupo-05.git
cd agentic-ia-grupo-05\tarea-final-c1
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. Configurar `.env`

```bash
cp .env.example .env               # Windows: Copy-Item .env.example .env
```

Completa los valores con la sección [Variables de entorno](#variables-de-entorno).

### 3. Comprobar el proyecto

```bash
python verificar.py                # no necesita clave
python verificar.py --con-llm      # usa Gemini y Redis; no probado en esta revisión
```

Resultado esperado de `python verificar.py`: `Todo en orden`, sin ningún ❌. Sin credenciales da 42 ✅
y un ⚠️, porque omite la búsqueda en Redis; con credenciales reales da 43 ✅.

### 4. Índice de la política en Redis

Pon `REDIS_PREFIJO=grupo05_v15` en tu `.env` y sigue este camino:

1. **Revisa si el índice ya existe**, sin escribir nada: `python verificar.py`. Si la línea
   `buscar_politica devuelve Fragmentos` dice ✅ con 3 fragmentos, el índice existe.
2. **Si existe** (es el caso del Redis del curso, cargado el 2026-11-03): úsalo tal cual. No lo cargues
   de nuevo.
3. **Si no existe** (la línea da ❌ porque no devuelve fragmentos, por ejemplo en otro Redis): revisa el
   plan y luego carga, con el mismo comando que se usó en el Redis del curso:

```bash
python scripts/cargar_indice.py --plan    # sin Redis ni Gemini: muestra los 20 documentos que cargaría
REDIS_PREFIJO=grupo05_v15 python scripts/cargar_indice.py --cargar --confirmar-indice grupo05_v15
```

Qué hace el cargador:

- **`--plan`:** no se conecta a Redis, así que no sabe si el índice existe. Solo revisa que la política
  local sea la v1.6 y que salgan 20 documentos: P01-P10 y RG-01-RG-10.
- **`--cargar`:** solo escribe si `REDIS_PREFIJO` es exactamente `grupo05_v15` y se confirma ese nombre.
  Si el índice no existe, lo crea con 3.072 dimensiones, COSINE y FLAT, y carga las 20 llaves.
- **Si el índice ya existe:** no se niega ni lo borra. Lo deja como está, con su configuración, y
  **reescribe las mismas 20 llaves** (`grupo05_v15:P01` … `grupo05_v15:RG-10`) con el texto local. Gasta
  unas 20 llamadas de embeddings, y por eso, si ya existe, no hace falta cargarlo.
- No borra nada más. Si Redis está lleno, la carga falla y puede quedar a medias: repítela cuando haya
  espacio.
- En Windows, o si prefieres no fijar la variable en la terminal, basta con tener
  `REDIS_PREFIJO=grupo05_v15` en el `.env` y correr el mismo comando sin `REDIS_PREFIJO=…` al inicio.

Si el índice no existe, `verificar.py` y el agente crean uno vacío con ese nombre al buscar. No pasa
nada: la carga lo completa.

### 5. Ejecutar el notebook

Usa Gemini y Redis. **No probado completo:** las secciones 5, 6 y 9 aún están por completar.

- **Con VS Code:** instala las extensiones Python y Jupyter, abre `agente.ipynb`, elige como kernel el
  `.venv` de esta carpeta y ejecuta todas las celdas. `requirements.txt` no instala Jupyter Notebook
  ni JupyterLab.
- **Por consola:** crea una copia con las salidas, que no se sube al repositorio:

```bash
python -m jupyter nbconvert --to notebook --execute agente.ipynb --output agente_ejecutado.ipynb
```

### 6. Correr el evaluador

```bash
python pruebas/evaluar.py --autoprueba           # sin LLM ni clave; esperado: 89 de 89 ✅
python pruebas/evaluar.py --seco                 # sin LLM ni clave; esperado: 34 de 34 casos
python pruebas/probar_herramientas.py            # sin LLM ni clave; esperado: 59 ✅ 0 ❌
python pruebas/evaluar.py --caso GS-07 --pausa 15   # un caso; usa Gemini y Redis
python pruebas/evaluar.py --grupo B --pausa 15   # un grupo (A a F); usa Gemini y Redis
```

Una corrida completa son unas 130 llamadas a Gemini. Conviene correr grupo por grupo con `--pausa 15`,
como se hizo en las corridas 1 y 2. Cada corrida con Gemini guarda un `.md` y un `.json` en
`pruebas/resultados/`. Más opciones en [pruebas/README.md](pruebas/README.md).

## Pruebas y resultados

[pruebas/resultados/](pruebas/resultados/) contiene las trazas de ejecución del evaluador: por cada caso
y turno, la entrada, la respuesta, las herramientas que pidió el agente, los fragmentos del RAG, los
errores de herramientas y el veredicto final, en el `.json`, con un resumen en el `.md`. No incluye las
trazas internas del grafo (`registrar_traza`), que el evaluador apaga.

Resultados guardados:

- [`corrida_2.md`](pruebas/resultados/corrida_2.md): **33 de 34 casos**, el 2026-11-03, con `main` en
  `5bbfd5d`, la política v1.6 y el índice `grupo05_v15`, sin fallas técnicas. Falla GS-29.
- [`prueba_dirigida_indice_v16.md`](pruebas/resultados/prueba_dirigida_indice_v16.md): GS-01 3 de 3,
  9 de 10 ejecuciones y un jailbreak por chat que no declara ninguna decisión.
- [`corrida_1_linea_base.md`](pruebas/resultados/corrida_1_linea_base.md): línea base, 31 de 33 casos.
- [`evolucion.md`](pruebas/resultados/evolucion.md): antes y después de cada mejora.
- [`estabilidad_v1_4.md`](pruebas/resultados/estabilidad_v1_4.md): tres repeticiones de los casos
  inestables.
- [`prueba_dirigida_PR17.md`](pruebas/resultados/prueba_dirigida_PR17.md): evidencia del juez con la
  validación.

La corrida final será una corrida 3 completa, después del arreglo de GS-29 (ver "Orden de cierre" en
[docs/evidencias_pauta.md](docs/evidencias_pauta.md)).
Cómo se evalúa cada campo del golden set: [pruebas/README.md](pruebas/README.md).

## Seguridad y límites conocidos

### Cómo se protege

- La clave y la URL de Redis solo van en `.env`, que Git ignora. Los resultados nunca las guardan.
- Glosas, documentos y fragmentos son datos, nunca instrucciones.
- El grafo valida siempre el gasto original: si el LLM altera su copia, se ignora y se anota qué cambió.
- Las reglas exactas las decide el código. El LLM no puede ser más permisivo que ellas.
- Si un turno con gasto no tiene un veredicto válido, la respuesta se reemplaza por una segura.
- El LLM no tiene herramientas para registrar ni borrar: el registro lo hace el grafo al cerrar.
- El agente se detiene al llegar a `MAX_PASOS`.

### Límites conocidos

- **GS-29:** el LLM a veces reclasifica a P08 una compra de mercadería de la cafetería y con eso esquiva
  la regla de solo factura de P07, y el juez no lo frena. Falló en las corridas 1 y 2. Arreglo pendiente
  en el prompt y el juez (Eduardo).
- **Turnos sin gasto:** el prompt prohíbe declarar una decisión sin gasto, y el grafo reemplaza un
  "Decisión: APROBAR". El jailbreak por chat de la prueba dirigida no declaró ninguna decisión.
- **Búsqueda de un camión de la empresa:** "peaje en camión de reparto" trae P04 primero. El LLM llega a
  P02 leyendo el "Cuándo NO usarla" de P04: GS-01 pasó 3 de 3 y en la corrida 2.
- **Variación:** Gemini no responde siempre igual; por eso hay pruebas de estabilidad.
- **Memoria:** el historial y el fondo viven en memoria durante la sesión; el registro es un SQLite
  local.
- **Fuera de alcance:** el agente no evalúa efectos tributarios, presupuestos ni centros de costo.

Simplificaciones del golden set:

- **GS-26:** no exige `buscar_politica`. El caso prueba la memoria del fondo, y no buscar cuando el
  agente ya conoce la política del gasto es lo que pide la pauta.
- **GS-34:** depende de la aclaración de la política v1.5, que el índice `grupo05_v15` ya tiene. Pasó en la
  corrida 2.
- **GS-24:** la multa se respalda con boleta porque el contrato solo admite boleta, factura o voucher;
  en la realidad sería un comprobante de pago.
- **RG-04** (segregación de funciones) no se prueba, porque el agente no recibe quién aprueba cada
  informe.

## Equipo y roles

| Rol | Persona | Rama |
|---|---|---|
| Caso y calidad | Alex Nail | `tf/caso-calidad` |
| Núcleo (ReAct) | Matías Muñoz | `tf/nucleo` |
| Herramientas y estado | Sebastián Mardones | `tf/herramientas` |
| Conocimiento y seguridad | Eduardo Basaure | `tf/conocimiento-seguridad` |

- Dueños de archivos y reglas de trabajo: [AGENTS.md](AGENTS.md).
- Guía de cada rol: [docs/instrucciones/](docs/instrucciones/).
- Prompts de desarrollo, un archivo por persona:
  [docs/prompts_desarrollo/](docs/prompts_desarrollo/).

```
tarea-final-c1/
├── agente.ipynb          notebook de entrega (solo importa desde src/)
├── verificar.py          juez del contrato: python verificar.py
├── src/                  código del agente (contrato, grafo, herramientas, RAG, memoria, ...)
├── scripts/              carga de la política en Redis
├── datos/                política ficticia, fondos y gastos de prueba
├── pruebas/              golden set, evaluador y resultados
└── docs/                 caso, evidencias, guías por rol y prompts
```
