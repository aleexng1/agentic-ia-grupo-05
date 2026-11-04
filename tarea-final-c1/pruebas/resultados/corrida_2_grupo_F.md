# Golden set: corrida 2026-11-03_2111

- **Resultado:** 3/3 (100,0 %)
- **Turnos sin juez (falla técnica):** 0
- **Turnos sin RAG (falla técnica):** 0
- **Golden set:** v1.3 (construido sobre la política v1.5)
- **Política vigente:** 1.6 (2026-11)
- **Modelo:** gemini-3.5-flash-lite (temperatura 0)
- **Commit:** `5bbfd5d1a706b598661bdb3f23e39108dd87ea40`
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
| GS-33 | 1 | plazo rendicion fecha mes siguiente dia 10 RG-03 | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-03 | -0.1693 |
| GS-33 | 1 | plazo rendicion fecha mes siguiente dia 10 RG-03 | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-10 | -0.2577 |
| GS-33 | 1 | plazo rendicion fecha mes siguiente dia 10 RG-03 | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-08 | -0.3041 |
