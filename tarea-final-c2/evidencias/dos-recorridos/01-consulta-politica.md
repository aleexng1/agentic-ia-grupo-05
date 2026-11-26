# Recorrido 01-consulta-politica: ruta esperada `consulta_politica`

Capturado el 2026-11-26T18:33:07-03:00 contra `http://127.0.0.1:8000` con `evidencias/dos-recorridos/capturar.py`.

## Entrada
```bash
curl -s -X POST http://127.0.0.1:8000/chat -H 'Content-Type: application/json' -H 'X-API-Key: ***' \
  -d '{"thread_id": "evidencia-01-consulta-politica-20261126T183256", "texto": "¿Cuál es el plazo máximo para rendir un gasto que hice en octubre?"}'
```

Respuesta inmediata (HTTP 202, `/chat` asíncrono):
```json
{
  "id_ejecucion": "a65dab23-1152-4a93-b336-31c2a99db0bd",
  "estado": "en_proceso",
  "consultar": "/registro/a65dab23-1152-4a93-b336-31c2a99db0bd",
  "thread_id": "evidencia-01-consulta-politica-20261126T183256"
}
```

## Ejecución observada (log del servidor con este id_ejecucion)
```text
2026-11-26 18:32:56 INFO    [tarea_final] chat · a65dab23-1152-4a93-b336-31c2a99db0bd · aceptado en segundo plano (tope 90 s)
INFO:     127.0.0.1:46474 - "GET /registro/a65dab23-1152-4a93-b336-31c2a99db0bd HTTP/1.1" 200 OK
INFO:     127.0.0.1:46488 - "GET /registro/a65dab23-1152-4a93-b336-31c2a99db0bd HTTP/1.1" 200 OK
INFO:     127.0.0.1:46490 - "GET /registro/a65dab23-1152-4a93-b336-31c2a99db0bd HTTP/1.1" 200 OK
INFO:     127.0.0.1:46502 - "GET /registro/a65dab23-1152-4a93-b336-31c2a99db0bd HTTP/1.1" 200 OK
INFO:     127.0.0.1:46508 - "GET /registro/a65dab23-1152-4a93-b336-31c2a99db0bd HTTP/1.1" 200 OK
INFO:     127.0.0.1:46512 - "GET /registro/a65dab23-1152-4a93-b336-31c2a99db0bd HTTP/1.1" 200 OK
INFO:     127.0.0.1:49484 - "GET /registro/a65dab23-1152-4a93-b336-31c2a99db0bd HTTP/1.1" 200 OK
INFO:     127.0.0.1:49496 - "GET /registro/a65dab23-1152-4a93-b336-31c2a99db0bd HTTP/1.1" 200 OK
INFO:     127.0.0.1:49500 - "GET /registro/a65dab23-1152-4a93-b336-31c2a99db0bd HTTP/1.1" 200 OK
INFO:     127.0.0.1:49508 - "GET /registro/a65dab23-1152-4a93-b336-31c2a99db0bd HTTP/1.1" 200 OK
2026-11-26 18:33:06 INFO    [tarea_final] ejecución a65dab23-1152-4a93-b336-31c2a99db0bd · ruta=consulta_politica · estado=ok · 9654 ms · a2a=False · herramientas=buscar_politica
2026-11-26 18:33:06 INFO    [tarea_final] chat · a65dab23-1152-4a93-b336-31c2a99db0bd · «¿Cuál es el plazo máximo para rendir un gasto que hice en octubre?» → consulta_politica
INFO:     127.0.0.1:49518 - "GET /registro/a65dab23-1152-4a93-b336-31c2a99db0bd HTTP/1.1" 200 OK
```

## Resultado (`GET /registro/a65dab23-1152-4a93-b336-31c2a99db0bd` al terminar → `resultado`)
```json
{
  "id_ejecucion": "a65dab23-1152-4a93-b336-31c2a99db0bd",
  "thread_id": "evidencia-01-consulta-politica-20261126T183256",
  "ruta": "consulta_politica",
  "motivo": "El usuario pregunta sobre el plazo máximo para rendir un gasto sin presentar un caso concreto.",
  "respuesta": "Según la política de rendiciones:\n- **RG-03 — Plazo de rendición.** El gasto se rinde en el mismo mes en que se hizo o, como máximo, hasta el **día 10 del mes siguiente**. Fuera de ese plazo el gasto se **rechaza**, salvo que el informe incluya el visto bueno escrito del Gerente General; en ese caso queda **observado** para revisión. [Fuente: datos/politica_ficticia.md#reglas-generales/RG-03]",
  "estado_final": "ok",
  "hubo_a2a": false,
  "herramientas_usadas": [
    "buscar_politica"
  ],
  "pasos": 0
}
```

## Registro (`GET /registro/a65dab23-1152-4a93-b336-31c2a99db0bd` con `X-API-Key: ***` → HTTP 200)
```json
{
  "id_ejecucion": "a65dab23-1152-4a93-b336-31c2a99db0bd",
  "fecha": "2026-11-26T21:32:56.485699+00:00",
  "ruta": "consulta_politica",
  "pasos": 0,
  "herramientas_usadas": [
    "buscar_politica"
  ],
  "hubo_a2a": false,
  "estado_final": "ok",
  "duracion_ms": 9654,
  "estado": "ok",
  "thread_id": "evidencia-01-consulta-politica-20261126T183256",
  "inicio": "2026-11-26T21:32:56+00:00",
  "fin": "2026-11-26T21:33:06+00:00",
  "segundos": 9.7,
  "detail": null
}
```

Ruta obtenida: `consulta_politica` · estado_final: `ok` · coincide con la esperada.
