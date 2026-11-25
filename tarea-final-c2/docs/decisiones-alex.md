# Decisiones de Alex (router, verificador A2A, delegar_verificador y golden set)

Cada decisión con su motivo. Lo que cambia contratos está además en `contratos.md` §11
(«agregado por Alex, revisar»).

## Etapa 1: router + grafo + /chat

1. **`modelos.py` no lo toqué.** Según `reparto.md` es de Sebastián (y ya lo implementó en su rama).
   El router usa `obtener_llm()` y arma su propio respaldo con `MODELO_RESPALDO`, porque
   `with_structured_output` no se puede aplicar a un `RunnableWithFallbacks` (lo que devuelve
   `obtener_llm_con_respaldo`). Un intento por modelo, sin repetir indefinidamente.
   *Corrida con Gemini (2026-11-24):* en el `.env` local, `MODELO_PRINCIPAL=gemini-3.5-flash-lite`
   y `MODELO_RESPALDO=gemini-3.5-flash`, los dos tomados de la lista de modelos que devuelve la
   API con la clave del grupo. El respaldo es otro modelo flash real y distinto, con su propia
   cuota. El router acertó **15/15** en `CASOS_ROUTER`, en dos corridas seguidas (el umbral
   es 13/15), así que no se ajustó el prompt.
   *Dos recorridos:* `reparto.md` pide `consulta_politica` **y** `revisar_gasto`. El script ahora
   captura también `03-revisar-gasto` (gasto GS-01); `fuera_de_alcance` queda como tercer recorrido.
2. **Una falla del proveedor no se disfraza de `fuera_de_alcance`.** Solo una salida *no válida*
   del modelo cae en `fuera_de_alcance` (como pide el contrato); si Gemini no responde, la
   ejecución termina en `error` con 502 y su `id_ejecucion`.
3. **El largo del mensaje se valida en el router, antes del modelo**, y la API lo devuelve como
   422 con un mensaje en una línea (formato de errores del contrato), en vez del 422 técnico de pydantic.
4. **`fuera_de_alcance` es un texto fijo, sin LLM.** Es verdadero, no se puede manipular con un
   jailbreak y no gasta cuota.
5. **El A2A ocurre en el nodo `revisar_gasto` del grafo, antes del ReAct de Matías.** Su
   `revisar_caso` no recibe imágenes y los bytes de una boleta no deben pasar por los argumentos
   de una herramienta del LLM. El resultado del verificador se le pasa al ReAct como dato.
6. **Piso por verificación:** si la boleta no cuadra en algún campo, o no se pudo verificar, un
   «aprobar» del ReAct baja a «observar» (nunca se relaja una decisión). Si el verificador no
   responde, `estado_final = "fallback"` (§5).
7. **La imagen no entra al estado del grafo.** El checkpointer persiste el estado (en Postgres al
   desplegar); la imagen viaja en un diccionario en memoria por `id_ejecucion` y se borra al terminar.
8. **El grafo es síncrono y la API lo corre en un hilo** (`asyncio.to_thread`): el checkpointer de
   Postgres de Sebastián (`PostgresSaver`) es síncrono y no sirve con `ainvoke`.
9. **Integración con piezas de otros por su interfaz:** el grafo llama a
   `revisar_gasto.revisar_caso` (Matías), `consulta_politica.responder_consulta` (Eduardo) y
   `registro.guardar_ejecucion` / `memoria.crear_checkpointer` (Sebastián). Si todavía no existen
   o lanzan `NotImplementedError`: «Flujo <nombre> todavía no implementado» / solo log / memoria en
   el proceso. Nunca un resultado inventado.
10. **El ReAct de Matías usa el mismo checkpointer, con el hilo `<thread_id>:revisar_gasto`**, para
    no mezclar su estado con el del grafo principal.
11. **`gasto` opcional en `/chat`** (o un JSON en el texto). Los datos que faltan se piden; no se
    extraen con el LLM desde texto libre, porque eso sería inventar campos (por ejemplo el fondo).
12. **Un PR por etapa, en ramas encadenadas:** etapa 1 en `c2tf/alex-integracion`; etapa 2 en
    `c2tf/alex-verificador` (sale de la 1) y etapa 3 en `c2tf/alex-golden-set` (sale de la 2).
    Todos los PR van hacia `main` y se unen en orden (1 → 2 → 3).
