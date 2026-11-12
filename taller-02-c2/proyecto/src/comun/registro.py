"""Registro legible (logging) de cada consulta que pasa por el coordinador.

Escribe en la salida estándar: se ve en la terminal de uvicorn y en `heroku logs`.
Nunca se registran claves ni cabeceras HTTP: solo el paso, el agente y los tiempos.
"""

import logging
import sys


NOMBRE_REGISTRO = "coordinador"
FORMATO = "%(asctime)s %(levelname)-7s [%(name)s] %(message)s"
FORMATO_HORA = "%Y-%m-%d %H:%M:%S"
LARGO_MAXIMO_PREGUNTA = 80


def obtener_registro() -> logging.Logger:
    """Registro del coordinador (sin configurar: eso lo hace configurar_registro)."""
    return logging.getLogger(NOMBRE_REGISTRO)


def configurar_registro(nivel: int = logging.INFO) -> logging.Logger:
    """Envía el registro del coordinador a stdout con fecha y hora.

    Se puede llamar varias veces (por ejemplo con --reload) sin duplicar líneas.
    No propaga al registro raíz para no repetir cada línea si otro módulo lo configura.
    """
    registro = obtener_registro()
    registro.setLevel(nivel)
    registro.propagate = False
    if not any(getattr(manejador, "_registro_coordinador", False) for manejador in registro.handlers):
        manejador = logging.StreamHandler(sys.stdout)
        manejador.setFormatter(logging.Formatter(FORMATO, datefmt=FORMATO_HORA))
        manejador._registro_coordinador = True
        registro.addHandler(manejador)
    return registro


def una_linea(texto: str) -> str:
    """Deja un texto en una sola línea, sin saltos ni espacios repetidos."""
    return " ".join(str(texto).replace("\r", " ").replace("\n", " ").split())


def recortar(texto: str, largo: int = LARGO_MAXIMO_PREGUNTA) -> str:
    """Una línea de como máximo `largo` caracteres (termina en … si se recortó)."""
    linea = una_linea(texto)
    if len(linea) <= largo:
        return linea
    return linea[: largo - 1].rstrip() + "…"


def segundos(valor: float) -> str:
    """Formatea segundos con coma decimal: 2.345 -> «2,3 s»."""
    return f"{valor:.1f}".replace(".", ",") + " s"
