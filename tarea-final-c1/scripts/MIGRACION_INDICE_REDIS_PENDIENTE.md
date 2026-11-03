# Migración del índice Redis: pendiente de verificar y autorizar

**Estado: BLOQUEADO.** No ejecutar una nueva carga sobre el índice `grupo05` hasta
completar el inventario y confirmar la compatibilidad de esquema con la versión
instalada de `langchain-redis`. Este documento no autoriza conexiones, escrituras
ni borrados. No se ha consultado Redis.

## Riesgo de formato e identificadores

La carga actual configura `legacy_key_format=False`, `index_name=REDIS_PREFIJO` y
IDs desnudos (`P01`…`P10`, `RG-01`…`RG-10`). La búsqueda usa la misma configuración.
El diff anterior construía IDs como `f"{prefijo}:{codigo}"`. Eso puede duplicar el
prefijo si el almacén añade `key_prefix` por separado. Es un riesgo diferente de
un doble separador (`::`), que solo aparecería si ambos componentes aportan `:`;
no se debe asumir que ocurre ni que no ocurre sin verificar la implementación y
las claves reales. Tampoco está probado que el formato nuevo encuentre, sobrescriba
o reemplace los documentos antiguos. `add_documents` no constituye prueba de
reemplazo o limpieza de claves de otro formato.

## Procedimiento obligatorio antes de migrar

1. **Autorizar el diagnóstico:** obtener autorización explícita de Alex para el
   inventario de solo lectura y acordar instancia, índice y ventana. No imprimir
   secretos ni valores de conexión.
2. **Inventariar el estado anterior (solo lectura):** guardar en un registro fechado
   las claves/documentos del ámbito `grupo05`, cantidad, IDs, prefijos y muestras
   redactadas. Registrar esquema del índice, campos, tipo/dimensiones de vector,
   métrica, algoritmo y formato de claves. No borrar ni modificar nada.
3. **Verificar el formato efectivo:** en un entorno aislado y con la versión exacta
   instalada, comprobar cómo `legacy_key_format`, `index_name`/`key_prefix` e IDs
   producen las claves. Distinguir prefijo duplicado de separador duplicado. Si no
   se puede demostrar compatibilidad con el inventario, detenerse y proponer un
   índice de destino nuevo; no escribir en el índice existente.
4. **Predecir las claves nuevas:** antes de escribir, registrar los veinte códigos
   únicos (`P01`–`P10`, `RG-01`–`RG-10`), IDs enviados y claves que la librería
   generaría para cada uno. Comparar con el inventario y explicar cada colisión,
   coexistencia o cambio de formato. La predicción debe ser reproducible y revisada.
5. **Respaldo y carga aprobada:** conservar respaldo/restauración comprobable del
   índice anterior. Obtener autorización explícita de Alex para la escritura y
   ejecutar la carga solo después de aprobar el plan. No mezclar validación con
   borrado.
6. **Verificar documentos:** comprobar que existen exactamente los veinte códigos
   previstos, que cada uno se recupera por su código y que sus metadatos y
   `texto_completo` coinciden con los documentos fuente (incluidos hashes y ausencia
   del historial). Comprobar también una búsqueda representativa y que el código
   antiguo no queda inadvertidamente sombreado ni duplicado.
7. **Reversión:** si falla cualquier comprobación, detener consultas/escrituras al
   destino, restaurar el índice anterior desde el respaldo o volver la configuración
   al esquema antiguo únicamente después de verificar que corresponde a ese esquema.
   No eliminar el índice previo como parte de la reversión automática.
8. **Limpieza separada:** identificar las claves antiguas exactas mediante el
   inventario y demostrar que pertenecen exclusivamente a la carga obsoleta. La
   eliminación requiere autorización explícita y específica de Alex, con lista de
   claves revisada, respaldo y plan de reversión. Sin esa autorización no se borra
   ninguna clave.

## Estado de compatibilidad

**Pendiente, no demostrada.** Sin inventario del índice existente y verificación del
formato exacto de la versión instalada no se puede afirmar que `legacy_key_format=False`
sea compatible, que los IDs nuevos actualicen las claves viejas ni que la nueva carga
las reemplace. No conectarse ni ejecutar la migración hasta cerrar los pasos anteriores.
