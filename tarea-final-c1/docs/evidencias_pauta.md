# Matriz de evidencias de la pauta

Dónde se demuestra cada criterio y cada bono declarado. Estado al 2026-11-02, sobre `main` en la
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

La corrida 1 midió 33 casos con el código previo al PR #27: GS-34 aún no tiene resultados. Los casos
del grupo A, salvo los repetidos, corrieron antes de la política v1.3.

## Criterios base

| Criterio | Puntos | Mecanismo | Dónde se ejecuta | Casos | Evidencia | Estado y qué falta |
|---|---:|---|---|---|---|---|
| Caso y criterio de éxito | 0,5 | Define el problema, el usuario, el alcance y cómo se comprueba | Notebook, sección 1; [`caso_y_criterio.md`](caso_y_criterio.md) | Ejemplo: GS-07 | `docs/caso_y_criterio.md` | ✅ Queda listo al unir este trabajo |
| LLM y trazabilidad | 0,5 | Usa Gemini real y anota cada paso del agente | Secciones 0, 2 y 3; `src/config.py`: `obtener_llm`, `registrar_traza`; `src/grafo.py`: `nodo_llm` | Normal: GS-01 | `corrida_1_linea_base.json` (modelo, commit y herramientas por turno) | 🟡 Gemini real está demostrado. Falta ver las trazas en el notebook, porque el evaluador las apaga. `registrar_traza` sigue marcada como stub en `src/config.py:45` (Matías) |
| ReAct y condición de parada | 1,0 | El LLM pide una herramienta, lee la observación y decide; se detiene al llegar al máximo de pasos | Sección 3; `src/grafo.py`: `construir_agente`, `nodo_llm`, `nodo_ejecutar_herramientas`, `elegir_siguiente`, `nodo_parada` | Normal: GS-01, GS-07. Adversarial: GS-10 agotó los pasos | `corrida_1_linea_base.md`: 29 turnos validan y emiten veredicto. `estabilidad_v1_4.md`: parada real en GS-10, ronda 3 | ✅ La parada real se vio con el límite anterior de 6 pasos. El límite de 10 solo se probó con un LLM falso (`verificar.py`, bloque 6) |
| Historial | 0,5 | Cada hilo conserva la conversación y el segundo turno usa lo anterior | Sección 4; `src/grafo.py`: `InMemorySaver`, `conversar` | Normal: GS-32. También GS-26, turno 2 | `corrida_1_grupo_F.md`, `corrida_1_grupo_D.md` | ✅ |
| Seguridad básica | 0,5 | El prompt limita el alcance; los datos del gasto no son instrucciones; una aprobación sin veredicto válido se reemplaza | Sección 5; `src/seguridad.py`: `PROMPT_SISTEMA`; `src/grafo.py`: `nodo_llm` | Normal: GS-28, GS-30. Adversarial: GS-27 (orden en la glosa), GS-29 (falsa autorización) | `corrida_1_grupo_E.md`: 3 de 4, sin aprobación indebida. `estabilidad_v1_4.md`: GS-29 3 de 3 | 🔴 La sección 5 del notebook está vacía, con un `TODO`: debe mostrar GS-27 a GS-30 y un jailbreak por chat (Matías). Falta impedir que el agente escriba una decisión en un turno sin gasto (Eduardo) |

## Bonos declarados

