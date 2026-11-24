# src/verificador/

Agente especialista A2A: lee la boleta con Gemini (visión) y compara con lo declarado.
App FastAPI propia (`app.py`) con su ficha (`ficha.py`). Encargo y respuesta en
[../../docs/contratos.md](../../docs/contratos.md) (sección 5).

- **Dueño:** Alex.
- **Hecho:** `agente.py` lee la imagen con Gemini (visión, salida estructurada, temperatura 0) y
  compara en código monto, fecha, RUT y folio; la categoría la juzga el modelo. Al modelo no se le
  muestran los valores declarados (salvo la categoría), así no puede copiarlos. Lo no leído va
  `null` y `cuadra = "no"`. La imagen no se guarda ni va al log (solo tipo, tamaño y hash).
  `src/comun/executor.py` ya lee FilePart + DataPart y responde DataPart (`responder_partes`).
- **Falta:** cambiar `proteger_app` por `proteger_con_token_a2a` cuando se una el PR de Matías
  (el cliente ya manda `Authorization: Bearer <TOKEN_A2A>`); correr las pruebas `necesita_llm`.
