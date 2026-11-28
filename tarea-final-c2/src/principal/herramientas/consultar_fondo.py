"""Herramienta consultar_fondo: saldo de un fondo por rendir, leído a través del servidor MCP.

Dueño: Matías (c2tf/matias-react-seguridad). Firma en docs/contratos.md §3.
La lógica de saldo está en fondos.py (copiada de c1); el servidor MCP
(src/mcp_fondos/servidor.py) la expone y esta herramienta es su cliente.

Cómo funciona: arranca el servidor como proceso hijo (transporte stdio), le pide la
herramienta "consultar_fondo" y lo cierra. Todo con un tiempo máximo explícito
(TIEMPO_MAXIMO_MCP_SEG). Si algo falla, lanza ToolException con un mensaje de una línea:
el ReAct lo ve como observación y no recibe un saldo inventado.
"""

import asyncio
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import anyio
from langchain_core.tools import StructuredTool, ToolException
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.comun.config import CARPETA_PROYECTO
from src.comun.contrato import EstadoFondo

# Arrancar el proceso, iniciar la sesión y consultar tarda unos 4 s en un PC normal.
TIEMPO_MAXIMO_MCP_SEG = 20.0
HERRAMIENTA_MCP = "consultar_fondo"
_PREFIJO_ERROR_MCP = f"Error executing tool {HERRAMIENTA_MCP}: "
_CAMPOS = ("id_fondo", "responsable", "saldo_inicial", "saldo_actual", "gastos_aprobados")


def _parametros_servidor() -> StdioServerParameters:
    """Cómo arrancar el servidor MCP: el mismo Python, como módulo, desde tarea-final-c2/.

    Se le pasa el entorno completo del proceso. Sin `env`, la librería MCP solo copia unas
    pocas variables (HOME, PATH...) y deja fuera LD_LIBRARY_PATH; en Heroku el Python hijo
    no encontraba libpython3.12.so.1.0 y cada consultar_fondo fallaba al arrancar.
    """
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "src.mcp_fondos.servidor"],
        cwd=str(CARPETA_PROYECTO),
        env=dict(os.environ),
    )


def _a_estado_fondo(resultado) -> EstadoFondo:
    """Convierte la respuesta MCP en EstadoFondo, o lanza ToolException si no sirve."""
    texto = " ".join(getattr(parte, "text", "") for parte in resultado.content).strip()
    if resultado.isError:
        motivo = texto.removeprefix(_PREFIJO_ERROR_MCP).replace("\n", " ") or "error sin detalle"
        raise ToolException(f"consultar_fondo (MCP): {motivo}")
    datos = resultado.structuredContent
    if not isinstance(datos, dict):
        try:
            datos = json.loads(texto)
        except json.JSONDecodeError:
            raise ToolException("consultar_fondo (MCP): la respuesta del servidor no es un JSON válido.") from None
    if isinstance(datos, dict) and set(datos) == {"result"}:
        datos = datos["result"]
    if not isinstance(datos, dict) or not set(_CAMPOS) <= set(datos):
        raise ToolException("consultar_fondo (MCP): la respuesta no trae los campos de EstadoFondo.")
    return {campo: datos[campo] for campo in _CAMPOS}


async def consultar_fondo_por_mcp(id_fondo: str) -> EstadoFondo:
    """Pide el fondo al servidor MCP y devuelve su EstadoFondo (versión async).

    Lanza ToolException con un mensaje claro si el fondo no existe, si el servidor no
    responde a tiempo o si falla al arrancar.
    """
    id_fondo = str(id_fondo or "").strip()
    if not id_fondo:
        raise ToolException("consultar_fondo: falta id_fondo (por ejemplo FR-001).")
    try:
        with anyio.fail_after(TIEMPO_MAXIMO_MCP_SEG):
            async with stdio_client(_parametros_servidor()) as (lectura, escritura):
                async with ClientSession(lectura, escritura) as sesion:
                    await sesion.initialize()
                    resultado = await sesion.call_tool(HERRAMIENTA_MCP, {"id_fondo": id_fondo})
    except TimeoutError:
        raise ToolException(
            f"consultar_fondo: el servidor MCP de fondos no respondió en {TIEMPO_MAXIMO_MCP_SEG:g} s; "
            "no tengo el saldo."
        ) from None
    except ToolException:
        raise
    except Exception as error:
        detalle = str(error).replace("\n", " ").strip() or error.__class__.__name__
        raise ToolException(f"consultar_fondo: no se pudo usar el servidor MCP de fondos ({detalle}).") from None
    return _a_estado_fondo(resultado)


def _consultar_sincronico(id_fondo: str) -> EstadoFondo:
    """Versión para el grafo síncrono: corre la consulta async en un hilo propio.

    Un hilo aparte evita el error de asyncio.run cuando quien llama ya está dentro de un
    event loop (por ejemplo, el endpoint async /chat de FastAPI).
    """
    with ThreadPoolExecutor(max_workers=1) as ejecutor:
        return ejecutor.submit(asyncio.run, consultar_fondo_por_mcp(id_fondo)).result()


consultar_fondo = StructuredTool.from_function(
    func=_consultar_sincronico,
    coroutine=consultar_fondo_por_mcp,
    name="consultar_fondo",
    description=(
        "Consulta por MCP el fondo por rendir del gasto (id_fondo, por ejemplo FR-001) y devuelve "
        "su EstadoFondo: id_fondo, responsable, saldo_inicial, saldo_actual y gastos_aprobados. "
        "Úsala antes de validar para conocer el saldo disponible."
    ),
)
