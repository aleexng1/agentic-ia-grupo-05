"""El catálogo del supervisor: qué agentes están vivos, cómo se llaman y qué hacen."""

import asyncio
import os

from src.coordinador import cliente as remoto

LARGO_MAX_NOMBRE = 60
LARGO_MAX_DESCRIPCION = 300
NINGUNO = "ninguno"  # palabra reservada: significa "ningún agente aplica"


def urls_de_agentes():
    """Direcciones de los agentes que el supervisor puede usar, leídas del .env."""
    urls = [
        os.getenv("URL_VIAJES", "http://127.0.0.1:8000"),
        os.getenv("URL_RESTAURANTES", "http://127.0.0.1:8001"),
    ]
    sin_repetir = []
    for url in urls:
        url = url.rstrip("/")
        if url and url not in sin_repetir:
            sin_repetir.append(url)
    return sin_repetir


def _limpio(texto, largo):
    """Una línea y de largo acotado: la ficha la escribe otro programa, no hay que confiar en ella."""
    linea = " ".join(str(texto).split())
    return linea if len(linea) <= largo else linea[:largo] + "..."


def _nombre_unico(nombre, usados):
    """Evita nombres repetidos o iguales a 'ninguno', que confundirían al supervisor."""
    base = nombre or "Agente sin nombre"
    candidato, n = base, 1
    while candidato in usados or candidato.lower() == NINGUNO:
        n += 1
        candidato = f"{base} ({n})"
    return candidato


async def descubrir():
    """Lee la ficha de cada agente y arma un cliente para él.

    Devuelve una lista de dicts con nombre, descripcion, cliente y url. Un agente que no
    responde se avisa en una línea y se deja fuera: el supervisor sigue con los demás.
    """
    urls = urls_de_agentes()
    resultados = await asyncio.gather(*(remoto.obtener_cliente(u) for u in urls), return_exceptions=True)

    catalogo, nombres_usados = [], set()
    for url, resultado in zip(urls, resultados):
        if isinstance(resultado, remoto.ErrorRemoto):
            print(f"Aviso: sin agente en {url} ({resultado}). Sigo sin él.")
            continue
        if isinstance(resultado, BaseException):
            print(f"Aviso: sin agente en {url} ({type(resultado).__name__}). Sigo sin él.")
            continue
        ficha = remoto.FICHAS[url]
        nombre = _nombre_unico(_limpio(ficha.name, LARGO_MAX_NOMBRE), nombres_usados)
        nombres_usados.add(nombre)
        catalogo.append({
            "nombre": nombre,
            "descripcion": _limpio(ficha.description, LARGO_MAX_DESCRIPCION),
            "cliente": resultado,
            "url": url,
        })

    if not catalogo:
        print("Error: ningún agente respondió, así que el supervisor no tiene a quién delegar.")
    return catalogo
