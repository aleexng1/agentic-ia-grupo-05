"""El router debe acertar al menos 13 de los 15 casos de casos_router.json.

Llama al modelo de verdad: necesita GOOGLE_API_KEY en .env.
"""

from scripts.test_router import cargar_casos, evaluar

MINIMO = 13


def test_casos_bien_formados():
    casos = cargar_casos()
    assert len(casos) == 15
    for ruta in ("preventa", "postventa", "generica"):
        assert sum(c["esperado"] == ruta for c in casos) == 5


def test_router_acierta_al_menos_13_de_15():
    resultados = evaluar()
    aciertos = sum(r["ok"] for r in resultados)
    fallados = [f"{r['mensaje']!r}: esperado {r['esperado']}, obtenido {r['obtenido']}"
                for r in resultados if not r["ok"]]
    assert aciertos >= MINIMO, f"{aciertos}/{len(resultados)} aciertos. Fallados: {fallados}"
