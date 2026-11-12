"""Configuración compartida: lee .env y crea el modelo."""

import os
import warnings

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

MODELO = os.getenv("MODELO", "gemini-3.5-flash-lite")

# gemini-3.5-flash-lite usa parámetros de muestreo fijos e ignora temperature.
# Se pide temperature=0 igual (por si se cambia de modelo) y se silencia el aviso repetido.
warnings.filterwarnings("ignore", message=r".*uses fixed sampling defaults.*")


def crear_llm(temperatura: float = 0) -> ChatGoogleGenerativeAI:
    """Crea el modelo configurado en MODELO. La clave se toma de GOOGLE_API_KEY."""
    return ChatGoogleGenerativeAI(model=MODELO, temperature=temperatura)
