# Prueba de punta a punta del vector store (Redis o FAISS según VECTOR_STORE) con un índice de prueba desechable.
# Uso: python scripts/test_storage.py   (o VECTOR_STORE=faiss python scripts/test_storage.py)
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.demo_embeddings import FRASES_EJEMPLO, coseno  # noqa: E402
from src.rag.storage import a_parecido, get_embeddings, get_redis_client, get_vector_store, motor_actual  # noqa: E402

PREGUNTA = "no tengo internet"
K = 2


def borrar_indice_redis(cliente, indice: str) -> None:
    """FT.DROPINDEX ... DD: borra el índice y solo los documentos de ese índice (sin SCAN del servidor)."""
    from redis.exceptions import ResponseError

    try:
        cliente.execute_command("FT.DROPINDEX", indice, "DD")
        print(f"Limpieza: índice '{indice}' y sus documentos borrados.")
    except ResponseError as e:
        if "unknown index" in str(e).lower() or "no such index" in str(e).lower():
            print(f"Limpieza: el índice '{indice}' no existía (nada que borrar).")
        else:
            raise


def probar(motor: str, indice: str, cliente) -> None:
    if motor == "redis":
        print(f"PING a Redis: {cliente.ping()}")
    store = get_vector_store(indice)
    print(f"Vector store listo: {type(store).__name__} (índice '{indice}')")

    store.add_texts(FRASES_EJEMPLO, metadatas=[{"fuente": "demo"}] * len(FRASES_EJEMPLO))
    print(f"Guardados {len(FRASES_EJEMPLO)} documentos con metadata {{'fuente': 'demo'}}")

    resultados = store.similarity_search_with_score(PREGUNTA, k=K)
    if len(resultados) != K:
        raise AssertionError(f"se esperaban {K} resultados y llegaron {len(resultados)}")

    # Verificación empírica de a_parecido: el parecido debe coincidir con el coseno calculado a mano.
    emb = get_embeddings()
    vp = emb.embed_query(PREGUNTA)
    coseno_real = dict(zip(FRASES_EJEMPLO, (coseno(vp, v) for v in emb.embed_documents(FRASES_EJEMPLO))))

    if motor == "redis":
        significado = "distancia coseno = 1 − parecido (0 = idéntico, 2 = opuesto)"
    else:
        significado = "distancia L2² con vectores normalizados = 2·(1 − parecido) (0 = idéntico, 4 = opuesto)"
    print(f"\nPregunta: {PREGUNTA!r} → {K} fragmentos más cercanos")
    print(f"  puntaje  = lo que entrega {motor}: {significado}  → menor es mejor")
    print("  parecido = a_parecido(puntaje), entre 0 y 1                         → mayor es mejor")
    print(f"\n  {'puntaje':>8} {'parecido':>9} {'coseno real':>12}  fragmento")
    for doc, puntaje in resultados:
        parecido = a_parecido(puntaje, motor)
        real = coseno_real[doc.page_content]
        print(f"  {puntaje:>8.4f} {parecido:>9.4f} {real:>12.4f}  {doc.page_content!r} {doc.metadata}")
        if not np.isclose(parecido, real, atol=1e-3):
            raise AssertionError(f"a_parecido ({parecido:.4f}) no coincide con el coseno real ({real:.4f})")
        if doc.metadata.get("fuente") != "demo":
            raise AssertionError(f"metadata inesperada: {doc.metadata}")
    print("\n  (coseno real = calculado con numpy; coincide con 'parecido', así que la fórmula de a_parecido es correcta)")


def main() -> int:
    try:
        motor = motor_actual()
        prefijo = os.getenv("PREFIJO")
        if not prefijo:
            raise RuntimeError("Falta PREFIJO en .env (ej. PREFIJO=equipo1).")
    except RuntimeError as e:
        print(f"FALLÓ: {e}")
        return 1

    indice = f"{prefijo}_test"
    print(f"Motor: {motor} · índice de prueba: {indice} (el índice real '{prefijo}' no se toca)\n")

    cliente = None
    try:
        if motor == "redis":
            cliente = get_redis_client()
        probar(motor, indice, cliente)
    except Exception as e:
        print(f"\nFALLÓ: {type(e).__name__}: {e}")
        return 1
    finally:
        if cliente is not None:
            try:
                borrar_indice_redis(cliente, indice)
            except Exception as e:
                print(f"ATENCIÓN: no se pudo borrar el índice '{indice}': {type(e).__name__}: {e}")
        elif motor == "faiss":
            print("Limpieza: FAISS quedó solo en memoria, no se guardó nada en disco.")

    print(f"\nOK: el vector store {motor} guarda, busca y convierte puntajes correctamente.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
