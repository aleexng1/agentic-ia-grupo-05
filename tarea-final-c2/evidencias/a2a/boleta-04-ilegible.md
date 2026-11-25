# A2A · boleta-04-ilegible.png (ilegible)

Capturado el 2026-11-25T19:22:27-03:00 · verificador en `http://127.0.0.1:8001` · tiempo límite 20 s · duración 4877 ms.

## Encargo (principal → verificador)
Parte de archivo (la imagen; aquí solo tipo, tamaño y hash) + parte de datos (lo declarado):
```json
{
  "imagen": {
    "archivo": "boleta-04-ilegible.png",
    "mime_type": "image/png",
    "bytes": 113655,
    "sha256_inicio": "5866b893c43544cb"
  },
  "datos": {
    "tarea": "verificar_boleta",
    "declarado": {
      "monto": 15990,
      "fecha": "2026-10-20",
      "rut_emisor": "11.111.111-1",
      "folio": "000456",
      "categoria": "Materiales de mantención"
    }
  }
}
```

## Respuesta del verificador (lo que recibe el principal)
```json
{
  "disponible": true,
  "leido": {
    "monto": null,
    "fecha": null,
    "rut_emisor": null,
    "folio": null,
    "categoria": null
  },
  "cuadra": {
    "monto": "no",
    "fecha": "no",
    "rut_emisor": "no",
    "folio": "no",
    "categoria": "no"
  },
  "confianza": 0.0,
  "observaciones": "La imagen no es legible: no se leyó ningún campo. El documento es una imagen borrosa de prueba y no permite leer ningún dato legible."
}
```

Esperado según `datos/boletas/declarado.json`: `{"monto": "no", "fecha": "no", "rut_emisor": "no", "folio": "no", "categoria": "no"}`

## Dónde se usa
En el nodo `revisar_gasto` del grafo principal: el resultado se pasa al ReAct como dato y, si algún campo no cuadra o el verificador no respondió, un «aprobar» baja a «observar» (`aplicar_verificacion`).

## Log del principal (este proceso)
```text
2026-11-25 19:22:22 INFO    [tarea_final] a2a · encargo → http://127.0.0.1:8001 · imagen image/png 113655 bytes · tiempo límite 20 s
2026-11-25 19:22:27 INFO    [tarea_final] a2a · respuesta ← verificador · confianza=0.00 · no cuadra: monto,fecha,rut_emisor,folio,categoria
```

## Log del verificador
```text
2026-11-25 19:22:22 INFO    [tarea_final] verificador · encargo ec2211d9 · imagen image/png 113655 bytes sha256:5866b893c43544cb · declarado monto=15990 fecha=2026-10-20 folio=000456
2026-11-25 19:22:27 INFO    [tarea_final] verificador · respuesta ec2211d9 · confianza=0.00 · no cuadra: monto,fecha,rut_emisor,folio,categoria
```
