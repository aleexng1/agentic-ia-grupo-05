"""Herramientas con datos ficticios de recintos para ferias y eventos.

Todos los recintos y comunas son inventados. No hay precios: este agente solo ve
capacidad y características del lugar.
"""

import unicodedata

from langchain_core.tools import tool


_RECINTOS = [
    {
        "nombre": "Salón Cumbre del Hotel Alto Quillay",
        "comuna": "Alto Quillay",
        "espacio": "interior",
        "capacidad_maxima": 180,
        "m2": 300,
        "tipos_evento": ["tecnologico", "cultural", "gastronomico"],
        "estacionamientos": 60,
        "accesible": True,
        "permite_servicio_comida": True,
    },
    {
        "nombre": "Centro de Convenciones Puerto Ciruelo",
        "comuna": "Puerto Ciruelo",
        "espacio": "interior",
        "capacidad_maxima": 600,
        "m2": 1800,
        "tipos_evento": ["tecnologico", "gastronomico", "cultural", "infantil"],
        "estacionamientos": 250,
        "accesible": True,
        "permite_servicio_comida": True,
    },
    {
        "nombre": "Gimnasio Municipal de Valdelumbre",
        "comuna": "Valdelumbre",
        "espacio": "interior",
        "capacidad_maxima": 400,
        "m2": 900,
        "tipos_evento": ["infantil", "cultural", "tecnologico"],
        "estacionamientos": 40,
        "accesible": True,
        "permite_servicio_comida": False,
    },
    {
        "nombre": "Galpón Cultural Rinconada Azul",
        "comuna": "Rinconada Azul",
        "espacio": "interior",
        "capacidad_maxima": 250,
        "m2": 600,
        "tipos_evento": ["cultural", "gastronomico", "tecnologico"],
        "estacionamientos": 15,
        "accesible": False,
        "permite_servicio_comida": True,
    },
    {
        "nombre": "Explanada del Parque Lomas de Arrayán",
        "comuna": "Lomas de Arrayán",
        "espacio": "exterior",
        "capacidad_maxima": 500,
        "m2": 3000,
        "tipos_evento": ["gastronomico", "cultural", "infantil"],
        "estacionamientos": 80,
        "accesible": True,
        "permite_servicio_comida": True,
    },
    {
        "nombre": "Colegio Villa Cuarzo (patio techado y salas)",
        "comuna": "Villa Cuarzo",
        "espacio": "interior",
        "capacidad_maxima": 120,
        "m2": 450,
        "tipos_evento": ["infantil", "tecnologico", "cultural"],
        "estacionamientos": 20,
        "accesible": True,
        "permite_servicio_comida": False,
    },
    {
        "nombre": "Centro Comunitario San Teodoro",
        "comuna": "San Teodoro del Valle",
        "espacio": "interior",
        "capacidad_maxima": 40,
        "m2": 90,
        "tipos_evento": ["infantil", "cultural", "tecnologico"],
        "estacionamientos": 6,
        "accesible": False,
        "permite_servicio_comida": True,
    },
    {
        "nombre": "Carpa Modular Bahía Pizarra",
        "comuna": "Bahía Pizarra",
        "espacio": "exterior",
        "capacidad_maxima": 300,
        "m2": 500,
        "tipos_evento": ["gastronomico", "cultural", "infantil", "tecnologico"],
        "estacionamientos": 50,
        "accesible": True,
        "permite_servicio_comida": True,
    },
]

_TIPOS = ("tecnologico", "gastronomico", "cultural", "infantil")
_ESPACIOS = ("interior", "exterior")

# Formas alternativas que puede escribir una persona o el modelo.
_ALIAS_TIPO = {
    "tecnologico": "tecnologico",
    "tecnologica": "tecnologico",
    "tecnologicos": "tecnologico",
    "tecnologia": "tecnologico",
    "tech": "tecnologico",
    "tecno": "tecnologico",
    "informatica": "tecnologico",
    "gastronomico": "gastronomico",
    "gastronomica": "gastronomico",
    "gastronomia": "gastronomico",
    "comida": "gastronomico",
    "food": "gastronomico",
    "cultural": "cultural",
    "culturales": "cultural",
    "cultura": "cultural",
    "arte": "cultural",
    "artistica": "cultural",
    "infantil": "infantil",
    "infantiles": "infantil",
    "ninos": "infantil",
    "nino": "infantil",
    "ninas": "infantil",
    "kids": "infantil",
    "familiar": "infantil",
}

