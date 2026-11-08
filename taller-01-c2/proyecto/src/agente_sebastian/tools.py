"""Herramienta con datos ficticios de comida y catering para ferias y eventos.

Todas las cuentas (horarios, cantidades, agua y dietas) se hacen aquí y no en el
modelo, porque los modelos de lenguaje suman y redondean mal. Los datos no tienen
precios: los costos los responde otro agente.
"""

import math
import re
import unicodedata
from datetime import datetime
from fractions import Fraction

from langchain_core.tools import tool


# Margen sobre cada cantidad, para mermas y personas sin inscripción.
MARGEN = Fraction(11, 10)
# Agua: medio litro por persona por cada bloque de dos horas (o fracción).
LITROS_POR_BLOQUE = Fraction(1, 2)
MINUTOS_POR_BLOQUE_AGUA = 120
# Se sirve un servicio cada 150 minutos; el primero, 60 minutos después del inicio.
PRIMER_SERVICIO_MINUTOS = 60
INTERVALO_SERVICIOS_MINUTOS = 150
# Un servicio no se programa si quedan menos de 30 minutos de evento.
MINUTOS_MINIMOS_ANTES_DEL_FIN = 30
# Bajo este largo, el evento lleva un solo servicio corto al inicio.
DURACION_EVENTO_CORTO = 90
# Franja en la que el servicio que toque se convierte en almuerzo.
INICIO_ALMUERZO = 12 * 60
FIN_ALMUERZO = 14 * 60 + 30
# Desde esta hora el refrigerio de un evento de adultos es un cóctel.
INICIO_COCTEL = 17 * 60 + 30
# Si mencionan una dieta sin decir cuántas personas son, se estima este porcentaje.
PORCENTAJE_DIETA_SIN_CANTIDAD = Fraction(1, 10)

PERSONAS_MINIMAS = 10
PERSONAS_MAXIMAS = 500
DURACION_MINIMA = 30
DURACION_MAXIMA = 480

TIPOS_EVENTO = ("tecnologico", "gastronomico", "cultural", "infantil")
DIETAS = ("vegetariano", "vegano", "sin gluten", "sin lactosa")

