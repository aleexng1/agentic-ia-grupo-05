# Flujo `consulta_politica` — Eduardo

Implementado y probado offline. No se ha validado la recuperación ni la
generación con los servicios reales. No es otro agente ni un ciclo ReAct.

## Integración con el router

Alex puede llamar a `responder_consulta(texto: str, thread_id: str) -> dict`
cuando el router decide `consulta_politica`. La llamada es síncrona.
Devuelve exactamente:

```text
{"respuesta": str, "fuentes": list[str], "herramientas_usadas": list[str]}
```

El flujo valida la entrada. No usa `thread_id` como parte de la búsqueda o
del prompt, ni escribe memoria, trazas conversacionales, un identificador de
ejecución o un veredicto. Alex conserva el control de la ruta, el mapeo a
`/chat` y el registro; la memoria se integra en el grafo principal.
Si se quiere publicar `fuentes` como campo separado en `/chat`, hay que
acordarlo: ya aparecen citadas dentro de `respuesta`.

## Decisión y fundamentación

| Entrada | Qué hace el flujo |
|---|---|
| Regla explícita o formulación clara, p. ej. plazo o aprobación propia | Llama a `buscar_politica.invoke({"consulta": ..., "k": 3})` e incluye el pasaje de la regla si fue recuperado. No llama al modelo de chat. |
| Pregunta semántica sobre la política | Recupera con `k=3`; si hay pasajes candidatos, Gemini selecciona sus IDs en una única llamada estructurada. La aplicación redacta una respuesta extractiva con esos pasajes, no imprime texto generado. |
| Tope documental con categoría y contexto | Lee la sección del contexto correcto en el RAG. Por ejemplo, hotel entre sedes es P02 y hotel al visitar un proveedor es P03. Extrae el importe por documento de esa categoría. |
| Tope por cargo y categoría cualificada | Usa `tope_para` primero. Si hay recorrido, verifica cargo y nivel contra la propuesta versionada y contrasta el monto con la sección documental recuperada. Hace explícito que el vínculo organizacional es ficticio, pendiente de aprobación y no autoriza el gasto. |
| Falta categoría, cargo o contexto imprescindible | Pide el dato. No usa el cargo para adivinar la subpolítica. No elige entre P02 y P03 si la pregunta admite ambos. |
| No hay recorrido | Lo indica sin asumir que el gasto está prohibido. No afirma un tope por cargo ni hace una búsqueda documental sustitutiva. |

Cada fragmento trae `politica`, `texto`, `fuente` y `puntaje`. Se compara
el texto completo y el metadato con el fragmento que el cargador prepara
desde la copia versionada de POL-RG-01. Esa copia y el catálogo **solo
validan** lo devuelto; no se usan para fabricar un fragmento o un recorrido
cuando falta. Un índice de otra versión o fragmentación puede requerir
revisión. No se usa un corte arbitrario por puntaje ni se presupone que los
tres vecinos KNN sean pertinentes.

Para la selección semántica se descartan primero pasajes sin anclas
léxicas pertinentes; algunas preguntas, como las de patente o cuenta,
requieren además que el pasaje trate el aspecto consultado. El modelo
solo puede elegir IDs de esos pasajes o abstenerse: no elige herramientas,
no devuelve fuentes arbitrarias ni propone montos. El código valida el
esquema y la pertenencia de cada ID, y cita solo su fuente efectiva. Si una
regla general llegó dentro del fragmento `#P04`, por ejemplo, se cita
`#P04`, no una fuente individual que no se recuperó. Una cita real y una
coincidencia léxica no garantizan que el pasaje conteste toda la pregunta;
la precisión semántica requiere evaluación real.

## Seguridad y errores

- La pregunta y los pasajes entran como datos JSON separados de las
  instrucciones de sistema. Las órdenes evidentes de revelar claves,
  ignorar reglas, inventar citas o modificar registros se rechazan.
  El filtro de palabras es una primera barrera, no la única protección.
- Un fragmento alterado se descarta antes de enviarlo a Gemini; el
  nivel devuelto por el grafo no se muestra sin verificarlo. El modelo
  no recibe herramientas, credenciales ni `thread_id`. No hay Cypher
  generado ni operaciones de carga. En validación real, no habilitar
  trazas que capturen preguntas sensibles.
