# Seguimiento de la ejecución autenticada · 2026-11-15

URL: https://grupo05-taller2-seba-94d12914f3eb.herokuapp.com/

## Corte de seguimiento · 20:50:26, UTC−03:00

- Se retomó **la misma ejecución** de `validar_remoto.py autenticado`, iniciada a
  las 20:39:48. Los procesos propios seguían presentes; no se lanzó otra instancia.
- En este corte no había intercambios, capturas ni resultados autenticados guardados
  en la carpeta. El último mensaje de la salida del instrumental era la instrucción
  de ingresar privadamente `CLAVE_API` en Chrome y pulsar «Continuar al chat».
- Eduardo había confirmado el ingreso privado. Esa confirmación por sí sola no
  demuestra un POST aceptado por el servidor ni permite aprobar ningún agente.
- **Error HTTP observado hasta este corte: ninguno registrado para la fase
  autenticada.** No se atribuye la detención a Heroku, Gemini o una clave inválida.
  La ausencia de archivos tampoco demuestra por sí sola que no hubiera una solicitud
  en vuelo. Se requiere aclarar el estado de la ventana original antes de decidir
  cualquier nueva ejecución.
- **Decisión: no reenviar consultas ni reintentar.** Comprobar primero la ventana
  original, sin leer ni publicar la clave. Las pruebas públicas conservan su evidencia
  y sus resultados previos; los agentes continúan pendientes en este corte.

Release **v10 reportada por Sebastián**; commit desplegado **pendiente de confirmación**.

## Cierre de la ejecución original · 20:54:51, UTC−03:00

- La notificación de finalización y
  [resultados-autenticados.json](resultados-autenticados.json) confirman
  **`TimeoutError`**. El instrumental esperaba hasta 15 minutos la visibilidad del
  chat tras el ingreso privado. No es el timeout de 65 segundos de una consulta
  ni un timeout del router de Heroku.
- El registro final contiene **0 solicitudes POST observadas**, **0 casos de agentes**
  y [0 capturas autenticadas](capturas-autenticadas.json). Ahora sí hay evidencia
  instrumental para afirmar que esta ejecución no inició consultas de agentes.
- Al solicitar aclaración, Eduardo seleccionó **«No hay ventana o clave»**. No se
  interpreta su confirmación anterior como acceso autorizado ni como clave inválida:
  no hubo respuesta HTTP autenticada que permita comprobarlo.
- **Decisión tomada después de registrar el error: no reintentar la autenticación
  ni reenviar consultas a agentes.** Acceso permitido, respuesta útil, agente correcto
  y motivo visible quedan pendientes para los cuatro agentes.
- Para completar solo la parte pendiente del cliente se hará una comprobación
  separada, con **una solicitud de clave ficticia** y rechazo 401 esperado: estado
  de espera natural, intentos de envío mientras espera, conteo de POST, recuperación
  y Nueva conversación tras el rechazo. No es un reintento autenticado ni una prueba
  de respuestas útiles o de memoria de los agentes. No se inducen fallas del
  proveedor/router, demoras ni cambios de configuración.

## Resultado del caso independiente del cliente · 21:07:57–21:07:59, UTC−03:00

- [resultados-panel-pendiente.json](resultados-panel-pendiente.json) registra una sola
  solicitud nueva con clave ficticia, rechazada **401**. Es una prueba específica de
  la guardia/espera del cliente, no un reintento de autenticación o de los agentes.
- Estado de espera real capturado con `aria-busy=true` antes y después de la imagen,
  indicador visible y botones de envío/sugerencias deshabilitados.
- Cuatro intentos adicionales de envío durante esa espera produjeron **1 POST total**.
  Tras el rechazo se recuperaron los controles y se conservó la pregunta.
- Nueva conversación eliminó el mensaje de usuario y borrador; dejó solo el saludo,
  sin indicador y sin solicitudes adicionales.
- Ninguna de estas comprobaciones acredita una consulta aceptada, la utilidad de una
  respuesta de agente o la memoria del servidor. Los cuatro agentes siguen pendientes.
