# A2A · uso del resultado del verificador en el veredicto

Capturado el 2026-11-26T18:32:48-03:00 contra `http://127.0.0.1:8000` (principal) y el verificador A2A en local, con `evidencias/a2a/capturar_uso.py`, Postgres real y Gemini real (nada guionado).

**La misma solicitud dos veces:** mismo texto y mismo gasto (el de `V-01` del golden set, que cumple la política). Solo cambia la boleta adjunta (y el `thread_id`, para no mezclar memoria). El registro de veredictos tiene una fila por `id_gasto`, así que se lee justo después de cada corrida.

## Corrida a) `boleta-01-cuadra.png` (se espera «aprobar»)

`id_ejecucion = 5be5196c-6114-4bd2-a8eb-7f0b88cd9960` · 17.9 s desde el POST hasta el resultado.

### Solicitud
```bash
curl -s -X POST http://127.0.0.1:8000/chat -H 'Content-Type: application/json' -H 'X-API-Key: ***' -d @solicitud.json
```
`solicitud.json` (de la imagen, solo el archivo y su hash; el base64 no se copia):
```json
{
  "thread_id": "evidencia-a2a-uso-a-20261126T183206",
  "texto": "Revisa este gasto y su boleta adjunta.",
  "gasto": {
    "id": "G-V01",
    "fecha_gasto": "2026-10-02",
    "fecha_rendicion": "2026-10-06",
    "monto": 45000,
    "tipo_documento": "boleta",
    "proveedor": "Estación de Servicio El Roble (ficticia)",
    "glosa": "Bencina auto propio para visitar tiendas de Temuco",
    "politica_declarada": "Vehículos Propios",
    "categoria_declarada": "Gasolina (vehículo propio)",
    "unidad_negocio": "TIE",
    "id_fondo": "FR-001",
    "rut_emisor": "11.111.111-1",
    "folio": "000123"
  },
  "imagen": {
    "archivo": "boleta-01-cuadra.png",
    "mime_type": "image/png",
    "bytes": 42579,
    "sha256": "dbd473e801de6cdce8c15bfcdad62d371fc7abcba3730b15e4f85af3927a6c00",
    "datos_base64": "(omitido)"
  }
}
```
Respuesta inmediata (HTTP 202):
```json
{
  "id_ejecucion": "5be5196c-6114-4bd2-a8eb-7f0b88cd9960",
  "estado": "en_proceso",
  "consultar": "/registro/5be5196c-6114-4bd2-a8eb-7f0b88cd9960",
  "thread_id": "evidencia-a2a-uso-a-20261126T183206"
}
```

### Encargo A2A (principal → verificador)
Parte de archivo (la imagen: tipo, tamaño y hash) + parte de datos (lo declarado, `declarado_para_verificador`):
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

### Respuesta del verificador
| Campo | Declarado | Leído en la boleta | ¿Cuadra? |
|---|---|---|---|
| monto | 45000 | 45000 | sí |
| fecha | 2026-10-02 | 2026-10-02 | sí |
| rut_emisor | 11.111.111-1 | 11.111.111-1 | sí |
| folio | 000123 | 000123 | sí |
| categoria | Gasolina (vehículo propio) | Gasolina 95 octanos | sí |

Confianza: **1.0** · disponible: True · observaciones: «Documento legible y datos extraídos correctamente.»
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

### Cómo se usó el resultado
- Propuesta del ReAct (`emitir_veredicto`, antes del juez y de los pisos): **aprobar**
- Veredicto final en `/chat`: **aprobar** · `estado_final = ok`
- Fila del registro de veredictos: **aprobar**

**Dónde se usó:** Todos los campos cuadran: **el piso por verificación de `nodo_cerrar`** revisó el resultado y no cambió nada, así que se registra la propuesta del ReAct («aprobar»).

Trazas del ReAct (`MOSTRAR_TRAZAS=1`: juez, pisos y cierre):
```text
── [juez] ──
{
  "valido": true,
  "razon": "El veredicto de aprobación está justificado. La política P01 es correcta para gasolina en auto propio según P01 y RG-06, el documento (boleta) es válido por RG-01, el plazo de rendición cumple con RG-03, y la validación determinista confirma que cumple sin incumplimientos.",
  "evaluado": true,
  "uso_respaldo": false
}
```

