# Evidencia: delegación A2A (0,5)

El principal le encarga al **verificador de boletas** (otro agente, con su propia app y su ficha
A2A) que lea una boleta y la compare con lo declarado, y usa su respuesta en el veredicto.

| Archivo | Qué muestra | Estado |
|---|---|---|
| `00-canal-sin-gemini-boleta-01-cuadra.md` | Corrida real con los dos lados: el encargo llega (log del verificador con el hash de la imagen), el verificador no puede leer porque falta `GOOGLE_API_KEY` y el principal recibe un **error estructurado** (`tipo_fallo`), sin datos inventados. **No** es la evidencia del 0,5: muestra el canal y la salida segura. | hecho (2026-11-24) |
| `boleta-01-cuadra.md` … `boleta-04-ilegible.md` | Las 4 boletas ficticias con Gemini: encargo, respuesta (`leido`, `cuadra`, `confianza`), dónde se usa y el log de ambos lados. | **pendiente** (falta `GOOGLE_API_KEY`) |

Cómo generarla (desde `tarea-final-c2/`, con `.env` completo):
```bash
uvicorn src.verificador.app:app --port 8001 2>&1 | tee /tmp/verificador.log   # terminal 1
python evidencias/a2a/capturar.py --log-verificador /tmp/verificador.log        # terminal 2
```
Del encargo se guarda solo el tipo, el tamaño y el SHA-256 de la imagen; nunca la imagen ni claves.
