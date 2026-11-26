# Recorrido 03-revisar-gasto: ruta esperada `revisar_gasto`

Capturado el 2026-11-26T18:33:34-03:00 contra `http://127.0.0.1:8000` con `evidencias/dos-recorridos/capturar.py`.

## Entrada
```bash
curl -s -X POST http://127.0.0.1:8000/chat -H 'Content-Type: application/json' -H 'X-API-Key: ***' \
  -d '{"thread_id": "evidencia-03-revisar-gasto-20261126T183307", "texto": "Revisa este gasto rendido.", "gasto": {"id": "G-0101", "fecha_gasto": "2026-10-06", "fecha_rendicion": "2026-10-09", "monto": 7800, "tipo_documento": "boleta", "proveedor": "Concesionaria Vial Lago Verde", "glosa": "peaje ida y vuelta CD - tienda Norte, camión de reparto", "politica_declarada": "Viajes Internos", "categoria_declarada": "Peaje", "unidad_negocio": "CD", "patente": "RZPT41", "numero_ot": null, "vb_gerente_general": false, "id_fondo": "FR-001"}}'
```

Respuesta inmediata (HTTP 202, `/chat` asíncrono):
```json
{
  "id_ejecucion": "785ff949-e96b-43dc-bdf3-3088cda484bb",
  "estado": "en_proceso",
  "consultar": "/registro/785ff949-e96b-43dc-bdf3-3088cda484bb",
  "thread_id": "evidencia-03-revisar-gasto-20261126T183307"
}
```

## Ejecución observada (log del servidor con este id_ejecucion)
```text
2026-11-26 18:33:07 INFO    [tarea_final] chat · 785ff949-e96b-43dc-bdf3-3088cda484bb · aceptado en segundo plano (tope 90 s)
INFO:     127.0.0.1:49550 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:49556 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:49568 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:49570 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:49584 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:43226 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:43232 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:43244 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:43250 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:43264 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:43268 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:43284 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:43294 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:43308 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:45042 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:45056 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:45068 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:45074 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:45090 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:45094 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:45096 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:45104 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:45118 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:45122 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
INFO:     127.0.0.1:34424 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
2026-11-26 18:33:33 INFO    [tarea_final] ejecución 785ff949-e96b-43dc-bdf3-3088cda484bb · ruta=revisar_gasto · estado=ok · 25546 ms · a2a=False · herramientas=buscar_politica,consultar_fondo,validar_gasto,emitir_veredicto
2026-11-26 18:33:33 INFO    [tarea_final] chat · 785ff949-e96b-43dc-bdf3-3088cda484bb · «Revisa este gasto rendido.» → revisar_gasto
INFO:     127.0.0.1:34426 - "GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb HTTP/1.1" 200 OK
```

## Resultado (`GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb` al terminar → `resultado`)
```json
{
  "id_ejecucion": "785ff949-e96b-43dc-bdf3-3088cda484bb",
  "thread_id": "evidencia-03-revisar-gasto-20261126T183307",
  "ruta": "revisar_gasto",
  "motivo": "El mensaje solicita la revisión de un gasto concreto con datos estructurados adjuntos.",
  "respuesta": "Decisión: APROBAR\nPolítica: P02\nCategoría: Peaje\nCuenta: CTA-6100\nMotivo: El gasto cumple con todas las reglas de la política P02 (Viajes Internos) y la categoría Peaje. El documento es una boleta válida, se encuentra dentro del plazo de rendición (RG-03), el saldo del fondo por rendir cubre el monto (RG-08) y no presenta incumplimientos normativos.",
  "estado_final": "ok",
  "hubo_a2a": false,
  "herramientas_usadas": [
    "buscar_politica",
    "consultar_fondo",
    "validar_gasto",
    "emitir_veredicto"
  ],
  "pasos": 4,
  "veredicto": {
    "decision": "aprobar",
    "motivo": "El gasto cumple con todas las reglas de la política P02 (Viajes Internos) y la categoría Peaje. El documento es una boleta válida, se encuentra dentro del plazo de rendición (RG-03), el saldo del fondo por rendir cubre el monto (RG-08) y no presenta incumplimientos normativos.",
    "politica_sugerida": "P02",
    "categoria_sugerida": "Peaje",
    "cuenta_sugerida": "CTA-6100"
  }
}
```

## Registro (`GET /registro/785ff949-e96b-43dc-bdf3-3088cda484bb` con `X-API-Key: ***` → HTTP 200)
```json
{
  "id_ejecucion": "785ff949-e96b-43dc-bdf3-3088cda484bb",
  "fecha": "2026-11-26T21:33:07.889388+00:00",
  "ruta": "revisar_gasto",
  "pasos": 4,
  "herramientas_usadas": [
    "buscar_politica",
    "consultar_fondo",
    "validar_gasto",
    "emitir_veredicto"
  ],
  "hubo_a2a": false,
  "estado_final": "ok",
  "duracion_ms": 25546,
  "estado": "ok",
  "thread_id": "evidencia-03-revisar-gasto-20261126T183307",
  "inicio": "2026-11-26T21:33:07+00:00",
  "fin": "2026-11-26T21:33:33+00:00",
  "segundos": 25.6,
  "detail": null
}
```

Ruta obtenida: `revisar_gasto` · estado_final: `ok` · coincide con la esperada.
