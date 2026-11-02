# Golden set: corrida 2026-11-02_1831

- **Resultado:** 2/2 (100,0 %)
- **Turnos sin juez (falla técnica):** 0
- **Golden set:** v1.2 (construido sobre la política v1.1)
- **Política vigente:** 1.3 (2026-11)
- **Modelo:** gemini-3.5-flash-lite (temperatura 0)
- **Commit:** `8949700fa5613e0ec78acd7f8f6cf5e850b89db3`
- **Filtros:** {"casos": "GS-03,GS-06", "grupo": null, "componente": null, "pausa": 15.0}

| Grupo o componente | Pasan |
|---|---:|
| A-limpio | 2/2 (100,0 %) |
| herramientas | 2/2 (100,0 %) |
| nucleo | 2/2 (100,0 %) |
| rag | 2/2 (100,0 %) |

| Caso | Grupo | Resultado | Resumen |
|---|---|---|---|
| GS-03 | A-limpio | ✅ | aprobar · P08 |
| GS-06 | A-limpio | ✅ | aprobar · P03 |

## Fragmentos que devolvió buscar_politica

Mayor puntaje significa más parecido a la consulta.

| Caso | Turno | Consulta | Política o regla | Fuente | Puntaje |
|---|---:|---|---|---|---:|
| GS-03 | 1 | Gastos del Personal Capacitaciones | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.233 |
| GS-03 | 1 | Gastos del Personal Capacitaciones | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2953 |
| GS-03 | 1 | Gastos del Personal Capacitaciones | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.302 |
| GS-03 | 1 | Gastos del Personal Capacitaciones | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.3042 |
| GS-03 | 1 | Gastos del Personal Capacitaciones | Servicios del Taller Marino | datos/politica_ficticia.md#P06 | -0.3044 |
| GS-06 | 1 | Locomoción Taxis Viajes Externos P02 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2215 |
| GS-06 | 1 | Locomoción Taxis Viajes Externos P02 | Viajes Externos | datos/politica_ficticia.md#P03 | -0.238 |
| GS-06 | 1 | Locomoción Taxis Viajes Externos P02 | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.2676 |
