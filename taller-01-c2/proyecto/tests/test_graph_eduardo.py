"""Regresión de validación de presupuestos completos en un solo turno.

El reconocimiento previo usa patrones limitados y no acumula datos entre turnos.
"""

import asyncio
from types import SimpleNamespace

import pytest

from src.agente_eduardo import graph as modulo_graph


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
    assert "solicitud completa" in respuesta
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
    assert "solicitud completa" in respuesta
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
