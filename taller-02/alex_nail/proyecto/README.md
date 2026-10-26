# Proyecto RAG

## Identificación

- Grupo: 05
- Integrantes: Eduardo Basaure, Matías Muñoz, Alex Nail, Sebastián Mardones
- Esta versión: Alex Nail
- Material de un compañero: el PDF del taller lo propuso Matías Muñoz.
- Ayudante de programación: Claude Code (en lugar de OpenCode).

## Cómo correrlo

Desde esta carpeta (`taller-02/alex_nail/proyecto/`):

```bash
# 1. Entorno virtual e instalación
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Variables: copiar la plantilla y completar GOOGLE_API_KEY y REDIS_URL
cp .env.example .env

# 3. Ingestar el documento
python scripts/ingest.py docs/humor-computacional.pdf --reset

# 4. Preguntar
python main.py rag "pregunta" --saltos

# 5. Ver el grafo (Mermaid, sin ejecutarlo)
python main.py rag --diagrama
```

## Documento usado

Pulkowska, W. (2025). *Detección automática del humor: los algoritmos aplicados a ambigüedad, incongruencia y rasgos complementarios*. Trabajo de Fin de Grado, Grado en Filología Hispánica. Tutor: Francisco J. Salguero Lamillar. Se usó una versión sin portada ni índice.