_ALIAS_ESPACIO = {
    "interior": "interior",
    "adentro": "interior",
    "dentro": "interior",
    "cerrado": "interior",
    "techado": "interior",
    "bajo techo": "interior",
    "exterior": "exterior",
    "afuera": "exterior",
    "fuera": "exterior",
    "aire libre": "exterior",
    "al aire libre": "exterior",
    "abierto": "exterior",
    "cualquiera": "cualquiera",
    "": "cualquiera",
    "ambos": "cualquiera",
    "indiferente": "cualquiera",
    "da igual": "cualquiera",
    "no importa": "cualquiera",
}

_PERSONAS_MIN = 10
_PERSONAS_MAX = 500
_HOLGURA_PCT = 110  # La capacidad debe ser al menos personas × 1,10.
_OCUPACION_IDEAL = 75
_OCUPACION_QUEDA_GRANDE = 35
_M2_POR_STAND = 9
_AREA_PARA_STANDS = 0.40
_MAX_RESULTADOS = 3
_NOTA = (
    "Datos ficticios. La disponibilidad, los permisos y el aforo legal los confirma "
    "una persona con el recinto."
)


def _normalizar(texto) -> str:
    """Pasa texto a minúsculas, sin tildes ni espacios sobrantes."""
    sin_tildes = unicodedata.normalize("NFKD", str(texto or "").strip().casefold())
    sin_tildes = "".join(letra for letra in sin_tildes if not unicodedata.combining(letra))
    return " ".join(sin_tildes.replace("-", " ").replace("_", " ").split())


def _tipo_valido(tipo_evento) -> str | None:
    """Devuelve el tipo de evento canónico o None si no se reconoce."""
    texto = _normalizar(tipo_evento)
    if texto in _ALIAS_TIPO:
        return _ALIAS_TIPO[texto]
    # Admite frases como "feria tecnológica" o "evento para niños".
    for palabra in texto.split():
        if palabra in _ALIAS_TIPO:
            return _ALIAS_TIPO[palabra]
    return None


def _espacio_valido(espacio) -> str | None:
    """Devuelve interior, exterior o cualquiera; None si no se reconoce."""
    texto = _normalizar(espacio)
    if texto in _ALIAS_ESPACIO:
        return _ALIAS_ESPACIO[texto]
    encontrados = {valor for alias, valor in _ALIAS_ESPACIO.items() if alias and alias in texto}
    if {"interior", "exterior"} <= encontrados:
        return "cualquiera"  # Por ejemplo: "interior o exterior".
    if len(encontrados) == 1:
        return encontrados.pop()
    return "cualquiera" if "cualquiera" in encontrados else None


def _personas_validas(personas) -> int | None:
    """Convierte la cantidad de personas a entero; None si no es un número."""
    if isinstance(personas, bool):
        return None
    try:
        return int(float(str(personas).strip().replace(",", ".")))
    except (TypeError, ValueError):
        return None


def _cabe(recinto: dict, personas: int) -> bool:
    """True si el recinto deja al menos un 10 % de holgura (cuenta con enteros)."""
    return recinto["capacidad_maxima"] * 100 >= personas * _HOLGURA_PCT


def _sin_resultados(motivo: str, personas: int | None = None) -> dict:
    """Respuesta de la herramienta cuando no hay recintos que recomendar."""
    return {"personas": personas, "recintos": [], "motivo": motivo, "nota": _NOTA}