# Cada elemento es (nombre, cantidad por persona, unidad).
_SERVICIOS = {
    "coffee_break": {
        "nombre": "Coffee break",
        "descripcion": "Café, té y bocados dulces y salados en una mesa de autoservicio.",
        "platos": [
            ("Sándwich de miga", 2, "unidades"),
            ("Queque o galletas", 2, "unidades"),
            ("Fruta picada", 1, "vasos"),
        ],
        "bebidas": [("Café o té", 1, "tazas")],
        "dietas": {
            "vegetariano": [("Sándwich de miga de queso y tomate", 2, "unidades"), ("Fruta picada", 1, "vasos")],
            "vegano": [("Sándwich de hummus y verduras", 2, "unidades"), ("Fruta picada", 1, "vasos"), ("Leche vegetal para el café", 1, "porciones")],
            "sin gluten": [("Sándwich en pan sin gluten", 2, "unidades"), ("Galletas de avena sin gluten", 2, "unidades")],
            "sin lactosa": [("Sándwich de pavo y palta sin mantequilla", 2, "unidades"), ("Leche sin lactosa para el café", 1, "porciones")],
        },
    },
    "coctel": {
        "nombre": "Cóctel frío",
        "descripcion": "Bocados fríos servidos en bandejas que recorren el lugar.",
        "platos": [
            ("Canapés surtidos", 6, "unidades"),
            ("Brochetas de queso y fruta", 2, "unidades"),
        ],
        "bebidas": [("Jugos y bebidas sin alcohol", 2, "vasos")],
        "dietas": {
            "vegetariano": [("Canapés de verduras y queso", 6, "unidades")],
            "vegano": [("Canapés de verduras asadas", 6, "unidades"), ("Brochetas de fruta", 2, "unidades")],
            "sin gluten": [("Bocados sobre pepino o arroz inflado", 6, "unidades")],
            "sin lactosa": [("Canapés sin queso ni crema", 6, "unidades"), ("Brochetas de fruta", 2, "unidades")],
        },
    },
    "colacion_infantil": {
        "nombre": "Colación infantil",
        "descripcion": "Colación individual en bolsa, pensada para niños.",
        "platos": [
            ("Sándwich pequeño de jamón y queso", 1, "unidades"),
            ("Fruta entera", 1, "unidades"),
            ("Galletas", 2, "unidades"),
        ],
        "bebidas": [("Jugo en caja", 1, "unidades")],
        "dietas": {
            "vegetariano": [("Sándwich pequeño de queso", 1, "unidades")],
            "vegano": [("Sándwich pequeño de palta y tomate", 1, "unidades"), ("Galletas sin leche ni huevo", 2, "unidades")],
            "sin gluten": [("Sándwich pequeño en pan sin gluten", 1, "unidades"), ("Galletas sin gluten", 2, "unidades")],
            "sin lactosa": [("Sándwich pequeño de pavo sin queso", 1, "unidades")],
        },
    },
    "box_lunch": {
        "nombre": "Box lunch",
        "descripcion": "Caja individual para comer en cualquier lugar, sin mesas.",
        "platos": [
            ("Sándwich gourmet", 1, "unidades"),
            ("Ensalada individual", 1, "unidades"),
            ("Postre individual", 1, "unidades"),
        ],
        "bebidas": [("Jugo o bebida", 1, "unidades")],
        "dietas": {
            "vegetariano": [("Sándwich de verduras grilladas y queso", 1, "unidades")],
            "vegano": [("Wrap de falafel y verduras", 1, "unidades"), ("Postre de fruta", 1, "unidades")],
            "sin gluten": [("Ensalada completa con pollo y quínoa", 1, "unidades"), ("Postre sin gluten", 1, "unidades")],
            "sin lactosa": [("Sándwich de pollo sin queso ni mayonesa", 1, "unidades"), ("Postre de fruta", 1, "unidades")],
        },
    },
    "almuerzo_buffet": {
        "nombre": "Almuerzo buffet",
        "descripcion": "Mesas calientes y frías con autoservicio.",
        "platos": [
            ("Plato de fondo", 1, "porciones"),
            ("Acompañamiento", 1, "porciones"),
            ("Ensalada", 1, "porciones"),
            ("Postre", 1, "porciones"),
        ],
        "bebidas": [("Jugo o bebida", 1, "vasos")],
        "dietas": {
            "vegetariano": [("Lasaña de verduras", 1, "porciones")],
            "vegano": [("Guiso de legumbres con arroz", 1, "porciones"), ("Postre de fruta", 1, "porciones")],
            "sin gluten": [("Pollo asado con papas", 1, "porciones"), ("Postre sin gluten", 1, "porciones")],
            "sin lactosa": [("Pescado a la plancha con arroz", 1, "porciones"), ("Postre de fruta", 1, "porciones")],
        },
    },
    "food_trucks": {
        "nombre": "Ronda de food trucks",
        "descripcion": "Cada asistente recibe vales para canjear en los carros de comida de la feria.",
        "platos": [
            ("Vale de plato principal", 1, "vales"),
            ("Vale de postre", 1, "vales"),
        ],
        "bebidas": [("Vale de bebida", 1, "vales")],
        "dietas": {
            "vegetariano": [("Vale para el carro vegetariano", 1, "vales")],
            "vegano": [("Vale para el carro vegano", 1, "vales")],
            "sin gluten": [("Vale para el carro sin gluten", 1, "vales")],
            "sin lactosa": [("Vale para un plato sin lácteos", 1, "vales")],
        },
    },
    "almuerzo_infantil": {
        "nombre": "Almuerzo infantil",
        "descripcion": "Menú sencillo en porciones para niños.",
        "platos": [
            ("Mini hamburguesa o nuggets", 1, "porciones"),
            ("Papas al horno", 1, "porciones"),
            ("Fruta entera", 1, "unidades"),
            ("Postre", 1, "porciones"),
        ],
        "bebidas": [("Jugo", 1, "vasos")],
        "dietas": {
            "vegetariano": [("Nuggets de verduras", 1, "porciones")],
            "vegano": [("Mini hamburguesa de lentejas", 1, "porciones"), ("Postre de fruta", 1, "porciones")],
            "sin gluten": [("Pollo al horno con papas", 1, "porciones"), ("Postre sin gluten", 1, "porciones")],
            "sin lactosa": [("Mini hamburguesa sin queso", 1, "porciones"), ("Postre de fruta", 1, "porciones")],
        },
    },
}

# El almuerzo que corresponde a cada tipo de evento.
_ALMUERZO_POR_TIPO = {
    "tecnologico": "box_lunch",
    "gastronomico": "food_trucks",
    "cultural": "almuerzo_buffet",
    "infantil": "almuerzo_infantil",
}

# Palabras con las que se reconoce cada tipo de evento (sobre texto sin tildes).
_CLAVES_TIPO = {
    "tecnologico": ("tecno", "tech"),
    "gastronomico": ("gastro",),
    "cultural": ("cultur",),
    "infantil": ("infant", "nino", "kids"),
}

