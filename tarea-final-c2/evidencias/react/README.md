# Evidencia: ReAct con parada explícita (Matías)

Corridas **LOCALES** del 2026-11-24, con Gemini real (`gemini-3.5-flash-lite`), desde la terminal y sin
servidor. Todavía **sin `id_ejecucion`**: ese número lo pone `/chat` cuando el router esté integrado
(se agregará entonces una corrida por `/chat` con su `GET /registro/{id}`).

Comando (desde `tarea-final-c2/`, con el `.venv` activado):

```
python -m src.principal.flujos.revisar_gasto GS-01
```

| Archivo | Entrada | Ejecución observada | Resultado |
|---|---|---|---|
| `01-veredicto-gs01.txt` | Caso GS-01 del golden set de c1 (peaje de $7.800, fondo FR-001), `MAX_PASOS_REACT=10` | 5 vueltas: `buscar_politica` ×2 → `consultar_fondo` (MCP) → `validar_gasto` → `emitir_veredicto`; luego juez, fondo y registro | **Parada por veredicto válido**: APROBAR / P02 / Peaje / CTA-6100 (igual a lo esperado), `estado_final = "ok"`, fondo de $200.000 a $192.200 |
| `02-parada-max-pasos-gs01.txt` | El mismo caso con `MAX_PASOS_REACT=2` | 2 vueltas y el nodo `parada` | **Parada por máximo de pasos**: «Me detuve: alcancé el máximo de 2 pasos…», sin veredicto, sin registro, `estado_final = "error"` |

Notas honestas:
- En estas corridas **Redis no estaba configurado** (`REDIS_URL` vacía): `buscar_politica` devolvió un error
  como observación y el agente siguió con las herramientas deterministas. Se ve en la traza. Falta repetir
  con el RAG de Eduardo funcionando.
- En la vuelta 4 el modelo agregó un campo `cargo` al gasto; el grafo lo detectó (`campos_alterados`) y
  validó el gasto original (`gasto_original_restaurado`). Es la protección de c1 funcionando.
- El registro de veredictos de estas corridas es el SQLite local (aún no Postgres).
