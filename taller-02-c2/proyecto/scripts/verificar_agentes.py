"""Comprueba las rutas de salud y las tarjetas públicas de los agentes."""

import argparse
import asyncio
import sys
from pathlib import Path

import httpx


_RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
if str(_RAIZ_PROYECTO) not in sys.path:
    sys.path.insert(0, str(_RAIZ_PROYECTO))

from src.comun.config import NOMBRES_AGENTES, url_agente, url_base


AGENTES = ("coordinador", *NOMBRES_AGENTES)
TIEMPO_LIMITE = 10.0


def _una_linea(texto: str) -> str:
    """Deja un mensaje de error en una sola línea."""
    return " ".join(texto.replace("\r", " ").replace("\n", " ").split())


async def _comprobar_salud(
    cliente: httpx.AsyncClient, nombre: str, url: str
) -> bool:
    """Consulta /salud, que la app única publica solo en la raíz."""
    url = url_base()
    for ruta in ("/salud",):
        try:
            respuesta = await cliente.get(f"{url}{ruta}")
        except httpx.TimeoutException:
            print(f"[ERROR] {nombre}: timeout al consultar {ruta} ({TIEMPO_LIMITE:g} s).")
            return False
        except httpx.RequestError as error:
            detalle = _una_linea(str(error)) or error.__class__.__name__
            print(f"[ERROR] {nombre}: no se pudo conectar a {url}: {detalle}")
            return False

        if respuesta.is_success:
            print(f"[OK] {nombre}: {ruta} respondió HTTP {respuesta.status_code}.")
            return True

        print(
            f"[ERROR] {nombre}: {ruta} respondió HTTP "
            f"{respuesta.status_code}."
        )
        return False

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
    # El coordinador vive en la raíz de la app única (URL_BASE) y cada agente
    # en URL_BASE/agentes/{nombre}.
    configurados = {
        nombre: url_base() if nombre == "coordinador" else url_agente(nombre)
        for nombre in AGENTES
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
        help="Comprueba solo este agente; por defecto revisa el coordinador y los cuatro agentes de la app única.",
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
