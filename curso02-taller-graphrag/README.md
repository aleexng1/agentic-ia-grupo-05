# Taller GraphRAG (práctica personal)

Taller de clase personal (Curso 2, sesión 14, 23 nov 2026): GraphRAG sobre un Excel de productos con réplicas. Neo4j + Gemini + LangGraph + LangSmith. Práctica individual de Alex, no se une a main.

## Pasos del taller

- [ ] 1. Cuenta e instancia gratis de Neo4j
- [ ] 2. Descargar el Excel
- [ ] 3. Programa que extrae relaciones de cada fila con Gemini
- [ ] 4. Página para revisar las relaciones de cada producto
- [ ] 5. Programa que sube a Neo4j y crea embeddings
- [ ] 6. Ver el grafo en Neo4j
- [ ] 7. Agregar GraphRAG (preguntas al grafo) a la página del paso 4
- [ ] 8. Agente LangGraph con trazas en LangSmith

## Configuración

1. Copia `.env.example` a `.env`.
2. Rellena `.env` con los datos del `.txt` que descarga Neo4j Aura al crear la instancia y con la clave de Gemini (Google AI Studio).
3. El `.env` nunca se sube al repositorio (está en `.gitignore`); solo se versiona `.env.example`.

## Cómo se usa

Todos los comandos se corren desde `curso02-taller-graphrag/` con el entorno virtual activado:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

| Paso | Comando | Qué hace |
|---|---|---|
| 3 | `python extraer_fichas.py` | Gemini extrae una ficha por producto → `data/fichas.jsonl` |
| 5 | `python cargar_neo4j.py` | Sube las fichas a Neo4j como grafo y crea los embeddings |
| 4 y 7 | `python servidor.py` | Levanta la página (revisar fichas + preguntar al grafo) |

En el `.env` hacen falta, además de las claves: `MODELO` (Gemini para extraer y responder) y `MODELO_EMBEDDINGS` (ver `.env.example`).

### Preguntar al grafo (paso 7)

1. Con el grafo ya cargado en Neo4j (`python cargar_neo4j.py`), levanta el servidor:
   ```bash
   python servidor.py
   ```
2. Abre la página en el navegador:
   ```bash
   xdg-open http://127.0.0.1:8000
   ```
3. Usa la pestaña **Preguntar al grafo**. La pestaña **Revisar relaciones** funciona igual que antes (también abriendo `revisar.html` con doble clic, sin servidor).

El servidor solo escucha en `127.0.0.1` (tu computador) y es quien guarda las claves: la página nunca las ve. Para detenerlo, `Ctrl+C` en la terminal.

Con cada pregunta se buscan los 5 productos más parecidos con los embeddings y se revisan sus conexiones en el grafo (marca, réplica, lo que copia, originales y parecidos). El botón **Comparar con la respuesta sin grafo** le hace a Gemini la misma pregunta con los mismos 5 productos, pero solo con la fila cruda del Excel, y debajo de cada respuesta se puede desplegar el contexto que recibió.
