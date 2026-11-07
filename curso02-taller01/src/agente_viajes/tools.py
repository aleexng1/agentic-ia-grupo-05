"""Herramientas del agente de viajes. Los datos son inventados (no hay internet)."""

import unicodedata

from langchain_core.tools import tool

# (origen, destino) -> lista de (aerolínea, salida, llegada, precio en CLP)
VUELOS = {
    ("SCL", "LIM"): [
        ("LATAM", "07:15", "09:50", 142000),
        ("Sky Airline", "13:40", "16:15", 118000),
        ("JetSMART", "20:05", "22:40", 99000),
    ],
    ("LIM", "SCL"): [
        ("LATAM", "10:30", "15:05", 148000),
        ("Sky Airline", "17:20", "21:55", 121000),
    ],
    ("SCL", "BOG"): [
        ("LATAM", "06:00", "10:35", 265000),
        ("Avianca", "14:10", "18:45", 248000),
        ("Sky Airline", "23:30", "04:05", 219000),
    ],
    ("BOG", "SCL"): [
        ("LATAM", "09:20", "17:00", 272000),
        ("Avianca", "21:45", "05:25", 251000),
    ],
    ("SCL", "EZE"): [
        ("LATAM", "08:00", "10:00", 98000),
        ("Aerolíneas Argentinas", "12:30", "14:30", 105000),
        ("JetSMART", "18:15", "20:15", 79000),
    ],
    ("EZE", "SCL"): [
        ("LATAM", "11:10", "13:10", 101000),
        ("Aerolíneas Argentinas", "16:45", "18:45", 109000),
    ],
    ("LIM", "BOG"): [
        ("Avianca", "07:50", "10:25", 156000),
        ("LATAM", "15:00", "17:35", 163000),
    ],
    ("BOG", "LIM"): [
        ("Avianca", "09:05", "11:40", 159000),
        ("LATAM", "18:30", "21:05", 166000),
        ("Sky Airline", "22:15", "00:50", 138000),
    ],
    ("LIM", "EZE"): [
        ("LATAM", "05:45", "11:00", 231000),
        ("Aerolíneas Argentinas", "13:20", "18:35", 244000),
    ],
    ("EZE", "LIM"): [
        ("LATAM", "07:30", "12:25", 236000),
        ("Aerolíneas Argentinas", "19:00", "23:55", 249000),
    ],
    ("BOG", "EZE"): [
        ("Avianca", "06:40", "14:30", 318000),
        ("Aerolíneas Argentinas", "11:55", "19:45", 335000),
        ("LATAM", "22:10", "06:00", 297000),
    ],
    ("EZE", "BOG"): [
        ("Avianca", "08:15", "13:25", 322000),
        ("LATAM", "20:40", "01:50", 301000),
    ],
}

# ciudad (en minúsculas y sin tildes) -> lista de (hotel, estrellas, precio por noche en CLP)
HOTELES = {
    "santiago": [
        ("Hotel Plaza Central", 4, 78000),
        ("Hostal Barrio Lastarria", 3, 42000),
        ("Gran Hotel Costanera", 5, 135000),
    ],
    "lima": [
        ("Hotel Miraflores Park", 4, 69000),
        ("Casa Barranco", 3, 38000),
        ("Gran Hotel San Isidro", 5, 118000),
    ],
    "bogota": [
        ("Hotel Chapinero Real", 4, 61000),
        ("Posada La Candelaria", 3, 33000),
    ],
    "buenos aires": [
        ("Hotel Palermo Soho", 4, 72000),
        ("Hostal San Telmo", 3, 36000),
        ("Gran Hotel Recoleta", 5, 126000),
    ],
}

# Para entender "Santiago", "scl", etc. con el mismo diccionario.
CODIGO_A_CIUDAD = {"scl": "santiago", "lim": "lima", "bog": "bogota", "eze": "buenos aires"}


def _normalizar(texto):
    """Minúsculas, sin tildes y sin espacios sobrantes."""
    sin_tildes = unicodedata.normalize("NFD", str(texto))
    sin_tildes = "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn")
    return sin_tildes.strip().lower()


@tool
def buscar_vuelos(origen: str, destino: str, fecha: str) -> list[dict]:
    """Busca vuelos entre dos aeropuertos usando códigos de tres letras (SCL, LIM, BOG, EZE).

    Args:
        origen: código del aeropuerto de salida, por ejemplo SCL.
        destino: código del aeropuerto de llegada, por ejemplo LIM.
        fecha: fecha del vuelo en formato AAAA-MM-DD.

    Devuelve una lista de vuelos con aerolínea, horario y precio en pesos chilenos
    (CLP). Si la ruta no existe, devuelve una lista vacía.
    """
    ruta = (str(origen).strip().upper(), str(destino).strip().upper())
    return [
        {
            "origen": ruta[0],
            "destino": ruta[1],
            "fecha": fecha,
            "aerolinea": aerolinea,
            "salida": salida,
            "llegada": llegada,
            "precio_clp": precio,
        }
        for aerolinea, salida, llegada, precio in VUELOS.get(ruta, [])
    ]


@tool
def buscar_hoteles(ciudad: str, noches: int) -> list[dict]:
    """Busca hoteles en una ciudad (Santiago, Lima, Bogotá o Buenos Aires).

    Args:
        ciudad: nombre de la ciudad.
        noches: cantidad de noches de estadía (un número entero mayor a cero).

    Devuelve una lista de hoteles con estrellas, precio por noche y total en pesos
    chilenos (CLP). Si la ciudad no existe, devuelve una lista vacía.
    """
    clave = _normalizar(ciudad)
    clave = CODIGO_A_CIUDAD.get(clave, clave)
    try:
        noches = int(noches)
    except (TypeError, ValueError):
        return []
    if noches < 1:
        return []
    return [
        {
            "ciudad": "Bogotá" if clave == "bogota" else clave.title(),
            "hotel": nombre,
            "estrellas": estrellas,
            "noches": noches,
            "precio_noche_clp": precio,
            "total_clp": precio * noches,
        }
        for nombre, estrellas, precio in HOTELES.get(clave, [])
    ]


HERRAMIENTAS = [buscar_vuelos, buscar_hoteles]
