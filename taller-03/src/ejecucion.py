"""Ejecución del grafo exterior, compartida por main.py y promptfoo/provider.py."""
from dataclasses import dataclass, field

from langchain_core.messages import AIMessage, ToolMessage

MAX_LLAMADAS_TOOLS = 6
# cada vuelta (modelo -> tools) cuenta 2 pasos, más el paso final del modelo
RECURSION_LIMIT = MAX_LLAMADAS_TOOLS * 2 + 1


def a_texto(contenido) -> str:
    if isinstance(contenido, str):
        return contenido
    if isinstance(contenido, list):
        return "\n".join(
            b["text"] if isinstance(b, dict) and "text" in b else str(b)
            for b in contenido
        )
    return str(contenido)


@dataclass
class Resultado:
    respuesta: str | None = None
    ruta: list[str] = field(default_factory=list)  # nodos del grafo exterior, en orden
    tools: list[dict] = field(default_factory=list)  # nombre, args y caracteres de cada llamada
    veredicto: dict | None = None
    revision: dict | None = None  # la última revisión de la guardia de salida
    reintento: bool = False


async def ejecutar_grafo(agente, mensaje: str, thread_id: str, al_paso=None) -> Resultado:
    """Corre el grafo; al_paso(ruta, nodo, update) se llama por cada actualización (main.py la usa para imprimir)."""
    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": RECURSION_LIMIT}
    entrada = {"messages": [{"role": "user", "content": mensaje}]}
    resultado = Resultado()
    pendientes: dict = {}
    async for espacio, paso in agente.astream(
        entrada, config, stream_mode="updates", subgraphs=True
    ):
        for nodo, update in paso.items():
            update = update or {}
            if al_paso:
                padre = espacio[0].split(":")[0] if espacio else None
                al_paso(f"{padre}/{nodo}" if padre else nodo, nodo, update)
            if espacio:  # agente interno: de aquí salen las tools llamadas
                for msg in update.get("messages", []):
                    if isinstance(msg, AIMessage):
                        for llamada in msg.tool_calls:
                            pendientes[llamada["id"]] = llamada
                    elif isinstance(msg, ToolMessage):
                        resultado.tools.append({
                            "nombre": msg.name,
                            "args": pendientes.get(msg.tool_call_id, {}).get("args", {}),
                            "caracteres": len(a_texto(msg.content)),
                        })
                continue
            resultado.ruta.append(nodo)  # solo el grafo exterior define la respuesta final
            if update.get("veredicto"):
                resultado.veredicto = update["veredicto"]
            if update.get("revision"):
                resultado.revision = update["revision"]
                resultado.reintento = resultado.reintento or update["revision"]["accion"] == "reintentar"
            for msg in update.get("messages", []):
                if isinstance(msg, AIMessage) and not msg.tool_calls:
                    resultado.respuesta = a_texto(msg.content)
    return resultado
