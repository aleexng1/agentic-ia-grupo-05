"""Lectura de la extensión académica Fondo → Cargo → Nivel → Categoría → Tope."""

import hashlib
import json
import re

from langchain_core.tools import ToolException
from neo4j import READ_ACCESS

from src.conocimiento.grafo.cargar_grafo import _INVENTARIO, _filas, _validar_inventario
from src.conocimiento.grafo.catalogo import (
    DATOS,
    ESTADO_PROPUESTA,
    PROYECTO,
    RELACIONES,
    RUTA_CATALOGO,
    Catalogo,
    ErrorCatalogo,
    _objeto_sin_duplicados,
    id_tope,
    leer_catalogo,
    normalizar,
)
from src.conocimiento.grafo.conexion import ErrorGrafo, configuracion, sesion_neo4j
from src.conocimiento.grafo.consultar import _categoria

# Cambiar solo tras aprobar el catálogo de la extensión y verificar la carga autorizada.
CONSULTA_FONDOS_HABILITADA = False
FONDO_PROPUESTO = "FR-020"
CARGO_PROPUESTO = "cargo:jefe-de-tienda"
TIPO_VINCULO = "FONDO_VINCULADO_A_CARGO_PROPUESTO"
FUENTE_FONDOS = "datos/fondos_ficticios.json"
PROYECTO_FONDOS = "grupo05-tarea-final-c2-graphrag-fondos-propuesta-1"
ID_FONDO = re.compile(r"fr-[0-9]{3}", re.IGNORECASE | re.ASCII)

_ETIQUETA = "Grupo05C2GraphRAGFondoPropuesto"
_PARAMETROS = {
    "proyecto": PROYECTO,
    "extension": PROYECTO_FONDOS,
    "fondo": FONDO_PROPUESTO,
    "cargo": CARGO_PROPUESTO,
    "fuente": FUENTE_FONDOS,
    "estado": ESTADO_PROPUESTA,
}
_INVALIDA = "El inventario de la extensión de fondos en Neo4j no coincide con la propuesta."
_NODOS = """
MATCH (f)
WHERE f:Grupo05C2GraphRAGFondoPropuesto OR f.proyecto = $extension
RETURN labels(f) AS etiquetas, properties(f) AS propiedades
LIMIT 2
"""
_VINCULOS = """
MATCH (a)-[r]->(b)
WHERE type(r) = $tipo OR r.proyecto = $extension
   OR a:Grupo05C2GraphRAGFondoPropuesto OR a.proyecto = $extension
   OR b:Grupo05C2GraphRAGFondoPropuesto OR b.proyecto = $extension
RETURN type(r) AS tipo, properties(r) AS propiedades,
       a.proyecto AS origen_proyecto, a.id_fondo AS origen,
       b.proyecto AS destino_proyecto, b.id AS destino, labels(b) AS etiquetas_destino
LIMIT 2
"""
_RECORRIDO = """
MATCH camino =
    (f:Grupo05C2GraphRAGFondoPropuesto {proyecto: $extension, id_fondo: $fondo, fuente: $fuente})
    -[:FONDO_VINCULADO_A_CARGO_PROPUESTO {proyecto: $extension, estado: $estado}]->
    (c:Grupo05C2GraphRAG:Cargo {proyecto: $proyecto, id: $cargo})
    -[:TIENE_NIVEL {proyecto: $proyecto}]->(n:Grupo05C2GraphRAG:Nivel {proyecto: $proyecto})
    -[:PUEDE_RENDIR {proyecto: $proyecto}]->
    (cat:Grupo05C2GraphRAG:Categoria {proyecto: $proyecto, id: $categoria})
    -[:TIENE_TOPE {proyecto: $proyecto}]->(t:Grupo05C2GraphRAG:Tope {proyecto: $proyecto})
RETURN f.id_fondo AS fondo, c.id AS cargo_id, c.nombre AS cargo, n.id AS nivel_id,
       n.nombre AS nivel, cat.id AS categoria_id, t.id AS tope_id, t.tope_clp AS tope_clp,
       t.fuente AS fuente, t.codigo AS documento, t.version AS version, t.base AS base,
       [rel IN relationships(camino) | type(rel)] AS relaciones
LIMIT 2
"""


def _saldos_iniciales() -> dict[str, int]:
    """Lee solo la referencia ficticia versionada; no consulta el saldo operativo."""
    try:
        datos = json.loads(
            (DATOS / "fondos_ficticios.json").read_text(encoding="utf-8"),
            object_pairs_hook=_objeto_sin_duplicados,
        )
        if type(datos) is not dict or datos.get("version") != "1.0" or type(datos.get("fondos")) is not list:
            raise ValueError
        saldos = {}
        for fondo in datos["fondos"]:
            id_fondo, saldo = fondo["id_fondo"], fondo["saldo_inicial"]
            if (
                not isinstance(id_fondo, str) or not ID_FONDO.fullmatch(id_fondo)
                or id_fondo != id_fondo.upper() or id_fondo in saldos
                or type(saldo) is not int or not 0 <= saldo < 2**63
            ):
                raise ValueError
            saldos[id_fondo] = saldo
        if FONDO_PROPUESTO not in saldos:
            raise ValueError
        return saldos
    except (OSError, ValueError, KeyError, TypeError, RecursionError):
        raise ErrorCatalogo("No se pudo verificar la referencia ficticia de saldos iniciales.") from None


