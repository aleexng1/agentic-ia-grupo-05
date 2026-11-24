"""Modelos de lenguaje: el principal y el de respaldo (resiliencia).

obtener_llm es la función de tarea-final-c1 (src/config.py); solo cambia el nombre de la
variable: GEMINI_MODEL pasó a llamarse MODELO_PRINCIPAL.
El respaldo (MODELO_RESPALDO) es nuevo en C2 y su dueño es Sebastián.
"""

import os

# Importar config carga el .env del proyecto.
from src.comun import config  # noqa: F401

# Modelo y temperatura fijos para que los resultados sean reproducibles (igual que en c1).
MODELO_DEL_CURSO = "gemini-3.5-flash-lite"
TEMPERATURA = 0


def obtener_llm():
    """Devuelve el modelo principal (Gemini) listo para usar, con temperatura 0.

    Lee MODELO_PRINCIPAL y GOOGLE_API_KEY del entorno.
    Si falta alguna, avisa con un mensaje claro en vez de fallar a medias.
    """
    from langchain_google_genai import ChatGoogleGenerativeAI

    modelo = os.getenv("MODELO_PRINCIPAL", "").strip()
    if not modelo:
        raise RuntimeError(
            f"Falta MODELO_PRINCIPAL en .env. Usa el modelo del curso: MODELO_PRINCIPAL={MODELO_DEL_CURSO}"
        )
    if not os.getenv("GOOGLE_API_KEY", "").strip():
        raise RuntimeError("Falta GOOGLE_API_KEY en .env: pega tu clave de Google AI Studio.")
    return ChatGoogleGenerativeAI(model=modelo, temperature=TEMPERATURA)


def obtener_llm_con_respaldo(herramientas: list | None = None):
    """Devuelve el modelo principal con MODELO_RESPALDO como respaldo ante una falla.

    Usa obtener_llm() para el principal y un ChatGoogleGenerativeAI con MODELO_RESPALDO
    (mismo GOOGLE_API_KEY, temperatura 0), unidos con `.with_fallbacks(...)`.
    Si `herramientas` viene, se hace bind_tools en ambos modelos antes de unirlos: un
    RunnableWithFallbacks no admite bind_tools después.
    Solo se cambia de modelo ante una excepción del proveedor (cuota, 503, timeout); nunca se
    inventa una respuesta. Si MODELO_RESPALDO está vacío, devuelve solo el principal.
    Quien responde con el respaldo debe marcar la ejecución como estado_final = "fallback";
    esa señal todavía no la emite este módulo.
    """
    from langchain_google_genai import ChatGoogleGenerativeAI

    principal = obtener_llm()
    modelo_respaldo = os.getenv("MODELO_RESPALDO", "").strip()
    if not modelo_respaldo:
        return principal.bind_tools(herramientas) if herramientas else principal
    respaldo = ChatGoogleGenerativeAI(model=modelo_respaldo, temperature=TEMPERATURA)
    if herramientas:
        return principal.bind_tools(herramientas).with_fallbacks(
            [respaldo.bind_tools(herramientas)]
        )
    return principal.with_fallbacks([respaldo])
