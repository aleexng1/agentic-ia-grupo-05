# Pruebas remotas en Heroku (Sebastián)

**Entorno:** HEROKU
**Fecha:** 14/11/2026
**URL:** https://grupo05-taller2-seba-94d12914f3eb.herokuapp.com/
**App:** grupo05-taller2-seba (stack heroku-24, release v8, dyno web Eco)
**Versión desplegada:** `origin/main` (commit 741305b)

Las claves no aparecen en este archivo. La `CLAVE_API` y la `GOOGLE_API_KEY` viven solo en las Config Vars de Heroku.

## Resultados

| # | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
|---|---|---|---|---|
| 1 | `GET /salud` | 200 | 200 | Público |
| 2 | `GET /.well-known/agent-card.json` | 200 | 200 | Ficha del coordinador |
| 3 | `GET /agentes/matias/.well-known/agent-card.json` | 200 | 200 | Ficha de agente |
| 4 | `POST /panel/consultar` sin cabecera `X-API-Key` | 401 | 401, "Falta la clave de acceso. Envíala en la cabecera X-API-Key." | Rechazo sin clave |
| 5 | `POST /panel/consultar` con clave incorrecta | 401 | 401, "La clave de acceso es incorrecta." | Rechazo con clave falsa |
| 6 | Con clave correcta y `texto` vacío | 400 | 400, "Escribe una pregunta para continuar." | Validación de pregunta vacía |
| 7 | Con clave correcta, `GOOGLE_API_KEY` vacía (antes de cargarla) | 502 con mensaje claro | 502, "Falta configurar la clave de Gemini..." | Falla de proveedor sin stack trace |
| 8 | Con clave correcta y `GOOGLE_API_KEY` inválida | 502 con mensaje claro | 502, "La clave de Gemini no es válida..." | Falla de proveedor sin stack trace |
| 9 | Pregunta de feria: "Quiero planificar una feria de emprendedores en Viña del Mar" | Respuesta del agente de Alex | 200, agente "Agente de Alex" | Pidió tipo de feria y asistentes |
| 10 | Pregunta sin agente: "¿Cuál es la capital de Francia?" | Respuesta "ninguno" | 200, agente "ninguno" | Sugiere los cuatro agentes |
| 11 | Pregunta sin agente: "¿Qué se necesita para cumplir la ley de protección de datos?" | Respuesta "ninguno" | 200, agente "ninguno" | |
| 12 | Pregunta sin agente: "¿Cómo funciona un control de acceso con clave?" | Respuesta "ninguno" | 200, agente "ninguno" | |
| 13 | Agente de Matías: programa de feria tecnológica de 6 horas para estudiantes | Programa de actividades | 200, agente "Agente de Matias" | Propone 4 bloques y avisa que quedan 140 minutos libres |
| 14 | Agente de Eduardo: presupuesto de feria gastronómica de 200 personas, 6 horas | Presupuesto simulado | 200, agente "Agente de Eduardo" | Montos ficticios; la primera versión de la pregunta pidió el tipo de evento |
| 15 | Agente de Sebastián: coffee break de 50 personas con menú vegetariano | Propuesta de catering | 200, agente "Agente de Sebastian" | Sin precios; cantidades calculadas |

## Logs

Extracto de `logs-heroku.txt`: líneas de `[coordinador]` y de las rutas `/panel/consultar`, `/salud` y `/agentes/*`. Se muestran el rechazo sin clave (401), la clave incorrecta (401), las validaciones (400) y las consultas exitosas. Este extracto no incluye los 502 de las filas 7 y 8, porque esas pruebas se hicieron antes de cargar la clave correcta.

## Notas

- La primera prueba con `GOOGLE_API_KEY` vacía dio 502. Después de cargar la clave, Google la rechazó porque el valor estaba mal copiado. Se corrigió con una carga nueva desde el `.env`.
- Los caracteres acentuados en peticiones enviadas desde Git Bash en Windows fallaban con 400 ("There was an error parsing the body"). Se resolvió enviando el JSON desde un archivo UTF-8. No es un error de la app.
