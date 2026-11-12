"""Herramientas con datos ficticios de actividades para ferias y eventos."""

import unicodedata
from datetime import datetime, timedelta

from langchain_core.tools import tool


_ACTIVIDADES = {
    "tecnologico": [
        {"nombre": "Charla: inteligencia artificial en la vida diaria", "duracion_minutos": 40, "publico": ["adulto", "estudiantes"], "descripcion": "Ejemplos cotidianos de IA, sin lenguaje técnico."},
        {"nombre": "Taller de robótica con kits", "duracion_minutos": 60, "publico": ["estudiantes", "familiar"], "descripcion": "Armado y programación básica de un robot pequeño."},
        {"nombre": "Demo de realidad virtual", "duracion_minutos": 30, "publico": ["familiar", "adulto", "estudiantes"], "descripcion": "Turnos cortos con cascos disponibles en el stand."},
        {"nombre": "Panel de startups locales", "duracion_minutos": 50, "publico": ["adulto"], "descripcion": "Tres emprendedores cuentan su proyecto y responden preguntas."},
        {"nombre": "Concurso de programación para jóvenes", "duracion_minutos": 90, "publico": ["estudiantes"], "descripcion": "Desafíos por equipos con premio simbólico."},
        {"nombre": "Juegos de lógica y programación sin pantalla", "duracion_minutos": 45, "publico": ["familiar"], "descripcion": "Tableros y tarjetas para aprender a dar instrucciones paso a paso."},
        {"nombre": "Impresión 3D en vivo", "duracion_minutos": 60, "publico": ["familiar", "adulto"], "descripcion": "Demostración de impresoras 3D y piezas para llevar."},
        {"nombre": "Mesa de ciberseguridad para hogares", "duracion_minutos": 40, "publico": ["adulto"], "descripcion": "Consejos prácticos sobre contraseñas, wifi y estafas comunes."},
    ],
    "gastronomico": [
        {"nombre": "Clase de cocina rápida", "duracion_minutos": 45, "publico": ["familiar", "adulto"], "descripcion": "Una receta sencilla preparada en vivo y degustación."},
        {"nombre": "Cata guiada de vinos", "duracion_minutos": 40, "publico": ["adulto"], "descripcion": "Cuatro muestras con guía de un sommelier."},
        {"nombre": "Recorrido por food trucks", "duracion_minutos": 60, "publico": ["familiar", "adulto", "estudiantes"], "descripcion": "Visita libre a cinco puestos con porciones pequeñas."},
        {"nombre": "Taller de pan casero", "duracion_minutos": 60, "publico": ["familiar"], "descripcion": "Cada participante amasa y se lleva su pan."},
    ],
    "cultural": [
        {"nombre": "Visita guiada al patrimonio del barrio", "duracion_minutos": 60, "publico": ["familiar", "adulto"], "descripcion": "Recorrido a pie de unos 40 minutos con historia local."},
        {"nombre": "Presentación de danza folclórica", "duracion_minutos": 30, "publico": ["familiar", "adulto", "estudiantes"], "descripcion": "Un espectáculo corto en el escenario principal."},
        {"nombre": "Exposición fotográfica comentada", "duracion_minutos": 45, "publico": ["adulto", "estudiantes"], "descripcion": "Recorrido por veinte fotografías con comentario del autor."},
        {"nombre": "Ronda de cuentacuentos", "duracion_minutos": 30, "publico": ["familiar"], "descripcion": "Historias para escuchar en grupo, sentados en el suelo."},
    ],
    "infantil": [
        {"nombre": "Pintacuentos", "duracion_minutos": 30, "publico": ["familiar"], "descripcion": "Los niños pintan una escena mientras se lee un cuento."},
        {"nombre": "Taller de globoflexia", "duracion_minutos": 45, "publico": ["familiar"], "descripcion": "Figuras con globos para niños de 4 a 10 años."},
        {"nombre": "Show de magia", "duracion_minutos": 40, "publico": ["familiar"], "descripcion": "Magia de cerca con participación de niños voluntarios."},
        {"nombre": "Carrera de sacos", "duracion_minutos": 30, "publico": ["familiar"], "descripcion": "Competencia recreativa por categorías de edad."},
    ],
}

