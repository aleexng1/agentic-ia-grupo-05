# Recorrido 03-revisar-gasto: ruta esperada `revisar_gasto`

Capturado el 2026-11-24T22:16:28-03:00 contra `http://127.0.0.1:8000` con `evidencias/dos-recorridos/capturar.py`.

## Entrada
```bash
curl -s -X POST http://127.0.0.1:8000/chat -H 'Content-Type: application/json' -H 'X-API-Key: ***' \
  -d '{"thread_id": "evidencia-03-revisar-gasto-20261124T221615", "texto": "Revisa este gasto rendido.", "gasto": {"id": "G-0101", "fecha_gasto": "2026-10-06", "fecha_rendicion": "2026-10-09", "monto": 7800, "tipo_documento": "boleta", "proveedor": "Concesionaria Vial Lago Verde", "glosa": "peaje ida y vuelta CD - tienda Norte, camión de reparto", "politica_declarada": "Viajes Internos", "categoria_declarada": "Peaje", "unidad_negocio": "CD", "patente": "RZPT41", "numero_ot": null, "vb_gerente_general": false, "id_fondo": "FR-001"}}'
```

## Ejecución observada (log del servidor con este id_ejecucion)
```text
2026-11-24 22:16:27 INFO    [tarea_final] ejecución e3e06ed6-7c81-4d03-89d9-9d68d8242f2d · ruta=revisar_gasto · estado=ok · 12254 ms · a2a=False · herramientas=buscar_politica,buscar_politica,consultar_fondo,validar_gasto,emitir_veredicto
2026-11-24 22:16:28 INFO    [tarea_final] chat · e3e06ed6-7c81-4d03-89d9-9d68d8242f2d · «Revisa este gasto rendido.» → revisar_gasto
```

## Resultado (HTTP 200)
```json
{
  "id_ejecucion": "e3e06ed6-7c81-4d03-89d9-9d68d8242f2d",
  "thread_id": "evidencia-03-revisar-gasto-20261124T221615",
  "ruta": "revisar_gasto",
  "motivo": "El mensaje solicita la revisión de un gasto concreto con datos estructurados adjuntos.",
  "respuesta": "Decisión: APROBAR\nPolítica: P02\nCategoría: Peaje\nCuenta: CTA-6100\nMotivo: El gasto cumple con todas las reglas aplicables de la política P02 (Viajes Internos), categoría Peaje, dentro del plazo de rendición, respaldado por boleta válida, con patente y saldo disponible suficiente en el fondo FR-001 (RG-08). No aplica la exclusión de P04 ya que peajes de viaje con vehículo de empresa corresponden a P02 o P03.",
  "estado_final": "ok",
  "hubo_a2a": false,
  "herramientas_usadas": [
    "buscar_politica",
    "buscar_politica",
    "consultar_fondo",
    "validar_gasto",
    "emitir_veredicto"
  ],
  "pasos": 5,
  "veredicto": {
    "decision": "aprobar",
    "motivo": "El gasto cumple con todas las reglas aplicables de la política P02 (Viajes Internos), categoría Peaje, dentro del plazo de rendición, respaldado por boleta válida, con patente y saldo disponible suficiente en el fondo FR-001 (RG-08). No aplica la exclusión de P04 ya que peajes de viaje con vehículo de empresa corresponden a P02 o P03.",
    "politica_sugerida": "P02",
    "categoria_sugerida": "Peaje",
    "cuenta_sugerida": "CTA-6100"
  }
}
```

## Registro (`GET /registro/e3e06ed6-7c81-4d03-89d9-9d68d8242f2d` con `X-API-Key: ***` → HTTP 200)
```json
{
  "id_ejecucion": "e3e06ed6-7c81-4d03-89d9-9d68d8242f2d",
  "fecha": "2026-11-25T01:16:15.726718+00:00",
  "ruta": "revisar_gasto",
  "pasos": 5,
  "herramientas_usadas": [
    "buscar_politica",
    "buscar_politica",
    "consultar_fondo",
    "validar_gasto",
    "emitir_veredicto"
  ],
  "hubo_a2a": false,
  "estado_final": "ok",
  "duracion_ms": 12254
}
```

Ruta obtenida: `revisar_gasto` · estado_final: `ok` · coincide con la esperada.
