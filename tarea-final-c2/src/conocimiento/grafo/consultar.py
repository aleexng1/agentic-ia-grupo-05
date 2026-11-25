"""Consultas GraphRAG sobre Neo4j. Dueño: Eduardo (c2tf/eduardo-conocimiento)."""

import re

from langchain_core.tools import ToolException
from neo4j import READ_ACCESS

from src.conocimiento.grafo.catalogo import (
    DOCUMENTO,
    ESTADO_PROPUESTA,
    POLITICAS,
    PROYECTO,
    RELACIONES,
    VERSION,
    fuente_para,
    id_tope,
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
LIMIT 2
"""
_RECORRIDO = """
MATCH camino =
    (cargo:Grupo05C2GraphRAG:Cargo {proyecto: $proyecto, id: $cargo_id})
    -[:TIENE_NIVEL {proyecto: $proyecto}]->(nivel:Grupo05C2GraphRAG:Nivel {proyecto: $proyecto})
    -[e:PUEDE_RENDIR {proyecto: $proyecto}]->(cat:Grupo05C2GraphRAG:Categoria {proyecto: $proyecto, id: $categoria_id})
    -[:TIENE_TOPE {proyecto: $proyecto}]->(tope:Grupo05C2GraphRAG:Tope {proyecto: $proyecto})
RETURN cargo.nombre AS cargo, nivel.nombre AS nivel, cat.nombre AS categoria,
       cat.id AS categoria_id, cat.politica AS politica,
       tope.id AS tope_id, tope.tope_clp AS tope_clp, tope.fuente AS fuente,
       tope.codigo AS documento, tope.version AS version, tope.base AS base,
       e.origen_datos AS estado_elegibilidad,
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


def _validar_recorrido(fila: dict, cargo_clave: str, categoria_id: str) -> None:
    politica, _, _ = categoria_id.partition(":")
    monto = fila.get("tope_clp")
    textos_validos = all(
        isinstance(fila.get(campo), str) and fila[campo].strip() and fila[campo].isprintable()
        for campo in ("cargo", "nivel", "categoria")
    )
    if not (
        textos_validos
        and normalizar(fila["cargo"]) == cargo_clave
        and fila.get("categoria_id") == categoria_id == f"{politica}:{slug(fila['categoria'])}"
        and politica in POLITICAS
        and fila.get("politica") == politica
        and type(monto) is int and 0 < monto < 2**63
        and fila.get("tope_id") == id_tope(categoria_id)
        and fila.get("fuente") == fuente_para(politica)
        and fila.get("documento") == DOCUMENTO
        and fila.get("version") == VERSION
        and fila.get("base") == "por_documento"
        and fila.get("estado_elegibilidad") == ESTADO_PROPUESTA
        and fila.get("relaciones") == list(RELACIONES)
    ):
        raise ToolException(_INCOMPATIBLE)


def _consultar_recorrido(cargo: str, categoria: str) -> dict | None:
    """Diagnóstico interno: recupera el recorrido de Neo4j, no del JSON."""
    cargo_clave = _entrada(cargo, "El cargo")
    categoria_id, categoria_clave = _categoria(categoria)
    try:
        with sesion_neo4j(configuracion(), READ_ACCESS) as sesion:
            with sesion.begin_transaction(timeout=5) as tx:
                candidatos = tx.run(
                    _CANDIDATOS, proyecto=PROYECTO, cargo_clave=cargo_clave,
                    categoria_id=categoria_id, categoria_clave=categoria_clave,
                ).data()
                if not candidatos:
                    return None
                if any(not isinstance(fila, dict) for fila in candidatos):
                    raise ToolException(_INCOMPATIBLE)
                ids = [(fila.get("cargo_id"), fila.get("categoria_id")) for fila in candidatos]
                if any(
                    not isinstance(c, str) or not c.startswith("cargo:")
                    or not isinstance(cat, str)
                    or (categoria_id is not None and cat != categoria_id)
                    or (categoria_id is None and cat.partition(":")[2] != slug(categoria_clave))
                    for c, cat in ids
                ):
                    raise ToolException(_INCOMPATIBLE)
                if len(ids) != 1:
                    if (
                        categoria_id is None and len(ids) == 2
                        and ids[0][0] == ids[1][0] and ids[0][1] != ids[1][1]
                    ):
                        raise ToolException("La categoría es ambigua. Indica la política, por ejemplo P02:hotel o P03:hotel.")
                    raise ToolException(_INCOMPATIBLE)
                cargo_id, categoria_id = ids[0]
                filas = tx.run(
                    _RECORRIDO, proyecto=PROYECTO, cargo_id=cargo_id, categoria_id=categoria_id
                ).data()
    except ErrorGrafo as error:
        raise ToolException(str(error)) from None
    if not filas:
        return None
    if len(filas) != 1 or not isinstance(filas[0], dict):
        raise ToolException(_INCOMPATIBLE)
    _validar_recorrido(filas[0], cargo_clave, categoria_id)
    return filas[0]


def tope_para(cargo: str, categoria: str) -> dict | None:
    """Devuelve el tope de un recorrido único, o None si no hay recorrido.

    Si una categoría aparece en más de una política, pide una categoría cualificada.
    Un recorrido pertenece a la propuesta académica; no autoriza un gasto.
    """
    recorrido = _consultar_recorrido(cargo, categoria)
    return None if recorrido is None else {campo: recorrido[campo] for campo in _PUBLICOS}
