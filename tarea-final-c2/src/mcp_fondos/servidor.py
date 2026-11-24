"""Servidor MCP que expone la herramienta consultar_fondo.

Dueño: Matías (c2tf/matias-react-seguridad). Reutiliza la lógica de src/principal/herramientas/fondos.py
(copiada de c1), que lee datos/fondos_ficticios.json.
Se levantaría con:  python -m src.mcp_fondos.servidor
"""


def consultar_fondo(id_fondo: str) -> dict:
    """Herramienta MCP: devuelve el EstadoFondo del fondo pedido (docs/contratos.md).

    Si el fondo no existe, responde un error MCP con mensaje claro (no un saldo en cero).
    """
    raise NotImplementedError("consultar_fondo (MCP): pendiente (Matías, c2tf/matias-react-seguridad).")


def main() -> None:
    """Crea el servidor (paquete `mcp`, FastMCP), registra consultar_fondo y lo levanta."""
    raise NotImplementedError("servidor MCP: pendiente (Matías, c2tf/matias-react-seguridad).")


if __name__ == "__main__":
    main()
