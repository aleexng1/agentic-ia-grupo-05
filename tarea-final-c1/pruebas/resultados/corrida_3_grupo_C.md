# Golden set: corrida 2026-11-03_2224

- **Resultado:** 12/12 (100,0 %)
- **Turnos sin juez (falla técnica):** 0
- **Turnos sin RAG (falla técnica):** 0
- **Golden set:** v1.3 (construido sobre la política v1.5)
- **Política vigente:** 1.6 (2026-11)
- **Modelo:** gemini-3.5-flash-lite (temperatura 0)
- **Commit:** `f050ad7dccdb7f396f934c22192f59339a5db6d4`
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
| GS-15 | 1 | Viajes Internos Almuerzo alimentación pasajes viaticos | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2147 |
| GS-15 | 1 | Viajes Internos Almuerzo alimentación pasajes viaticos | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2402 |
| GS-15 | 1 | Viajes Internos Almuerzo alimentación pasajes viaticos | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.2887 |
| GS-16 | 1 | Almuerzo ruta de reparto a tiendas individual lugar de trabajo sin viaje ni reunion RG-02 | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-02 | -0.2323 |
| GS-16 | 1 | Almuerzo ruta de reparto a tiendas individual lugar de trabajo sin viaje ni reunion RG-02 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2545 |
| GS-16 | 1 | Almuerzo ruta de reparto a tiendas individual lugar de trabajo sin viaje ni reunion RG-02 | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-01 | -0.2825 |
| GS-17 | 1 | almuerzo ruta de reparto alimentacion individual viaje | Viajes Internos | datos/politica_ficticia.md#P02 | -0.3172 |
| GS-17 | 1 | almuerzo ruta de reparto alimentacion individual viaje | Viajes Externos | datos/politica_ficticia.md#P03 | -0.3258 |
| GS-17 | 1 | almuerzo ruta de reparto alimentacion individual viaje | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-02 | -0.3373 |
| GS-17 | 1 | almuerzo ruta de reparto alimentacion individual viaje | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.3395 |
| GS-17 | 1 | almuerzo ruta de reparto alimentacion individual viaje | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.3438 |
| GS-18 | 1 | Flota de Camiones y Camionetas mantenciones menores patente ot | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2232 |
| GS-18 | 1 | Flota de Camiones y Camionetas mantenciones menores patente ot | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.28 |
| GS-18 | 1 | Flota de Camiones y Camionetas mantenciones menores patente ot | Mantención de Instalaciones | datos/politica_ficticia.md#P10 | -0.299 |
| GS-18 | 1 | Flota de Camiones y Camionetas mantenciones menores patente ot | Servicios del Taller Marino | datos/politica_ficticia.md#P06 | -0.3139 |
| GS-18 | 1 | Flota de Camiones y Camionetas mantenciones menores patente ot | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-10 | -0.3294 |
| GS-19 | 1 | Grúas Horquilla | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.2625 |
| GS-19 | 1 | Grúas Horquilla | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.3609 |
| GS-19 | 1 | Grúas Horquilla | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.366 |
| GS-20 | 1 | Servicios del Taller Marino Insumos para la OT | Servicios del Taller Marino | datos/politica_ficticia.md#P06 | -0.2463 |
| GS-20 | 1 | Servicios del Taller Marino Insumos para la OT | Mantención de Instalaciones | datos/politica_ficticia.md#P10 | -0.3206 |
| GS-20 | 1 | Servicios del Taller Marino Insumos para la OT | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.3234 |
| GS-21 | 1 | Mantención de Instalaciones bodega de tienda Materiales de mantención | Mantención de Instalaciones | datos/politica_ficticia.md#P10 | -0.2287 |
| GS-21 | 1 | Mantención de Instalaciones bodega de tienda Materiales de mantención | Insumos de Oficina y Aseo | datos/politica_ficticia.md#P09 | -0.293 |
| GS-21 | 1 | Mantención de Instalaciones bodega de tienda Materiales de mantención | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.2948 |
| GS-22 | 1 | almuerzo equipo de tienda en visita a CD Viajes Internos Gastos de Representación | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2277 |
| GS-22 | 1 | almuerzo equipo de tienda en visita a CD Viajes Internos Gastos de Representación | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2436 |
| GS-22 | 1 | almuerzo equipo de tienda en visita a CD Viajes Internos Gastos de Representación | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.2629 |
| GS-22 | 1 | almuerzo equipo de tienda en visita a CD Viajes Internos Gastos de Representación | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.2873 |
| GS-22 | 1 | almuerzo equipo de tienda en visita a CD Viajes Internos Gastos de Representación | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.2919 |
| GS-23 | 1 | Gastos del Personal Cumpleaños regalo sobrino personal | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.2629 |
| GS-23 | 1 | Gastos del Personal Cumpleaños regalo sobrino personal | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-02 | -0.2714 |
| GS-23 | 1 | Gastos del Personal Cumpleaños regalo sobrino personal | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.3095 |
| GS-24 | 1 | multas de transito flotas camioneta P04 | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.1859 |
| GS-24 | 1 | multas de transito flotas camioneta P04 | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.3021 |
| GS-24 | 1 | multas de transito flotas camioneta P04 | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.3066 |
| GS-34 | 1 | almuerzo individual en la oficina de la tienda RG-02 | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-02 | -0.2497 |
| GS-34 | 1 | almuerzo individual en la oficina de la tienda RG-02 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2849 |
| GS-34 | 1 | almuerzo individual en la oficina de la tienda RG-02 | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-01 | -0.3062 |
