"""Plan offline o carga autorizada del grafo Cargo → Nivel → Categoría → Tope."""

import argparse
import hashlib
import json
from contextlib import contextmanager
from contextvars import ContextVar

from neo4j import WRITE_ACCESS

from src.conocimiento.grafo.catalogo import (
    PROYECTO,
    RUTA_CATALOGO,
    Catalogo,
    ErrorCatalogo,
    conteos,
    id_tope,
    leer_catalogo,
    normalizar,
)
from src.conocimiento.grafo.conexion import ErrorGrafo, configuracion, sesion_neo4j

_DESTINO_CONFIRMADO = ContextVar("destino_graphrag_confirmado", default=None)
_RESTRICCION = """
CREATE CONSTRAINT g05_c2_graphrag_proyecto_id IF NOT EXISTS
FOR (n:Grupo05C2GraphRAG) REQUIRE (n.proyecto, n.id) IS UNIQUE
"""
# Solo se interpola estructura fija del código. Los datos entran exclusivamente por parámetros.
_NODOS = {
    etiqueta: f"""
    UNWIND $filas AS fila
    MERGE (n:Grupo05C2GraphRAG:{etiqueta} {{proyecto: $proyecto, id: fila.id}})
    ON CREATE SET n += fila, n.huella = $huella
    """
    for etiqueta in ("Cargo", "Nivel", "Categoria", "Tope")
}
_ARISTAS = {
    tipo: f"""
    UNWIND $filas AS fila
    MATCH (a:Grupo05C2GraphRAG:{origen} {{proyecto: $proyecto, id: fila.origen}})
    MATCH (b:Grupo05C2GraphRAG:{destino} {{proyecto: $proyecto, id: fila.destino}})
    MERGE (a)-[r:{tipo} {{proyecto: $proyecto}}]->(b)
    ON CREATE SET r.origen_datos = fila.origen_datos
    """
    for tipo, origen, destino in (
        ("TIENE_NIVEL", "Cargo", "Nivel"),
        ("PUEDE_RENDIR", "Nivel", "Categoria"),
        ("TIENE_TOPE", "Categoria", "Tope"),
    )
}
# Incluye aristas internas aunque pierdan su propiedad proyecto, y aristas del
# proyecto conectadas a un nodo ajeno. Un vínculo de otra extensión queda fuera.
_INVENTARIO = """
MATCH (n:Grupo05C2GraphRAG {proyecto: $proyecto})
RETURN labels(n) AS etiquetas, properties(n) AS propiedades,
       null AS tipo, null AS origen, null AS destino
UNION ALL
MATCH (n:Grupo05C2GraphRAG {proyecto: $proyecto})-[r]-(vecino)
WHERE r.proyecto = $proyecto OR (vecino:Grupo05C2GraphRAG AND vecino.proyecto = $proyecto)
WITH DISTINCT r
WITH r, startNode(r) AS a, endNode(r) AS b
RETURN null AS etiquetas, properties(r) AS propiedades, type(r) AS tipo,
       CASE WHEN a:Grupo05C2GraphRAG AND a.proyecto = $proyecto THEN a.id END AS origen,
       CASE WHEN b:Grupo05C2GraphRAG AND b.proyecto = $proyecto THEN b.id END AS destino
"""


@contextmanager
def confirmar_carga(destino: str):
    """Contexto explícito para un operador humano autorizado; no otorga privilegios."""
    token = _DESTINO_CONFIRMADO.set(destino)
    try:
        yield
    finally:
        _DESTINO_CONFIRMADO.reset(token)


def _filas(catalogo: Catalogo) -> tuple[dict, dict]:
    org = catalogo.organizacion_ficticia
    normativa = catalogo.normativa
    nodos = {
        "Cargo": [
            {"id": c.id, "nombre": c.nombre, "clave": normalizar(c.nombre), "origen_datos": catalogo.estado}
            for c in org.cargos
        ],
        "Nivel": [
            {"id": n.id, "nombre": n.nombre, "origen_datos": catalogo.estado} for n in org.niveles
        ],
        "Categoria": [
            {"id": c.id, "nombre": c.nombre, "clave": normalizar(c.nombre), "politica": c.id.split(":")[0]}
            for c in normativa.categorias
        ],
        "Tope": [
            {"id": id_tope(c.id), "tope_clp": c.tope_clp, "fuente": c.fuente, "codigo": normativa.codigo,
             "version": normativa.version, "base": "por_documento"}
            for c in normativa.categorias
        ],
    }
    aristas = {
        "TIENE_NIVEL": [
            {"origen": c.id, "destino": c.nivel_id, "origen_datos": catalogo.estado} for c in org.cargos
        ],
        "PUEDE_RENDIR": [
            {"origen": r.nivel_id, "destino": id_categoria, "origen_datos": catalogo.estado}
            for r in org.elegibilidad_propuesta for id_categoria in r.categorias
        ],
        "TIENE_TOPE": [
            {"origen": c.id, "destino": id_tope(c.id), "origen_datos": normativa.codigo}
            for c in normativa.categorias
        ],
    }
    return nodos, aristas


