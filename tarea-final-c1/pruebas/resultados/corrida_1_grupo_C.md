# Golden set: corrida 2026-11-02_1838

- **Resultado:** 11/11 (100,0 %)
- **Turnos sin juez (falla técnica):** 0
- **Golden set:** v1.2 (construido sobre la política v1.1)
- **Política vigente:** 1.3 (2026-11)
- **Modelo:** gemini-3.5-flash-lite (temperatura 0)
- **Commit:** `8949700fa5613e0ec78acd7f8f6cf5e850b89db3`
- **Filtros:** {"casos": null, "grupo": "C", "componente": null, "pausa": 15.0}

| Grupo o componente | Pasan |
|---|---:|
| C-regla | 11/11 (100,0 %) |
| herramientas | 11/11 (100,0 %) |
| nucleo | 11/11 (100,0 %) |
| rag | 11/11 (100,0 %) |

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

## Fragmentos que devolvió buscar_politica

Mayor puntaje significa más parecido a la consulta.

| Caso | Turno | Consulta | Política o regla | Fuente | Puntaje |
|---|---:|---|---|---|---:|
| GS-14 | 1 | Mercadería Cafetería | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.2446 |
| GS-14 | 1 | Mercadería Cafetería | Insumos de Oficina y Aseo | datos/politica_ficticia.md#P09 | -0.3443 |
| GS-14 | 1 | Mercadería Cafetería | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.3447 |
| GS-15 | 1 | Viajes Internos Almuerzo | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2458 |
| GS-15 | 1 | Viajes Internos Almuerzo | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2772 |
| GS-15 | 1 | Viajes Internos Almuerzo | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.3169 |
| GS-16 | 1 | Viajes Internos Almuerzo plazo rendicion | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2663 |
| GS-16 | 1 | Viajes Internos Almuerzo plazo rendicion | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2977 |
| GS-16 | 1 | Viajes Internos Almuerzo plazo rendicion | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.3265 |
| GS-17 | 1 | Viajes Internos Almuerzo plazo rendicion | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2663 |
| GS-17 | 1 | Viajes Internos Almuerzo plazo rendicion | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2977 |
| GS-17 | 1 | Viajes Internos Almuerzo plazo rendicion | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.3265 |
| GS-18 | 1 | Flota de Camiones y Camionetas Mantenciones menores patentes vehiculos obligatorios | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2164 |
| GS-18 | 1 | Flota de Camiones y Camionetas Mantenciones menores patentes vehiculos obligatorios | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.2877 |
| GS-18 | 1 | Flota de Camiones y Camionetas Mantenciones menores patentes vehiculos obligatorios | Mantención de Instalaciones | datos/politica_ficticia.md#P10 | -0.3212 |
| GS-19 | 1 | Grúas Horquilla | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.2633 |
| GS-19 | 1 | Grúas Horquilla | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.3652 |
| GS-19 | 1 | Grúas Horquilla | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.3695 |
| GS-20 | 1 | Servicios del Taller Marino Insumos para la OT | Servicios del Taller Marino | datos/politica_ficticia.md#P06 | -0.2479 |
| GS-20 | 1 | Servicios del Taller Marino Insumos para la OT | Mantención de Instalaciones | datos/politica_ficticia.md#P10 | -0.3216 |
| GS-20 | 1 | Servicios del Taller Marino Insumos para la OT | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.3264 |
| GS-21 | 1 | Mantención de Instalaciones | Mantención de Instalaciones | datos/politica_ficticia.md#P10 | -0.2418 |
| GS-21 | 1 | Mantención de Instalaciones | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.3217 |
| GS-21 | 1 | Mantención de Instalaciones | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.3414 |
| GS-21 | 1 | Mantención de Instalaciones | Insumos de Oficina y Aseo | datos/politica_ficticia.md#P09 | -0.3485 |
| GS-21 | 1 | Mantención de Instalaciones | Servicios del Taller Marino | datos/politica_ficticia.md#P06 | -0.365 |
| GS-22 | 1 | almuerzo equipo de tienda viajes internos comidas viaticos | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2811 |
| GS-22 | 1 | almuerzo equipo de tienda viajes internos comidas viaticos | Viajes Externos | datos/politica_ficticia.md#P03 | -0.3022 |
| GS-22 | 1 | almuerzo equipo de tienda viajes internos comidas viaticos | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.3112 |
| GS-22 | 1 | almuerzo equipo de tienda viajes internos comidas viaticos | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.3118 |
| GS-22 | 1 | almuerzo equipo de tienda viajes internos comidas viaticos | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.3376 |
| GS-23 | 1 | Gastos del Personal Cumpleaños regalo de cumpleaños | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.2528 |
| GS-23 | 1 | Gastos del Personal Cumpleaños regalo de cumpleaños | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.3253 |
| GS-23 | 1 | Gastos del Personal Cumpleaños regalo de cumpleaños | Viajes Internos | datos/politica_ficticia.md#P02 | -0.3405 |
| GS-24 | 1 | multa camión de reparto flota camiones y camionetas P04 | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.1996 |
| GS-24 | 1 | multa camión de reparto flota camiones y camionetas P04 | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.3044 |
| GS-24 | 1 | multa camión de reparto flota camiones y camionetas P04 | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.3179 |
