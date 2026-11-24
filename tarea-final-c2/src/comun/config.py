"""Configuración: lee las variables de entorno (.env en local, Config Vars en Heroku).

Origen: une config.py de taller-02-c2 (puerto, url_base) y de tarea-final-c1
(CARPETA_PROYECTO, registrar_traza). obtener_llm se movió a src/comun/modelos.py.

Los nombres de TODAS las variables están en .env.example y en docs/contratos.md.
Este módulo nunca imprime valores de claves.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

# Carpeta tarea-final-c2/ (sirve para encontrar .env, datos/ y evaluacion/).
CARPETA_PROYECTO = Path(__file__).resolve().parents[2]

load_dotenv(CARPETA_PROYECTO / ".env")


# ---------------------------------------------------------------------------
# Ciclo ReAct
# ---------------------------------------------------------------------------

MAX_PASOS_POR_DEFECTO = 10


def max_pasos_react() -> int:
    """Máximo de vueltas del ciclo ReAct por turno: MAX_PASOS_REACT, o 10 si no existe.

    Es la condición de parada explícita del flujo revisar_gasto (ver docs/contratos.md).
    Un valor que no sea un entero positivo es un error de configuración: se avisa claro.
    """
    valor = os.getenv("MAX_PASOS_REACT", "").strip()
    if not valor:
        return MAX_PASOS_POR_DEFECTO
    try:
        pasos = int(valor)
    except ValueError:
        raise ValueError(f"MAX_PASOS_REACT debe ser un entero positivo; vale «{valor}».") from None
    if pasos < 1:
        raise ValueError(f"MAX_PASOS_REACT debe ser un entero positivo; vale «{valor}».")
    return pasos


# Se lee una vez al importar; src/comun/contrato.py lo reexporta para el código de c1.
MAX_PASOS = max_pasos_react()


# ---------------------------------------------------------------------------
# Servidor (copiado de taller-02-c2)
# ---------------------------------------------------------------------------


def puerto() -> int:
    """Puerto real donde escucha la app: PORT (lo asigna Heroku), si no PUERTO, si no 8000."""
    for variable in ("PORT", "PUERTO"):
        valor = os.getenv(variable, "").strip()
        if valor:
            try:
                return int(valor)
            except ValueError:
                raise ValueError(f"{variable} debe ser un número de puerto; vale «{valor}».") from None
    return 8000


def url_verificador() -> str:
    """Dirección pública del verificador A2A (URL_VERIFICADOR), sin barra final.

    La usan las dos apps: el principal para delegar y el verificador para publicar su ficha.
    """
    return (os.getenv("URL_VERIFICADOR", "").strip() or "http://127.0.0.1:8001").rstrip("/")


def timeout_a2a_seg() -> float:
    """Segundos máximos que el principal espera al verificador (TIMEOUT_A2A_SEG, 20 por defecto)."""
    valor = os.getenv("TIMEOUT_A2A_SEG", "").strip()
    try:
        return float(valor) if valor else 20.0
    except ValueError:
        raise ValueError(f"TIMEOUT_A2A_SEG debe ser un número de segundos; vale «{valor}».") from None


def forzar_fallo_a2a() -> bool:
    """True si FORZAR_FALLO_A2A=1: sirve para la evidencia de fallo controlado (sin apagar nada)."""
    return os.getenv("FORZAR_FALLO_A2A", "0").strip() == "1"


# ---------------------------------------------------------------------------
# Trazas (copiado de tarea-final-c1)
# ---------------------------------------------------------------------------


def registrar_traza(evento: str, datos: dict) -> None:
    """Imprime un paso del agente de forma legible (qué pasó y con qué datos).

    Se apaga poniendo MOSTRAR_TRAZAS=0 en .env.
    """
    if os.getenv("MOSTRAR_TRAZAS", "1").strip() == "0":
        return
    detalle = json.dumps(datos, ensure_ascii=False, indent=2, default=str)
    print(f"── [{evento}] ──\n{detalle}")
