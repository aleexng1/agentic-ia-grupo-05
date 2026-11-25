# Recorrido 01-consulta-politica: ruta esperada `consulta_politica`

Capturado el 2026-11-24T22:16:15-03:00 contra `http://127.0.0.1:8000` con `evidencias/dos-recorridos/capturar.py`.

## Entrada
```bash
curl -s -X POST http://127.0.0.1:8000/chat -H 'Content-Type: application/json' -H 'X-API-Key: ***' \
  -d '{"thread_id": "evidencia-01-consulta-politica-20261124T221612", "texto": "¿Cuál es el plazo máximo para rendir un gasto que hice en octubre?"}'
```

## Ejecución observada (log del servidor con este id_ejecucion)
```text
2026-11-24 22:16:14 ERROR   [tarea_final] ejecución 45ed9644-e35c-4013-b3f3-37042f9390fb · ruta=consulta_politica · falló sin salida: No se pudo completar la búsqueda documental (Redis o embeddings).
2026-11-24 22:16:14 INFO    [tarea_final] ejecución 45ed9644-e35c-4013-b3f3-37042f9390fb · ruta=consulta_politica · estado=error · 1761 ms · a2a=False · herramientas=-
```

## Resultado (HTTP 502)
```json
{
  "detail": "No se pudo completar la búsqueda documental (Redis o embeddings). (id_ejecucion: 45ed9644-e35c-4013-b3f3-37042f9390fb)"
}
```

## Registro (`GET /registro/45ed9644-e35c-4013-b3f3-37042f9390fb` con `X-API-Key: ***` → HTTP 200)
```json
{
  "id_ejecucion": "45ed9644-e35c-4013-b3f3-37042f9390fb",
  "fecha": "2026-11-25T01:16:13.047783+00:00",
  "ruta": "consulta_politica",
  "pasos": 0,
  "herramientas_usadas": [],
  "hubo_a2a": false,
  "estado_final": "error",
  "duracion_ms": 1761
}
```

La ejecución falló (HTTP 502) con un mensaje claro y sin datos inventados; la ruta que eligió el router y su `estado_final` quedan en el log de arriba y en `ejecuciones`.
