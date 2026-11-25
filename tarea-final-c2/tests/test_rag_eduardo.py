"""Pruebas unitarias del RAG documental; Redis y Gemini son simulados."""

import json
from inspect import signature
from unittest.mock import Mock

import pytest
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import ToolException
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from redis.exceptions import ConnectionError

from src.comun.contrato import Fragmento
from src.conocimiento.rag import rag
from src.principal.flujos import revisar_gasto
from src.principal.herramientas.buscar_politica import buscar_politica


@pytest.fixture(autouse=True)
def indice_simulado(monkeypatch):
    indice = Mock(spec=["similarity_search_with_score"])
    indice.similarity_search_with_score.return_value = []
    monkeypatch.setattr(rag, "_obtener_indice", Mock(return_value=indice))
    return indice


def test_contrato_y_reexportacion():
    assert buscar_politica is rag.buscar_politica
    assert buscar_politica in revisar_gasto.HERRAMIENTAS
    assert buscar_politica.name == "buscar_politica"
    firma = signature(buscar_politica.func)
    assert list(firma.parameters) == ["consulta", "k"]
    assert firma.parameters["consulta"].annotation is str
    assert firma.parameters["k"].annotation is int
    assert firma.parameters["k"].default == 3
    assert firma.return_annotation == list[Fragmento]
    esquema = buscar_politica.args_schema.model_json_schema()
    assert esquema["required"] == ["consulta"]
    assert esquema["properties"]["consulta"]["type"] == "string"
    assert esquema["properties"]["k"]["type"] == "integer"
    assert esquema["properties"]["k"]["default"] == 3


def documento(politica, texto, fuente):
    return Document(
        page_content="Texto preparado para el embedding",
        metadata={"politica": politica, "texto_completo": texto, "fuente": fuente},
    )


def test_recupera_fragmentos_completos_y_cita_fuentes(indice_simulado):
    fuente_politica = "datos/politica_ficticia.md#P02"
    fuente_regla = "datos/politica_ficticia.md#reglas-generales/RG-05"
    indice_simulado.similarity_search_with_score.return_value = [
        (documento("Viajes Internos", "Tope de hotel por documento.", fuente_politica), 0.15),
        (documento("Reglas generales", "Regla general de topes.", fuente_regla), "0.35"),
    ]

    resultado = buscar_politica.invoke({"consulta": "  tope de hotel  ", "k": 2})

    indice_simulado.similarity_search_with_score.assert_called_once_with("tope de hotel", k=2)
    assert resultado == [
        {"politica": "Viajes Internos", "texto": "Tope de hotel por documento.",
         "fuente": fuente_politica, "puntaje": -0.15},
        {"politica": "Reglas generales", "texto": "Regla general de topes.",
         "fuente": fuente_regla, "puntaje": -0.35},
    ]
    assert all(set(fragmento) == Fragmento.__required_keys__ for fragmento in resultado)
    assert all(isinstance(fragmento["puntaje"], float) for fragmento in resultado)
    assert resultado[0]["puntaje"] > resultado[1]["puntaje"]


@pytest.mark.parametrize(("args", "k"), [({}, 3), ({"k": 1}, 1), ({"k": 10}, 10)])
def test_sin_resultados_devuelve_lista_vacia(indice_simulado, args, k):
    assert buscar_politica.invoke({"consulta": "sin coincidencias", **args}) == []
    indice_simulado.similarity_search_with_score.assert_called_once_with("sin coincidencias", k=k)


@pytest.mark.parametrize("consulta", ["", " \t\n"])
def test_rechaza_consulta_vacia_sin_buscar(consulta):
    with pytest.raises(ToolException, match="no puede estar vacía"):
        buscar_politica.invoke({"consulta": consulta})
    rag._obtener_indice.assert_not_called()


def test_funcion_rechaza_consulta_no_textual():
    with pytest.raises(ToolException, match="debe ser texto"):
        buscar_politica.func(None)
    rag._obtener_indice.assert_not_called()


@pytest.mark.parametrize("k", [0, 11])
def test_herramienta_rechaza_k_fuera_de_rango(k):
    with pytest.raises(ToolException, match="entre 1 y 10"):
        buscar_politica.invoke({"consulta": "hotel", "k": k})
    rag._obtener_indice.assert_not_called()


@pytest.mark.parametrize("k", [True, 2.5, "2"])
def test_funcion_rechaza_k_no_entero_antes_de_buscar(k):
    # StructuredTool valida/coacciona con Pydantic antes de llamar a .func.
    with pytest.raises(ToolException, match="debe ser un entero"):
        buscar_politica.func("hotel", k=k)
    rag._obtener_indice.assert_not_called()


