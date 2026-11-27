"""Demostración local de la propuesta Fondo → Cargo → Nivel → Categoría → Tope."""

import json

from src.conocimiento.grafo.catalogo import (
    ESTADO_PROPUESTA,
    RUTA_CATALOGO,
    RUTA_POLITICA,
    _topes_documentados,
    leer_catalogo,
)

from src.conocimiento.grafo.fondos import (
    CARGO_PROPUESTO,
    FONDO_PROPUESTO,
    FUENTE_FONDOS,
    TIPO_VINCULO,
    _saldos_iniciales,
)


def demostrar(id_fondo: str = FONDO_PROPUESTO, categoria_id: str = "P03:hotel") -> dict:
    """Compara la lectura documental con un recorrido del catálogo v1 en memoria."""
    topes = _topes_documentados(RUTA_POLITICA.read_text(encoding="utf-8"))
    tope = topes.get(categoria_id)
    resultado = {
        "documental": None if tope is None else {"tope_clp": tope[1], "fuente": tope[2]},
        "relacional_propuesto": None,
    }
    if tope is None or id_fondo != FONDO_PROPUESTO:
        return resultado

    catalogo = leer_catalogo(str(RUTA_CATALOGO))
    if catalogo.version_catalogo != 1:
        raise ValueError("El prototipo requiere el catálogo organizacional v1.")
    org = catalogo.organizacion_ficticia
    cargo = next((c for c in org.cargos if c.id == CARGO_PROPUESTO), None)
    if cargo is None:
        raise ValueError("El cargo del vínculo propuesto no existe en el catálogo v1.")
    nivel = next(n for n in org.niveles if n.id == cargo.nivel_id)
    if not any(e.nivel_id == nivel.id and categoria_id in e.categorias for e in org.elegibilidad_propuesta):
        return resultado
    categoria = next(c for c in catalogo.normativa.categorias if c.id == categoria_id)

    saldo_inicial = _saldos_iniciales()[id_fondo]

    resultado["relacional_propuesto"] = {
        "recorrido": [id_fondo, cargo.nombre, nivel.nombre, categoria.id],
        "vinculo_fondo_cargo": {"tipo": TIPO_VINCULO, "estado": ESTADO_PROPUESTA},
        "tope_clp": categoria.tope_clp,
        "fuente_tope": categoria.fuente,
        "saldo_inicial_ficticio_clp": saldo_inicial,
        "fuente_saldo_inicial": FUENTE_FONDOS,
    }
    return resultado


if __name__ == "__main__":
    print(json.dumps(demostrar(), ensure_ascii=False, indent=2))
