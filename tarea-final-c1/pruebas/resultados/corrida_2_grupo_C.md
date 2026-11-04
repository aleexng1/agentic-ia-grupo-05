# Golden set: corrida 2026-11-03_2108

- **Resultado:** 12/12 (100,0 %)
- **Turnos sin juez (falla técnica):** 0
- **Turnos sin RAG (falla técnica):** 0
- **Golden set:** v1.3 (construido sobre la política v1.5)
- **Política vigente:** 1.6 (2026-11)
- **Modelo:** gemini-3.5-flash-lite (temperatura 0)
- **Commit:** `5bbfd5d1a706b598661bdb3f23e39108dd87ea40`
- **Filtros:** {"casos": null, "grupo": "C", "componente": null, "pausa": 15}

| Grupo o componente | Pasan |
|---|---:|
| C-regla | 12/12 (100,0 %) |
| herramientas | 12/12 (100,0 %) |
| nucleo | 12/12 (100,0 %) |
| rag | 12/12 (100,0 %) |

| Caso | Grupo | Resultado | Resumen |
|---|---|---|---|
| GS-14 | C-regla | ✅ | rechazar · P07 |
| GS-15 | C-regla | ✅ | rechazar · P02 |
| GS-16 | C-regla | ✅ | rechazar · P02 |
| GS-17 | C-regla | ✅ | observar · P02 |
| GS-18 | C-regla | ✅ | observar · P04 |
| GS-19 | C-regla | ✅ | observar · P05 |
| GS-20 | C-regla | ✅ | observar · P06 |
| GS-21 | C-regla | ✅ | observar · P10 |
| GS-22 | C-regla | ✅ | observar · P02 |
| GS-23 | C-regla | ✅ | rechazar · P08 |
| GS-24 | C-regla | ✅ | observar · P04 |
| GS-34 | C-regla | ✅ | rechazar · P02 |

## Fragmentos que devolvió buscar_politica

Mayor puntaje significa más parecido a la consulta.

| Caso | Turno | Consulta | Política o regla | Fuente | Puntaje |
|---|---:|---|---|---|---:|
| GS-14 | 1 | Mercadería Cafetería | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.2503 |
| GS-14 | 1 | Mercadería Cafetería | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.3373 |
| GS-14 | 1 | Mercadería Cafetería | Insumos de Oficina y Aseo | datos/politica_ficticia.md#P09 | -0.3403 |
| GS-15 | 1 | Viajes Internos Almuerzo | Viajes Internos | datos/politica_ficticia.md#P02 | -0.242 |
| GS-15 | 1 | Viajes Internos Almuerzo | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2788 |
| GS-15 | 1 | Viajes Internos Almuerzo | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.3234 |
| GS-16 | 1 | almuerzo ruta de reparto alimentacion personal lugar de trabajo viaticos viajes internos | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2743 |
| GS-16 | 1 | almuerzo ruta de reparto alimentacion personal lugar de trabajo viaticos viajes internos | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2936 |
| GS-16 | 1 | almuerzo ruta de reparto alimentacion personal lugar de trabajo viaticos viajes internos | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.3038 |
| GS-17 | 1 | alimentacion almuerzo ruta reparto viaticos viaje alimentos | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2985 |
| GS-17 | 1 | alimentacion almuerzo ruta reparto viaticos viaje alimentos | Viajes Externos | datos/politica_ficticia.md#P03 | -0.3004 |
| GS-17 | 1 | alimentacion almuerzo ruta reparto viaticos viaje alimentos | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.3159 |
| GS-17 | 1 | alimentacion almuerzo ruta reparto viaticos viaje alimentos | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.3194 |
| GS-17 | 1 | alimentacion almuerzo ruta reparto viaticos viaje alimentos | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.3302 |
| GS-18 | 1 | Flota de Camiones y Camionetas mantenciones menores patente ot | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2232 |
| GS-18 | 1 | Flota de Camiones y Camionetas mantenciones menores patente ot | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.28 |
| GS-18 | 1 | Flota de Camiones y Camionetas mantenciones menores patente ot | Mantención de Instalaciones | datos/politica_ficticia.md#P10 | -0.299 |
| GS-19 | 1 | Grúas Horquilla | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.2625 |
| GS-19 | 1 | Grúas Horquilla | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.3609 |
| GS-19 | 1 | Grúas Horquilla | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.366 |
| GS-20 | 1 | Servicios del Taller Marino insumos para la OT | Servicios del Taller Marino | datos/politica_ficticia.md#P06 | -0.2358 |
| GS-20 | 1 | Servicios del Taller Marino insumos para la OT | Mantención de Instalaciones | datos/politica_ficticia.md#P10 | -0.3144 |
| GS-20 | 1 | Servicios del Taller Marino insumos para la OT | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.318 |
| GS-21 | 1 | Mantención de Instalaciones materiales de mantención | Mantención de Instalaciones | datos/politica_ficticia.md#P10 | -0.2226 |
| GS-21 | 1 | Mantención de Instalaciones materiales de mantención | Insumos de Oficina y Aseo | datos/politica_ficticia.md#P09 | -0.2939 |
| GS-21 | 1 | Mantención de Instalaciones materiales de mantención | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.2945 |
| GS-22 | 1 | almuerzo equipo de tienda en visita a CD Viajes Internos Alimentacion | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2595 |
| GS-22 | 1 | almuerzo equipo de tienda en visita a CD Viajes Internos Alimentacion | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2825 |
| GS-22 | 1 | almuerzo equipo de tienda en visita a CD Viajes Internos Alimentacion | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.2932 |
| GS-23 | 1 | Gastos del Personal Cumpleaños regalo | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.244 |
| GS-23 | 1 | Gastos del Personal Cumpleaños regalo | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-02 | -0.2667 |
| GS-23 | 1 | Gastos del Personal Cumpleaños regalo | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.3149 |
| GS-23 | 1 | Gastos del Personal Cumpleaños regalo | Viajes Internos | datos/politica_ficticia.md#P02 | -0.3248 |
| GS-23 | 1 | Gastos del Personal Cumpleaños regalo | Viajes Externos | datos/politica_ficticia.md#P03 | -0.3353 |
| GS-24 | 1 | multa camión flota P04 | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.1897 |
| GS-24 | 1 | multa camión flota P04 | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.2979 |
| GS-24 | 1 | multa camión flota P04 | Servicios del Taller Marino | datos/politica_ficticia.md#P06 | -0.3164 |
| GS-34 | 1 | almuerzo individual en la oficina de la tienda alimentacion personal | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-02 | -0.3246 |
| GS-34 | 1 | almuerzo individual en la oficina de la tienda alimentacion personal | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.3281 |
| GS-34 | 1 | almuerzo individual en la oficina de la tienda alimentacion personal | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.3378 |
