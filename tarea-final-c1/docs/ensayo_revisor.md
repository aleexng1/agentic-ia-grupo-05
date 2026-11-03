# Ensayo de revisor

Prueba de seguir solo el README desde cero, como lo haría un revisor. No usó Gemini ni Redis reales.

- **Fecha:** 2026-11-02
- **Commit ensayado:** `10157cb`, de la rama `tf/caso-calidad`. Las correcciones se volvieron a probar en `73d9973`.
- **Entorno:** Linux, Python 3.12.3, git 2.43.0, carpeta temporal nueva y variables de entorno limpias.
- **`.env`:** valores de prueba, sin claves reales, con Redis apuntando a una dirección local.

**Resultado:** el proyecto se instala y sus pruebas sin LLM pasan desde cero. El README tenía dos vacíos
que ya se corrigieron. Quedan tres avisos para el grupo.

## Pasos

| Paso del README | Comando | Resultado |
|---|---|---|
| 1. Entorno | `git clone` de la rama | ✅ Con `--branch tf/caso-calidad`, porque el README nuevo aún no estaba en `main` |
| 1. Entorno | `python3.12 -m venv .venv` y activar | ✅ |
| 1. Entorno | `python -m pip install -r requirements.txt` | ✅ 44 s, sin errores |
| 2. Configurar | `cp .env.example .env` y completar | ✅ |
| 3. Comprobar | `python verificar.py` | ✅ 42 ✅ 0 ❌ y un ⚠️ por Redis, también con el `.env` sin completar |
| 5. Notebook | Abrirlo sin VS Code | ⚠️ Jupyter Notebook y JupyterLab no vienen instalados. Ya corregido |
| 5. Notebook | `python -m jupyter nbconvert ...` | ✅ Probado solo con un notebook de una celda, sin el agente |
| 6. Evaluador | `python pruebas/evaluar.py --autoprueba` | ✅ 83 de 83 |
| 6. Evaluador | `python pruebas/evaluar.py --seco` | ✅ 34 de 34 casos |
| 6. Evaluador | `python pruebas/probar_herramientas.py` | ✅ 56 ✅ 0 ❌ |
| 6. Evaluador | `--caso` sin clave | ✅ Avisa con claridad que falta `GOOGLE_API_KEY` |
| Final | `git status` | ✅ Limpio: no quedan archivos sin ignorar |

Todos los enlaces internos del README y de `docs/` funcionan.

## Problemas encontrados

| Problema | A quién le toca | Estado |
|---|---|---|
| El README decía "abre `agente.ipynb`" y daba por hecho un editor con Jupyter | Alex | ✅ Corregido: indica VS Code o la ejecución por consola |
| El README no decía qué resultado esperar en cada comando | Alex | ✅ Corregido |
| `requirements.txt` fija las 11 dependencias directas, pero no las indirectas. 15 salieron con otra versión que la del entorno de desarrollo, entre ellas `google-genai`, `pydantic` y `python-dateutil`. Las pruebas pasan, pero un revisor no instala exactamente lo que se usó en las corridas | Todos (archivo compartido) | Aviso |
| `.env.example` dice "confirmar con la coordinación qué instancia usar", y el README dice que se usa el Redis del curso | Todos (archivo compartido) | Aviso |
| Git no ignora `agente_ejecutado.ipynb`, la copia con salidas que crea la ejecución por consola | Todos (`.gitignore` es compartido) | Aviso; el README advierte que no se sube |
| Las secciones 5, 6 y 9 del notebook están vacías | Matías y Eduardo | Ya está en la matriz |

## Qué no se probó

- Cualquier paso con Gemini o Redis reales: `python verificar.py --con-llm`, `python -m scripts.cargar_indice`
  y las corridas del evaluador con LLM. Esos comandos se usaron con credenciales reales durante el proyecto.
- La ejecución completa del notebook.
- Las instrucciones de Windows.
- Si un revisor externo puede conseguir la URL del Redis del curso. El README lo da por hecho.
