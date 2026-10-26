# Bonus · La misma batería en Redis y en FAISS

Configuración: 800/120, TOP_K 3, UMBRAL 0,68, agente actual (con el nodo `reformular`). Los dos índices tienen los mismos 96 fragmentos con los mismos embeddings (salieron de la caché). Redis es el servidor compartido del curso; FAISS es local, en `data/AlexNail/`.

Capturas: `capturas/bonus_redis_qNN.txt` y `capturas/bonus_faiss_qNN.txt` (q01 … q10, qS, qF), `capturas/ingesta_800_120_faiss.txt` y `capturas/bonus_tiempos.txt`.

> **Nota importante:** la batería de la Etapa 4 se corrió sin `reformular`. Aquí las dos bases usan el agente actual, así que cada pregunta pasa primero por `reformular`, que llama al modelo y no siempre reescribe igual. En 3 de las 12 preguntas (1, 2 y F) la reescritura fue idéntica en las dos corridas, y ahí el resultado fue **idéntico** (mismo top-3, mismos parecidos). En las otras 9 la reescritura cambió entre corridas, y las diferencias de esas filas se deben a eso, no a la base. Van marcadas con ⚠.

## Resultados por pregunta

| # | Tipo | Pregunta reescrita · Redis | Pregunta reescrita · FAISS | Mejor parecido R / F | Ruta R / F | ¿Mismo top-3? | Página citada R / F |
|---|---|---|---|---|---|---|---|
| 1 | dentro | Año de celebración de la primera conferencia dedicada exclusivamente al humor computacional | (idéntica) | 0,775 / 0,775 | responder / responder | Sí: p.6, p.26, p.25 con los mismos parecidos | p.6 / p.6 |
| 2 | dentro | Tres teorías principales del humor | (idéntica) | 0,795 / 0,795 | responder / responder | Sí: p.4, p.3, p.4 con los mismos parecidos | p.3 / p.3 |
| 3 | dentro | factores de uso de la teoría de la incongruencia en detección automática de humor | fundamentos teóricos de la teoría de la incongruencia en sistemas de detección automática de humor | 0,804 / 0,829 | responder / responder | No ⚠: R p.2, p.4, p.23 · F p.4, p.2, p.1 | p.4 / p.4 |
| 4 | dentro | Valor de K y propósito de su uso en el algoritmo KNN por Liu et al. (2018a) | Valor del parámetro K y aplicación en el algoritmo KNN por Liu et al. (2018a) | 0,783 / 0,781 | responder / responder | Mismas páginas (p.19, p.19, p.20), parecidos levemente distintos ⚠ | p.19 / p.19 |
| 5 | dentro | Interpretación de la entropía en el modelo bayesiano de Kao et al. (2016) | Significado de la entropía en el modelo bayesiano de Kao et al. (2016) | 0,756 / 0,754 | responder / responder | Mismas páginas (p.15, p.16, p.17), parecidos levemente distintos ⚠ | p.15 y p.16 / p.15 y p.16 |
| 6 | fuera | Cotización actual del bitcoin | Cotización actual de bitcoin | 0,597 / 0,596 | no_se / no_se | No ⚠: el 3.º cambia (R p.11 · F p.15) | — / — |
| 7 | fuera | Metodología de cálculo del Impuesto al Valor Agregado (IVA) en facturación en Chile | Metodología de cálculo del Impuesto al Valor Agregado (IVA) en factura en Chile | 0,602 / 0,601 | no_se / no_se | Mismas páginas (p.2, p.9, p.7) ⚠ | — / — |
| 8 | fuera | Selección ganadora de la Copa Mundial de Fútbol de la FIFA vigente | Selección ganadora de la Copa Mundial de Fútbol FIFA | 0,559 / 0,572 | no_se / no_se | No ⚠: R p.22, p.15, p.9 · F p.15, p.22, p.29 | — / — |
| 9 | ambigua | Evaluación comparativa del rendimiento de BERT y GPT en la detección de humor en español | Comparación de rendimiento entre BERT y GPT en la detección de humor en español | 0,748 / 0,751 | responder / responder | No ⚠: el 3.º cambia (R p.26 · F p.16) | sin cita / sin cita (dice que no hay información) |
| 10 | ambigua | Tasa de precisión de los modelos transformer en la detección de humor | Rendimiento porcentual de precisión de los modelos transformers en la detección de humor | 0,789 / 0,766 | responder / responder | Mismas páginas (p.24, p.22, p.22) ⚠ | sin cita / sin cita (dice que no hay porcentaje) |
| S | dentro | Año de celebración del primer congreso especializado en humor por computadora | Año de celebración del primer congreso centrado exclusivamente en el humor por computadora | 0,762 / 0,758 | responder / responder | No ⚠: el 3.º cambia (R p.25 · F p.26) | p.6 / p.6 |
| F | fuera | Configuración de índice HNSW con búsqueda k-NN y vectores en Redis | (idéntica) | 0,652 / 0,652 | no_se / no_se | Sí: p.29, p.19, p.19 con los mismos parecidos | — / — |

