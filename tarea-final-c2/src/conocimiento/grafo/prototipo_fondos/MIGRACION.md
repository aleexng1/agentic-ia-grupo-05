# GraphRAG con fondos: integración y validación pendiente

La extensión incorpora un adaptador de **solo lectura** (`../fondos.py`) y un ejecutor
separado para la migración (`migrar.py`). La capacidad de chat se entrega **deshabilitada**:
`CONSULTA_FONDOS_HABILITADA = False`. La demostración `demo.py` sigue siendo local; su salida
no acredita que el vínculo exista en Neo4j.

## Fuentes y alcance

| Aporte | Fuente | Resultado esperado para FR-020 y P03:hotel |
|---|---|---|
| RAG documental | `datos/politica_ficticia.md#P03`, POL-RG-01 v1.6; el fragmento recuperado debe coincidir con el Markdown versionado | Tope de **$325.000 CLP por documento**. El documento no vincula el fondo con un cargo. |
| GraphRAG | Neo4j: vínculo académico de la extensión y catálogo organizacional v1 | **FR-020 → Jefe de tienda → Jefatura → P03:hotel → Tope** (`tope:POL-RG-01:1.6:P03:hotel`). La propuesta de vínculo se define explícitamente en la extensión; el responsable del JSON no la demuestra. |
| Referencia ficticia y comparación | `datos/fondos_ficticios.json`, v1.0, más comparación de enteros | El tope supera el saldo inicial ficticio de **$20.000 CLP**. El saldo operativo corresponde al MCP. |

El recorrido no modifica el tope por nivel y no emite veredictos ni autoriza gastos.
El chat solo compara montos tras validar el recorrido y contrastarlo con RAG. El alta
no guarda saldos en Neo4j.

## Procedimiento para una futura migración autorizada

1. Acordar el catálogo de la extensión y el vínculo con Alex, Matías y Eduardo, y coordinar
   con el operador de Neo4j. Probar primero en una base de ensayo autorizada. Mantener
   el interruptor deshabilitado durante el alta.
2. Desde `tarea-final-c2/`, con el entorno Python del proyecto, configurar en el proceso
   `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` y `NEO4J_DATABASE` mediante el mecanismo
   aprobado para secretos. El CLI no lee `.env`. Confirmar el destino exacto
   `esquema://host:puerto/base`. Usar una credencial de lectura para `--verificar` y la app;
   debe poder ver el inventario base y las aristas incidentes a la extensión. Reservar
   una credencial de escritura para el operador.
3. Reservar una ventana **con un único escritor**: no ejecutar dos altas/bajas ni otras
   escrituras sobre el catálogo o la extensión en paralelo. Guardar la salida de la
   verificación previa y posterior. El alta/baja valida dentro de una transacción el
   inventario v1 completo (24 nodos, 27 relaciones, identidades, propiedades, fuentes y
   huella), el inventario de la extensión y el recorrido P03:hotel cuando está instalado.
   Solo confirma si el estado posterior es exacto. Repetir el alta sobre la extensión
   íntegra o la baja sobre un espacio vacío es un no-op.

```powershell
python -m src.conocimiento.grafo.prototipo_fondos.migrar --plan

# Solo tras la autorización y apuntando al destino aprobado:
$destino = 'neo4j+s://host-autorizado:7687/neo4j'
python -m src.conocimiento.grafo.prototipo_fondos.migrar --verificar ausente --confirmar-destino $destino
python -m src.conocimiento.grafo.prototipo_fondos.migrar --aplicar --confirmar-destino $destino
python -m src.conocimiento.grafo.prototipo_fondos.migrar --verificar instalada --confirmar-destino $destino
```

Si el alta ya fue confirmada y se está reintentando, usar `--verificar instalada` para
comprobar su estado. Ante una diferencia, no continuar a la activación. Tras la
aprobación y la comprobación de la carga, habilitar `CONSULTA_FONDOS_HABILITADA`
en el código de la versión autorizada y desplegarla. No hay una variable de entorno
que active el código entregado.

Para revertir, desplegar primero la versión con el interruptor deshabilitado en todas
las instancias. En la ventana de un único escritor:

```powershell
python -m src.conocimiento.grafo.prototipo_fondos.migrar --verificar instalada --confirmar-destino $destino
python -m src.conocimiento.grafo.prototipo_fondos.migrar --revertir --confirmar-destino $destino
python -m src.conocimiento.grafo.prototipo_fondos.migrar --verificar ausente --confirmar-destino $destino
```

