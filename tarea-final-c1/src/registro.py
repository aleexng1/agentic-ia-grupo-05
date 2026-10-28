"""Registro de veredictos en SQLite (la "acción" del agente).

Dueño: rol Herramientas y estado.
La base es un archivo local que Git ignora (*.db): cada persona tiene la suya.
"""

from src.config import CARPETA_PROYECTO
from src.contrato import Gasto, Veredicto

# Archivo de la base de datos de prueba.
RUTA_REGISTRO = CARPETA_PROYECTO / "registro_veredictos.db"


def registrar_veredicto(gasto: Gasto, veredicto: Veredicto) -> dict:
    """Guarda el veredicto de un gasto y devuelve el estado antes y después.

    Devuelve un diccionario con al menos:
        "antes":   cómo estaba el registro antes de guardar (ej. cantidad de filas),
        "despues": cómo quedó después de guardar.
    """
    # TODO(herramientas): reemplazar stub por INSERT en SQLite (RUTA_REGISTRO)
    return {
        "id_gasto": gasto["id"],
        "decision": veredicto["decision"],
        "antes": {"registros": 0},
        "despues": {"registros": 1},
    }


def reiniciar_registro() -> None:
    """Deja la base de prueba como al inicio (vacía), sin tocar nada más."""
    # TODO(herramientas): reemplazar stub (borrar solo las filas de RUTA_REGISTRO)
    return None
