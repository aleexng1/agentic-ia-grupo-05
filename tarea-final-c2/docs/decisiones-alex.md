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
