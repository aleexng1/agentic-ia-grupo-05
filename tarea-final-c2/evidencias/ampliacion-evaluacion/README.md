# Evidencia: evaluación con golden set (+0,5)

Un conjunto de casos **versionado** (`evaluacion/golden_set.json`, v1.0), **ejecutado**
(`evaluacion/evaluar.py`) y con **resultados esperados** por turno (ruta y decisión).

| Archivo | Qué muestra | Estado |
|---|---|---|
| `informe-AAAAMMDDTHHMMSS.md` / `.json` | Fecha, versión del set, modelo, modo, commit, % de aciertos total y por grupo, fallos (con su `id_ejecucion`) y pendientes | **pendiente** (falta `GOOGLE_API_KEY`) |

Cómo generarla (desde `tarea-final-c2/`, con `.env` completo):
```bash
python -m evaluacion.evaluar --validar     # 1) formato (no necesita Gemini)
python -m evaluacion.evaluar               # 2) corrida completa → escribe el informe aquí
```
Para la entrega conviene correrla cuando estén unidos los flujos de Matías (`revisar_gasto`) y de
Eduardo (`consulta_politica`): antes de eso, sus casos salen como **pendientes** (no cuentan).

Hecho sin Gemini (2026-11-24): `--validar` → «golden set v1.0: formato correcto, 57 casos (59 turnos)».
