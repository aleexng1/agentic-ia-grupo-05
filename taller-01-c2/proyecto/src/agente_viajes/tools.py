"""Herramientas con datos ficticios de vuelos y hoteles."""

import unicodedata

from langchain_core.tools import tool


_VUELOS = {
    ("SCL", "LIM"): [
        {"aerolinea": "LATAM", "salida": "08:20", "llegada": "11:10", "precio_clp": 178000},
        {"aerolinea": "SKY Airline", "salida": "14:35", "llegada": "17:25", "precio_clp": 142000},
        {"aerolinea": "JetSMART", "salida": "19:10", "llegada": "22:00", "precio_clp": 129000},
    ],
    ("LIM", "SCL"): [
        {"aerolinea": "LATAM", "salida": "07:45", "llegada": "12:35", "precio_clp": 181000},
        {"aerolinea": "Sky Airline", "salida": "16:20", "llegada": "21:10", "precio_clp": 147000},
    ],
    ("SCL", "BOG"): [
        {"aerolinea": "LATAM", "salida": "06:50", "llegada": "12:05", "precio_clp": 254000},
        {"aerolinea": "Avianca", "salida": "13:40", "llegada": "18:55", "precio_clp": 278000},
    ],
    ("BOG", "SCL"): [
        {"aerolinea": "Avianca", "salida": "09:15", "llegada": "16:30", "precio_clp": 269000},
        {"aerolinea": "LATAM", "salida": "21:05", "llegada": "04:20", "precio_clp": 247000},
    ],
    ("SCL", "EZE"): [
        {"aerolinea": "LATAM", "salida": "07:30", "llegada": "09:35", "precio_clp": 119000},
        {"aerolinea": "JetSMART", "salida": "17:45", "llegada": "19:50", "precio_clp": 96000},
        {"aerolinea": "Aerolíneas Argentinas", "salida": "21:10", "llegada": "23:15", "precio_clp": 136000},
    ],
    ("EZE", "SCL"): [
        {"aerolinea": "LATAM", "salida": "10:20", "llegada": "12:25", "precio_clp": 122000},
        {"aerolinea": "Aerolíneas Argentinas", "salida": "18:50", "llegada": "20:55", "precio_clp": 131000},
    ],
    ("LIM", "BOG"): [
        {"aerolinea": "LATAM", "salida": "08:10", "llegada": "11:20", "precio_clp": 162000},
        {"aerolinea": "Avianca", "salida": "15:25", "llegada": "18:35", "precio_clp": 174000},
    ],
    ("BOG", "LIM"): [
        {"aerolinea": "Avianca", "salida": "07:55", "llegada": "11:05", "precio_clp": 169000},
        {"aerolinea": "LATAM", "salida": "20:40", "llegada": "23:50", "precio_clp": 158000},
    ],
    ("LIM", "EZE"): [
        {"aerolinea": "LATAM", "salida": "09:00", "llegada": "15:10", "precio_clp": 286000},
        {"aerolinea": "Aerolíneas Argentinas", "salida": "22:15", "llegada": "04:25", "precio_clp": 302000},
    ],
    ("EZE", "LIM"): [
        {"aerolinea": "LATAM", "salida": "08:35", "llegada": "12:45", "precio_clp": 291000},
        {"aerolinea": "Aerolíneas Argentinas", "salida": "19:30", "llegada": "23:40", "precio_clp": 297000},
    ],
    ("BOG", "EZE"): [
        {"aerolinea": "Avianca", "salida": "07:20", "llegada": "15:05", "precio_clp": 315000},
        {"aerolinea": "LATAM", "salida": "21:10", "llegada": "04:55", "precio_clp": 298000},
    ],
    ("EZE", "BOG"): [
        {"aerolinea": "Avianca", "salida": "09:40", "llegada": "15:25", "precio_clp": 309000},
        {"aerolinea": "LATAM", "salida": "18:15", "llegada": "00:00", "precio_clp": 294000},
    ],
}

_HOTELES = {
    "santiago": [
        {"nombre": "Hotel Providencia Plaza", "sector": "Providencia", "estrellas": 4, "precio_noche_clp": 89000},
        {"nombre": "Casa Lastarria", "sector": "Lastarria", "estrellas": 3, "precio_noche_clp": 67500},
        {"nombre": "Andes Centro Hotel", "sector": "Centro", "estrellas": 4, "precio_noche_clp": 76000},
    ],
    "lima": [
        {"nombre": "Miraflores del Parque", "sector": "Miraflores", "estrellas": 4, "precio_noche_clp": 82000},
        {"nombre": "Casa Barranco", "sector": "Barranco", "estrellas": 3, "precio_noche_clp": 59000},
        {"nombre": "Costa Verde Suites", "sector": "Miraflores", "estrellas": 5, "precio_noche_clp": 128000},
    ],
    "bogota": [
        {"nombre": "Hotel Parque 93", "sector": "Chicó", "estrellas": 4, "precio_noche_clp": 94000},
        {"nombre": "La Candelaria Inn", "sector": "La Candelaria", "estrellas": 3, "precio_noche_clp": 54000},
        {"nombre": "Andino Suites", "sector": "Zona T", "estrellas": 5, "precio_noche_clp": 139000},
    ],
    "buenos aires": [
        {"nombre": "Palermo Soho Hotel", "sector": "Palermo", "estrellas": 4, "precio_noche_clp": 87000},
        {"nombre": "San Telmo Casa", "sector": "San Telmo", "estrellas": 3, "precio_noche_clp": 62000},
        {"nombre": "Recoleta Grand", "sector": "Recoleta", "estrellas": 5, "precio_noche_clp": 145000},
    ],
}

_CIUDADES_POR_CODIGO = {
    "SCL": "santiago",
    "LIM": "lima",
    "BOG": "bogota",
    "EZE": "buenos aires",
}


def _normalizar(texto: str) -> str:
    """Pasa texto a minúsculas y elimina tildes y espacios exteriores."""
    sin_tildes = unicodedata.normalize("NFKD", texto.strip().casefold())
    return "".join(letra for letra in sin_tildes if not unicodedata.combining(letra))


@tool
def buscar_vuelos(origen: str, destino: str, fecha: str) -> list[dict]:
    """Busca vuelos ficticios diarios entre aeropuertos SCL, LIM, BOG y EZE.

    La fecha indicada se incorpora a los resultados; horarios y tarifas son
    datos de muestra y no representan disponibilidad ni una reserva real.
    """
    ruta = (origen.strip().upper(), destino.strip().upper())
    vuelos = _VUELOS.get(ruta, [])
    return [
        {
            "origen": ruta[0],
            "destino": ruta[1],
            "fecha": fecha.strip(),
            **vuelo,
        }
        for vuelo in vuelos
    ]


@tool
def buscar_hoteles(ciudad: str, noches: int) -> list[dict]:
    """Busca hoteles ficticios en Santiago, Lima, Bogotá o Buenos Aires."""
    ciudad_normalizada = _normalizar(ciudad)
    ciudad_normalizada = _CIUDADES_POR_CODIGO.get(
        ciudad_normalizada.upper(), ciudad_normalizada
    )
    hoteles = _HOTELES.get(ciudad_normalizada, [])
    if not hoteles or noches < 1:
        return []

    return [
        {
            "ciudad": ciudad_normalizada,
            **hotel,
            "noches": noches,
            "precio_total_clp": hotel["precio_noche_clp"] * noches,
        }
        for hotel in hoteles
    ]