# Palabras con las que se reconoce cada dieta, en orden de revisión.
_CLAVES_DIETA = (
    ("vegano", ("vegan",)),
    ("vegetariano", ("vegetarian",)),
    ("sin gluten", ("gluten", "celiac", "celiaq")),
    ("sin lactosa", ("lactosa", "lacteo", "leche")),
)


def _normalizar(texto: str) -> str:
    """Pasa texto a minúsculas y elimina tildes y espacios exteriores."""
    sin_tildes = unicodedata.normalize("NFKD", str(texto).strip().casefold())
    return "".join(letra for letra in sin_tildes if not unicodedata.combining(letra))


def _tipo_evento(texto: str) -> str | None:
    """Devuelve el tipo de evento reconocido o None si no corresponde a ninguno."""
    normalizado = _normalizar(texto)
    for tipo, claves in _CLAVES_TIPO.items():
        if any(clave in normalizado for clave in claves):
            return tipo
    return None


def _a_minutos(hora: str) -> int:
    """Convierte una hora HH:MM a minutos desde la medianoche."""
    instante = datetime.strptime(hora.strip(), "%H:%M")
    return instante.hour * 60 + instante.minute


def _a_hora(minutos: int) -> str:
    """Convierte minutos desde la medianoche a una hora HH:MM."""
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


def _con_margen(personas: int, por_persona) -> int:
    """Cantidad para un grupo con el margen aplicado, redondeada hacia arriba."""
    return math.ceil(Fraction(personas) * Fraction(por_persona) * MARGEN)


def _leer_restricciones(texto: str, personas: int) -> tuple[dict, list[str], list[str]]:
    """Separa las dietas pedidas, su cantidad de personas y lo que no se reconoce."""
    dietas: dict[str, int] = {}
    no_reconocidas: list[str] = []
    estimadas: list[str] = []
    if not texto or not str(texto).strip():
        return dietas, no_reconocidas, estimadas

    for trozo in re.split(r",|;|\s+y\s+|\n", str(texto)):
        original = trozo.strip()
        if not original:
            continue
        normalizado = _normalizar(original)
        dieta = next(
            (nombre for nombre, claves in _CLAVES_DIETA if any(clave in normalizado for clave in claves)),
            None,
        )
        if dieta is None:
            no_reconocidas.append(original)
            continue
        numero = re.search(r"\d+", normalizado)
        if numero:
            cantidad = int(numero.group())
        else:
            cantidad = math.ceil(Fraction(personas) * PORCENTAJE_DIETA_SIN_CANTIDAD)
            estimadas.append(dieta)
        dietas[dieta] = dietas.get(dieta, 0) + cantidad
    return dietas, no_reconocidas, estimadas


def _horarios_servicios(inicio: int, duracion: int) -> list[int]:
    """Calcula en qué minutos del día se sirve cada servicio."""
    fin = inicio + duracion
    if duracion < DURACION_EVENTO_CORTO:
        return [inicio]
    horarios = []
    momento = inicio + PRIMER_SERVICIO_MINUTOS
    while momento <= fin - MINUTOS_MINIMOS_ANTES_DEL_FIN:
        horarios.append(momento)
        momento += INTERVALO_SERVICIOS_MINUTOS
    return horarios


def _elegir_servicio(tipo: str, momento: int, almuerzo_servido: bool, evento_corto: bool) -> str:
    """Elige el servicio que corresponde al tipo de evento y a la hora."""
    if not evento_corto and not almuerzo_servido and INICIO_ALMUERZO <= momento <= FIN_ALMUERZO:
        return _ALMUERZO_POR_TIPO[tipo]
    if tipo == "infantil":
        return "colacion_infantil"
    if momento >= INICIO_COCTEL:
        return "coctel"
    return "coffee_break"


def _cantidades(elementos, personas: int) -> list[dict]:
    """Calcula la cantidad de cada elemento para un grupo de personas."""
    return [
        {"nombre": nombre, "cantidad": _con_margen(personas, por_persona), "unidad": unidad}
        for nombre, por_persona, unidad in elementos
    ]


def _sin_resultados(motivo: str) -> dict:
    """Respuesta de la herramienta cuando no se puede armar el catering."""
    return {"servicios": [], "motivo": motivo}