- Entrada inválida: `ValueError` (validación de solicitud por la API).
  Ambigüedad, falta de evidencia o recorrido ausente: respuesta explícita,
  sin fuentes ni herramientas que no correspondan.
- Fallos de RAG (Redis o embeddings), Neo4j o Gemini: `ErrorDeServicio`
  con mensaje fijo y sin detalles internos, compatible con HTTP 502.
  Una salida del modelo incompatible también produce `ErrorDeServicio`;
  una abstención válida del modelo no se trata como error.
- Ante montos que no coinciden, se indica la inconsistencia y no se
  confirma ninguno. Si Neo4j falla no se da un tope por cargo con solo
  Redis; si falta la evidencia documental pertinente tampoco se
  confirma un tope basado solo en el recorrido.
- `herramientas_usadas` enumera las búsquedas que efectivamente se
  llamaron, en orden. Gemini no es una herramienta del flujo.

## Dependencias y límites

El flujo usa `src/comun/modelos.py::obtener_llm()` y `json_schema` de
Gemini para la selección. No implementa un respaldo alternativo ni oculta
fallos con una respuesta generada localmente. Con Sebastián queda por
acordar cómo devolver un selector estructurado para ambos modelos y
comunicar a Alex el uso del respaldo (`estado_final = "fallback"`), sin
añadir unilateralmente campos al contrato. En la referencia local de su
rama, el respaldo existe como `RunnableWithFallbacks` pero no expone esa
señal ni permite aplicar `with_structured_output` después de envolver los
modelos.

La interpretación determinista cubre formulaciones frecuentes; no
resuelve todas las paráfrasis ni preguntas compuestas. Si la redacción es
ambigua, pedir por separado **un cargo**, **una categoría** y **una
política**. El catálogo GraphRAG solo cubre topes de estadía en P02 y P03
y requiere aprobación del equipo. Las consultas son de política, no
deciden si un gasto concreto se aprueba.

## Pruebas reales posteriores — sin ejecutar

Primero, con autorización, completar [la validación de Redis](../../conocimiento/rag/LECTURA.md)
y [la de Neo4j](../../conocimiento/grafo/README.md), confirmar versión del
índice, modelo de embeddings, esquema y catálogo aprobado, y usar las
cuentas de solo lectura. Luego habilitar el modelo compartido y ejecutar
la matriz con un hilo ficticio. Tras la integración de Alex, repetir por
`/chat` y conservar la respuesta, fuentes usadas y el `id_ejecucion` real
del registro, sin incluir credenciales.

| Consulta o condición | Comprobación esperada (no observada en servicios) |
|---|---|
| ¿Hasta cuándo puedo rendir un gasto? | RG-03: día 10 del mes siguiente y excepción de visto bueno escrito. Solo RAG. |
| ¿Puede quien hizo el gasto aprobar su propia rendición? | RG-04: no. Solo RAG. |
| ¿Se puede rendir un almuerzo individual en la oficina? | RG-02: gasto personal rechazado. Solo RAG. |
| ¿Qué pasa si un documento supera su tope? | RG-05: se observa y se justifica el exceso. Solo RAG. |
| ¿Qué patente exige P04 para flota? | Cita un pasaje real de P04 que respalde la respuesta. Probar el selector de Gemini sin herramientas. |
| Tope de hotel interno / para visitar a un proveedor | P02: $445.000 / P03: $325.000 CLP por documento. |
| Tope `P02:hotel` para Jefe de tienda y para Analista de Operaciones | Misma cifra documental; niveles propuestos distintos. Herramientas: `tope_para`, luego `buscar_politica`. |
| Tope `P03:hotel` para Analista de Operaciones o cargo inexistente | No hay recorrido; no deduce una prohibición ni reporta un monto. |
| Tope de hotel sin contexto; días de vacaciones | Aclaración en el primer caso; abstención sin fuentes en el segundo, aunque KNN devuelva vecinos. |
| Fallo de servicio en un entorno de ensayo autorizado | HTTP 502 al integrar la API, sin secretos ni tope atribuido a un cargo. No alterar el índice o catálogo para simular fallos. |

En offline: desde `tarea-final-c2/`, con la carga de `.env` deshabilitada,
ejecutar `python -m pytest tests/test_consulta_politica_eduardo.py`. Las
pruebas usan mocks de las búsquedas y del modelo; no son evidencia de
ejecución en Redis, Neo4j ni Gemini.
