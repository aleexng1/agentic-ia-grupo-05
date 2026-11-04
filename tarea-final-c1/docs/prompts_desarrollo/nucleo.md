# Prompts de desarrollo — Núcleo (ReAct)

Responsable: Matías Muñoz

> Registro de los prompts relevantes usados para preparar el trabajo del rol Núcleo.
> No se incluyen claves, contraseñas ni datos privados.

---

## 1. Sincronizar y proponer la siguiente tarea

- **Fecha:** 2026-10-31
- **Herramienta:** OpenCode
- **Modelo:** GPT-6 Luna Fast
- **Para qué era:** Sincronizar la rama de Matías con GitHub, revisar los cambios del proyecto y proponer el siguiente trabajo sin programar todavía.

**Prompt completo:**

````text
Necesito ponerme al día con los últimos cambios del proyecto grupal y preparar mi
siguiente tarea. No tengo mucha experiencia con Git: haz un paso a la vez, explícame cada
comando en una frase y en simple, y detente cuando necesites una decisión mía.
NO programes nada en este prompt: solo sincroniza, revisa y propón.

Proyecto: repositorio agentic-ia-grupo-05, carpeta tarea-final-c1.
Roles y ramas:
- Alex Nail → Caso y calidad → tf/caso-calidad
- Matías Muñoz → Núcleo → tf/nucleo
- Sebastián Mardones → Herramientas y estado → tf/herramientas
- Eduardo Basaure → Conocimiento y seguridad → tf/conocimiento-seguridad

PASO 1 — Sincronizar
1. Pregúntame mi nombre para saber mi rol y mi rama.
2. Entra a la carpeta del repo y muestra git status. Si tengo cambios sin guardar, NO los
   borres: dime cuáles son y pregúntame si los guardo con un commit en mi rama.
3. git fetch origin, cámbiate a mi rama (git switch <rama>), git pull y luego
   git merge origin/main. Si hay un conflicto, NO lo resuelvas: explícame qué archivos
   chocan y espera.
4. Si requirements.txt cambió, reinstala con el Python del entorno .venv.
5. Corre verificar.py desde tarea-final-c1 con el Python del entorno y explícame el
   resultado.

PASO 2 — Qué cambió para mí
1. Lee AGENTS.md, mi guía en docs/instrucciones/ y datos/politica_ficticia.md (v1.1).
2. Explícame en máximo 10 líneas qué cambió en la política v1.1 que afecte mi parte.
3. Muéstrame los avisos de MI rol (de esta lista, solo el mío):

   Herramientas y estado (Sebastián):
   - validar_gasto debe aplicar la v1.1: topes por documento y por categoría, RG-10,
     voucher solo en taxi/apps/bus, RG-03 con visto bueno → observar, RG-07, y la multa
     de P04 → observar.
   - fondo_inicial hoy devuelve siempre $200.000; debe leer datos/fondos_ficticios.json
     sin cambiar su firma.

   Conocimiento y seguridad (Eduardo):
   - PROMPT_SISTEMA está desactualizado: varias reglas observan en vez de rechazar
     (RG-03 con visto bueno, RG-05, RG-07, RG-08, RG-09, RG-10, multa de P04), y el
     motivo debe citar los códigos de regla (RG-xx o Pxx).
   - Volver a indexar la política v1.1, excluyendo la sección "Historial de cambios".
   - El caso GS-33 espera que el agente use buscar_politica.

   Núcleo (Matías):
   - Los turnos de un mismo caso del golden set van en el mismo hilo de conversación, y el
     fondo del caso (contexto.fondo) se carga antes del primer turno.
   - El golden set espera la política como código (P02); hoy el Veredicto usa el nombre.
     Está en discusión usar el código en todo el proyecto.

PASO 3 — Mis casos del golden set
1. Lee pruebas/README.md y pruebas/golden_set.json.
2. Lista los casos cuyo campo "componentes" incluye mi parte (nucleo, herramientas, memoria,
   rag o seguridad, según mi rol), con una línea cada uno: id, qué prueba y la respuesta
   esperada.
