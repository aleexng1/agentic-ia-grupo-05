"""Pruebas de la herramienta buscar_recintos (no usan el modelo ni la clave)."""

import pytest

from src.agente_alex import tools
from src.agente_alex.tools import buscar_recintos


def buscar(tipo_evento, personas, espacio="cualquiera"):
    """Llama a la herramienta igual que lo hace el agente."""
    return buscar_recintos.invoke(
        {"tipo_evento": tipo_evento, "personas": personas, "espacio": espacio}
    )


def nombres(resultado):
    return [recinto["nombre"] for recinto in resultado["recintos"]]


# --- Rango de personas -------------------------------------------------------


@pytest.mark.parametrize("personas", [0, 9, 501, 2000, -5])
def test_fuera_de_rango_responde_en_una_linea(personas):
    resultado = buscar("tecnologico", personas)
    assert resultado["recintos"] == []
    assert "10 a 500" in resultado["motivo"]
    assert "\n" not in resultado["motivo"]


@pytest.mark.parametrize("personas", [10, 500])
def test_bordes_del_rango_si_se_aceptan(personas):
    resultado = buscar("cultural", personas)
    assert resultado["recintos"], resultado.get("motivo")


# --- Holgura del 10 % --------------------------------------------------------


def test_holgura_justa_se_acepta():
    # Centro Comunitario San Teodoro: capacidad 40. 36 × 1,10 = 39,6 → cabe.
    assert "Centro Comunitario San Teodoro" in nombres(buscar("infantil", 36, "interior"))


def test_sin_holgura_se_descarta():
    # 37 × 1,10 = 40,7 → ya no cabe en una capacidad de 40.
    resultado = buscar("infantil", 37, "interior")
    assert "Centro Comunitario San Teodoro" not in nombres(resultado)


def test_holgura_exacta_sin_error_de_decimales():
    # 100 × 1,10 en decimales da 110,00000000000001; la cuenta con enteros no falla.
    # Ningún recinto entregado puede tener menos capacidad que la mínima.
    resultado = buscar("tecnologico", 100)
    assert resultado["capacidad_minima"] == 110
    for recinto in resultado["recintos"]:
        assert recinto["capacidad_maxima"] * 100 >= 100 * 110


def test_todos_los_recintos_cumplen_la_holgura():
    for personas in (10, 55, 150, 273, 450):
        for recinto in buscar("cultural", personas)["recintos"]:
            assert recinto["capacidad_maxima"] >= personas * 1.10 - 1e-9


# --- Cuentas, orden y "queda grande" -----------------------------------------


def test_feria_tecnologica_150_personas():
    resultado = buscar("tecnologico", 150)
    assert len(resultado["recintos"]) == 3
    primero = resultado["recintos"][0]
    assert primero["nombre"] == "Salón Cumbre del Hotel Alto Quillay"
    assert primero["ocupacion_pct"] == 83.3        # 150 / 180
    assert primero["m2_por_persona"] == 2.0        # 300 / 150
    assert primero["stands_estimados"] == 13       # 300 × 0,40 / 9
    assert "precio" not in str(resultado).lower()


def test_ordena_por_ocupacion_cercana_al_75():
    recintos = buscar("tecnologico", 150)["recintos"]
    distancias = [abs(r["ocupacion_pct"] - 75) for r in recintos]
    assert distancias == sorted(distancias)


def test_aviso_queda_grande():
    # 10 personas en la explanada de 500: ocupación 2 %.
    resultado = buscar("infantil", 10, "exterior")
    assert resultado["recintos"]
    for recinto in resultado["recintos"]:
        assert recinto["ocupacion_pct"] < 35
        assert recinto["aviso"].startswith("queda grande")


def test_sin_aviso_cuando_el_ajuste_es_bueno():
    primero = buscar("tecnologico", 150)["recintos"][0]
    assert "aviso" not in primero


def test_maximo_tres_resultados():
    assert len(buscar("cultural", 20)["recintos"]) <= 3


# --- Sinónimos y texto libre -------------------------------------------------


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("tech", "tecnologico"),
        ("Tecnológico", "tecnologico"),
        ("feria tecnológica", "tecnologico"),
        ("GASTRONOMÍA", "gastronomico"),
        ("niños", "infantil"),
        ("Cultura", "cultural"),
    ],
)
def test_sinonimos_de_tipo(texto, esperado):
    assert buscar(texto, 80)["tipo_evento"] == esperado


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("afuera", "exterior"),
        ("aire libre", "exterior"),
        ("al aire libre", "exterior"),
        ("Exterior", "exterior"),
        ("adentro", "interior"),
        ("bajo techo", "interior"),
        ("", "cualquiera"),
        ("interior o exterior", "cualquiera"),
    ],
)
def test_sinonimos_de_espacio(texto, esperado):
    resultado = buscar("infantil", 80, texto)
    assert resultado["espacio"] == esperado
    if esperado != "cualquiera":
        assert all(r["espacio"] == esperado for r in resultado["recintos"])


# --- Sin resultados -----------------------------------------------------------


def test_sin_resultados_sugiere_otro_espacio():
    # Tecnológica de 400 al aire libre: la carpa (300) queda chica, pero hay interiores.
    resultado = buscar("tecnologico", 400, "exterior")
    assert resultado["recintos"] == []
    assert "interior" in resultado["motivo"]
    assert "\n" not in resultado["motivo"]


def test_sin_resultados_sugiere_menos_personas(monkeypatch):
    # Con el catálogo real siempre hay alternativa; se deja solo la carpa (300) para
    # probar el caso en que ni cambiando de espacio alcanza.
    carpa = [r for r in tools._RECINTOS if r["nombre"] == "Carpa Modular Bahía Pizarra"]
    monkeypatch.setattr(tools, "_RECINTOS", carpa)
    resultado = buscar("tecnologico", 300, "exterior")
    assert resultado["recintos"] == []
    assert "272 personas o menos" in resultado["motivo"]  # 300 // 1,10 = 272
    assert "\n" not in resultado["motivo"]


def test_tipo_desconocido():
    resultado = buscar("deportivo", 100)
    assert resultado["recintos"] == []
    assert "tecnologico" in resultado["motivo"]


def test_espacio_desconocido():
    resultado = buscar("cultural", 100, "en la luna")
    assert resultado["recintos"] == []
    assert "interior" in resultado["motivo"]


# --- Nunca lanza un error -----------------------------------------------------


@pytest.mark.parametrize(
    "tipo_evento, personas, espacio",
    [
        (None, None, None),
        ("", "", ""),
        ("tecnologico", "ciento cincuenta", "interior"),
        ("tecnologico", "150", "interior"),
        ("tecnologico", 150.7, "interior"),
        ("tecnologico", True, "interior"),
        (123, [1, 2], {"a": 1}),
    ],
)
def test_nunca_lanza_error(tipo_evento, personas, espacio):
    resultado = buscar_recintos.func(tipo_evento, personas, espacio)
    assert isinstance(resultado, dict)
    assert "recintos" in resultado
    if not resultado["recintos"]:
        assert resultado["motivo"]
