# Evidencia: evaluación con golden set (+0,5)

Un conjunto de casos **versionado** (`evaluacion/golden_set.json`, v1.0), **ejecutado**
(`evaluacion/evaluar.py`) y con **resultados esperados** por turno (ruta y decisión).

| Archivo | Qué muestra | Estado |
|---|---|---|
| `informe-AAAAMMDDTHHMMSS.md` / `.json` | Fecha, versión del set, modelo, modo, commit, % de aciertos total y por grupo, fallos (con su `id_ejecucion`) y pendientes | formato del informe |
| `informe-20261124T213858.md` / `.json` | Primera corrida con Gemini (`gemini-3.5-flash-lite`, en proceso, verificador levantado): **router 59/59 rutas correctas**; 17/17 aciertos en los casos que ya se pueden evaluar (E, F, R, X); **40 casos pendientes** porque en esta rama todavía no están `revisar_caso` (Matías, 35 turnos) ni `responder_consulta` (Eduardo, 6 turnos). | hecho (2026-11-24). **Volver a correr** cuando estén unidos #95 y el flujo de Eduardo: esa es la corrida para la nota |

Cómo generarla (desde `tarea-final-c2/`, con `.env` completo):
```bash
python -m evaluacion.evaluar --validar     # 1) formato (no necesita Gemini)
python -m evaluacion.evaluar               # 2) corrida completa → escribe el informe aquí
```
Para la entrega conviene correrla cuando estén unidos los flujos de Matías (`revisar_gasto`) y de
Eduardo (`consulta_politica`): antes de eso, sus casos salen como **pendientes** (no cuentan).

Formato (2026-11-24): `--validar` → «golden set v1.0: formato correcto, 57 casos (59 turnos)».