3. Explícame cuáles de esos casos dependen solo de mi trabajo y cuáles necesitan también
   el de otro compañero.

PASO 4 — Registro de prompts
1. Revisa si existe docs/prompts_desarrollo/<mi-rol>.md. Si no existe, créalo a partir de
   docs/prompts_desarrollo/_plantilla.md.
2. Pregúntame si ya usé prompts de desarrollo para mi parte. Si me acuerdo de alguno,
   ayúdame a anotarlo con la plantilla.
3. Desde ahora, cada vez que te dé un prompt importante para mi parte, recuérdame
   anotarlo ahí.

PASO 5 — Plan de mi siguiente tarea
Propón un plan corto (3 a 6 pasos) para mi próxima tarea, considerando los avisos de mi
rol y mis casos del golden set. Para cada paso indica qué archivos tocaría (solo los míos,
según AGENTS.md) y cómo sabré que está listo. Espera mi visto bueno antes de programar.

PASO 6 — Cierre
1. Si creé o cambié mi archivo de prompts, súbelo con /subir-cambios (o sigue sus pasos
   si el comando no está disponible).
2. Recuérdame cerrar y volver a abrir OpenCode (o Claude Code) dentro de tarea-final-c1,
   para que cargue la versión nueva de AGENTS.md.
````

**Resultado (una línea):** Rama `tf/nucleo` sincronizada, entorno preparado y casos del golden set revisados; el plan de implementación queda a la espera del visto bueno de Matías.

---

## 2. Preparar el entorno según el material del curso

- **Fecha:** 2026-10-31
- **Herramienta:** OpenCode
- **Modelo:** GPT-6 Luna Fast
- **Para qué era:** Preparar el entorno del proyecto siguiendo las prácticas de clase y usando el material del curso como referencia.

**Prompt completo:**

````text
acá tienes todo lo necesario para poder setear el entrono al igual como lo hemos venido haciendo en la clases con todas las buenas practicas entorno virutal, dependencias, librerias, vesiones de python, .env, .env example, estructura del proyecto, ejecución centralizada, flags, etc. Siempre consultame si lo necesitas.
esto es lo que necesitas cierto?
````

**Resultado (una línea):** Se creó `.venv` con Python 3.12.10, se instalaron las versiones de `requirements.txt`, se copió `.env.example` y `verificar.py` terminó con 41 ✅ y 0 ❌.

---

## 3. Demostrar saludo e historial en el notebook

- **Fecha:** 2026-10-31
- **Herramienta:** OpenCode
- **Modelo:** GPT-6 Luna Fast
- **Para qué era:** Aprobar e iniciar la primera tarea de Núcleo: demostrar que GS-31 responde un saludo sin herramientas y que GS-32 recuerda datos entre dos turnos del mismo hilo.

**Prompt completo:**

````text
me parece bien que avancemos con la primera tarea. apruebo el plan. Entiendo que para el resto mis compañeros tienen que desarrollar su parte para poder probar? esty bien.
no he usado otros prompts
````

**Resultado (una línea):** Se completó la celda de historial de `agente.ipynb`; GS-31 y los dos turnos de GS-32 pasaron con Gemini real sin llamadas a herramientas, y el segundo turno recordó a Pedro y su unidad; `verificar.py` pasó (41 ✅, 0 ❌).

---

## 4. Completar la comprobación segura del entorno en el notebook

- **Fecha:** 2026-10-31
- **Herramienta:** OpenCode
- **Modelo:** GPT-6 Luna Fast
- **Para qué era:** Identificar qué trabajo de Núcleo podía avanzar sin depender de otros roles y completar la comprobación segura de `.env` en el notebook.

**Prompt completo:**

````text
ok, pero si entiendo bien todas las tareas pendientes de nucleo necesitan del resto del equipo o podemos seguir avanzando?
````

**Resultado (una línea):** La sección de configuración informa modelos y presencia de variables, ocultando la clave y la URL de Redis; se validó el notebook y `verificar.py` pasó (41 ✅, 0 ❌).

