# Prompts de desarrollo — Herramientas y estado

Responsable: Sebastián Mardones

> Registra aquí los prompts que usaste para desarrollar tu parte, del más antiguo al más nuevo.
> Copia el bloque de abajo una vez por prompt. Nunca pegues claves, contraseñas ni datos reales:
> si un prompt los tenía, reemplaza esa parte por `[omitido: motivo]`.

---

## 1. Arquitectura e implementación de validar_gasto, memoria del fondo y registro

- **Fecha:** 2026-10-31
- **Herramienta:** Claude (claude.ai, entorno de ejecución de Claude Code)
- **Modelo:** Claude Opus 5.5 (`claude-opus-5-5`)
- **Para qué era:** definir la arquitectura y las decisiones de mi rol, y luego implementar
  `src/herramientas.py`, `src/memoria.py` y `src/registro.py` contra la política v1.1 y el golden set v1.0.

**Prompt completo:**

````text
[adjuntos: Pauta_tarea_final.md y el resumen del proyecto del Grupo 05]
Prepara la arquitectura y las decisiones de esta tarea mi parte. Este trabajo corresponde a un
agente que está la conversación [Configurar equipo para proyecto grupal GitHub]
Considera el stack necesario. Utiliza como referencia mis trabajos del curso que están en la ruta
[D:\Certificate Agentic IA] y el MCP en Github

Hazme las consultas que consideres necesarias.
````

**Decisiones que tomé al responder las consultas del asistente:**

