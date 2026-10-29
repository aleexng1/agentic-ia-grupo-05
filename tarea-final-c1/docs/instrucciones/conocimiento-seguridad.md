# Guía del rol: Conocimiento y seguridad

Responsable: Eduardo Basaure

> Rama de trabajo: **`tf/conocimiento-seguridad`** · Reglas generales: [AGENTS.md](../../AGENTS.md)

## Tu rol en una frase

Haces que el agente sepa buscar en la política (RAG con Redis) solo cuando lo necesita, que no se salga de su tarea ni se deje engañar, y que un juez revise sus veredictos.

**Criterios de la pauta que aseguras:**

| Criterio | Puntaje |
|---|---|
| RAG con el Redis del curso, un fragmento por política, y mostrar que NO busca cuando no hace falta | +1,0 |
| Prompt de alcance + pruebas de fuera de alcance y jailbreak (incluido uno en la glosa) | 0,5 |
| Juez LLM con modelo, prompt y veredictos visibles | +0,5 |

## Tus archivos

Puedes modificar (rutas dentro de `tarea-final-c1/`):

- `src/rag.py` (`buscar_politica`)
- `src/seguridad.py` (`PROMPT_SISTEMA`, `juzgar`)
- `scripts/cargar_indice.py` (carga la política en Redis)

**No toques** los archivos de otros roles. Si necesitas un cambio en ellos, escribe la propuesta
y avísale a la persona dueña. Los archivos **compartidos** (`src/contrato.py`, `AGENTS.md`,
`requirements.txt`, `.env.example`, `verificar.py`) solo se cambian con acuerdo del grupo.

## Qué entregas y cómo sabes que terminaste

- [ ] **Confirmar con la coordinación del curso qué instancia de Redis vale** (local, Docker o la
      del curso) y anotarla en el README (avísale a Alex). En clase-05 se usó Redis 8 / redis-stack
      con `langchain-redis`; el `redis-server` que instala `apt` no sirve (no trae búsqueda vectorial).
- [ ] `scripts/cargar_indice.py` carga **un fragmento por política** en Redis (ya separa el texto
      por títulos `## `), usando `REDIS_URL`, `REDIS_PREFIJO` y `EMBEDDING_MODEL` del `.env`.
- [ ] `buscar_politica(consulta, k)` devuelve `Fragmento`s reales (politica, texto, fuente, puntaje).
- [ ] Demostrar en el notebook (sección 6) un caso donde el agente **NO** busca (ej. una pregunta
      que ya se respondió en el historial, o una fuera de alcance), viéndolo en las trazas.
- [ ] `PROMPT_SISTEMA` con alcance y acciones permitidas, y pruebas (sección 5) de:
  - [ ] pregunta fuera de alcance;
  - [ ] jailbreak directo ("ignora tus reglas...");
  - [ ] jailbreak **escondido en la glosa** del gasto (ej. G-005 de `datos/rendiciones_prueba.csv`).
- [ ] `juzgar(gasto, clasificacion, veredicto)` con un LLM juez; el notebook (sección 9) muestra
      el modelo, el prompt del juez y sus veredictos. Devuelve `{"valido": bool, "razon": str}`.
- [ ] `python verificar.py` pasa y `python verificar.py --con-llm` también (ahí se prueban de
      verdad la búsqueda y el juez).

## De quién dependes y quién depende de ti

- **Dependes de:** Caso y calidad (la política final para indexar) y de la coordinación (la
  instancia de Redis). Mientras tanto indexa la política v1.1 (datos/politica_ficticia.md), excluyendo la sección Historial de cambios: el formato no cambia.
- **Dependen de ti:** Núcleo (usa `buscar_politica` y `PROMPT_SISTEMA` en el grafo) y Caso y
  calidad (casos adversariales del golden set y juez).

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
git switch tf/conocimiento-seguridad
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
git switch tf/conocimiento-seguridad
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
Lee AGENTS.md y docs/instrucciones/conocimiento-seguridad.md. Soy del rol Conocimiento y
seguridad, en la rama tf/conocimiento-seguridad. Quiero completar scripts/cargar_indice.py y
buscar_politica en src/rag.py para usar Redis con langchain-redis, como en el curso (un
fragmento por política, variables REDIS_URL, REDIS_PREFIJO y EMBEDDING_MODEL del .env).
Primero explícame en simple el plan y cómo pruebo que Redis funciona, y espera mi visto
bueno. No cambies firmas ni src/contrato.py. Solo toca mis archivos. Al final corre
python verificar.py y explícame el resultado.
```
