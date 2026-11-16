# Solicitud y alcance · REMOTO · 2026-11-15

URL: https://grupo05-taller2-seba-94d12914f3eb.herokuapp.com/

Eduardo solicitó continuar la validación REMOTA en `c2t2/eduardo-frontend`, leyendo
README, AGENTS y su documento, conservando el estado existente de Git. Sebastián
informó **release v10**: se registra como **reportada**, con **commit desplegado por
confirmar**, sin equipararlo a `origin/main`.

Casos solicitados: rechazo sin clave y con clave ficticia, acceso con la `CLAVE_API`
vigente de Heroku, una consulta a cada agente (respuesta, agente y motivo), nueva
conversación, espera y ausencia de envíos duplicados, escritorio y móvil diferenciando
emulación de equipo real.

La clave de Google nunca se ingresa en el panel. No se usa ni se consulta `.env` para
autenticar Heroku. Si falta la clave remota, solo se detienen los casos autenticados
y se ofrece ingresarla privadamente en Chrome, sin escribirla en conversación,
comandos, registros, archivos ni capturas. Cargar una clave no prueba autorización:
debe responder la primera consulta real.

Todo se guarda en esta carpeta nueva mientras el PR #83 permanezca abierto, sin
editar `documento-Eduardo.md`, índices anteriores ni archivos de Alex. Matriz de
resultados con exactamente cinco columnas: **Entorno y fecha, Solicitud, Esperado,
Obtenido y Observaciones**. Los pendientes no se aprueban.

Sin cambios de configuración, despliegues, reinicios, fallas inducidas en Heroku,
suites locales completas, staging, commit ni push. Las observaciones de duplicados
se limitan a los POST del navegador; no equivalen a acceso a los logs internos A2A
o de Gemini. El teléfono físico, Safari y el teclado virtual no quedan acreditados
por una emulación.

## Continuación solicitada por Eduardo

Seguir la ejecución autenticada original, sin duplicarla. Para aprobar cada agente,
exigir HTTP 200, respuesta útil, agente correcto y motivo visible; conservar pregunta,
respuesta y captura sin credenciales. Completar solo Nueva conversación, espera y
ausencia de envíos duplicados que estuvieran pendientes. Cerrar este mismo informe
separando aprobadas, fallidas y pendientes, con evidencia, fecha, URL, v10 reportada
y commit desplegado por confirmar; entregar lista exacta de archivos, sin commit/push.

Si la ejecución falla o queda detenida, registrar primero el error observado antes de
decidir un reintento. En el seguimiento Eduardo indicó «No hay ventana o clave».
Se registra el `TimeoutError` de la espera de ingreso y **no se reintenta** la fase
autenticada. El caso posterior de espera/guardia es una prueba independiente del
cliente, con clave ficticia y 401 esperado, no una consulta funcional a agentes.
