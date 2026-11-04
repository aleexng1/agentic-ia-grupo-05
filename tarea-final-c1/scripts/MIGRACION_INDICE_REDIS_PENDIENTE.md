# Migración ejecutada: índice Redis `grupo05_v15` — política v1.6

> **Estado al 2026-11-04: CARGA EJECUTADA POR ALEX SEGÚN EVIDENCIA PUBLICADA Y VALIDADA FUNCIONALMENTE.** La carga de `grupo05_v15` se realizó el **2026-11-03** y las pruebas reales posteriores usaron ese índice. Este documento recoge la evidencia del equipo; **Eduardo no ejecutó ni auditó directamente Redis**. El nombre histórico del archivo se conserva para no romper enlaces existentes.

## Decisión vigente del equipo — 2026-11-03

- **Índice anterior:** `grupo05`, informado por Alex con **10 documentos de política v1.4**. Debe conservarse intacto.
- **Nuevo destino:** `grupo05_v15`, nombre acordado por Alex para almacenar **20 documentos de la política POL-RG-01 v1.6**: P01–P10 y RG-01–RG-10.
- El sufijo `_v15` identifica el índice nuevo elegido por el equipo: **no indica la versión del contenido**, que será **1.6**.
- El prefijo local histórico `tarea-final-c1-grupo5` **no es** el índice del equipo y no debe emplearse para el corte.
- La transición documentada se hizo hacia un índice nuevo, sin solicitar borrado ni recarga de `grupo05`. Que el índice antiguo permanezca sin cambios es una afirmación operativa del equipo; no se presenta aquí como inventario independiente.
- **Configuración vigente del equipo:** `REDIS_PREFIJO=grupo05_v15`, confirmada por Alex y reflejada en el README y `.env.example`. Nadie debe recargar por su cuenta un índice que ya funciona.

## Implementación incorporada mediante el PR #34

`scripts/cargar_indice.py` separa exactamente diez políticas y diez reglas generales y valida los códigos, campos, texto embebible, texto completo y ausencia del historial de cambios. Usa `index_name=REDIS_PREFIJO`, `legacy_key_format=False`, 3072 dimensiones, métrica COSINE y algoritmo FLAT; envía los IDs desnudos `P01`…`P10` y `RG-01`…`RG-10` para evitar construir manualmente un prefijo doble.

- **`--plan`:** validación local de la política v1.6 y de sus 20 documentos. No lee secretos del archivo `.env`, no crea clientes y no consulta Redis ni Gemini.
- **`--cargar`:** modo de escritura explícito. Exige `--confirmar-indice grupo05_v15` y que el **prefijo efectivo** `REDIS_PREFIJO` sea exactamente `grupo05_v15`. Solo en ese modo carga el `.env` del proyecto y ejecuta la ingesta. La confirmación CLI es una barrera técnica, **no reemplaza la aprobación humana**.
- **`_cargar_documentos()`:** también rechaza directamente un prefijo diferente de `grupo05_v15`. Sigue siendo una función con capacidad real de escritura; no invocarla fuera del procedimiento autorizado.
- La clave física exacta que genere `langchain-redis` debe comprobarse en Redis; los códigos e IDs del plan **no constituyen un inventario real** ni garantizan el formato físico.
- El script **no** elimina índices ni claves antiguas. La carga puede consumir cuotas de embeddings y fallar a mitad de proceso; no se asume atomicidad.

## Procedimiento de control histórico (no repetir la carga sin nueva autorización)

Los pasos siguientes documentan la secuencia de control y reversión acordada; **no implican que se disponga de un acta individual o de evidencias separadas de cada paso**. Para comprobar la ejecución real, consultar los PR y pruebas citados al final del documento.

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

## Riesgos y puntos de control posteriores

- **Nombre vs versión:** `grupo05_v15` almacena la política **v1.6** por decisión del equipo. Registrar ambos datos en toda evidencia.
- **Formato de claves:** `legacy_key_format=False` e IDs desnudos reducen el riesgo de doble prefijo, pero no verifican por sí solos el formato físico ni los metadatos de la versión instalada.
- **Ingesta parcial:** `add_documents` no garantiza una operación atómica. Si la carga falla, inventariar el estado parcial antes de reintentar; no asumir idempotencia o ausencia de duplicados sin comprobar.
- **Seguridad y cuota:** separar permisos de inspección y escritura, no publicar secretos, limitar invocaciones de Gemini y preservar trazas redactadas.
- **Integración completada:** el PR #37 incorporó `handle_tool_errors=(ToolException,)` en las construcciones de `ToolNode`; las comprobaciones offline posteriores y la corrida 3 se publicaron sin fallas técnicas.
- **Comprobación funcional:** la prueba dirigida con el índice v1.6 ya registró GS-01 3/3. La corrida 3 completa obtuvo 34/34, incluyendo GS-29; las pruebas offline por sí solas no habrían acreditado esos resultados.

## Evidencia publicada y límites de verificación

- **PR #39 (Alex):** documenta la carga efectiva del **2026-11-03**, 20 documentos P01–P10 y RG-01–RG-10, configuración 3.072 dimensiones / COSINE / FLAT e índice `grupo05_v15`: https://github.com/aleexng1/agentic-ia-grupo-05/pull/39.
- **README vigente:** [Embeddings e índice](../README.md#embeddings-e-índice) registra esquema físico, campos y llaves, y la carga comprobada por el operador.
- **Corrida 2:** [33/34 con índice nuevo](../pruebas/resultados/corrida_2.md), sin errores técnicos; GS-29 fue un error de clasificación del LLM, no una falla de Redis.
- **PR #41 y prueba dirigida:** [10/10 ejecuciones, GS-29 3/3](../pruebas/resultados/prueba_dirigida_PR41_general.md) después del ajuste general de los prompts y antes de fusionar.
- **Corrida 3 final:** [34/34](../pruebas/resultados/corrida_3.md), con el código en `f050ad7`, política v1.6 y `grupo05_v15`; cero turnos sin juez y cero sin RAG. El cambio posterior del PR #42 fue solo un comentario de versión en `src/herramientas.py`.
- **Pruebas locales de mantenimiento:** `verificar.py` 43/43, `probar_herramientas.py` 59/59 y `evaluar.py --autoprueba` 89/89. No sustituyen las pruebas reales publicadas.

**Alcance de esta evidencia:** no se adjunta una exportación independiente de las claves físicas ni el historial de autorizaciones por paso. Por tanto, el estado ejecutado se atribuye al registro de Alex/PR #39 y a las recuperaciones efectivas posteriores, sin afirmar que Eduardo inspeccionó directamente Redis.

**Cargador — pendiente ya resuelto en código:** `scripts/cargar_indice.py` captura errores en `_cargar_documentos` y entrega `RuntimeError` con el **tipo de excepción** (`type(error).__name__`), sin incluir el texto potencialmente sensible del SDK. No requiere tocar `src/` ni repetir la corrida final.

**Operación segura después del corte:** no volver a ejecutar `--cargar` por iniciativa individual, no borrar `grupo05`, no exponer URLs ni credenciales y no repetir pruebas reales con Gemini sin coordinar cuota con Alex.
