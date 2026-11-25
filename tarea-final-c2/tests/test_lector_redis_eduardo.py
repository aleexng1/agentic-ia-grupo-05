"""Pruebas sin red: el cliente real traduce las operaciones a comandos simulados."""

import json
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest
from langchain_core.tools import ToolException
from redis.exceptions import NoPermissionError, ResponseError, TimeoutError

from src.conocimiento.rag import lector_redis, rag

INDICE = "grupo05_v15"
MODELO = "models/gemini-embedding-001"
FUENTE = "datos/politica_ficticia.md#P02"


def esquema():
    return {
        "index_name": INDICE,
        "index_definition": ["key_type", "HASH", "prefixes", [INDICE]],
        "attributes": [
            ["identifier", campo, "attribute", campo, "type", "TEXT"]
            for campo in ("text", "_metadata_json", "_index_name")
        ] + [[
            "identifier", "embedding", "attribute", "embedding", "type", "VECTOR",
            "algorithm", "FLAT", "data_type", "FLOAT32", "dim", 3072, "distance_metric", "COSINE",
        ]],
    }


def fila(distancia="0.2", metadata=None):
    if metadata is None:
        metadata = json.dumps({"politica": "Viajes Internos", "texto_completo": "Política", "fuente": FUENTE})
    return ["text", "Índice", "_metadata_json", metadata, "vector_distance", distancia]


@pytest.fixture
def simulado(monkeypatch):
    info = esquema()
    datos = [2, "doc1", fila("0.2"), "doc2", fila("0.4")]
    eventos = Mock()

    def comando(nombre, *args, **kwargs):
        if nombre == "FT.INFO":
            return [valor for par in info.items() for valor in par]
        if nombre == "FT.SEARCH":
            return datos
        pytest.fail(f"Comando no permitido en lector: {nombre}")

    eventos.redis.side_effect = comando
    eventos.gemini.embed_query.return_value = [1.0] + [0.0] * 3071
    monkeypatch.setattr(lector_redis.Redis, "execute_command", eventos.redis)
    monkeypatch.setattr(lector_redis, "_embeddings", Mock(return_value=eventos.gemini))
    monkeypatch.setenv("REDIS_URL", "redis://redis.invalid:6379/0")
    monkeypatch.setenv("REDIS_PREFIJO", INDICE)
    monkeypatch.setenv("EMBEDDING_MODEL", MODELO)
    rag._obtener_indice.cache_clear()
    yield info, datos, eventos
    rag._obtener_indice.cache_clear()


def test_solo_info_y_search_parametrizada_en_orden(simulado):
    _, _, eventos = simulado
    rag._obtener_indice()
    assert eventos.mock_calls == []

    resultados = rag.buscar_politica.invoke({"consulta": "  hotel interno  ", "k": 2})

    assert [frag["puntaje"] for frag in resultados] == [-0.2, -0.4]
    assert all(frag["fuente"] == FUENTE and frag["texto"] == "Política" for frag in resultados)
    assert eventos.mock_calls[:2] == [call.redis("FT.INFO", INDICE), call.gemini.embed_query("hotel interno")]
    assert len(eventos.mock_calls) == 3
    comando, indice, consulta, *opciones = eventos.redis.call_args.args
    assert (comando, indice) == ("FT.SEARCH", INDICE)
    assert "@_index_name:" in consulta and INDICE in consulta
    assert "KNN 2 @embedding $" in consulta and "hotel interno" not in consulta
    assert opciones[opciones.index("SORTBY"):][:3] == ["SORTBY", "vector_distance", "ASC"]
    assert opciones[opciones.index("LIMIT"):][:3] == ["LIMIT", 0, 2]
    assert opciones[opciones.index("DIALECT") + 1] == 2
    blob = next(valor for valor in opciones if isinstance(valor, bytes))
    assert len(blob) == 3072 * 4 and blob[:4] == b"\x00\x00\x80?"
    lector_redis._embeddings.assert_called_once_with(MODELO)


def test_sin_campo_de_filtro_preserva_busqueda_sin_filtro_y_k_predeterminado(simulado):
    info, datos, eventos = simulado
    del info["attributes"][2]
    datos[:] = [0]
    assert rag.buscar_politica.invoke({"consulta": "hotel"}) == []
    consulta = eventos.redis.call_args.args[2]
    assert consulta.startswith("*=>[KNN 3") and "_index_name" not in consulta


@pytest.mark.parametrize("campo,valor", [
    ("dim", 768), ("data_type", "FLOAT64"), ("distance_metric", "L2"), ("algorithm", "HNSW"),
    ("distance_metric", None), ("algorithm", None), ("data_type", None),
])
def test_rechaza_esquema_vectorial_antes_de_embeddings(simulado, campo, valor):
    info, _, eventos = simulado
    vector = info["attributes"][-1]
    posicion = vector.index(campo)
    if valor is None:
        del vector[posicion:posicion + 2]
    else:
        vector[posicion + 1] = valor
    with pytest.raises(ToolException, match="esquema"):
        rag.buscar_politica.invoke({"consulta": "hotel"})
    assert eventos.mock_calls == [call.redis("FT.INFO", INDICE)]
    lector_redis._embeddings.assert_not_called()


