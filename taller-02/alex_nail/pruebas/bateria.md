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
| 1 | Primera conferencia de humor computacional | dentro | buscar → responder | 0,757 | Respondió | cita p.6, esperada p.6 ✓ verificada en el texto de la página | Bibliografía en el top-3: p.26 y p.25 (puestos 2 y 3). La respuesta repite el fragmento, sin inventar. |
| 2 | Tres teorías principales del humor | dentro | buscar → responder | 0,783 | Respondió | cita p.3 y p.4, esperada p.3 (detalle p.4) ✓ verificada en el texto de la página | Sin bibliografía. Junta dos páginas en una cita ("[… p.3, 4]"). Sin invenciones. |
| 3 | Por qué la incongruencia es la más usada | dentro | buscar → responder | 0,822 | Respondió | cita p.4, esperada p.4 ✓ verificada en el texto de la página | Sin bibliografía (p.4, p.2, p.1). Trae la razón completa. |
| 4 | K usado por Liu et al. (2018a) | dentro | buscar → responder | 0,789 | Respondió | cita p.19, esperada p.19 ✓ verificada en el texto de la página | Sin bibliografía: no apareció la entrada de la p.26. "Puns y one-liners" está literal en el fragmento. Escribe "$K=5$" en formato LaTeX. |
| 5 | Qué mide la entropía (Kao et al.) | dentro | buscar → responder | 0,743 | Respondió | cita p.15 y p.16, esperada p.15 y p.16 ✓ verificada en el texto de la página | Sin bibliografía. Usa las dos páginas; "equilibradas" está literal en el fragmento de la p.15. |
| 6 | Precio del bitcoin | fuera | buscar → no_se | 0,573 | no_se | — (no cita) | Bibliografía (p.29) en el top-3, pero bajo el umbral. |
| 7 | IVA de una factura en Chile | fuera | buscar → no_se | 0,559 | no_se | — (no cita) | Sin bibliografía. |
| 8 | Último Mundial de fútbol | fuera | buscar → no_se | 0,548 | no_se | — (no cita) | Bibliografía (p.29) en el top-3, pero bajo el umbral. |
| 9 | BERT o GPT en español | ambigua | buscar → responder | 0,749 | Respondió que el contexto no alcanza | cita p.24, esperada "roza p.21 y p.22" ✗ (esas páginas no entraron al top-3); lo que afirma la respuesta ("supremacía de los transformers", "mecanismo de atención") ✓ verificado en el texto de la p.24 | Sin bibliografía. Dice "el contexto no menciona ni a BERT ni a GPT", que es cierto para lo que recibió (p.16, p.24, p.1). El PDF sí los nombra en la p.22, pero ese fragmento no entró al top-3. |
| 10| Porcentaje de acierto de los transformers | ambigua | buscar → responder | 0,803 | Respondió que no hay cifras | cita p.22 y p.24, esperada "roza p.24" ✓ verificada en el texto de la página (las dos hablan de transformers y ninguna da porcentajes; la p.24 dice "insuperables") | Sin bibliografía. Dice correctamente que no hay porcentaje; cita páginas para una afirmación negativa. |
| S | (sinónimos) Primer congreso de humor por computadora | dentro | buscar → responder | 0,737 | Respondió | cita p.6, esperada p.6 ✓ verificada en el texto de la página | Bibliografía (p.26) en los puestos 2 y 3. Funciona con sinónimos, pero es el parecido más bajo de las "dentro". |
| F | (palabras del PDF) Índice HNSW con KNN en Redis | fuera | buscar → no_se | 0,648 | no_se | — (no cita) | Bibliografía (p.29) en el puesto 1. Quedó a 0,002 del umbral: casi un falso positivo. |

Capturas: `capturas/etapa4_q01.txt` … `etapa4_q10.txt`, `etapa4_qS.txt` y `etapa4_qF.txt`.

**Falsos positivos** (una "fuera" que respondió): ninguno con UMBRAL = 0,65. Pero la F (HNSW, KNN y Redis) quedó en 0,648, solo 0,002 bajo el umbral: comparte palabras con el PDF ("KNN", "vectores") y casi pasa.
**Falsos negativos** (una "dentro" que fue a no_se): ninguno. La "dentro" más baja es la S (sinónimos), con 0,737, 0,087 sobre el umbral.

