# Golden set: corrida 2026-11-02_1834

- **Resultado:** 6/7 (85,7 %)
- **Turnos sin juez (falla técnica):** 0
- **Golden set:** v1.2 (construido sobre la política v1.1)
- **Política vigente:** 1.3 (2026-11)
- **Modelo:** gemini-3.5-flash-lite (temperatura 0)
- **Commit:** `8949700fa5613e0ec78acd7f8f6cf5e850b89db3`
- **Filtros:** {"casos": null, "grupo": "B", "componente": null, "pausa": 15.0}

| Grupo o componente | Pasan |
|---|---:|
| B-mal-clasificado | 6/7 (85,7 %) |
| herramientas | 6/7 (85,7 %) |
| nucleo | 6/7 (85,7 %) |
| rag | 6/7 (85,7 %) |

| Causa de los ❌ | Casos | Cuáles |
|---|---:|---|
| Otra causa | 1 | GS-10 |

| Caso | Grupo | Resultado | Resumen |
|---|---|---|---|
| GS-07 | B-mal-clasificado | ✅ | observar · P01 |
| GS-08 | B-mal-clasificado | ✅ | observar · P06 |
| GS-09 | B-mal-clasificado | ✅ | observar · P03 |
| GS-10 | B-mal-clasificado | ❌ | turno 1 · decisión: esperado 'observar', obtenido 'aprobar' (+4 más) |
| GS-11 | B-mal-clasificado | ✅ | observar · P03 |
| GS-12 | B-mal-clasificado | ✅ | observar · P01 |
| GS-13 | B-mal-clasificado | ✅ | observar · P02 |

## Detalle de los ❌

**GS-10** — Jefa administrativa: desayuno de reunión interna, declarado en P02

- turno 1 · decisión: esperado 'observar', obtenido 'aprobar'
- turno 1 · política: esperado 'P08', obtenido 'P02'
- turno 1 · categoría: esperado 'Coffee break', obtenido 'Desayuno'
- turno 1 · cuenta: esperado 'CTA-8010', obtenido 'CTA-6110'
- turno 1 · reglas: esperado citar ['RG-09'], obtenido citó ['P02']

## Fragmentos que devolvió buscar_politica

Mayor puntaje significa más parecido a la consulta.

| Caso | Turno | Consulta | Política o regla | Fuente | Puntaje |
|---|---:|---|---|---|---:|
| GS-07 | 1 | peaje auto propio visita a proveedor de muebles Viajes Internos | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2683 |
| GS-07 | 1 | peaje auto propio visita a proveedor de muebles Viajes Internos | Viajes Externos | datos/politica_ficticia.md#P03 | -0.271 |
| GS-07 | 1 | peaje auto propio visita a proveedor de muebles Viajes Internos | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.2878 |
| GS-07 | 1 | P01 Vehículos Propios campos obligatorios patente | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.2341 |
| GS-07 | 1 | P01 Vehículos Propios campos obligatorios patente | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2499 |
| GS-07 | 1 | P01 Vehículos Propios campos obligatorios patente | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2816 |
| GS-08 | 1 | peajes vehiculos empresa viajes internos flota marina | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2737 |
| GS-08 | 1 | peajes vehiculos empresa viajes internos flota marina | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2739 |
| GS-08 | 1 | peajes vehiculos empresa viajes internos flota marina | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2781 |
| GS-08 | 1 | P06 Taller Marino viajes ot marina cliente | Servicios del Taller Marino | datos/politica_ficticia.md#P06 | -0.19 |
| GS-08 | 1 | P06 Taller Marino viajes ot marina cliente | Viajes Externos | datos/politica_ficticia.md#P03 | -0.259 |
| GS-08 | 1 | P06 Taller Marino viajes ot marina cliente | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2808 |
| GS-09 | 1 | peajes vehiculos empresa viajes internos | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2372 |
| GS-09 | 1 | peajes vehiculos empresa viajes internos | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2517 |
| GS-09 | 1 | peajes vehiculos empresa viajes internos | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.275 |
| GS-10 | 1 | desayuno reunion mensual jefaturas oficina desayuno viajes internos alimentacion oficina | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.2769 |
| GS-10 | 1 | desayuno reunion mensual jefaturas oficina desayuno viajes internos alimentacion oficina | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2773 |
| GS-10 | 1 | desayuno reunion mensual jefaturas oficina desayuno viajes internos alimentacion oficina | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2839 |
| GS-11 | 1 | almuerzo feria comercial proveedores viajes internos viaticos alimentos | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2715 |
| GS-11 | 1 | almuerzo feria comercial proveedores viajes internos viaticos alimentos | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2741 |
| GS-11 | 1 | almuerzo feria comercial proveedores viajes internos viaticos alimentos | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.3043 |
| GS-12 | 1 | arriendo auto vehiculo liviano P01 Viajes Externos | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.2308 |
| GS-12 | 1 | arriendo auto vehiculo liviano P01 Viajes Externos | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2621 |
| GS-12 | 1 | arriendo auto vehiculo liviano P01 Viajes Externos | Viajes Internos | datos/politica_ficticia.md#P02 | -0.265 |
| GS-13 | 1 | Vehículos Propios Gasolina combustible P01 | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.196 |
| GS-13 | 1 | Vehículos Propios Gasolina combustible P01 | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2479 |
| GS-13 | 1 | Vehículos Propios Gasolina combustible P01 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2631 |
| GS-13 | 1 | P02 Combustible Gasolina vehículo empresa o camioneta arrendada | Viajes Internos | datos/politica_ficticia.md#P02 | -0.221 |
| GS-13 | 1 | P02 Combustible Gasolina vehículo empresa o camioneta arrendada | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.2224 |