def _ficha(recinto: dict, personas: int) -> dict:
    """Arma la ficha de un recinto con las cuentas ya hechas."""
    ocupacion = round(personas * 100 / recinto["capacidad_maxima"], 1)
    ficha = {
        "nombre": recinto["nombre"],
        "comuna": recinto["comuna"],
        "espacio": recinto["espacio"],
        "capacidad_maxima": recinto["capacidad_maxima"],
        "ocupacion_pct": ocupacion,
        "m2": recinto["m2"],
        "m2_por_persona": round(recinto["m2"] / personas, 1),
        "stands_estimados": int(recinto["m2"] * _AREA_PARA_STANDS // _M2_POR_STAND),
        "estacionamientos": recinto["estacionamientos"],
        "accesible": "sí" if recinto["accesible"] else "no",
        "permite_servicio_comida": "sí" if recinto["permite_servicio_comida"] else "no",
    }
    if ocupacion < _OCUPACION_QUEDA_GRANDE:
        ficha["aviso"] = (
            f"queda grande: con {personas} personas se ocupa solo el {ocupacion} % "
            "y el lugar se verá vacío."
        )
    return ficha


def _sugerencia(tipo: str, personas: int, espacio: str) -> str:
    """Explica en una línea por qué no hubo recintos y qué se puede cambiar."""
    aptos = [r for r in _RECINTOS if tipo in r["tipos_evento"]]
    if espacio != "cualquiera":
        otro = "exterior" if espacio == "interior" else "interior"
        if any(r["espacio"] == otro and _cabe(r, personas) for r in aptos):
            return (
                f"No hay recintos {espacio}es para una feria {tipo} de {personas} personas; "
                f"sí los hay en espacio {otro}."
            )
        aptos = [r for r in aptos if r["espacio"] == espacio]
    if not aptos:
        return f"No hay recintos de ese espacio para ferias de tipo {tipo}; prueba con otro espacio."
    mayor = max(r["capacidad_maxima"] for r in aptos)
    maximo = mayor * 100 // _HOLGURA_PCT
    return (
        f"Ningún recinto alcanza para {personas} personas con un 10 % de holgura; "
        f"prueba con {maximo} personas o menos, u otro espacio."
    )


def _buscar(tipo_evento, personas, espacio) -> dict:
    """Lógica de la búsqueda; la herramienta la envuelve para no lanzar errores."""
    cantidad = _personas_validas(personas)
    if cantidad is None:
        return _sin_resultados("La cantidad de personas debe ser un número entre 10 y 500.")
    if not _PERSONAS_MIN <= cantidad <= _PERSONAS_MAX:
        return _sin_resultados(
            f"Solo recomiendo recintos para eventos de {_PERSONAS_MIN} a {_PERSONAS_MAX} "
            f"personas; pediste {cantidad}.",
            cantidad,
        )

    tipo = _tipo_valido(tipo_evento)
    if tipo is None:
        return _sin_resultados(
            "Tipo de evento no reconocido; usa tecnologico, gastronomico, cultural o infantil.",
            cantidad,
        )
    lugar = _espacio_valido(espacio)
    if lugar is None:
        return _sin_resultados(
            "Espacio no reconocido; usa interior, exterior o cualquiera.", cantidad
        )

    candidatos = [
        recinto
        for recinto in _RECINTOS
        if tipo in recinto["tipos_evento"]
        and (lugar == "cualquiera" or recinto["espacio"] == lugar)
        and _cabe(recinto, cantidad)
    ]
    if not candidatos:
        return _sin_resultados(_sugerencia(tipo, cantidad, lugar), cantidad)

    fichas = [_ficha(recinto, cantidad) for recinto in candidatos]
    fichas.sort(key=lambda ficha: abs(ficha["ocupacion_pct"] - _OCUPACION_IDEAL))
    return {
        "personas": cantidad,
        "capacidad_minima": (cantidad * _HOLGURA_PCT + 99) // 100,
        "tipo_evento": tipo,
        "espacio": lugar,
        "recintos": fichas[:_MAX_RESULTADOS],
        "nota": _NOTA,
    }


@tool
def buscar_recintos(tipo_evento: str, personas: int, espacio: str = "cualquiera") -> dict:
    """Busca hasta tres recintos ficticios para una feria o evento y entrega las cuentas hechas.

    tipo_evento: tecnologico, gastronomico, cultural o infantil. También acepta formas
        como "feria tecnológica", "tech", "gastronomía", "arte" o "niños".
    personas: cantidad de asistentes esperados, número entero entre 10 y 500.
    espacio: interior, exterior o cualquiera (valor por defecto). También acepta
        "adentro", "bajo techo", "afuera" o "aire libre". Usa cualquiera si la persona
        no dijo nada sobre el espacio.

    Solo incluye recintos con al menos un 10 % de holgura (capacidad >= personas × 1,10)
    y los ordena por la ocupación más cercana al 75 %.
    Devuelve un diccionario con: personas, capacidad_minima, recintos (lista con nombre,
    comuna, espacio, capacidad_maxima, ocupacion_pct, m2, m2_por_persona,
    stands_estimados, estacionamientos, accesible, permite_servicio_comida y, si
    corresponde, aviso "queda grande") y una nota. Si no hay recintos, la lista viene
    vacía y se agrega un motivo de una línea con qué cambiar. No incluye precios.
    """
    try:
        return _buscar(tipo_evento, personas, espacio)
    except Exception as error:  # La herramienta nunca debe cortar al agente.
        detalle = str(error).replace("\n", " ").strip() or error.__class__.__name__
        return _sin_resultados(f"No pude revisar los recintos: {detalle}")