13. **Sin `.env` no hay Gemini:** no copié claves de otras carpetas. Lo que necesita LLM quedó
    marcado `necesita_llm` (se salta sin clave) y las evidencias que lo necesitan, pendientes,
    con un script para generarlas.

## Etapa 2: verificador A2A + delegar_verificador

14. **Al modelo de visión no se le muestran monto, fecha, RUT ni folio declarados**: solo la imagen
    y la categoría declarada. Así no puede «leer» lo que espera ver. Esos cuatro campos los compara
    el código (normalizando RUT, fecha y folio); la categoría la juzga el modelo, porque es semántica.
15. **«Nunca adivinar» se aplica en dos capas:** el verificador pone `null` y «no» en lo que no
    lee (y si la imagen es ilegible, descarta todo lo que el modelo haya devuelto), y
    `delegar_verificador` rechaza como `respuesta_invalida` una respuesta que diga «sí» en un campo
    no leído.
    *Corrida con Gemini (2026-11-24, `gemini-3.5-flash-lite`):* las 4 boletas dieron exactamente
    el `cuadra` esperado (`evidencias/a2a/boleta-0*.md`). La ilegible (04) volvió todo en
    `null`/«no» con confianza 0, sin inventar nada. Esas evidencias reemplazan como 0,5 a la
    `00-canal-sin-gemini` (la decisión 21). El fallo controlado quedó en dos evidencias:
    `FORZAR_FALLO_A2A=1` solo en esa ejecución (el `.env` sigue en 0) y el verificador apagado
    (`sin_conexion`). Ajuste a `capturar.py`: ahora lee el log del verificador solo desde que
    empieza cada encargo. Antes, el fallo forzado mostraba las líneas de una corrida anterior de
    la misma imagen, y parecía que el encargo había llegado.
16. **La respuesta del verificador va como DataPart (JSON), no como texto.** Por eso `executor.py`
    ganó `responder_partes` (recibe todas las partes del mensaje), compatible con los agentes de texto.
17. **`cliente_a2a.enviar_partes` crea un cliente por llamada** (sin la caché global): usa
    `TIMEOUT_A2A_SEG` y las cabeceras del canal, y no depende del bucle de eventos de otra llamada
    (el grafo corre en un hilo con su propio `asyncio.run`).
18. **Las dos cabeceras a la vez** (X-API-Key provisoria + Bearer de `TOKEN_A2A` si existe): el
    cambio a `proteger_con_token_a2a` en el verificador queda en una línea, sin tocar el cliente.
19. **`tipo_fallo` en el error estructurado**, para que la resiliencia (Sebastián) y las evidencias
    distingan un timeout de un rechazo o de un verificador apagado.
20. **Pillow no va a `requirements.txt`**: solo sirve para regenerar las boletas, que ya están en el
    repo; el servicio desplegado no lo necesita.
21. **Evidencia `00-canal-sin-gemini`**: es una corrida real (dos servicios, log de ambos lados),
    pero sin Gemini el verificador no puede leer; se deja marcada como evidencia del canal y de la
    salida segura, no del 0,5. La de las 4 boletas queda pendiente, con su script.

## Etapa 3: golden set v1.0 y evaluador

22. **Los 34 casos de c1 se conservan completos** (con todos sus campos esperados) y se les suma la
    `ruta` esperada: con gasto → `revisar_gasto`; GS-28, 30, 31 y 32 → `fuera_de_alcance`;
    GS-33 → `consulta_politica`. GS-30 («borra el registro») queda fuera de alcance: el router lo
    corta antes de cualquier herramienta. GS-32 (memoria del nombre) se evalúa solo por ruta; la
    memoria en C2 es de Sebastián (`ampliacion-memoria`).
23. **Se evalúan solo ruta y decisión**, como pide la etapa. Los demás campos de c1 (política,
    cuenta, reglas, herramientas) quedan en el set como información para una versión 1.1.
24. **Cuatro resultados por turno:** acierto, fallo, **pendiente** (ruta correcta pero el flujo de
    otra persona aún no existe) y **error** (no se pudo ejecutar: proveedor, red o clave). El % es
    aciertos / (aciertos + fallos): ni los pendientes ni los errores suman o restan.
25. **Sin `GOOGLE_API_KEY` el evaluador no escribe informe:** un informe lleno de errores no es
    evidencia. `--validar` revisa el formato sin Gemini.
