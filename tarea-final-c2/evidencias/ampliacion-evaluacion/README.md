# Evidencia: evaluación con golden set (+0,5)

Un conjunto de casos **versionado** (`evaluacion/golden_set.json`, v1.0), **ejecutado**
(`evaluacion/evaluar.py`) y con **resultados esperados** por turno (ruta y decisión).

| Archivo | Qué muestra | Estado |
|---|---|---|
| `informe-AAAAMMDDTHHMMSS.md` / `.json` | Fecha, versión del set, modelo, modo, commit, % de aciertos total y por grupo, fallos (con su `id_ejecucion`) y pendientes | formato del informe |
| `informe-20261124T213858.md` / `.json` | Primera corrida con Gemini (`gemini-3.5-flash-lite`, en proceso, verificador levantado): **router 59/59 rutas correctas**; 17/17 aciertos en los casos que ya se pueden evaluar (E, F, R, X); **40 casos pendientes** porque en esta rama todavía no están `revisar_caso` (Matías, 35 turnos) ni `responder_consulta` (Eduardo, 6 turnos). | hecho (2026-11-24). Reemplazada por la corrida final de abajo |
| **`informe-20261126T193234.md` / `.json`** | **Corrida final para la nota**, con todo unido (ReAct de Matías, RAG de Eduardo con Redis real, verificador A2A, Postgres) por `POST /chat` asíncrono: **57/57 casos (100 %), 59/59 turnos, router 59/59, 0 fallos, 0 pendientes, 0 errores, 0 `fallback`**. Armada en **3 corridas** (`--retomar`, 0 cortes por cuota) con `gemini-3.5-flash-lite` y respaldo `gemini-3.5-flash`; commits `ec09694` y `7279b78`, sin cambios de código del agente entre ellos. Con `MAX_PASOS_REACT=6` ningún caso llegó al tope de pasos (los 59 turnos terminan en `estado_final = ok`). Cada turno trae su `id_ejecucion` | **hecho (2026-11-26)** |

Cómo generarla (desde `tarea-final-c2/`, con `.env` completo):
```bash
python -m evaluacion.evaluar --validar     # 1) formato (no necesita Gemini)
python -m evaluacion.evaluar               # 2) corrida completa → escribe el informe aquí
python -m evaluacion.evaluar --pausa 20    #    lo mismo, con 20 s entre casos (cuota por minuto de Gemini)
python -m evaluacion.evaluar --retomar --pausa 20   # si se cortó por cuota: sigue donde quedó
```
Si se agota la cuota, la corrida se detiene sola (después de 2 reintentos), guarda el avance y dice
cómo seguir. El informe final indica en cuántas corridas se armó y con qué modelos.
Para la entrega conviene correrla cuando estén unidos los flujos de Matías (`revisar_gasto`) y de
Eduardo (`consulta_politica`): antes de eso, sus casos salen como **pendientes** (no cuentan).

Formato (2026-11-24): `--validar` → «golden set v1.0: formato correcto, 57 casos (59 turnos)».

Intento de corrida completa en `main` integrado (2026-11-24, con Postgres de prueba y verificador):
**se detuvo en el caso 16 de 57** porque se agotó la cuota de Gemini (`GoogleRateLimitError`). El
router cambió al respaldo, pero el ReAct todavía no tiene respaldo. No se guardó informe, porque
uno lleno de errores de cuota no mide al agente. Hay que repetirla con cuota disponible, `--pausa`,
`DATABASE_URL` y el verificador levantado, idealmente con Redis real.
