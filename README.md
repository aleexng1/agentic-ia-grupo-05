# Agentic AI – Talleres Grupo 05

## Qué es este repo
Aquí trabajamos los talleres del Curso 1 del Certificado en Agentic AI (UAI + Xerax), Grupo 05. Usamos Python, LangGraph y modelos Gemini. Los talleres son notebooks (.ipynb).

## Primera configuración
1. Clona el repo:
   ```bash
   git clone https://github.com/aleexng1/agentic-ia-grupo-05.git
   cd agentic-ia-grupo-05
   ```
2. Crea y activa un entorno virtual:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Instala las librerías:
   ```bash
   pip install -r requirements.txt
   ```
4. Copia `.env.example` a `.env` y pon tu propia clave de Gemini:
   ```bash
   cp .env.example .env
   ```
5. Ejecuta `nbstripout --install`. Esto limpia los resultados de los notebooks antes de cada commit, para que las comparaciones de código sean legibles.

## Cómo trabajamos
- La rama `main` es la versión oficial. Nadie escribe directo en ella.
- Cada persona trabaja en su propia rama con formato `nombre/taller-NN` (ejemplo: `alex/taller-01`).
- Para comparar soluciones, se abre un pull request hacia la rama de integración `taller-NN-final`.
- El resultado final entra a `main` por pull request.

## Comandos básicos
| Qué quiero hacer | Comando |
|---|---|
| Crear mi rama | `git checkout -b alex/taller-01` |
| Ver qué cambié | `git status` |
| Guardar cambios (commit) | `git add .` y luego `git commit -m "Mensaje claro"` |
| Subir mi rama | `git push -u origin alex/taller-01` |
| Traer cambios de otros | `git pull` |

## Reglas
- Nunca subir claves ni el archivo `.env`.
- Un taller por carpeta.
- No editar los `taller-NN` de otros sin avisar.

## Entrega
Por confirmar con la coordinación del curso: dónde y cómo se entregan los talleres.