- RG-08 (saldo del fondo) se revisa con `memoria.revisar_saldo`, y el Núcleo lo agrega a la
  observación de `validar_gasto` en su nodo de herramientas (PR #2). La firma de `validar_gasto` no cambia.
- `registrar_veredicto` no es una herramienta del LLM. Lo llama el grafo después del juez.
- El asistente escribe el documento de arquitectura y el código; el push lo hago yo con `/subir-cambios`.

**Resultado (una línea):** reglas leídas de la política (no copiadas), 28/28 turnos deterministas
del golden set correctos (GS-23 depende del LLM por RG-02), `verificar.py` 41 ✅ 0 ❌.

---

## 2. Revisión de la arquitectura y corrección del piso de reglas

- **Fecha:** 2026-10-31
- **Herramienta:** Claude Code (app de escritorio), con el MCP de GitKraken para GitHub
- **Modelo:** Claude Opus 5.5 (`claude-opus-5-5`)
- **Para qué era:** revisar el documento de arquitectura contra el código, ver el estado de mi rama
  en GitHub y corregir las fallas encontradas.

**Prompt completo:**

````text
[adjunto: Arquitectura y decisiones — Herramientas y estado (Grupo 05).md]
Revisa esta arquitectura y la implementación, abre y ejecuta el MCP de Github y muestrame mi rama.
````

Después aprobé las correcciones ("Sí, corrígelos") y la subida ("Sí, súbelos").

**Decisiones que tomé al responder las consultas del asistente:**

- Corregir `efecto_de`: solo vale el "Efecto: …" del final del detalle. Antes, un
  `Efecto: aprobar` escrito en la categoría declarada o en la patente bajaba el piso a APROBAR.
- Corregir el parche para Matías: el usuario ve la decisión corregida por el piso, y un turno sin
  `validar_gasto` no registra nada ni reutiliza el gasto del turno anterior.
- Dejar como propuesta al grupo que el grafo cargue un gasto de confianza: hoy el piso usa el
  gasto que le pasa el LLM.

**Resultado (una línea):** `verificar.py` 41 ✅ 0 ❌ y `probar_herramientas.py` 45 ✅ 0 ❌
(2 pruebas nuevas del piso); el parche aplica limpio sobre el PR #2.

---

## 3. Pendientes del mensaje de Alex tras unir los PR #2 y #3

- **Fecha:** 2026-10-31
- **Herramienta:** Claude Code (app de escritorio)
- **Modelo:** Claude Opus 5.5 (`claude-opus-5-5`)
- **Para qué era:** ponerme al día con `main`, agregar las pruebas del rol a `pruebas/` (con permiso
  de Alex solo para ese archivo) y ajustar el parche de `grafo.py` antes de pasárselo a Matías.

**Prompt completo:**

````text
[adjunto: captura del mensaje de Alex con las decisiones y los pendientes de cada rol]
Sí, avanza
````

**Decisiones que tomé al responder las consultas del asistente:**

- Agregar `pruebas/probar_herramientas.py` en un PR propio, como autorizó Alex.
- Ajustar el parche para Matías: un turno sin `validar_gasto` ya no borra ni sobrescribe el veredicto
  anterior (se revisa en los mensajes del turno, sin reiniciar el estado), y si `aplicar_veredicto`
  falla por falta de saldo el gasto queda observado en vez de cortar el turno.
- La decisión escrita con asteriscos ("**Decisión:** APROBAR") sigue sin reconocerse: se resuelve con
  la salida estructurada que coordinan Matías y Eduardo.

**Resultado (una línea):** `verificar.py` 41 ✅ 0 ❌, `probar_herramientas.py` 45 ✅ 0 ❌ y 6 de 6
escenarios del parche correctos con LLM falso; el parche aplica limpio sobre `main`.

---

## 4. Política v1.2 e id_fondo inexistente

- **Fecha:** 2026-11-01
- **Herramienta:** Claude Code (app de escritorio)
- **Modelo:** Claude Opus 5.5 (`claude-opus-5-5`)
- **Para qué era:** traer a mi rama lo unido en `main` (PR #4 a #7), pasar mis archivos a la política
  v1.2 y resolver el pendiente del `id_fondo` inexistente del resumen de Alex.

**Prompt completo:**

````text
[adjuntas: capturas del grupo con el resumen de Alex tras unir los PR #4 a #7]
¿Qué debería ejecutar?
````

Después le pedí al asistente que hiciera el pull y los cambios ("Sí, hazlos").

**Decisiones que tomé al responder las consultas del asistente:**

- La regla nueva de la v1.2 (rendición anterior al gasto) ya la revisaba `validar_gasto` como RG-10:
  solo cambié las menciones a la versión y agregué una prueba.
- Un `id_fondo` inexistente queda observado por RG-10 en `validar_gasto`, que lee los fondos de
  `datos/fondos_ficticios.json` (no van copiados en el código).
- `memoria.buscar_fondo` devuelve `None` en vez de cortar el turno, y `aplicar_veredicto` y
  `resumen_fondo` aceptan `None` (sin fondo no se puede aprobar). Para cerrar el pendiente, Matías
  cambia en `grafo.py` las 2 llamadas a `fondo_inicial` por `buscar_fondo`; se lo paso como propuesta.

**Resultado (una línea):** `verificar.py` 40 ✅ 0 ❌ (1 ⚠️ porque a mi `.env` le falta `REDIS_URL`),
`probar_herramientas.py` 50 ✅ 0 ❌, y con el cambio de Matías probado en una copia, GS-01 con `FR-999`
termina en OBSERVAR y queda registrado.

---

## 5. Campos que el LLM cambió en su copia del gasto

- **Fecha:** 2026-11-01
- **Herramienta:** Claude Code (app de escritorio), con el MCP de GitKraken para leer el PR #8
- **Modelo:** Claude Opus 5.5 (`claude-opus-5-5`)
- **Para qué era:** entregarle a Matías la función que pidió para el gasto original: decir qué campos
  cambió el LLM en su copia del gasto.

**Prompt completo:**

````text
[adjunta: captura del mensaje de Matías que pide la interfaz de la función que detecta qué campos
cambió el LLM en su copia del gasto]
````

Después aprobé la implementación ("Sí, impleméntala").

**Decisiones que tomé al responder las consultas del asistente:**

- `campos_alterados(gasto_original, gasto_llm) -> list[str]` en `src/herramientas.py`: función pura,
  no es herramienta del LLM y no cambia `src/contrato.py`. Devuelve los campos cambiados, agregados o
  quitados, ordenados, y `[]` si la copia es igual.
- No avisa por diferencias de forma: ausente, `None`, `""` y `False` cuentan como vacío; los números se
  comparan por valor (`7800`, `7800.0` y `"7800"`), porque Gemini suele mandar enteros como decimales;
  los textos, sin espacios a los lados.
- La protección la hace el Núcleo, que valida siempre el gasto original (PR #8); esta función explica
  qué cambió, para la traza y como evidencia del caso adversarial del piso (GS-16 con la rendición
  adelantada: la copia pasaría y el original se rechaza por RG-03).
- Al revisar el PR #8 encontré que en GS-26 el turno 2 validaba el gasto del turno 1, porque el gasto
  original queda guardado en el hilo. Se lo paso como propuesta: a Matías, dejar `"gasto": None` en la
  entrada de cada turno, y a Alex, usar `conversar_con_caso` en el evaluador.

**Resultado (una línea):** `verificar.py` 40 ✅ 0 ❌ (1 ⚠️ por `REDIS_URL`) y `probar_herramientas.py`
56 ✅ 0 ❌ (6 pruebas nuevas en la sección G).

---

## 6. Evidencia del piso de reglas: caso normal y adversarial

- **Fecha:** 2026-11-02
- **Herramienta:** Claude Code (app de escritorio)
- **Modelo:** Claude Opus 5.5 (`claude-opus-5-5`)
- **Para qué era:** dejar la evidencia que pidió Matías de que el agente no decide por debajo de las
  reglas exactas, con un caso normal y uno adversarial.

**Prompt completo:**

````text
[adjunta: captura del grupo con el resumen de Alex y el mensaje de Matías: "Sebastián: queda
pendiente la evidencia del piso de reglas, con un caso normal y uno adversarial."]
Contexto
````

Después le pedí traer `main` a mi rama dos veces ("Sí, tráelo": 193dc59 y a92e493) y hacer la
evidencia ("ejecútalo").

**Decisiones que tomé al responder las consultas del asistente:**

- La evidencia pasa por el grafo real (`construir_agente` y `conversar_con_caso`) con un LLM guionado
  en vez de Gemini. Con Gemini real el modelo suele rechazar solo (GS-27 pasó en la prueba de Alex) y
  el piso no llega a actuar; además así no gasta cuota.
- El juez se simula en el peor caso (valida todo), para mostrar que el piso no depende de él. El
  registro usa una base temporal.
- Caso normal, GS-16: el LLM se equivoca sin ataque y propone OBSERVAR; el piso lo sube a RECHAZAR por
  RG-03 (evento `piso_reglas`).
- Control, GS-01: una aprobación correcta no se toca (sin eventos del piso).
- Caso adversarial, GS-27: el LLM obedece la glosa, adelanta la rendición en su copia y propone
  APROBAR. El grafo valida el original (`campos_alterados` = `fecha_rendicion`), bloquea la aprobación
  por RG-03, termina en RECHAZAR y no descuenta el fondo.
- Comprobé que la prueba detecta un piso roto: si `decision_sugerida` devuelve siempre aprobar, fallan
  el caso normal y el adversarial.
- Pasé la mención de versión de `src/herramientas.py` a la v1.5. La v1.5 se lee sin cambios de código
  (tope de Capacitaciones de $35.000 y comida individual en RG-02).

**Resultado (una línea):** `probar_herramientas.py` 59 ✅ 0 ❌ (3 pruebas nuevas en la sección H) y
`verificar.py` 42 ✅ 0 ❌.

---

## 7. Piso de reglas para el notebook: base temporal y caso benigno con Gemini

- **Fecha:** 2026-11-02
- **Herramienta:** Claude Code (app de escritorio)
- **Modelo:** Claude Opus 5.5 (`claude-opus-5-5`)
- **Para qué era:** dejar lista mi parte de la sección del notebook para el piso de reglas que pide
  la matriz de evidencias, y que Matías solo tenga que pegar las celdas.

**Prompt completo:**

````text
[adjunta: captura del mensaje de Alex con lo unido en main y lo que falta. Para Seba + Matías:
"Nueva sección del notebook para el guardrail "piso de reglas": usar prueba_piso_en_agente()
completa (no revisar_con_agente por separado, porque escribiría en el registro local), explicar por
qué el caso adversarial es simulado (Gemini no se equivoca a pedido) y agregar un caso benigno real
con Gemini."]
Contexto
````

Después aprobé el plan del asistente ("Sí, hazlo").

**Decisiones que tomé al responder las consultas del asistente:**

- `revisar_con_agente` registra siempre en una base temporal (`tempfile`, como el notebook en las
  secciones 7 y 8). Así ya se puede llamar sola sin tocar el registro local.
- Nueva sección I, `prueba_piso_con_gemini()`: GS-01 con Gemini y el juez reales. Pasa si Gemini
  propone APROBAR, el final es APROBAR y el piso no interviene. Solo corre con `--con-llm`, porque
  gasta cuota; si falta la clave o Redis, queda ❌ con el error en vez de cortar las pruebas.
- Probé la lógica de la sección I sin cuota, cambiando Gemini por un guion: si aprueba pasa, si
  observa falla, y sin clave falla con el mensaje.
- El notebook es de Matías: le paso como propuesta el texto y las dos celdas.
- Encontré que `verificar.py` deja una fila G-VERIF en el registro local cada vez que corre. No lo
  cambié porque es compartido.

**Resultado (una línea):** `probar_herramientas.py` 59 ✅ 0 ❌ y `verificar.py` 42 ✅ 0 ❌; la sección I
con Gemini real no se pudo ejecutar porque mi `.env` no tiene `GOOGLE_API_KEY` ni `REDIS_URL`.
