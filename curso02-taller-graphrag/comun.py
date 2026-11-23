"""Piezas compartidas por cargar_neo4j.py (paso 5) y servidor.py (paso 7).

Aquí viven las constantes del grafo (índice vectorial, dimensiones, nombres de relaciones),
la conexión a Neo4j (con los certificados de certifi) y el cálculo de embeddings con Gemini,
para que la carga y las consultas usen exactamente lo mismo.
"""

import os
import time
from pathlib import Path
from typing import Callable, TypeVar

import certifi
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from neo4j import GraphDatabase, TrustCustomCAs
from neo4j.exceptions import AuthError

BASE = Path(__file__).resolve().parent

# --- El grafo ---------------------------------------------------------------
DIMENSIONES = 768
NOMBRE_INDICE = "producto_embedding"
RELACIONES = "DE_MARCA|EN_CATEGORIA|DE_LINEA|IMITA|TIENE"

# --- Reintentos ante límite de uso o fallas del servidor ----------------------
CODIGOS_REINTENTABLES = {408, 429, 500, 502, 503, 504}

# Esquemas "seguros" de Neo4j -> esquema equivalente sin verificación incluida en la URI.
# Con certifi hay que pasar los certificados por separado, y eso solo se permite con estos.
ESQUEMAS_SEGUROS = {"neo4j+s": "neo4j", "bolt+s": "bolt"}

AYUDA_CONEXION = """\
No pude conectarme a Neo4j. Causas posibles:
  1. Python sin certificados raíz (pasa con el Python de python.org en Mac): el driver falla con
     «Unable to retrieve routing information». Este programa ya usa los certificados de certifi;
     si ves este mensaje, confirma que certifi está instalado (pip install -r requirements.txt).
  2. La instancia de Aura gratis está pausada (se pausa por inactividad): reanúdala en la consola de Aura.
  3. NEO4J_URI mal copiado (debe verse como neo4j+s://xxxxxxxx.databases.neo4j.io) o sin internet.
Detalle técnico: {detalle}"""


class ErrorConexion(Exception):
    """No se pudo abrir la conexión con Neo4j (el mensaje ya trae la explicación)."""


class ErrorConfiguracion(Exception):
    """Falta algo en el .env o el modelo devuelve algo incompatible con el índice."""


def formato_precio(n: int) -> str:
    return "$" + f"{n:,}".replace(",", ".")


def cargar_env(requeridas: list[str]) -> dict[str, str]:
    """Carga el .env de esta carpeta y devuelve las variables pedidas (sin mostrar sus valores)."""
    load_dotenv(BASE / ".env")
    faltan = [v for v in requeridas if not os.getenv(v)]
    if faltan:
        raise ErrorConfiguracion(f"Faltan variables en el .env: {', '.join(faltan)} (ver .env.example).")
    return {v: os.environ[v] for v in requeridas}


# --- Neo4j ------------------------------------------------------------------
def conectar(uri: str, usuario: str, clave: str):
    """Abre el driver usando los certificados raíz de certifi para neo4j+s:// / bolt+s://."""
    esquema, _, resto = uri.partition("://")
    opciones: dict = {}
    if esquema in ESQUEMAS_SEGUROS:
        uri = f"{ESQUEMAS_SEGUROS[esquema]}://{resto}"
        opciones = {"encrypted": True, "trusted_certificates": TrustCustomCAs(certifi.where())}
    driver = GraphDatabase.driver(uri, auth=(usuario, clave), **opciones)
    try:
        driver.verify_connectivity()
    except AuthError:
        driver.close()
        raise ErrorConexion("Neo4j rechazó el usuario o la contraseña. En instancias nuevas de Aura el "
                            "usuario NO es «neo4j»: es el ID de la instancia (revisa el .txt que descargaste).")
    except Exception as e:  # ServiceUnavailable, errores de SSL, DNS, etc.
        driver.close()
        raise ErrorConexion(AYUDA_CONEXION.format(detalle=f"{type(e).__name__}: {str(e)[:300]}"))
    return driver


# --- Gemini -----------------------------------------------------------------
T = TypeVar("T")


def reintentar(llamada: Callable[[], T], intentos: int = 4, espera_base: float = 5, etiqueta: str = "Gemini") -> T:
    """Ejecuta `llamada` reintentando (con espera creciente) ante límite de uso o fallas pasajeras.

    Los errores de configuración (clave, modelo o petición inválidos) no se reintentan.
    """
    ultimo_error: Exception | None = None
    for intento in range(1, intentos + 1):
        try:
            return llamada()
        except errors.APIError as e:
            ultimo_error = e
            if e.code not in CODIGOS_REINTENTABLES:
                raise
        except Exception as e:  # red caída, respuesta vacía, etc.
            ultimo_error = e
        if intento < intentos:
            espera = espera_base * 2 ** (intento - 1)
            print(f"    {etiqueta}: intento {intento}/{intentos} falló ({type(ultimo_error).__name__}); "
                  f"espero {espera:g}s…")
            time.sleep(espera)
    raise ultimo_error  # type: ignore[misc]


def pedir_embedding(cliente: genai.Client, modelo: str, texto: str, tarea: str = "RETRIEVAL_DOCUMENT",
                    intentos: int = 4, espera_base: float = 5) -> list[float]:
    """Embedding de `texto` con el mismo modelo y dimensiones del grafo.

    tarea: "RETRIEVAL_DOCUMENT" al guardar productos, "RETRIEVAL_QUERY" al buscar con una pregunta.
    """
    def llamar() -> list[float]:
        respuesta = cliente.models.embed_content(
            model=modelo,
            contents=texto,
            config=types.EmbedContentConfig(task_type=tarea, output_dimensionality=DIMENSIONES),
        )
        return list(respuesta.embeddings[0].values)

    vector = reintentar(llamar, intentos, espera_base, etiqueta="embedding")
    if len(vector) != DIMENSIONES:
        raise ErrorConfiguracion(f"El modelo de embeddings devolvió {len(vector)} dimensiones y el índice es "
                                 f"de {DIMENSIONES}. Revisa MODELO_EMBEDDINGS en el .env.")
    return vector
