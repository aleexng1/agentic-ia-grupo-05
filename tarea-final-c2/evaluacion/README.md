# evaluacion/

- `golden_set.json`: **golden set v1.0** de C2, versionado (campo `version` + `historial`). 57 casos,
  59 turnos, todo ficticio:
  - los 34 de c1 (grupos A a F) con su **ruta esperada**;
  - `R-router`: los 15 mensajes de `tests/test_router.py` (solo la ruta);
  - `X-fuera-de-alcance`: 4 pedidos fuera del alcance;
  - `V-verificacion`: 4 gastos con boleta (`datos/boletas/`) para la delegación A2A.
- `golden_set_c1.json`: los 34 casos originales de tarea-final-c1 (referencia, sin cambios).
- `evaluar.py`: corre los casos y escribe el informe en `evidencias/ampliacion-evaluacion/`.

```bash
python -m evaluacion.evaluar --validar                      # formato del set (sin Gemini)
python -m evaluacion.evaluar                                # contra el grafo, en este proceso
python -m evaluacion.evaluar --url http://127.0.0.1:8000    # contra /chat (local o Heroku)
python -m evaluacion.evaluar --grupo R-router               # un grupo
```

Se compara la **ruta** y, si el caso la trae, la **decisión**. Cada turno queda como acierto,
fallo, **pendiente** (la ruta es correcta pero el flujo de otra persona todavía no existe) o error
(no se pudo ejecutar). El % es aciertos / (aciertos + fallos).

- **Dueño:** Alex. Referencia que no se copió: `tarea-final-c1/pruebas/evaluar.py`.
