"""Regresión de validación de presupuestos completos.

El reconocimiento previo usa patrones limitados. Los datos se buscan en el mensaje
nuevo y en los anteriores del mismo context_id (memoria del grafo).
"""

import asyncio
from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver

from src.agente_eduardo import graph as modulo_graph


@pytest.fixture(autouse=True)
def memoria_limpia(monkeypatch):
    """Cada prueba parte con la memoria del grafo vacía."""
    monkeypatch.setattr(modulo_graph.graph, "checkpointer", MemorySaver())


@pytest.mark.parametrize(
    ("solicitud", "pregunta"),
    [
        ("Calcula el presupuesto de una feria tecnológica para 80 personas", "duración"),
        ("Calcula el presupuesto de una feria tecnológica de 2 horas", "personas"),
        ("Calcula el presupuesto para 80 personas durante 2 horas", "tipo de evento"),
    ],
)
def test_dato_obligatorio_faltante_no_invoca_el_agente(monkeypatch, solicitud, pregunta):
    invocaciones = []

    async def invocar(*args, **kwargs):
        invocaciones.append((args, kwargs))
        return {"messages": [SimpleNamespace(content="presupuesto")]}

    monkeypatch.setattr(modulo_graph.graph, "ainvoke", invocar)
    respuesta = asyncio.run(modulo_graph.responder(solicitud, "contexto-prueba"))

    assert pregunta in respuesta
    assert "Indícame ese dato" in respuesta
    assert "tipo de evento" in respuesta
    assert "cantidad de personas" in respuesta
    assert "duración" in respuesta
    assert invocaciones == []


@pytest.mark.parametrize(
    "solicitud",
    [
        "Estima el gasto de una feria tecnológica para 80 personas",
        "¿Cuánto costaría una feria tecnológica para 80 personas?",
    ],
)
def test_nuevos_patrones_de_presupuesto_incompleto_no_invocan_el_agente(
    monkeypatch, solicitud
):
    invocaciones = []

    async def invocar(*args, **kwargs):
        invocaciones.append((args, kwargs))
        return {"messages": [SimpleNamespace(content="presupuesto")]}

    monkeypatch.setattr(modulo_graph.graph, "ainvoke", invocar)
    respuesta = asyncio.run(modulo_graph.responder(solicitud, "contexto-prueba"))

    assert "duración" in respuesta
    assert "Indícame ese dato" in respuesta
    assert "tipo de evento" in respuesta
    assert "cantidad de personas" in respuesta
    assert invocaciones == []


@pytest.mark.parametrize(
    ("solicitud", "especialista"),
    [
        ("Recomiéndame un menú vegetariano para 80 personas", "Sebastián"),
        ("Recomiéndame un recinto para 80 personas", "Alex"),
        ("Sugiere actividades para 80 personas", "Matías"),
    ],
)
def test_consulta_ajena_se_deriva_por_el_grafo(monkeypatch, solicitud, especialista):
    invocaciones = []

    async def invocar(*args, **kwargs):
        invocaciones.append((args, kwargs))
        return {"messages": [SimpleNamespace(content=f"Te corresponde con {especialista}.")]}

    monkeypatch.setattr(modulo_graph.graph, "ainvoke", invocar)
    respuesta = asyncio.run(modulo_graph.responder(solicitud, "contexto-prueba"))

    assert especialista in respuesta
    assert len(invocaciones) == 1


@pytest.mark.parametrize(
    ("solicitud", "especialista"),
    [
        ("Recomiéndame un menú vegetariano para 80 personas", "Sebastián"),
        ("Recomiéndame un recinto para 80 personas", "Alex"),
        ("Sugiere actividades para 80 personas", "Matías"),
    ],
)
def test_saltos_consulta_ajena_muestra_nodo_model(monkeypatch, capsys, solicitud, especialista):
    mensaje = SimpleNamespace(content=f"Te corresponde con {especialista}.", tool_calls=[])

    def transmitir(*args, **kwargs):
        yield {"model": {"messages": [mensaje]}}

    monkeypatch.setattr(modulo_graph.graph, "stream", transmitir)
    modulo_graph.saltos(solicitud)
    salida = capsys.readouterr().out

    assert "Nodo: model" in salida
    assert "Saltos totales: 1" in salida
    assert especialista in salida