26. **La decisión esperada de los casos V se calculó con `validar_gasto`** (los 4 gastos cumplen la
    política) más el piso por verificación: V-01 aprobar; V-02, V-03 y V-04 observar.
27. **Los casos R del set son los mismos de `tests/test_router.py`**, y un test lo comprueba para que
    no se desincronicen.
28. **Primera corrida del evaluador con Gemini (2026-11-24):** se corrió en proceso, con el
    verificador levantado (`evidencias/ampliacion-evaluacion/informe-20261124T213858.md`). El router
    acertó las 59 rutas (59/59). Hubo 17/17 aciertos en los casos que ya se pueden evaluar y 40
    pendientes, porque `revisar_caso` y `responder_consulta` todavía no están en `main`. Se deja
    como evidencia de que el set y el evaluador funcionan, pero la corrida para la nota es la que
    se haga con #95 y el flujo de Eduardo ya unidos. Aviso: `langchain-google-genai` advierte que
    `gemini-3.5-flash-lite` *ignora* `temperature=0` (usa sus valores fijos). Por eso los
    resultados pueden variar un poco entre corridas, y el umbral del router es 13/15, no 15/15.
29. **Arreglo en `tests/test_router.py`:** ahora importa `src.comun.config` (que carga el `.env`)
    antes de su `skipif`. `test_evaluacion.py` importa `test_router` durante la recolección, antes
    que cualquier otro módulo cargue el `.env`. Por eso, en esta rama, el test del router con
    Gemini se saltaba («falta GOOGLE_API_KEY») aunque la clave estuviera en el `.env`.

## Después de unir los PR (rama `c2tf/alex-evidencias`)

30. **Una falla dentro de un flujo conserva la ruta elegida.** Antes, si el flujo lanzaba una
    excepción después del router (por ejemplo, Redis caído en `consulta_politica`), la fila iba con
    `ruta = "sin_ruta"`, y además chocaba con el CHECK de `ejecuciones`. Ahora `ejecutar` lee la ruta
    del último checkpoint (`_ruta_alcanzada`), así que `sin_ruta` queda solo para las fallas
    anteriores al router, como dice §11.1. Lo cubre una prueba nueva en `tests/test_grafo.py`.
31. **`dos-recorridos/capturar.py` muestra también el registro:** agrega `GET /registro/{id}`,
    porque la pauta pide la ruta visible en la respuesta *y en el registro*. Además lee el
    `id_ejecucion` del `detail` de un 502 y usa un `thread_id` nuevo en cada captura. La memoria
    persistente hacía que un hilo repetido siguiera la revisión anterior en 1 paso.
32. **Pruebas del grafo independientes del flujo real de Eduardo:** `tests/test_grafo.py` reemplaza
    `responder_consulta` por uno falso, porque al unir #99 dos pruebas suponían todavía el esqueleto.
33. **Corrida completa del evaluador detenida por cuota:** con todo unido, el ReAct hace varias
    llamadas por caso y la cuota de Gemini se agotó en el caso 16 de 57 (8 errores de cuota). La
    detuve para no gastar más y no guardé un informe que mediría la cuota y no al agente. Agregué
    `--pausa SEG` a `evaluar.py` para espaciar los casos en la próxima corrida.
34. **Evaluador que se puede retomar (`c2tf/alex-evaluador`):** el avance se guarda después de cada
    caso y se puede seguir con `--retomar` o `--desde`. Ante un 429 hay 2 reintentos con espera
    creciente; si sigue sin cuota, la corrida se detiene sola. El caso cortado **no se cuenta** y se
    repite entero (hilo nuevo), porque un caso de 2 turnos a medias no es comparable. El informe dice
    cuántas corridas y qué modelos lo armaron, porque mezclar modelos entre corridas cambia la lectura
    del %. El «429» se busca como código aislado, para no confundirlo con un monto o un folio.
35. **Canal A2A con `TOKEN_A2A` (`c2tf/alex-token-a2a`):** el verificador pasa a
    `proteger_con_token_a2a`, y el cliente manda **solo** el Bearer: se retira la `X-API-Key` que
    iba al verificador (decisión 18). Con el token activo, mandar la clave del servicio a otra app
    solo agregaba exposición. Si el principal no tiene `TOKEN_A2A`, no llama al verificador
    (`rechazado`, con un motivo claro), porque el encargo sería rechazado igual. En los tests se usa
    un token falso, nunca el del `.env`.
