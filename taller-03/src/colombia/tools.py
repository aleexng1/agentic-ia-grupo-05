import os

from langchain_mcp_adapters.client import MultiServerMCPClient


async def cargar_herramientas():
    cliente = MultiServerMCPClient(
        {
            "api_colombia": {
                "url": os.environ["API_COLOMBIA_MCP_URL"],
                "transport": "streamable_http",
            }
        }
    )
    return await cliente.get_tools()
