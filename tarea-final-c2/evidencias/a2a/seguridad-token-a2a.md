# A2A · seguridad del canal: el verificador exige `Authorization: Bearer <TOKEN_A2A>`

Capturado el 2026-11-25T19:21:47-03:00 contra `http://127.0.0.1:8001` con `evidencias/a2a/capturar_token.py`. El token y la clave se muestran como `***`.

## 1. Lecturas públicas
- `GET /health` → HTTP 200
- `GET /.well-known/agent-card.json` → HTTP 200

## 2. Encargos rechazados (no se ejecuta nada)

### Sin token
Cabeceras enviadas: `{}`
→ **HTTP 401** `{"detail":"Falta el token A2A. Envíalo en la cabecera Authorization: [oculta] <token>."}`

### Token incorrecto
Cabeceras enviadas: `{"Authorization": "Bearer token-equivocado"}`
→ **HTTP 401** `{"detail":"El token A2A es incorrecto."}`

### Token correcto pero sin «Bearer»
Cabeceras enviadas: `{"Authorization": "***"}`
→ **HTTP 401** `{"detail":"Falta el token A2A. Envíalo en la cabecera Authorization: [oculta] <token>."}`

### Solo la X-API-Key del servicio (protección provisoria anterior)
Cabeceras enviadas: `{"X-API-Key": "***"}`
→ **HTTP 401** `{"detail":"Falta el token A2A. Envíalo en la cabecera Authorization: [oculta] <token>."}`

## 3. Encargo real con el token correcto (`delegar_verificador`, `boleta-01-cuadra.png`)
Cabeceras enviadas: `{"Authorization": "Bearer ***"}` (la `X-API-Key` ya no sale del principal).
Duración: 4358 ms.
```json
{
  "disponible": true,
  "leido": {
    "monto": 45000,
    "fecha": "2026-10-02",
    "rut_emisor": "11.111.111-1",
    "folio": "000123",
    "categoria": "Gasolina 95 octanos"
  },
  "cuadra": {
    "monto": "sí",
    "fecha": "sí",
    "rut_emisor": "sí",
    "folio": "sí",
    "categoria": "sí"
  },
  "confianza": 1.0,
  "observaciones": "Documento de prueba perfectamente legible."
}
```

## Log del verificador (estas peticiones)
```text
INFO:     127.0.0.1:55312 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:55314 - "GET /.well-known/agent-card.json HTTP/1.1" 200 OK
2026-11-25 19:21:47 WARNING [tarea_final] encargo A2A rechazado · POST / · sin token
INFO:     127.0.0.1:55326 - "POST / HTTP/1.1" 401 Unauthorized
2026-11-25 19:21:47 WARNING [tarea_final] encargo A2A rechazado · POST / · token incorrecto
INFO:     127.0.0.1:55340 - "POST / HTTP/1.1" 401 Unauthorized
2026-11-25 19:21:47 WARNING [tarea_final] encargo A2A rechazado · POST / · sin token
INFO:     127.0.0.1:55350 - "POST / HTTP/1.1" 401 Unauthorized
2026-11-25 19:21:47 WARNING [tarea_final] encargo A2A rechazado · POST / · sin token
INFO:     127.0.0.1:55366 - "POST / HTTP/1.1" 401 Unauthorized
INFO:     127.0.0.1:55380 - "GET /.well-known/agent-card.json HTTP/1.1" 200 OK
2026-11-25 19:21:47 INFO    [tarea_final] verificador · encargo 60e77051 · imagen image/png 42579 bytes sha256:dbd473e801de6cdc · declarado monto=45000 fecha=2026-10-02 folio=000123
2026-11-25 19:21:51 INFO    [tarea_final] verificador · respuesta 60e77051 · confianza=1.00 · no cuadra: -
INFO:     127.0.0.1:55380 - "POST / HTTP/1.1" 200 OK
```
