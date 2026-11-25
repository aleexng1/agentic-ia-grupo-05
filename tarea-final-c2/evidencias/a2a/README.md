# Evidencia: delegación A2A (0,5)

El principal le encarga al **verificador de boletas** (otro agente, con su propia app y su ficha
A2A) que lea una boleta y la compare con lo declarado, y usa su respuesta en el veredicto.

| Archivo | Qué muestra | Estado |
|---|---|---|
| `00-canal-sin-gemini-boleta-01-cuadra.md` | Corrida real con los dos lados: el encargo llega (log del verificador con el hash de la imagen), el verificador no puede leer porque falta `GOOGLE_API_KEY` y el principal recibe un **error estructurado** (`tipo_fallo`), sin datos inventados. **No** es la evidencia del 0,5: muestra el canal y la salida segura. | hecho (2026-11-24) |
| `boleta-01-cuadra.md` … `boleta-04-ilegible.md` | **Evidencia del 0,5.** Las 4 boletas ficticias leídas con Gemini (`gemini-3.5-flash-lite`): encargo, respuesta (`leido`, `cuadra`, `confianza`), dónde se usa y el log de ambos lados. Las 4 dan exactamente el `cuadra` esperado: 01 todo «sí»; 02 monto «no» (lee 62.000 contra 52.000 declarados); 03 fecha «no» (lee 2026-09-12 contra 2026-10-12); 04 ilegible, todo `null`/«no» y confianza 0. | hecho (2026-11-24); **recapturadas el 2026-11-25 con el canal por `TOKEN_A2A`** (mismo resultado) |
| `seguridad-token-a2a.md` | **Seguridad del canal A2A**: `/health` y la ficha son públicos. Un encargo sin token, con un token incorrecto, sin «Bearer» o con solo la `X-API-Key` del servicio → **401**, y no se lee la boleta. Con `Authorization: Bearer ***` el encargo real responde. Incluye el log del verificador con cada rechazo. El token nunca aparece. | hecho (2026-11-25) |
| `fallo-forzado-boleta-02-monto-distinto.md` | **Fallo controlado** con `FORZAR_FALLO_A2A=1` (solo en esa ejecución; el `.env` queda en 0): error estructurado `tipo_fallo = forzado`, sin campos leídos, y el verificador no recibe nada. | hecho (2026-11-24) |
| `fallo-verificador-apagado-boleta-02-monto-distinto.md` | **Fallo real**: el verificador está apagado → `tipo_fallo = sin_conexion` en milisegundos, sin datos inventados. | hecho (2026-11-24) |

Cómo generarla (desde `tarea-final-c2/`, con `.env` completo):
```bash
uvicorn src.verificador.app:app --port 8001 2>&1 | tee /tmp/verificador.log   # terminal 1
python evidencias/a2a/capturar.py --log-verificador /tmp/verificador.log        # terminal 2
FORZAR_FALLO_A2A=1 python evidencias/a2a/capturar.py --log-verificador /tmp/verificador.log --solo 02 --prefijo fallo-forzado-
# apagar el verificador (Ctrl+C en la terminal 1) y:
python evidencias/a2a/capturar.py --log-verificador /tmp/verificador.log --solo 02 --prefijo fallo-verificador-apagado-
```
Seguridad del canal (con el verificador levantado, igual que arriba):
```bash
python evidencias/a2a/capturar_token.py --log-verificador /tmp/verificador.log
```
Del encargo se guarda solo el tipo, el tamaño y el SHA-256 de la imagen; nunca la imagen ni claves.
Desde el 2026-11-25 el canal exige `Authorization: Bearer <TOKEN_A2A>` (`proteger_con_token_a2a`); el principal ya no manda la `X-API-Key` al verificador.
