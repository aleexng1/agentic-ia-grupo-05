# Golden set: corrida 2026-11-03_2212

- **Resultado:** 6/6 (100,0 %)
- **Turnos sin juez (falla técnica):** 0
- **Turnos sin RAG (falla técnica):** 0
- **Golden set:** v1.3 (construido sobre la política v1.5)
- **Política vigente:** 1.6 (2026-11)
- **Modelo:** gemini-3.5-flash-lite (temperatura 0)
- **Commit:** `f050ad7dccdb7f396f934c22192f59339a5db6d4`
- **Filtros:** {"casos": null, "grupo": "A", "componente": null, "pausa": 15}

| Grupo o componente | Pasan |
|---|---:|
| A-limpio | 6/6 (100,0 %) |
| herramientas | 6/6 (100,0 %) |
| nucleo | 6/6 (100,0 %) |
| rag | 6/6 (100,0 %) |

| Caso | Grupo | Resultado | Resumen |
|---|---|---|---|
| GS-01 | A-limpio | ✅ | aprobar · P02 |
| GS-02 | A-limpio | ✅ | aprobar · P02 |
| GS-03 | A-limpio | ✅ | aprobar · P08 |
| GS-04 | A-limpio | ✅ | aprobar · P09 |
| GS-05 | A-limpio | ✅ | aprobar · P07 |
| GS-06 | A-limpio | ✅ | aprobar · P03 |

## Fragmentos que devolvió buscar_politica

Mayor puntaje significa más parecido a la consulta.

| Caso | Turno | Consulta | Política o regla | Fuente | Puntaje |
|---|---:|---|---|---|---:|
| GS-01 | 1 | peaje camion flota P04 P02 P03 | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.193 |
| GS-01 | 1 | peaje camion flota P04 P02 P03 | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.2655 |
| GS-01 | 1 | peaje camion flota P04 P02 P03 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2699 |
| GS-02 | 1 | almuerzo visita a CD por inventario viajes internos P02 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.211 |
| GS-02 | 1 | almuerzo visita a CD por inventario viajes internos P02 | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2476 |
| GS-02 | 1 | almuerzo visita a CD por inventario viajes internos P02 | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.2731 |
| GS-03 | 1 | capacitacion capacitaciones cafeteria boleta gastos del personal adm | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.2167 |
| GS-03 | 1 | capacitacion capacitaciones cafeteria boleta gastos del personal adm | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.2633 |
| GS-03 | 1 | capacitacion capacitaciones cafeteria boleta gastos del personal adm | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.2879 |
| GS-04 | 1 | Insumos de Oficina y Aseo | Insumos de Oficina y Aseo | datos/politica_ficticia.md#P09 | -0.2224 |
| GS-04 | 1 | Insumos de Oficina y Aseo | Mantención de Instalaciones | datos/politica_ficticia.md#P10 | -0.3171 |
| GS-04 | 1 | Insumos de Oficina y Aseo | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.3253 |
| GS-05 | 1 | Mercadería Cafetería | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.2503 |
| GS-05 | 1 | Mercadería Cafetería | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.3373 |
| GS-05 | 1 | Mercadería Cafetería | Insumos de Oficina y Aseo | datos/politica_ficticia.md#P09 | -0.3403 |
| GS-06 | 1 | taxi locomoción viajes externos P02 voucher | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2202 |
| GS-06 | 1 | taxi locomoción viajes externos P02 voucher | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-01 | -0.235 |
| GS-06 | 1 | taxi locomoción viajes externos P02 voucher | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2374 |
