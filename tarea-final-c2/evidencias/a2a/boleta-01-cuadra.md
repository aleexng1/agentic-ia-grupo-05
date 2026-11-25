# A2A · boleta-01-cuadra.png (cuadra)

Capturado el 2026-11-25T19:22:09-03:00 · verificador en `http://127.0.0.1:8001` · tiempo límite 20 s · duración 5718 ms.

## Encargo (principal → verificador)
Parte de archivo (la imagen; aquí solo tipo, tamaño y hash) + parte de datos (lo declarado):
```json
{
  "imagen": {
    "archivo": "boleta-01-cuadra.png",
    "mime_type": "image/png",
    "bytes": 42579,
    "sha256_inicio": "dbd473e801de6cdc"
  },
  "datos": {
    "tarea": "verificar_boleta",
    "declarado": {
      "monto": 45000,
      "fecha": "2026-10-02",
      "rut_emisor": "11.111.111-1",
      "folio": "000123",
      "categoria": "Gasolina (vehículo propio)"
    }
  }
}
```

## Respuesta del verificador (lo que recibe el principal)
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
  "observaciones": "Documento legible y datos extraídos correctamente."
}
```

Esperado según `datos/boletas/declarado.json`: `{"monto": "sí", "fecha": "sí", "rut_emisor": "sí", "folio": "sí", "categoria": "sí"}`

## Dónde se usa
En el nodo `revisar_gasto` del grafo principal: el resultado se pasa al ReAct como dato y, si algún campo no cuadra o el verificador no respondió, un «aprobar» baja a «observar» (`aplicar_verificacion`).

## Log del principal (este proceso)
```text
2026-11-25 19:22:04 INFO    [tarea_final] a2a · encargo → http://127.0.0.1:8001 · imagen image/png 42579 bytes · tiempo límite 20 s
2026-11-25 19:22:09 INFO    [tarea_final] a2a · respuesta ← verificador · confianza=1.00 · no cuadra: -
```

## Log del verificador
```text
2026-11-25 19:22:04 INFO    [tarea_final] verificador · encargo 95bff538 · imagen image/png 42579 bytes sha256:dbd473e801de6cdc · declarado monto=45000 fecha=2026-10-02 folio=000123
2026-11-25 19:22:09 INFO    [tarea_final] verificador · respuesta 95bff538 · confianza=1.00 · no cuadra: -
```