@pytest.mark.parametrize(
    ("solicitud", "pregunta"),
    [
        ("Calcula el presupuesto para 80 personas durante 2 horas", "tipo de evento"),
        ("Calcula el presupuesto de una feria tecnológica durante 2 horas", "personas"),
        ("Calcula el presupuesto de una feria tecnológica para 80 personas", "duración"),
    ],
)
def test_saltos_presupuesto_incompleto_pregunta_sin_invocar(
    monkeypatch, capsys, solicitud, pregunta
):
    invocaciones = []

    def transmitir(*args, **kwargs):
        invocaciones.append((args, kwargs))
        yield {"model": {"messages": []}}

    monkeypatch.setattr(modulo_graph.graph, "stream", transmitir)
    modulo_graph.saltos(solicitud)
    salida = capsys.readouterr().out

    assert pregunta in salida
    assert "Saltos totales: 0" in salida
    assert invocaciones == []


def test_solicitud_completa_invoca_el_agente(monkeypatch):
    invocaciones = []

    async def invocar(*args, **kwargs):
        invocaciones.append((args, kwargs))
        return {"messages": [SimpleNamespace(content="presupuesto calculado")]}

    monkeypatch.setattr(modulo_graph.graph, "ainvoke", invocar)
    respuesta = asyncio.run(
        modulo_graph.responder(
            "Calcula el presupuesto de una feria tecnológica para 80 personas durante 4 horas",
            "contexto-prueba",
        )
    )

    assert respuesta == "presupuesto calculado"
    assert len(invocaciones) == 1


def _invocador(invocaciones, respuesta="presupuesto calculado"):
    async def invocar(*args, **kwargs):
        invocaciones.append((args, kwargs))
        return {"messages": [SimpleNamespace(content=respuesta)]}

    return invocar


def test_seguimiento_completa_el_dato_faltante_en_el_mismo_contexto(monkeypatch):
    invocaciones = []
    monkeypatch.setattr(modulo_graph.graph, "ainvoke", _invocador(invocaciones))

    primera = asyncio.run(
        modulo_graph.responder("Presupuesto para una feria gastronómica de 120 personas", "ctx-1")
    )
    assert "duración" in primera
    assert invocaciones == []

    estado = modulo_graph.graph.get_state({"configurable": {"thread_id": "ctx-1"}})
    tipos = [mensaje.type for mensaje in estado.values["messages"]]
    assert tipos == ["human", "ai"]

    segunda = asyncio.run(modulo_graph.responder("3 horas", "ctx-1"))
    assert segunda == "presupuesto calculado"
    assert len(invocaciones) == 1


def test_seguimiento_sin_el_dato_vuelve_a_preguntar(monkeypatch):
    invocaciones = []
    monkeypatch.setattr(modulo_graph.graph, "ainvoke", _invocador(invocaciones))

    asyncio.run(modulo_graph.responder("Presupuesto para una feria gastronómica", "ctx-2"))
    segunda = asyncio.run(modulo_graph.responder("3 horas", "ctx-2"))

    assert "personas" in segunda
    assert invocaciones == []


def test_otro_contexto_no_completa_los_datos(monkeypatch):
    invocaciones = []
    monkeypatch.setattr(modulo_graph.graph, "ainvoke", _invocador(invocaciones))

    asyncio.run(
        modulo_graph.responder("Presupuesto para una feria gastronómica de 120 personas", "ctx-3")
    )
    otra = asyncio.run(modulo_graph.responder("Presupuesto para 3 horas", "ctx-otro"))

    assert "tipo de evento" in otra
    assert invocaciones == []


@pytest.mark.parametrize(
    "seguimiento",
    ["¿Y si son 200 personas?", "¿Y cuánto cuesta si son 200 personas?"],
)
def test_seguimiento_de_presupuesto_completo_usa_los_datos_anteriores(monkeypatch, seguimiento):
    config = {"configurable": {"thread_id": "ctx-4"}}
    modulo_graph.graph.update_state(
        config,
        {
            "messages": [
                HumanMessage(content="Presupuesto para una feria tecnológica de 80 personas y 2 horas"),
                AIMessage(content="Total: $1.000.000 CLP"),
            ]
        },
        as_node="model",
    )
    invocaciones = []
    monkeypatch.setattr(modulo_graph.graph, "ainvoke", _invocador(invocaciones))

    respuesta = asyncio.run(modulo_graph.responder(seguimiento, "ctx-4"))

    assert respuesta == "presupuesto calculado"
    assert len(invocaciones) == 1


def test_costanera_no_cuenta_como_costo():
    assert modulo_graph._dato_faltante("Programa para una feria en la costanera de 3 horas") is None


@pytest.mark.parametrize("palabra", ["niños", "niñas", "asistentes", "invitados", "participantes"])
def test_acepta_otras_palabras_para_personas(palabra):
    solicitud = f"Presupuesto para 80 {palabra} en una feria infantil de 2 horas"
    assert modulo_graph._dato_faltante(solicitud) is None
