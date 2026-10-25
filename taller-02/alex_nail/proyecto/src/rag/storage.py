# Embeddings y vector store (Redis o FAISS según VECTOR_STORE). Único lugar donde se crea el modelo de embeddings.
import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[2]
DATA = RAIZ / "data"

# Las variables ya definidas en el entorno (p. ej. VECTOR_STORE=faiss en la línea de comandos) tienen prioridad.
load_dotenv(RAIZ / ".env")


def get_embeddings():
    """Modelo de embeddings de Google, leído SIEMPRE de EMBEDDING_MODEL, con caché en disco
    (data/cache_embeddings/) para no volver a pagar textos ni preguntas ya convertidos."""
    from langchain_classic.embeddings import CacheBackedEmbeddings
    from langchain_classic.storage import LocalFileStore
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    modelo = os.getenv("EMBEDDING_MODEL")
    if not modelo:
        raise RuntimeError("Falta EMBEDDING_MODEL en .env (ej. models/gemini-embedding-001).")
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("Falta GOOGLE_API_KEY en .env.")
    cache = DATA / "cache_embeddings"
    return CacheBackedEmbeddings.from_bytes_store(
        GoogleGenerativeAIEmbeddings(model=modelo),
        LocalFileStore(cache / "documentos"),
        namespace=f"{modelo}/",  # cada modelo tiene su propia caché
        # Caché aparte para preguntas: Gemini embebe distinto una pregunta (RETRIEVAL_QUERY) que un documento.
        query_embedding_cache=LocalFileStore(cache / "preguntas"),
        key_encoder="sha256",
        batch_size=100,  # guarda en caché cada lote apenas llega (no se pierde si la cuota se corta a mitad)
    )


def motor_actual() -> str:
    motor = os.getenv("VECTOR_STORE", "redis").strip().lower()
    if motor not in ("redis", "faiss"):
        raise RuntimeError(f"VECTOR_STORE debe ser 'redis' o 'faiss', no '{motor}'.")
    return motor


def get_redis_client():
    """Cliente Redis desde REDIS_URL, verificando que el servidor tenga búsqueda vectorial."""
    from redis import Redis
    from redis.exceptions import ConnectionError as RedisConnectionError
    from redis.exceptions import ResponseError

    url = os.getenv("REDIS_URL", "").strip()
    if not url:
        raise RuntimeError(
            "Falta REDIS_URL en .env. Agrega una línea como:\n"
            "  REDIS_URL=redis://localhost:6379\n"
            "Si tu Redis pide contraseña, inclúyela en la URL (mira .env.example).\n"
            "(o usa VECTOR_STORE=faiss para trabajar sin Redis)."
        )
    if not url.startswith(("redis://", "rediss://", "unix://")):
        raise RuntimeError(
            "REDIS_URL debe empezar con redis:// (o rediss:// si usa TLS). "
            "Revisa el .env: la línea debe ser REDIS_URL=redis://..., sin repetir el nombre de la variable."
        )

    cliente = Redis.from_url(url)
    try:
        cliente.ping()
    except RedisConnectionError as e:
        raise RuntimeError(f"No se pudo conectar a Redis ({type(e).__name__}). Revisa host, puerto y contraseña de REDIS_URL.") from None
    try:
        cliente.execute_command("FT._LIST")
    except ResponseError:
        raise RuntimeError(
            "El servidor Redis no tiene búsqueda vectorial (comando FT.* desconocido). "
            "Se necesita Redis 8 o redis-stack, no el redis-server de apt. "
            "Ej.: docker run -d -p 6379:6379 redis:8"
        ) from None
    return cliente


def get_vector_store(prefijo: str):
    """Vector store según VECTOR_STORE: Redis (índice {prefijo}, COSINE) o FAISS (data/{prefijo}/)."""
    embeddings = get_embeddings()

    if motor_actual() == "faiss":
        from langchain_community.vectorstores import FAISS

        carpeta = DATA / prefijo
        if (carpeta / "index.faiss").exists():
            return FAISS.load_local(
                str(carpeta), embeddings, allow_dangerous_deserialization=True, normalize_L2=True
            )

        import faiss
        from langchain_community.docstore.in_memory import InMemoryDocstore

        dimension = len(embeddings.embed_query("dimension"))
        # normalize_L2=True: con vectores unitarios la distancia L2² es 2·(1 − coseno).
        return FAISS(
            embedding_function=embeddings,
            index=faiss.IndexFlatL2(dimension),
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
            normalize_L2=True,
        )

    from langchain_redis import RedisConfig, RedisVectorStore

    config = RedisConfig(
        index_name=prefijo,
        redis_client=get_redis_client(),
        distance_metric="COSINE",
        metadata_schema=[{"name": "fuente", "type": "tag"}],
    )
    return RedisVectorStore(embeddings, config=config)


def guardar_faiss(store, prefijo: str) -> Path:
    carpeta = DATA / prefijo
    store.save_local(str(carpeta))
    return carpeta


def a_parecido(puntaje: float, motor: str | None = None) -> float:
    """Convierte el puntaje del motor a parecido coseno en [0, 1] (mayor = más parecido).

    - Redis COSINE entrega distancia = 1 − coseno            → parecido = 1 − d
    - FAISS (L2 con vectores normalizados) entrega d = 2·(1 − coseno) → parecido = 1 − d/2
    """
    motor = motor or motor_actual()
    parecido = 1 - puntaje if motor == "redis" else 1 - puntaje / 2
    return max(0.0, min(1.0, parecido))
