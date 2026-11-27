"""Pruebas offline de la extensión separada para el caso FR-020."""

from src.conocimiento.grafo.prototipo_fondos.demo import demostrar


def test_relacion_propuesta_complementa_tope_documental():
    resultado = demostrar()
    assert resultado["documental"] == {"tope_clp": 325000, "fuente": "datos/politica_ficticia.md#P03"}
    assert resultado["relacional_propuesto"] == {
        "recorrido": ["FR-020", "Jefe de tienda", "Jefatura", "P03:hotel"],
        "vinculo_fondo_cargo": {
            "tipo": "FONDO_VINCULADO_A_CARGO_PROPUESTO",
            "estado": "propuesta_academica_pendiente_de_aprobacion",
        },
        "tope_clp": 325000,
        "fuente_tope": "datos/politica_ficticia.md#P03",
        "saldo_inicial_ficticio_clp": 20000,
        "fuente_saldo_inicial": "datos/fondos_ficticios.json",
    }


def test_otro_fondo_no_hereda_vinculo_aunque_el_documento_tenga_tope():
    assert demostrar("FR-001") == {
        "documental": {"tope_clp": 325000, "fuente": "datos/politica_ficticia.md#P03"},
        "relacional_propuesto": None,
    }
