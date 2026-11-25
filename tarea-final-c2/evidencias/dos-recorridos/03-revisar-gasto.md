# Recorrido 03-revisar-gasto: ruta esperada `revisar_gasto`

Capturado el 2026-11-24T21:49:19-03:00 contra `http://127.0.0.1:8000` con `evidencias/dos-recorridos/capturar.py`.

## Entrada
```bash
curl -s -X POST http://127.0.0.1:8000/chat -H 'Content-Type: application/json' -H 'X-API-Key: ***' \
  -d '{"thread_id": "evidencia-03-revisar-gasto", "texto": "Revisa este gasto rendido.", "gasto": {"id": "G-0101", "fecha_gasto": "2026-10-06", "fecha_rendicion": "2026-10-09", "monto": 7800, "tipo_documento": "boleta", "proveedor": "Concesionaria Vial Lago Verde", "glosa": "peaje ida y vuelta CD - tienda Norte, camión de reparto", "politica_declarada": "Viajes Internos", "categoria_declarada": "Peaje", "unidad_negocio": "CD", "patente": "RZPT41", "numero_ot": null, "vb_gerente_general": false, "id_fondo": "FR-001"}}'
```

## Ejecución observada (log del servidor con este id_ejecucion)
```text
2026-11-24 21:49:18 INFO    [tarea_final] ejecución 35e1f958-617f-4ca7-b435-07a958f8bc71 · ruta=revisar_gasto · estado=error · 2350 ms · a2a=False · herramientas=-
2026-11-24 21:49:18 WARNING [tarea_final] ejecución 35e1f958-617f-4ca7-b435-07a958f8bc71 · guardar_ejecucion todavía no implementado: queda solo en el log
2026-11-24 21:49:18 INFO    [tarea_final] chat · 35e1f958-617f-4ca7-b435-07a958f8bc71 · «Revisa este gasto rendido.» → revisar_gasto
```

## Resultado (HTTP 200)
```json
{
  "id_ejecucion": "35e1f958-617f-4ca7-b435-07a958f8bc71",
  "thread_id": "evidencia-03-revisar-gasto",
  "ruta": "revisar_gasto",
  "motivo": "El mensaje solicita la revisión de un gasto concreto con datos estructurados adjuntos.",
  "respuesta": "Flujo revisar_gasto todavía no implementado.",
  "estado_final": "error",
  "hubo_a2a": false,
  "herramientas_usadas": [],
  "pasos": 0
}
```

Ruta obtenida: `revisar_gasto` · estado_final: `error` · coincide con la esperada.