_PUBLICOS = {"familiar", "adulto", "estudiantes"}

# Formas alternativas que puede escribir una persona o el modelo para cada público.
_ALIAS_PUBLICO = {
    "ninos": "familiar",
    "nino": "familiar",
    "infantil": "familiar",
    "familia": "familiar",
    "adultos": "adulto",
    "estudiante": "estudiantes",
    "jovenes": "estudiantes",
    "universitarios": "estudiantes",
}


def _normalizar(texto: str) -> str:
    """Pasa texto a minúsculas y elimina tildes y espacios exteriores."""
    sin_tildes = unicodedata.normalize("NFKD", texto.strip().casefold())
    return "".join(letra for letra in sin_tildes if not unicodedata.combining(letra))


def _sumar_minutos(hora: str, minutos: int) -> str:
    """Suma minutos a una hora HH:MM y devuelve la nueva hora HH:MM."""
    inicio = datetime.strptime(hora, "%H:%M")
    return (inicio + timedelta(minutes=minutos)).strftime("%H:%M")


def _sin_resultados(motivo: str) -> dict:
    """Respuesta de la herramienta cuando no se puede armar un programa."""
    return {"actividades": [], "minutos_usados": 0, "minutos_libres": 0, "motivo": motivo}


@tool
def armar_programa(
    tipo_evento: str,
    duracion_minutos: int,
    publico: str,
    hora_inicio: str = "10:00",
) -> dict:
    """Arma un programa de actividades ficticias que caben en la duración indicada.

    tipo_evento: tecnologico, gastronomico, cultural o infantil.
    publico: familiar (también niños o familia), adulto o estudiantes (también jóvenes).
    hora_inicio: hora de inicio en formato HH:MM (24 horas).
    Devuelve un diccionario con: actividades (lista en orden, con hora de inicio y de
    término), minutos_usados y minutos_libres. Si no hay actividades, la lista viene
    vacía y se agrega un motivo.
    """
    tipo = _normalizar(tipo_evento)
    publico_normalizado = _normalizar(publico)
    publico_normalizado = _ALIAS_PUBLICO.get(publico_normalizado, publico_normalizado)
    if tipo not in _ACTIVIDADES or publico_normalizado not in _PUBLICOS:
        return _sin_resultados("Tipo de evento o público no válido.")
    if duracion_minutos < 30 or duracion_minutos > 480:
        return _sin_resultados("La duración debe estar entre 30 y 480 minutos.")
    try:
        datetime.strptime(hora_inicio, "%H:%M")
    except ValueError:
        return _sin_resultados("La hora de inicio debe tener formato HH:MM.")

    programa = []
    hora = hora_inicio
    usados = 0
    for actividad in _ACTIVIDADES[tipo]:
        if publico_normalizado not in actividad["publico"]:
            continue
        if usados + actividad["duracion_minutos"] > duracion_minutos:
            continue
        programa.append(
            {
                "orden": len(programa) + 1,
                "hora_inicio": hora,
                "hora_fin": _sumar_minutos(hora, actividad["duracion_minutos"]),
                "nombre": actividad["nombre"],
                "duracion_minutos": actividad["duracion_minutos"],
                "descripcion": actividad["descripcion"],
            }
        )
        usados += actividad["duracion_minutos"]
        hora = _sumar_minutos(hora, actividad["duracion_minutos"])

    resultado = {
        "actividades": programa,
        "minutos_usados": usados,
        "minutos_libres": duracion_minutos - usados,
    }
    if not programa:
        resultado["motivo"] = "Ninguna actividad cabe en ese tiempo para ese público."
    return resultado
