# Matriz de evidencias de la pauta

Dónde se demuestra cada criterio y cada bono declarado. Estado final al 2026-11-04, sobre `main` en la
versión de este documento.

## Cómo se evalúa, en resumen

La nota parte en 1,0. Los criterios base suman hasta 3,0, lo que da un máximo de 4,0. Los bonos suman
hasta 3,0 más. Si el flujo central falla, la nota queda limitada a 3,0. Si la seguridad básica se
rompe, se pierden sus 0,5. Un bono que falla no suma, y cada bono debe declararse junto con el lugar
donde se ejecuta. Un mismo mecanismo no recibe doble crédito.

Declaramos bonos por 4,0, sobre un tope de 3,0: hay 1,0 de margen.

## Estados

- ✅ **Demostrado:** el mecanismo funciona y hay evidencia guardada.
- 🟡 **Falta evidencia:** el mecanismo existe, pero falta mostrarlo o medirlo.
- 🔴 **Pendiente:** falta construir algo para que el criterio se cumpla.

## Dónde está la evidencia

- **Notebook ejecutado:** [`agente_ejecutado.ipynb`](../agente_ejecutado.ipynb), con las salidas de una
  ejecución completa de arriba abajo. Se hizo el 2026-11-04 desde `main` en `bcd61cc`, con Gemini real y el
  índice `grupo05_v15`. Cada criterio tiene al menos una celda **en vivo**, además de la evidencia
  guardada. Su resumen final da **42 ✅, 0 ⚠️ y 0 ❌**. Se revisó que no tuviera claves, URLs de Redis,
  rutas personales ni correos. `agente.ipynb` es el mismo notebook sin salidas.
