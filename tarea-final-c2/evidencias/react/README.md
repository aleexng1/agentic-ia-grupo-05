# Evidencia: ReAct con parada explícita (Matías)

El flujo `revisar_gasto` es un ReAct (LangGraph) que termina por una de cuatro paradas explícitas:
veredicto válido (`ok`/`fallback`), máximo de pasos `MAX_PASOS_REACT` (`error`), acción no
autorizada (`bloqueado`) o tiempo agotado (`error`). Cada parada tiene su evidencia:

| Parada | Evidencia | Con `id_ejecucion` |
|---|---|---|
| Veredicto válido | `../dos-recorridos/03-revisar-gasto.md` (por `/chat`, 2026-11-26) y `01-veredicto-gs01.txt` (terminal) | **Sí**, en la de `/chat` |
| Máximo de pasos | `02-parada-max-pasos-gs01.txt` (terminal) + prueba automática | No (ver abajo) |
| Acción no autorizada | `../seguridad/02-bloqueo-accion-no-autorizada.md` (Postgres real) | **Sí** |
| Tiempo agotado | pruebas automáticas de `hora_limite` en `tests/test_revisar_gasto_c2.py` | No aplica |

## 1. Parada por veredicto válido, por `/chat` (la versión para la nota)

`../dos-recorridos/03-revisar-gasto.md`, capturada por Alex el 2026-11-26 21:34 con el servidor real
(`uvicorn api.app:app`), Redis del grupo (RAG), el MCP de fondos, el juez y Postgres. Muestra el ReAct
paso a paso: herramienta → resultado → decisión → parada.

- **Entrada:** `POST /chat` con «Revisa este gasto rendido.» y el gasto GS-01 del golden set de c1
  (peaje de $7.800, fondo FR-001). Respuesta 202 con `id_ejecucion = a078d302-b429-4448-9774-cdaafe74343d`.
- **Ejecución observada:** la traza de cada paso y el log del servidor con ese `id_ejecucion`:
  `ruta=revisar_gasto · estado=ok · 11395 ms · herramientas=buscar_politica,consultar_fondo,validar_gasto,emitir_veredicto`.
- **Resultado:** **APROBAR / P02 / Peaje / CTA-6100** en **4 pasos**, igual a lo esperado de GS-01;
  `estado_final = "ok"`. `GET /registro/{id}` devuelve la misma fila desde la tabla `ejecuciones`.

## 2. Corridas desde la terminal (2026-11-24, sin servidor)

Comando (desde `tarea-final-c2/`, con el `.venv` activado):

```
python -m src.principal.flujos.revisar_gasto GS-01
```

| Archivo | Entrada | Ejecución observada | Resultado |
|---|---|---|---|
| `01-veredicto-gs01.txt` | Caso GS-01, `MAX_PASOS_REACT=10` | 5 vueltas: `buscar_politica` ×2 → `consultar_fondo` (MCP) → `validar_gasto` → `emitir_veredicto`; luego juez, fondo y registro | **Parada por veredicto válido**: APROBAR / P02 / Peaje / CTA-6100, `estado_final = "ok"`, fondo de $200.000 a $192.200 |
| `02-parada-max-pasos-gs01.txt` | El mismo caso con `MAX_PASOS_REACT=2` | 2 vueltas y el nodo `parada` | **Parada por máximo de pasos**: «Me detuve: alcancé el máximo de 2 pasos…», sin veredicto, sin registro, `estado_final = "error"` |

### Por qué la parada por máximo de pasos no tiene `id_ejecucion`

Con el valor del proyecto (`MAX_PASOS_REACT=6`) ningún caso llega al tope: en la corrida final del
evaluador (#114) los 57 casos terminaron con veredicto. Para mostrar la parada hay que bajar el tope
a propósito, y en el servicio desplegado eso cambiaría el comportamiento para todo el grupo. Por eso
se muestra con la terminal (`MAX_PASOS_REACT=2`) y la respalda una prueba automática que corre en
cada `pytest`:

- `tests/test_react_mcp.py::test_se_detiene_por_max_pasos_con_estado_error`: un modelo que nunca
  emite veredicto, `MAX_PASOS=2` → `estado_final = "error"`, 2 pasos, 2 llamadas al modelo, sin
  veredicto y **sin escribir en el registro**.

Si se puede bajar el tope un momento en Heroku, se agrega aquí la misma parada por `/chat`.

### Notas sobre las corridas del 2026-11-24

- **Redis no estaba configurado** (`REDIS_URL` vacía): `buscar_politica` devolvió un error como
  observación y el agente siguió con las herramientas deterministas. Se ve en la traza. La captura
  por `/chat` de la sección 1 ya usa el RAG.
- En la vuelta 4 el modelo agregó un campo `cargo` al gasto; el grafo lo detectó (`campos_alterados`)
  y validó el gasto original (`gasto_original_restaurado`). Es la protección de c1 funcionando.
- El registro de veredictos de esas corridas era el SQLite local (todavía no Postgres).

## 3. Repetición con RAG desde la terminal (2026-11-26)

Con Redis y Neo4j del grupo (solo lectura), el ReAct llegó a la decisión esperada en los tres casos:

| Caso | Sin RAG (2026-11-24) | Con RAG (2026-11-26) | Esperado |
|---|---|---|---|
| GS-01 | aprobar P02 | **aprobar P02** (el juez lo valida) | aprobar P02 |
| GS-27 | rechazar RG-03 | **rechazar RG-03** | rechazar RG-03 |
| GS-29 | observar P02 | **rechazar P07** (solo acepta factura) | rechazar P07 |

Estas trazas **no se guardaron como evidencia**: en ese equipo no había Postgres y el paso final
(escribir el registro) no pudo terminar. La versión con registro es la de `/chat` de la sección 1.
