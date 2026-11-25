# A2A · boleta-03-fecha-distinta.png (fecha distinta)

Capturado el 2026-11-25T19:22:22-03:00 · verificador en `http://127.0.0.1:8001` · tiempo límite 20 s · duración 2281 ms.

## Encargo (principal → verificador)
Parte de archivo (la imagen; aquí solo tipo, tamaño y hash) + parte de datos (lo declarado):
```json
{
  "imagen": {
    "archivo": "boleta-03-fecha-distinta.png",
    "mime_type": "image/png",
    "bytes": 43518,
    "sha256_inicio": "3b12eb43737498b2"
  },
  "datos": {
    "tarea": "verificar_boleta",
    "declarado": {
      "monto": 9800,
      "fecha": "2026-10-12",
      "rut_emisor": "33.333.333-3",
      "folio": "078901",
      "categoria": "Peajes"
    }
  }
}
```

## Respuesta del verificador (lo que recibe el principal)
```json
{
  "disponible": true,
  "leido": {
    "monto": 9800,
    "fecha": "2026-09-12",
    "rut_emisor": "33.333.333-3",
    "folio": "078901",
    "categoria": "peaje"
  },
  "cuadra": {
    "monto": "sí",
    "fecha": "no",
    "rut_emisor": "sí",
    "folio": "sí",
    "categoria": "sí"
  },
  "confianza": 1.0,
  "observaciones": "Documento legible de prueba para peaje."
}
```

Esperado según `datos/boletas/declarado.json`: `{"monto": "sí", "fecha": "no", "rut_emisor": "sí", "folio": "sí", "categoria": "sí"}`

## Dónde se usa
En el nodo `revisar_gasto` del grafo principal: el resultado se pasa al ReAct como dato y, si algún campo no cuadra o el verificador no respondió, un «aprobar» baja a «observar» (`aplicar_verificacion`).

## Log del principal (este proceso)
```text
2026-11-25 19:22:20 INFO    [tarea_final] a2a · encargo → http://127.0.0.1:8001 · imagen image/png 43518 bytes · tiempo límite 20 s
2026-11-25 19:22:22 INFO    [tarea_final] a2a · respuesta ← verificador · confianza=1.00 · no cuadra: fecha
```

## Log del verificador
```text
2026-11-25 19:22:20 INFO    [tarea_final] verificador · encargo 27f4c5d2 · imagen image/png 43518 bytes sha256:3b12eb43737498b2 · declarado monto=9800 fecha=2026-10-12 folio=078901
2026-11-25 19:22:22 INFO    [tarea_final] verificador · respuesta 27f4c5d2 · confianza=1.00 · no cuadra: fecha
```
