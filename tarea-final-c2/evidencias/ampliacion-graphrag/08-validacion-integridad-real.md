# Validacion real de integridad GraphRAG

Fecha: 2026-11-27.
Entorno: ejecucion local contra Neo4j Aura Instance01.
Rama: c2tf/eduardo-cierre-integridad.
Alcance: correcciones H02 y H06 anteriores a la extension de fondos.

## H06 - Integridad del inventario

| Control | Resultado |
|---|---|
| Conexion | PASS |
| Acceso a la base | PASS |
| Conteo original | 24 nodos |
| Inventario completo | 24 nodos y 27 relaciones |
| Contraste con catalogo versionado | PASS |

Se verificaron las identidades, etiquetas, propiedades,
tipos, huellas y relaciones del inventario existente.
No se ejecuto el cargador ni se realizaron escrituras.

## H02 - Consultas reales

| Caso | Cargo | Categoria | Resultado CLP | Tiempo | Control |
|---|---|---|---:|---:|---|
| R01 | Jefe de tienda | P03:hotel | 325000 | 2.969 s | PASS |
| R02 | Analista de Operaciones | P02:hotel | 445000 | 2.766 s | PASS |
| R03 | Analista de Operaciones | P03:hotel | null | 2.719 s | PASS |
| R04 | Jefe de tienda | P02:hotel | 445000 | 2.765 s | PASS |

Resultado: 4/4 casos aprobados.

La ausencia de recorrido R03 no constituye una prohibicion
normativa. Los topes corresponden al documento POL-RG-01 v1.6.
El catalogo organizacional sigue pendiente de aprobacion.

## Limitaciones

- Evidencia de ejecucion local directa, no mediante /chat.
- No se generaron id_ejecucion remotos.
- La extension de fondos permanece deshabilitada.
- La validacion real de H03 se detuvo antes de conectar
  a Redis por el requisito de transporte TLS.
- La autenticacion remota de Heroku sigue pendiente.

Resultados transcritos desde la salida de PowerShell.


## Verificacion previa de la extension

Fecha: 2026-11-27.

- Inventario base: 24 nodos y 27 relaciones.
- Extension instalada: false.
- Cambio realizado: false.
- Resultado: PASS.

Verificacion remota exclusivamente de lectura.
No constituye una aprobacion ni una migracion.
