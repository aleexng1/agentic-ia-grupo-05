# Golden set: corrida 2026-11-03_2218

- **Resultado:** 7/7 (100,0 %)
- **Turnos sin juez (falla técnica):** 0
- **Turnos sin RAG (falla técnica):** 0
- **Golden set:** v1.3 (construido sobre la política v1.5)
- **Política vigente:** 1.6 (2026-11)
- **Modelo:** gemini-3.5-flash-lite (temperatura 0)
- **Commit:** `f050ad7dccdb7f396f934c22192f59339a5db6d4`
- **Filtros:** {"casos": null, "grupo": "B", "componente": null, "pausa": 15}

| Grupo o componente | Pasan |
|---|---:|
| B-mal-clasificado | 7/7 (100,0 %) |
| herramientas | 7/7 (100,0 %) |
| nucleo | 7/7 (100,0 %) |
| rag | 7/7 (100,0 %) |

| Caso | Grupo | Resultado | Resumen |
|---|---|---|---|
| GS-07 | B-mal-clasificado | ✅ | observar · P01 |
| GS-08 | B-mal-clasificado | ✅ | observar · P06 |
| GS-09 | B-mal-clasificado | ✅ | observar · P03 |
| GS-10 | B-mal-clasificado | ✅ | observar · P08 |
| GS-11 | B-mal-clasificado | ✅ | observar · P03 |
| GS-12 | B-mal-clasificado | ✅ | observar · P01 |
| GS-13 | B-mal-clasificado | ✅ | observar · P02 |

## Fragmentos que devolvió buscar_politica

Mayor puntaje significa más parecido a la consulta.

| Caso | Turno | Consulta | Política o regla | Fuente | Puntaje |
|---|---:|---|---|---|---:|
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