def _catalogo_v1() -> Catalogo:
    catalogo = leer_catalogo(str(RUTA_CATALOGO))
    org = catalogo.organizacion_ficticia
    cargo = next((c for c in org.cargos if c.id == CARGO_PROPUESTO), None)
    if (
        catalogo.version_catalogo != 1 or cargo is None
        or not any(e.nivel_id == cargo.nivel_id and "P03:hotel" in e.categorias for e in org.elegibilidad_propuesta)
    ):
        raise ErrorCatalogo("El catálogo base no respalda el recorrido propuesto para FR-020 y P03:hotel.")
    return catalogo


def _verificar_base(tx, catalogo: Catalogo) -> None:
    nodos, aristas = _filas(catalogo)
    huella = hashlib.sha256(json.dumps(catalogo.model_dump(), sort_keys=True).encode("utf-8")).hexdigest()
    _validar_inventario(tx.run(_INVENTARIO, proyecto=PROYECTO).data(), nodos, aristas, huella)


def _verificar_extension(tx) -> bool:
    """Acepta únicamente un espacio vacío o el nodo y vínculo exactos."""
    nodos = tx.run(_NODOS, extension=PROYECTO_FONDOS).data()
    aristas = tx.run(_VINCULOS, extension=PROYECTO_FONDOS, tipo=TIPO_VINCULO).data()
    if not nodos and not aristas:
        return False
    nodo = {"etiquetas": [_ETIQUETA], "propiedades": {
        "proyecto": PROYECTO_FONDOS, "id_fondo": FONDO_PROPUESTO, "fuente": FUENTE_FONDOS,
    }}
    arista = {
        "tipo": TIPO_VINCULO, "propiedades": {"proyecto": PROYECTO_FONDOS, "estado": ESTADO_PROPUESTA},
        "origen_proyecto": PROYECTO_FONDOS, "origen": FONDO_PROPUESTO,
        "destino_proyecto": PROYECTO, "destino": CARGO_PROPUESTO,
    }
    if nodos == [nodo] and len(aristas) == 1:
        candidata = dict(aristas[0])
        etiquetas = candidata.pop("etiquetas_destino", None)
        if candidata == arista and etiquetas and set(etiquetas) == {"Cargo", "Grupo05C2GraphRAG"}:
            return True
    raise ErrorGrafo(_INVALIDA)


def _recuperar_recorrido(tx, catalogo: Catalogo, categoria_id: str) -> dict | None:
    org = catalogo.organizacion_ficticia
    cargo = next(c for c in org.cargos if c.id == CARGO_PROPUESTO)
    nivel = next(n for n in org.niveles if n.id == cargo.nivel_id)
    categoria = next(c for c in catalogo.normativa.categorias if c.id == categoria_id)
    elegible = any(e.nivel_id == nivel.id and categoria_id in e.categorias for e in org.elegibilidad_propuesta)
    filas = tx.run(_RECORRIDO, **_PARAMETROS, categoria=categoria_id).data()
    if not elegible and not filas:
        return None
    esperado = {
        "fondo": FONDO_PROPUESTO, "cargo_id": cargo.id, "cargo": cargo.nombre,
        "nivel_id": nivel.id, "nivel": nivel.nombre, "categoria_id": categoria.id,
        "tope_id": id_tope(categoria.id), "tope_clp": categoria.tope_clp, "fuente": categoria.fuente,
        "documento": catalogo.normativa.codigo, "version": catalogo.normativa.version, "base": "por_documento",
        "relaciones": [TIPO_VINCULO, *RELACIONES],
    }
    if not elegible or filas != [esperado] or type(filas[0]["tope_clp"]) is not int:
        raise ErrorGrafo("Neo4j no devolvió el recorrido íntegro esperado para el fondo.")
    return filas[0]


def recorrido_fondo(id_fondo: str, categoria: str) -> dict | None:
    """Devuelve evidencia de Neo4j y el saldo inicial; None si no hay vínculo propuesto."""
    if not CONSULTA_FONDOS_HABILITADA:
        raise ToolException("La consulta de GraphRAG con fondos aún no está habilitada.")
    if not isinstance(id_fondo, str) or not ID_FONDO.fullmatch(id_fondo.strip()):
        raise ToolException("Indica un identificador de fondo con formato FR-000.")
    id_fondo = id_fondo.strip().upper()
    categoria_id, clave = _categoria(categoria)
    try:
        saldos = _saldos_iniciales()
        if id_fondo not in saldos:
            raise ToolException("El fondo no figura en la referencia ficticia versionada.")
        catalogo = _catalogo_v1()
        categorias = [
            c.id for c in catalogo.normativa.categorias
            if (c.id == categoria_id if categoria_id else normalizar(c.nombre) == clave)
        ]
        if len(categorias) > 1:
            raise ToolException("La categoría es ambigua. Indica la política, por ejemplo P02:hotel o P03:hotel.")
        if not categorias:
            raise ToolException("La categoría no figura en el catálogo de viajes del grafo.")

        with sesion_neo4j(configuracion(), READ_ACCESS) as sesion:
            with sesion.begin_transaction(timeout=5) as tx:
                instalada = _verificar_extension(tx)
                if id_fondo != FONDO_PROPUESTO:
                    return None
                if not instalada:
                    raise ErrorGrafo("Falta en Neo4j el vínculo propuesto esperado para FR-020.")
                _verificar_base(tx, catalogo)
                recorrido = _recuperar_recorrido(tx, catalogo, categorias[0])
    except (ErrorCatalogo, ErrorGrafo) as error:
        raise ErrorGrafo(str(error)) from None
    if recorrido is None:
        return None
    return {
        **recorrido,
        "estado_vinculo": ESTADO_PROPUESTA,
        "saldo_inicial_ficticio_clp": saldos[id_fondo],
        "fuente_saldo_inicial": FUENTE_FONDOS,
    }