@pytest.mark.parametrize("incompatible", ["json", "prefijo", "contenido", "metadata"])
def test_rechaza_almacenamiento_y_campos_incompatibles(simulado, incompatible):
    info, _, eventos = simulado
    if incompatible == "json":
        info["index_definition"][1] = "JSON"
    elif incompatible == "prefijo":
        info["index_definition"][-1] = ["otro"]
    else:
        del info["attributes"][0 if incompatible == "contenido" else 1]
    with pytest.raises(ToolException, match="esquema"):
        rag.buscar_politica.invoke({"consulta": "hotel"})
    assert eventos.mock_calls == [call.redis("FT.INFO", INDICE)]


@pytest.mark.parametrize("error", [ResponseError, NoPermissionError, TimeoutError])
def test_fallo_de_inspeccion_no_llama_gemini_ni_filtra_detalle(simulado, error):
    _, _, eventos = simulado
    eventos.redis.side_effect = error("detalle-interno-simulado")
    with pytest.raises(ToolException, match="No se pudo inspeccionar") as capturado:
        rag.buscar_politica.invoke({"consulta": "hotel"})
    assert "detalle-interno" not in str(capturado.value)
    assert eventos.mock_calls == [call.redis("FT.INFO", INDICE)]


@pytest.mark.parametrize("vector", [
    [1.0], [0.0] * 3072, [float("nan")] * 3072, [float("inf")] * 3072, [1e50] * 3072,
    ["1"] * 3072, [True] * 3072,
], ids=["dim", "nulo", "nan", "inf", "overflow", "cadena", "booleano"])
def test_vector_invalido_no_llega_a_search(simulado, vector):
    _, _, eventos = simulado
    eventos.gemini.embed_query.return_value = vector
    with pytest.raises(ToolException, match="vector de consulta incompatible"):
        rag.buscar_politica.invoke({"consulta": "hotel"})
    assert eventos.mock_calls == [call.redis("FT.INFO", INDICE), call.gemini.embed_query("hotel")]


@pytest.mark.parametrize("metadata", ["no-json", "[]", "{}", '{"fuente": "   "}'])
def test_metadata_danada_no_inventa_resultados(simulado, metadata):
    _, datos, _ = simulado
    datos[:] = [1, "doc", fila(metadata=metadata)]
    with pytest.raises(ToolException, match="metadatos incompatibles|texto_completo válido"):
        rag.buscar_politica.invoke({"consulta": "hotel"})


def test_timeout_de_busqueda_controlado_sin_reintento(simulado):
    _, _, eventos = simulado
    comando = eventos.redis.side_effect

    def con_timeout(nombre, *args, **kwargs):
        if nombre == "FT.SEARCH":
            raise TimeoutError("detalle-interno-simulado")
        return comando(nombre, *args, **kwargs)

    eventos.redis.side_effect = con_timeout
    with pytest.raises(ToolException, match="No se pudo consultar") as capturado:
        rag.buscar_politica.invoke({"consulta": "hotel"})
    assert "detalle-interno" not in str(capturado.value)
    assert eventos.redis.call_count == 2


def test_limites_de_redis_y_rechazo_de_opciones_en_url(simulado, monkeypatch):
    _, _, eventos = simulado
    desde_url = Mock(wraps=lector_redis.Redis.from_url)
    monkeypatch.setattr(lector_redis.Redis, "from_url", desde_url)
    rag._obtener_indice()
    opciones = desde_url.call_args.kwargs
    assert opciones["socket_connect_timeout"] == 3
    assert opciones["socket_timeout"] == 5
    assert opciones["retry"].get_retries() == 0
    assert eventos.mock_calls == []
    with pytest.raises(lector_redis.ErrorLectura, match="opciones de conexión"):
        lector_redis.LectorRedis("redis://redis.invalid?socket_timeout=0", INDICE, MODELO)
    assert desde_url.call_count == 1


def test_gemini_conserva_modelo_y_tarea_con_limites_por_peticion(monkeypatch):
    from langchain_google_genai import embeddings

    cliente = Mock()
    cliente.models.embed_content.return_value = SimpleNamespace(
        embeddings=[SimpleNamespace(values=[1.0] * 3072)]
    )
    monkeypatch.setattr(embeddings, "Client", Mock(return_value=cliente))
    monkeypatch.setenv("GOOGLE_API_KEY", "valor-ficticio-para-prueba")
    monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "false")
    lector_redis._embeddings.cache_clear()
    try:
        vector = lector_redis._embeddings(MODELO).embed_query("hotel")
    finally:
        lector_redis._embeddings.cache_clear()
    assert len(vector) == 3072
    llamada = cliente.models.embed_content.call_args.kwargs
    assert llamada["model"] == MODELO
    assert llamada["contents"] == "hotel"
    config = llamada["config"]
    assert config.task_type == "RETRIEVAL_QUERY"
    assert config.output_dimensionality is None  # Igual que el cargador y el lector heredado.
    assert config.http_options.timeout == 10_000
    assert config.http_options.retry_options.attempts == 1
