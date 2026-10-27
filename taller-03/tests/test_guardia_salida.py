"""Prueba guardia_salida directamente (sin agente). Usa el modelo real y datos ficticios."""
import asyncio
import os

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from src.colombia.graph import crear_guardia_salida, crear_modelo

pytestmark = pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="falta GOOGLE_API_KEY")

RESULTADOS = (
    '[{"id":1,"name":"Parque Ficticio Aurora","departmentId":99,"landArea":1200.5},'
    '{"id":2,"name":"Reserva Ficticia Luna","departmentId":99,"landArea":300.0}]'
)


def revisar(borrador: str) -> dict:
    modelo = crear_modelo(
        os.environ.get("MODELO_GUARDIA") or os.environ["MODELO"],
        os.environ["GOOGLE_API_KEY"],
        temperature=0,
    )
    estado = {
        "messages": [
            HumanMessage("¿Qué áreas naturales tiene el departamento ficticio 99?", id="h"),
            AIMessage("", tool_calls=[{"name": "get_natural_areas_by_department", "args": {"departmentId": 99}, "id": "t1"}], id="a1"),
            ToolMessage(RESULTADOS, name="get_natural_areas_by_department", tool_call_id="t1", id="m1"),
            AIMessage(borrador, id="a2"),
        ],
        "veredicto": None,
        "revision": None,
        "reintento": False,
    }
    return asyncio.run(crear_guardia_salida(modelo)(estado))["revision"]


def test_cifra_inventada_no_se_aprueba():
    rev = revisar("El Parque Ficticio Aurora tiene 9999 hectáreas de superficie.")
    assert not rev["aprobada"]
    assert "dato_no_respaldado" in rev["problemas"]


def test_borrador_fiel_se_aprueba():
    rev = revisar("El departamento tiene el Parque Ficticio Aurora, con 1200.5 hectáreas, y la Reserva Ficticia Luna, con 300.0 hectáreas.")
    assert rev["aprobada"], rev["detalle"]
    assert rev["problemas"] == []


def test_borrador_largo_marca_formato():
    relleno = " ".join(["tranquilo"] * 190)
    rev = revisar(f"El Parque Ficticio Aurora tiene 1200.5 hectáreas y es un lugar {relleno}.")
    assert "formato" in rev["problemas"]
    assert not rev["aprobada"]
