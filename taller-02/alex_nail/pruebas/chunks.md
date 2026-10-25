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
| A · 400/50 |  |  |  |  |
| B · 1200/200 |  |  |  |  |
| 800/120 |  |  |  |  |

Elegimos: ____   Porque: ____
