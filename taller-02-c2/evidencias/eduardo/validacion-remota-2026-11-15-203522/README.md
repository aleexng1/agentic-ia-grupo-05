# Validación REMOTA de Eduardo · 2026-11-15

**URL probada:** https://grupo05-taller2-seba-94d12914f3eb.herokuapp.com/

**Release reportada: v10**, informada por Sebastián mediante la solicitud de Eduardo.
**Commit realmente desplegado: POR CONFIRMAR.** No se consultó Heroku CLI ni se atribuyen
estos resultados a `origin/main`. La validación corresponde al sitio observado en las
fechas de cada registro, no a una identidad de despliegue demostrada.

**Cierre PARCIAL:** pruebas públicas y del cliente completadas en el alcance indicado;
acceso válido y cuatro agentes **PENDIENTES**. La ejecución autenticada original terminó
con `TimeoutError` al esperar el ingreso, con **0 POST y 0 consultas a agentes**. No se
reinició ni se duplicó. La comprobación adicional del cliente hizo **un solo POST con
clave ficticia**, rechazado con 401. No hay ninguna respuesta útil autenticada que
permita aprobar un agente.

## Balance final

- **Aprobadas, con alcance limitado y evidencia abajo:** panel/salud, bloqueo del
  formulario vacío, rechazo HTTP sin clave y con clave ficticia, visualización de
  escritorio y **móvil emulado** del ingreso/saludo, espera natural del cliente,
  recuperación tras 401, guardia contra envíos repetidos durante esa espera y limpieza
  de historial/borrador mediante Nueva conversación tras el rechazo.
- **Fallidas:** la **ejecución instrumental de ingreso privado** no se completó
  (`TimeoutError`, 20:54:51). **No se observó una falla funcional de Heroku o de un
  agente**: los 401 eran rechazos esperados, no fallas del servicio. Un agente no
  ejecutado no se marca como fallido ni aprobado.
- **Pendientes/bloqueadas:** acceso con `CLAVE_API` vigente, las cuatro consultas
  autenticadas, respuesta útil/agente/motivo visibles de cada una, cambio de contexto
  y aislamiento entre conversaciones autorizadas y espera/duplicados durante una
  consulta aceptada. También siguen sin comprobarse la vista móvil de una respuesta
  autorizada y el **teléfono físico**. El commit desplegado sigue pendiente.
- **Sin reintentos autenticados.** Tras consultar el estado, Eduardo indicó
  «No hay ventana o clave». No se usa la clave local como sustituto ni se solicita
  publicar una clave. [Incidencia y decisiones](seguimiento-autenticado.md).

## Entorno, Git y separación del PR #83

- Rama local: `c2t2/eduardo-frontend`; `HEAD` inicial:
  `8a5bb9babdeddf4df957473806a5213928a18901`.
- Referencia local `origin/main`: `71df3e80adea7ec675db73eefe884cb82eeffc9a`.
  No se actualizó ni se equiparó a Heroku.