### Resultado
`GET /registro/5be5196c-6114-4bd2-a8eb-7f0b88cd9960` → `resultado` (lo que entrega `/chat`):
```json
{
  "id_ejecucion": "5be5196c-6114-4bd2-a8eb-7f0b88cd9960",
  "thread_id": "evidencia-a2a-uso-a-20261126T183206",
  "ruta": "revisar_gasto",
  "motivo": "El mensaje adjunta un gasto estructurado y una imagen solicitando su revisión.",
  "respuesta": "Decisión: APROBAR\nPolítica: P01\nCategoría: Gasolina (vehículo propio)\nCuenta: CTA-5100\nMotivo: El gasto cumple con todas las reglas de la política P01 (Vehículos Propios), cuenta con boleta válida, fue rendido dentro del plazo (RG-03), el monto no supera el saldo disponible del fondo (RG-08) y la clasificación declarada es correcta.\n\nVerificación de la boleta (confianza 1.00): todos los campos coinciden con lo declarado.",
  "estado_final": "ok",
  "hubo_a2a": true,
  "herramientas_usadas": [
    "delegar_verificador",
    "buscar_politica",
    "consultar_fondo",
    "validar_gasto",
    "emitir_veredicto"
  ],
  "pasos": 4,
  "veredicto": {
    "decision": "aprobar",
    "motivo": "El gasto cumple con todas las reglas de la política P01 (Vehículos Propios), cuenta con boleta válida, fue rendido dentro del plazo (RG-03), el monto no supera el saldo disponible del fondo (RG-08) y la clasificación declarada es correcta.",
    "politica_sugerida": "P01",
    "categoria_sugerida": "Gasolina (vehículo propio)",
    "cuenta_sugerida": "CTA-5100"
  },
  "verificacion": {
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
}
```
El resto de `GET /registro/{id}` (estado y fila de `ejecuciones`):
```json
{
  "id_ejecucion": "5be5196c-6114-4bd2-a8eb-7f0b88cd9960",
  "fecha": "2026-11-26T21:32:06.411083+00:00",
  "ruta": "revisar_gasto",
  "pasos": 4,
  "herramientas_usadas": [
    "delegar_verificador",
    "buscar_politica",
    "consultar_fondo",
    "validar_gasto",
    "emitir_veredicto"
  ],
  "hubo_a2a": true,
  "estado_final": "ok",
  "duracion_ms": 16809,
  "estado": "ok",
  "thread_id": "evidencia-a2a-uso-a-20261126T183206",
  "inicio": "2026-11-26T21:32:06+00:00",
  "fin": "2026-11-26T21:32:23+00:00",
  "segundos": 16.8,
  "detail": null
}
```
Fila del registro de veredictos (`veredictos`, Postgres), leída justo después de esta corrida:
```json
{
  "id_gasto": "G-V01",
  "id_fondo": "FR-001",
  "monto": 45000,
  "decision": "aprobar",
  "motivo": "El gasto cumple con todas las reglas de la política P01 (Vehículos Propios), cuenta con boleta válida, fue rendido dentro del plazo (RG-03), el monto no supera el saldo disponible del fondo (RG-08) y la clasificación declarada es correcta.",
  "politica_sugerida": "P01",
  "categoria_sugerida": "Gasolina (vehículo propio)",
  "cuenta_sugerida": "CTA-5100",
  "registrado_en": "2026-11-26T21:32:23.202463+00:00"
}
```