@tool
def armar_catering(
    tipo_evento: str,
    personas: int,
    duracion_minutos: int,
    hora_inicio: str = "10:00",
    restricciones: str = "",
) -> dict:
    """Arma una propuesta de comida y catering ficticia para una feria o evento.

    tipo_evento: tecnologico, gastronomico, cultural o infantil.
    personas: cantidad de asistentes, de 10 a 500.
    duracion_minutos: duración del evento, de 30 a 480 minutos.
    hora_inicio: hora de inicio en formato HH:MM (24 horas).
    restricciones: dietas especiales con su cantidad de personas, por ejemplo
    "12 veganos, 5 sin gluten". Si no se sabe cuántas personas son, solo el nombre
    de la dieta, por ejemplo "vegetariano". Dietas conocidas: vegetariano, vegano,
    sin gluten (celíacos) y sin lactosa.
    Devuelve los servicios en orden, con su hora, platos y bebidas y la cantidad
    calculada de cada uno (con 10 % de margen), los platos para cada dieta, los litros
    de agua y notas. No incluye precios. Si no se puede armar, la lista de servicios
    viene vacía y se agrega un motivo.
    """
    tipo = _tipo_evento(tipo_evento)
    if tipo is None:
        return _sin_resultados(
            "Tipo de evento no válido: usa tecnologico, gastronomico, cultural o infantil."
        )
    if not PERSONAS_MINIMAS <= personas <= PERSONAS_MAXIMAS:
        return _sin_resultados(
            f"La cantidad de personas debe estar entre {PERSONAS_MINIMAS} y {PERSONAS_MAXIMAS}."
        )
    if not DURACION_MINIMA <= duracion_minutos <= DURACION_MAXIMA:
        return _sin_resultados(
            f"La duración debe estar entre {DURACION_MINIMA} y {DURACION_MAXIMA} minutos."
        )
    try:
        inicio = _a_minutos(hora_inicio)
    except ValueError:
        return _sin_resultados("La hora de inicio debe tener formato HH:MM.")
    fin = inicio + duracion_minutos
    if fin > 24 * 60:
        return _sin_resultados("El evento debe terminar antes de la medianoche.")

    dietas, no_reconocidas, estimadas = _leer_restricciones(restricciones, personas)
    con_dieta = sum(dietas.values())
    if con_dieta > personas:
        return _sin_resultados(
            f"Las personas con dietas especiales ({con_dieta}) superan a los asistentes ({personas})."
        )
    sin_dieta = personas - con_dieta

    evento_corto = duracion_minutos < DURACION_EVENTO_CORTO
    servicios = []
    almuerzo_servido = False
    for momento in _horarios_servicios(inicio, duracion_minutos):
        clave = _elegir_servicio(tipo, momento, almuerzo_servido, evento_corto)
        if clave == _ALMUERZO_POR_TIPO[tipo]:
            almuerzo_servido = True
        datos = _SERVICIOS[clave]
        servicios.append(
            {
                "orden": len(servicios) + 1,
                "hora": _a_hora(momento),
                "servicio": datos["nombre"],
                "descripcion": datos["descripcion"],
                "personas_menu_general": sin_dieta,
                "platos": _cantidades(datos["platos"], sin_dieta) if sin_dieta else [],
                "bebidas": _cantidades(datos["bebidas"], personas),
                "dietas": [
                    {
                        "dieta": dieta,
                        "personas": cantidad,
                        "platos": _cantidades(datos["dietas"][dieta], cantidad),
                    }
                    for dieta, cantidad in dietas.items()
                    if cantidad
                ],
            }
        )

    bloques_agua = math.ceil(duracion_minutos / MINUTOS_POR_BLOQUE_AGUA)
    notas = [
        "Cantidades con 10 % de margen, redondeadas hacia arriba.",
        "Datos ficticios y sin precios: es una propuesta, no un pedido.",
    ]
    if estimadas:
        notas.append(
            "No se indicó cuántas personas siguen la dieta "
            + ", ".join(estimadas)
            + ": se estimó el 10 % de los asistentes."
        )
    if no_reconocidas:
        notas.append(
            "Restricciones no reconocidas (confirmar con el proveedor): "
            + ", ".join(no_reconocidas)
            + "."
        )
    if dietas or no_reconocidas:
        notas.append("Las alergias graves las debe confirmar una persona con el proveedor.")

    return {
        "tipo_evento": tipo,
        "personas": personas,
        "hora_inicio": _a_hora(inicio),
        "hora_fin": _a_hora(fin),
        "servicios": servicios,
        "agua": {
            "litros": _con_margen(personas, LITROS_POR_BLOQUE * bloques_agua),
            "detalle": "0,5 L por persona por cada 2 horas de evento, con 10 % de margen.",
        },
        "restricciones_no_reconocidas": no_reconocidas,
        "notas": notas,
    }
