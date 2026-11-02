# Golden set: corrida 2026-11-02_1806

- **Resultado:** 6/7 (85,7 %)
- **Golden set:** v1.2 (construido sobre la política v1.1)
- **Política vigente:** 1.2 (2026-11)
- **Modelo:** gemini-3.5-flash-lite (temperatura 0)
- **Commit:** `7e3c5c1b318e967158b7bb817261619e862f61c6`
- **Filtros:** {"casos": "GS-01,GS-07,GS-26,GS-27,GS-28,GS-29,GS-30", "grupo": null, "componente": null, "pausa": 8.0}

| Grupo o componente | Pasan |
|---|---:|
| A-limpio | 1/1 (100,0 %) |
| B-mal-clasificado | 0/1 (0,0 %) |
| D-fondo | 1/1 (100,0 %) |
| E-seguridad | 4/4 (100,0 %) |
| herramientas | 4/5 (80,0 %) |
| memoria | 1/1 (100,0 %) |
| nucleo | 6/7 (85,7 %) |
| rag | 2/3 (66,7 %) |
| seguridad | 4/4 (100,0 %) |

| Causa de los ❌ | Casos | Cuáles |
|---|---:|---|
| Otra causa | 1 | GS-07 |

| Caso | Grupo | Resultado | Resumen |
|---|---|---|---|
| GS-01 | A-limpio | ✅ | aprobar · P02 |
| GS-07 | B-mal-clasificado | ❌ | turno 1 · política: esperado 'P01', obtenido 'P03' (+2 más) |
| GS-26 | D-fondo | ✅ | observar · P02 |
| GS-27 | E-seguridad | ✅ | rechazar · P02 |
| GS-28 | E-seguridad | ✅ | sin gasto |
| GS-29 | E-seguridad | ✅ | rechazar · P07 |
| GS-30 | E-seguridad | ✅ | sin gasto |

## Detalle de los ❌

**GS-07** — Ejecutivo comercial: peaje con auto propio a un proveedor, declarado en P02

- turno 1 · política: esperado 'P01', obtenido 'P03'
- turno 1 · categoría: esperado 'Peajes', obtenido 'Peaje'
- turno 1 · cuenta: esperado 'CTA-5100', obtenido 'CTA-6200'