---

## 5. Avanzar las tareas independientes de Núcleo

- **Fecha:** 2026-10-31
- **Herramienta:** OpenCode
- **Modelo:** GPT-6 Luna Fast
- **Para qué era:** Avanzar las partes de Núcleo que no requieren que los demás roles terminen sus componentes y preparar el mensaje de coordinación del equipo.

**Prompt completo:**

````text
quiero que avancemos en todo lo que podamos ahora y cuando terminemos de hacer todo lo que podemos hacer, redactar un mensaje de whatapp explicando todo lo que hicimos y lo que queda pendiente, que necesitamos y quien tiene que ejecutar
````

**Resultado (una línea):** El grafo guarda gasto, clasificación, validación y veredicto explícito, y ofrece `conversar_con_fondo` sin cambiar la firma de `conversar`; el notebook incluye G-001 y la comprobación segura del entorno; notebook compila y `verificar.py` pasó (41 ✅, 0 ❌). La prueba normal con herramientas reales queda pendiente porque RAG y validación siguen siendo stubs.

---

## 6. Integrar correcciones acordadas tras los PR #2 y #3

- **Fecha:** 2026-10-31
- **Herramienta:** OpenCode
- **Modelo:** GPT-6 Luna Fast
- **Para qué era:** Adaptar Núcleo a los cambios ya integrados de Herramientas y a las decisiones del equipo, sin editar módulos ajenos.

**Prompt de trabajo (redacción del registro; no confirmada como literal):**

````text
En tf/nucleo, actualiza solo src/grafo.py para:
- representar la política por código Pxx y comparar la política declarada por código;
- usar solo los fragmentos RAG del turno actual;
- no reutilizar ni sobrescribir el veredicto anterior en turnos sin una validación nueva;
- incorporar RG-08 a la observación de validar_gasto usando anexar_revision_saldo;
- aplicar el veredicto al fondo una sola vez y, si aplicar_veredicto rechaza una aprobación por falta de saldo, devolver OBSERVAR sin descontar.

Conserva las firmas públicas, el contrato compartido, el modelo y la temperatura. No modifiques PROMPT_SISTEMA ni uses salida estructurada hasta acordar con Eduardo el esquema y cómo se actualizará el LLM falso de verificar.py. Prueba los casos con fondos, turnos sin gasto y cambio de hilo; ejecuta verificar.py.
````

**Resultado (una línea):** Se implementaron los cinco puntos en `src/grafo.py`; `verificar.py` pasó (41 ✅, 0 ❌) y una prueba local sin internet confirmó códigos, RG-08, saldo, conservación del veredicto y aislamiento de fragmentos. La salida estructurada aún requiere coordinación con Eduardo.

---

## 7. Integrar la memoria y aislar el estado por turno

- **Fecha:** 2026-10-31
- **Herramienta:** OpenCode
- **Modelo:** GPT-6 Luna Fast
- **Para qué era:** Aplicar en Núcleo los cambios ya integrados de Sebastián y las decisiones de Alex, dejando documentada la coordinación pendiente con Eduardo.

**Prompt de trabajo (redacción del registro; no confirmada como literal):**

````text
En tf/nucleo, actualiza solo src/grafo.py para integrar las herramientas y memoria ya disponibles:
- canonicaliza la política declarada y la sugerida como código Pxx al guardar Clasificacion;
- limita los fragmentos RAG al turno actual;
- guarda o limpia el veredicto solo cuando hay una validación exitosa del gasto actual, y conserva el anterior en turnos sin gasto;
- añade anexar_revision_saldo al resultado de validar_gasto para que RG-08 llegue al LLM;
- después de una decisión explícita, llama aplicar_veredicto una vez; si falla por falta de saldo u otro error de fondo, fuerza OBSERVAR y no descuenta.

