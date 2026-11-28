"""Consultas GraphRAG sobre Neo4j. Dueño: Eduardo (c2tf/eduardo-conocimiento)."""

import re

from langchain_core.tools import ToolException
from neo4j import READ_ACCESS

from src.conocimiento.grafo.catalogo import (
    PROYECTO,
    RELACIONES,
    RUTA_CATALOGO,
    ErrorCatalogo,
    id_tope,
    leer_catalogo,
    normalizar,
    slug,
)
from src.conocimiento.grafo.conexion import ErrorGrafo, configuracion, sesion_neo4j

# La ambigüedad se resuelve por contexto de viaje, nunca por el nivel propuesto.
_CANDIDATOS = """
MATCH (cargo:Grupo05C2GraphRAG:Cargo {proyecto: $proyecto, clave: $cargo_clave})
MATCH (cat:Grupo05C2GraphRAG:Categoria {proyecto: $proyecto})
WHERE ($categoria_id IS NULL AND cat.clave = $categoria_clave)
   OR ($categoria_id IS NOT NULL AND cat.id = $categoria_id)
RETURN cargo.id AS cargo_id, cat.id AS categoria_id
LIMIT 3
"""
_RECORRIDO = """
MATCH camino =
    (cargo:Grupo05C2GraphRAG:Cargo {proyecto: $proyecto, id: $cargo_id})
    -[tn:TIENE_NIVEL {proyecto: $proyecto}]->(nivel:Grupo05C2GraphRAG:Nivel {proyecto: $proyecto})
    -[e:PUEDE_RENDIR {proyecto: $proyecto}]->(cat:Grupo05C2GraphRAG:Categoria {proyecto: $proyecto, id: $categoria_id})
    -[tt:TIENE_TOPE {proyecto: $proyecto}]->(tope:Grupo05C2GraphRAG:Tope {proyecto: $proyecto})
RETURN cargo.id AS cargo_id, nivel.id AS nivel_id,
       cargo.nombre AS cargo, nivel.nombre AS nivel, cat.nombre AS categoria,
       cat.id AS categoria_id, cat.politica AS politica,
       tope.id AS tope_id, tope.tope_clp AS tope_clp, tope.fuente AS fuente,
       tope.codigo AS documento, tope.version AS version, tope.base AS base,
       e.origen_datos AS estado_elegibilidad,
       tn.origen_datos AS origen_nivel, tt.origen_datos AS origen_tope,
       [rel IN relationships(camino) | type(rel)] AS relaciones
LIMIT 2
"""
_PUBLICOS = ("cargo", "nivel", "categoria", "tope_clp", "fuente")
_INCOMPATIBLE = "Neo4j devolvió un resultado incompatible con el grafo de rendiciones."


def _entrada(texto: str, campo: str) -> str:
    if isinstance(texto, str) and len(texto) <= 100:
        clave = normalizar(texto)
        if clave and clave.isprintable():
            return clave
    raise ToolException(f"{campo} debe ser un texto no vacío de hasta 100 caracteres.")


def _categoria(categoria: str) -> tuple[str | None, str]:
    clave = _entrada(categoria, "La categoría")
    if ":" not in clave:
        return None, clave
    politica, nombre = (parte.strip() for parte in clave.split(":", 1))
    if not re.fullmatch(r"p[0-9]{2}", politica) or not nombre or ":" in nombre:
        raise ToolException("Usa una categoría cualificada como P02:hotel.")
    return f"{politica.upper()}:{slug(nombre)}", nombre


def _consultar_recorrido(cargo: str, categoria: str) -> dict | None:
    """Diagnóstico interno: recupera el recorrido de Neo4j, no del JSON."""
    cargo_clave = _entrada(cargo, "El cargo")
    categoria_id, categoria_clave = _categoria(categoria)
    try:
        catalogo = leer_catalogo(str(RUTA_CATALOGO))
    except ErrorCatalogo:
        raise ToolException("No se pudo verificar el catálogo de GraphRAG.") from None
    org, normativa = catalogo.organizacion_ficticia, catalogo.normativa
    cargo_ref = next((c for c in org.cargos if normalizar(c.nombre) == cargo_clave), None)
    categorias_ref = {
        c.id: c for c in normativa.categorias
        if (c.id == categoria_id if categoria_id else normalizar(c.nombre) == categoria_clave)
    }
    candidatos_ref = [
        {"cargo_id": cargo_ref.id, "categoria_id": id_} for id_ in sorted(categorias_ref)
    ] if cargo_ref else []

    try:
        with sesion_neo4j(configuracion(), READ_ACCESS) as sesion:
            with sesion.begin_transaction(timeout=5) as tx:
                candidatos = tx.run(
                    _CANDIDATOS, proyecto=PROYECTO, cargo_clave=cargo_clave,
                    categoria_id=categoria_id, categoria_clave=categoria_clave,
                ).data()
                if len(candidatos) != len(candidatos_ref) or any(
                    candidatos.count(esperado) != 1 for esperado in candidatos_ref
                ):
                    raise ToolException(_INCOMPATIBLE)
                if not candidatos:
                    return None
                if len(candidatos) > 1:
                    raise ToolException("La categoría es ambigua. Indica la política, por ejemplo P02:hotel o P03:hotel.")
                cargo_id = candidatos[0]["cargo_id"]
                categoria_id = candidatos[0]["categoria_id"]
                filas = tx.run(
                    _RECORRIDO, proyecto=PROYECTO, cargo_id=cargo_id, categoria_id=categoria_id
                ).data()
    except ErrorGrafo as error:
        raise ToolException(str(error)) from None

    elegible = any(
        e.nivel_id == cargo_ref.nivel_id and categoria_id in e.categorias
        for e in org.elegibilidad_propuesta
    )
    if not elegible and not filas:
        return None
    if not elegible or len(filas) != 1 or not isinstance(filas[0], dict):
        raise ToolException(_INCOMPATIBLE)
    nivel = next(n for n in org.niveles if n.id == cargo_ref.nivel_id)
    cat = categorias_ref[categoria_id]
    esperado = {
        "cargo_id": cargo_ref.id, "cargo": cargo_ref.nombre, "nivel_id": nivel.id, "nivel": nivel.nombre,
        "categoria_id": cat.id, "categoria": cat.nombre, "politica": cat.id.split(":")[0],
        "tope_id": id_tope(cat.id), "tope_clp": cat.tope_clp, "fuente": cat.fuente,
        "documento": normativa.codigo, "version": normativa.version, "base": "por_documento",
        "estado_elegibilidad": catalogo.estado, "origen_nivel": catalogo.estado,
        "origen_tope": normativa.codigo, "relaciones": list(RELACIONES),
    }
    if filas[0] != esperado or type(filas[0]["tope_clp"]) is not int:
        raise ToolException(_INCOMPATIBLE)
    return filas[0]


def tope_para(cargo: str, categoria: str) -> dict | None:
    """Devuelve el tope de un recorrido único, o None si no hay recorrido.

    Si una categoría aparece en más de una política, pide una categoría cualificada.
    Un recorrido pertenece a la propuesta académica; no autoriza un gasto.
    """
    recorrido = _consultar_recorrido(cargo, categoria)
    return None if recorrido is None else {campo: recorrido[campo] for campo in _PUBLICOS}
