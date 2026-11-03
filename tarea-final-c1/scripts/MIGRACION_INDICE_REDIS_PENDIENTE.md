# Plan de carga segura de Redis: índice nuevo `grupo05_v15` (pendiente de autorización)

> **Estado: PREPARADO EN CÓDIGO, NO EJECUTADO.** Este documento no autoriza consultar, crear, recargar ni eliminar índices o claves. **Alex coordina y ejecuta** el inventario y la carga, con autorizaciones separadas para lectura y escritura. El PR #34 no debe interpretarse como autorización operacional.

## Decisión vigente del equipo — 2026-11-03

- **Índice anterior:** `grupo05`, informado por Alex con **10 documentos de política v1.4**. Debe conservarse intacto.
- **Nuevo destino:** `grupo05_v15`, nombre acordado por Alex para almacenar **20 documentos de la política POL-RG-01 v1.6**: P01–P10 y RG-01–RG-10.
- El sufijo `_v15` identifica el índice nuevo elegido por el equipo: **no indica la versión del contenido**, que será **1.6**.
- El prefijo local histórico `tarea-final-c1-grupo5` **no es** el índice del equipo y no debe emplearse para el corte.
- No se hará una actualización destructiva ni una recarga sobre `grupo05`. La transición será por creación y validación del índice nuevo, seguida de un cambio de configuración coordinado.
- Hasta que Alex confirme la carga y el corte, los participantes **no deben cambiar** su `REDIS_PREFIJO` para consultas reales ni ejecutar la carga por su cuenta.

## Implementación preparada en el PR #34

`scripts/cargar_indice.py` separa exactamente diez políticas y diez reglas generales y valida los códigos, campos, texto embebible, texto completo y ausencia del historial de cambios. Usa `index_name=REDIS_PREFIJO`, `legacy_key_format=False`, 3072 dimensiones, métrica COSINE y algoritmo FLAT; envía los IDs desnudos `P01`…`P10` y `RG-01`…`RG-10` para evitar construir manualmente un prefijo doble.

- **`--plan`:** validación local de la política v1.6 y de sus 20 documentos. No lee secretos del archivo `.env`, no crea clientes y no consulta Redis ni Gemini.
- **`--cargar`:** modo de escritura explícito. Exige `--confirmar-indice grupo05_v15` y que el **prefijo efectivo** `REDIS_PREFIJO` sea exactamente `grupo05_v15`. Solo en ese modo carga el `.env` del proyecto y ejecuta la ingesta. La confirmación CLI es una barrera técnica, **no reemplaza la aprobación humana**.
- **`_cargar_documentos()`:** también rechaza directamente un prefijo diferente de `grupo05_v15`. Sigue siendo una función con capacidad real de escritura; no invocarla fuera del procedimiento autorizado.
- La clave física exacta que genere `langchain-redis` debe comprobarse en Redis; los códigos e IDs del plan **no constituyen un inventario real** ni garantizan el formato físico.
- El script **no** elimina índices ni claves antiguas. La carga puede consumir cuotas de embeddings y fallar a mitad de proceso; no se asume atomicidad.

## Procedimiento de ejecución reservado para Alex

