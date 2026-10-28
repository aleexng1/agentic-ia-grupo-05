"""Configuración: carga del .env, el modelo de lenguaje y las trazas.

Dueño: rol Núcleo. NO cambiar el modelo ni la temperatura (ver AGENTS.md).
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

# Carpeta tarea-final-c1/ (sirve para encontrar .env, datos/ y pruebas/).
CARPETA_PROYECTO = Path(__file__).resolve().parents[1]

load_dotenv(CARPETA_PROYECTO / ".env")

# Modelo y temperatura fijos para que los resultados sean reproducibles.
MODELO_DEL_CURSO = "gemini-3.5-flash-lite"
TEMPERATURA = 0


def obtener_llm():
    """Devuelve el modelo Gemini listo para usar, con temperatura 0.

    Lee GEMINI_MODEL y GOOGLE_API_KEY del archivo .env.
    Si falta alguna, avisa con un mensaje claro en vez de fallar a medias.
    """
    from langchain_google_genai import ChatGoogleGenerativeAI

    modelo = os.getenv("GEMINI_MODEL", "").strip()
    if not modelo:
        raise RuntimeError(
            f"Falta GEMINI_MODEL en .env. Usa el modelo del curso: GEMINI_MODEL={MODELO_DEL_CURSO}"
        )
    if not os.getenv("GOOGLE_API_KEY", "").strip():
        raise RuntimeError("Falta GOOGLE_API_KEY en .env: pega tu clave de Google AI Studio.")
    return ChatGoogleGenerativeAI(model=modelo, temperature=TEMPERATURA)


def registrar_traza(evento: str, datos: dict) -> None:
    """Imprime un paso del agente de forma legible (qué pasó y con qué datos).

    Se apaga poniendo MOSTRAR_TRAZAS=0 en .env.
    """
    # TODO(nucleo): reemplazar stub (formato final de trazas para el notebook)
    if os.getenv("MOSTRAR_TRAZAS", "1").strip() == "0":
        return
    detalle = json.dumps(datos, ensure_ascii=False, indent=2, default=str)
    print(f"── [{evento}] ──\n{detalle}")