def _validar_inventario(inventario: list[dict], nodos: dict, aristas: dict, huella: str) -> None:
    esperados = {
        (None, fila["id"], None): (
            {"Grupo05C2GraphRAG", etiqueta}, {**fila, "proyecto": PROYECTO, "huella": huella},
        )
        for etiqueta, filas in nodos.items() for fila in filas
    }
    esperados.update({
        (tipo, fila["origen"], fila["destino"]): (
            set(), {"proyecto": PROYECTO, "origen_datos": fila["origen_datos"]},
        )
        for tipo, filas in aristas.items() for fila in filas
    })
    mensaje = "El inventario de GraphRAG no coincide con el catálogo; no se repararán datos existentes."
    for fila in inventario:
        propiedades = fila["propiedades"]
        if fila["tipo"] is None:
            if propiedades.get("huella") != huella:
                raise ErrorGrafo("Ya existe otro catálogo del proyecto. No se actualizará automáticamente.")
            clave = (None, propiedades.get("id"), None)
        else:
            clave = (fila["tipo"], fila["origen"], fila["destino"])
        if not all(p is None or isinstance(p, str) for p in clave):
            raise ErrorGrafo(mensaje)
        etiquetas_ref, propiedades_ref = esperados.pop(clave, (None, {}))
        if (
            set(fila["etiquetas"] or ()) != etiquetas_ref
            or propiedades != propiedades_ref
            or any(type(propiedades[k]) is not type(valor) for k, valor in propiedades_ref.items())
        ):
            raise ErrorGrafo(mensaje)
    if esperados:
        raise ErrorGrafo(mensaje)


def cargar_grafo(ruta_datos: str) -> dict:
    """Carga una propuesta validada, solo con confirmación humana del destino exacto."""
    confirmado = _DESTINO_CONFIRMADO.get()
    if confirmado is None:
        raise ErrorGrafo("La carga requiere una confirmación explícita del destino de Neo4j.")
    catalogo = leer_catalogo(ruta_datos)
    ajustes = configuracion()
    if confirmado != ajustes.destino:
        raise ErrorGrafo("La confirmación no coincide con el destino configurado de Neo4j.")
    nodos, aristas = _filas(catalogo)
    huella = hashlib.sha256(json.dumps(catalogo.model_dump(), sort_keys=True).encode("utf-8")).hexdigest()
    with sesion_neo4j(ajustes, WRITE_ACCESS) as sesion:
        # Neo4j separa las escrituras de esquema de las escrituras de datos.
        with sesion.begin_transaction(timeout=20) as tx:
            tx.run(_RESTRICCION).consume()
            tx.commit()
        with sesion.begin_transaction(timeout=10) as tx:
            inventario = tx.run(_INVENTARIO, proyecto=PROYECTO).data()
            if not inventario:
                for etiqueta, filas in nodos.items():
                    tx.run(_NODOS[etiqueta], proyecto=PROYECTO, filas=filas, huella=huella).consume()
                for tipo, filas in aristas.items():
                    tx.run(_ARISTAS[tipo], proyecto=PROYECTO, filas=filas).consume()
                inventario = tx.run(_INVENTARIO, proyecto=PROYECTO).data()
            _validar_inventario(inventario, nodos, aristas, huella)
            tx.commit()
    return conteos(catalogo)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    modos = parser.add_mutually_exclusive_group(required=True)
    modos.add_argument("--plan", action="store_true", help="Validación local sin conexión.")
    modos.add_argument("--cargar", action="store_true", help="Solo con autorización humana.")
    parser.add_argument("--ruta", default=str(RUTA_CATALOGO), help="Catálogo JSON dentro de datos/.")
    parser.add_argument("--confirmar-destino", help="Destino exacto: esquema://host:puerto/base.")
    args = parser.parse_args(argv)
    if args.plan and args.confirmar_destino is not None:
        parser.error("--plan no admite confirmación de destino.")
    if args.cargar and not args.confirmar_destino:
        parser.error("--cargar exige --confirmar-destino y autorización humana.")

    try:
        if args.plan:
            catalogo = leer_catalogo(args.ruta)
            print(f"PASS: {catalogo.normativa.codigo} v{catalogo.normativa.version}; catálogo v{catalogo.version_catalogo}")
            print(f"Estado: {catalogo.estado}")
            print(json.dumps(conteos(catalogo)))
            print("SIN Neo4j, SIN .env, SIN escrituras")
        else:
            with confirmar_carga(args.confirmar_destino):
                print(json.dumps(cargar_grafo(args.ruta)))
    except (ErrorGrafo, ErrorCatalogo) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
