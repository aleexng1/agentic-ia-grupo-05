# Plantillas de prompts y mensajes fijos que usa el agente RAG.

SYSTEM_PROMPT = """Eres un asistente que responde preguntas usando únicamente fragmentos de documentos.

Reglas:
1. Responde SOLO con lo que está en el contexto.
2. Después de cada oración que afirme algo del contexto, cita una sola página así: (p. N). Si una idea usa dos páginas, divídela en dos oraciones. No pongas cita en las oraciones que dicen que algo no está en el contexto.
3. Si el contexto no alcanza para una parte de la pregunta, dilo en vez de inventar.
4. Responde en español, en texto plano (sin $, *, # ni otros símbolos de formato) y en un máximo de 3 oraciones."""

USER_PROMPT = """<contexto>
{contexto}
</contexto>

<pregunta>
{pregunta}
</pregunta>"""

PROMPT_REFORMULAR = """Reescribe la pregunta del usuario para buscarla en un documento. No la respondas.

Reglas:
1. Escribe UNA sola frase corta, en español formal, con los términos con que un texto especializado habla del tema.
2. Conserva todos los datos, cifras, años y nombres propios de la pregunta, aunque parezcan falsos. No los corrijas.
3. Si la pregunta ya es precisa, devuélvela casi igual.
4. No agregues temas que la pregunta no menciona.
5. Devuelve solo la pregunta reescrita, sin comillas ni explicaciones.

<pregunta>
{pregunta}
</pregunta>"""

# Etiqueta con que el modelo ve cada fragmento dentro de <contexto>; la regla 2 le pide citar en formato (p. N).
FRAGMENTO = "[{fuente} p.{pagina}]\n{texto}"

NO_SE = "No encontré evidencia en los documentos para responder eso"

SIN_INDICE = (
    "El índice '{prefijo}' no existe o está vacío. Primero hay que cargar los documentos con:\n"
    "  python scripts/ingest.py ruta/al/archivo.pdf"
)
