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


def obtener_llm_con_respaldo():
    """Devuelve un modelo que, si el principal falla, reintenta con MODELO_RESPALDO.

    Debe usar obtener_llm() para el principal y otro ChatGoogleGenerativeAI con
    MODELO_RESPALDO (mismo GOOGLE_API_KEY, temperatura 0) unidos con `.with_fallbacks(...)`.
    Solo se cambia de modelo ante fallas del proveedor (cuota, 503, timeout): nunca se
    inventa una respuesta. Quien lo use marca la ejecución como estado_final = "fallback"
    cuando respondió el respaldo. Si MODELO_RESPALDO está vacío, devuelve solo el principal.
    """
    raise NotImplementedError("obtener_llm_con_respaldo: pendiente (Sebastián, c2tf/sebastian-despliegue).")
