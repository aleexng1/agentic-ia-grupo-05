# Herramientas del agente RAG: búsqueda de fragmentos en el vector store (Redis o FAISS).
import os

from src.rag.prompts import SIN_INDICE
from src.rag.storage import DATA, a_parecido, get_redis_client, get_vector_store, motor_actual


class IndiceVacio(Exception):
    """El índice no existe o no tiene documentos: hay que correr scripts/ingest.py."""


def documentos_en_indice(prefijo: str) -> int:
    """Cuenta documentos SIN llamar a Gemini ni crear nada (get_vector_store crearía un índice vacío)."""
    if motor_actual() == "redis":
        from redis.exceptions import ResponseError

        try:
            return int(get_redis_client().ft(prefijo).info()["num_docs"])
        except ResponseError:
            return 0  # el índice no existe
    import faiss

    archivo = DATA / prefijo / "index.faiss"
    return faiss.read_index(str(archivo)).ntotal if archivo.exists() else 0


def buscar_fragmentos(pregunta: str, k: int | None = None) -> list[dict]:
    """TOP_K fragmentos más cercanos a la pregunta, con su parecido entre 0 y 1 (mayor = más parecido)."""
    prefijo = os.getenv("PREFIJO")
    k = k or int(os.getenv("TOP_K", "3"))
    if not prefijo or documentos_en_indice(prefijo) == 0:
        raise IndiceVacio(SIN_INDICE.format(prefijo=prefijo))

    store = get_vector_store(prefijo)
    motor = motor_actual()
    # El store embebe la pregunta con get_embeddings() (con caché): no se embebe dos veces.
    resultados = store.similarity_search_with_score(pregunta, k=k)
    return [
        {
            "texto": doc.page_content,
            "fuente": doc.metadata.get("fuente", "?"),
            "pagina": doc.metadata.get("pagina", "?"),
            "parecido": float(a_parecido(puntaje, motor)),  # FAISS entrega numpy.float32, que la memoria no serializa
        }
        for doc, puntaje in resultados
    ]
