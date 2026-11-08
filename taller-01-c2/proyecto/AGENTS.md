# Reglas del proyecto

- Todo en español: nombres, comentarios, mensajes.
- Las funciones que usan internet son async.
- Toda llamada por red tiene un timeout explícito.
- Si algo no responde, el error se muestra en una sola línea entendible, sin stack trace.
- Cada agente expone una función responder(texto, context_id) que devuelve un texto. Es el contrato que todos cumplen.
- Cada agente se puede correr desde la terminal sin servidor, igual que en el Curso 1: `python main.py {agente} "pregunta"`. Con `--saltos` muestra por qué nodos y herramientas pasó; con `--diagrama` imprime su estructura en Mermaid sin ejecutarlo.
