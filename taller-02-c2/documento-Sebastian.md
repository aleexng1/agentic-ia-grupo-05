# Documento de Sebastián: despliegue en Heroku y operación

**Grupo 05 · Taller 2 (c2t2) · Rama `c2t2/sebastian-heroku`**

## 1. Qué hice

Mi parte fue desplegar la app única (coordinador y cuatro agentes) en Heroku con mi cuenta y documentar cómo se opera.

1. Traje `origin/main` a mi rama (`git merge origin/main`) y probé la app en local con las pruebas del proyecto: 168 pasaron.
2. Creé la app en Heroku con la CLI: `grupo05-taller2-seba`, región us, stack heroku-24.
3. Cargué las Config Vars con la CLI: `CLAVE_API` (generada con `secrets.token_urlsafe`, nunca mostrada), `MODELO=gemini-3.5-flash-lite`, `WEB_CONCURRENCY=1`, `URL_BASE` y `GOOGLE_API_KEY`. No definí `PORT`, porque lo asigna Heroku.
4. Desplegué `main` con `git push` a la URL de git de Heroku. El build leyó el `Procfile` y el `requirements.txt` de la raíz. Quedó el release v5 con el commit `741305b`, y el dyno `web` corre en plan Eco.
5. Probé en remoto (sección 3) y escribí la sección «Operación en Heroku» del README (commit `0f92987`).
6. Guardé las evidencias de las pruebas y un extracto de logs en `evidencias/sebastian/` (commit `999fc22`).
7. Abrí el PR #81 desde `c2t2/sebastian-heroku` hacia `main`.

La URL pública es https://grupo05-taller2-seba-94d12914f3eb.herokuapp.com/.

## 2. Prompts que usé

Trabajé con Claude Code y le pedí, en orden:

- Hacer los despliegues con la Heroku CLI, después de leer el reparto del grupo (qué hace cada uno y las reglas de la rama).
- Revisar el estado del repositorio y de Heroku antes de tocar nada.
- Preparar la rama sin tocar `tf/herramientas`, usando un worktree.
- Probar en remoto después del despliegue, con una pregunta por agente.
- Revisar y humanizar los mensajes para el grupo antes de pegarlos.
- Guardar las evidencias y abrir el PR.

Usé un worktree para no mover mi rama de trabajo, y escribí los comandos de la CLI en la terminal de Windows con la sintaxis de PowerShell cuando hizo falta.

## 3. Pruebas

### Pruebas remotas (entorno HEROKU)

Las pruebas corrieron el 14/11/2026 contra la URL pública. Las respuestas completas están en `evidencias/sebastian/pruebas-remotas.md`.

| # | Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
|---|---|---|---|---|---|
| 1 | HEROKU, 14/11/2026 | `GET /salud` | 200 | 200 | Público |
| 2 | HEROKU, 14/11/2026 | `GET /.well-known/agent-card.json` | 200 | 200 | Ficha del coordinador |
| 3 | HEROKU, 14/11/2026 | `GET /agentes/matias/.well-known/agent-card.json` | 200 | 200 | Ficha de agente |
| 4 | HEROKU, 14/11/2026 | `POST /panel/consultar` sin `X-API-Key` | 401 | 401, "Falta la clave de acceso..." | Rechazo sin clave |
| 5 | HEROKU, 14/11/2026 | `POST /panel/consultar` con clave incorrecta | 401 | 401, "La clave de acceso es incorrecta." | Rechazo con clave falsa |
| 6 | HEROKU, 14/11/2026 | Clave correcta y `texto` vacío | 400 | 400, "Escribe una pregunta para continuar." | Validación |
| 7 | HEROKU, 14/11/2026 | Clave correcta, `GOOGLE_API_KEY` sin cargar | 502 con mensaje claro | 502, "Falta configurar la clave de Gemini..." | Falla del proveedor sin stack trace |
| 8 | HEROKU, 14/11/2026 | Clave correcta, `GOOGLE_API_KEY` con valor inválido | 502 con mensaje claro | 502, "La clave de Gemini no es válida..." | Se corrigió después (ver sección 4) |
| 9 | HEROKU, 14/11/2026 | Feria de emprendedores en Viña del Mar | Respuesta del agente de Alex | 200, agente de Alex | Pidió tipo de feria y asistentes |
| 10 | HEROKU, 14/11/2026 | "¿Cuál es la capital de Francia?" | "ninguno" | 200, "ninguno" | Sugiere los cuatro agentes |
| 11 | HEROKU, 14/11/2026 | "¿Qué se necesita para cumplir la ley de protección de datos?" | "ninguno" | 200, "ninguno" | |
| 12 | HEROKU, 14/11/2026 | "¿Cómo funciona un control de acceso con clave?" | "ninguno" | 200, "ninguno" | |
| 13 | HEROKU, 14/11/2026 | Programa de feria tecnológica de 6 horas para estudiantes | Programa del agente de Matías | 200, agente de Matías | Propone 4 bloques y deja 140 minutos libres |
| 14 | HEROKU, 14/11/2026 | Presupuesto de feria gastronómica de 200 personas, 6 horas | Presupuesto simulado del agente de Eduardo | 200, agente de Eduardo | Montos ficticios; una pregunta sin tipo de evento pidió aclaración |
| 15 | HEROKU, 14/11/2026 | Coffee break vegetariano para 50 personas | Propuesta del agente de Sebastián | 200, agente de Sebastián | Cantidades sin precios |

