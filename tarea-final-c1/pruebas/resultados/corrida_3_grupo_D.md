# Golden set: corrida 2026-11-03_2224

- **Resultado:** 2/2 (100,0 %)
- **Turnos sin juez (falla técnica):** 0
- **Turnos sin RAG (falla técnica):** 0
- **Golden set:** v1.3 (construido sobre la política v1.5)
- **Política vigente:** 1.6 (2026-11)
- **Modelo:** gemini-3.5-flash-lite (temperatura 0)
- **Commit:** `f050ad7dccdb7f396f934c22192f59339a5db6d4`
- **Filtros:** {"casos": null, "grupo": "D", "componente": null, "pausa": 15}

| Grupo o componente | Pasan |
|---|---:|
| D-fondo | 2/2 (100,0 %) |
| herramientas | 2/2 (100,0 %) |
| memoria | 2/2 (100,0 %) |
| nucleo | 2/2 (100,0 %) |
| rag | 2/2 (100,0 %) |

| Caso | Grupo | Resultado | Resumen |
|---|---|---|---|
| GS-25 | D-fondo | ✅ | observar · P01 |
| GS-26 | D-fondo | ✅ | observar · P02 |

## Fragmentos que devolvió buscar_politica

Mayor puntaje significa más parecido a la consulta.

| Caso | Turno | Consulta | Política o regla | Fuente | Puntaje |
|---|---:|---|---|---|---:|
| GS-25 | 1 | Vehículos Propios Gasolina (vehículo propio) combustible viaje o visita a tiendas | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.2272 |
| GS-25 | 1 | Vehículos Propios Gasolina (vehículo propio) combustible viaje o visita a tiendas | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-06 | -0.2774 |
| GS-25 | 1 | Vehículos Propios Gasolina (vehículo propio) combustible viaje o visita a tiendas | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2778 |
| GS-26 | 1 | petróleo camioneta empresa viaje combustible P02 P03 P01 P04 | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2269 |
| GS-26 | 1 | petróleo camioneta empresa viaje combustible P02 P03 P01 P04 | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2319 |
| GS-26 | 1 | petróleo camioneta empresa viaje combustible P02 P03 P01 P04 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2349 |
| GS-26 | 1 | petróleo camioneta empresa viaje combustible P02 P03 P01 P04 | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.2505 |
| GS-26 | 1 | petróleo camioneta empresa viaje combustible P02 P03 P01 P04 | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-06 | -0.2762 |
