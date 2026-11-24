# Evidencia: dos recorridos (router + worker, parte del 1,0)

Dos solicitudes distintas activan flujos distintos del **mismo** agente principal.

| Archivo | Ruta esperada | Estado |
|---|---|---|
| `01-consulta-politica.md` | `consulta_politica` | **pendiente** (falta `GOOGLE_API_KEY`) |
| `02-fuera-de-alcance.md` | `fuera_de_alcance` | **pendiente** (falta `GOOGLE_API_KEY`) |

Cómo generarla (desde `tarea-final-c2/`, con `.env` completo):
```bash
uvicorn api.app:app --port 8000 2>&1 | tee /tmp/principal.log        # terminal 1
python evidencias/dos-recorridos/capturar.py --url http://127.0.0.1:8000 --log /tmp/principal.log   # terminal 2
```
Cada `.md` trae la **entrada** (curl con la clave tapada), la **ejecución observada** (líneas del
log con su `id_ejecucion`) y el **resultado** (JSON de `/chat`).

Mientras Eduardo no una `consulta_politica`, ese recorrido termina con
`estado_final = "error"` y «Flujo consulta_politica todavía no implementado»; la ruta elegida
por el router igual queda a la vista (`"ruta": "consulta_politica"`).

Prueba sin Gemini ya hecha (2026-11-24, no es evidencia): con uvicorn local, `/chat` sin
`GOOGLE_API_KEY` responde **502** con un mensaje claro y su `id_ejecucion`, y el texto vacío
responde **422** sin llamar al modelo. La clave del servicio no aparece en el log.
