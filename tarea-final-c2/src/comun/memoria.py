"""Memoria persistente por thread_id: el checkpointer de LangGraph en Postgres.

Dueño: Sebastián (c2tf/sebastian-despliegue). Con esto, una conversación retoma su estado
después de una interrupción o un reinicio del dyno, porque vive en Postgres y no en memoria.

Uso (lo arma el grafo de Alex):
    grafo = construir_grafo(checkpointer=crear_checkpointer())
    grafo.invoke(entrada, {"configurable": {"thread_id": thread_id}})
"""

import psycopg
from psycopg.rows import dict_row

from langgraph.checkpoint.postgres import PostgresSaver

from src.comun.registro import url_postgres


def crear_checkpointer() -> PostgresSaver:
    """Devuelve un PostgresSaver listo para usar, con sus tablas creadas si faltaban.

    Abre una conexión que vive lo que dura el proceso. autocommit=True es lo que pide
    PostgresSaver; dict_row, el formato de fila que espera.
    """
    conexion = psycopg.connect(
        url_postgres(), autocommit=True, prepare_threshold=0, row_factory=dict_row
    )
    saver = PostgresSaver(conexion)
    saver.setup()
    return saver
