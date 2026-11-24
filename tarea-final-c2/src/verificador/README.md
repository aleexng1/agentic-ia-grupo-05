# src/verificador/

Agente especialista A2A: lee la boleta con Gemini (visión) y compara con lo declarado.
App FastAPI propia (`app.py`) con su ficha (`ficha.py`). Encargo y respuesta en
[../../docs/contratos.md](../../docs/contratos.md) (sección 5).

- **Dueño:** Alex.
- **Hecho:** la app arranca, `/health` y la ficha A2A (`/.well-known/agent-card.json`).
- **Falta:** `agente.verificar_boleta`; extender `src/comun/executor.py` para leer FilePart + DataPart y responder DataPart; pasar de X-API-Key provisoria a `TOKEN_A2A`.
