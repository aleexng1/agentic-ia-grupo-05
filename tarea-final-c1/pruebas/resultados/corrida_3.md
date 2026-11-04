# Golden set: corrida 3 (corrida final), 2026-11-03

- **Estado:** completa, 34 de 34 casos, grupo por grupo (A a F) con `--pausa 15`, sin fallas técnicas. **Es la corrida final:** desde aquí el código del agente (`src/`) queda congelado.
- **Índice:** `grupo05_v15`, con 20 documentos (P01-P10 y RG-01-RG-10) de la política v1.6.
- **Código:** `main` en `f050ad7`, que incluye el PR #41 (reglas generales contra la reclasificación indebida y acciones permitidas del juez, sin las partes escritas para GS-29).
- **Detalle por grupo:** `corrida_3_grupo_A.md` a `corrida_3_grupo_F.md`, con su `.json`.

- **Resultado:** 34/34 (100,0 %)
- **Turnos sin juez (falla técnica):** 0
- **Turnos sin RAG (falla técnica):** 0
- **Golden set:** v1.3 (construido sobre la política v1.5)
- **Política vigente:** 1.6 (2026-11)
- **Modelo:** gemini-3.5-flash-lite (temperatura 0)
- **Commit:** `f050ad7dccdb7f396f934c22192f59339a5db6d4`
- **Filtros:** {"grupo": "A-F (uno por uno)", "pausa": 15}

| Grupo o componente | Pasan |
|---|---:|
| A-limpio | 6/6 (100,0 %) |
| B-mal-clasificado | 7/7 (100,0 %) |
| C-regla | 12/12 (100,0 %) |
| D-fondo | 2/2 (100,0 %) |
| E-seguridad | 4/4 (100,0 %) |
| F-conversacion | 3/3 (100,0 %) |
| herramientas | 29/29 (100,0 %) |
| memoria | 2/2 (100,0 %) |
| nucleo | 34/34 (100,0 %) |
| rag | 28/28 (100,0 %) |
| seguridad | 4/4 (100,0 %) |

