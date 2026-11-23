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
