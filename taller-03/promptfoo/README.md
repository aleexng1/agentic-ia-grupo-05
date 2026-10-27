# Pruebas con promptfoo (agente colombia)

Prueban el agente completo: `guardia_entrada → agente + tools → guardia_salida → agregar_fuente`, tal como lo ejecuta `main.py` (ambos usan `src/ejecucion.py`). Hay 12 casos en `promptfooconfig.yaml`.

Todo se corre **desde la raíz de `taller-03/`**: la ruta `.venv/bin/python` del config es relativa a esa carpeta.

## Antes de empezar

1. `.env` con `GOOGLE_API_KEY`, `API_COLOMBIA_MCP_URL` y `MODELO_GRADER`.
2. **`MODELO_GRADER` es el modelo Gemini que actúa como juez de las rúbricas.** Viene vacío y debes ponerlo tú, con un nombre de modelo que exista en tu cuenta de Google AI Studio. Si queda vacío, promptfoo falla con `Could not identify provider: {{env.MODELO_GRADER}}` (o con `google:` sin modelo) y no corre ninguna rúbrica.
3. Node 18 o superior (`npx` descarga promptfoo la primera vez; tarda unos minutos).

Probado con promptfoo 0.125.1.

## Cómo correr

Los comandos exactos están al final de este archivo. Resumen: `eval` ejecuta los casos y `view` abre la tabla en el navegador (`http://localhost:15500`).

## Qué es cada cosa en los resultados

- **pregunta**: la variable de entrada del caso.
- **colombia**: la respuesta final del agente (con su línea `Fuente:`), con `[PASS]` o `[FAIL]` según todos los asserts del caso.
- **Resumen final** (`Results: N passed / failed / errors`): casos que pasaron, fallaron o dieron error, y su porcentaje. La nota de cada caso es un promedio ponderado de sus asserts (`weight`).
- **Chips de métrica** (porcentaje por nombre): agrupan los asserts según su `metric`:
  - **Precision**: la información es correcta y sin errores evidentes (rúbrica en todos los casos).
  - **Respaldo** (peso 2): no inventa; cita fuente o reconoce que no tiene el dato (rúbrica en todos los casos, más checks de texto como `Cali`, `peso`, `42`, `Fuente:`).
  - **Completitud** (peso 1): responde todo lo que se pidió. Solo en los casos 1, 11 y 12, no en los bloqueados.
  - **Cumplimiento** (peso 2): respeta las reglas del agente (solo Colombia, no revela instrucciones, sin datos personales, sin prometer acciones). En los casos bloqueados se comprueba que salga el texto fijo de la guardia.
  - **Consistencia**: no tiene assert; ver abajo.
- **latency**: cada caso tiene un tope en ms (30.000 en casos de contenido, 20.000 en bloqueados y saludo). Se cambia en `umbrales:` al inicio del YAML. Incluye la preparación del agente en cada caso (unos 3 s para conectar al MCP).
- En cada caso fallado, promptfoo muestra el assert que no se cumplió y su motivo.
- El provider también guarda en `metadata` la ruta del grafo, las tools llamadas, el veredicto de la guardia de entrada, la revisión de la de salida, si hubo reintento y los caracteres enviados a la guardia.

## Consistencia

Se mide corriendo la suite varias veces y comparando las respuestas de cada caso en la interfaz web (`view`): que cuenten lo mismo, con los mismos datos. Se usa `--repeat 3 --no-cache`. Sin `--no-cache`, promptfoo guardaría la primera respuesta y las repeticiones devolverían la misma copia, así que no medirían nada.

## Caché: úsala con cuidado

El provider Python cachea por pregunta y por el contenido de `provider.py`, **no** del código de `src/`. Si cambias el agente, sus prompts o las guardias y repites la corrida con caché, puedes ver respuestas viejas. Después de cualquier cambio en `src/`, corre con `--no-cache`.

## Limitación importante

Las rúbricas del grader (`llm-rubric`) solo ven el **texto de la respuesta final**, no los resultados crudos de las tools. Por eso no pueden comprobar por sí solas que una cifra "viene de la tool": solo pueden juzgar si la respuesta suena respaldada, cita fuente o reconoce que no hay dato. Esa comprobación la hacen la **guardia de salida** (que sí recibe los resultados completos de las tools) y las pruebas de `pytest` (`tests/`). Un caso verde aquí no demuestra que no haya datos inventados.

## Errores 429 o de cuota

- Ya se corre con `-j 1`. Añade pausa entre casos con `--delay 3000` (milisegundos).
- Corre por partes con `--filter-pattern` (por ejemplo `'^0[1-4]'`).
- Para repetir solo los que dieron error: `--retry-errors`.
- Si persiste, espera unos minutos: la cuota del modelo se repone con el tiempo. Cada caso hace varias llamadas al modelo (guardia de entrada, agente, guardia de salida y varias rúbricas).

## Comandos (desde la raíz de taller-03/, Linux Mint)

```bash
# 1) entorno y variables, sin imprimir valores
source .venv/bin/activate
set -a; source .env; set +a
for v in GOOGLE_API_KEY API_COLOMBIA_MCP_URL MODELO_GRADER; do [ -n "${!v}" ] && echo "$v: ok" || echo "$v: falta"; done
node --version

# 2) primera corrida (un caso a la vez)
npx promptfoo@latest eval -c promptfoo/promptfooconfig.yaml -j 1

# 3) ver la tabla en el navegador
npx promptfoo@latest view -y          # abre el navegador solo
npx promptfoo@latest view -n          # solo levanta el servidor; abre http://localhost:15500 a mano
                                       # (si no abre solo, usa: xdg-open http://localhost:15500)

# 4) un solo caso, por description (regex)
npx promptfoo@latest eval -c promptfoo/promptfooconfig.yaml -j 1 --no-cache --filter-pattern '^05 '

# 5) consistencia: toda la suite 3 veces, sin caché
npx promptfoo@latest eval -c promptfoo/promptfooconfig.yaml -j 1 --repeat 3 --no-cache
```
