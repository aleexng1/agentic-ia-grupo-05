"""El router puede fallar como máximo 2 casos de casos_router.json, sea cual sea el total.

Llama al modelo de verdad: necesita GOOGLE_API_KEY en .env.
"""

from scripts.test_router import cargar_casos, evaluar

MAX_FALLOS = 2
RUTAS = {"preventa", "postventa", "generica"}


def test_casos_bien_formados():
    casos = cargar_casos()
    for caso in casos:
        assert caso["mensaje"].strip()
        assert caso["esperado"] in RUTAS, caso
    for ruta in RUTAS:
        assert sum(c["esperado"] == ruta for c in casos) >= 5, f"faltan casos de {ruta}"


def test_router_falla_como_maximo_2_casos():
    resultados = evaluar()
    fallados = [f"{r['mensaje']!r}: esperado {r['esperado']}, obtenido {r['obtenido']}"
                for r in resultados if not r["ok"]]
    aciertos = len(resultados) - len(fallados)
    assert len(fallados) <= MAX_FALLOS, f"{aciertos}/{len(resultados)} aciertos. Fallados: {fallados}"
