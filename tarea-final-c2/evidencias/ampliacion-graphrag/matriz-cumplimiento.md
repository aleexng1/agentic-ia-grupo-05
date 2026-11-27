# Matriz de cumplimiento: RAG y GraphRAG

Cierre para revisión del [PR #119](https://github.com/aleexng1/agentic-ia-grupo-05/pull/119),
con base en el [commit `ede4b0e`](https://github.com/aleexng1/agentic-ia-grupo-05/commit/ede4b0e).
Fuentes: [pauta](../../docs/pauta.md),
[reparto](../../docs/reparto.md), [contrato](../../docs/contratos.md) y
[mapa de Alex](../../docs/mapa-evidencias.md). El
[issue #100](https://github.com/aleexng1/agentic-ia-grupo-05/issues/100)
no se consultó en remoto: la columna de alcance se basa en las referencias
versionadas y no certifica el estado del checklist de GitHub.

Se inspeccionaron localmente las cinco capturas sanitizadas de ejecuciones
previas. No se observaron credenciales, correos, URI de servicios ni datos
personales; los PNG no contienen bloques de metadatos ni datos tras
`IEND`. La salida no sanitizada de RAG queda excluida por `.gitignore`,
confirmado con `git check-ignore`. Estas capturas no son pruebas remotas
nuevas ni sustituyen ejecuciones de `/chat` cotejadas por ID.

El RAG documental aporta el monto normativo por documento y su cita.
GraphRAG aporta el recorrido relacional de la propuesta organizacional.
El [informe real de integridad](08-validacion-integridad-real.md) tiene
alcance anterior a la ampliación con fondos. Los resultados históricos,
las comprobaciones reales de H02/H06 y las pruebas offline se informan
por separado, sin sumar conjuntos de casos superpuestos.

| Criterio / alcance local relacionado con #100 | Entrada, ejecución y resultado disponibles | ID real | Estado y evidencia faltante |
|---|---|---|---|
| RAG documental (+0,5) / H03 | Capturas históricas: 3 resultados con fuente y puntaje (`PASS`); 2/2 respuestas documentales P02/P03 con importe, cita y `buscar_politica`. H03 validado offline; la prueba real se detuvo antes de conectar a Redis por el requisito TLS. | No | **Parcial:** falta validación real de H03 con TLS, el texto de los fragmentos y una respuesta citada de `/chat` con registro. |
| GraphRAG: carga, idempotencia e inventario (+1,0 para toda la ampliación) / H06 | H06 aprobado en Neo4j real mediante solo lectura: **24 nodos y 27 relaciones íntegros**, contrastados con el catálogo. Las dos cargas y la idempotencia `PASS` son resultados históricos informados. | No aplica a la lectura directa | **Inventario verificado:** faltan originales del plan, ambas cargas y comparación de identidades para la idempotencia. |
| GraphRAG: recorrido Cargo → Nivel → Categoría → Tope | Capturas verificadas: recorrido Jefe de tienda/Hotel (4 nodos, 3 relaciones, 105 ms) y consulta tabular (15 registros, 89 ms). CSV original intacto: 15/15 en la validación previa. | No aplica a las consultas directas de Neo4j | **Verificado en Neo4j:** la captura tabular muestra parte de las filas y no deja ver la consulta completa; el CSV conserva las filas, no la consulta. |
| GraphRAG: consulta distintiva por cargo / integración con RAG / H02 | H02: **4/4 consultas reales aprobadas** por cargo y categoría en Neo4j. Las corridas 7/7 y 5/5 son históricas; ninguna de estas pruebas se hizo por `/chat`. | No | **Pendiente en Heroku:** pregunta P03 por cargo, ruta, recorrido, fuente, resultado e ID con fila de registro. El catálogo sigue pendiente de aprobación grupal. |
| GraphRAG: ampliación con fondos | Implementada y probada offline con servicios simulados. FR-020 conserva el recorrido con el cargo compatible o sin cargo explícito; el cargo incompatible se rechaza antes de consultar Neo4j o Redis. El saldo actual se deriva al MCP. | No | **Deshabilitada:** pendientes la migración y la aprobación del catálogo. |
| Chat web y despliegue con registro (base, 0,5; chat sin puntos propios) | Capturador local revisado; la autenticación en Heroku sigue pendiente. | Pendiente | **Pendiente en esta revisión:** URL autorizada, release, `/health`, chat web con ruta/estado/`id_ejecucion`, `/registro` y log sanitizado. Coordinar con Sebastián. |

## Inventario publicable verificado

| Tipo | Archivos |
|---|---|
| Capturas sanitizadas de RAG | [`04-prueba-real-rag-pass-sanitizada.png`](../ampliacion-rag/04-prueba-real-rag-pass-sanitizada.png), [`05-consulta-politica-real-pass.png`](../ampliacion-rag/05-consulta-politica-real-pass.png) |
| Capturas sanitizadas de GraphRAG | [`03-visualizacion-grafo-neo4j.png`](03-visualizacion-grafo-neo4j.png), [`05-recorrido-cargo-tope.png`](05-recorrido-cargo-tope.png), [`07-tabla-recorridos.png`](07-tabla-recorridos.png) |
| Evidencia original tabular | [`06-recorridos-graphrag.csv`](06-recorridos-graphrag.csv) |
| Informe real de integridad | [`08-validacion-integridad-real.md`](08-validacion-integridad-real.md) |
| Documentación nueva o actualizada | [`ampliacion-rag/README.md`](../ampliacion-rag/README.md), [`ampliacion-graphrag/README.md`](README.md), `matriz-cumplimiento.md` |
| Control de publicación | [`ampliacion-rag/.gitignore`](../ampliacion-rag/.gitignore), con la exclusión exacta de la PNG original |

El capturador y los marcadores `.gitkeep` ya están versionados, sin cambios;
no forman parte de este lote ni son evidencias de ejecución.

## Resto de la pauta (referencia al mapa del equipo)

No se revalidaron evidencias de otros integrantes; los estados siguientes
son los del mapa local, no un dictamen nuevo ni una certificación remota.

| Criterio | Estado del mapa local y pendiente destacado |
|---|---|
| Router + worker + ReAct (base, 1,0) | Parcial: recapturar `consulta_politica` con Redis y los dos tipos de cierre ReAct con sus IDs y registros. |
| A2A (base, 0,5) | Parcial: falta acreditar el efecto de la verificación sobre el veredicto, con Redis y registro por ID. |
| Seguridad (base, 0,5) | Lista en local según el mapa: 401 sin clave y bloqueo sin ejecutar. La revisión de publicación de estas evidencias es un control distinto. |
| Resiliencia (base, 0,5) | Parcial: falta la falla provocada con `fallback` en el registro. |
| Golden set (+0,5) | Parcial: falta la corrida integral. |
| Memoria persistente (+0,5) | Pendiente: demostrar continuidad del hilo tras reinicio. |
| MCP (+0,5) | Lista según el mapa, todavía sin ID de la revisión. |
| n8n A2A (respaldo, +1,0) | Pendiente: caso adicional que no duplique la delegación obligatoria. |
| Entrega | Repositorio y README son referencias locales; no se verificaron el acceso al servicio ni la entrega completa del grupo. Las credenciales van fuera del repo; los extras cuentan solo con la base completa y sin doble acreditación. |

**Decisión:** las cinco capturas, el CSV, el informe real y los archivos
de documentación y control del inventario son publicables. La acreditación final sigue
pendiente de la aprobación grupal del catálogo y de las evidencias remotas
cotejadas por ID. El PR #111 queda intacto. El índice general de evidencias
sigue a cargo de Alex.
