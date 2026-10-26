# Etapa 2 · Embeddings: predice antes de medir

## 1. Mis tres frases (las escribo yo)

Condiciones: dos frases que digan **lo mismo con palabras distintas** (que casi no compartan palabras) y una de **otro tema**. De mi dominio de trabajo.

- Frase 1: ____
- Frase 2 (lo mismo que la 1, con otras palabras): ____
- Frase 3 (otro tema): ____

## 2. Mi predicción (antes de correr nada)

- Par más parecido: ____
- Parecido que espero para ese par: ____
- Parecido que espero para los pares con la frase 3: ____

Dato que ya conozco de la demo del Prompt 2: con este modelo, incluso frases sin relación dan cerca de 0,75 (router ↔ pan amasado = 0,788). Lo que importa es la **diferencia** entre pares, no el número solo.

## 3. Resultado real

Comando:
```
python scripts/demo_embeddings.py "frase 1" "frase 2" "frase 3"
```

| Par | Parecido |
|---|---|
|  |  |
|  |  |
|  |  |

¿Acerté?: ____

**Conclusión (2 líneas):** ____

## 4. Prueba: mismas palabras, sentido distinto

Comando (la tercera frase dice lo mismo que la primera, sin repetir "banco"):
```
python scripts/demo_embeddings.py "El banco cerró temprano hoy" "Me senté en el banco de la plaza" "La sucursal bancaria ya no atiende"
```

Qué esperar: si el parecido es de **significado**, "banco cerró" ↔ "sucursal no atiende" debería salir más alto que "banco cerró" ↔ "banco de la plaza", aunque este último par comparta la palabra. Si no pasa, también es un hallazgo válido: hay que anotarlo.

| Par | Parecido |
|---|---|
| "El banco cerró temprano hoy" ↔ "La sucursal bancaria ya no atiende" | 0,8646 (más parecido) |
| "El banco cerró temprano hoy" ↔ "Me senté en el banco de la plaza" | 0,8081 |
| "Me senté en el banco de la plaza" ↔ "La sucursal bancaria ya no atiende" | 0,7725 |

Captura: `capturas/etapa2_banco.txt`.

Conclusión: ____

## 5. Índice vectorial vs coseno a mano (ya medido)

Evidencia en `capturas/indice_vs_coseno_redis.txt` y `capturas/indice_vs_coseno_faiss.txt`. Mediana de 5 preguntas. El top-3 de A y de B coincidió en las 25 búsquedas.

**Redis (servidor remoto del curso)**

| n | A: coseno a mano | B: índice | Vectores que viajaron (A / B) |
|---|---|---|---|
| 200 | 565 ms | 136 ms | 200 / 3 |
| 2000 | 2215 ms | 141 ms | 2000 / 3 |

**FAISS (local, índice plano)**

| n | A: numpy | B: FAISS |
|---|---|---|
| 200 | 0,04 ms | 0,13 ms |
| 2000 | 0,74 ms | 1,59 ms |
| 20000 | 18,6 ms | 76,2 ms |

Nota: por la cuota diaria de Gemini, en n = 2000 hay 900 vectores reales y 1100 simulados (copias con un pequeño ruido). Los tiempos no cambian, porque el cálculo cuesta lo mismo con vectores reales o simulados.

**Mi regla (una línea, ajústala con tus palabras):** si los vectores están en un servidor remoto, siempre el índice, porque A tiene que bajarlos todos por la red en cada pregunta (16 veces más lento con 2000). El coseno a mano solo sirve para entender el cálculo o para pocos vectores que ya están en memoria. Con un índice FAISS plano, numpy incluso gana, y la ventaja del índice aparece con índices aproximados (HNSW) y muchos datos.
