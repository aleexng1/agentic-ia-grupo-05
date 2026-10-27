import asyncio
import functools
import logging
import os
import sys
from collections import defaultdict

from langchain_core.runnables.config import ensure_config
from langchain_mcp_adapters.client import MultiServerMCPClient

from .registro import registrar

TOOLS_PERMITIDAS = {
    "list_colombia_resources", "get_api_reference",
    "search_items", "get_items_by_name", "get_item_by_id",
    "list_items", "list_items_paged",
    "get_cities_by_department", "get_natural_areas_by_department",
    "get_touristic_attractions_by_department", "get_country_info",
}

PAGE_SIZE_MAX = 50
TEXTO_MAX = 60
TIMEOUT_SEGUNDOS = 10
MAX_LLAMADAS = 6

MSG_PAGE_SIZE = f"pageSize no puede ser mayor a {PAGE_SIZE_MAX}. Vuelve a llamar con un valor de {PAGE_SIZE_MAX} o menos."
MSG_TEXTO = "El texto de búsqueda ('{campo}') no puede pasar de {max} caracteres. Acórtalo y vuelve a intentar."
MSG_TIMEOUT = f"La consulta tardó más de {TIMEOUT_SEGUNDOS} segundos y se canceló. Intenta de nuevo o responde con lo que ya tienes."
MSG_LIMITE = "Límite de consultas alcanzado; responde con lo que ya tienes"
MSG_ERROR = "La consulta falló ({tipo}). Intenta con otros datos o responde con lo que ya tienes."


class ContadorLlamadas:
    """Llamadas a tools por thread_id; guardia_entrada lo reinicia en cada pregunta."""

    def __init__(self):
        self._cuenta = defaultdict(int)

    @staticmethod
    def _thread() -> str:
        return ensure_config().get("configurable", {}).get("thread_id", "default")

    def reiniciar(self, thread_id: str) -> None:
        self._cuenta[thread_id] = 0

    def sumar(self) -> int:
        self._cuenta[self._thread()] += 1
        return self._cuenta[self._thread()]


CONTADOR = ContadorLlamadas()


def filtrar_permitidas(herramientas: list) -> list:
    permitidas = [h for h in herramientas if h.name in TOOLS_PERMITIDAS]
    for h in herramientas:
        if h.name not in TOOLS_PERMITIDAS:
            registrar("tools", "tool_ignorada", h.name)
    faltan = sorted(TOOLS_PERMITIDAS - {h.name for h in herramientas})
    if faltan:
        registrar("tools", "tool_faltante", ", ".join(faltan), logging.WARNING)
        print(f"Aviso: el servidor MCP no ofrece estas tools permitidas: {', '.join(faltan)}", file=sys.stderr)
    return permitidas


def validar_argumentos(args: dict) -> str | None:
    if (args.get("pageSize") or 0) > PAGE_SIZE_MAX:
        return MSG_PAGE_SIZE
    for campo in ("keyword", "name"):
        if len(str(args.get(campo) or "")) > TEXTO_MAX:
            return MSG_TEXTO.format(campo=campo, max=TEXTO_MAX)
    return None


def envolver(herramienta):
    """Copia la tool con una corrutina que valida, limita y pone timeout antes de llamar a la original."""
    original = herramienta.coroutine
    con_artefacto = herramienta.response_format == "content_and_artifact"

    def respuesta(texto: str):
        return (texto, None) if con_artefacto else texto

    @functools.wraps(original)
    async def protegida(*posicionales, **argumentos):
        if CONTADOR.sumar() > MAX_LLAMADAS:
            registrar("tools", "limite_llamadas", herramienta.name)
            return respuesta(MSG_LIMITE)
        motivo = validar_argumentos(argumentos)
        if motivo:
            registrar("tools", "argumento_invalido", f"{herramienta.name}: {motivo}")
            return respuesta(motivo)
        try:
            return await asyncio.wait_for(original(*posicionales, **argumentos), TIMEOUT_SEGUNDOS)
        except asyncio.TimeoutError:
            registrar("tools", "timeout", herramienta.name)
            return respuesta(MSG_TIMEOUT)
        except Exception as exc:
            registrar("tools", "error_tool", f"{herramienta.name}: {type(exc).__name__}")
            return respuesta(MSG_ERROR.format(tipo=type(exc).__name__))

    return herramienta.model_copy(update={"coroutine": protegida})


async def cargar_herramientas():
    cliente = MultiServerMCPClient(
        {
            "api_colombia": {
                "url": os.environ["API_COLOMBIA_MCP_URL"],
                "transport": "streamable_http",
            }
        }
    )
    herramientas = await cliente.get_tools()
    return [envolver(h) for h in filtrar_permitidas(herramientas)]
