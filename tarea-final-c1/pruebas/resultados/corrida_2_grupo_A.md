# Golden set: corrida 2026-11-03_2101

- **Resultado:** 6/6 (100,0 %)
- **Turnos sin juez (falla técnica):** 0
- **Turnos sin RAG (falla técnica):** 0
- **Golden set:** v1.3 (construido sobre la política v1.5)
- **Política vigente:** 1.6 (2026-11)
- **Modelo:** gemini-3.5-flash-lite (temperatura 0)
- **Commit:** `5bbfd5d1a706b598661bdb3f23e39108dd87ea40`
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
| GS-01 | 1 | peaje camion de reparto flota vehiculos mantenimiento peajes estacionamiento combustible | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2778 |
| GS-01 | 1 | peaje camion de reparto flota vehiculos mantenimiento peajes estacionamiento combustible | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.3074 |
| GS-01 | 1 | peaje camion de reparto flota vehiculos mantenimiento peajes estacionamiento combustible | Servicios del Taller Marino | datos/politica_ficticia.md#P06 | -0.3238 |
| GS-01 | 1 | peaje camion de reparto flota vehiculos mantenimiento peajes estacionamiento combustible | Mantención de Instalaciones | datos/politica_ficticia.md#P10 | -0.3378 |
| GS-01 | 1 | peaje camion de reparto flota vehiculos mantenimiento peajes estacionamiento combustible | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-06 | -0.3385 |
| GS-01 | 1 | Viajes Internos P02 peajes viaje camion de reparto flota de camiones y camionetas P03 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.1941 |
| GS-01 | 1 | Viajes Internos P02 peajes viaje camion de reparto flota de camiones y camionetas P03 | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2199 |
| GS-01 | 1 | Viajes Internos P02 peajes viaje camion de reparto flota de camiones y camionetas P03 | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2263 |
| GS-02 | 1 | almuerzo visita a CD por inventario viajes internos | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2589 |
| GS-02 | 1 | almuerzo visita a CD por inventario viajes internos | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2749 |
| GS-02 | 1 | almuerzo visita a CD por inventario viajes internos | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.3067 |
| GS-03 | 1 | capacitacion alimentacion gastos del personal cafeteria | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.2379 |
| GS-03 | 1 | capacitacion alimentacion gastos del personal cafeteria | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.2796 |
| GS-03 | 1 | capacitacion alimentacion gastos del personal cafeteria | Viajes Externos | datos/politica_ficticia.md#P03 | -0.3203 |
| GS-04 | 1 | Insumos de Oficina y Aseo | Insumos de Oficina y Aseo | datos/politica_ficticia.md#P09 | -0.2224 |
| GS-04 | 1 | Insumos de Oficina y Aseo | Mantención de Instalaciones | datos/politica_ficticia.md#P10 | -0.3171 |
| GS-04 | 1 | Insumos de Oficina y Aseo | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.3253 |
| GS-05 | 1 | Mercadería Cafetería | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.2503 |
| GS-05 | 1 | Mercadería Cafetería | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.3373 |
| GS-05 | 1 | Mercadería Cafetería | Insumos de Oficina y Aseo | datos/politica_ficticia.md#P09 | -0.3403 |
| GS-06 | 1 | locomoción taxis viajes externos P02 P03 | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2037 |
| GS-06 | 1 | locomoción taxis viajes externos P02 P03 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2124 |
| GS-06 | 1 | locomoción taxis viajes externos P02 P03 | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.255 |
