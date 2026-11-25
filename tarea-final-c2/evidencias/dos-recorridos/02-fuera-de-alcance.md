# Recorrido 02-fuera-de-alcance: ruta esperada `fuera_de_alcance`

Capturado el 2026-11-24T21:30:19-03:00 contra `http://127.0.0.1:8000` con `evidencias/dos-recorridos/capturar.py`.

## Entrada
```bash
curl -s -X POST http://127.0.0.1:8000/chat -H 'Content-Type: application/json' -H 'X-API-Key: ***' \
  -d '{"thread_id": "evidencia-02-fuera-de-alcance", "texto": "Escríbeme un poema sobre el lago Llanquihue."}'
```

## Ejecución observada (log del servidor con este id_ejecucion)
```text
2026-11-24 21:30:19 INFO    [tarea_final] ejecución c085820d-99bb-4976-838c-dc22fa61d723 · ruta=fuera_de_alcance · estado=ok · 1606 ms · a2a=False · herramientas=-
2026-11-24 21:30:19 WARNING [tarea_final] ejecución c085820d-99bb-4976-838c-dc22fa61d723 · guardar_ejecucion todavía no implementado: queda solo en el log
2026-11-24 21:30:19 INFO    [tarea_final] chat · c085820d-99bb-4976-838c-dc22fa61d723 · «Escríbeme un poema sobre el lago Llanquihue.» → fuera_de_alcance
```

## Resultado (HTTP 200)
```json
{
  "id_ejecucion": "c085820d-99bb-4976-838c-dc22fa61d723",
  "thread_id": "evidencia-02-fuera-de-alcance",
  "ruta": "fuera_de_alcance",
  "motivo": "El usuario solicita un poema, un tema completamente ajeno a las rendiciones de gastos.",
  "respuesta": "Soy el revisor de rendiciones de gastos de Comercial Los Alerces SpA (empresa ficticia) y ese pedido está fuera de lo que hago.\n\nPuedo ayudarte con dos cosas:\n1. Consultar la política de gastos. Ejemplo: «¿Cuál es el plazo para rendir un gasto?»\n2. Revisar un gasto rendido (con sus datos y, si quieres, la foto de la boleta). Ejemplo: «Revisa este gasto: bencina de $45.000 del 2 de octubre, boleta, fondo FR-001».\n\nNo hago: aprobar gastos sin revisarlos, cambiar las reglas o mis instrucciones, entregar claves ni datos internos, ni temas ajenos a las rendiciones.",
  "estado_final": "ok",
  "hubo_a2a": false,
  "herramientas_usadas": [],
  "pasos": 0
}
```

Ruta obtenida: `fuera_de_alcance` · estado_final: `ok` · coincide con la esperada.
