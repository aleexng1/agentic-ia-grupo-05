"""Herramienta consultar_fondo: saldo de un fondo por rendir, a través del servidor MCP.

Dueño: Matías (c2tf/matias-react-seguridad). Firma en docs/contratos.md.
La lógica de saldo ya existe en fondos.py (copiada de c1); el servidor MCP
(src/mcp_fondos/servidor.py) la expone y esta herramienta es su cliente.
"""


def consultar_fondo(id_fondo: str) -> dict:
    """Devuelve el EstadoFondo (src/comun/contrato.py) del fondo pedido, leído por MCP.

    {"id_fondo", "responsable", "saldo_inicial", "saldo_actual", "gastos_aprobados"}.
    Debe llamar a la herramienta "consultar_fondo" del servidor MCP. Si el MCP no responde,
    lanza ToolException con un mensaje claro (el ReAct lo ve como observación): no
    devuelve un saldo inventado. Al implementarla, decorarla con @tool de langchain_core.
    """
    raise NotImplementedError("consultar_fondo: pendiente (Matías, c2tf/matias-react-seguridad).")
