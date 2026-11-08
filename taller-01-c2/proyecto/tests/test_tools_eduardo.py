"""Pruebas deterministas de la herramienta de presupuesto simulado."""

from copy import deepcopy

import pytest

from src.agente_eduardo.tools import estimar_presupuesto


def _estimar(**datos):
    return estimar_presupuesto.invoke(datos)


def test_importes_exactos_para_feria_tecnologica():
    resultado = _estimar(tipo_evento="tecnologico", personas=80, duracion_minutos=240)
    assert resultado["partidas_clp"] == {
        "recinto_referencial": 800_000,
        "equipamiento": 200_000,
        "personal": 768_000,
        "logistica": 64_000,
        "alimentacion_generica": 144_000,
    }
    assert resultado["subtotal_clp"] == 1_976_000
    assert resultado["contingencia_clp"] == 197_600
    assert resultado["total_clp"] == 2_173_600


def test_subtotal_contingencia_y_total_son_coherentes():
    resultado = _estimar(tipo_evento="cultural", personas=13, duracion_minutos=31)
    assert resultado["subtotal_clp"] == sum(resultado["partidas_clp"].values())
    assert resultado["total_clp"] == resultado["subtotal_clp"] + resultado["contingencia_clp"]
    assert resultado["contingencia_clp"] == (resultado["subtotal_clp"] * 10 + 99) // 100


@pytest.mark.parametrize("tipo", ["tecnologico", "gastronomico", "cultural", "infantil"])
def test_cubre_las_cuatro_categorias(tipo):
    resultado = _estimar(tipo_evento=tipo, personas=10, duracion_minutos=30)
    assert resultado["tipo_evento"] == tipo
    assert len(resultado["partidas_clp"]) == 5


@pytest.mark.parametrize(
    ("personas", "duracion"),
    [(10, 30), (500, 480)],
)
def test_acepta_limites_incluidos(personas, duracion):
    assert "total_clp" in _estimar(tipo_evento="cultural", personas=personas, duracion_minutos=duracion)


@pytest.mark.parametrize(
    "datos",
    [
        {"tipo_evento": "deportivo", "personas": 50, "duracion_minutos": 120},
        {"tipo_evento": "cultural", "personas": 9, "duracion_minutos": 120},
        {"tipo_evento": "cultural", "personas": 501, "duracion_minutos": 120},
        {"tipo_evento": "cultural", "personas": True, "duracion_minutos": 120},
        {"tipo_evento": "cultural", "personas": 50, "duracion_minutos": 29},
        {"tipo_evento": "cultural", "personas": 50, "duracion_minutos": 481},
    ],
)
def test_invalidos_devuelven_solo_motivo(datos):
    resultado = _estimar(**datos)
    assert set(resultado) == {"motivo"}
    assert resultado["motivo"]


def test_normaliza_tildes_y_alias_habituales():
    resultado = _estimar(tipo_evento="Feria Tecnológica", personas=80, duracion_minutos=240)
    assert resultado["tipo_evento"] == "tecnologico"


def test_no_afirma_precios_reales_ni_autoriza_gastos():
    resultado = _estimar(tipo_evento="gastronómico", personas=50, duracion_minutos=120)
    assert "ficticios" in resultado["advertencia"]
    assert "no son precios reales" in resultado["advertencia"]
    assert "no constituyen autorización de gasto" in resultado["advertencia"]
    assert "impuestos no modelados" in resultado["advertencia"].casefold()
    assert not any("precio_real" in clave or "autoriza" in clave for clave in resultado)


def test_otras_invocaciones_no_alteran_un_resultado_previo():
    original = _estimar(tipo_evento="infantil", personas=40, duracion_minutos=90)
    copia = deepcopy(original)
    _estimar(tipo_evento="tecnologico", personas=500, duracion_minutos=480)
    assert original == copia
