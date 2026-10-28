# Guía del rol: Núcleo (ReAct)

> Rama de trabajo: **`tf/nucleo`** · Reglas generales: [AGENTS.md](../../AGENTS.md)

## Tu rol en una frase

Construyes el "cerebro" del agente: el ciclo en que el LLM piensa, pide una herramienta, lee el resultado y decide, recordando la conversación; y armas el notebook final.

**Criterios de la pauta que aseguras:**

| Criterio | Puntaje |
|---|---|
| Ciclo ReAct (herramienta, observación, decisión) | 1,0 |
| Historial (segundo turno usa lo anterior) | 0,5 |
| LLM real y trazas legibles | 0,5 |
| Condición de parada explícita | (incluido en ReAct) |
| Notebook final ejecutable de arriba abajo | (base de la entrega) |

## Tus archivos

Puedes modificar (rutas dentro de `tarea-final-c1/`):

- `src/grafo.py` (ciclo ReAct + historial)
- `src/config.py` (LLM y trazas; **no** cambies modelo ni temperatura)
- `agente.ipynb`

**No toques** los archivos de otros roles. Si necesitas un cambio en ellos, escribe la propuesta
y avísale a la persona dueña. Los archivos **compartidos** (`src/contrato.py`, `AGENTS.md`,
`requirements.txt`, `.env.example`, `verificar.py`) solo se cambian con acuerdo del grupo.

## Qué entregas y cómo sabes que terminaste

- [ ] `construir_agente()` arma el ciclo LLM → herramientas → LLM con las herramientas reales
      (`buscar_politica`, `validar_gasto`) y memoria por hilo. Ya hay una versión mínima que funciona.
- [ ] El estado del grafo guarda `gasto`, `clasificacion`, `validacion` y `veredicto` (tipos de
      `src/contrato.py`), para que el notebook los pueda mostrar.
- [ ] **Condición de parada explícita**: para cuando el LLM responde sin pedir herramientas o al
      llegar a `MAX_PASOS` (6). Se ve en las trazas.
- [ ] **Trazas legibles** con `registrar_traza`: cada paso muestra qué pensó/pidió el LLM y qué
      observó.
- [ ] **Segundo turno**: una pregunta en el mismo hilo que solo se puede responder con el historial.
- [ ] Integrar en `agente.ipynb` el trabajo de los otros roles (secciones 3 a 11), importando
      desde `src/` sin lógica larga en el notebook.
- [ ] El notebook corre de arriba abajo sin errores (Kernel → Restart & Run All).
- [ ] `python verificar.py` y `python verificar.py --con-llm` pasan.

Si cambias cómo usas el LLM (por ejemplo `with_structured_output`), el "LLM falso" de
`verificar.py` puede dejar de servir: proponlo al grupo, no lo cambies solo (es compartido).

## De quién dependes y quién depende de ti

- **Dependes de:** Herramientas y estado (`validar_gasto`, memoria, registro), Conocimiento y
  seguridad (`buscar_politica`, `PROMPT_SISTEMA`, `juzgar`) y Caso y calidad (casos de prueba).
  Mientras no estén, usa los stubs: ya devuelven datos válidos.
- **Dependen de ti:** todos, porque el notebook final muestra el trabajo de cada rol.

## Puesta en marcha paso a paso

Haz esto una sola vez. Copia y pega cada línea en la terminal y espera a que termine.
Necesitas tener instalados **Git** y **Python 3.12**.

### Windows (PowerShell)

```powershell
# 1. Descargar el repositorio y entrar a él (solo la primera vez)
git clone https://github.com/aleexng1/agentic-ia-grupo-05.git
cd agentic-ia-grupo-05
#    Si YA lo tenías clonado: no lo clones de nuevo. Entra a su carpeta con cd y corre:
#    git fetch origin

# 2. Cambiarte a tu rama de trabajo y entrar a la carpeta del proyecto
#    (la carpeta tarea-final-c1 aparece al estar en tu rama)
git switch tf/nucleo
cd tarea-final-c1

# 3. Crear el entorno virtual con Python 3.12 y activarlo
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
#    Si sale un error de "ejecución de scripts deshabilitada", corre esto una vez y repite:
#    Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

# 4. Instalar las librerías (versiones fijas)
python -m pip install -r requirements.txt

# 5. Crear tu archivo de configuración y completarlo (clave y valores del README)
Copy-Item .env.example .env
notepad .env

# 6. Comprobar que todo funciona: debe terminar con "Todo en orden"
python verificar.py
```

### Linux

```bash
# 1. Descargar el repositorio y entrar a él (solo la primera vez)
git clone https://github.com/aleexng1/agentic-ia-grupo-05.git
cd agentic-ia-grupo-05
#    Si YA lo tenías clonado: no lo clones de nuevo. Entra a su carpeta con cd y corre:
#    git fetch origin

# 2. Cambiarte a tu rama de trabajo y entrar a la carpeta del proyecto
#    (la carpeta tarea-final-c1 aparece al estar en tu rama)
git switch tf/nucleo
cd tarea-final-c1

# 3. Crear el entorno virtual con Python 3.12 y activarlo
python3.12 -m venv .venv
source .venv/bin/activate

# 4. Instalar las librerías (versiones fijas)
python -m pip install -r requirements.txt

# 5. Crear tu archivo de configuración y completarlo (clave y valores del README)
cp .env.example .env
nano .env

# 6. Comprobar que todo funciona: debe terminar con "Todo en orden"
python verificar.py
```

**Cada vez que vuelvas a trabajar:** abre la terminal en `tarea-final-c1`, activa el entorno
(paso 3, solo la línea de activar), revisa que estás en tu rama con `git branch --show-current`
y abre OpenCode (o Claude Code) **dentro de la carpeta `tarea-final-c1`**.

**Para guardar y subir tu avance:** escribe `/subir-cambios` en OpenCode. Hace todo en orden y al
final te da el enlace del pull request.

## Tu primer prompt para OpenCode

Abre OpenCode dentro de `tarea-final-c1`, en tu rama, y pega esto:

```text
Lee AGENTS.md y docs/instrucciones/nucleo.md. Soy del rol Núcleo, en la rama tf/nucleo.
Explícame en simple cómo funciona hoy src/grafo.py (ciclo ReAct, historial y parada).
Luego propón un plan corto para: guardar gasto, clasificacion, validacion y veredicto en el
estado, y mejorar las trazas para que se lean bien en el notebook. Espera mi visto bueno
antes de cambiar código. Solo toca src/grafo.py, src/config.py y agente.ipynb, y no cambies
el modelo ni la temperatura. Al final corre python verificar.py y explícame el resultado.
```