@pytest.mark.parametrize(
    ("campo", "valor", "error"),
    [
        ("texto_completo", None, "texto_completo válido"),
        ("texto_completo", 123, "texto_completo válido"),
        ("texto_completo", "", "texto_completo válido"),
        ("texto_completo", " \t\n", "texto_completo válido"),
        ("politica", None, "metadatos incompatibles"),
        ("politica", "", "metadatos incompatibles"),
        ("politica", " \t\n", "metadatos incompatibles"),
        ("fuente", None, "metadatos incompatibles"),
        ("fuente", ["P02"], "metadatos incompatibles"),
        ("fuente", "", "metadatos incompatibles"),
        ("fuente", " \t\n", "metadatos incompatibles"),
    ],
)
def test_metadatos_invalidos_no_se_sustituyen(indice_simulado, campo, valor, error):
    doc = documento("Viajes Internos", "Texto completo", "datos/politica_ficticia.md#P02")
    if valor is None:
        del doc.metadata[campo]
    else:
        doc.metadata[campo] = valor
    indice_simulado.similarity_search_with_score.return_value = [(doc, 0.2)]
    with pytest.raises(ToolException, match=error):
        buscar_politica.invoke({"consulta": "hotel"})


@pytest.mark.parametrize(
    "puntaje",
    [None, "no numérico", float("nan"), float("inf"), float("-inf"), "NaN", "inf", "-inf"],
)
def test_puntaje_incompatible_produce_error_controlado(indice_simulado, puntaje):
    doc = documento("Viajes Internos", "Texto completo", "datos/politica_ficticia.md#P02")
    indice_simulado.similarity_search_with_score.return_value = [(doc, puntaje)]
    with pytest.raises(ToolException, match="puntuación incompatible"):
        buscar_politica.invoke({"consulta": "hotel"})


def test_metadatos_validos_conservan_su_texto_original(indice_simulado):
    doc = documento(" Viajes Internos ", "\nTexto completo\n", " datos/politica_ficticia.md#P02 ")
    indice_simulado.similarity_search_with_score.return_value = [(doc, 0.2)]

    assert buscar_politica.invoke({"consulta": "hotel"}) == [
        {"politica": doc.metadata["politica"], "texto": doc.metadata["texto_completo"],
         "fuente": doc.metadata["fuente"], "puntaje": -0.2},
    ]


@pytest.mark.parametrize("fallo_inicializacion", [False, True])
def test_error_de_redis_no_expone_detalles(indice_simulado, fallo_inicializacion):
    punto_fallo = (
        rag._obtener_indice if fallo_inicializacion else indice_simulado.similarity_search_with_score
    )
    marcador = "detalle-interno-simulado"
    punto_fallo.side_effect = ConnectionError(marcador)
    with pytest.raises(ToolException, match=r"Falló la búsqueda.*ConnectionError") as error:
        buscar_politica.invoke({"consulta": "hotel"})
    assert marcador not in str(error.value)
    assert error.value.__suppress_context__


def test_toolnode_react_recibe_fragmentos_o_error_controlado(indice_simulado):
    nodo = ToolNode(revisar_gasto.HERRAMIENTAS, handle_tool_errors=(ToolException,))
    grafo = StateGraph(MessagesState)
    # ToolNode necesita el runtime que provee un grafo compilado, igual que en ReAct.
    grafo.add_node("herramientas", lambda estado: nodo.invoke(estado))
    grafo.set_entry_point("herramientas")
    grafo.set_finish_point("herramientas")
    agente = grafo.compile()
    llamada = AIMessage(content="", tool_calls=[
        {"name": "buscar_politica", "args": {"consulta": "hotel"}, "id": "rag-1"},
    ])
    fuente = "datos/politica_ficticia.md#P02"
    indice_simulado.similarity_search_with_score.return_value = [
        (documento("Viajes Internos", "Texto completo", fuente), 0.1),
    ]

    respuesta = agente.invoke({"messages": [llamada]})["messages"][-1]
    assert isinstance(respuesta, ToolMessage)
    assert respuesta.tool_call_id == "rag-1"
    assert respuesta.status == "success"
    assert json.loads(respuesta.content)[0]["fuente"] == fuente

    indice_simulado.similarity_search_with_score.side_effect = ConnectionError("detalle-interno")
    respuesta = agente.invoke({"messages": [llamada]})["messages"][-1]
    assert respuesta.status == "error"
    assert "Falló la búsqueda" in respuesta.content
    assert "detalle-interno" not in respuesta.content
