# A2A · boleta-02-monto-distinto.png (monto distinto)

Capturado el 2026-11-24T21:33:14-03:00 · verificador en `http://127.0.0.1:8001` · tiempo límite 20 s · duración 176 ms.

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
  "disponible": false,
  "tipo_fallo": "sin_conexion",
  "motivo": "no hay conexión con el verificador (¿está levantado y URL_VERIFICADOR es correcta?)"
}
```

**Fallo controlado** (`tipo_fallo = sin_conexion`): el principal no recibe ningún campo leído, así que no hay nada que comparar ni que inventar. En el grafo, el gasto queda en «observar» con `estado_final = "fallback"` (pruebas `tests/test_grafo.py` y `tests/test_verificador.py`).

## Dónde se usa
En el nodo `revisar_gasto` del grafo principal: el resultado se pasa al ReAct como dato y, si algún campo no cuadra o el verificador no respondió, un «aprobar» baja a «observar» (`aplicar_verificacion`).

## Log del principal (este proceso)
```text
2026-11-24 21:33:14 INFO    [tarea_final] a2a · encargo → http://127.0.0.1:8001 · imagen image/png 44527 bytes · tiempo límite 20 s
2026-11-24 21:33:14 WARNING [tarea_final] a2a · verificador no disponible · sin_conexion · no hay conexión con el verificador (¿está levantado y URL_VERIFICADOR es correcta?)
```

## Log del verificador
```text
(el verificador no registró este encargo: no le llegó)
```
