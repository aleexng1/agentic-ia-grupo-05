import os

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver

from .prompts import SISTEMA
from .tools import cargar_herramientas


async def construir_agente(api_key: str | None = None):
    herramientas = await cargar_herramientas()
    modelo = ChatGoogleGenerativeAI(
        model=os.environ["MODELO"],
        google_api_key=api_key or os.environ.get("GOOGLE_API_KEY"),
    )
    return create_agent(
        modelo,
        herramientas,
        system_prompt=SISTEMA,
        checkpointer=MemorySaver(),
    )
