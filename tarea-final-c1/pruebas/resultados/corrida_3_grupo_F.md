# Golden set: corrida 2026-11-03_2227

- **Resultado:** 3/3 (100,0 %)
- **Turnos sin juez (falla técnica):** 0
- **Turnos sin RAG (falla técnica):** 0
- **Golden set:** v1.3 (construido sobre la política v1.5)
- **Política vigente:** 1.6 (2026-11)
- **Modelo:** gemini-3.5-flash-lite (temperatura 0)
- **Commit:** `f050ad7dccdb7f396f934c22192f59339a5db6d4`
- **Filtros:** {"casos": null, "grupo": "F", "componente": null, "pausa": 15}

| Grupo o componente | Pasan |
|---|---:|
| F-conversacion | 3/3 (100,0 %) |
| nucleo | 3/3 (100,0 %) |
| rag | 1/1 (100,0 %) |

| Caso | Grupo | Resultado | Resumen |
|---|---|---|---|
| GS-31 | F-conversacion | ✅ | sin gasto |
| GS-32 | F-conversacion | ✅ | sin gasto |
| GS-33 | F-conversacion | ✅ | sin gasto |

## Fragmentos que devolvió buscar_politica

Mayor puntaje significa más parecido a la consulta.

| Caso | Turno | Consulta | Política o regla | Fuente | Puntaje |
|---|---:|---|---|---|---:|
| GS-33 | 1 | plazo de rendicion dia del mes siguiente | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-03 | -0.2092 |
| GS-33 | 1 | plazo de rendicion dia del mes siguiente | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-10 | -0.316 |
| GS-33 | 1 | plazo de rendicion dia del mes siguiente | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-08 | -0.3248 |
