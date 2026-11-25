"""Registro de ejecuciones: (1) líneas de log legibles y (2) la tabla `ejecuciones`.

(1) Logging, copiado de taller-02-c2: escribe en la salida estándar (terminal de uvicorn y
    `heroku logs`). Nunca se registran claves ni cabeceras HTTP.
(2) Tabla `ejecuciones` (nuevo en C2, dueño: Sebastián): una fila por cada llamada a /chat.
    Columnas y estados en docs/contratos.md. Va en Postgres (DATABASE_URL): en Heroku el
    disco se borra al reiniciar, así que SQLite no sirve para el despliegue.
"""

import logging
import os
import sys

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb


NOMBRE_REGISTRO = "tarea_final"
FORMATO = "%(asctime)s %(levelname)-7s [%(name)s] %(message)s"
FORMATO_HORA = "%Y-%m-%d %H:%M:%S"
LARGO_MAXIMO_PREGUNTA = 80


def obtener_registro() -> logging.Logger:
    """Registro del coordinador (sin configurar: eso lo hace configurar_registro)."""
    return logging.getLogger(NOMBRE_REGISTRO)


def tolerar_codificacion(flujo) -> None:
    """Hace que un carácter que la consola no puede escribir se escape en vez de fallar.

    En Windows, con la salida redirigida a un archivo, Python usa cp1252 y no puede escribir
    «→», «←» ni «✗»: esa línea del registro se perdía con UnicodeEncodeError. Con
    backslashreplace sale como «\\u2192» y la línea se conserva. Si el flujo no admite
    reconfigurarse (por ejemplo, el de pytest), se deja como está.
    """
    try:
        flujo.reconfigure(errors="backslashreplace")
    except (AttributeError, ValueError, OSError):
        pass


def configurar_registro(nivel: int = logging.INFO) -> logging.Logger:
    """Envía el registro del coordinador a stdout con fecha y hora.

    Se puede llamar varias veces (por ejemplo con --reload) sin duplicar líneas.
    No propaga al registro raíz para no repetir cada línea si otro módulo lo configura.
    """
    registro = obtener_registro()
    registro.setLevel(nivel)
    registro.propagate = False
    if not any(getattr(manejador, "_registro_coordinador", False) for manejador in registro.handlers):
        tolerar_codificacion(sys.stdout)
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




# ---------------------------------------------------------------------------
# Conexión a Postgres (DATABASE_URL). Compartida con registro_veredictos.py.
# ---------------------------------------------------------------------------


def url_postgres() -> str:
    """DATABASE_URL normalizada. Heroku la entrega como postgres://; se pasa a postgresql://."""
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("Falta DATABASE_URL en .env (en Heroku lo crea el add-on de Postgres).")
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    return url


def conectar_postgres() -> psycopg.Connection:
    """Abre una conexión a Postgres con DATABASE_URL."""
    return psycopg.connect(url_postgres())


# ---------------------------------------------------------------------------
# Tabla `ejecuciones` (C2, dueño: Sebastián). Ver docs/contratos.md, sección 7.
# ---------------------------------------------------------------------------

ESTADOS_FINALES = ("ok", "bloqueado", "fallback", "error")
RUTAS = ("consulta_politica", "revisar_gasto", "fuera_de_alcance")

_ESQUEMA_EJECUCIONES = f"""
CREATE TABLE IF NOT EXISTS ejecuciones (
    id_ejecucion        TEXT PRIMARY KEY,
    fecha               TIMESTAMPTZ NOT NULL,
    ruta                TEXT NOT NULL CHECK (ruta IN {RUTAS!r}),
    pasos               INTEGER NOT NULL,
    herramientas_usadas JSONB NOT NULL,
    hubo_a2a            BOOLEAN NOT NULL,
    estado_final        TEXT NOT NULL CHECK (estado_final IN {ESTADOS_FINALES!r}),
    duracion_ms         INTEGER NOT NULL
)
"""

_COLUMNAS_EJECUCION = (
    "id_ejecucion", "fecha", "ruta", "pasos", "herramientas_usadas", "hubo_a2a", "estado_final", "duracion_ms",
)

_tabla_lista = False


def crear_tabla_ejecuciones() -> None:
    """Crea la tabla `ejecuciones` en Postgres si no existe. Se puede llamar varias veces."""
    global _tabla_lista
    with conectar_postgres() as conexion:
        conexion.execute(_ESQUEMA_EJECUCIONES)
    _tabla_lista = True


def guardar_ejecucion(ejecucion: dict) -> None:
    """Inserta una fila en `ejecuciones` con las columnas de docs/contratos.md.

    No guarda el texto del usuario ni la imagen ni claves: solo los metadatos de la ejecución.
    Si la base no responde, deja una línea de log de error y NO rompe la respuesta de /chat.
    Si el id ya existe, no duplica la fila.
    """
    if ejecucion.get("estado_final") not in ESTADOS_FINALES:
        raise ValueError(f"estado_final no válido: {ejecucion.get('estado_final')!r}")
    try:
        if not _tabla_lista:
            crear_tabla_ejecuciones()
        fila = {c: ejecucion[c] for c in _COLUMNAS_EJECUCION}
        fila["herramientas_usadas"] = Jsonb(list(ejecucion["herramientas_usadas"]))
        with conectar_postgres() as conexion:
            conexion.execute(
                """
                INSERT INTO ejecuciones (id_ejecucion, fecha, ruta, pasos, herramientas_usadas,
                                         hubo_a2a, estado_final, duracion_ms)
                VALUES (%(id_ejecucion)s, %(fecha)s, %(ruta)s, %(pasos)s, %(herramientas_usadas)s,
                        %(hubo_a2a)s, %(estado_final)s, %(duracion_ms)s)
                ON CONFLICT (id_ejecucion) DO NOTHING
                """,
                fila,
            )
    except Exception as error:  # la respuesta al usuario no depende del registro
        obtener_registro().error("no se pudo guardar la ejecución %s · %s", ejecucion.get("id_ejecucion"), error)


def leer_ejecucion(id_ejecucion: str) -> dict | None:
    """Devuelve la fila de `ejecuciones` con ese id como diccionario, o None si no existe.

    La usa GET /registro/{id_ejecucion} (protegido con X-API-Key) en api/app.py.
    """
    if not _tabla_lista:
        crear_tabla_ejecuciones()
    with conectar_postgres() as conexion:
        cursor = conexion.cursor(row_factory=dict_row)
        cursor.execute(
            "SELECT " + ", ".join(_COLUMNAS_EJECUCION) + " FROM ejecuciones WHERE id_ejecucion = %s",
            (id_ejecucion,),
        )
        fila = cursor.fetchone()
    if fila is None:
        return None
    fila["fecha"] = fila["fecha"].isoformat()
    return dict(fila)
