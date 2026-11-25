# Recorrido 01-consulta-politica: ruta esperada `consulta_politica`

Capturado el 2026-11-24T21:30:17-03:00 contra `http://127.0.0.1:8000` con `evidencias/dos-recorridos/capturar.py`.

## Entrada
```bash
curl -s -X POST http://127.0.0.1:8000/chat -H 'Content-Type: application/json' -H 'X-API-Key: ***' \
  -d '{"thread_id": "evidencia-01-consulta-politica", "texto": "¿Cuál es el plazo máximo para rendir un gasto que hice en octubre?"}'
```

## Ejecución observada (log del servidor con este id_ejecucion)
```text
2026-11-24 21:30:17 INFO    [tarea_final] ejecución ae89c418-148a-4809-9248-d1d64a4597d7 · ruta=consulta_politica · estado=error · 1722 ms · a2a=False · herramientas=-
2026-11-24 21:30:17 WARNING [tarea_final] ejecución ae89c418-148a-4809-9248-d1d64a4597d7 · guardar_ejecucion todavía no implementado: queda solo en el log
2026-11-24 21:30:17 INFO    [tarea_final] chat · ae89c418-148a-4809-9248-d1d64a4597d7 · «¿Cuál es el plazo máximo para rendir un gasto que hice en octubre?» → consulta_politica
```

## Resultado (HTTP 200)
```json
{
  "id_ejecucion": "ae89c418-148a-4809-9248-d1d64a4597d7",
  "thread_id": "evidencia-01-consulta-politica",
  "ruta": "consulta_politica",
  "motivo": "El usuario pregunta sobre el plazo máximo para rendir un gasto sin presentar un caso concreto.",
  "respuesta": "Flujo consulta_politica todavía no implementado.",
  "estado_final": "error",
  "hubo_a2a": false,
  "herramientas_usadas": [],
  "pasos": 0
}
```

Ruta obtenida: `consulta_politica` · estado_final: `error` · coincide con la esperada.
