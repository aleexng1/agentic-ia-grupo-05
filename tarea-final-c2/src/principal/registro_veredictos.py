"""Registro de veredictos en Postgres (la "acción" del agente).

Dueño: Sebastián (c2tf/sebastian-despliegue). Antes era SQLite; en Heroku el disco se borra
al reiniciar, así que va en Postgres (DATABASE_URL), igual que la tabla `ejecuciones`.

Decisiones de diseño:
- NO es una herramienta del LLM. La llama el grafo en un nodo determinista,
  solo después de que el juez valida el veredicto. Así un jailbreak en la glosa o en el
  mensaje (GS-27, GS-30) no puede escribir ni borrar el registro.
- Se puede repetir con seguridad: hay una fila por gasto (id_gasto es único). Registrar
  dos veces lo mismo no duplica; registrar una decisión distinta actualiza la fila.
- Cada escritura devuelve el estado antes y después (evidencia para la sección 8).
- reiniciar_registro solo vacía la tabla: no toca otros datos. Es para pruebas.
"""

from src.comun.contrato import DECISIONES, Gasto, Veredicto
from src.comun.registro import conectar_postgres

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
    registrado_en       TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""

# Columnas que se comparan para saber si una nueva escritura cambia algo.
_COLUMNAS_CONTENIDO = (
    "id_fondo", "monto", "decision", "motivo", "politica_sugerida", "categoria_sugerida", "cuenta_sugerida",
)


def _foto(conexion, id_gasto: str) -> dict:
    """Estado del registro: cantidad de filas, filas por decisión y la fila de este gasto."""
    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM veredictos")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT decision, COUNT(*) AS n FROM veredictos GROUP BY decision")
    por_decision = {decision: n for decision, n in cursor.fetchall()}
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM veredictos WHERE id_gasto = %s", (id_gasto,))
    fila = cursor.fetchone()
    gasto = None
    if fila is not None:
        columnas = [descripcion.name for descripcion in cursor.description]
        gasto = dict(zip(columnas, fila))
        gasto["registrado_en"] = gasto["registrado_en"].isoformat()
    return {"registros": total, "por_decision": por_decision, "gasto": gasto}


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
    }
    # La transacción se confirma al salir del primer "with" (o se deshace si hay error).
    with conectar_postgres() as conexion:
        conexion.execute(_ESQUEMA)
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
                VALUES (%(id_gasto)s, %(id_fondo)s, %(monto)s, %(decision)s, %(motivo)s,
                        %(politica_sugerida)s, %(categoria_sugerida)s, %(cuenta_sugerida)s, now())
                ON CONFLICT (id_gasto) DO UPDATE SET
                    id_fondo = EXCLUDED.id_fondo, monto = EXCLUDED.monto, decision = EXCLUDED.decision,
                    motivo = EXCLUDED.motivo, politica_sugerida = EXCLUDED.politica_sugerida,
                    categoria_sugerida = EXCLUDED.categoria_sugerida,
                    cuenta_sugerida = EXCLUDED.cuenta_sugerida, registrado_en = EXCLUDED.registrado_en
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
    with conectar_postgres() as conexion:
        conexion.execute(_ESQUEMA)
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM veredictos ORDER BY registrado_en, id_gasto")
        columnas = [descripcion.name for descripcion in cursor.description]
        filas = []
        for fila in cursor.fetchall():
            registro = dict(zip(columnas, fila))
            registro["registrado_en"] = registro["registrado_en"].isoformat()
            filas.append(registro)
        return filas


def reiniciar_registro() -> None:
    """Deja la tabla de veredictos vacía, sin tocar nada más. Solo para pruebas."""
    with conectar_postgres() as conexion:
        conexion.execute(_ESQUEMA)
        conexion.execute("DELETE FROM veredictos")
    return None