- **Corrida final del golden set:** **corrida 3** (`corrida_3.md`): **34 de 34**, el 2026-11-03, con `main`
  en `f050ad7`, la política v1.6 y el índice `grupo05_v15` (20 documentos). No hubo fallas técnicas: 0
  turnos sin juez y 0 sin RAG. La corrida 2 (33 de 34) y la corrida 1 (31 de 33) quedan como comparación
  en `evolucion.md`. Después de la corrida 3, el único cambio en `src/` fue un comentario de versión en
  `src/herramientas.py` (PR #42), sin efecto en el comportamiento.

Las rutas de resultados son relativas a `pruebas/resultados/`. "Sección N" es la sección del notebook.

## Criterios base

| Criterio | Puntos | Mecanismo | Dónde se ejecuta | Casos | Evidencia | Estado |
|---|---:|---|---|---|---|---|
| Caso y criterio de éxito | 0,5 | Define el problema, el usuario, el alcance y cómo se comprueba | Sección 1; [`caso_y_criterio.md`](caso_y_criterio.md) | Ejemplo: GS-07 | `docs/caso_y_criterio.md`; sección 1 de `agente_ejecutado.ipynb` | ✅ |
| LLM y trazabilidad | 0,5 | Usa Gemini real y anota cada paso del agente | Secciones 0, 2 y 3 (modelo, variables sin secretos, traza resumida de `registrar_traza`); sección 5 (`PROMPT_SISTEMA`); sección 9 (modelo y `PROMPT_JUEZ`); `src/config.py`: `obtener_llm`, `registrar_traza` | Normal: G-001 en vivo | `agente_ejecutado.ipynb`, sección 3: traza llm → buscar → validar → emitir → juez → registro. `corrida_3.json`: modelo, commit, índice y herramientas por turno | ✅ En `src/config.py:45` queda el comentario `TODO(nucleo)` del stub, pero la función ya imprime la traza; el código está congelado |
| ReAct y condición de parada | 1,0 | El LLM pide una herramienta, lee la observación y decide; se detiene al llegar al máximo de pasos | Sección 3; `src/grafo.py`: `construir_agente`, `nodo_llm`, `nodo_ejecutar_herramientas`, `elegir_siguiente`, `nodo_parada` | Normal: G-001 en vivo, GS-01, GS-07. Adversarial: GS-10 agotó los pasos | `agente_ejecutado.ipynb`, sección 3: G-001 APROBAR P01. `corrida_3.md`: 30 de 36 turnos validan y emiten veredicto. `estabilidad_v1_4.md`: parada real en GS-10, ronda 3 | ✅ La parada real se vio con el límite anterior de 6 pasos; el límite de 10 se prueba con un LLM falso (`verificar.py`, bloque 6) |
| Historial | 0,5 | Cada hilo conserva la conversación y el segundo turno usa lo anterior | Sección 4; `src/grafo.py`: `InMemorySaver`, `conversar` | Normal: GS-32 en vivo. También GS-26, turno 2 | `agente_ejecutado.ipynb`, sección 4: "Te llamas Pedro y trabajas en el Centro de Distribución". `corrida_3_grupo_F.md`, `corrida_3_grupo_D.md` | ✅ |
| Seguridad básica | 0,5 | El prompt limita el alcance; los datos del gasto no son instrucciones; sin gasto no se declara una decisión; una aprobación sin veredicto válido se reemplaza | Sección 5; `src/seguridad.py`: `PROMPT_SISTEMA`; `src/grafo.py`: `nodo_llm` | Normal: GS-28 en vivo, GS-30. Adversarial: jailbreak por chat en vivo, GS-27 (orden en la glosa), GS-29 (falsa autorización) | `agente_ejecutado.ipynb`, sección 5: GS-28 fuera de alcance sin herramientas; el jailbreak no declara decisión, no deja veredicto y no escribe filas. `corrida_3_grupo_E.md`: 4 de 4, sin aprobación indebida | ✅ |

## Bonos declarados

| Criterio | Puntos | Mecanismo | Dónde se ejecuta | Casos | Evidencia | Estado |
|---|---:|---|---|---|---|---|
| Memoria avanzada (fondo por rendir) | +1,0 | El saldo se descuenta al aprobar y se usa en la decisión siguiente | Sección 7; `src/memoria.py`: `revisar_saldo`, `anexar_revision_saldo`, `aplicar_veredicto`; `src/grafo.py`: `nodo_cerrar` | Normal: GS-26 en vivo. Adversarial: GS-25 (supera el saldo); FR-999 con LLM falso | `agente_ejecutado.ipynb`, sección 7: turno 1 APROBAR ($50.000 → $20.000), turno 2 OBSERVAR por RG-08. `corrida_3_grupo_D.md`: 2 de 2 | ✅ |
| RAG (Redis, índice `grupo05_v15`) | +1,0 | Busca en la política, cita la fuente y no busca cuando no hace falta. 20 documentos (P01-P10 y RG-01-RG-10), configuración explícita (3.072, COSINE, FLAT) y un error de Redis vuelve al LLM sin cortar el turno | Sección 6; `src/rag.py`: `buscar_politica`; `scripts/cargar_indice.py`; `src/grafo.py`: `ToolNode` | En vivo: "Hola" (no busca) y el plazo (GS-33, busca). También GS-07, GS-23, GS-34 | `agente_ejecutado.ipynb`, sección 6: configuración leída del índice real; GS-33 trae RG-03 primero y responde "día 10 del mes siguiente". `corrida_3.md`: rag 28 de 28, 107 fragmentos con fuente y puntaje | ✅ |
| Acción avanzada (registro SQLite) | +0,5 | El grafo registra el veredicto, con estado antes y después; el LLM no tiene esa herramienta | Sección 8; `src/registro.py`: `registrar_veredicto`, `leer_registro`, `reiniciar_registro`; `src/grafo.py`: `nodo_cerrar` | Normal: GS-07 en vivo, GS-26. Adversarial: GS-27, GS-29, GS-30 | `agente_ejecutado.ipynb`, sección 8: base temporal vacía → 1 fila (G-0701, observar) → reinicio → vacía, y un segundo reinicio seguro. `corrida_3_grupo_D.md`, `corrida_3_grupo_E.md` | ✅ |
| Golden set | +0,5 | Casos con su respuesta correcta y un evaluador que los compara | Sección 11; `pruebas/golden_set.json`; `pruebas/evaluar.py`: `evaluar`, `mostrar_tabla` | 34 casos: normales, mal clasificados y adversariales | `corrida_3.md`: **34 de 34**, la corrida final, completa y sin fallas técnicas. `agente_ejecutado.ipynb`, sección 11: resumen de la corrida 3 y GS-07 en vivo. `evolucion.md`: comparación con las corridas 1 y 2 | ✅ Versionado (v1.3) y ejecutado completo con el código final, sin fallos sin resolver |
| Juez LLM | +0,5 | Un segundo LLM revisa el veredicto con la validación como evidencia, y sin su visto bueno no se aprueba | Sección 9; `src/seguridad.py`: `juzgar_con_validacion`, `PROMPT_JUEZ`; `src/grafo.py`: `nodo_cerrar` | En vivo: GS-01 (benigno) y GS-29 (adversarial) | `agente_ejecutado.ipynb`, sección 9: modelo, `PROMPT_JUEZ`, y para cada caso `valido`, la razón y la decisión aplicada. `prueba_dirigida_PR41_general.md`: la razón en cada dictamen. `corrida_3.md`: 0 turnos sin juez. `evolucion.md`: antes y después | ✅ En la primera ejecución completa el juez marcó como no válido el rechazo correcto de GS-29; como solo frena aprobaciones, la decisión aplicada no cambió. En la ejecución entregada lo validó |
| Guardrail "piso de reglas" | +0,5 | Código sin LLM: si el LLM propone algo más permisivo que las reglas, se corrige; si altera el gasto, se valida el original y se anota qué cambió. Es un mecanismo distinto del juez LLM | Sección 10; `src/grafo.py`: `nodo_cerrar`, `_estado_con_gasto_original`; `src/herramientas.py`: `decision_sugerida`, `campos_alterados`; `pruebas/probar_herramientas.py`: `prueba_piso_en_agente`, `prueba_piso_con_gemini` | Simulado y rotulado: GS-16 (el piso corrige), GS-01 (no interviene), GS-27 (bloquea la aprobación con la fecha alterada). Real: GS-01 benigno | `agente_ejecutado.ipynb`, sección 10: los 3 casos simulados con la decisión aplicada y el benigno real con Gemini. `pruebas/probar_herramientas.py`, secciones E, G y H | ✅ El caso adversarial es simulado porque no es fiable pedirle a Gemini que se equivoque a propósito; en las corridas reales el piso no tuvo que intervenir |

## Requisito general

| Criterio | Puntos | Mecanismo | Dónde se ejecuta | Evidencia | Estado |
|---|---:|---|---|---|---|
| Notebook ejecutable de arriba abajo | Base de la entrega | Todas las secciones corren en orden, con Gemini y Redis; sin `.env`, las celdas en vivo se detienen con un mensaje claro | `agente.ipynb` | `agente_ejecutado.ipynb`: 13 celdas de código sin errores, 42 ✅, 0 ⚠️ y 0 ❌ | ✅ |

## Bonos no declarados

- **Workflow adicional:** no se usó. El caso se resuelve con un solo ciclo ReAct y un cierre determinista.
- **MCP:** no se usó. Las herramientas son funciones locales del mismo proyecto, sin un servicio externo que conectar.

## Orden de cierre

Cada paso usa el resultado del anterior; si un paso cambia `src/`, se repite desde la corrida.

1. ✅ **Arreglo de GS-29** (Eduardo, PR #41): un solo cambio en `PROMPT_SISTEMA` y `PROMPT_JUEZ`, solo con
   reglas generales.
2. ✅ **Corrida 3** (Alex): 34 de 34 con el código final (`f050ad7`). **Desde aquí no se cambia `src/`.**
3. ✅ **Secciones del notebook** (Matías, completadas por Alex en los PR #46, #48 y #49): 5, 6, 8, 9 y la del
   guardrail, en vivo y con el código final.
4. ✅ **Ejecución completa** del notebook desde cero, y `agente_ejecutado.ipynb` revisado para que no tenga
   secretos ni rutas personales (PR #50).
5. ✅ **README y esta matriz** con la evidencia final. Los registros de prompts se revisaron: ver la lista de
   cierre.

## Lista de cierre antes de entregar

- [x] Actualizar en el README los límites conocidos que ya se hayan resuelto.
- [x] Actualizar esta matriz con la evidencia de la corrida final (corrida 3) y del notebook ejecutado.
- [x] Confirmar que el índice tiene la política v1.6 (`grupo05_v15`, comprobado el 2026-11-03).
- [x] Ejecutar el notebook completo de arriba abajo, desde cero (2026-11-04, `agente_ejecutado.ipynb`).
- [ ] Revisar que los prompts de desarrollo de los 4 estén completos. Están revisados, pero quedan dos
  limitaciones: en el de Eduardo, la fecha y el modelo de 8 entradas antiguas no se pueden recuperar y las
  entradas de los PR #34, #38 y #41 son síntesis, no prompts literales, como él mismo declara; en el de
  Matías, el párrafo "Estado de prompts" quedó desactualizado.
- [x] Entregar `agente.ipynb` limpio y `agente_ejecutado.ipynb` con salidas, revisado para que no
  tenga secretos (fuera del `.gitignore` desde el PR #50).
