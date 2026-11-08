"""Pruebas de la herramienta armar_catering (no usan el modelo ni la clave)."""

from src.agente_sebastian.tools import armar_catering


def _armar(**datos):
    """Llama a la herramienta como lo hace el modelo."""
    return armar_catering.invoke(datos)


def _platos(servicio):
    """Devuelve un diccionario nombre → cantidad de los platos de un servicio."""
    return {plato["nombre"]: plato["cantidad"] for plato in servicio["platos"]}


def test_feria_tecnologica_de_cuatro_horas_con_veganos():
    resultado = _armar(
        tipo_evento="tecnologico",
        personas=150,
        duracion_minutos=240,
        hora_inicio="10:00",
        restricciones="12 veganos",
    )
    servicios = resultado["servicios"]
    assert [(s["hora"], s["servicio"]) for s in servicios] == [
        ("11:00", "Coffee break"),
        ("13:30", "Box lunch"),
    ]
    # 150 - 12 = 138 personas con menú general; 138 × 2 × 1,1 = 303,6 → 304.
    assert servicios[0]["personas_menu_general"] == 138
    assert _platos(servicios[0])["Sándwich de miga"] == 304
    # Las bebidas son para todos: 150 × 1 × 1,1 = 165.
    assert servicios[0]["bebidas"][0]["cantidad"] == 165
    vegano = servicios[0]["dietas"][0]
    assert vegano["dieta"] == "vegano"
    assert vegano["personas"] == 12
    # 12 × 2 × 1,1 = 26,4 → 27.
    assert vegano["platos"][0]["cantidad"] == 27
    # Agua: 150 × 0,5 L × 2 bloques × 1,1 = 165 L.
    assert resultado["agua"]["litros"] == 165
    assert resultado["hora_fin"] == "14:00"


def test_margen_sin_errores_de_redondeo():
    # 100 × 1 × 1,1 da 110 exacto; con decimales binarios saldría 111.
    resultado = _armar(tipo_evento="cultural", personas=100, duracion_minutos=120, hora_inicio="09:00")
    assert resultado["servicios"][0]["bebidas"][0]["cantidad"] == 110


def test_evento_corto_lleva_un_solo_servicio_al_inicio():
    resultado = _armar(tipo_evento="cultural", personas=40, duracion_minutos=60, hora_inicio="12:30")
    servicios = resultado["servicios"]
    assert len(servicios) == 1
    assert servicios[0]["hora"] == "12:30"
    # Aunque sea mediodía, un evento de una hora no lleva almuerzo.
    assert servicios[0]["servicio"] == "Coffee break"


def test_feria_infantil_de_tarde_lleva_colacion():
    resultado = _armar(tipo_evento="infantil", personas=80, duracion_minutos=180, hora_inicio="15:00")
    assert [(s["hora"], s["servicio"]) for s in resultado["servicios"]] == [("16:00", "Colación infantil")]


def test_evento_de_noche_lleva_coctel():
    resultado = _armar(tipo_evento="tecnologico", personas=60, duracion_minutos=180, hora_inicio="18:00")
    assert [(s["hora"], s["servicio"]) for s in resultado["servicios"]] == [("19:00", "Cóctel frío")]


def test_jornada_completa_tiene_un_solo_almuerzo():
    resultado = _armar(tipo_evento="gastronomico", personas=200, duracion_minutos=480, hora_inicio="10:00")
    assert [(s["hora"], s["servicio"]) for s in resultado["servicios"]] == [
        ("11:00", "Coffee break"),
        ("13:30", "Ronda de food trucks"),
        ("16:00", "Coffee break"),
    ]
    # 200 × 0,5 L × 4 bloques × 1,1 = 440 L.
    assert resultado["agua"]["litros"] == 440


def test_reconoce_alias_y_texto_libre():
    resultado = _armar(
        tipo_evento="Feria Tecnológica",
        personas=50,
        duracion_minutos=120,
        restricciones="5 celíacos y 3 intolerantes a la lactosa",
    )
    assert resultado["tipo_evento"] == "tecnologico"
    dietas = {d["dieta"]: d["personas"] for d in resultado["servicios"][0]["dietas"]}
    assert dietas == {"sin gluten": 5, "sin lactosa": 3}
    assert resultado["servicios"][0]["personas_menu_general"] == 42


def test_dieta_sin_cantidad_se_estima_y_se_avisa():
    resultado = _armar(tipo_evento="cultural", personas=45, duracion_minutos=120, restricciones="vegetariano")
    vegetariano = resultado["servicios"][0]["dietas"][0]
    # El 10 % de 45 es 4,5 → 5 personas.
    assert vegetariano == {**vegetariano, "dieta": "vegetariano", "personas": 5}
    assert any("se estimó el 10 %" in nota for nota in resultado["notas"])


def test_restriccion_desconocida_se_informa():
    resultado = _armar(tipo_evento="cultural", personas=30, duracion_minutos=120, restricciones="kosher")
    assert resultado["restricciones_no_reconocidas"] == ["kosher"]
    assert any("kosher" in nota for nota in resultado["notas"])


def test_hora_por_defecto_es_diez():
    resultado = _armar(tipo_evento="cultural", personas=30, duracion_minutos=120)
    assert resultado["hora_inicio"] == "10:00"


def test_datos_invalidos_devuelven_motivo_sin_error():
    casos = [
        dict(tipo_evento="deportivo", personas=50, duracion_minutos=120),
        dict(tipo_evento="cultural", personas=5, duracion_minutos=120),
        dict(tipo_evento="cultural", personas=50, duracion_minutos=600),
        dict(tipo_evento="cultural", personas=50, duracion_minutos=120, hora_inicio="25:00"),
        dict(tipo_evento="cultural", personas=50, duracion_minutos=240, hora_inicio="22:00"),
        dict(tipo_evento="cultural", personas=20, duracion_minutos=120, restricciones="15 veganos, 10 sin gluten"),
    ]
    for caso in casos:
        resultado = _armar(**caso)
        assert resultado["servicios"] == []
        assert resultado["motivo"]


def test_nunca_incluye_precios():
    resultado = _armar(
        tipo_evento="gastronomico",
        personas=300,
        duracion_minutos=480,
        hora_inicio="09:00",
        restricciones="20 veganos, 10 sin gluten, 5 vegetarianos, 5 sin lactosa",
    )
    # Se revisan los datos (servicios y agua); las notas dicen "sin precios" a propósito.
    texto = str([resultado["servicios"], resultado["agua"]]).casefold()
    for palabra in ("$", "precio", "costo", "clp", "peso"):
        assert palabra not in texto
