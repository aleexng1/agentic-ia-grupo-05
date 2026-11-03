# Reglas del proyecto

Estas reglas valen para todo lo que se genere en este proyecto.

1. **Todo en español:** nombres, comentarios y mensajes.
2. **Las funciones que usan internet son `async`.**
3. **Toda llamada por red tiene un timeout explícito.**
4. **Si algo no responde, el error se muestra en una sola línea entendible**, sin stack trace.
5. **Cada agente expone una función `responder(texto, context_id)` que devuelve un texto.** Es el contrato que todos cumplen.
6. **Cada agente se puede correr desde la terminal sin servidor**, igual que en el Curso 1:
   `python main.py {agente} "pregunta"`.
   - Con `--saltos` muestra por qué nodos y herramientas pasó.
   - Con `--diagrama` imprime su estructura en Mermaid sin ejecutarlo.

## Estructura de cada agente

Cada agente vive en su carpeta con la misma forma: `tools.py`, `prompts.py`,
`graph.py` o `crew.py`, y `server.py`.

## Diferencias con el curso (a2a-sdk 1.3.0)

Reglas para todo el código de clientes y coordinador:

- El método para enviar un mensaje es `SendMessage` (no `message/send`).
- Toda petición lleva la cabecera `A2A-Version: 1.0`. Sin ella el servidor
  responde error -32009 con HTTP 200 dentro del JSON: revisar siempre el
  cuerpo, no solo el código HTTP.
- Los roles son `ROLE_USER` y `ROLE_AGENT`.
- El texto de la respuesta viene en `result.message.parts[0].text`. No hay
  `Task`, `artifacts` ni estado "completed" mientras el executor responda con
  un solo `Message`.
- La dirección del agente en la ficha está en `supportedInterfaces[0].url`
  (campos en camelCase).
- La ficha sigue en `/.well-known/agent-card.json`.
- Si el `context_id` no viene, el servidor genera uno y lo devuelve.
