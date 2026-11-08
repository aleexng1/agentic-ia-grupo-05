"""Herramientas con datos ficticios de restaurantes."""

import unicodedata

from crewai.tools import tool


_RESTAURANTES = {
    "LIM": [
        {"nombre": "La Mar Cevichería", "zona": "Miraflores", "tipo_comida": "Peruana y mariscos", "precio_medio_clp": 24000, "horario": "Lun–sáb 12:00–17:00"},
        {"nombre": "Isolina", "zona": "Barranco", "tipo_comida": "Criolla peruana", "precio_medio_clp": 19000, "horario": "Mar–dom 12:00–23:00"},
        {"nombre": "Rafael", "zona": "Miraflores", "tipo_comida": "Peruana contemporánea", "precio_medio_clp": 38000, "horario": "Lun–sáb 13:00–23:00"},
        {"nombre": "Hanzo", "zona": "San Isidro", "tipo_comida": "Japonesa y nikkei", "precio_medio_clp": 30000, "horario": "Lun–sáb 12:30–23:00"},
        {"nombre": "Panchita", "zona": "Miraflores", "tipo_comida": "Parrilla peruana", "precio_medio_clp": 22000, "horario": "Todos los días 12:00–23:00"},
    ],
    "BOG": [
        {"nombre": "Andrés Carne de Res", "zona": "Chía", "tipo_comida": "Parrilla colombiana", "precio_medio_clp": 42000, "horario": "Mié–dom 12:00–01:00"},
        {"nombre": "Leo", "zona": "Chapinero", "tipo_comida": "Colombiana de autor", "precio_medio_clp": 68000, "horario": "Mar–sáb 12:00–22:00"},
        {"nombre": "Mini-Mal", "zona": "Chapinero Alto", "tipo_comida": "Colombiana contemporánea", "precio_medio_clp": 35000, "horario": "Mar–sáb 12:00–21:30"},
        {"nombre": "Criterion", "zona": "Chicó", "tipo_comida": "Francesa", "precio_medio_clp": 72000, "horario": "Lun–sáb 12:00–22:00"},
        {"nombre": "Prudencia", "zona": "La Candelaria", "tipo_comida": "Colombiana de temporada", "precio_medio_clp": 29000, "horario": "Mar–sáb 12:00–16:00"},
    ],
    "EZE": [
        {"nombre": "Don Julio", "zona": "Palermo", "tipo_comida": "Parrilla argentina", "precio_medio_clp": 52000, "horario": "Todos los días 12:00–00:00"},
        {"nombre": "La Cabrera", "zona": "Palermo Soho", "tipo_comida": "Parrilla argentina", "precio_medio_clp": 39000, "horario": "Todos los días 12:00–00:00"},
        {"nombre": "El Preferido de Palermo", "zona": "Palermo", "tipo_comida": "Argentina y bodegón", "precio_medio_clp": 33000, "horario": "Mar–dom 12:00–00:00"},
        {"nombre": "i Latina", "zona": "Villa Crespo", "tipo_comida": "Latinoamericana de autor", "precio_medio_clp": 76000, "horario": "Mar–sáb 19:30–23:00"},
        {"nombre": "Sarkis", "zona": "Villa Crespo", "tipo_comida": "Armenia y mediterránea", "precio_medio_clp": 21000, "horario": "Todos los días 12:00–00:00"},
    ],
}

_CIUDADES = {
    "LIM": "Lima",
    "LIMA": "Lima",
    "BOG": "Bogotá",
    "BOGOTA": "Bogotá",
    "EZE": "Buenos Aires",
    "BUENOS AIRES": "Buenos Aires",
}


def _normalizar(texto: str) -> str:
    """Normaliza tildes y mayúsculas para comparar entradas."""
    sin_tildes = unicodedata.normalize("NFKD", texto.strip().casefold())
    return "".join(letra for letra in sin_tildes if not unicodedata.combining(letra))


@tool
def buscar_restaurantes(ciudad: str, tipo: str) -> list[dict]:
    """Busca restaurantes ficticios por código de ciudad y tipo de comida.

    Ciudades disponibles: LIM (Lima), BOG (Bogotá) y EZE (Buenos Aires).
    """
    ciudad_normalizada = _normalizar(ciudad)
    codigo = next(
        (
            codigo
            for codigo, nombre_ciudad in _CIUDADES.items()
            if _normalizar(codigo) == ciudad_normalizada
            or _normalizar(nombre_ciudad) == ciudad_normalizada
        ),
        None,
    )
    if codigo is None:
        return []

    restaurantes = _RESTAURANTES.get(codigo, [])
    tipo_normalizado = _normalizar(tipo).replace("comida ", "")
    if tipo_normalizado in ("", "cualquiera", "cualquier tipo", "todos", "todas"):
        return [dict(restaurante, ciudad=_CIUDADES[codigo]) for restaurante in restaurantes]

    encontrados = []
    for restaurante in restaurantes:
        tipo_restaurante = _normalizar(restaurante["tipo_comida"])
        if tipo_normalizado in tipo_restaurante or tipo_restaurante in tipo_normalizado:
            encontrados.append(dict(restaurante, ciudad=_CIUDADES[codigo]))
    return encontrados


@tool
def detalle_restaurante(nombre: str) -> dict | list:
    """Devuelve zona, cocina, precio medio y horario de un restaurante."""
    nombre_normalizado = _normalizar(nombre)
    for codigo, restaurantes in _RESTAURANTES.items():
        for restaurante in restaurantes:
            nombre_restaurante = _normalizar(restaurante["nombre"])
            if nombre_normalizado == nombre_restaurante or nombre_normalizado in nombre_restaurante:
                return dict(restaurante, ciudad=_CIUDADES[codigo])
    return []
