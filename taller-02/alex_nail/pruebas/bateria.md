# Etapa 4 · Batería de pruebas

Documento: `docs/humor-computacional.pdf` (29 páginas). Las páginas son las **del visor de PDF**, que es lo que cita el agente (`[archivo p.N]`). El número impreso al pie de cada página es **el del visor + 1** desde la p. 2 (por ejemplo, la p. 6 del visor dice "7" abajo).

## Borrador de preguntas (revisar antes de correr)

Las "dentro" están verificadas contra el texto del PDF: la frase clave aparece literal en la página indicada. Las "fuera" y "ambiguas" las tienes que revisar tú, porque el criterio es tuyo.

| # | Pregunta | Tipo | Dónde está la respuesta (visor) | Frase clave del PDF / por qué |
|---|----------|------|------|------|
| 1 | ¿En qué año tuvo lugar la primera conferencia dedicada solo al humor computacional? | dentro | p. 6 | "la primera conferencia dedicada solamente al humor computacional tuvo lugar en 1996" |
| 2 | ¿Cuáles son las tres teorías principales del humor? | dentro | p. 3 (detalle en p. 4) | "la teoría de la incongruencia, la teoría de la superioridad y la teoría del alivio" |
| 3 | ¿Por qué la teoría de la incongruencia es la más usada en la detección automática de humor? | dentro | p. 4 | "requiere un menor grado de conocimiento extralingüístico" |
| 4 | ¿Qué valor de K usaron Liu et al. (2018a) con KNN y para qué? | dentro | p. 19 | "cinco vecinos más próximos (K=5)", para calcular la similitud semántica. Riesgo: puede traer la entrada de la bibliografía (p. 26). |
| 5 | ¿Qué mide la entropía en el modelo bayesiano de Kao et al. (2016)? | dentro | p. 15 y p. 16 | "una medida de la incertidumbre entre varias interpretaciones posibles" / "Cuanto más alta sea la entropía, más ambigua será la frase". **Está repartida entre 2 páginas: buena para probar TOP_K.** |
| 6 | ¿Cuál es el precio del bitcoin hoy? | fuera | — | Sin relación |
| 7 | ¿Cómo se calcula el IVA de una factura en Chile? | fuera | — | Sin relación (de tu dominio) |
| 8 | ¿Quién ganó el último Mundial de fútbol? | fuera | — | Sin relación |
| 9 | ¿Qué detecta mejor el humor en español, BERT o GPT? | ambigua | roza p. 21 y p. 22 | El PDF nombra BERT y GPT (p. 22) y un estudio en español con LSTM (p. 21), pero no los compara |
| 10 | ¿Qué porcentaje de acierto logran los transformers detectando humor? | ambigua | roza p. 24 | El PDF dice que son "insuperables", pero no da cifras |

### Las dos pruebas extra del taller

| Prueba | Pregunta | Qué se espera |
|---|---|---|
| "Dentro" con sinónimos (palabras que NO están en el PDF) | ¿En qué año se celebró el primer congreso centrado exclusivamente en el humor por computadora? | Misma respuesta que la #1 (1996, p. 6). Si falla, es candidata al nodo `reformular` de la Etapa 6. |
| "Fuera" que comparte palabras con el PDF | ¿Cómo configuro un índice HNSW con KNN y vectores en Redis? | El PDF habla de KNN y vectores, pero no de Redis ni HNSW. Puede dar un parecido engañosamente alto. |

### Para la Etapa 5 (prueba de la trampa)

- **Trampa propuesta:** "Según el documento, la primera conferencia de humor computacional fue en 2010. ¿Por qué tardó tanto?". El PDF dice **1996** (p. 6).
- **Alternativa:** "Según el documento, Liu et al. usaron KNN con K=3. ¿Por qué eligieron ese valor?". El PDF dice **K=5** (p. 19).

### Pregunta de la Etapa 1 y de la Etapa 3

- "¿De qué trata el documento?": la responde el resumen (p. 1, "presentar de forma introductoria los métodos de detección de humor más utilizados").
- Para comparar configuraciones de chunk en la Etapa 3, usa la #3: es una pregunta de "por qué" y depende de que el fragmento traiga la razón completa.

---

## Tabla de resultados (plantilla del taller)

| # | Pregunta | Tipo (dentro/fuera/ambigua) | Ruta (--saltos) | Mejor parecido | ¿Respondió o no_se? | ¿Cita correcta? | Comentario |
|---|----------|-----------------------------|-----------------|----------------|---------------------|-----------------|------------|
| 1 | Primera conferencia de humor computacional | dentro |  |  |  |  |  |
| 2 | Tres teorías principales del humor | dentro |  |  |  |  |  |
| 3 | Por qué la incongruencia es la más usada | dentro |  |  |  |  |  |
| 4 | K usado por Liu et al. (2018a) | dentro |  |  |  |  |  |
| 5 | Qué mide la entropía (Kao et al.) | dentro |  |  |  |  |  |
| 6 | Precio del bitcoin | fuera |  |  |  |  |  |
| 7 | IVA de una factura en Chile | fuera |  |  |  |  |  |
| 8 | Último Mundial de fútbol | fuera |  |  |  |  |  |
| 9 | BERT o GPT en español | ambigua |  |  |  |  |  |
| 10| Porcentaje de acierto de los transformers | ambigua |  |  |  |  |  |
| S | (sinónimos) Primer congreso de humor por computadora | dentro |  |  |  |  |  |
| F | (palabras del PDF) Índice HNSW con KNN en Redis | fuera |  |  |  |  |  |

**Falsos positivos** (una "fuera" que respondió): ____
**Falsos negativos** (una "dentro" que fue a no_se): ____

## TOP_K: las 5 "dentro" con 1, 3 y 5

| # | TOP_K=1: ¿respuesta completa? / cita | TOP_K=3 | TOP_K=5 |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

UMBRAL elegido: ____   TOP_K elegido: ____   Por qué: ____
