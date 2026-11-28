# GraphRAG — issue #100

El catálogo organizacional es ficticio y **sigue pendiente de aprobación
grupal**. Se autorizó la carga de prueba, no la adopción definitiva del
catálogo ni la aprobación de gastos.

## Cierre para revisión — PR #119

Base del cierre: [commit `ede4b0e`](https://github.com/aleexng1/agentic-ia-grupo-05/commit/ede4b0e)
del [PR #119](https://github.com/aleexng1/agentic-ia-grupo-05/pull/119).
El [informe real del 27-11-2026](08-validacion-integridad-real.md) respalda
H06 (inventario íntegro de **24 nodos y 27 relaciones**, verificado en
Neo4j en solo lectura) y H02 (**4/4 consultas reales aprobadas**). Esa
ejecución directa fue anterior a la ampliación con fondos y no pasó por
`/chat`. Las corridas históricas del 25-11 se conservan por separado.

El [RAG documental](../ampliacion-rag/README.md) respalda el monto por
documento y su fuente. GraphRAG aporta la existencia del recorrido
Cargo → Nivel → Categoría → Tope en la propuesta organizacional.
La ampliación Fondo → Cargo → Nivel → Categoría → Tope está implementada
y probada offline con servicios simulados. La consulta con FR-020
conserva el recorrido cuando no se indica cargo o se pide Jefe de tienda;
si se pide Analista de Operaciones, informa incompatibilidad sin consultar
Neo4j ni Redis. El saldo inicial ficticio proviene de la referencia
versionada; el saldo actual corresponde al MCP.

La ampliación sigue deshabilitada: quedan pendientes la
[migración](../../src/conocimiento/grafo/prototipo_fondos/MIGRACION.md) y
la aprobación grupal del catálogo. La autenticación en Heroku sigue
pendiente, al igual que la evidencia con `id_ejecucion` real.

## Resultados reales históricos, informados por el operador (25-11-2026)

AuraDB Free Instance01: TLS y autenticación verificados, base inicialmente
vacía. Se aplicó la selección de base configurable con `NEO4J_DATABASE` y se
aprobó el plan offline. Resultado informado:

| Carga | Nodos | Relaciones | Duración |
|---|---:|---:|---:|
| Primera carga real | 24 | 27 | 5.521 s |
| Segunda carga, con comprobaciones | 24 | 27 | 8.314 s |

Las identidades lógicas de nodos y relaciones fueron iguales; no se crearon
nodos ni relaciones nuevos en la segunda carga. Idempotencia: **PASS**.
La visualización real mostró 15 recorridos, 24 nodos y 27 relaciones:
2 cargos, 2 niveles, 10 categorías y 10 topes; 2 `TIENE_NIVEL`, 15
`PUEDE_RENDIR` y 10 `TIENE_TOPE`. El operador informó además una
consulta visual específica (4 nodos, 3 relaciones, 105 ms) y una
consulta tabular (15 recorridos, 89 ms). El CSV permite comprobar las
filas, pero no contiene la consulta ejecutada, el tiempo ni los conteos
de Neo4j.

### Pruebas funcionales GraphRAG

| Caso | Cargo | Entrada | Resultado informado | Estado | Tiempo (s) |
|---|---|---|---|---|---:|
| G01 | Jefe de tienda | P02:hotel | 445000 CLP, Jefatura | PASS | 3.083 |
| G02 | Jefe de tienda | P03:hotel | 325000 CLP, Jefatura | PASS | 2.819 |
| G03 | Analista de Operaciones | P02:hotel | 445000 CLP, Profesional | PASS | 2.753 |
| G04 | Analista de Operaciones | P03:hotel | Sin recorrido | PASS | 2.725 |
| G05 | Jefe de tienda | Hotel sin política | Solicitud de aclaración | PASS | 2.601 |
| G06 | Cargo inexistente | P02:hotel | Sin resultado | PASS | 2.507 |
| G07 | Jefe de tienda | P02:taxi | Sin resultado | PASS | 2.564 |

Total informado: **7/7 PASS, 19.054 s**.

### Integración real RAG + GraphRAG

| Caso | Consulta de tope de hotel | Resultado y fuente informados | Herramientas | Estado | Tiempo (s) |
|---|---|---|---|---|---:|
| I01 | Jefe de tienda, P02 | 445000 CLP, Jefatura; `datos/politica_ficticia.md#P02` | `tope_para`, `buscar_politica` | PASS | 6.322 |
| I02 | Jefe de tienda, P03 | 325000 CLP, Jefatura; `datos/politica_ficticia.md#P03` | `tope_para`, `buscar_politica` | PASS | 3.517 |
| I03 | Analista de Operaciones, P02 | 445000 CLP, Profesional; `datos/politica_ficticia.md#P02` | `tope_para`, `buscar_politica` | PASS | 3.469 |
| I04 | Analista de Operaciones, P03 | Sin recorrido; no implica prohibición normativa | `tope_para` | PASS | 2.778 |
| I05 | Jefe de tienda, sin política | Solicitud de aclaración P02/P03, sin fuentes | Ninguna | PASS | 0.0 |

Total informado: **5/5 PASS, 16.088 s**. Pruebas directas de
`responder_consulta`, **no** ejecuciones por `/chat`. No hay IDs de API para
estas pruebas. Regresión histórica informada: **245 pruebas propias aprobadas**
(225 existentes y 20 para `NEO4J_DATABASE`), **10.72 s**.

Los totales de tiempo de las tablas son históricos: la suma de las filas
mostradas da 19,052 s (G) y 16,086 s (I), 2 ms por debajo de cada total
informado. Sin trazas originales no se puede atribuir la diferencia.

## Evidencias de ejecuciones previas verificadas localmente

| Archivo | Tipo y alcance |
|---|---|
| [`03-visualizacion-grafo-neo4j.png`](03-visualizacion-grafo-neo4j.png) (164 947 B) | Vista global de Neo4j: 24 nodos, 27 relaciones y 15 recorridos devueltos. Muestra el estado del grafo, no las operaciones de carga. |
| [`05-recorrido-cargo-tope.png`](05-recorrido-cargo-tope.png) (143 863 B) | Recorrido Jefe de tienda → Nivel → Hotel → Tope por documento: 4 nodos, 3 relaciones y 1 registro, completado en 105 ms. No muestra el importe en la vista de grafo. |
| [`06-recorridos-graphrag.csv`](06-recorridos-graphrag.csv) (1 877 B) | Original tabular con los 15 caminos de la propuesta. No incluye la consulta ni IDs de `/chat`. |
| [`07-tabla-recorridos.png`](07-tabla-recorridos.png) (207 336 B) | Vista tabular de Neo4j con siete columnas y una muestra visible de las filas; el pie indica 15 registros y 89 ms. La consulta está truncada en la captura; el CSV contiene las 15 filas. |
| [`08-validacion-integridad-real.md`](08-validacion-integridad-real.md) | Informe real posterior de H02 y H06 en Neo4j, anterior a la ampliación con fondos. |
| [`matriz-cumplimiento.md`](matriz-cumplimiento.md) | Consolidación local de la pauta y de las referencias al issue #100. |
| `README.md`, `.gitkeep` | Documentación y marcador de directorio. |

Las tres capturas muestran el esquema y datos ficticios, sin credenciales,
correos, URI de conexión ni datos personales visibles. Solo contienen
bloques `IHDR`, `IDAT` e `IEND`, sin datos finales adicionales. No acreditan
las dos cargas, su idempotencia ni las pruebas funcionales o de integración.

**Validación previa con Python: 15/15 correctos.** En esta revisión no se
repitió; solo se comprobó que el SHA-256 del CSV no cambió durante la
actualización documental. En la validación previa se leyó el CSV en UTF-8 con
`csv.reader(strict=True)` y se comparó el conjunto completo de filas con
el producto cargo → nivel → categorías elegibles del
[catálogo](../../datos/cargos_niveles.json). Los 10 pares política/categoría
y sus montos se contrastaron de forma independiente con la
[política POL-RG-01 v1.6](../../datos/politica_ficticia.md) (P02 y P03).
Los siete campos son consistentes, sin duplicados por fila ni por
`Cargo + Politica + Categoria`, sin faltantes ni sobrantes.

| Política | Desayuno | Almuerzo | Cena | Hotel | Hostal |
|---|---:|---:|---:|---:|---:|
| P02 | 10 000 | 20 000 | 45 000 | 445 000 | 295 000 |
| P03 | 20 000 | 45 000 | 50 000 | 325 000 | 265 000 |

Montos en CLP por documento. Hay 5 filas P02 de Analista de Operaciones
(Profesional), 5 P02 y 5 P03 de Jefe de tienda (Jefatura). `Fuente`
identifica el archivo y la sección de la política; `Estado` coincide con
la propuesta pendiente en todas las filas. El monto no varía por nivel:
el grafo aporta la existencia del recorrido. No tener recorrido de
Analista en P03 no significa prohibición normativa. No se detectaron
credenciales, correos, URI de servicios ni datos personales en el CSV.

**Pendiente documental:** originales sanitizados del plan, ambas cargas y
comparación de identidades para la idempotencia; consulta tabular completa
sin truncar y trazas originales 7/7 y 5/5, si se conservan.

**Pendiente en Heroku:** capturar `/chat` por cargo con ID real, herramientas, fuente y fila de
registro con el [capturador compartido](../ampliacion-rag/README.md). Para
mostrar que el cargo distingue el recorrido y no el monto, el caso positivo
de Jefe de tienda para P03 se puede acompañar con el caso de contraste
Analista de Operaciones para P03, que el capturador no envía.
Coordinar el índice general con Alex y la aprobación del catálogo con el grupo.