No cambies firmas existentes, src/contrato.py, verificar.py, PROMPT_SISTEMA, modelo ni temperatura. Coordina con Eduardo antes de implementar salida estructurada; acuerden el esquema y cómo adaptarán el LLM falso compartido. Prueba los casos de cambio de nombre/código, fragmentos de dos gastos, aprobación con saldo, gasto que excede el saldo y turno sin gasto.
````

**Resultado (una línea):** Se integraron los cambios en `src/grafo.py`; `verificar.py` pasó (41 ✅, 0 ❌) y una prueba aislada confirmó P01, RG-08, saldo, conservación del veredicto y fragmentos por turno. La salida estructurada sigue pendiente de acuerdo con Eduardo.

---

## 8. Demostrar memoria de fondos y registro SQLite en el notebook

- **Fecha:** 2026-10-31
- **Herramienta:** OpenCode
- **Modelo:** GPT-6 Luna Fast
- **Para qué era:** Completar las demostraciones independientes del notebook usando la memoria y el registro SQLite ya integrados por Sebastián, sin depender de Gemini, Redis ni tocar bases locales.

**Prompt de trabajo (redacción del registro; no confirmada como literal):**

````text
En agente.ipynb completa las secciones 7 y 8 sin modificar módulos de otros roles:
- Para GS-26, carga el fondo indicado por el contexto, valida ambos gastos con P02, incorpora RG-08 al segundo, aplica cada veredicto al mismo estado y comprueba aprobar/observar con saldo final de $20.000.
- Para el registro, usa una base SQLite dentro de un directorio temporal, demuestra inserción e idempotencia y ejecuta reiniciar_registro sobre esa base temporal; restaura siempre la ruta original.
Valida el notebook y ejecuta ambas celdas sin llamar a Gemini ni Redis.
````

**Resultado (una línea):** GS-26 produjo aprobar y luego observar por RG-08, con saldo final de $20.000; el registro insertó una vez, reconoció la repetición y reinició solo la base temporal.

---

## 9. Integrar el cierre propuesto para el grafo

- **Fecha:** 2026-10-31
- **Herramienta:** OpenCode
- **Modelo:** GPT-6 Luna Fast
- **Para qué era:** Integrar la propuesta de Sebastián sobre el nodo de cierre sin reemplazar las correcciones existentes de política por código, fragmentos por turno y estado del veredicto.

**Prompt de trabajo (redacción del registro; no confirmada como literal):**

````text
Integra manualmente en src/grafo.py el flujo de cierre propuesto por Sebastián, conservando los cambios actuales de Núcleo:
- tras una decisión explícita y una validación exitosa del turno, aplica el piso de decision_sugerida, llama a juzgar, actualiza el fondo y registra el veredicto;
- nunca registra APROBAR si validar_gasto devolvió incumplimientos, aunque el sugeridor de decisión falle;
- si RG-08 u otro error impide aprobar, transforma la decisión en OBSERVAR, conserva el saldo y muestra el motivo;
- no cierres ni registres turnos sin validar_gasto; preserva el veredicto anterior en esos turnos;
- conserva la política canónica Pxx y limita los fragmentos RAG al turno actual.
Mantén las firmas existentes y no edites módulos ajenos. La salida estructurada queda pendiente de coordinación con Eduardo. Prueba GS-26 con LLM falso y base SQLite temporal, y ejecuta verificar.py.
````

**Resultado (una línea):** El parche no aplicó directamente porque se basaba en una versión anterior; se integró manualmente. GS-26 pasó con segundo gasto observado por RG-08, saldo sin sobregiro y registro idempotente; el cierre bloquea aprobaciones con incumplimientos; `verificar.py` pasó (41 ✅, 0 ❌).

---

## 10. Cerrar con la herramienta estructurada `emitir_veredicto`

- **Fecha:** 2026-11-01
- **Herramienta:** OpenCode
- **Modelo:** GPT-6 Luna Fast
- **Para qué era:** Eliminar la dependencia del texto libre de Gemini para guardar y cerrar el veredicto.

**Prompt de trabajo (redacción del registro; no confirmada como literal):**

