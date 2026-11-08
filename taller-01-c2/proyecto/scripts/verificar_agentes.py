"""Comprueba las rutas de salud y las tarjetas públicas de los agentes."""

import argparse
import asyncio
import os

import httpx
from dotenv import load_dotenv


AGENTES = {
    "coordinador": ("URL_COORDINADOR", "http://127.0.0.1:8002"),
    "matias": ("URL_MATIAS", "http://127.0.0.1:8003"),
    "alex": ("URL_ALEX", "http://127.0.0.1:8004"),
    "eduardo": ("URL_EDUARDO", "http://127.0.0.1:8005"),
    "sebastian": ("URL_SEBASTIAN", "http://127.0.0.1:8006"),
}
TIEMPO_LIMITE = 10.0


def _una_linea(texto: str) -> str:
    """Deja un mensaje de error en una sola línea."""
    return " ".join(texto.replace("\r", " ").replace("\n", " ").split())


async def _comprobar_salud(
    cliente: httpx.AsyncClient, nombre: str, url: str
) -> bool:
    """Prueba primero /salud y usa /health si la primera ruta no existe."""
    for ruta in ("/salud", "/health"):
        try:
            respuesta = await cliente.get(f"{url}{ruta}")
        except httpx.TimeoutException:
            print(f"[ERROR] {nombre}: timeout al consultar {ruta} ({TIEMPO_LIMITE:g} s).")
            return False
        except httpx.RequestError as error:
            detalle = _una_linea(str(error)) or error.__class__.__name__
            print(f"[ERROR] {nombre}: no se pudo conectar a {url}: {detalle}")
            return False

        if respuesta.status_code == 404 and ruta == "/salud":
            continue
        if respuesta.is_success:
            print(f"[OK] {nombre}: {ruta} respondió HTTP {respuesta.status_code}.")
            return True

        print(
            f"[ERROR] {nombre}: {ruta} respondió HTTP "
            f"{respuesta.status_code}."
        )
        return False

    print(f"[ERROR] {nombre}: no existe la ruta /salud ni /health.")
    return False


async def _comprobar_tarjeta(
    cliente: httpx.AsyncClient, nombre: str, url: str
) -> bool:
    """Consulta la tarjeta A2A publicada por el servidor."""
    ruta = "/.well-known/agent-card.json"
    try:
        respuesta = await cliente.get(f"{url}{ruta}")
    except httpx.TimeoutException:
        print(f"[ERROR] {nombre}: timeout al consultar la tarjeta ({TIEMPO_LIMITE:g} s).")
        return False
    except httpx.RequestError as error:
        detalle = _una_linea(str(error)) or error.__class__.__name__
        print(f"[ERROR] {nombre}: no se pudo consultar la tarjeta: {detalle}")
        return False

    if not respuesta.is_success:
        print(f"[ERROR] {nombre}: la tarjeta respondió HTTP {respuesta.status_code}.")
        return False

    try:
        tarjeta = respuesta.json()
    except ValueError:
        print(f"[ERROR] {nombre}: la tarjeta no devolvió JSON válido.")
        return False

    nombre_tarjeta = tarjeta.get("name") if isinstance(tarjeta, dict) else None
    if not nombre_tarjeta:
        print(f"[ERROR] {nombre}: la respuesta no contiene el nombre de la tarjeta.")
        return False

    print(f"[OK] {nombre}: tarjeta A2A publicada como «{nombre_tarjeta}».")
    return True


async def _verificar_agente(
    cliente: httpx.AsyncClient, nombre: str, url: str
) -> bool:
    """Comprueba salud y tarjeta de un agente."""
    print(f"\nAgente {nombre} · {url}")
    salud_correcta = await _comprobar_salud(cliente, nombre, url)
    tarjeta_correcta = await _comprobar_tarjeta(cliente, nombre, url)
    return salud_correcta and tarjeta_correcta


async def _ejecutar(nombres: list[str]) -> int:
    """Consulta los servicios seleccionados en paralelo."""
    load_dotenv()
    # Si una variable está vacía (por ejemplo URL_MATIAS en el equipo de un compañero),
    # se usa la dirección local por defecto de ese agente.
    configurados = {
        nombre: (os.getenv(variable) or valor).strip().rstrip("/")
        for nombre, (variable, valor) in AGENTES.items()
    }

    async with httpx.AsyncClient(timeout=TIEMPO_LIMITE) as cliente:
        resultados = await asyncio.gather(
            *(
                _verificar_agente(cliente, nombre, configurados[nombre])
                for nombre in nombres
            )
        )

    return 0 if all(resultados) else 1


def main() -> int:
    """Interpreta opciones y ejecuta las comprobaciones."""
    parser = argparse.ArgumentParser(
        description="Comprueba salud y tarjeta A2A de los agentes configurados."
    )
    parser.add_argument(
        "--agente",
        choices=AGENTES,
        help="Comprueba solo este agente; por defecto revisa el coordinador y los cuatro agentes (puertos 8002 a 8006).",
    )
    argumentos = parser.parse_args()
    nombres = [argumentos.agente] if argumentos.agente else list(AGENTES)

    try:
        return asyncio.run(_ejecutar(nombres))
    except KeyboardInterrupt:
        print("Comprobación interrumpida.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
