"""Registro de veredictos en SQLite (la "acción" del agente).

Dueño: rol Herramientas y estado.
La base es un archivo local que Git ignora (*.db): cada persona tiene la suya.

Decisiones de diseño:
- NO es una herramienta del LLM. La llama el grafo (Núcleo) en un nodo determinista,
  solo después de que el juez valida el veredicto. Así un jailbreak en la glosa o en el
  mensaje (GS-27, GS-30) no puede escribir ni borrar el registro.
- Se puede repetir con seguridad: hay una fila por gasto (id_gasto es único). Registrar
  dos veces lo mismo no duplica; registrar una decisión distinta actualiza la fila.
- Cada escritura devuelve el estado antes y después (evidencia para la sección 8).
- reiniciar_registro solo vacía la tabla: no borra el archivo ni toca otros datos.
"""

import sqlite3
from contextlib import closing
from datetime import datetime

from src.config import CARPETA_PROYECTO
from src.contrato import DECISIONES, Gasto, Veredicto

# Archivo de la base de datos de prueba.
RUTA_REGISTRO = CARPETA_PROYECTO / "registro_veredictos.db"

_ESQUEMA = """
CREATE TABLE IF NOT EXISTS veredictos (
    id_gasto            TEXT PRIMARY KEY,
    id_fondo            TEXT NOT NULL,
    monto               INTEGER NOT NULL,
    decision            TEXT NOT NULL CHECK (decision IN ('aprobar', 'observar', 'rechazar')),
    motivo              TEXT NOT NULL,
    politica_sugerida   TEXT NOT NULL,
    categoria_sugerida  TEXT NOT NULL,
    cuenta_sugerida     TEXT NOT NULL,
    registrado_en       TEXT NOT NULL
)
"""

# Columnas que se comparan para saber si una nueva escritura cambia algo.
_COLUMNAS_CONTENIDO = (
    "id_fondo", "monto", "decision", "motivo", "politica_sugerida", "categoria_sugerida", "cuenta_sugerida",
)


def _conectar() -> sqlite3.Connection:
    """Abre la base (la crea si no existe) y asegura que la tabla exista."""
    conexion = sqlite3.connect(RUTA_REGISTRO)
    conexion.row_factory = sqlite3.Row
    conexion.execute(_ESQUEMA)
    return conexion


def _foto(conexion: sqlite3.Connection, id_gasto: str) -> dict:
    """Estado del registro: cantidad de filas, filas por decisión y la fila de este gasto."""
    total = conexion.execute("SELECT COUNT(*) FROM veredictos").fetchone()[0]
    por_decision = {
        fila["decision"]: fila["n"]
        for fila in conexion.execute("SELECT decision, COUNT(*) AS n FROM veredictos GROUP BY decision")
    }
    fila = conexion.execute("SELECT * FROM veredictos WHERE id_gasto = ?", (id_gasto,)).fetchone()
    return {"registros": total, "por_decision": por_decision, "gasto": dict(fila) if fila else None}


def registrar_veredicto(gasto: Gasto, veredicto: Veredicto) -> dict:
    """Guarda el veredicto de un gasto y devuelve el estado antes y después.

    Devuelve un diccionario con al menos:
        "antes":   cómo estaba el registro antes de guardar (ej. cantidad de filas),
        "despues": cómo quedó después de guardar.
    Además: "id_gasto", "decision" y "operacion" ("insertado", "actualizado" o "sin_cambios").
    """
    if veredicto.get("decision") not in DECISIONES:
        raise ValueError(f"Decisión '{veredicto.get('decision')}' no válida; debe ser una de {DECISIONES}.")
    nueva = {
        "id_gasto": gasto["id"],
        "id_fondo": gasto["id_fondo"],
        "monto": int(gasto["monto"]),
        "decision": veredicto["decision"],
        "motivo": veredicto["motivo"],
        "politica_sugerida": veredicto["politica_sugerida"],
        "categoria_sugerida": veredicto["categoria_sugerida"],
        "cuenta_sugerida": veredicto["cuenta_sugerida"],
        "registrado_en": datetime.now().isoformat(timespec="seconds"),
    }
    with closing(_conectar()) as conexion, conexion:  # el segundo "with" confirma o deshace la transacción
        antes = _foto(conexion, gasto["id"])
        previa = antes["gasto"]
        if previa and all(previa[c] == nueva[c] for c in _COLUMNAS_CONTENIDO):
            operacion = "sin_cambios"
        else:
            operacion = "actualizado" if previa else "insertado"
            conexion.execute(
                """
                INSERT INTO veredictos (id_gasto, id_fondo, monto, decision, motivo, politica_sugerida,
                                        categoria_sugerida, cuenta_sugerida, registrado_en)
                VALUES (:id_gasto, :id_fondo, :monto, :decision, :motivo, :politica_sugerida,
                        :categoria_sugerida, :cuenta_sugerida, :registrado_en)
                ON CONFLICT(id_gasto) DO UPDATE SET
                    id_fondo = excluded.id_fondo, monto = excluded.monto, decision = excluded.decision,
                    motivo = excluded.motivo, politica_sugerida = excluded.politica_sugerida,
                    categoria_sugerida = excluded.categoria_sugerida,
                    cuenta_sugerida = excluded.cuenta_sugerida, registrado_en = excluded.registrado_en
                """,
                nueva,
            )
        despues = _foto(conexion, gasto["id"])
    return {
        "id_gasto": gasto["id"],
        "decision": veredicto["decision"],
        "operacion": operacion,
        "antes": antes,
        "despues": despues,
    }


def leer_registro() -> list[dict]:
    """Devuelve todas las filas del registro (para mostrarlas en el notebook)."""
    with closing(_conectar()) as conexion:
        return [dict(fila) for fila in conexion.execute("SELECT * FROM veredictos ORDER BY registrado_en, id_gasto")]


def reiniciar_registro() -> None:
    """Deja la base de prueba como al inicio (vacía), sin tocar nada más."""
    with closing(_conectar()) as conexion, conexion:
        conexion.execute("DELETE FROM veredictos")
    return None
