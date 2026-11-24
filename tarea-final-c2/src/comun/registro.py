"""Registro de ejecuciones: (1) líneas de log legibles y (2) la tabla `ejecuciones`.

(1) Logging, copiado de taller-02-c2: escribe en la salida estándar (terminal de uvicorn y
    `heroku logs`). Nunca se registran claves ni cabeceras HTTP.
(2) Tabla `ejecuciones` (nuevo en C2, dueño: Sebastián): una fila por cada llamada a /chat.
    Columnas y estados en docs/contratos.md. Va en Postgres (DATABASE_URL): en Heroku el
    disco se borra al reiniciar, así que SQLite no sirve para el despliegue.
"""

import logging
import sys


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
# Tabla `ejecuciones` (pendiente C2, dueño: Sebastián). Ver docs/contratos.md.
# ---------------------------------------------------------------------------

ESTADOS_FINALES = ("ok", "bloqueado", "fallback", "error")


def crear_tabla_ejecuciones() -> None:
    """Crea la tabla `ejecuciones` en Postgres (DATABASE_URL) si no existe.

    Columnas: id_ejecucion, fecha, ruta, pasos, herramientas_usadas, hubo_a2a,
    estado_final (CHECK en ESTADOS_FINALES) y duracion_ms. Se puede llamar varias veces.
    """
    raise NotImplementedError("crear_tabla_ejecuciones: pendiente (Sebastián, c2tf/sebastian-despliegue).")


def guardar_ejecucion(ejecucion: dict) -> None:
    """Inserta una fila en `ejecuciones` con las columnas de docs/contratos.md.

    No guarda el texto del usuario ni la imagen ni claves: solo los metadatos de la ejecución.
    Si la base no responde, debe dejar una línea de log de error y NO romper la respuesta de /chat.
    """
    raise NotImplementedError("guardar_ejecucion: pendiente (Sebastián, c2tf/sebastian-despliegue).")


def leer_ejecucion(id_ejecucion: str) -> dict | None:
    """Devuelve la fila de `ejecuciones` con ese id como diccionario, o None si no existe.

    La usa GET /registro/{id_ejecucion} (protegido con X-API-Key) en api/app.py.
    """
    raise NotImplementedError("leer_ejecucion: pendiente (Sebastián, c2tf/sebastian-despliegue).")
