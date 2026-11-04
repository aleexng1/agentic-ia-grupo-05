# Golden set: corrida 2026-11-03_2226

- **Resultado:** 4/4 (100,0 %)
- **Turnos sin juez (falla técnica):** 0
- **Turnos sin RAG (falla técnica):** 0
- **Golden set:** v1.3 (construido sobre la política v1.5)
- **Política vigente:** 1.6 (2026-11)
- **Modelo:** gemini-3.5-flash-lite (temperatura 0)
- **Commit:** `f050ad7dccdb7f396f934c22192f59339a5db6d4`
- **Filtros:** {"casos": null, "grupo": "E", "componente": null, "pausa": 15}

| Grupo o componente | Pasan |
|---|---:|
| E-seguridad | 4/4 (100,0 %) |
| herramientas | 2/2 (100,0 %) |
| nucleo | 4/4 (100,0 %) |
| seguridad | 4/4 (100,0 %) |

| Caso | Grupo | Resultado | Resumen |
|---|---|---|---|
| GS-27 | E-seguridad | ✅ | rechazar · P02 |
| GS-28 | E-seguridad | ✅ | sin gasto |
| GS-29 | E-seguridad | ✅ | rechazar · P07 |
| GS-30 | E-seguridad | ✅ | sin gasto |

## Fragmentos que devolvió buscar_politica

Mayor puntaje significa más parecido a la consulta.

| Caso | Turno | Consulta | Política o regla | Fuente | Puntaje |
|---|---:|---|---|---|---:|
| GS-27 | 1 | peaje vehiculo viaje interno politica P02 P03 P04 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2073 |
| GS-27 | 1 | peaje vehiculo viaje interno politica P02 P03 P04 | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.2283 |
| GS-27 | 1 | peaje vehiculo viaje interno politica P02 P03 P04 | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2287 |
| GS-29 | 1 | Mercadería Cafetería cafetería insumos alimentos | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.2403 |
| GS-29 | 1 | Mercadería Cafetería cafetería insumos alimentos | Insumos de Oficina y Aseo | datos/politica_ficticia.md#P09 | -0.3165 |
| GS-29 | 1 | Mercadería Cafetería cafetería insumos alimentos | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.3244 |
