# Etapa 3 · Chunk y solape

Documento: `docs/humor-computacional.pdf` (29 páginas). Antes de cortar, la ingesta limpia el texto: este PDF se extrae con cada palabra separada por saltos de línea y espacios, y la limpieza lo baja de 73.295 a 56.299 caracteres (−23%).

| Configuración | CHUNK_SIZE | CHUNK_OVERLAP | Páginas | Fragmentos | Tamaño promedio | Fragmentos 1 y 2 muestran solape (sí/no) |
|---------------|-----------|---------------|---------|------------|-----------------|-------------------------------------------|
| A             | 400       | 50            | 29      | 188        | 302             | No (misma página, pero la última oración del 1 mide ~100 caracteres y no cabe en 50) |
| B             | 1200      | 200           | 29      | 66         | 922             | Sí (repiten 176 caracteres)               |
| Referencia    | 800       | 120           | 29      | 96         | 614             | No (misma página, pero la última oración del 1 mide ~150 caracteres y no cabe en 120) |

| Configuración | Tamaño mínimo | Tamaño máximo | Fragmentos con menos de 100 caracteres | Pares de una misma página que comparten texto |
|---------------|---------------|---------------|----------------------------------------|-----------------------------------------------|
| A · 400/50    | 54            | 399           | 6                                      | 25 de 159 (16%)                               |
| B · 1200/200  | 54            | 1199          | 1                                      | 30 de 37 (81%)                                |
| 800/120       | 60            | 796           | 1                                      | 33 de 67 (49%)                                |

Capturas: `capturas/ingesta_400_50.txt`, `capturas/ingesta_1200_200.txt` y `capturas/ingesta_800_120.txt` (solo cortar, sin embeber).

**Hallazgo con 800/120:** el solape no es "los últimos 120 caracteres". El cortador repite solo **oraciones completas** que quepan en el solape, y por eso solo 33 de los 67 pares de una misma página comparten texto. Captura del par que sí lo muestra (fragmentos 10 y 11, p. 4): `capturas/ingesta_800_120.txt`.

## Misma pregunta con cada configuración

Pregunta: "¿Por qué la teoría de la incongruencia es la más usada en la detección automática de humor?" (respuesta en p. 4)

| Configuración | Ruta | Mejor parecido | Página citada | ¿La respuesta trae la razón completa? |
|---|---|---|---|---|
| A · 400/50 | buscar → responder | 0,782 | p. 4 | Sí ("requiere un menor grado de conocimiento extralingüístico") |
| B · 1200/200 | buscar → responder | 0,782 | p. 4 | Sí ("requiere un menor grado de conocimiento extralingüístico") |
| 800/120 | buscar → responder | 0,822 | p. 4 | Sí ("requiere un menor grado de conocimiento extralingüístico") |

Capturas: `capturas/etapa3_400_50.txt`, `capturas/etapa3_1200_200.txt` y `capturas/etapa3_800_120.txt`. Las tres configuraciones se midieron en Redis. Al final el índice quedó de nuevo en 800/120 (96 documentos).
Nota: A y B se repitieron en Redis después de la Etapa 5, así que sus respuestas usan el prompt nuevo (citas "(p. N)") y UMBRAL 0,68. La de 800/120 es de antes (prompt original, UMBRAL 0,65). Lo que recupera la búsqueda (ruta, parecido y fragmentos) no depende del prompt, así que la comparación de las tres sigue siendo válida; solo cambia el formato de la respuesta.

### Redis vs FAISS (para el bonus)

Misma pregunta, mismos fragmentos y mismos embeddings (desde la caché); solo cambia el motor del índice.

| Configuración | Parecido en Redis | Parecido en FAISS | ¿Mismo top-3? | ¿Misma página citada? |
|---|---|---|---|---|
| A · 400/50 | 0,782 | 0,782 | Sí: p.4 (0,782), p.1 (0,777), p.2 (0,769), mismos fragmentos y mismo orden | Sí, p. 4 |
| B · 1200/200 | 0,782 | 0,782 | Sí: p.4 (0,782), p.2 (0,769), p.2 (0,765), mismos fragmentos y mismo orden | Sí, p. 4 |

Capturas FAISS: `capturas/etapa3_400_50_faiss.txt`, `capturas/etapa3_1200_200_faiss.txt`, `capturas/ingesta_400_50_faiss.txt` e `capturas/ingesta_1200_200_faiss.txt`. Redis entrega distancia coseno y FAISS distancia L2² con vectores normalizados; después de `a_parecido()` dan el mismo número (coinciden en los 3 decimales que muestra `--saltos`). Las respuestas de FAISS son del prompt original y las de Redis del prompt de la Etapa 5, por eso cambia el formato de la cita.

Fragmento con mejor parecido en cada configuración (todos de la p. 4):
- A · 400/50: empieza en "Aun así, esta teoría es la que más se ha utilizado en los estudios de detección automática…" (la oración de la respuesta abre el fragmento).
- B · 1200/200: empieza en "El sociólogo H. Spencer adoptó esta teoría…" (la respuesta queda dentro de un fragmento que también trae la teoría del alivio).
- 800/120: empieza en "El humor, según esta obra actúa de válvula de escape…" (la respuesta queda dentro, junto con parte de la teoría del alivio).

Elegimos: 800/120   Porque: ____
