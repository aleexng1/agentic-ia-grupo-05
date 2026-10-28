# AGENTS.md — Tarea Final Curso 1 (Grupo 05)

Reglas para el asistente de código (OpenCode o Claude Code). Léelas completas antes de actuar.

## 1. Qué es el proyecto

Agente revisor de rendiciones de gastos de **Comercial Los Alerces SpA**, empresa FICTICIA.
Recibe un gasto rendido (monto, fechas, documento, glosa, política elegida por el trabajador...).
Paso 1, clasificar: busca en la política (RAG con Redis) la política, categoría y cuenta correctas.
Paso 2, validar: llama a `validar_gasto` (reglas exactas) y decide APROBAR, OBSERVAR o RECHAZAR,
explicando la regla aplicada. Hecho con LangGraph (ciclo ReAct) y Gemini. Todo dato es inventado.

## 2. Roles, ramas y dueños de archivos

### Asignación de roles

| Rol | Persona | Rama |
|---|---|---|
| Caso y calidad | alex | `tf/caso-calidad` |
| Núcleo (ReAct) | por definir | `tf/nucleo` |
| Herramientas y estado | por definir | `tf/herramientas` |
| Conocimiento y seguridad | por definir | `tf/conocimiento-seguridad` |

Para saber tu rol, mira la rama actual (`git branch --show-current`) y búscala en esta tabla.
Guía de cada rol: `docs/instrucciones/<rol>.md`.

### Dueño de cada archivo (rutas dentro de `tarea-final-c1/`)

| Dueño | Archivos |
|---|---|
| Caso y calidad | `datos/`, `pruebas/`, `README.md`, `docs/` |
| Núcleo | `src/grafo.py`, `src/config.py`, `agente.ipynb` |
| Herramientas y estado | `src/herramientas.py`, `src/memoria.py`, `src/registro.py` |
| Conocimiento y seguridad | `src/rag.py`, `src/seguridad.py`, `scripts/cargar_indice.py` |
| COMPARTIDOS (solo con acuerdo del grupo) | `src/contrato.py`, `src/__init__.py`, `AGENTS.md`, `CLAUDE.md`, `requirements.txt`, `.env.example`, `verificar.py` |

Fuera de `tarea-final-c1/`: los talleres anteriores (`taller-01/`, `taller-02/`, ...) no se tocan.
`.gitattributes`, `.gitignore`, `.opencode/` y `.claude/` de la raíz también son COMPARTIDOS.

## 3. Reglas para el asistente de código

- Solo modifica archivos cuyo dueño sea el rol de la rama actual. Si necesitas un cambio en
  otro archivo, NO lo hagas: escribe la propuesta (qué cambiar y por qué) y avisa a la persona.
- No cambies firmas de funciones ni tipos de `src/contrato.py`. Las firmas acordadas son las que
  revisa `verificar.py` (bloque 3).
- No cambies el modelo ni la temperatura en `src/config.py`.
- Nunca escribas claves, contraseñas ni datos reales; todo dato es ficticio. Nunca subas `.env`.
- Nunca trabajes, hagas commit ni push en `main`. Siempre en la rama propia.
- Antes de subir cambios, `python verificar.py` debe pasar (sin ❌).
- Código, nombres y comentarios en español; funciones cortas y comentadas en simple.
- Los stubs están marcados con `# TODO(<rol>): reemplazar stub`. Reemplaza solo los de tu rol,
  manteniendo la firma y el formato de lo que devuelve.
- Abre los archivos con `encoding="utf-8"` (en Windows es obligatorio para tildes y ñ).
- Explica cada paso al usuario en una frase simple: no todos programan.
- Antes de un paso que no se puede deshacer (borrar, forzar, reescribir historial), pregunta.

## 4. Cómo se prueba

```
python verificar.py            # sin clave de API: contrato, firmas, formatos y ciclo ReAct con LLM falso
python verificar.py --con-llm  # además conversa con Gemini (necesita .env completo)
```

`buscar_politica` y `juzgar` necesitan Redis o la clave; sin ellos, `verificar.py` los marca ⚠️
(omitidos) y se revisan con `--con-llm`. Un error de formato siempre es ❌.

## 5. Glosario mínimo

- **Rama**: copia paralela del proyecto donde trabajas sin afectar a los demás.
- **Commit**: foto guardada de tus cambios, con un mensaje que dice qué hiciste.
- **Push**: subir tus commits a GitHub.
- **Pull request (PR)**: solicitud para unir tu rama a `main`; Alex la revisa y la une.
- **Stub**: versión de prueba de una función que devuelve un resultado fijo, para que los demás
  puedan avanzar antes de que esté lista la versión real.
- **Contrato**: los tipos de datos y firmas acordados (`src/contrato.py`). Si todos lo respetan,
  las piezas encajan.
- **verificar.py**: el juez del contrato; revisa que todo encaje y muestra ✅ / ❌.

## 6. Cómo subir cambios

Usa el comando `/subir-cambios` (OpenCode o Claude Code). Revisa la rama, los archivos, trae lo
último de `main`, corre `verificar.py`, hace commit y push, y muestra el enlace del pull request.
