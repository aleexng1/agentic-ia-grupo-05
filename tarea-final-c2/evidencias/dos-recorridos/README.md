# Evidencia: dos recorridos (router + worker, parte del 1,0)

Solicitudes distintas activan flujos distintos del **mismo** agente principal. La pauta pide
`consulta_politica` **y** `revisar_gasto` (01 y 03); `fuera_de_alcance` (02) es un tercer recorrido.

| Archivo | Ruta esperada | Estado |
|---|---|---|
| `01-consulta-politica.md` | `consulta_politica` | recapturado 2026-11-24 en `main` integrado, con el flujo de Eduardo y Postgres: el router elige `consulta_politica` (se ve en el log y en `GET /registro/{id}`), pero sin acceso a Redis el flujo responde **502** «No se pudo completar la búsqueda documental (Redis o embeddings)», sin inventar. **Volver a capturar cuando haya `REDIS_URL` real**: esa es la versión para la nota |
| `02-fuera-de-alcance.md` | `fuera_de_alcance` | capturado 2026-11-24 con Gemini: `estado_final = ok` |
| `03-revisar-gasto.md` | `revisar_gasto` | recapturado 2026-11-24 en `main` integrado (ReAct de Matías, MCP, juez y Postgres): **APROBAR P02 / Peaje / CTA-6100** en 5 pasos, igual a lo esperado de GS-01; la ruta y el `estado_final = ok` se ven en la respuesta y en `GET /registro/{id}` |

Cómo generarla (desde `tarea-final-c2/`, con `.env` completo):
```bash
uvicorn api.app:app --port 8000 2>&1 | tee /tmp/principal.log        # terminal 1 (MOSTRAR_TRAZAS=0)
python evidencias/dos-recorridos/capturar.py --url http://127.0.0.1:8000 --log /tmp/principal.log   # terminal 2 (--solo 03: uno solo)
```
Cada `.md` trae la **entrada** (curl con la clave tapada), la **ejecución observada** (líneas del
log con su `id_ejecucion`), el **resultado** (JSON de `/chat`) y el **registro** (`GET /registro/{id}`).
Cada captura usa un `thread_id` nuevo (con memoria persistente, un hilo repetido arrastra el turno anterior).
Para que se guarde en `ejecuciones`, el principal necesita `DATABASE_URL` (en local, un Postgres de prueba).

Mientras Eduardo no una `consulta_politica`, ese recorrido termina con
`estado_final = "error"` y «Flujo consulta_politica todavía no implementado»; la ruta elegida
por el router igual queda a la vista (`"ruta": "consulta_politica"`).

Prueba sin Gemini ya hecha (2026-11-24, no es evidencia): con uvicorn local, `/chat` sin
`GOOGLE_API_KEY` responde **502** con un mensaje claro y su `id_ejecucion`, y el texto vacío
responde **422** sin llamar al modelo. La clave del servicio no aparece en el log.
