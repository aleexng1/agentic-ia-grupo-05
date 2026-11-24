# Evidencia: MCP de fondos (Matías)

Corridas **LOCALES** del 2026-11-24.

| Archivo | Entrada | Ejecución observada | Resultado |
|---|---|---|---|
| `01-servidor-y-herramientas.txt` | `python -m src.mcp_fondos.servidor --listar`, y luego `consultar_fondo` con FR-020 y FR-999 | El cliente arranca el servidor MCP por stdio (igual que el agente), hace `initialize` y `list_tools` | Servidor `fondos-los-alerces` con una herramienta, `consultar_fondo`. FR-020 devuelve su fondo; FR-999 da un error claro de una línea, sin saldo inventado |
| `../react/01-veredicto-gs01.txt` | Caso GS-01 revisado por el ReAct con Gemini real | En la **vuelta 3 el modelo pide `consultar_fondo(FR-001)`** y la observación es la respuesta del servidor MCP | El saldo leído por MCP ($200.000) se usa en la revisión y queda en $192.200 después de aprobar |

Cómo funciona: `src/principal/herramientas/consultar_fondo.py` es el cliente MCP (tiempo máximo 20 s);
el servidor está en `src/mcp_fondos/servidor.py`. Detalle en `src/mcp_fondos/README.md`.