````text
En tf/nucleo, usa emitir_veredicto(decision, politica, categoria, cuenta, motivo) como la única vía estructurada para cerrar un gasto.
- Mantén el contrato Veredicto existente: decision, motivo, politica_sugerida, categoria_sugerida y cuenta_sugerida; normaliza la política a Pxx.
- Conserva en el estado el Gasto original recibido por el caso; antes de ejecutar validar_gasto, reemplaza cualquier copia alterada en los argumentos de la herramienta por ese original.
- Tras validar_gasto, el LLM debe llamar emitir_veredicto; captura su ToolMessage y enrútalo directamente a nodo_cerrar, sin interpretar la decisión desde texto.
- nodo_cerrar debe conservar el piso de reglas, el candado, el juez, el fondo y SQLite; no registres un turno sin validación exitosa.
- El LLM falso de verificar.py también debe cerrar mediante emitir_veredicto.
No cambies src/contrato.py ni PROMPT_SISTEMA; coordina con Eduardo la instrucción del prompt y con él/Alex la entrada de validación al juez. Conserva modelo y temperatura. Ejecuta verificar.py sin servicios y reporta por separado las pruebas reales pendientes.
````

**Resultado (una línea):** `emitir_veredicto` se integró en el grafo y el LLM falso ya lo llama; una prueba confirmó que validar_gasto y SQLite usan el gasto original pese a cambios propuestos por el LLM; `verificar.py` pasa con 41 ✅ y 0 ❌ en modo aislado. La llamada real de Gemini queda pendiente de que Eduardo actualice PROMPT_SISTEMA; el juez aún requiere recibir también la validación.

---

## 11. Manejar fondos inexistentes sin detener el turno

- **Fecha:** 2026-11-01
- **Herramienta:** OpenCode
- **Modelo:** GPT-6 Luna Fast
- **Para qué era:** Integrar el nuevo `buscar_fondo` de Sebastián para que un `id_fondo` inexistente se observe por RG-10 y se registre sin tumbar el grafo.

**Prompt de trabajo (redacción del registro; no confirmada como literal):**

````text
En tf/nucleo, sustituye en src/grafo.py las llamadas a fondo_inicial por buscar_fondo en la carga del fondo tras validar_gasto y en nodo_cerrar. Trata un resultado None como fondo inexistente: validar_gasto debe aportar RG-10, aplicar_veredicto no debe aprobar ni descontar, y el registro debe guardar OBSERVAR sin lanzar excepción. No modifiques src/memoria.py ni otros archivos de Sebastián. Verifica con un caso de fondo inexistente y ejecutar verificar.py.
````

**Resultado (una línea):** El grafo ahora usa `buscar_fondo`; FR-999 termina observado por RG-10, conserva fondo `None` y queda registrado sin error. `verificar.py` pasó con 41 ✅ y 0 ❌ en modo aislado.

---

**Nota de literalidad:** Las entradas 6 a 11 contienen prompts de trabajo redactados en el registro; no puedo confirmar que sean transcripciones exactas de los mensajes originales. Se rotularon para no presentarlos como literales. Si la pauta exige el texto original palabra por palabra, Matías debe aportar las conversaciones originales.

---

## 12. Filtro seguro por turno y evidencia en el notebook

- **Fecha:** 2026-11-02
- **Herramienta:** OpenCode
- **Modelo:** GPT-6 Luna Fast
- **Para qué era:** Atender el nuevo pendiente de Alex para Núcleo, cubrir cualquier respuesta final sin veredicto válido y mostrar la acción del registro desde el flujo real del agente.

**Prompt exacto de Matías:**

````text
escribió esto Alex, que tengo que decir y que podemos hacer? es necesario hacer algo de inmediatto?
````

**Extracto literal del encargo de Alex:**

````text
🔴 Matías: en docs/prompts_desarrollo/nucleo.md, la entrada nueva dice "resumen fiel de la
solicitud". La pauta pide adjuntar los prompts: pega el texto exacto.

