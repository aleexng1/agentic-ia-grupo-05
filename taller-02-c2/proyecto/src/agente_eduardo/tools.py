"""Estimaciones reproducibles con tarifas enteramente ficticias."""

import unicodedata

from langchain_core.tools import tool


# Montos inventados para pruebas y demostración; no representan precios de mercado.
_TARIFAS_FICTICIAS = {
    "tecnologico": {
        "recinto_por_bloque_30_min": 100_000,
        "equipamiento_por_persona": 2_500,
        "personal_por_persona_bloque": 1_200,
        "logistica_por_persona": 800,
        "alimentacion_generica_por_persona": 1_800,
    },
    "gastronomico": {
        "recinto_por_bloque_30_min": 90_000,
        "equipamiento_por_persona": 2_000,
        "personal_por_persona_bloque": 1_000,
        "logistica_por_persona": 900,
        "alimentacion_generica_por_persona": 2_200,
    },
    "cultural": {
        "recinto_por_bloque_30_min": 80_000,
        "equipamiento_por_persona": 1_800,
        "personal_por_persona_bloque": 900,
        "logistica_por_persona": 700,
        "alimentacion_generica_por_persona": 1_500,
    },
    "infantil": {
        "recinto_por_bloque_30_min": 75_000,
        "equipamiento_por_persona": 2_200,
        "personal_por_persona_bloque": 1_100,
        "logistica_por_persona": 850,
        "alimentacion_generica_por_persona": 1_600,
    },
}

_ALIAS_TIPO = {
    "feria tecnologica": "tecnologico",
    "tecnologia": "tecnologico",
    "tecnologico": "tecnologico",
    "tech": "tecnologico",
    "feria gastronomica": "gastronomico",
    "gastronomia": "gastronomico",
    "gastronomico": "gastronomico",
    "feria cultural": "cultural",
    "cultura": "cultural",
    "cultural": "cultural",
    "feria infantil": "infantil",
    "ninos": "infantil",
    "infantil": "infantil",
}


def _normalizar(texto: str) -> str:
    """Convierte tildes, mayúsculas y espacios múltiples a una forma comparable."""
    sin_tildes = unicodedata.normalize("NFKD", texto.strip().casefold())
    return " ".join("".join(c for c in sin_tildes if not unicodedata.combining(c)).split())


@tool
def estimar_presupuesto(tipo_evento: str, personas: int, duracion_minutos: int) -> dict:
    """Calcula un presupuesto simulado en CLP usando exclusivamente tarifas ficticias.

    tipo_evento: tecnologico, gastronomico, cultural o infantil (acepta variantes).
    personas: cantidad entera entre 10 y 500.
    duracion_minutos: duración entera entre 30 y 480.
    Devuelve partidas, subtotal, contingencia, total, supuestos y advertencia;
    si los datos no son válidos devuelve solamente un motivo.
    """
    if not isinstance(tipo_evento, str):
        return {"motivo": "El tipo de evento debe ser texto."}
    tipo = _ALIAS_TIPO.get(_normalizar(tipo_evento))
    if tipo is None:
        return {"motivo": "Tipo de evento no válido; use tecnológico, gastronómico, cultural o infantil."}
    if isinstance(personas, bool) or not isinstance(personas, int) or not 10 <= personas <= 500:
        return {"motivo": "La cantidad de personas debe ser un entero entre 10 y 500."}
    if isinstance(duracion_minutos, bool) or not isinstance(duracion_minutos, int) or not 30 <= duracion_minutos <= 480:
        return {"motivo": "La duración debe ser un entero entre 30 y 480 minutos."}

    tarifa = _TARIFAS_FICTICIAS[tipo]
    bloques_30_min = (duracion_minutos + 29) // 30
    partidas = {
        "recinto_referencial": tarifa["recinto_por_bloque_30_min"] * bloques_30_min,
        "equipamiento": tarifa["equipamiento_por_persona"] * personas,
        "personal": tarifa["personal_por_persona_bloque"] * personas * bloques_30_min,
        "logistica": tarifa["logistica_por_persona"] * personas,
        "alimentacion_generica": tarifa["alimentacion_generica_por_persona"] * personas,
    }
    subtotal = sum(partidas.values())
    contingencia = (subtotal * 10 + 99) // 100
    return {
        "tipo_evento": tipo,
        "personas": personas,
        "duracion_minutos": duracion_minutos,
        "partidas_clp": partidas,
        "subtotal_clp": subtotal,
        "contingencia_clp": contingencia,
        "total_clp": subtotal + contingencia,
        "supuestos": [
            f"La duración se calcula en {bloques_30_min} bloques de 30 minutos, redondeando hacia arriba.",
            "La contingencia es 10 % del subtotal, redondeada hacia arriba al peso.",
            "La alimentación es genérica y no define menú, dieta, proveedor ni cantidades de platos.",
        ],
        "advertencia": "Simulación con importes completamente ficticios; no son precios reales y no constituyen autorización de gasto. Impuestos no modelados.",
    }
