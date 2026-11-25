"""Consulta el índice documental existente sin crear ni modificar índices o claves."""

import json
from functools import lru_cache
from math import isfinite
from numbers import Real
from struct import Struct, error as StructError
from urllib.parse import parse_qsl, urlsplit

from langchain_core.documents import Document
from redis import Redis
from redis.backoff import NoBackoff
from redis.exceptions import RedisError
from redis.retry import Retry
from redisvl.query import VectorQuery
from redisvl.query.filter import Text

DIMENSIONES = 3072
_VECTOR = Struct(f"<{DIMENSIONES}f")


class ErrorLectura(RuntimeError):
    """Error del lector con un mensaje fijo apto para el agente."""


def _pares(datos):
    if isinstance(datos, dict):
        return datos
    return dict(zip(datos[::2], datos[1::2], strict=True))


def _filtro_esquema(info, indice):
    """Valida FT.INFO RESP2 sin inferir parámetros ausentes."""
    try:
        definicion = _pares(info["index_definition"])
        campos = {}
        for entrada in info["attributes"]:
            cabecera = entrada if isinstance(entrada, dict) else _pares(entrada[:6])
            campos[cabecera["attribute"]] = cabecera, entrada

        cabecera, entrada = campos["embedding"]
        if isinstance(entrada, dict):
            atributos = {clave.lower(): valor for clave, valor in entrada.items() if clave != "type"}
        else:
            resto = entrada[6:]
            # Algunas versiones devuelven primero el algoritmo y el número de parámetros.
            if resto and resto[0] in ("FLAT", "HNSW"):
                atributos = {"algorithm": resto[0], **_pares(resto[2:])}
            else:
                atributos = _pares(resto)
            atributos = {clave.lower(): valor for clave, valor in atributos.items()}

        def campo_hash(nombre, tipo):
            campo, _ = campos[nombre]
            return campo["identifier"] == nombre and campo["type"] == tipo

        tipo_vector = atributos.get("data_type", atributos.get("datatype", atributos.get("type")))
        con_filtro = "_index_name" in campos
        compatible = (
            info["index_name"] == indice
            and definicion["key_type"] == "HASH"
            and definicion["prefixes"] in ([indice], [indice + ":"])
            and cabecera["identifier"] == "embedding"
            and cabecera["type"] == "VECTOR"
            and str(atributos.get("dim", atributos.get("dims"))) == str(DIMENSIONES)
            and tipo_vector == "FLOAT32"
            and atributos.get("distance_metric") == "COSINE"
            and atributos.get("algorithm") == "FLAT"
            and campo_hash("text", "TEXT")
            and campo_hash("_metadata_json", "TEXT")
            and (not con_filtro or campo_hash("_index_name", "TEXT"))
        )
        if compatible:
            return Text("_index_name") == indice if con_filtro else None
    except (KeyError, TypeError, ValueError, IndexError, AttributeError):
        pass
    raise ErrorLectura("El esquema del índice Redis no es compatible con el RAG.") from None


def _serializar_vector(vector):
    try:
        if len(vector) == DIMENSIONES and all(
            isinstance(valor, Real) and not isinstance(valor, bool) and isfinite(valor)
            for valor in vector
        ):
            datos = _VECTOR.pack(*vector)
            if any(_VECTOR.unpack(datos)):
                return datos
    except (TypeError, ValueError, OverflowError, StructError):
        pass
    raise ErrorLectura("El proveedor devolvió un vector de consulta incompatible.") from None


@lru_cache(maxsize=1)
def _embeddings(modelo):
    from google.genai.types import HttpOptions, HttpRetryOptions
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    class EmbeddingsConLimites(GoogleGenerativeAIEmbeddings):
        # La versión instalada no aplica request_options al construir EmbedContentConfig.
        def _build_config(self, **opciones):
            config = super()._build_config(**opciones)
            config.http_options = HttpOptions(
                timeout=10_000, retry_options=HttpRetryOptions(attempts=1)
            )
            return config

    return EmbeddingsConLimites(model=modelo)


class LectorRedis:
    """Por búsqueda, solo FT.INFO y FT.SEARCH, además del handshake de redis-py."""

    def __init__(self, url, indice, modelo):
        # redis-py da prioridad a parámetros de la URL, incluso sobre los timeouts.
        if any(clave != "db" for clave, _ in parse_qsl(urlsplit(url).query, keep_blank_values=True)):
            raise ErrorLectura("La URL de Redis no admite opciones de conexión salvo db.")
        cliente = Redis.from_url(
            url,
            protocol=2,
            decode_responses=True,
            socket_connect_timeout=3,
            socket_timeout=5,
            retry=Retry(NoBackoff(), 0),
            lib_name=None,
            lib_version=None,
        )
        self._busqueda = cliente.ft(indice)
        self._indice = indice
        self._modelo = modelo

    def similarity_search_with_score(self, consulta, *, k):
        try:
            info = self._busqueda.info()
        except RedisError:
            raise ErrorLectura(
                "No se pudo inspeccionar el índice Redis. Verifica que exista y que el acceso esté permitido."
            ) from None
        filtro = _filtro_esquema(info, self._indice)
        vector = _serializar_vector(_embeddings(self._modelo).embed_query(consulta))
        knn = VectorQuery(
            vector=vector,
            vector_field_name="embedding",
            filter_expression=filtro,
            return_fields=["text", "_metadata_json"],
            num_results=k,
            sort_by=("vector_distance", "ASC"),
        )
        try:
            respuesta = self._busqueda.search(knn.query, query_params=knn.params)
        except RedisError:
            raise ErrorLectura("No se pudo consultar el índice Redis.") from None

        resultados = []
        for fila in respuesta.docs:
            try:
                metadata = json.loads(fila._metadata_json)
                if not isinstance(metadata, dict):
                    raise ValueError
                documento = Document(page_content=fila.text, metadata=metadata)
            except (AttributeError, TypeError, ValueError, RecursionError):
                raise ErrorLectura("El documento recuperado tiene metadatos incompatibles.") from None
            # Los campos requeridos y la distancia se validan en buscar_politica.
            resultados.append((documento, getattr(fila, "vector_distance", None)))
        return resultados
