# Evolución del agente

Antes y después de cada mejora, con fecha, commit y causa. Todos los datos son ficticios.

## 1. El juez recibe la validación (PR #17)

**Qué cambió:** el cierre del agente pasó de `juzgar()` a `juzgar_con_validacion()`. Antes, el juez
auditaba el veredicto sin ver el resultado de `validar_gasto`, y por eso bloqueaba aprobaciones
correctas. Ahora recibe esa evidencia.

| Caso | Antes (2026-11-01) | Después (2026-11-02) |
|---|---|---|
| GS-01 | ❌ `observar` en commit `dbf3677` | ✅ `aprobar` en commit `7e3c5c1` |
| GS-26, turno 1 | ❌ `observar` en commit `b7b1ff0` | ✅ `aprobar` en commit `7e3c5c1` |
| GS-26, turno 2 | ❌ `aprobar`, sin RG-08 | ✅ `observar`, citando RG-08 |

**Causa del "antes":** en ambos casos, `validar_gasto` no encontró incumplimientos y el LLM propuso
aprobar. El juez, sin ver esa validación, bloqueó la aprobación.

- **GS-01.** El juez respondió: *"El veredicto de aprobación no está justificado ya que no se incluyó
  la salida de validar_gasto para confirmar el cumplimiento determinista"*.
- **GS-26.** El juez respondió que *"no se verificó adecuadamente si la cuenta CTA-6901 y la
  clasificación en P02 son correctas"*, justo lo que `validar_gasto` ya había confirmado. Al quedar
  en observar, el turno 1 no descontó el fondo. Por eso, en el turno 2 el saldo alcanzaba y RG-08 no
  se aplicó: esa segunda falla fue consecuencia de la primera.

**Evidencia del "después":** [`prueba_dirigida_PR17.md`](prueba_dirigida_PR17.md) y
[`prueba_dirigida_PR17.json`](prueba_dirigida_PR17.json), con Gemini real: 6 de 7 casos, sin 429 y
sin turnos sin juez. El caso que falla, GS-07, es un error de clasificación sin relación con el juez.

**Cómo se midió y qué tan lejos llega esta evidencia:**

- Fue una prueba dirigida, una vez por caso, con `gemini-3.5-flash-lite`. Gemini puede variar entre
  corridas, así que esto muestra el efecto en estos casos, no que nunca vuelvan a fallar.
- Las pruebas del "antes" corrieron sobre el código de esos commits, con un solo ajuste temporal:
  `enviar_turno` usaba `conversar_con_caso`, porque el evaluador aún no lo hacía. Sus archivos eran
  temporales y no se conservaron: las frases del juez vienen del registro de esa revisión.
- La misma comparación no se repite en la corrida 1, porque la línea base se hizo después del PR #17.
- El 2026-11-01, una copia con el cierre ya conectado a `juzgar_con_validacion` hizo pasar GS-01.

## 2. P08 distingue Coffee break de Capacitaciones (política v1.3)

**Qué cambió:** P08 decía "Coffee break de una reunión o capacitación", aunque `Capacitaciones` es una
categoría aparte. La v1.3 define las dos, agrega un tope para `Capacitaciones` y se recargó el índice.
El caso del golden set no se modificó.

| Caso | Antes (política v1.2) | Después (política v1.3) |
|---|---|---|
| GS-03 | ❌ `observar` y `Coffee break`, en commit `d97b3a5` | ✅ `aprobar` y `Capacitaciones`, en commit `8949700` |

**Causa del "antes":** el agente movió a `Coffee break` un gasto declarado en `Capacitaciones`, y esa
lectura era defendible con el texto antiguo.

**Evidencia:** [`corrida_1_grupo_A.md`](corrida_1_grupo_A.md) y
[`corrida_1_repeticion_GS-03_GS-06.md`](corrida_1_repeticion_GS-03_GS-06.md), una vez cada una.
