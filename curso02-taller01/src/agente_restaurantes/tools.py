"""Herramientas del agente de restaurantes. Los datos son inventados (no hay internet)."""

import json
import unicodedata

from crewai.tools import tool

# ciudad (en minúsculas y sin tildes) -> nombre para mostrar
CIUDADES = {"lima": "Lima", "bogota": "Bogotá", "buenos aires": "Buenos Aires"}
CODIGO_A_CIUDAD = {"lim": "lima", "bog": "bogota", "eze": "buenos aires"}

# ciudad -> lista de (nombre, zona, tipo de comida, precio medio por persona en CLP, horario, plato estrella)
RESTAURANTES = {
    "lima": [
        ("La Brisa Marina", "Miraflores", "cevichería", 28000, "12:00-17:00", "ceviche clásico"),
        ("Casa Huaca Viva", "Miraflores", "peruana", 32000, "13:00-23:00", "lomo saltado"),
        ("Nikkei Barranco", "Barranco", "nikkei", 58000, "13:00-22:00", "nigiri de anticucho"),
        ("Picantería del Puente", "Barranco", "criolla", 21000, "12:00-21:00", "ají de gallina"),
        ("Napoli San Isidro", "San Isidro", "italiana", 24000, "12:30-23:30", "pizza margarita"),
    ],
    "bogota": [
        ("Ajiaco de la Candelaria", "La Candelaria", "colombiana", 14000, "11:30-18:00", "ajiaco santafereño"),
        ("Brasa Zona G", "Zona G", "parrilla", 38000, "12:00-23:00", "picaña a la brasa"),
        ("Café Chapinero Alto", "Chapinero", "cafetería y brunch", 16000, "07:30-17:00", "arepa de huevo"),
        ("Sushi Usaquén", "Usaquén", "japonesa", 34000, "12:00-22:30", "roll de mango"),
        ("Fogón Paisa", "Zona T", "colombiana", 26000, "12:00-22:00", "bandeja paisa"),
    ],
    "buenos aires": [
        ("Parrilla Don Aurelio", "Palermo", "parrilla argentina", 36000, "20:00-00:30", "bife de chorizo"),
        ("Trattoria del Puerto", "Puerto Madero", "italiana", 42000, "12:30-23:30", "ñoquis con salsa"),
        ("Empanadas de la Boca", "La Boca", "argentina informal", 9000, "11:00-22:00", "empanada de carne"),
        ("Café Recoleta Vieja", "Recoleta", "cafetería", 12000, "08:00-20:00", "medialunas"),
        ("Pizza Rosario", "San Telmo", "pizzería", 15000, "19:00-01:00", "fugazzeta"),
    ],
}

SIN_RESULTADOS = "sin resultados"
TIPOS_CUALQUIERA = {"", "todos", "todo", "cualquiera", "cualquier tipo", "cualquier"}


def _normalizar(texto):
    """Minúsculas, sin tildes y sin espacios sobrantes."""
    sin_tildes = unicodedata.normalize("NFD", str(texto))
    sin_tildes = "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn")
    return sin_tildes.strip().lower()


def _raiz(palabra):
    """Quita la vocal final para que 'peruano' encuentre 'peruana' (y 'japonés' a 'japonesa')."""
    palabra = _normalizar(palabra)
    return palabra[:-1] if palabra and palabra[-1] in "aeos" else palabra


def _clave_ciudad(ciudad):
    clave = _normalizar(ciudad)
    return CODIGO_A_CIUDAD.get(clave, clave)


def _como_dict(ciudad, fila):
    nombre, zona, tipo, precio, horario, plato = fila
    return {
        "nombre": nombre,
        "ciudad": CIUDADES[ciudad],
        "zona": zona,
        "tipo": tipo,
        "precio_medio_clp": precio,
        "horario": horario,
        "plato_estrella": plato,
    }


@tool("buscar_restaurantes")
def buscar_restaurantes(ciudad: str, tipo: str = "") -> str:
    """Busca restaurantes en una ciudad (Lima, Bogotá o Buenos Aires; también LIM, BOG, EZE).

    Args:
        ciudad: nombre de la ciudad o código de aeropuerto, por ejemplo "Lima" o "LIM".
        tipo: tipo de comida que se busca, por ejemplo "peruana", "parrilla" o "italiana".
            Si no importa, déjalo vacío.

    Devuelve una lista en JSON con nombre, zona, tipo de comida, precio medio por
    persona en pesos chilenos (CLP) y horario. Si no hay resultados, devuelve el
    texto "sin resultados".
    """
    clave = _clave_ciudad(ciudad)
    filas = RESTAURANTES.get(clave)
    if filas is None:
        return f"{SIN_RESULTADOS}: no tengo restaurantes en '{ciudad}'. Ciudades disponibles: Lima, Bogotá y Buenos Aires."
    if _normalizar(tipo) not in TIPOS_CUALQUIERA:
        raiz = _raiz(tipo)
        filas = [f for f in filas if raiz in _normalizar(f"{f[2]} {f[5]} {f[1]}")]
    if not filas:
        return f"{SIN_RESULTADOS}: no hay restaurantes de '{tipo}' en {CIUDADES[clave]}."
    return json.dumps([_como_dict(clave, f) for f in filas], ensure_ascii=False)


@tool("detalle_restaurante")
def detalle_restaurante(nombre: str) -> str:
    """Da el detalle de un restaurante a partir de su nombre (o parte de él).

    Args:
        nombre: nombre del restaurante, por ejemplo "Brasa Zona G".

    Devuelve en JSON la ciudad, zona, tipo de comida, precio medio por persona en
    pesos chilenos (CLP), horario y plato estrella. Si no lo encuentra, devuelve el
    texto "sin resultados".
    """
    buscado = _normalizar(nombre)
    if buscado:
        for ciudad, filas in RESTAURANTES.items():
            for fila in filas:
                if buscado in _normalizar(fila[0]):
                    return json.dumps(_como_dict(ciudad, fila), ensure_ascii=False)
    return f"{SIN_RESULTADOS}: no encontré ningún restaurante llamado '{nombre}'."


HERRAMIENTAS = [buscar_restaurantes, detalle_restaurante]
