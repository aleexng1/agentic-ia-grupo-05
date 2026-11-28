"""Planifica, verifica o migra la extensión de fondos con autorización explícita."""

import argparse
import json

from neo4j import READ_ACCESS, WRITE_ACCESS

from src.conocimiento.grafo import fondos
from src.conocimiento.grafo.catalogo import Catalogo, ErrorCatalogo, conteos
from src.conocimiento.grafo.conexion import ErrorGrafo, configuracion, sesion_neo4j

_ALTA = """
MATCH (c:Grupo05C2GraphRAG:Cargo {proyecto: $proyecto, id: $cargo})
CREATE (f:Grupo05C2GraphRAGFondoPropuesto {proyecto: $extension, id_fondo: $fondo, fuente: $fuente})
CREATE (f)-[:FONDO_VINCULADO_A_CARGO_PROPUESTO {proyecto: $extension, estado: $estado}]->(c)
"""
_BAJA = """
MATCH (f:Grupo05C2GraphRAGFondoPropuesto {proyecto: $extension, id_fondo: $fondo, fuente: $fuente})
      -[r:FONDO_VINCULADO_A_CARGO_PROPUESTO {proyecto: $extension, estado: $estado}]->
      (:Grupo05C2GraphRAG:Cargo {proyecto: $proyecto, id: $cargo})
DELETE r, f
"""


def _migrar(catalogo: Catalogo, destino: str, operacion: str | None, esperada: bool) -> dict:
    ajustes = configuracion()
    if ajustes.destino != destino:
        raise ErrorGrafo("La confirmación no coincide con el destino configurado de Neo4j.")
    if operacion == "revertir" and fondos.CONSULTA_FONDOS_HABILITADA:
        raise ErrorGrafo("Deshabilita la consulta de fondos antes de revertir la extensión.")
    with sesion_neo4j(ajustes, WRITE_ACCESS if operacion else READ_ACCESS) as sesion:
        with sesion.begin_transaction(timeout=15) as tx:
            fondos._verificar_base(tx, catalogo)
            anterior = fondos._verificar_extension(tx)
            if anterior:
                fondos._recuperar_recorrido(tx, catalogo, "P03:hotel")
            cambio = bool(operacion) and anterior != esperada
            if cambio:
                consulta = _ALTA if operacion == "aplicar" else _BAJA
                tx.run(consulta, **fondos._PARAMETROS).consume()
                fondos._verificar_base(tx, catalogo)
                posterior = fondos._verificar_extension(tx)
                if posterior:
                    fondos._recuperar_recorrido(tx, catalogo, "P03:hotel")
            else:
                posterior = anterior
            if posterior != esperada:
                raise ErrorGrafo("El estado de la extensión no coincide con lo solicitado.")
            if cambio:
                tx.commit()
    return {"base_verificada": conteos(catalogo), "instalada": posterior, "cambio": cambio}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    modos = parser.add_mutually_exclusive_group(required=True)
    modos.add_argument("--plan", action="store_true", help="Verificación local sin conexión.")
    modos.add_argument("--verificar", choices=("ausente", "instalada"), help="Inspección remota de solo lectura.")
    modos.add_argument("--aplicar", action="store_true", help="Alta con autorización y un único escritor.")
    modos.add_argument("--revertir", action="store_true", help="Baja con autorización y lecturas deshabilitadas.")
    parser.add_argument("--confirmar-destino", help="Destino exacto: esquema://host:puerto/base.")
    args = parser.parse_args(argv)
    if args.plan and args.confirmar_destino is not None:
        parser.error("--plan no admite destino.")
    if not args.plan and not args.confirmar_destino:
        parser.error("La operación en Neo4j exige --confirmar-destino.")
    try:
        catalogo = fondos._catalogo_v1()
        fondos._saldos_iniciales()
        if args.plan:
            resultado = {
                "base_esperada": conteos(catalogo),
                "extension": fondos.PROYECTO_FONDOS,
                "vinculo_propuesto": [fondos.FONDO_PROPUESTO, fondos.CARGO_PROPUESTO],
            }
        else:
            operacion = "aplicar" if args.aplicar else "revertir" if args.revertir else None
            esperada = args.aplicar or args.verificar == "instalada"
            resultado = _migrar(catalogo, args.confirmar_destino, operacion, esperada)
        print(json.dumps(resultado, ensure_ascii=False))
    except (ErrorGrafo, ErrorCatalogo) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
