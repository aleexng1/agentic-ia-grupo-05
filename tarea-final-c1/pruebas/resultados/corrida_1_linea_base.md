# Golden set: corrida 1, línea base (PARCIAL), 2026-11-02

- **Estado:** PARCIAL: 6 de 33 casos (grupo A). Los porcentajes son sobre los casos corridos. Pendientes: grupos B, C, D, E, F.
- **Por qué se detuvo:** el juez no respondió en GS-06 turno 1. La regla de la corrida es detenerse ante una falla técnica. El juez no muestra el error original, así que no está confirmado que fuera un 429.
- **Resultado:** 4/6 (66,7 %)
- **Turnos sin juez (falla técnica):** 1 (GS-06 turno 1)
- **Golden set:** v1.2 (construido sobre la política v1.1)
- **Política vigente:** 1.2 (2026-11)
- **Modelo:** gemini-3.5-flash-lite (temperatura 0)
- **Commit:** `d97b3a50a6a8392520bcc99ec788431f7f1f9e33`
- **Filtros:** {"grupos": ["A"], "pausa": 8}

| Grupo o componente | Pasan |
|---|---:|
| A-limpio | 4/6 (66,7 %) |
| herramientas | 4/6 (66,7 %) |
| nucleo | 4/6 (66,7 %) |
| rag | 4/6 (66,7 %) |

| Causa de los ❌ | Casos | Cuáles |
|---|---:|---|
| Juez sin respuesta (falla técnica) | 1 | GS-06 |
| Otra causa | 1 | GS-03 |

| Caso | Grupo | Resultado | Resumen |
|---|---|---|---|
| GS-01 | A-limpio | ✅ | aprobar · P02 |
| GS-02 | A-limpio | ✅ | aprobar · P02 |
| GS-03 | A-limpio | ❌ | turno 1 · decisión: esperado 'aprobar', obtenido 'observar' (+1 más) |
| GS-04 | A-limpio | ✅ | aprobar · P09 |
| GS-05 | A-limpio | ✅ | aprobar · P07 |
| GS-06 | A-limpio | ❌ | turno 1 · decisión: esperado 'aprobar', obtenido 'observar' |

## Detalle de los ❌

**GS-03** — Analista de personas: coffee break de una capacitación, bajo el tope

- turno 1 · decisión: esperado 'aprobar', obtenido 'observar'
- turno 1 · categoría: esperado 'Capacitaciones', obtenido 'Coffee break'

**GS-06** — Comprador: taxi con voucher a la planta de un proveedor

- turno 1 · decisión: esperado 'aprobar', obtenido 'observar'

## Fragmentos que devolvió buscar_politica

Mayor puntaje significa más parecido a la consulta.

| Caso | Turno | Consulta | Política o regla | Fuente | Puntaje |
|---|---:|---|---|---|---:|
| GS-01 | 1 | peajes transporte flota camiones de reparto politica vehiculos peaje | Flota de Camiones y Camionetas | datos/politica_ficticia.md#P04 | -0.318 |
| GS-01 | 1 | peajes transporte flota camiones de reparto politica vehiculos peaje | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.3498 |
| GS-01 | 1 | peajes transporte flota camiones de reparto politica vehiculos peaje | Viajes Externos | datos/politica_ficticia.md#P03 | -0.3656 |
| GS-01 | 1 | Viajes Internos peaje P02 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.1832 |
| GS-01 | 1 | Viajes Internos peaje P02 | Viajes Externos | datos/politica_ficticia.md#P03 | -0.242 |
| GS-01 | 1 | Viajes Internos peaje P02 | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.2619 |
| GS-02 | 1 | Viajes Internos Almuerzo | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2458 |
| GS-02 | 1 | Viajes Internos Almuerzo | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2772 |
| GS-02 | 1 | Viajes Internos Almuerzo | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.3233 |
| GS-03 | 1 | Capacitaciones Gastos del Personal Bienestar capacitación alimentación | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.2329 |
| GS-03 | 1 | Capacitaciones Gastos del Personal Bienestar capacitación alimentación | Viajes Externos | datos/politica_ficticia.md#P03 | -0.3174 |
| GS-03 | 1 | Capacitaciones Gastos del Personal Bienestar capacitación alimentación | Viajes Internos | datos/politica_ficticia.md#P02 | -0.326 |
| GS-04 | 1 | Insumos de Oficina y Aseo | Insumos de Oficina y Aseo | datos/politica_ficticia.md#P09 | -0.2286 |
| GS-04 | 1 | Insumos de Oficina y Aseo | Mantención de Instalaciones | datos/politica_ficticia.md#P10 | -0.3139 |
| GS-04 | 1 | Insumos de Oficina y Aseo | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.331 |
| GS-05 | 1 | Mercadería Cafetería | Mercadería Cafetería | datos/politica_ficticia.md#P07 | -0.2446 |
| GS-05 | 1 | Mercadería Cafetería | Insumos de Oficina y Aseo | datos/politica_ficticia.md#P09 | -0.3443 |
| GS-05 | 1 | Mercadería Cafetería | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.3491 |
| GS-05 | 1 | Mercadería Cafetería | Mantención de Instalaciones | datos/politica_ficticia.md#P10 | -0.3512 |
| GS-05 | 1 | Mercadería Cafetería | Grúas Horquilla | datos/politica_ficticia.md#P05 | -0.3534 |
| GS-06 | 1 | Locomoción Viajes Externos P02 | Viajes Internos | datos/politica_ficticia.md#P02 | -0.1918 |
| GS-06 | 1 | Locomoción Viajes Externos P02 | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2048 |
| GS-06 | 1 | Locomoción Viajes Externos P02 | Vehículos Propios | datos/politica_ficticia.md#P01 | -0.2377 |
