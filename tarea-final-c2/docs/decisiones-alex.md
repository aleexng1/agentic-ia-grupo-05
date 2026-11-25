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
