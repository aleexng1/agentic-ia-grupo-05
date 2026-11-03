# Estabilidad tras política v1.4

- **Qué mide:** si GS-07, GS-10 y GS-29 pasan de forma estable después de las aclaraciones de la v1.4.
- **Cómo:** 3 rondas de los 3 casos, con `--pausa 15`, después de recargar el índice.
- **Resultado:** 8 de 9 repeticiones pasan.
- **Turnos sin juez (falla técnica):** 0
- **Política:** 1.4 (2026-11) · **Golden set:** v1.2 · **Modelo:** gemini-3.5-flash-lite · **Commit:** `b03fd4c`

| Caso | Pasa | Ronda 1 | Ronda 2 | Ronda 3 |
|---|---:|---|---|---|
| GS-07 | 3 de 3 | ✅ observar, P01 | ✅ observar, P01 | ✅ observar, P01 |
| GS-10 | 2 de 3 | ✅ observar, P08 | ✅ observar, P08 | ❌ sin veredicto |
| GS-29 | 3 de 3 | ✅ rechazar, P07 | ✅ rechazar, P07 | ✅ rechazar, P07 |

## Detalle de los ❌

**GS-10, ronda 3** — Jefa administrativa: desayuno de reunión interna, declarado en P02

- **Respuesta:** Me detuve: alcancé el máximo de 6 pasos sin una decisión final.
- **Herramientas:** buscar_politica, buscar_politica, validar_gasto, validar_gasto, emitir_veredicto, validar_gasto
- **Lectura:** agotó los 6 pasos sin un `emitir_veredicto` válido. No hubo veredicto, aprobación ni registro. El evaluador no guarda el texto del error de la herramienta.

| Consulta | Política o regla | Fuente | Puntaje |
|---|---|---|---:|
| desayuno reunion mensual jefaturas oficina desayuno viajes internos alimentacion | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2698 |
| desayuno reunion mensual jefaturas oficina desayuno viajes internos alimentacion | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2826 |
| desayuno reunion mensual jefaturas oficina desayuno viajes internos alimentacion | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.2836 |
| P08 gastos del personal categorias alimentacion reunion interna oficina | Gastos del Personal | datos/politica_ficticia.md#P08 | -0.1492 |
| P08 gastos del personal categorias alimentacion reunion interna oficina | Viajes Internos | datos/politica_ficticia.md#P02 | -0.2058 |
| P08 gastos del personal categorias alimentacion reunion interna oficina | Viajes Externos | datos/politica_ficticia.md#P03 | -0.2077 |

## Fragmentos por ronda

Mayor puntaje significa más parecido a la consulta.

| Ronda | Caso | Consulta | Política o regla | Puntaje |
|---:|---|---|---|---:|
| 1 | GS-07 | peaje auto propio vehicular viajes internos | Viajes Internos | -0.2494 |
| 1 | GS-07 | peaje auto propio vehicular viajes internos | Vehículos Propios | -0.2558 |
| 1 | GS-07 | peaje auto propio vehicular viajes internos | Viajes Externos | -0.271 |
| 1 | GS-10 | desayuno reunion mensual jefaturas oficina desayuno viajes internos alimentacion P02 P03 | Viajes Internos | -0.2071 |
| 1 | GS-10 | desayuno reunion mensual jefaturas oficina desayuno viajes internos alimentacion P02 P03 | Viajes Externos | -0.219 |
| 1 | GS-10 | desayuno reunion mensual jefaturas oficina desayuno viajes internos alimentacion P02 P03 | Gastos del Personal | -0.2469 |
| 1 | GS-10 | desayuno reunion mensual jefaturas oficina desayuno viajes internos alimentacion P02 P03 | Mercadería Cafetería | -0.2712 |
| 1 | GS-10 | desayuno reunion mensual jefaturas oficina desayuno viajes internos alimentacion P02 P03 | Vehículos Propios | -0.2761 |
| 1 | GS-29 | Mercadería Cafetería | Mercadería Cafetería | -0.2446 |
| 1 | GS-29 | Mercadería Cafetería | Gastos del Personal | -0.3429 |
| 1 | GS-29 | Mercadería Cafetería | Insumos de Oficina y Aseo | -0.3443 |
| 2 | GS-07 | peaje auto propio o particular viajes internos | Viajes Internos | -0.2729 |
| 2 | GS-07 | peaje auto propio o particular viajes internos | Vehículos Propios | -0.2753 |
| 2 | GS-07 | peaje auto propio o particular viajes internos | Viajes Externos | -0.2933 |
| 2 | GS-10 | desayuno reunion mensual de jefaturas en oficina alimentacion viajes internos adm | Viajes Internos | -0.2573 |
| 2 | GS-10 | desayuno reunion mensual de jefaturas en oficina alimentacion viajes internos adm | Gastos del Personal | -0.2656 |
| 2 | GS-10 | desayuno reunion mensual de jefaturas en oficina alimentacion viajes internos adm | Viajes Externos | -0.2666 |
| 2 | GS-29 | Mercadería Cafetería | Mercadería Cafetería | -0.2446 |
| 2 | GS-29 | Mercadería Cafetería | Gastos del Personal | -0.3429 |
| 2 | GS-29 | Mercadería Cafetería | Insumos de Oficina y Aseo | -0.3443 |
| 3 | GS-07 | peaje vehículo propio visita a proveedor viajes internos transportes locales | Viajes Internos | -0.2635 |
| 3 | GS-07 | peaje vehículo propio visita a proveedor viajes internos transportes locales | Vehículos Propios | -0.2635 |
| 3 | GS-07 | peaje vehículo propio visita a proveedor viajes internos transportes locales | Viajes Externos | -0.2669 |
| 3 | GS-07 | peaje vehículo propio visita a proveedor viajes internos transportes locales | Flota de Camiones y Camionetas | -0.3051 |
| 3 | GS-07 | peaje vehículo propio visita a proveedor viajes internos transportes locales | Servicios del Taller Marino | -0.3146 |
| 3 | GS-10 | desayuno reunion mensual jefaturas oficina desayuno viajes internos alimentacion | Viajes Internos | -0.2698 |
| 3 | GS-10 | desayuno reunion mensual jefaturas oficina desayuno viajes internos alimentacion | Viajes Externos | -0.2826 |
| 3 | GS-10 | desayuno reunion mensual jefaturas oficina desayuno viajes internos alimentacion | Gastos del Personal | -0.2836 |
| 3 | GS-10 | P08 gastos del personal categorias alimentacion reunion interna oficina | Gastos del Personal | -0.1492 |
| 3 | GS-10 | P08 gastos del personal categorias alimentacion reunion interna oficina | Viajes Internos | -0.2058 |
| 3 | GS-10 | P08 gastos del personal categorias alimentacion reunion interna oficina | Viajes Externos | -0.2077 |
| 3 | GS-29 | Mercadería Cafetería | Mercadería Cafetería | -0.2446 |
| 3 | GS-29 | Mercadería Cafetería | Gastos del Personal | -0.3429 |
| 3 | GS-29 | Mercadería Cafetería | Insumos de Oficina y Aseo | -0.3443 |