### Log del principal (este id_ejecucion y el canal A2A)
```text
2026-11-26 18:32:06 INFO    [tarea_final] chat · 5be5196c-6114-4bd2-a8eb-7f0b88cd9960 · aceptado en segundo plano (tope 90 s)
INFO:     127.0.0.1:48280 - "GET /registro/5be5196c-6114-4bd2-a8eb-7f0b88cd9960 HTTP/1.1" 200 OK
INFO:     127.0.0.1:48284 - "GET /registro/5be5196c-6114-4bd2-a8eb-7f0b88cd9960 HTTP/1.1" 200 OK
2026-11-26 18:32:08 INFO    [tarea_final] a2a · encargo → http://127.0.0.1:8001 · imagen image/png 42579 bytes · tiempo límite 20 s
INFO:     127.0.0.1:48290 - "GET /registro/5be5196c-6114-4bd2-a8eb-7f0b88cd9960 HTTP/1.1" 200 OK
INFO:     127.0.0.1:48302 - "GET /registro/5be5196c-6114-4bd2-a8eb-7f0b88cd9960 HTTP/1.1" 200 OK
INFO:     127.0.0.1:48318 - "GET /registro/5be5196c-6114-4bd2-a8eb-7f0b88cd9960 HTTP/1.1" 200 OK
2026-11-26 18:32:11 INFO    [tarea_final] a2a · respuesta ← verificador · confianza=1.00 · no cuadra: -
INFO:     127.0.0.1:48330 - "GET /registro/5be5196c-6114-4bd2-a8eb-7f0b88cd9960 HTTP/1.1" 200 OK
INFO:     127.0.0.1:56790 - "GET /registro/5be5196c-6114-4bd2-a8eb-7f0b88cd9960 HTTP/1.1" 200 OK
INFO:     127.0.0.1:56798 - "GET /registro/5be5196c-6114-4bd2-a8eb-7f0b88cd9960 HTTP/1.1" 200 OK
INFO:     127.0.0.1:56802 - "GET /registro/5be5196c-6114-4bd2-a8eb-7f0b88cd9960 HTTP/1.1" 200 OK
INFO:     127.0.0.1:56808 - "GET /registro/5be5196c-6114-4bd2-a8eb-7f0b88cd9960 HTTP/1.1" 200 OK
INFO:     127.0.0.1:56814 - "GET /registro/5be5196c-6114-4bd2-a8eb-7f0b88cd9960 HTTP/1.1" 200 OK
INFO:     127.0.0.1:56816 - "GET /registro/5be5196c-6114-4bd2-a8eb-7f0b88cd9960 HTTP/1.1" 200 OK
INFO:     127.0.0.1:56818 - "GET /registro/5be5196c-6114-4bd2-a8eb-7f0b88cd9960 HTTP/1.1" 200 OK
INFO:     127.0.0.1:56832 - "GET /registro/5be5196c-6114-4bd2-a8eb-7f0b88cd9960 HTTP/1.1" 200 OK
INFO:     127.0.0.1:56838 - "GET /registro/5be5196c-6114-4bd2-a8eb-7f0b88cd9960 HTTP/1.1" 200 OK
INFO:     127.0.0.1:56842 - "GET /registro/5be5196c-6114-4bd2-a8eb-7f0b88cd9960 HTTP/1.1" 200 OK
INFO:     127.0.0.1:46502 - "GET /registro/5be5196c-6114-4bd2-a8eb-7f0b88cd9960 HTTP/1.1" 200 OK
2026-11-26 18:32:23 INFO    [tarea_final] ejecución 5be5196c-6114-4bd2-a8eb-7f0b88cd9960 · ruta=revisar_gasto · estado=ok · 16809 ms · a2a=True · herramientas=delegar_verificador,buscar_politica,consultar_fondo,validar_gasto,emitir_veredicto
2026-11-26 18:32:23 INFO    [tarea_final] chat · 5be5196c-6114-4bd2-a8eb-7f0b88cd9960 · «Revisa este gasto y su boleta adjunta.» → revisar_gasto
INFO:     127.0.0.1:46512 - "GET /registro/5be5196c-6114-4bd2-a8eb-7f0b88cd9960 HTTP/1.1" 200 OK
```
### Log del verificador (este encargo, por el hash de la imagen)
```text
2026-11-26 18:32:08 INFO    [tarea_final] verificador · encargo e6303469 · imagen image/png 42579 bytes sha256:dbd473e801de6cdc · declarado monto=45000 fecha=2026-10-02 folio=000123
2026-11-26 18:32:11 INFO    [tarea_final] verificador · respuesta e6303469 · confianza=1.00 · no cuadra: -
```

## Corrida b) `boleta-05-monto-distinto-01.png` (se espera «observar»)

`id_ejecucion = f0b7ffea-caef-4098-8fe0-660198f552b7` · 21.9 s desde el POST hasta el resultado.