### Pruebas locales (entorno LOCAL)

| # | Entorno y fecha | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
|---|---|---|---|---|---|
| L1 | LOCAL, 14/11/2026 | `pytest` en `taller-02-c2/proyecto` | Todas pasan, sin llamar a Gemini | 168 passed | Entorno virtual con Python 3.12 |
| L2 | LOCAL, 14/11/2026 | `POST /panel/consultar` con texto "hola" y clave de prueba, sin `GOOGLE_API_KEY` | 502 con mensaje claro | 502, "Falta configurar la clave de Gemini..." | Confirma el mismo error que en Heroku |

## 4. Qué cambié después de probar

- **`URL_BASE`:** la primera vez puse `https://grupo05-taller2-seba.herokuapp.com`, pero el hostname real de la app lleva un sufijo. Lo corregí con `heroku config:set URL_BASE=...` y la app reinició (release v4).
- **`GOOGLE_API_KEY`:** la primera carga quedó con un valor de prueba o incompleto, y Google la rechazó (prueba 8). Después también quedó vacía una vez, porque el comando usaba `grep` en PowerShell, que no existe. Lo corregí cargando la clave desde el `.env` local con la sintaxis de PowerShell. Al final, la prueba con preguntas reales dio 200.
- **Peticiones con acentos:** las pruebas con `curl` y el JSON inline en Git Bash dieron 400 ("There was an error parsing the body"). Enviar el JSON desde un archivo UTF-8 lo resolvió. No era un error de la app.
- **Código:** no modifiqué código del proyecto. Solo cambié configuración de Heroku y el README.
- **Redespliegue final:** después de que se unió #81 a main, roté la `CLAVE_API` y desplegué `main` (commit `96ebca4`) en la release v12. El historial de main reescribió #81, así que el despliegue se hizo con un commit de Heroku que tiene el mismo árbol que main. Las pruebas básicas en remoto de esa versión, del 15/11/2026, están en `evidencias/sebastian/pruebas-remotas.md`.

## 5. Incidente de exposición de claves

Durante una sesión de diagnóstico se mostraron por error variables de otra aplicación de la misma cuenta de Heroku, que no pertenece a este proyecto. No se usaron ni se repitieron en ningún archivo del repositorio. Las claves de esa aplicación deben rotarse por su dueño.

## 6. Seguridad del despliegue

- `CLAVE_API` y `GOOGLE_API_KEY` solo viven en las Config Vars de Heroku y en el `.env` local, que está en `.gitignore`.
- Ninguna clave aparece en el repositorio, en el README ni en las evidencias.
- Matías usó la `CLAVE_API` anterior para sus pruebas. Se rotó en la release v11, y la nueva clave se entregó por un canal privado a Matías, Eduardo y Alex.

## 7. Límites y pendientes

- La memoria de la conversación vive en la RAM del dyno. Si Heroku lo duerme o se reinicia, el chat parte de cero.
- El dyno Eco se duerme tras 30 minutos sin visitas; la primera respuesta puede tardar varios segundos.
- `CLAVE_API` ya fue rotada: la nueva se cargó en la release v11, antes de desplegar `main` en la release v12.
- Release actual: v12, commit de Heroku `4593bafb`, con el mismo árbol que `main` (`96ebca4`). `git diff --stat 4593bafb 96ebca4` no muestra diferencias.
