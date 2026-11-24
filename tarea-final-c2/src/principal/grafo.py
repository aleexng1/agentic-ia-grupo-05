"""Agente principal (LangGraph): router → uno de los tres flujos.

Dueño: Alex (c2tf/alex-integracion). Contratos en docs/contratos.md.

    entrada (/chat) ──> router ──┬─> consulta_politica   (RAG + GraphRAG, sin ReAct)
                                 ├─> revisar_gasto       (ReAct con parada + A2A al verificador)
                                 └─> fuera_de_alcance    (rechazo explicado, sin herramientas)

El principal es router Y worker: enruta y además ejecuta el trabajo de cada flujo.
"""


def construir_grafo():
    """Arma y compila el grafo LangGraph del agente principal.

    Nodos: "router" (src/principal/router.py) y un nodo por flujo (src/principal/flujos/).
    Arista condicional desde "router" según la ruta elegida. Usa un checkpointer por
    thread_id para la memoria de conversación (en el despliegue, Postgres: ver docs/reparto.md).
    """
    raise NotImplementedError("construir_grafo: pendiente (Alex, c2tf/alex-integracion).")


async def responder(thread_id: str, texto: str, imagen: dict | None = None) -> dict:
    """Atiende un mensaje de /chat y devuelve el diccionario de respuesta de docs/contratos.md.

    Pasos: crear id_ejecucion, medir el tiempo, invocar el grafo con thread_id, juntar ruta,
    pasos, herramientas usadas, si hubo A2A y estado_final; guardar la fila con
    src/comun/registro.guardar_ejecucion y devolver
    {"id_ejecucion", "thread_id", "ruta", "respuesta", "estado_final"}.
    `imagen` es {"mime_type", "datos_base64"} o None (formato en docs/contratos.md).
    Mientras no exista, api/app.py convierte el NotImplementedError en HTTP 501.
    """
    raise NotImplementedError("el router del agente principal todavía no existe (Alex, c2tf/alex-integracion).")
