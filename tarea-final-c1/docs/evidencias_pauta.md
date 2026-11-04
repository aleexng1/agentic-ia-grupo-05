# Matriz de evidencias de la pauta

Dónde se demuestra cada criterio y cada bono declarado. Estado al 2026-11-03, sobre `main` en la
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

Las rutas de resultados son relativas a `pruebas/resultados/`. El notebook no guarda salidas, así que la evidencia de ejecución está en esos
archivos, no en el notebook.

La evidencia principal es la **corrida 3, la corrida final** (`corrida_3.md`): **34 de 34 casos pasan**,
el 2026-11-03, con `main` en `f050ad7`, la política v1.6 y el índice `grupo05_v15` (20 documentos). No hubo
fallas técnicas: 0 turnos sin juez y 0 sin RAG. Desde esta corrida, el código del agente (`src/`) queda
congelado. La corrida 2 (33 de 34) y la corrida 1 (31 de 33) quedan como comparación en `evolucion.md`.
Después de la corrida 3, el único cambio en `src/` fue un comentario de versión en `src/herramientas.py` (PR #42), sin efecto en el comportamiento.

## Criterios base

| Criterio | Puntos | Mecanismo | Dónde se ejecuta | Casos | Evidencia | Estado y qué falta |
|---|---:|---|---|---|---|---|
| Caso y criterio de éxito | 0,5 | Define el problema, el usuario, el alcance y cómo se comprueba | Notebook, sección 1; [`caso_y_criterio.md`](caso_y_criterio.md) | Ejemplo: GS-07 | `docs/caso_y_criterio.md` | ✅ Queda listo al unir este trabajo |
| LLM y trazabilidad | 0,5 | Usa Gemini real y anota cada paso del agente | Secciones 0, 2 y 3; `src/config.py`: `obtener_llm`, `registrar_traza`; `src/grafo.py`: `nodo_llm` | Normal: GS-01 | `corrida_3.json` (modelo, commit, índice y herramientas por turno) | 🟡 Gemini real está demostrado. Falta ver las trazas en el notebook, porque el evaluador las apaga. `registrar_traza` sigue marcada como stub en `src/config.py:45` (Matías) |
| ReAct y condición de parada | 1,0 | El LLM pide una herramienta, lee la observación y decide; se detiene al llegar al máximo de pasos | Sección 3; `src/grafo.py`: `construir_agente`, `nodo_llm`, `nodo_ejecutar_herramientas`, `elegir_siguiente`, `nodo_parada` | Normal: GS-01, GS-07. Adversarial: GS-10 agotó los pasos | `corrida_3.md`: 30 de 36 turnos validan y emiten veredicto; los otros 6 no tienen gasto que validar o ya lo validaron. `estabilidad_v1_4.md`: parada real en GS-10, ronda 3 | ✅ La parada real se vio con el límite anterior de 6 pasos. El límite de 10 solo se probó con un LLM falso (`verificar.py`, bloque 6) |
| Historial | 0,5 | Cada hilo conserva la conversación y el segundo turno usa lo anterior | Sección 4; `src/grafo.py`: `InMemorySaver`, `conversar` | Normal: GS-32. También GS-26, turno 2 | `corrida_3_grupo_F.md`, `corrida_3_grupo_D.md` | ✅ |
| Seguridad básica | 0,5 | El prompt limita el alcance; los datos del gasto no son instrucciones; sin gasto no se declara una decisión; una aprobación sin veredicto válido se reemplaza | Sección 5; `src/seguridad.py`: `PROMPT_SISTEMA`; `src/grafo.py`: `nodo_llm` | Normal: GS-28, GS-30. Adversarial: GS-27 (orden en la glosa), GS-29 (falsa autorización), jailbreak por chat | `corrida_3_grupo_E.md`: 4 de 4, sin aprobación indebida; en GS-29 no obedece la falsa autorización y rechaza en P07. En la corrida 2, GS-29 falló por clasificación, no por seguridad. `prueba_dirigida_indice_v16.md`: el jailbreak por chat no declara ninguna decisión | 🔴 La sección 5 del notebook está vacía, con un `TODO`: debe mostrar GS-27 a GS-30 y el jailbreak por chat (Matías). El mecanismo ya está probado con Gemini |

## Bonos declarados

| Criterio | Puntos | Mecanismo | Dónde se ejecuta | Casos | Evidencia | Estado y qué falta |
|---|---:|---|---|---|---|---|
| Memoria avanzada (fondo por rendir) | +1,0 | El saldo se descuenta al aprobar y se usa en la decisión siguiente | Sección 7; `src/memoria.py`: `revisar_saldo`, `anexar_revision_saldo`, `aplicar_veredicto`; `src/grafo.py`: `nodo_cerrar` | Normal: GS-26. Adversarial: GS-25 (supera el saldo); FR-999 con LLM falso | `corrida_3_grupo_D.md`: 2 de 2 | ✅ |
| RAG (Redis, índice `grupo05_v15`) | +1,0 | Busca en la política, cita la fuente y no busca cuando no hace falta. 20 documentos (P01-P10 y RG-01-RG-10), configuración explícita (3.072, COSINE, FLAT) y un error de Redis vuelve al LLM sin cortar el turno | Sección 6; `src/rag.py`: `buscar_politica`; `scripts/cargar_indice.py`; `src/grafo.py`: `ToolNode` | Normal: GS-07, GS-33. Una regla como documento propio: GS-23, GS-34. No busca: GS-31, GS-26 turno 2 | `corrida_3.md`: rag 28 de 28, 107 fragmentos con fuente y puntaje, 12 casos con un fragmento RG. Carga e inventario del 2026-11-03 en `README.md` | 🔴 La sección 6 del notebook está vacía, con un `TODO`: debe mostrar la decisión de buscar y de no buscar, la configuración del índice y los fragmentos (Matías y Eduardo). El índice ya tiene la política v1.6 |
| Acción avanzada (registro SQLite) | +0,5 | El grafo registra el veredicto, con estado antes y después; el LLM no tiene esa herramienta | Sección 8; `src/registro.py`: `registrar_veredicto`, `leer_registro`, `reiniciar_registro`; `src/grafo.py`: `nodo_cerrar` | Normal: GS-26. Adversarial: GS-27, GS-29, GS-30 | `corrida_3_grupo_D.md`, `corrida_3_grupo_E.md`. Reinicio: `pruebas/probar_herramientas.py`, sección C, con base temporal | 🟡 Falta restaurar en la sección 8 la demostración del reinicio seguro (Matías) |
| Golden set | +0,5 | Casos con su respuesta correcta y un evaluador que los compara | Sección 10; `pruebas/golden_set.json`; `pruebas/evaluar.py`: `evaluar`, `mostrar_tabla` | 34 casos: normales, mal clasificados y adversariales | `corrida_3.md`: **34 de 34**, la corrida final, completa y sin fallas técnicas. `evolucion.md`: comparación con las corridas 1 y 2 | ✅ Versionado (v1.3) y ejecutado completo con el código final, sin fallos sin resolver |
| Juez LLM | +0,5 | Un segundo LLM revisa el veredicto con la validación como evidencia, y sin su visto bueno no se aprueba | Sección 9; `src/seguridad.py`: `juzgar_con_validacion`, `PROMPT_JUEZ`; `src/grafo.py`: `nodo_cerrar` | Benigno: GS-01. Con antes y después: GS-01, GS-26. Sin frenar un error: GS-10 | `evolucion.md`, `prueba_dirigida_PR17.md`, `corrida_3.md` (0 turnos sin juez). `prueba_dirigida_PR41_general.md`: la razón del juez en cada dictamen, también cuando valida una aprobación (GS-01, GS-03), una observación (GS-07, GS-10) y el rechazo de GS-29; útil para la sección 9 | 🔴 La sección 9 del notebook está vacía, con un `TODO`. Debe mostrar modelo, prompt, un veredicto benigno, uno adversarial y la decisión aplicada (Matías y Eduardo). En la corrida 2 no frenó la reclasificación indebida de GS-29; con el PR #41 la exige coherente con «Cuándo usarla» y «Cuándo NO usarla», y GS-29 pasa en la corrida 3 |
| Guardrail "piso de reglas" | +0,5 | Código sin LLM: si el LLM propone algo más permisivo que las reglas, se corrige; si altera el gasto, se valida el original y se anota qué cambió. Es un mecanismo distinto del juez LLM | Sin sección en el notebook; `src/grafo.py`: `nodo_cerrar`, `_estado_con_gasto_original`; `src/herramientas.py`: `decision_sugerida`, `campos_alterados`; `pruebas/probar_herramientas.py`: `prueba_piso_en_agente` | Benigno: GS-01, con LLM simulado. Normal: GS-16, el LLM se equivoca y el piso lo corrige. Adversarial: GS-27, el LLM altera la fecha y propone aprobar, con LLM simulado | `pruebas/probar_herramientas.py`, secciones E, G y H | 🟡 La sección H demuestra los tres casos en el grafo real, y falla si se rompe el guardrail. Falta una sección del notebook que use `prueba_piso_en_agente()` completa, diga que el LLM es simulado y por qué, y sume un caso benigno real con Gemini. En las corridas 1, 2 y 3 no se activó (Matías y Sebastián) |

## Requisito general

| Criterio | Puntos | Mecanismo | Dónde se ejecuta | Evidencia | Estado y qué falta |
|---|---:|---|---|---|---|
| Notebook ejecutable de arriba abajo | Base de la entrega | Todas las secciones corren en orden, con Gemini y Redis | `agente.ipynb` | Ninguna guardada | 🔴 Las secciones 5, 6 y 9 están vacías, y no hay una ejecución completa registrada |

## Bonos no declarados

- **Workflow adicional:** no se usó. El caso se resuelve con un solo ciclo ReAct y un cierre determinista.
- **MCP:** no se usó. Las herramientas son funciones locales del mismo proyecto, sin un servicio externo que conectar.

## Orden de cierre

Cada paso usa el resultado del anterior; si un paso cambia `src/`, se repite desde la corrida.

1. ✅ **Arreglo de GS-29** (Eduardo, PR #41): un solo cambio en `PROMPT_SISTEMA` y `PROMPT_JUEZ`, solo con
   reglas generales.
2. ✅ **Corrida 3** (Alex): 34 de 34 con el código final (`f050ad7`). **Desde aquí no se cambia `src/`.**
3. **Secciones del notebook** (Matías, con Eduardo y Sebastián): 5, 6, 8, 9 y la del guardrail, ejecutadas
   con el código final.
4. **Ejecución completa** del notebook de arriba abajo, desde cero, y `agente_ejecutado.ipynb` revisado
   para que no tenga secretos.
5. **README, esta matriz y los registros de prompts** de los 4, con la evidencia de la corrida 3.

## Lista de cierre antes de entregar

- [x] Actualizar en el README los límites conocidos que ya se hayan resuelto (con la corrida 3).
- [x] Actualizar esta matriz con la evidencia de la corrida final (corrida 3).
- [x] Confirmar que el índice tiene la política v1.6 (`grupo05_v15`, comprobado el 2026-11-03).
- [ ] Ejecutar el notebook completo de arriba abajo, desde cero.
- [ ] Revisar que los prompts de desarrollo de los 4 estén completos.
- [ ] Entregar `agente.ipynb` limpio y `agente_ejecutado.ipynb` con salidas, revisado para que no
  tenga secretos (sacarlo del `.gitignore` al final).
