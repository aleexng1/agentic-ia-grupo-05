# Pruebas remotas en Heroku (Sebastián)

**Entorno:** HEROKU
**Fecha:** 14/11/2026
**URL:** https://grupo05-taller2-seba-94d12914f3eb.herokuapp.com/
**App:** grupo05-taller2-seba (stack heroku-24, dyno web Eco)
**Versión desplegada en las 15 pruebas de la tabla:** `origin/main` (commit 741305b), release v8
**Versión desplegada en la repetición final:** `main` (commit 96ebca4), release v12
Las consultas manuales de Eduardo del 15/11/2026 (21:51–22:03) se hicieron en esta misma release v12: ver [`manual-autenticada-2026-11-15/README.md`](../eduardo/manual-autenticada-2026-11-15/README.md).

Las claves no aparecen en este archivo. La `CLAVE_API` y la `GOOGLE_API_KEY` viven solo en las Config Vars de Heroku.

## Resultados

| # | Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
|---|---|---|---|---|---|
| 1 | HEROKU · 14/11/2026 | `GET /salud` | 200 | 200 | Público |
| 2 | HEROKU · 14/11/2026 | `GET /.well-known/agent-card.json` | 200 | 200 | Ficha del coordinador |
| 3 | HEROKU · 14/11/2026 | `GET /agentes/matias/.well-known/agent-card.json` | 200 | 200 | Ficha de agente |
| 4 | HEROKU · 14/11/2026 | `POST /panel/consultar` sin cabecera `X-API-Key` | 401 | 401, "Falta la clave de acceso. Envíala en la cabecera X-API-Key." | Rechazo sin clave |
| 5 | HEROKU · 14/11/2026 | `POST /panel/consultar` con clave incorrecta | 401 | 401, "La clave de acceso es incorrecta." | Rechazo con clave falsa |
| 6 | HEROKU · 14/11/2026 | Con clave correcta y `texto` vacío | 400 | 400, "Escribe una pregunta para continuar." | Validación de pregunta vacía |
| 7 | HEROKU · 14/11/2026 | Con clave correcta, `GOOGLE_API_KEY` vacía (antes de cargarla) | 502 con mensaje claro | 502, "Falta configurar la clave de Gemini..." | Falla de proveedor sin stack trace |
| 8 | HEROKU · 14/11/2026 | Con clave correcta y `GOOGLE_API_KEY` inválida | 502 con mensaje claro | 502, "La clave de Gemini no es válida..." | Falla de proveedor sin stack trace |
| 9 | HEROKU · 14/11/2026 | Pregunta de feria: "Quiero planificar una feria de emprendedores en Viña del Mar" | Respuesta del agente de Alex | 200, agente "Agente de Alex" | Pidió tipo de feria y asistentes |
| 10 | HEROKU · 14/11/2026 | Pregunta sin agente: "¿Cuál es la capital de Francia?" | Respuesta "ninguno" | 200, agente "ninguno" | Sugiere los cuatro agentes |
| 11 | HEROKU · 14/11/2026 | Pregunta sin agente: "¿Qué se necesita para cumplir la ley de protección de datos?" | Respuesta "ninguno" | 200, agente "ninguno" | |
| 12 | HEROKU · 14/11/2026 | Pregunta sin agente: "¿Cómo funciona un control de acceso con clave?" | Respuesta "ninguno" | 200, agente "ninguno" | |
| 13 | HEROKU · 14/11/2026 | Agente de Matías: programa de feria tecnológica de 6 horas para estudiantes | Programa de actividades | 200, agente "Agente de Matias" | Propone 4 bloques y avisa que quedan 140 minutos libres |
| 14 | HEROKU · 14/11/2026 | Agente de Eduardo: presupuesto de feria gastronómica de 200 personas, 6 horas | Presupuesto simulado | 200, agente "Agente de Eduardo" | Montos ficticios; la primera versión de la pregunta pidió el tipo de evento |
| 15 | HEROKU · 14/11/2026 | Agente de Sebastián: coffee break de 50 personas con menú vegetariano | Propuesta de catering | 200, agente "Agente de Sebastian" | Sin precios; cantidades calculadas |

## Logs

Extracto de `logs-heroku.txt`: líneas de `[coordinador]` y de las rutas `/panel/consultar`, `/salud` y `/agentes/*`. Se muestran el rechazo sin clave (401), la clave incorrecta (401), las validaciones (400) y las consultas exitosas. Este extracto no incluye los 502 de las filas 7 y 8, porque esas pruebas se hicieron antes de cargar la clave correcta.

## Notas

- La primera prueba con `GOOGLE_API_KEY` vacía dio 502. Después de cargar la clave, Google la rechazó porque el valor estaba mal copiado. Se corrigió con una carga nueva desde el `.env`.
- Los caracteres acentuados en peticiones enviadas desde Git Bash en Windows fallaban con 400 ("There was an error parsing the body"). Se resolvió enviando el JSON desde un archivo UTF-8. No es un error de la app.

## Repetición en la release v12 (main 96ebca4)

Se repitieron las pruebas básicas después de rotar la `CLAVE_API` y desplegar `main`. La `CLAVE_API` no aparece en este archivo.

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
|---|---|---|---|---|
| HEROKU · release v12 · 15/11/2026 | `GET /salud` | 200 | 200 | — |
| HEROKU · release v12 · 15/11/2026 | Fichas de los cuatro agentes (`/agentes/*/.well-known/agent-card.json`) | 200 | 200 | — |
| HEROKU · release v12 · 15/11/2026 | `POST /panel/consultar` sin `X-API-Key` | 401 | 401 | — |
| HEROKU · release v12 · 15/11/2026 | `POST /panel/consultar` con clave falsa | 401 | 401 | — |
| HEROKU · release v12 · 15/11/2026 | `POST /panel/consultar` con la clave nueva y texto válido | 200 con respuesta de agente | 200 | — |
| HEROKU · release v12 · 15/11/2026 | `POST /panel/consultar` con la clave nueva y texto vacío | 400 | 400 | — |

