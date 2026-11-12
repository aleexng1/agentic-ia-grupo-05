# Reglas del proyecto

- Todo en español: nombres, comentarios, mensajes.
- Las funciones que usan internet son async.
- Toda llamada por red tiene un timeout explícito.
- Si algo no responde, el error se muestra en una sola línea entendible, sin stack trace.
- Cada agente expone una función responder(texto, context_id) que devuelve un texto. Es el contrato que todos cumplen.
- Cada agente se puede correr desde la terminal sin servidor: `python main.py {agente} "pregunta"`. Con `--saltos` muestra por qué nodos y herramientas pasó; con `--diagrama` imprime su estructura en Mermaid sin ejecutarlo.

## App única

- Todo se sirve desde una sola aplicación FastAPI (`app.py`): el coordinador en la raíz y cada agente en `/agentes/{nombre}`. Se levanta desde `taller-02-c2/proyecto` con `uvicorn app:app --reload --port 8000`.
- Las fichas se publican con `URL_BASE + "/agentes/{nombre}"`; `URL_BASE` viene del `.env`. No se escriben direcciones ni puertos fijos en el código: se usa `src/comun/config.py`.
- El coordinador descubre las fichas en la primera pregunta, no al arrancar la app.
- Las pruebas (`pytest`) no usan la clave de Gemini y deben pasar antes de subir cambios.

## Zona de cada persona

- Alex: base e integración (`app.py`, `src/comun/config.py`, `src/comun/servidor.py`, `src/coordinador/`, archivos de Heroku en la raíz del repo).
- Matías: validación de acceso (`CLAVE_API`) y manejo de errores en el servidor.
- Eduardo: `src/comun/panel.py` y `src/comun/panel.html`.
- Sebastián: sección «Operación en Heroku» del README.
- Cada uno mantiene además su propio agente (`src/agente_{nombre}/`).
- Nadie toca la zona de otro sin avisar.