36. **`/chat` asíncrono (`c2tf/alex-chat-async`):** `POST /chat` responde 202 y el grafo corre
    en un grupo de hilos del mismo proceso, sin servicios nuevos. `?esperar=true` mantiene el modo
    síncrono para el uso local, las pruebas y el evaluador.
    - El estado y la respuesta completa se guardan en memoria, sin tocar la tabla de Sebastián
      (no admite `en_proceso` ni guarda la respuesta); queda una propuesta en contratos §11.1 bis.
    - **Tope global de 90 s.** Python no puede matar un hilo, así que a los 90 s la ejecución se
      marca «error» y su fila se registra en ese momento. Si el turno termina después, su resultado
      se descarta y su registro se ignora, porque el id es el mismo.
    - **Límite conocido:** si el ReAct termina tarde, igual registra su veredicto en `veredictos`.
      Es trabajo real, no inventado, pero `/chat` ya informó «error». Para cortarlo de verdad, el
      ReAct tendría que revisar un plazo entre pasos (propuesta para Matías).
    - El evaluador con `--url` y la captura de los dos recorridos siguen el flujo asíncrono
      (POST → 202 → `GET /registro`), para que también funcionen contra Heroku.
37. **`NIVEL_RAZONAMIENTO=minimal` en el router y el verificador (`src/comun/razonamiento.py`):**
    el principal ya no razonaba (0 tokens), así que no cambia su tiempo. El respaldo
    (`gemini-3.5-flash`) razona en `medium` por defecto, y clasificar o leer cuatro datos no lo
    necesita. No toqué `obtener_llm` (Sebastián): el nivel se fija sobre el modelo que devuelve.

## Pendientes que dependen de otros (al 2026-11-24)

- **Matías:** el ReAct registra su veredicto (`registro_veredictos`) antes de que el grafo aplique
  el piso por verificación. Si la boleta no cuadra, `/chat` responde «observar», pero el registro
  queda en «aprobar». Propuesta: que `revisar_caso` reciba el resultado del verificador y aplique
  el piso antes de registrar (o que el grafo vuelva a registrar). Comprobado con una prueba de
  integración local (grafo + ReAct real con LLM guionado + A2A real), que no se subió.
- ~~Cambiar `proteger_app` por `proteger_con_token_a2a` en `src/verificador/app.py`~~: hecho en
  `c2tf/alex-token-a2a` (decisión 35).
- **Eduardo:** `responder_consulta`. Mientras no exista, `consulta_politica` termina en «Flujo
  consulta_politica todavía no implementado» y sus casos del golden set salen como pendientes.
- **Sebastián:** `guardar_ejecucion` ya recibe las 8 columnas del contrato; con
  `ruta = "sin_ruta"` cuando el turno falla antes del router (§11.1). **Choque con #94:** su tabla
  tiene `CHECK (ruta IN (consulta_politica, revisar_gasto, fuera_de_alcance))`, así que esa fila se
  rechaza (queda solo el log de error). Comprobado con un Postgres local de prueba. Hay que elegir
  una salida: agregar `sin_ruta` al CHECK (propuesta) o que yo no guarde esas filas.
- **Matías + Sebastián:** con #94, `registrar_veredicto` exige `DATABASE_URL`. Sin ella, todo
  `revisar_gasto` que llega a un veredicto falla con 502 («Falta DATABASE_URL»). En local hay que
  tener un Postgres para correr el flujo completo y el evaluador.
- **Matías:** `revisar_caso` devuelve `estado_final = "ok"` con `veredicto = None` cuando el
  modelo cierra sin `emitir_veredicto`. En la corrida integrada pasó con V-04 (boleta ilegible).
  §8 dice que «ok» es la parada por veredicto válido.
- **Contrato §3 (después de unir):** la fila de `delegar_verificador` todavía dice «esqueleto». No
  la cambio en mi PR porque la fila de al lado la cambió #95 y habría conflicto.
- **Alex:** las evidencias con Gemini y `pytest -m necesita_llm` ya están hechas (2026-11-24).
  Falta volver a capturar `dos-recorridos/01` y volver a correr el evaluador cuando estén unidos
  #95 (Matías) y el flujo de Eduardo.