| Criterio | Puntos | Mecanismo | Dónde se ejecuta | Casos | Evidencia | Estado y qué falta |
|---|---:|---|---|---|---|---|
| Memoria avanzada (fondo por rendir) | +1,0 | El saldo se descuenta al aprobar y se usa en la decisión siguiente | Sección 7; `src/memoria.py`: `revisar_saldo`, `anexar_revision_saldo`, `aplicar_veredicto`; `src/grafo.py`: `nodo_cerrar` | Normal: GS-26. Adversarial: GS-25 (supera el saldo); FR-999 con LLM falso | `corrida_1_grupo_D.md`: 2 de 2 | ✅ |
| RAG (Redis, índice `grupo05`) | +1,0 | Busca en la política, cita la fuente y no busca cuando no hace falta | Sección 6; `src/rag.py`: `buscar_politica`; `scripts/cargar_indice.py` | Normal: GS-07, GS-33. No busca: GS-31, GS-26 turno 2 | `corrida_1_linea_base.md`: 108 fragmentos con fuente y puntaje | 🔴 La sección 6 del notebook está vacía, con un `TODO`: debe mostrar la decisión de buscar y de no buscar, la configuración del índice y los fragmentos (Matías y Eduardo). Eduardo debe poner las reglas como documentos propios, fijar y documentar la configuración, corregir el prefijo doble y evitar que un error corte el turno. El índice sigue en v1.4: falta una recarga coordinada |
| Acción avanzada (registro SQLite) | +0,5 | El grafo registra el veredicto, con estado antes y después; el LLM no tiene esa herramienta | Sección 8; `src/registro.py`: `registrar_veredicto`, `leer_registro`, `reiniciar_registro`; `src/grafo.py`: `nodo_cerrar` | Normal: GS-26. Adversarial: GS-27, GS-29, GS-30 | `corrida_1_grupo_D.md`, `corrida_1_grupo_E.md`. Reinicio: `pruebas/probar_herramientas.py`, sección C, con base temporal | 🟡 Falta restaurar en la sección 8 la demostración del reinicio seguro (Matías) |
| Golden set | +0,5 | Casos con su respuesta correcta y un evaluador que los compara | Sección 10; `pruebas/golden_set.json`; `pruebas/evaluar.py`: `evaluar`, `mostrar_tabla` | 34 casos: normales, mal clasificados y adversariales | `corrida_1_linea_base.md`: 31 de 33. `evolucion.md`, `estabilidad_v1_4.md` | 🟡 Está versionado (v1.3) y completo. Falta ejecutarlo completo con los 34 casos, después de la recarga |
| Juez LLM | +0,5 | Un segundo LLM revisa el veredicto con la validación como evidencia, y sin su visto bueno no se aprueba | Sección 9; `src/seguridad.py`: `juzgar_con_validacion`, `PROMPT_JUEZ`; `src/grafo.py`: `nodo_cerrar` | Benigno: GS-01. Con antes y después: GS-01, GS-26. Sin frenar un error: GS-10 | `evolucion.md`, `prueba_dirigida_PR17.md` | 🔴 La sección 9 del notebook está vacía, con un `TODO`. Debe mostrar modelo, prompt, un veredicto benigno, uno adversarial y la decisión aplicada (Matías y Eduardo). En la corrida 1 no frenó la aprobación indebida de GS-10 |
| Guardrail "piso de reglas" | +0,5 | Código sin LLM: si el LLM propone algo más permisivo que las reglas, se corrige; si altera el gasto, se valida el original y se anota qué cambió. Es un mecanismo distinto del juez LLM | Sin sección en el notebook; `src/grafo.py`: `nodo_cerrar`, `_estado_con_gasto_original`; `src/herramientas.py`: `decision_sugerida`, `campos_alterados` | Benigno: GS-01. Adversarial: GS-16 con la fecha alterada, con un LLM simulado | `pruebas/probar_herramientas.py`, secciones E y G | 🔴 Falta una sección del notebook con un caso benigno real y uno adversarial, su veredicto y la decisión aplicada. El adversarial puede usar un LLM simulado, si la sección lo dice y explica por qué: Gemini no se equivoca a pedido. En la corrida 1 no se activó, y no hay evidencia guardada de `campos_alterados` (Matías y Sebastián) |

## Requisito general

| Criterio | Puntos | Mecanismo | Dónde se ejecuta | Evidencia | Estado y qué falta |
|---|---:|---|---|---|---|
| Notebook ejecutable de arriba abajo | Base de la entrega | Todas las secciones corren en orden, con Gemini y Redis | `agente.ipynb` | Ninguna guardada | 🔴 Las secciones 5, 6 y 9 están vacías, y no hay una ejecución completa registrada |

## Bonos no declarados

- **Workflow adicional:** no se usó. El caso se resuelve con un solo ciclo ReAct y un cierre determinista.
- **MCP:** no se usó. Las herramientas son funciones locales del mismo proyecto, sin un servicio externo que conectar.

## Lista de cierre antes de entregar

- [ ] Actualizar en el README los límites conocidos que ya se hayan resuelto.
- [ ] Actualizar esta matriz con la evidencia de la corrida final.
- [ ] Confirmar que el índice `grupo05` tiene la política v1.5.
- [ ] Ejecutar el notebook completo de arriba abajo, desde cero.
- [ ] Revisar que los prompts de desarrollo de los 4 estén completos.
