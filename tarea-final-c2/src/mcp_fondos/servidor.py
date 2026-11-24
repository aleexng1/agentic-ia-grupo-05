"""Servidor MCP que expone la herramienta consultar_fondo (fondos por rendir ficticios).

Dueño: Matías (c2tf/matias-react-seguridad). Reutiliza la lógica de
src/principal/herramientas/fondos.py (copiada de c1), que lee datos/fondos_ficticios.json.

Se levanta con (desde tarea-final-c2/):  python -m src.mcp_fondos.servidor
Transporte stdio: el cliente (src/principal/herramientas/consultar_fondo.py) lo arranca como
proceso hijo, le habla por la entrada/salida estándar y lo cierra al terminar.
Por eso este módulo nunca escribe en stdout: los avisos van a stderr.
"""

from mcp.server.fastmcp import FastMCP

from src.principal.herramientas.fondos import fondo_inicial

NOMBRE_SERVIDOR = "fondos-los-alerces"

servidor = FastMCP(
    NOMBRE_SERVIDOR,
    instructions=(
        "Fondos por rendir FICTICIOS de Comercial Los Alerces SpA. "
        "consultar_fondo devuelve el saldo inicial registrado de un fondo; no modifica nada."
    ),
    log_level="WARNING",  # sin una línea por petición en la terminal; los errores sí se ven
)


@servidor.tool()
def consultar_fondo(id_fondo: str) -> dict:
    """Devuelve el EstadoFondo del fondo pedido: id_fondo, responsable, saldo_inicial,
    saldo_actual y gastos_aprobados (contratos.md §3 y §4).

    Es de solo lectura. Si el fondo no existe responde un error MCP con mensaje claro
    (nunca un saldo en cero ni un fondo inventado).
    """
    return fondo_inicial(str(id_fondo).strip())


async def listar_por_mcp() -> dict:
    """Arranca el servidor como lo hace el agente (proceso hijo, stdio) y le pide su lista de herramientas.

    Es la evidencia de "servidor MCP levantado con su lista de herramientas". Tiempo máximo explícito.
    """
    import anyio
    from mcp import ClientSession
    from mcp.client.stdio import stdio_client

    from src.principal.herramientas.consultar_fondo import TIEMPO_MAXIMO_MCP_SEG, _parametros_servidor

    with anyio.fail_after(TIEMPO_MAXIMO_MCP_SEG):
        async with stdio_client(_parametros_servidor()) as (lectura, escritura):
            async with ClientSession(lectura, escritura) as sesion:
                inicio = await sesion.initialize()
                herramientas = (await sesion.list_tools()).tools
    return {
        "servidor": inicio.serverInfo.name,
        "herramientas": [{"nombre": h.name, "descripcion": " ".join((h.description or "").split())} for h in herramientas],
    }


def main() -> None:
    """Sin argumentos levanta el servidor MCP por stdio. Con --listar muestra sus herramientas."""
    import sys

    if "--listar" in sys.argv[1:]:
        import asyncio
        import json

        try:
            print(json.dumps(asyncio.run(listar_por_mcp()), ensure_ascii=False, indent=2))
        except Exception as error:
            detalle = str(error).replace("\n", " ").strip() or error.__class__.__name__
            print(f"No se pudo levantar el servidor MCP de fondos: {detalle}", file=sys.stderr)
            raise SystemExit(1) from None
        return
    servidor.run()


if __name__ == "__main__":
    main()