Las filas 7 y 8 de la tabla principal (502 por `GOOGLE_API_KEY`) no se repitieron en v12, porque requieren quitar la clave de Gemini en Heroku.

## Pruebas locales de los dos casos de error (código de main 96ebca4)

Se probaron en local, sin tocar Heroku, con el código de `main` exportado a una carpeta temporal y sin `.env`.

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
|---|---|---|---|---|
| LOCAL · código de main `96ebca4` · 15/11/2026 | `CLAVE_API` vacía: `CLAVE_API` vacía, `GOOGLE_API_KEY` vacía | 503 (el servidor no acepta consultas) | 503 con mensaje "no tiene configurada la clave de acceso (CLAVE_API)" | — |
| LOCAL · código de main `96ebca4` · 15/11/2026 | Sin clave de Gemini: `CLAVE_API` con valor de prueba, `GOOGLE_API_KEY` vacía | 502 con mensaje claro | 502 con mensaje "Falta configurar la clave de Gemini (GOOGLE_API_KEY) en el .env o en las Config Vars" | — |

El 503 depende de `CLAVE_API` vacía, no de `GOOGLE_API_KEY`. La falta de la clave de Gemini responde 502. Las dos pruebas usan `PORT` igual a `URL_BASE`, porque el coordinador busca a los agentes en esa dirección.

## Preguntas a cada agente en la release v12 (main 96ebca4)

Se probó en remoto la release v12 con una pregunta a cada agente y una pregunta sin agente. Las respuestas son del modelo y pueden variar entre ejecuciones; lo que se verifica es el código de respuesta y qué agente atendió.

| Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
|---|---|---|---|---|
| HEROKU · release v12 · 15/11/2026 | "¿Qué recinto sirve para una feria de 300 personas en Santiago?" | 200 y el agente que corresponde | 200, Agente de Alex | Pidió el tipo de evento (tecnológico, gastronómico, cultural o infantil) |
| HEROKU · release v12 · 15/11/2026 | "Presupuesto para una feria gastronómica de 100 personas, 4 horas" | 200 y el agente que corresponde | 200, Agente de Eduardo | Presupuesto simulado en CLP con contingencia |
| HEROKU · release v12 · 15/11/2026 | "Programa de una feria tecnológica de 4 horas para 80 personas" | 200 y el agente que corresponde | 200, Agente de Matias | Programa de actividades |
| HEROKU · release v12 · 15/11/2026 | "Coffee break para 30 personas con opción sin gluten" | 200 y el agente que corresponde | 200, Agente de Sebastian | Propuesta de catering |
| HEROKU · release v12 · 15/11/2026 | "¿Cuál es la capital de Francia?" (sin agente) | 200 y «ninguno» | 200, ninguno | Sugiere los cuatro agentes |

Extracto del log de Heroku (release v12) con el envío A2A del coordinador a 127.0.0.1. Las IP de clientes están reemplazadas por `<ip-cliente>`:

```
[coordinador] pregunta recibida · «¿Qué recinto sirve para una feria de 300 personas en Santiago?»
[coordinador] supervisor eligió Agente de Alex
[coordinador] A2A → http://127.0.0.1:24918/agentes/alex · enviando
INFO: 127.0.0.1:44052 - "POST /agentes/alex HTTP/1.1" 200 OK
[coordinador] A2A ← Agente de Alex · respuesta recibida en 1,9 s
INFO: <ip-cliente> - "POST /panel/consultar HTTP/1.1" 200 OK
[coordinador] pregunta recibida · «Presupuesto para una feria gastronómica de 100 personas, 4 horas»
[coordinador] supervisor eligió Agente de Eduardo
[coordinador] A2A → http://127.0.0.1:24918/agentes/eduardo · enviando
INFO: 127.0.0.1:54918 - "POST /agentes/eduardo HTTP/1.1" 200 OK
[coordinador] A2A ← Agente de Eduardo · respuesta recibida en 7,5 s
INFO: <ip-cliente> - "POST /panel/consultar HTTP/1.1" 200 OK
[coordinador] pregunta recibida · «Programa de una feria tecnológica de 4 horas para 80 personas»
[coordinador] supervisor eligió Agente de Matias
[coordinador] A2A → http://127.0.0.1:24918/agentes/matias · enviando
INFO: 127.0.0.1:54918 - "POST /agentes/matias HTTP/1.1" 200 OK
[coordinador] A2A ← Agente de Matias · respuesta recibida en 2,6 s
INFO: <ip-cliente> - "POST /panel/consultar HTTP/1.1" 200 OK
[coordinador] pregunta recibida · «Coffee break para 30 personas con opción sin gluten»
[coordinador] supervisor eligió Agente de Sebastian
[coordinador] A2A → http://127.0.0.1:24918/agentes/sebastian · enviando
INFO: 127.0.0.1:54918 - "POST /agentes/sebastian HTTP/1.1" 200 OK
[coordinador] A2A ← Agente de Sebastian · respuesta recibida en 9,1 s
INFO: <ip-cliente> - "POST /panel/consultar HTTP/1.1" 200 OK
[coordinador] pregunta recibida · «¿Cuál es la capital de Francia?»
[coordinador] supervisor eligió ninguno
INFO: <ip-cliente> - "POST /panel/consultar HTTP/1.1" 200 OK
```
