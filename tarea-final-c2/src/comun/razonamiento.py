"""Nivel de razonamiento interno («thinking») de Gemini para las llamadas cortas de Alex.

Dueño: Alex. Lo usan el router (`src/principal/router.py`) y la lectura de la boleta del
verificador (`src/verificador/agente.py`): clasificar un mensaje o leer cuatro datos de una
imagen no necesita razonar, y cada token de razonamiento suma latencia.

Los modelos Gemini 3 no permiten apagar el razonamiento: el nivel más bajo es "minimal".
`gemini-3.5-flash-lite` ya usa "minimal" por defecto, pero `gemini-3.5-flash` (el respaldo)
usa "medium". Por eso se fija explícitamente en todos.

NIVEL_RAZONAMIENTO = minimal (por defecto) | low | medium | high | predeterminado (el del modelo).
"""

import os

NIVELES = ("minimal", "low", "medium", "high")
POR_DEFECTO = "minimal"


def nivel_razonamiento() -> str | None:
    """El nivel configurado, o None si se pidió el del modelo («predeterminado»)."""
    valor = os.getenv("NIVEL_RAZONAMIENTO", "").strip().lower() or POR_DEFECTO
    if valor == "predeterminado":
        return None
    if valor not in NIVELES:
        raise ValueError(
            f"NIVEL_RAZONAMIENTO debe ser uno de {', '.join(NIVELES)} o «predeterminado»; vale «{valor}»."
        )
    return valor


def con_nivel_razonamiento(llm):
    """Aplica NIVEL_RAZONAMIENTO a un ChatGoogleGenerativeAI (se lee en cada llamada) y lo devuelve."""
    nivel = nivel_razonamiento()
    if nivel is not None and hasattr(llm, "reasoning_effort"):
        llm.reasoning_effort = nivel
    return llm
