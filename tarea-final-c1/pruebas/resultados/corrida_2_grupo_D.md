# Golden set: corrida 2026-11-03_2109

- **Resultado:** 2/2 (100,0 %)
- **Turnos sin juez (falla técnica):** 0
- **Turnos sin RAG (falla técnica):** 0
- **Golden set:** v1.3 (construido sobre la política v1.5)
- **Política vigente:** 1.6 (2026-11)
- **Modelo:** gemini-3.5-flash-lite (temperatura 0)
- **Commit:** `5bbfd5d1a706b598661bdb3f23e39108dd87ea40`
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
| GS-25 | 1 | Vehículos Propios Gasolina (vehículo propio) P01 | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.1817 |
| GS-25 | 1 | Vehículos Propios Gasolina (vehículo propio) P01 | Reglas generales | datos/politica_ficticia.md#reglas-generales/RG-06 | -0.2376 |
| GS-25 | 1 | Vehículos Propios Gasolina (vehículo propio) P01 | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2471 |
| GS-26 | 1 | petróleo combustible vehículos empresa camión flota viajes internos P02 P03 P04 | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2115 |
| GS-26 | 1 | petróleo combustible vehículos empresa camión flota viajes internos P02 P03 P04 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2196 |
| GS-26 | 1 | petróleo combustible vehículos empresa camión flota viajes internos P02 P03 P04 | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2351 |
| GS-26 | 1 | petróleo combustible vehículos empresa camión flota viajes internos P02 P03 P04 | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.2653 |
| GS-26 | 1 | petróleo combustible vehículos empresa camión flota viajes internos P02 P03 P04 | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.2772 |
