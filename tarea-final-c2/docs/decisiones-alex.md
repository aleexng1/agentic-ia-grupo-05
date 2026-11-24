# Decisiones de Alex (router, verificador A2A, delegar_verificador y golden set)

Cada decisión con su motivo. Lo que cambia contratos está además en `contratos.md` §11
(«agregado por Alex, revisar»).

## Etapa 1: router + grafo + /chat

1. **`modelos.py` no lo toqué.** Según `reparto.md` es de Sebastián (y ya lo implementó en su rama).
   El router usa `obtener_llm()` y arma su propio respaldo con `MODELO_RESPALDO`, porque
   `with_structured_output` no se puede aplicar a un `RunnableWithFallbacks` (lo que devuelve
   `obtener_llm_con_respaldo`). Un intento por modelo, sin repetir indefinidamente.
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

## Pendientes que dependen de otros (al 2026-11-24)

- **Matías:** el ReAct registra su veredicto (`registro_veredictos`) antes de que el grafo aplique
  el piso por verificación. Si la boleta no cuadra, `/chat` responde «observar», pero el registro
  queda en «aprobar». Propuesta: que `revisar_caso` reciba el resultado del verificador y aplique
  el piso antes de registrar (o que el grafo vuelva a registrar). Comprobado con una prueba de
  integración local (grafo + ReAct real con LLM guionado + A2A real), que no se subió.
- **Matías:** cuando se una #95, cambiar `proteger_app` por `proteger_con_token_a2a` en
  `src/verificador/app.py` (el cliente ya manda el Bearer).
- **Eduardo:** `responder_consulta`. Mientras no exista, `consulta_politica` termina en «Flujo
  consulta_politica todavía no implementado» y sus casos del golden set salen como pendientes.
- **Sebastián:** `guardar_ejecucion` ya recibe las 8 columnas del contrato; con
  `ruta = "sin_ruta"` cuando el turno falla antes del router (§11.1).
- **Alex (con `GOOGLE_API_KEY`):** generar las evidencias `dos-recorridos`, `a2a` (4 boletas) y el
  informe del evaluador, y correr `pytest -m necesita_llm`.