R = Redis, F = FAISS. Los parecidos van a 3 decimales, como los muestra `--saltos`.

**Lectura:**
- Cuando la pregunta reescrita es la misma (1, 2 y F), Redis y FAISS dan exactamente el mismo top-3 y los mismos parecidos. Es lo mismo que se vio en la Etapa 3 con 400/50 y 1200/200.
- Todas las diferencias de la tabla aparecen solo cuando `reformular` reescribió distinto. Ninguna se explica por la base.
- La página citada coincide entre bases en las 6 preguntas que responden con cita (1 a 5 y S); la 9 y la 10 responden sin cita en las dos bases.

## Tiempos de búsqueda (`buscar_fragmentos()`, sin el modelo)

Mismo texto en las dos bases: las 12 preguntas reescritas de la corrida en Redis, con el embedding desde la caché. Mediana de 5 repeticiones por pregunta, en ms; la primera llamada de cada base va aparte como "arranque".

| | Redis | FAISS |
|---|---|---|
| Mediana de las 12 preguntas | 2621,7 ms | 85,3 ms |
| Rango por pregunta | 2571 – 2709 ms | 84 – 89 ms |
| Arranque (1.ª llamada) | 4131,4 ms | 136,4 ms |

**Desglose de dónde se va el tiempo** (también en `capturas/bonus_tiempos.txt`):

| Paso dentro de `buscar_fragmentos()` | Redis | FAISS |
|---|---|---|
| Contar documentos del índice (conexión nueva + `FT.INFO` / leer `index.faiss`) | 1107,2 ms | 0,2 ms |
| Abrir el store (conexión nueva + `RedisVectorStore` / cargar `data/AlexNail/` desde disco) | 1347,5 ms | 85,1 ms |
| Solo buscar, con el store ya abierto | 141,0 ms | 0,9 ms |

En Redis, ~94% del tiempo se va en abrir dos conexiones nuevas al servidor remoto en cada búsqueda. Así está escrito `buscar_fragmentos()`: no reutiliza la conexión. La búsqueda KNN en sí tarda ~141 ms, igual que en la Etapa 2 (`indice_vs_coseno_redis.txt`, ~140 ms). En FAISS, casi todo el tiempo es leer el índice desde disco; la búsqueda en memoria tarda menos de 1 ms.

## ¿Cambió alguna decisión del umbral?

**Con UMBRAL 0,68, ninguna pregunta cambia de ruta entre bases:** las 12 van al mismo lado (8 a `responder`, 4 a `no_se`).

Rango sin falsos positivos ni falsos negativos, recalculado para cada base (a 3 decimales):

| | Redis | FAISS | Etapa 4 (sin reformular, Redis) |
|---|---|---|---|
| "Dentro" más baja (incluida la S) | 0,756 (5) | 0,754 (5) | 0,737 (S) |
| "Fuera" más alta (incluida la F) | 0,652 (F) | 0,652 (F) | 0,648 (F) |
| Rango sin FP ni FN | 0,652 < UMBRAL ≤ 0,756 | 0,652 < UMBRAL ≤ 0,754 | 0,648 < UMBRAL ≤ 0,737 |
| ¿Está 0,68 dentro? | Sí | Sí | Sí |

- **Las dos bases dan prácticamente el mismo rango.** La diferencia del borde superior (0,756 contra 0,754) viene de que `reformular` reescribió distinto la pregunta 5, no de la base.
- **Comparado con la Etapa 4,** con `reformular` las "dentro" subieron (la más baja pasó de 0,737 a ~0,755) y la F subió poco (de 0,648 a 0,652). El rango quedó algo más ancho.
- **Ambiguas, aparte:** la 9 (0,748 / 0,751) y la 10 (0,789 / 0,766) siguen sobre 0,68 en las dos bases y van a `responder`. En ambas el modelo dijo que el contexto no alcanza, sin citar. La 9 queda dentro del rango sin errores. Un UMBRAL entre 0,749 y 0,751 la mandaría a `no_se` en Redis (0,748) y a `responder` en FAISS (0,751), por cómo `reformular` la reescribió en cada corrida, no por la base.

## Párrafo 1

____

## Párrafo 2

____