- PR [#83](https://github.com/aleexng1/agentic-ia-grupo-05/pull/83): **abierto y no
  fusionado**, confirmado por API pública a las **20:39:10, UTC−03:00**. Por ello
  todo este trabajo queda exclusivamente en esta carpeta nueva. No se editan los
  tres documentos de Eduardo que Alex está ajustando ni otros archivos anteriores.
- Estado previo al trabajo: únicamente la foto sin seguimiento
  `taller-01-c2/evidencias/eduardo/03-ficha-telefono.jpg`. La línea base privada de
  conservación, fuera del repositorio, protege 430 archivos, incluido `.env`.
- Windows; Python **3.12.10**, Playwright **1.65.1**, httpx **0.28.1**, Chrome
  **157.0.8103.78**. Se reutiliza `.venv`; no se instalan dependencias ni se ejecuta
  ninguna suite local. Fase pública: Chrome sin ventana; autenticada: ventana propia
  de Chrome para ingreso privado.

El HTML remoto difiere del archivo Windows solo por los finales de línea: coincide
al normalizar CRLF a LF, según [comparacion-html.json](comparacion-html.json).
**Eso no identifica el commit completo ni verifica v10.**

## Resultados públicos · cinco columnas

En toda la tabla, **REMOTO** designa la URL de cabecera. Horas locales en UTC−03:00;
el registro del POST sin clave conserva además su hora UTC original.

| Entorno y fecha | Solicitud | Esperado | Obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| REMOTO · Heroku · 2026-11-15 · identidad del despliegue | Identificar URL, release y commit | Identidad desplegada trazable | **PARCIAL:** URL observada; v10 **reportada**; commit **pendiente** | No se verificó la release con Heroku ni se infiere el commit desde Git. |
| REMOTO · Heroku · 2026-11-15 · 20:39:10–20:39:12 | GET `/` y `/salud` por HTTPS | 200; panel correcto y `{"ok":true}` | **APROBADO en este equipo:** ambos 200; título «Planifica tu feria · Grupo 5»; panel `no-store`, `nosniff`, `no-referrer` | [Registro](resultados-publicos.json), [ingreso escritorio](01-ingreso-escritorio.png). Chrome informa TLS 1.3 y emisor **ESET SSL Filter CA**: hay inspección TLS del equipo; no es una comprobación independiente de la cadena pública de Heroku. |
| REMOTO · Heroku · Chrome escritorio · 2026-11-15 · 20:39:13 | Continuar con campo de clave vacío | No abrir el chat ni enviar consulta | **APROBADO, solo formulario:** campo requerido inválido; chat oculto; 0 POST | No sustituye el rechazo HTTP sin cabecera del caso siguiente. [Registro](resultados-publicos.json). |
| REMOTO · Heroku · R06 · 2026-11-15 · 20:39:13 | POST real `/panel/consultar` sin `X-API-Key`, con pregunta no vacía | 401 por clave ausente | **APROBADO:** 401 JSON; «Falta la clave de acceso. Envíala en la cabecera X-API-Key.» | [Cuerpo y tiempo](r06-sin-clave.json). Fetch real desde Chrome, no aviso nativo del panel ni respuesta simulada. Sin acceso a logs remotos: no se afirma un conteo interno de coordinador, A2A o Gemini. |
| REMOTO · Heroku · R07 · 2026-11-15 · 20:39:13 | Clave deliberadamente ficticia en el panel; enviar pregunta de presupuesto | 401; volver al ingreso, vaciar clave y conservar pregunta | **APROBADO:** 401; aviso nativo de clave incorrecta; chat oculto, campo vacío y pregunta conservada | [Intercambio](r07-clave-ficticia.json), [captura](02-clave-ficticia-rechazada.png). Un intento, sin reintento automático. Se oculta íntegramente el campo incluso estando vacío. |
| REMOTO · Heroku · Chrome escritorio · 2026-11-15 · 20:39:13 | Escribir borrador y pulsar Nueva conversación, con clave ficticia cargada pero sin enviar consulta | Limpiar borrador e historial sin POST | **APROBADO solo en interfaz:** 0 mensajes de usuario, 1 saludo, entrada vacía, 0 POST adicionales | [Captura](03-nueva-conversacion-solo-interfaz.png). No acredita aún cambio de `context_id` enviado al servidor ni cancelación de una consulta autorizada. |
| REMOTO · Heroku · escritorio 1280 × 960 · 2026-11-15 · 20:39:12–20:39:13 | Revisar ingreso, rechazo y chat inicial | Interfaz legible y controles accesibles, sin desborde horizontal | **APROBADO para estas pantallas:** ancho página/interior 1280 px; botones ≥44 px; entrada 16 px | [Capturas y procedencia](capturas-publicas.json). Inspección visual más medidas DOM; no auditoría completa de accesibilidad. |
| REMOTO · Heroku · móvil EMULADO en Chrome · 2026-11-15 · 20:39:14–20:39:16 | Ingreso y saludo del chat con perfil Pixel 7 (412 px); repetir vista a 320 px | Sin desborde horizontal, chat antes de agentes, botones ≥44 px y entrada 16 px | **APROBADO para ingreso/saludo emulados:** sin desborde a 412 y 320 px; chat primero; medidas conformes | [Ingreso](04-ingreso-movil-emulado.png), [412 px](05-chat-movil-emulado-sin-consulta.png), [320 px](06-chat-320-emulado-sin-consulta.png). Clave ficticia cargada, sin consulta autorizada. **No es teléfono físico**, Safari, teclado virtual ni una respuesta de agente. |

## Casos autenticados · cierre sin reintentos

Para aprobar **cada** agente se exige **HTTP 200 + respuesta útil + agente correcto +
motivo visible**, conservando pregunta, respuesta y captura sin credenciales. Ninguno
de esos cuatro casos se ejecutó: no se inventan respuestas o capturas para completarlos.
Las preguntas previstas, claramente rotuladas **NO ENVIADAS**, están en
[agentes-pendientes.json](agentes-pendientes.json).

| Entorno y fecha | Solicitud | Esperado | Obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| REMOTO · Heroku · Chrome con ventana · 2026-11-15 · 20:39:49–20:54:51 | Esperar ingreso privado y habilitación del chat en la ejecución original | Chat visible; luego una consulta controlada por agente | **EJECUCIÓN INSTRUMENTAL NO COMPLETADA:** `TimeoutError` esperando el chat; 0 POST; 0 casos y 0 capturas | [Registro original](resultados-autenticados.json), [manifiesto vacío](capturas-autenticadas.json), [seguimiento](seguimiento-autenticado.md). Es la espera de ingreso de hasta 15 minutos, no el timeout de consulta de 65 s ni el router de Heroku. No hubo reintento. |
| REMOTO · Heroku · 2026-11-15 · NO EJECUTADA | Consultar con `CLAVE_API` vigente de Heroku | Servidor acepta una consulta real con 200 | **PENDIENTE/BLOQUEADA:** no hubo POST autenticado | La confirmación inicial del ingreso no demuestra autorización; posteriormente Eduardo indicó que no disponía de ventana o clave. Ninguna clave local se usó como sustituto. |
| REMOTO · Heroku · Matías · 2026-11-15 · NO EJECUTADA | Programa de feria cultural familiar, 3 horas desde las 16:00 | 200, programa útil, `Agente de Matias` y motivo visible | **PENDIENTE:** pregunta prevista no enviada; sin HTTP, respuesta o captura | [Plan explícitamente no ejecutado](agentes-pendientes.json), [registro de la fase](resultados-autenticados.json). |
| REMOTO · Heroku · Alex · 2026-11-15 · NO EJECUTADA | Recinto interior para feria tecnológica de 80 personas | 200, opciones útiles, `Agente de Alex` y motivo visible | **PENDIENTE:** pregunta prevista no enviada; sin HTTP, respuesta o captura | [Plan explícitamente no ejecutado](agentes-pendientes.json), [registro de la fase](resultados-autenticados.json). |
| REMOTO · Heroku · Eduardo · 2026-11-15 · NO EJECUTADA | Presupuesto simulado para feria tecnológica de 80 personas y 4 horas | 200, presupuesto útil con partidas y CLP, `Agente de Eduardo` y motivo visible | **PENDIENTE:** pregunta prevista no enviada; sin HTTP, respuesta o captura | [Plan explícitamente no ejecutado](agentes-pendientes.json), [registro de la fase](resultados-autenticados.json). Los POST rechazados del alcance público no son consultas funcionales a Eduardo. |
| REMOTO · Heroku · Sebastián · 2026-11-15 · NO EJECUTADA | Catering de 10:00 a 14:00, 80 personas, 10 vegetarianas y 5 sin gluten | 200, propuesta útil con dietas/horarios/agua, `Agente de Sebastian` y motivo visible | **PENDIENTE:** pregunta prevista no enviada; sin HTTP, respuesta o captura | [Plan explícitamente no ejecutado](agentes-pendientes.json), [registro de la fase](resultados-autenticados.json). |

## Pendientes del cliente comprobados sin clave remota

Ejecución adicional **21:07:57–21:07:59, UTC−03:00**, del 15-11-2026, contra la misma
URL. Una pregunta nueva de interfaz, no el reenvío de los casos autenticados: «Validación
del panel: necesito el programa de una feria infantil de 3 horas desde las 15:00, con
datos de demostración.». Se usó exclusivamente una clave ficticia y se recibió el 401
esperado. Sin interceptar respuestas, retener red, inducir fallas o demoras ni ejecutar
suites locales. El estado nativo «Consultando al coordinador…» **no prueba que el
coordinador haya sido invocado**: el servidor rechazó la autorización.

| Entorno y fecha | Solicitud | Esperado | Obtenido | Observaciones |
| --- | --- | --- | --- | --- |
| REMOTO · Heroku · Chrome escritorio 1280 × 960 · 2026-11-15 · 21:07:59 | Enviar una pregunta con clave ficticia y observar la espera natural | Indicador, `aria-busy=true`, envío y sugerencias bloqueados; recuperación al responder | **APROBADO para el rechazo real:** todo observado; `aria-busy=true` antes y después de la captura; tras 401 queda `false`, sin indicador, controles habilitados y pregunta conservada | [Mediciones y cuerpo](resultados-panel-pendiente.json), [espera nativa](07-espera-panel-rechazo-real.png), [rechazo](08-panel-recuperado-tras-401.png). 0,447 s hasta leer el cuerpo, incluida captura instrumental; no mide latencia pura del servidor ni una espera autorizada de agentes. |
| REMOTO · Heroku · Chrome escritorio · 2026-11-15 · 21:07:59 | Durante esa misma espera, intentar Enter con texto, submit programático y clicks sobre Enviar/sugerencia bloqueados | Una sola solicitud POST, sin reenvíos automáticos | **APROBADO en el navegador para este caso:** **1 POST total** pese a 4 intentos adicionales; HTTP 401 | [Conteo y cuerpo de la única solicitud](resultados-panel-pendiente.json). Los dos intentos con texto no vacío se ejecutan en el mismo turno JS que el primer envío; los clicks son sobre controles deshabilitados. No acredita conteos internos A2A/Gemini ni duplicados durante una consulta autorizada, que siguen pendientes. |
| REMOTO · Heroku · Chrome escritorio · 2026-11-15 · 21:07:59 | Volver al historial con clave ficticia cargada, sin consultar; pulsar Nueva conversación tras el rechazo | Eliminar pregunta/borrador/historial anterior sin otro POST | **APROBADO solo en cliente:** antes 1 mensaje de usuario y pregunta conservada; después 0 mensajes de usuario, entrada vacía, 1 saludo, sin indicador y 0 POST adicionales | [Mediciones](resultados-panel-pendiente.json), [historial limpio](09-nueva-conversacion-tras-rechazo.png). No prueba memoria/aislamiento del servidor, cambio de `context_id` entre consultas aceptadas ni descarte de una respuesta autorizada tardía. |

En las tres fases se observaron **3 POST públicos rechazados** (uno sin clave y dos
con clave ficticia, el último específico de espera/guardia) y **0 POST autenticados**.
No se reenviaron las preguntas previstas para los agentes.

## Evidencia, privacidad y límites

- [Solicitud y alcance](solicitud-y-alcance.md) y [ejecutor dirigido](validar_remoto.py).
- [Resultados públicos primarios](resultados-publicos.json): estados HTTP, detalles
  recibidos, TLS visto desde este equipo, versiones, geometrías y cuerpos permitidos.
- [Manifiesto de capturas públicas](capturas-publicas.json): archivo, fecha con zona,
  URL, alcance, viewport y SHA-256 por imagen. No se añade una falsa barra de navegador
  ni se fabrican avisos. Las capturas nativas conservan el diseño real.
- [Capturas del cierre del cliente](capturas-panel-pendiente.json): tres imágenes
  adicionales con fecha, URL, alcance, viewport y huella. Se revisaron visualmente.
- [Registro de incidencia](seguimiento-autenticado.md), [resultados autenticados
  originales](resultados-autenticados.json) y [planes pendientes](agentes-pendientes.json).
- Sin `.env` ni claves locales para autenticar Heroku. La clave de Google nunca se
  ingresa en el panel. El instrumental no lee el campo de clave ni las cabeceras de
  petición, no genera HAR/trazas/storage-state ni adjunta consolas o capturas de Network.
- El campo de clave se enmascara íntegramente en todas las capturas, sin revelar
  longitud. Solo se registran `texto` y `context_id` de las peticiones y los campos
  del contrato de respuesta. No se inspeccionan Config Vars ni logs de Heroku.
- No se provocan errores del proveedor/router, desconexiones ni demoras. No se cambian
  configuración, versiones, código de producción, procesos de la app ni servicios locales.
- Memoria entre reinicios, cancelación del trabajo en el servidor, logs A2A, seguridad
  integral y límite del router **no comprobados**. No son aprobaciones implícitas.
- Sin `git add`, commit, push, merge ni cambios en los documentos compartidos.

## Archivos y conservación al cierre

Lista exacta, con rutas relativas a la raíz:
[archivos-modificados.txt](archivos-modificados.txt). Todas sus rutas están dentro de
esta carpeta; son archivos nuevos respecto de Git. La foto previa del Taller 1 queda
fuera de la lista. En esta continuación se actualizó este README para cerrar el informe;
no se sobrescribieron registros ni capturas primarias anteriores.

[revision-final.json](revision-final.json) contiene la comprobación final de los 430
archivos previos y del índice, integridad de capturas, sintaxis del instrumental,
enlaces/tablas de cinco columnas y alcance de los archivos. La revisión de patrones
de credenciales es limitada; no sustituye una auditoría integral ni expone huellas
privadas de `.env`. Las evidencias históricas y claves privadas no se modifican.
