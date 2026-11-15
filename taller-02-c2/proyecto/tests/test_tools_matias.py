"""Pruebas de la herramienta armar_programa (no usan el modelo ni la clave)."""

from datetime import datetime

import pytest

from src.agente_matias.tools import _ACTIVIDADES, armar_programa

TIPOS = list(_ACTIVIDADES)
PUBLICOS = ["familiar", "adulto", "estudiantes"]
DURACIONES = [30, 60, 90, 180, 360, 480]


def _armar(**datos):
    """Llama a la herramienta como lo hace el modelo."""
    return armar_programa.invoke(datos)


def _minutos(hora):
    inicio = datetime.strptime(hora, "%H:%M")
    return inicio.hour * 60 + inicio.minute


@pytest.mark.parametrize("duracion", DURACIONES)
@pytest.mark.parametrize("publico", PUBLICOS)
@pytest.mark.parametrize("tipo", TIPOS)
def test_el_programa_nunca_pasa_de_la_duracion_pedida(tipo, publico, duracion):
    resultado = _armar(tipo_evento=tipo, duracion_minutos=duracion, publico=publico)

    suma = sum(actividad["duracion_minutos"] for actividad in resultado["actividades"])
    assert suma == resultado["minutos_usados"]
    assert resultado["minutos_usados"] <= duracion
    assert resultado["minutos_libres"] == duracion - resultado["minutos_usados"]
    assert resultado["minutos_libres"] >= 0


@pytest.mark.parametrize("tipo", TIPOS)
def test_las_actividades_son_consecutivas_y_las_horas_cuadran(tipo):
    resultado = _armar(
        tipo_evento=tipo, duracion_minutos=360, publico="familiar", hora_inicio="10:00"
    )
    actividades = resultado["actividades"]

    assert actividades, "debe haber al menos una actividad para un evento de 6 horas"
    assert actividades[0]["hora_inicio"] == "10:00"
    for anterior, siguiente in zip(actividades, actividades[1:]):
        assert siguiente["hora_inicio"] == anterior["hora_fin"]
    for orden, actividad in enumerate(actividades, start=1):
        assert actividad["orden"] == orden
        duracion = _minutos(actividad["hora_fin"]) - _minutos(actividad["hora_inicio"])
        assert duracion == actividad["duracion_minutos"]
    assert _minutos(actividades[-1]["hora_fin"]) == 10 * 60 + resultado["minutos_usados"]


def test_solo_incluye_actividades_del_publico_pedido():
    resultado = _armar(tipo_evento="tecnologico", duracion_minutos=480, publico="adulto")
    permitidas = {
        actividad["nombre"]
        for actividad in _ACTIVIDADES["tecnologico"]
        if "adulto" in actividad["publico"]
    }
    nombres = {actividad["nombre"] for actividad in resultado["actividades"]}
    assert nombres and nombres <= permitidas


def test_un_evento_de_seis_horas_deja_pocos_minutos_libres():
    """Con el catálogo ampliado, un evento largo no queda con horas vacías."""
    for tipo in TIPOS:
        resultado = _armar(tipo_evento=tipo, duracion_minutos=360, publico="familiar")
        assert resultado["minutos_libres"] < 120, tipo


def test_los_alias_de_publico_dan_el_mismo_programa():
    base = _armar(tipo_evento="infantil", duracion_minutos=180, publico="familiar")
    for alias in ("niños", "ninos", "infantil", "familia"):
        assert _armar(tipo_evento="infantil", duracion_minutos=180, publico=alias) == base


def test_tipo_con_tilde_y_mayusculas_se_reconoce():
    resultado = _armar(tipo_evento="  Tecnológico ", duracion_minutos=120, publico="Adulto")
    assert resultado["actividades"]


def test_si_ninguna_actividad_cabe_la_lista_viene_vacia_con_motivo():
    # El catálogo «infantil» solo tiene actividades para familias: para adultos no hay ninguna.
    resultado = _armar(tipo_evento="infantil", duracion_minutos=180, publico="adulto")
    assert resultado["actividades"] == []
    assert resultado["minutos_usados"] == 0
    assert resultado["motivo"] == "Ninguna actividad cabe en ese tiempo para ese público."


@pytest.mark.parametrize(
    "datos, fragmento",
    [
        ({"tipo_evento": "deportivo", "duracion_minutos": 120, "publico": "adulto"}, "no válido"),
        ({"tipo_evento": "cultural", "duracion_minutos": 120, "publico": "mascotas"}, "no válido"),
        ({"tipo_evento": "cultural", "duracion_minutos": 10, "publico": "adulto"}, "duración"),
        ({"tipo_evento": "cultural", "duracion_minutos": 600, "publico": "adulto"}, "duración"),
        (
            {"tipo_evento": "cultural", "duracion_minutos": 120, "publico": "adulto", "hora_inicio": "25:99"},
            "HH:MM",
        ),
    ],
)
def test_datos_invalidos_devuelven_lista_vacia_y_motivo(datos, fragmento):
    resultado = _armar(**datos)
    assert resultado["actividades"] == []
    assert resultado["minutos_usados"] == 0
    assert fragmento in resultado["motivo"]