### Solicitud
```bash
curl -s -X POST http://127.0.0.1:8000/chat -H 'Content-Type: application/json' -H 'X-API-Key: ***' -d @solicitud.json
```
`solicitud.json` (de la imagen, solo el archivo y su hash; el base64 no se copia):
```json
{
  "thread_id": "evidencia-a2a-uso-b-20261126T183225",
  "texto": "Revisa este gasto y su boleta adjunta.",
  "gasto": {
    "id": "G-V01",
    "fecha_gasto": "2026-10-02",
    "fecha_rendicion": "2026-10-06",
    "monto": 45000,
    "tipo_documento": "boleta",
    "proveedor": "Estación de Servicio El Roble (ficticia)",
    "glosa": "Bencina auto propio para visitar tiendas de Temuco",
    "politica_declarada": "Vehículos Propios",
    "categoria_declarada": "Gasolina (vehículo propio)",
    "unidad_negocio": "TIE",
    "id_fondo": "FR-001",
    "rut_emisor": "11.111.111-1",
    "folio": "000123"
  },
  "imagen": {
    "archivo": "boleta-05-monto-distinto-01.png",
    "mime_type": "image/png",
    "bytes": 43082,
    "sha256": "408fa81dd06eb41f9fa63b84b84eee1d137b33bf6ddaa40db760d271d364aa64",
    "datos_base64": "(omitido)"
  }
}
```
Respuesta inmediata (HTTP 202):
```json
{
  "id_ejecucion": "f0b7ffea-caef-4098-8fe0-660198f552b7",
  "estado": "en_proceso",
  "consultar": "/registro/f0b7ffea-caef-4098-8fe0-660198f552b7",
  "thread_id": "evidencia-a2a-uso-b-20261126T183225"
}
```

