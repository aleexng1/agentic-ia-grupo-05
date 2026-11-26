# GraphRAG — issue #100

El catálogo organizacional es ficticio y **sigue pendiente de aprobación
grupal**. Se autorizó la carga de prueba, no la adopción definitiva del
catálogo ni la aprobación de gastos.

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
`PUEDE_RENDIR` y 10 `TIENE_TOPE`.

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

## Artefactos disponibles y pendientes

- **Originales disponibles:** el [catálogo ficticio](../../datos/cargos_niveles.json)
  y los [fixtures offline](../../tests/test_graphrag_eduardo.py) están en el
  repositorio. No se encontraron capturas, exportaciones o logs originales de
  AuraDB o de las cargas y recorridos en esta carpeta.
- **Nuevas pruebas de OpenCode:** regresión local con mocks, incluyendo
  `NEO4J_DATABASE`, además del flujo y el capturador. No hubo conexión a
  AuraDB ni se generaron capturas de un servicio real.
- **Pendientes:** anexar manualmente, si se conservan, las salidas sanitizadas
  del plan, ambas cargas y la comprobación de identidades; la captura de
  Neo4j Browser que muestre recorrido y conteos sin credenciales ni URI;
  y las salidas funcionales originales. Capturar por `/chat` una consulta
  distintiva por cargo con ID real, herramientas, fuente y fila de registro
  ejecutando el [capturador único](../ampliacion-rag/README.md). Coordinar con
  Alex el índice general y con el grupo la aprobación del catálogo.
