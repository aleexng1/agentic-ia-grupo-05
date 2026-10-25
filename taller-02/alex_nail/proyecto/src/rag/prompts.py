# Plantillas de prompts y mensajes fijos que usa el agente RAG.

SYSTEM_PROMPT = """Eres un asistente que responde preguntas usando únicamente fragmentos de documentos.

Reglas:
1. Responde SOLO con lo que está en el contexto.
2. Cita cada afirmación como [archivo p.N].
3. Si el contexto no alcanza para una parte de la pregunta, dilo en vez de inventar.
4. Responde en español y de forma breve."""

USER_PROMPT = """<contexto>
{contexto}
</contexto>

<pregunta>
{pregunta}
</pregunta>"""

# Cómo se presenta cada fragmento dentro de <contexto>; la etiqueta es la misma que debe usar la cita.
FRAGMENTO = "[{fuente} p.{pagina}]\n{texto}"

NO_SE = "No encontré evidencia en los documentos para responder eso"

SIN_INDICE = (
    "El índice '{prefijo}' no existe o está vacío. Primero hay que cargar los documentos con:\n"
    "  python scripts/ingest.py ruta/al/archivo.pdf"
)
