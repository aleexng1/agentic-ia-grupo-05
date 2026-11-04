# Golden set: corrida 2026-11-03_2104

- **Resultado:** 7/7 (100,0 %)
- **Turnos sin juez (falla técnica):** 0
- **Turnos sin RAG (falla técnica):** 0
- **Golden set:** v1.3 (construido sobre la política v1.5)
- **Política vigente:** 1.6 (2026-11)
- **Modelo:** gemini-3.5-flash-lite (temperatura 0)
- **Commit:** `5bbfd5d1a706b598661bdb3f23e39108dd87ea40`
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
| GS-07 | 1 | peaje vehiculo propio viaje interno P02 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.1951 |
| GS-07 | 1 | peaje vehiculo propio viaje interno P02 | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.225 |
| GS-07 | 1 | peaje vehiculo propio viaje interno P02 | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2452 |
| GS-07 | 1 | Viajes a proveedores P03 | Viajes Externos | datos/politica_ficticia.md#P03 | -0.1827 |
| GS-07 | 1 | Viajes a proveedores P03 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.228 |
| GS-08 | 1 | peaje traslado a marina viaje flota mantenimiento P02 P03 P04 | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2141 |
| GS-08 | 1 | peaje traslado a marina viaje flota mantenimiento P02 P03 P04 | Servicios del Taller Marino | datos/politica_ficticia.md#P06 | -0.2352 |
| GS-08 | 1 | peaje traslado a marina viaje flota mantenimiento P02 P03 P04 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2483 |
| GS-08 | 1 | peaje traslado a marina viaje flota mantenimiento P02 P03 P04 | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2532 |
| GS-08 | 1 | peaje traslado a marina viaje flota mantenimiento P02 P03 P04 | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.2622 |
| GS-09 | 1 | peaje viaje de negocios vehiculo empresa política categoria cuenta | Viajes Externos | datos/politica_ficticia.md#P03 | -0.234 |
| GS-09 | 1 | peaje viaje de negocios vehiculo empresa política categoria cuenta | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2344 |
| GS-09 | 1 | peaje viaje de negocios vehiculo empresa política categoria cuenta | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.2477 |
| GS-10 | 1 | alimentacion desayuno reunion jefaturas oficina | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.2885 |
| GS-10 | 1 | alimentacion desayuno reunion jefaturas oficina | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.3177 |
| GS-10 | 1 | alimentacion desayuno reunion jefaturas oficina | Viajes Internos | datos/politica_ficticia.md#P02 | -0.3215 |
| GS-11 | 1 | feria comercial proveedores almuerzo viajes internos P02 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.205 |
| GS-11 | 1 | feria comercial proveedores almuerzo viajes internos P02 | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2268 |
| GS-11 | 1 | feria comercial proveedores almuerzo viajes internos P02 | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.2773 |
| GS-12 | 1 | arriendo auto liviano vehiculo viajes pasajeros politica P01 P02 P03 | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-06 | -0.2042 |
| GS-12 | 1 | arriendo auto liviano vehiculo viajes pasajeros politica P01 P02 P03 | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.2342 |
| GS-12 | 1 | arriendo auto liviano vehiculo viajes pasajeros politica P01 P02 P03 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2541 |
| GS-12 | 1 | arriendo auto liviano vehiculo viajes pasajeros politica P01 P02 P03 | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2606 |
| GS-12 | 1 | arriendo auto liviano vehiculo viajes pasajeros politica P01 P02 P03 | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2716 |
| GS-13 | 1 | vehiculos propios bencina combustible traslado tienda sur | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.2487 |
| GS-13 | 1 | vehiculos propios bencina combustible traslado tienda sur | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2879 |
| GS-13 | 1 | vehiculos propios bencina combustible traslado tienda sur | Viajes Internos | datos/politica_ficticia.md#P02 | -0.293 |
| GS-13 | 1 | P02 combustible gasolina vehiculo empresa camioneta arrendada o P03 | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2114 |
| GS-13 | 1 | P02 combustible gasolina vehiculo empresa camioneta arrendada o P03 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2206 |