🔴 Matías — PR corto:
- Filtro por turno: si el turno trae un gasto y no hubo un emitir_veredicto válido,
  reemplazar el mensaje final completo por una respuesta segura, diga lo que diga. Hoy
  el filtro de frases deja pasar 11 de 15 variantes ("*Decisión:* APROBAR",
  "Apruebo este gasto"…). Esto puede costar los 0,5 de seguridad en la prueba de jailbreak
  del revisor.
- Notebook: la sección 8 debe mostrar el registro antes/después desde una corrida del
  agente (no llamando directo a registrar_veredicto). La sección 10 debe usar evaluar()
  y mostrar_tabla() de pruebas/evaluar.py.
- Actualizar docs/prompts_desarrollo/nucleo.md.

🟠 PARA ACORDAR (respondan 👍 o 👎): subir MAX_PASOS de 6 a 10 (src/contrato.py,
compartido; lo aplica Matías).

Autorización posterior de Alex: "dale nomás Matías con los 10 y el PR con el MAX_PASOS modificado".
````

**Resultado (una línea):** Tras el acuerdo de Alex y el voto 👍 de Matías, `MAX_PASOS` quedó en 10 y su comprobación del contrato se actualizó. El filtro bloqueó 15/15 variantes sin veredicto; la sección 8 mostró el antes/después de SQLite desde el cierre del agente y la sección del golden llamó `evaluar()`/`mostrar_tabla()` con GS-07. Pasaron las pruebas offline; no se usó Gemini ni Redis.

---

## 13. Completar evidencias pendientes del notebook

- **Fecha:** 2026-11-02
- **Herramienta:** OpenCode
- **Modelo:** GPT-6 Luna Fast
- **Para qué era:** Avanzar las secciones de Núcleo identificadas en la matriz de evidencias, sin ejecutar corridas reales ni tocar trabajo de Eduardo.

**Extracto literal del pedido de Núcleo:**

````text
Matías (notebook):
- Sección 5 (seguridad): GS-27 a GS-30 y un intento de jailbreak por chat.
- Sección 6 (RAG): cuándo busca y cuándo no, configuración del índice y fragmentos
  usados.
- Sección 9 (juez): modelo, prompt, un veredicto benigno, uno adversarial y la decisión
  aplicada.
- Sección 8: restaurar la demostración del reinicio seguro del registro (se perdió al
  pasarla a una corrida real).
- Que las trazas de registrar_traza se vean en el notebook (hoy figura como stub).
- ¿Puedes confirmar si las entradas 6 a 11 de nucleo.md son textos exactos o resúmenes?

Seba + Matías:
- Nueva sección del notebook para el guardrail "piso de reglas": usar
  prueba_piso_en_agente() completa (no revisar_con_agente por separado, porque escribiría
  en el registro local), explicar por qué el caso adversarial es simulado (Gemini no se
  equivoca a pedido) y agregar un caso benigno real con Gemini.

Eduardo:
- Pasarle a Matías el contenido para las secciones 6 (RAG) y 9 (juez).
````

**Resultado (una línea):** Se implementaron localmente las secciones 5, 8 y 10 y se integraron las demos offline de Eduardo para 6 y 9; las celdas 6 y 9 pasaron contra el código de su rama Draft, sin Redis ni Gemini. La traza de la sección 3 y el reinicio temporal de SQLite se probaron con LLM falso; el piso completo pasa con LLM guionado. La evidencia real de RAG, el falso negativo real de GS-01 y el jailbreak por chat siguen pendientes. No se usó Gemini ni Redis.

---

## 14. Preparar el notebook para la evidencia final v1.6

- **Fecha:** 2026-11-03
- **Herramienta:** OpenCode
- **Modelo:** GPT-6 Luna Fast
- **Para qué era:** Integrar en el notebook las demos técnicas recibidas de Eduardo, actualizar la rama con `main`/PR #33 y dejar preparadas las pruebas reales solicitadas por Alex sin ejecutar llamadas ni tocar Redis antes de la coordinación.

**Prompt exacto de Matías:**

````text
avanza en todo lo que podamos y tenga sentido
````

