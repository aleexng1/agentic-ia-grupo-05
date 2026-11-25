# A2A · boleta-02-monto-distinto.png (monto distinto)

Capturado el 2026-11-24T21:32:25-03:00 · verificador en `http://127.0.0.1:8001` · tiempo límite 20 s · duración 2897 ms.

## Encargo (principal → verificador)
Parte de archivo (la imagen; aquí solo tipo, tamaño y hash) + parte de datos (lo declarado):
```json
{
  "imagen": {
    "archivo": "boleta-02-monto-distinto.png",
    "mime_type": "image/png",
    "bytes": 44527,
    "sha256_inicio": "e3180ac8b2f1c5e1"
  },
  "datos": {
    "tarea": "verificar_boleta",
    "declarado": {
      "monto": 52000,
      "fecha": "2026-10-14",
      "rut_emisor": "22.222.222-2",
      "folio": "004512",
      "categoria": "Hotel"
    }
  }
}
```

## Respuesta del verificador (lo que recibe el principal)
```json
{
  "disponible": true,
  "leido": {
    "monto": 62000,
    "fecha": "2026-10-14",
    "rut_emisor": "22.222.222-2",
    "folio": "004512",
    "categoria": "hotel y cena"
  },
  "cuadra": {
    "monto": "no",
    "fecha": "sí",
    "rut_emisor": "sí",
    "folio": "sí",
    "categoria": "sí"
  },
  "confianza": 1.0,
  "observaciones": "Documento legible de prueba para gasto de hotel."
}
```

Esperado según `datos/boletas/declarado.json`: `{"monto": "no", "fecha": "sí", "rut_emisor": "sí", "folio": "sí", "categoria": "sí"}`

## Dónde se usa
En el nodo `revisar_gasto` del grafo principal: el resultado se pasa al ReAct como dato y, si algún campo no cuadra o el verificador no respondió, un «aprobar» baja a «observar» (`aplicar_verificacion`).

## Log del principal (este proceso)
```text
2026-11-24 21:32:22 INFO    [tarea_final] a2a · encargo → http://127.0.0.1:8001 · imagen image/png 44527 bytes · tiempo límite 20 s
2026-11-24 21:32:25 INFO    [tarea_final] a2a · respuesta ← verificador · confianza=1.00 · no cuadra: monto
```

## Log del verificador
```text
2026-11-24 21:32:22 INFO    [tarea_final] verificador · encargo 005039a1 · imagen image/png 44527 bytes sha256:e3180ac8b2f1c5e1 · declarado monto=52000 fecha=2026-10-14 folio=004512
2026-11-24 21:32:25 INFO    [tarea_final] verificador · respuesta 005039a1 · confianza=1.00 · no cuadra: monto
```