### Lectura de los datos

Las 12 preguntas ordenadas por mejor parecido (valores exactos, sin redondear):

| Mejor parecido | # | Tipo |
|---|---|---|
| 0,82186 | 3 | dentro |
| 0,80342 | 10 | ambigua |
| 0,78877 | 4 | dentro |
| 0,78274 | 2 | dentro |
| 0,75679 | 1 | dentro |
| 0,74908 | 9 | ambigua |
| 0,74332 | 5 | dentro |
| **0,73694** | **S** | **dentro ← la más baja de las "dentro"** |
| **0,64754** | **F** | **fuera ← la más alta de las "fuera"** |
| 0,57288 | 6 | fuera |
| 0,55887 | 7 | fuera |
| 0,54833 | 8 | fuera |

- **Rango sin falsos positivos ni falsos negativos:** 0,64754 < UMBRAL ≤ 0,73694. Sí existe, y tiene un ancho de ~0,089.
- El UMBRAL actual (0,65) está dentro del rango, pero pegado a su borde inferior: le saca solo 0,002 a la F.
- **Ambiguas, aparte:** la 9 (0,749) y la 10 (0,803) quedan sobre todo el rango, así que con cualquier umbral de ese rango van a `responder`. En las dos el modelo dijo que el contexto no alcanzaba, en vez de inventar (regla 3 del prompt). El umbral no las filtra; las contiene el prompt.
- Son 12 preguntas: el rango sirve como referencia, no como garantía.

## TOP_K: las 5 "dentro" con 1, 3 y 5

| # | TOP_K=1: ¿respuesta completa? / cita | TOP_K=3 | TOP_K=5 |
|---|---|---|---|
| 1 | Completa · cita p.6 · sin ruido | Completa · cita p.6 · ruido: bibliografía p.26 y p.25 (no afectó la respuesta) | Completa · cita p.6 · ruido: 4 de 5 son bibliografía (p.25, 26, 26, 28) |
| 2 | **Incompleta** · cita p.4 · el único fragmento habla de "tres teorías clásicas" pero no las nombra; el modelo dijo que no podía responder | Completa · cita p.3 y p.4 · sin ruido | Completa · cita p.3 · sin ruido (todo de p.2 a p.4) |
| 3 | Completa · cita p.4 · sin ruido | Completa · cita p.4 · sin ruido | Completa · cita p.4 · ruido de otro tema: transformers (p.24) y rasgos latentes (p.23), no afectó la respuesta |
| 4 | Completa · cita p.19 · sin ruido | Completa · cita p.19 · ruido leve: otro trabajo de Liu et al. (2018b, p.20) | Completa · cita p.19 · ruido: bibliografía p.28 y p.29 |
| 5 | **Parcial** · cita p.15 · solo "incertidumbre entre varias interpretaciones"; no trae la p.16 ("cuanto más alta sea la entropía, más ambigua será la frase") | Completa · cita p.15 y p.16 · une las dos páginas | Completa · cita p.15 y p.16 · ruido de otro tema: rendimiento del modelo bayesiano (p.17) y árboles de decisión (p.18) |

Capturas: TOP_K=3 en `capturas/etapa4_q01.txt` … `etapa4_q05.txt`; TOP_K=1 en `capturas/etapa4_topk1_q01.txt` …; TOP_K=5 en `capturas/etapa4_topk5_q01.txt` …

UMBRAL elegido: 0,68   TOP_K elegido: 3   Por qué:

UMBRAL 0,68: las "dentro" sacaron entre 0,737 y 0,822 y las "fuera" entre 0,548 y 0,648, así que cualquier valor entre 0,648 y 0,737 separa sin errores. El 0,65 original quedaba a 0,002 de la pregunta F. Elegí 0,68 para tener margen hacia los dos lados sin perder "¿De qué trata el documento?" (0,699).

TOP_K 3: con 1, la pregunta 2 no nombró las tres teorías y la 5 perdió la mitad de la respuesta (estaba en la p. 16). Con 5 no se pierde nada, pero entra mucha bibliografía (4 de 5 en la pregunta 1). Con 3, las cinco respuestas salen completas y con menos ruido.
