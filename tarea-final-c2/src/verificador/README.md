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
- **Hecho:** `app.py` está protegido con `proteger_con_token_a2a` (exige `Authorization: Bearer
  <TOKEN_A2A>` en los POST; `/health` y la ficha son públicos). Las pruebas `necesita_llm` corren con
  las 4 boletas.