1. **Autorizar lectura de forma expresa.** Acordar instancia Redis, identidad autorizada, índice `grupo05`, alcance de consultas y ventana. No registrar URLs con credenciales ni claves de API.
2. **Inventario anterior, solo lectura.** Documentar cantidad (reportada: 10), claves, códigos, prefijos, esquema, campos, tipo/dimensiones de vector, métrica, algoritmo, versión de la política y respaldo/reversión posible. Diferenciar lo observado de lo reportado. Verificar también si el índice de destino `grupo05_v15` ya existe; **si existe, detener la carga** hasta inventariarlo y evaluar colisiones.
3. **Validar el plan local.** Con la versión exacta del código y dependencias, ejecutar `python scripts/cargar_indice.py --plan`: deben aparecer 20 documentos de v1.6. Revisar un manifiesto reproducible de códigos, IDs, fuentes, hashes y campos esperados; no asumir nombres de claves sin verificarlos.
4. **Aprobar por separado la escritura.** Alex confirma explícitamente entorno, índice de destino `grupo05_v15`, alcance, responsable, presupuesto/cuota, ventana y condición de reversión. **No** autoriza borrar ni sobrescribir `grupo05`.
5. **Configurar solo el proceso de carga autorizado.** El prefijo efectivo de ese proceso debe ser `REDIS_PREFIJO=grupo05_v15`. Verificar que ninguna variable heredada del proceso prevalezca sobre el `.env`. No mostrar el valor de `REDIS_URL` ni `GOOGLE_API_KEY`.
6. **Ejecutar la carga únicamente con autorización:** `python scripts/cargar_indice.py --cargar --confirmar-indice grupo05_v15`. Esta instrucción es **solo para Alex**, no un paso de pruebas offline.
7. **Inventario posterior, solo lectura.** Verificar en `grupo05_v15`: índice existente, esquema esperado (3072/COSINE/FLAT), **20 documentos únicos**, códigos P01–P10 y RG-01–RG-10, contenido v1.6, fuentes, `texto_completo`, `contenido_sha256`, ausencia del historial y ausencia de claves duplicadas. Comprobar también que `grupo05` conserve sus 10 documentos anteriores, sin cambios.
8. **Pruebas de recuperación dirigidas.** Solo con autorización de consumo y con el índice nuevo validado: búsqueda representativa y casos GS-07, GS-10 y GS-29; comprobar fragmentos, metadatos y clasificación. Registrar resultados reales, no inferirlos de pruebas simuladas.
9. **Corte coordinado.** Tras la aceptación de Alex, comunicar al equipo que debe configurar `REDIS_PREFIJO=grupo05_v15`, reiniciar procesos o limpiar cachés de conexiones según corresponda y repetir las comprobaciones de lectura. No efectuar el corte antes de la validación.
10. **Reversión sin borrado.** Ante una anomalía, detener carga/corte, conservar evidencia y volver al índice anterior `grupo05` solo si se verificó previamente su compatibilidad con el código lector del momento. Revertir configuración no restaura automáticamente un índice modificado; por eso el antiguo permanece intacto. Cualquier limpieza de `grupo05_v15` requiere decisión y autorización separadas de Alex.

## Riesgos y puntos de control

- **Nombre vs versión:** `grupo05_v15` almacenará política **v1.6** por decisión del equipo. Registrar ambos datos en toda evidencia.
- **Formato de claves:** `legacy_key_format=False` e IDs desnudos reducen el riesgo de doble prefijo, pero no verifican por sí solos el formato físico ni los metadatos de la versión instalada.
- **Ingesta parcial:** `add_documents` no garantiza una operación atómica. Si la carga falla, inventariar el estado parcial antes de reintentar; no asumir idempotencia o ausencia de duplicados sin comprobar.
- **Seguridad y cuota:** separar permisos de inspección y escritura, no publicar secretos, limitar invocaciones de Gemini y preservar trazas redactadas.
- **Integración:** antes del uso operativo, coordinar con Matías el manejo de `ToolException` en las dos construcciones de `ToolNode` y verificar el grafo con fallos RAG simulados.
- **Comprobación funcional:** las pruebas offline no equivalen a recuperación real desde Redis ni a resultados correctos de Gemini. GS-01 debe revalidarse con la política v1.6.

## Evidencia disponible y pendiente

**Disponible:** política local v1.6, plan offline de 20 documentos, comprobaciones del cargador contra escritura en el índice antiguo, `verificar.py` con 42 aciertos/0 fallos y servicio RAG omitido sin conectividad, autoprueba 88/88 y pruebas de herramientas 59/59. No son pruebas de carga real.

**Pendiente:** aprobación de lectura, inventario anterior y existencia del destino, autorización separada de escritura, carga ejecutada por Alex, inventario posterior, consultas reales, prueba de GS-01 y corte coordinado.

**Prohibido mientras esté pendiente:** ejecutar `--cargar` por iniciativa individual, escribir en `grupo05`, borrar claves o presentar salidas simuladas como trazas reales.
