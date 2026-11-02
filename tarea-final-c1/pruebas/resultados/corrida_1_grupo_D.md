# Golden set: corrida 2026-11-02_1839

- **Resultado:** 2/2 (100,0 %)
- **Turnos sin juez (falla técnica):** 0
- **Golden set:** v1.2 (construido sobre la política v1.1)
- **Política vigente:** 1.3 (2026-11)
- **Modelo:** gemini-3.5-flash-lite (temperatura 0)
- **Commit:** `8949700fa5613e0ec78acd7f8f6cf5e850b89db3`
- **Filtros:** {"casos": null, "grupo": "D", "componente": null, "pausa": 15.0}

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
| GS-25 | 1 | Vehículos Propios Gasolina combustible vehículo propio gasto personal arriendo auto liviano | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.2136 |
| GS-25 | 1 | Vehículos Propios Gasolina combustible vehículo propio gasto personal arriendo auto liviano | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2681 |
| GS-25 | 1 | Vehículos Propios Gasolina combustible vehículo propio gasto personal arriendo auto liviano | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2879 |
| GS-25 | 1 | Vehículos Propios Gasolina combustible vehículo propio gasto personal arriendo auto liviano | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2883 |
| GS-25 | 1 | Vehículos Propios Gasolina combustible vehículo propio gasto personal arriendo auto liviano | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.2986 |
| GS-26 | 1 | Petróleo vehículo empresa camioneta arrendada Viajes Internos | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2559 |
| GS-26 | 1 | Petróleo vehículo empresa camioneta arrendada Viajes Internos | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.2597 |
| GS-26 | 1 | Petróleo vehículo empresa camioneta arrendada Viajes Internos | Viajes Externos | datos/politica_ficticia.md#P03 | -0.273 |
