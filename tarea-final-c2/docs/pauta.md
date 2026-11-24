# Pauta de la tarea final (resumen)

Resumen para el grupo y para los agentes que programan (Claude Code, OpenCode). Dice **qué hay
que lograr para la nota**. Quién hace cada parte: [reparto.md](reparto.md). Cómo se conectan las
piezas: [contratos.md](contratos.md).

## Base: nota 4,0

Todos los criterios de la base son obligatorios.

| Criterio | Puntos | Qué tiene que pasar | Evidencia en |
|---|---|---|---|
| Router + worker + ReAct con parada explícita | 1,0 | El agente principal enruta a flujos distintos **y** ejecuta trabajo. El flujo `revisar_gasto` es un ciclo ReAct que se detiene por una condición explícita (veredicto válido o `MAX_PASOS_REACT`). | `evidencias/dos-recorridos/`, `evidencias/react/` |
| Delegación A2A | 0,5 | El principal le encarga a otro agente (el verificador de boletas) una tarea por A2A y usa su respuesta. | `evidencias/a2a/` |
| Seguridad | 0,5 | (a) Sin clave, el servicio rechaza la petición. (b) Una acción no autorizada se **bloquea sin ejecutarse**. | `evidencias/seguridad/` |
| Resiliencia | 0,5 | Ante una falla o un timeout hay fallback o un mensaje claro, **sin inventar** datos y **sin repetir indefinidamente**. | `evidencias/fallo-controlado/` |
| Despliegue con registro | 0,5 | El servicio está desplegado y registra **qué flujo corrió y cómo terminó** cada ejecución. | `evidencias/despliegue/` |

## Ampliaciones declaradas: +3,0 como tope

| Ampliación | Puntos | Evidencia en |
|---|---|---|
| RAG documental | 0,5 | `evidencias/ampliacion-rag/` |
| Evaluación con golden set | 0,5 | `evidencias/ampliacion-evaluacion/` |
| Memoria persistente | 0,5 | `evidencias/ampliacion-memoria/` |
| MCP | 0,5 | `evidencias/ampliacion-mcp/` |
| GraphRAG | 1,0 | `evidencias/ampliacion-graphrag/` |
| **De respaldo:** n8n A2A | 1,0 | `evidencias/ampliacion-n8n/` |

Las cinco primeras suman 3,0, justo el tope. **n8n es el respaldo** por si alguna otra no se
acredita. Tiene que ser un **caso adicional**: no rehace la delegación A2A obligatoria
(el verificador de la base sigue siendo un agente A2A propio).

## Reglas

- **Un extra solo cuenta con la base completa.** La base va primero.
- **El mismo trabajo no se acredita dos veces.** Por ejemplo, la delegación A2A de la base no
  cuenta también como ampliación, y el registro del despliegue no cuenta como memoria persistente.
- **Un extra fallido no descuenta.** Si no alcanza a funcionar, se declara como no logrado y listo.
- **Cada prueba muestra tres cosas:** la **entrada** (qué se mandó), la **ejecución observada**
  (traza, log o registro con su `id_ejecucion`) y el **resultado** (qué respondió y cómo terminó).

## Entrega

- **Repositorio** con el código (`tarea-final-c2/`).
- **README** con la ficha mínima: Alcance y flujos, Entorno, Acceso al servicio, Configuración,
  Datos de ejemplo, Evidencias y Ampliaciones declaradas.
- **Servicio desplegado** y accesible.
- **Evidencias** en `evidencias/`, una subcarpeta por prueba.
- **Las credenciales se mandan aparte y nunca van en el repo.** Esto incluye la clave del
  servicio, tokens y URLs con usuario y clave.