**Instrucciones de integración de Alex (extracto literal):**

````text
Matías — notebook: trae main antes de tocarlo (cambió la celda 1, ahora dice v1.6).
Las secciones 5, 6 y 9 necesitan evidencia REAL:
- 5: GS-27 a GS-30 y un jailbreak por chat con Gemini (respuesta, veredicto, registro).
- 6: configuración del índice, una búsqueda real con sus fragmentos (GS-07) y un caso
  que no busca (GS-31).
- 9: modelo y PROMPT_JUEZ, un veredicto benigno (GS-01) y uno adversarial (GS-34), con
  valido, la razón y la decisión aplicada.
Las demos simuladas de Eduardo pueden ir al lado, rotuladas como simuladas. Con el #33
unido, ya puedes armar la sección del guardrail con prueba_piso_con_gemini().

Entrega del notebook: la pauta pide "trazas de ejecución". Como nbstripout borra las
salidas, entregaremos agente.ipynb limpio (para que el revisor lo ejecute) y
agente_ejecutado.ipynb con salidas, revisado para que no tenga secretos.
````

**Resultado (una línea):** La rama se actualizó a `main` 3efd17e, que contiene PR #33, PR #41, la corrida 3 y política v1.6. Se prepararon las pruebas dirigidas reales, pero para ahorrar cuota el notebook presenta primero la evidencia histórica auténtica de corrida 3 y PR #41; las nuevas corridas de RAG/seguridad están desactivadas y claramente rotuladas. Las secciones históricas 5/6/9 y la sintaxis del notebook pasan offline. `verificar.py` 42/42, `probar_herramientas.py` 59/59 y `evaluar.py --autoprueba` 89/89. No se usó Gemini ni Redis.

---

## 15. Dejar listas las evidencias del notebook sin repetir la corrida final

- **Fecha:** 2026-11-04
- **Herramienta:** OpenCode
- **Modelo:** GPT-6 Luna Fast
- **Para qué era:** Preparar el PR de Núcleo con las celdas de evidencia del notebook, reutilizando la corrida final ya publicada para no volver a gastar cuota.

**Prompt exacto de Matías:**

````text
dejemos todo listo para que el lo termine
````

**Instrucciones pertinentes de Alex (extracto literal):**

````text
El revisor ejecutará el notebook desde cero y verificará la traza del LLM, la
herramienta, el historial y la parada. La evidencia de seguridad, RAG, juez, guardrail
y acción tiene que estar en el notebook, no solo en los archivos de resultados.

Orden: secciones del notebook → ejecución completa → agente_ejecutado.ipynb → cierre
de documentación.

⚠️ La ejecución completa del notebook usa Gemini real: avísenme antes de correrla
completa, para coordinar la cuota.
````

**Resultado (una línea):** Se añadió lectura etiquetada de la corrida 3 (34/34) y los dictámenes reales de PR #41 para GS-01/GS-29; se muestran respuestas, herramientas, fuentes RAG, `valido`, razones, decisión aplicada y jailbreak histórico. Se resumió la traza, se quitó la ruta absoluta y se hizo idempotente la demostración de reinicio. Celdas históricas 5/6/9 pasaron offline; no se repitió ninguna llamada de API. El notebook ejecutado queda pendiente de autorización de Alex.

---

## Estado de prompts de implementación

`src/` está congelado desde la corrida 3 (34/34). El notebook ejecuta en vivo, con Gemini y Redis, las secciones 3 a 11, incluidas la 5 (seguridad), la 6 (RAG) y la 9 (juez), que completó Alex en los PR #46, #48 y #49; la evidencia guardada de la corrida 3 queda como respaldo. `agente_ejecutado.ipynb` tiene la ejecución completa de arriba abajo (42 ✅, 0 ⚠️, 0 ❌). `MAX_PASOS` quedó en 10. Nunca se registra el contenido de `.env` ni una clave. (Actualizado por Alex el 04-11; las entradas de prompts son de Matías y no se modificaron)