### Encargo A2A (principal → verificador)
Parte de archivo (la imagen: tipo, tamaño y hash) + parte de datos (lo declarado, `declarado_para_verificador`):
```json
{
  "imagen": {
    "archivo": "boleta-05-monto-distinto-01.png",
    "mime_type": "image/png",
    "bytes": 43082,
    "sha256_inicio": "408fa81dd06eb41f"
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

### Respuesta del verificador
| Campo | Declarado | Leído en la boleta | ¿Cuadra? |
|---|---|---|---|
| monto | 45000 | 54000 | no |
| fecha | 2026-10-02 | 2026-10-02 | sí |
| rut_emisor | 11.111.111-1 | 11.111.111-1 | sí |
| folio | 000123 | 000123 | sí |
| categoria | Gasolina (vehículo propio) | Gasolina 95 octanos | sí |

Confianza: **1.0** · disponible: True · observaciones: «Documento legible y datos completos.»
```json
{
  "disponible": true,
  "leido": {
    "monto": 54000,
    "fecha": "2026-10-02",
    "rut_emisor": "11.111.111-1",
    "folio": "000123",
    "categoria": "Gasolina 95 octanos"
  },
  "cuadra": {
    "monto": "no",
    "fecha": "sí",
    "rut_emisor": "sí",
    "folio": "sí",
    "categoria": "sí"
  },
  "confianza": 1.0,
  "observaciones": "Documento legible y datos completos."
}
```

### Cómo se usó el resultado
- Propuesta del ReAct (`emitir_veredicto`, antes del juez y de los pisos): **aprobar**
- Veredicto final en `/chat`: **observar** · `estado_final = ok`
- Fila del registro de veredictos: **observar**

**Dónde se usó:** **El piso por verificación de `nodo_cerrar`** (`src/principal/flujos/revisar_gasto.py`, `motivo_piso_verificacion`) bajó la propuesta del ReAct de «aprobar» a «observar» **antes** de `registrar_veredicto`, porque la boleta no coincide con lo declarado en monto.

Trazas del ReAct (`MOSTRAR_TRAZAS=1`: juez, pisos y cierre):
```text
── [juez] ──
{
  "valido": true,
  "razon": "El veredicto de aprobación está justificado. La política P01 es correcta para combustible en vehículo propio (RG-06), el documento es una boleta válida (RG-01), la rendición está en plazo (RG-03), y la validación determinista confirma el cumplimiento sin incumplimientos.",
  "evaluado": true,
  "uso_respaldo": false
}
── [piso_verificacion] ──
{
  "gasto": "G-V01",
  "motivo": "la boleta no coincide con lo declarado en monto"
}
```

### Resultado
`GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7` → `resultado` (lo que entrega `/chat`):
```json
{
  "id_ejecucion": "f0b7ffea-caef-4098-8fe0-660198f552b7",
  "thread_id": "evidencia-a2a-uso-b-20261126T183225",
  "ruta": "revisar_gasto",
  "motivo": "El mensaje adjunta un gasto estructurado y una boleta solicitando su revisión.",
  "respuesta": "Decisión: OBSERVAR\n\nAjusté la propuesta del agente (APROBAR): la boleta no coincide con lo declarado en monto.\n\nVerificación de la boleta (confianza 1.00): no coincide en monto.",
  "estado_final": "ok",
  "hubo_a2a": true,
  "herramientas_usadas": [
    "delegar_verificador",
    "buscar_politica",
    "consultar_fondo",
    "validar_gasto",
    "emitir_veredicto"
  ],
  "pasos": 4,
  "veredicto": {
    "decision": "observar",
    "motivo": "El gasto cumple con todas las normativas aplicables de la política P01 Vehículos Propios (categoría Gasolina vehículo propio). El documento (boleta) es válido, el plazo de rendición está dentro del mes vigente (RG-03), el saldo del fondo FR-001 cubre el monto rendido (RG-08) y la validación determinista confirma que cumple correctamente sin observaciones. [Ajustado de APROBAR a OBSERVAR: la boleta no coincide con lo declarado en monto.]",
    "politica_sugerida": "P01",
    "categoria_sugerida": "Gasolina (vehículo propio)",
    "cuenta_sugerida": "CTA-5100"
  },
  "verificacion": {
    "disponible": true,
    "leido": {
      "monto": 54000,
      "fecha": "2026-10-02",
      "rut_emisor": "11.111.111-1",
      "folio": "000123",
      "categoria": "Gasolina 95 octanos"
    },
    "cuadra": {
      "monto": "no",
      "fecha": "sí",
      "rut_emisor": "sí",
      "folio": "sí",
      "categoria": "sí"
    },
    "confianza": 1.0,
    "observaciones": "Documento legible y datos completos."
  }
}
```
El resto de `GET /registro/{id}` (estado y fila de `ejecuciones`):
```json
{
  "id_ejecucion": "f0b7ffea-caef-4098-8fe0-660198f552b7",
  "fecha": "2026-11-26T21:32:25.352071+00:00",
  "ruta": "revisar_gasto",
  "pasos": 4,
  "herramientas_usadas": [
    "delegar_verificador",
    "buscar_politica",
    "consultar_fondo",
    "validar_gasto",
    "emitir_veredicto"
  ],
  "hubo_a2a": true,
  "estado_final": "ok",
  "duracion_ms": 21773,
  "estado": "ok",
  "thread_id": "evidencia-a2a-uso-b-20261126T183225",
  "inicio": "2026-11-26T21:32:25+00:00",
  "fin": "2026-11-26T21:32:47+00:00",
  "segundos": 21.8,
  "detail": null
}
```
Fila del registro de veredictos (`veredictos`, Postgres), leída justo después de esta corrida:
```json
{
  "id_gasto": "G-V01",
  "id_fondo": "FR-001",
  "monto": 45000,
  "decision": "observar",
  "motivo": "El gasto cumple con todas las normativas aplicables de la política P01 Vehículos Propios (categoría Gasolina vehículo propio). El documento (boleta) es válido, el plazo de rendición está dentro del mes vigente (RG-03), el saldo del fondo FR-001 cubre el monto rendido (RG-08) y la validación determinista confirma que cumple correctamente sin observaciones. [Ajustado de APROBAR a OBSERVAR: la boleta no coincide con lo declarado en monto.]",
  "politica_sugerida": "P01",
  "categoria_sugerida": "Gasolina (vehículo propio)",
  "cuenta_sugerida": "CTA-5100",
  "registrado_en": "2026-11-26T21:32:47.107636+00:00"
}
```

### Log del principal (este id_ejecucion y el canal A2A)
```text
2026-11-26 18:32:25 INFO    [tarea_final] chat · f0b7ffea-caef-4098-8fe0-660198f552b7 · aceptado en segundo plano (tope 90 s)
INFO:     127.0.0.1:46538 - "GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7 HTTP/1.1" 200 OK
INFO:     127.0.0.1:46544 - "GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7 HTTP/1.1" 200 OK
2026-11-26 18:32:27 INFO    [tarea_final] a2a · encargo → http://127.0.0.1:8001 · imagen image/png 43082 bytes · tiempo límite 20 s
INFO:     127.0.0.1:46556 - "GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7 HTTP/1.1" 200 OK
INFO:     127.0.0.1:46566 - "GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7 HTTP/1.1" 200 OK
INFO:     127.0.0.1:46582 - "GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7 HTTP/1.1" 200 OK
2026-11-26 18:32:30 INFO    [tarea_final] a2a · respuesta ← verificador · confianza=1.00 · no cuadra: monto
INFO:     127.0.0.1:46586 - "GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7 HTTP/1.1" 200 OK
INFO:     127.0.0.1:46596 - "GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7 HTTP/1.1" 200 OK
INFO:     127.0.0.1:60978 - "GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7 HTTP/1.1" 200 OK
INFO:     127.0.0.1:60992 - "GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7 HTTP/1.1" 200 OK
INFO:     127.0.0.1:32770 - "GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7 HTTP/1.1" 200 OK
INFO:     127.0.0.1:32782 - "GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7 HTTP/1.1" 200 OK
INFO:     127.0.0.1:32786 - "GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7 HTTP/1.1" 200 OK
INFO:     127.0.0.1:32794 - "GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7 HTTP/1.1" 200 OK
INFO:     127.0.0.1:32798 - "GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7 HTTP/1.1" 200 OK
INFO:     127.0.0.1:32812 - "GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7 HTTP/1.1" 200 OK
INFO:     127.0.0.1:32824 - "GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7 HTTP/1.1" 200 OK
INFO:     127.0.0.1:32838 - "GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7 HTTP/1.1" 200 OK
INFO:     127.0.0.1:58738 - "GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7 HTTP/1.1" 200 OK
INFO:     127.0.0.1:58744 - "GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7 HTTP/1.1" 200 OK
INFO:     127.0.0.1:58760 - "GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7 HTTP/1.1" 200 OK
INFO:     127.0.0.1:58766 - "GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7 HTTP/1.1" 200 OK
2026-11-26 18:32:47 INFO    [tarea_final] ejecución f0b7ffea-caef-4098-8fe0-660198f552b7 · ruta=revisar_gasto · estado=ok · 21773 ms · a2a=True · herramientas=delegar_verificador,buscar_politica,consultar_fondo,validar_gasto,emitir_veredicto
2026-11-26 18:32:47 INFO    [tarea_final] chat · f0b7ffea-caef-4098-8fe0-660198f552b7 · «Revisa este gasto y su boleta adjunta.» → revisar_gasto
INFO:     127.0.0.1:58774 - "GET /registro/f0b7ffea-caef-4098-8fe0-660198f552b7 HTTP/1.1" 200 OK
```
### Log del verificador (este encargo, por el hash de la imagen)
```text
2026-11-26 18:32:27 INFO    [tarea_final] verificador · encargo 3e981b31 · imagen image/png 43082 bytes sha256:408fa81dd06eb41f · declarado monto=45000 fecha=2026-10-02 folio=000123
2026-11-26 18:32:30 INFO    [tarea_final] verificador · respuesta 3e981b31 · confianza=1.00 · no cuadra: monto
```

## Comparación

| | a) | b) |
|---|---|---|
| Boleta | `boleta-01-cuadra.png` (`dbd473e801de6cdc…`) | `boleta-05-monto-distinto-01.png` (`408fa81dd06eb41f…`) |
| `id_ejecucion` | `5be5196c-6114-4bd2-a8eb-7f0b88cd9960` | `f0b7ffea-caef-4098-8fe0-660198f552b7` |
| Datos declarados | iguales (V-01) | iguales (V-01) |
| Campos que no cuadran | ninguno | monto |
| Confianza del verificador | 1.0 | 1.0 |
| Propuesta del ReAct | aprobar | aprobar |
| Juez | valida | valida |
| Piso por verificación (`nodo_cerrar`) | no cambió nada | bajó a «observar» |
| Veredicto en `/chat` | **aprobar** | **observar** |
| Registro de veredictos | aprobar | observar |
| `estado_final` | ok | ok |
| Esperado | aprobar | observar |

**Cumple:** con los mismos datos declarados, la boleta que cuadra termina en «aprobar» y la que no cuadra en «observar», en `/chat` y en el registro.
