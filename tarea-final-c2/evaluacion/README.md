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
python -m evaluacion.evaluar --pausa 20                     # 20 s entre casos (cuota por minuto)
python -m evaluacion.evaluar --retomar --pausa 20           # sigue desde el avance parcial
python -m evaluacion.evaluar --desde GS-17                  # (re)corre desde ese caso (id o posición)
```

**Corridas largas y cuota de Gemini.**
- Después de cada caso, el avance se guarda en `evidencias/ampliacion-evaluacion/avance-parcial.json`
  (git lo ignora).
- Ante un 429 / `RESOURCE_EXHAUSTED`, el caso se reintenta hasta 2 veces (30 s y 60 s;
  `--espera-cuota` cambia la primera espera). Si sigue sin cuota, la corrida se detiene sola con
  código 3 y dice desde qué caso seguir.
- Ese caso no cuenta como fallo ni como error del agente: al retomar se vuelve a correr completo, en
  un hilo nuevo.
- Si hay un avance y no se pasa `--retomar`, el evaluador no lo pisa (`--nuevo` lo descarta).
- El informe final se escribe solo con todos los casos. Dice en cuántas corridas se armó y con qué
  modelos (principal y respaldo, por corrida). Después se borra el avance.

Se compara la **ruta** y, si el caso la trae, la **decisión**. Cada turno queda como acierto,
fallo, **pendiente** (la ruta es correcta pero el flujo de otra persona todavía no existe) o error
(no se pudo ejecutar). El % es aciertos / (aciertos + fallos).

- **Dueño:** Alex. Referencia que no se copió: `tarea-final-c1/pruebas/evaluar.py`.