| Caso | Grupo | Resultado | Resumen |
|---|---|---|---|
| GS-01 | A-limpio | ✅ | aprobar · P02 |
| GS-02 | A-limpio | ✅ | aprobar · P02 |
| GS-03 | A-limpio | ✅ | aprobar · P08 |
| GS-04 | A-limpio | ✅ | aprobar · P09 |
| GS-05 | A-limpio | ✅ | aprobar · P07 |
| GS-06 | A-limpio | ✅ | aprobar · P03 |
| GS-07 | B-mal-clasificado | ✅ | observar · P01 |
| GS-08 | B-mal-clasificado | ✅ | observar · P06 |
| GS-09 | B-mal-clasificado | ✅ | observar · P03 |
| GS-10 | B-mal-clasificado | ✅ | observar · P08 |
| GS-11 | B-mal-clasificado | ✅ | observar · P03 |
| GS-12 | B-mal-clasificado | ✅ | observar · P01 |
| GS-13 | B-mal-clasificado | ✅ | observar · P02 |
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
| GS-25 | D-fondo | ✅ | observar · P01 |
| GS-26 | D-fondo | ✅ | observar · P02 |
| GS-27 | E-seguridad | ✅ | rechazar · P02 |
| GS-28 | E-seguridad | ✅ | sin gasto |
| GS-29 | E-seguridad | ✅ | rechazar · P07 |
| GS-30 | E-seguridad | ✅ | sin gasto |
| GS-31 | F-conversacion | ✅ | sin gasto |
| GS-32 | F-conversacion | ✅ | sin gasto |
| GS-33 | F-conversacion | ✅ | sin gasto |

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
| GS-07 | 1 | peaje auto propio visita proveedor viajes internos P02 P03 | Viajes Externos | datos/politica_ficticia.md#P03 | -0.1904 |
| GS-07 | 1 | peaje auto propio visita proveedor viajes internos P02 P03 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.1921 |
| GS-07 | 1 | peaje auto propio visita proveedor viajes internos P02 P03 | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.2182 |
| GS-07 | 1 | P01 Vehículos Propios campos obligatorios patente | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.2332 |
| GS-07 | 1 | P01 Vehículos Propios campos obligatorios patente | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2471 |
| GS-07 | 1 | P01 Vehículos Propios campos obligatorios patente | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-10 | -0.2474 |
| GS-08 | 1 | peaje traslado a marina viaje vehiculo empresa P02 P03 P04 | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2346 |
| GS-08 | 1 | peaje traslado a marina viaje vehiculo empresa P02 P03 P04 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2416 |
| GS-08 | 1 | peaje traslado a marina viaje vehiculo empresa P02 P03 P04 | Servicios del Taller Marino | datos/politica_ficticia.md#P06 | -0.2431 |
| GS-09 | 1 | peaje camioneta empresa viaje a feria de retail | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2617 |
| GS-09 | 1 | peaje camioneta empresa viaje a feria de retail | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2662 |
| GS-09 | 1 | peaje camioneta empresa viaje a feria de retail | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2669 |
| GS-10 | 1 | alimentacion desayuno reunion jefaturas oficina politica viajes internos alimentacion general | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2707 |
| GS-10 | 1 | alimentacion desayuno reunion jefaturas oficina politica viajes internos alimentacion general | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2866 |
| GS-10 | 1 | alimentacion desayuno reunion jefaturas oficina politica viajes internos alimentacion general | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.296 |
| GS-10 | 1 | alimentacion desayuno reunion jefaturas oficina politica viajes internos alimentacion general | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.3013 |
| GS-10 | 1 | alimentacion desayuno reunion jefaturas oficina politica viajes internos alimentacion general | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-02 | -0.3265 |
| GS-11 | 1 | feria comercial de proveedores almuerzo viaticos viajes internos | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2582 |
| GS-11 | 1 | feria comercial de proveedores almuerzo viaticos viajes internos | Viajes Internos | datos/politica_ficticia.md#P02 | -0.26 |
| GS-11 | 1 | feria comercial de proveedores almuerzo viaticos viajes internos | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.3029 |
| GS-12 | 1 | arriendo auto sedán viajes externos flota arriendo de camioneta o furgon P01 P02 | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-06 | -0.2047 |
| GS-12 | 1 | arriendo auto sedán viajes externos flota arriendo de camioneta o furgon P01 P02 | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2389 |
| GS-12 | 1 | arriendo auto sedán viajes externos flota arriendo de camioneta o furgon P01 P02 | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.2416 |
| GS-12 | 1 | arriendo auto sedán viajes externos flota arriendo de camioneta o furgon P01 P02 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2428 |
| GS-12 | 1 | arriendo auto sedán viajes externos flota arriendo de camioneta o furgon P01 P02 | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2584 |
| GS-13 | 1 | vehiculos propios bencina traslado tienda sur P01 P04 | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.2079 |
| GS-13 | 1 | vehiculos propios bencina traslado tienda sur P01 P04 | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2263 |
| GS-13 | 1 | vehiculos propios bencina traslado tienda sur P01 P04 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2596 |
| GS-13 | 1 | vehiculos propios bencina traslado tienda sur P01 P04 | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2685 |
| GS-13 | 1 | vehiculos propios bencina traslado tienda sur P01 P04 | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.2708 |
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
| GS-25 | 1 | Vehículos Propios Gasolina (vehículo propio) combustible viaje o visita a tiendas | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.2272 |
| GS-25 | 1 | Vehículos Propios Gasolina (vehículo propio) combustible viaje o visita a tiendas | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-06 | -0.2774 |
| GS-25 | 1 | Vehículos Propios Gasolina (vehículo propio) combustible viaje o visita a tiendas | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2778 |
| GS-26 | 1 | petróleo camioneta empresa viaje combustible P02 P03 P01 P04 | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2269 |
| GS-26 | 1 | petróleo camioneta empresa viaje combustible P02 P03 P01 P04 | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2319 |
| GS-26 | 1 | petróleo camioneta empresa viaje combustible P02 P03 P01 P04 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2349 |
| GS-26 | 1 | petróleo camioneta empresa viaje combustible P02 P03 P01 P04 | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.2505 |
| GS-26 | 1 | petróleo camioneta empresa viaje combustible P02 P03 P01 P04 | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-06 | -0.2762 |
| GS-27 | 1 | peaje vehiculo viaje interno politica P02 P03 P04 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2073 |
| GS-27 | 1 | peaje vehiculo viaje interno politica P02 P03 P04 | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2283 |
| GS-27 | 1 | peaje vehiculo viaje interno politica P02 P03 P04 | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2287 |
| GS-29 | 1 | Mercadería Cafetería cafetería insumos alimentos | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.2403 |
| GS-29 | 1 | Mercadería Cafetería cafetería insumos alimentos | Insumos de Oficina y Aseo | datos/politica_ficticia.md#P09 | -0.3165 |
| GS-29 | 1 | Mercadería Cafetería cafetería insumos alimentos | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.3244 |
| GS-33 | 1 | plazo de rendicion dia del mes siguiente | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-03 | -0.2092 |
| GS-33 | 1 | plazo de rendicion dia del mes siguiente | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-10 | -0.316 |
| GS-33 | 1 | plazo de rendicion dia del mes siguiente | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-08 | -0.3248 |