La baja solo borra el vínculo y nodo exactos, con `DELETE` sin `DETACH DELETE`.
Si aparece una arista adicional o cualquier discrepancia, se cancela la operación.
La extensión no crea esquema ni reescribe nodos, aristas o huellas de v1.

## Evidencia offline

`test_graph_agrega_recorrido_que_no_da_rag_documental` compara dos respuestas con
la misma sección P03 recuperada de forma simulada a partir del Markdown: ambas
citan el mismo tope; solo la segunda muestra las cuatro relaciones del recorrido
de Neo4j simulado y la comparación con el saldo inicial del JSON real de prueba.
`test_chat_preserva_contrato_e_id_ejecucion` verifica el identificador y el estado
en `/chat` con router y registro simulados. Estos resultados no son evidencia de
una ejecución contra los servicios reales.

```powershell
$env:PYTHON_DOTENV_DISABLED = '1'
python -m pytest -q tests/test_graphrag_fondos_eduardo.py tests/test_prototipo_fondos_eduardo.py
```

## Aceptación futura por `/chat`

Usar el servicio autorizado con autenticación funcional y Redis/embeddings disponibles
para los casos que requieren RAG. Enviar `texto`, sin imagen ni `gasto`, con un hilo nuevo
por caso. La clasificación del router real y la respuesta del servicio se deben observar.

| Caso | `texto` de ejemplo | Resultado esperado |
|---|---|---|
| Control RAG | ¿Cuál es el tope P03:hotel? | $325.000 y fuente P03; `buscar_politica`, sin recorrido de fondo. |
| Aporte GraphRAG | ¿Qué recorrido de la política conecta FR-020 con el tope P03:hotel y cómo se compara con su saldo inicial ficticio? | Recorrido completo, tope $325.000, saldo inicial $20.000; `recorrido_fondo` y `buscar_politica`. |
| Sin vínculo | Según la política, ¿qué vínculo tiene FR-001 con Jefe de tienda para el tope P03:hotel? | Ausencia controlada de vínculo, sin atribuirle cargo. |
| Fondo desconocido | ¿Cuál es el tope de la política P03:hotel para FR-999? | Fondo no encontrado en la referencia ficticia. |
| Ambigüedad | ¿Cuál es el tope de hotel según la política para FR-020? | Solicita P02 (viaje interno) o P03 (viaje externo). |
| Por cargo | ¿Cuál es el tope P03:hotel para Jefe de tienda? | Consulta tradicional por cargo; `tope_para` y `buscar_politica`. |
| Saldo operativo | En la consulta de política de FR-020 y P03:hotel, ¿cuál es el saldo actual del fondo? | Remite al MCP, sin presentar saldo inicial como actual. |
| Alterado o ausente | Repetir el caso «Aporte GraphRAG» con una réplica de ensayo alterada o sin la extensión y el interruptor habilitado. | Ejecución en `error`, sin monto ni recorrido afirmado. |
| Neo4j no disponible | Repetir «Aporte GraphRAG» con la conexión a Neo4j indisponible en ensayo. | Ejecución en `error`, sin relaciones inventadas. |
| Interruptor apagado | Repetir «Aporte GraphRAG» antes de habilitar. | Informa que la capacidad aún no está habilitada. |

Ejemplo de captura asíncrona (inyectar la clave en el proceso por el mecanismo aprobado):

```powershell
$base = 'https://servicio-autorizado'
$headers = @{ 'X-API-Key' = $env:API_KEY_SERVICIO }
$body = @{ texto = '¿Qué recorrido de la política conecta FR-020 con el tope P03:hotel y cómo se compara con su saldo inicial ficticio?' } | ConvertTo-Json -Compress
$aceptada = Invoke-RestMethod -Method Post -Uri "$base/chat" -Headers $headers -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($body))
$aceptada.id_ejecucion
Invoke-RestMethod -Uri "$base$($aceptada.consultar)" -Headers $headers
```

Repetir `GET /registro/{id_ejecucion}` hasta que termine. Guardar por caso la entrada,
`id_ejecucion`, `ruta`, `estado_final`, `herramientas_usadas`, respuesta o `detail`, y
las citas visibles. Para el contraste RAG/GraphRAG, conservar ambos registros del
mismo entorno y resaltar el recorrido que solo aparece en la segunda respuesta.
Los resultados de ensayo alterado o desconectado se identifican como tales.
No hay `id_ejecucion` reales de esta extensión en esta entrega.
