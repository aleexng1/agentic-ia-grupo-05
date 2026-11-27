"""Contraste del contenido recuperado con el Markdown versionado."""

from functools import lru_cache

from src.conocimiento.rag.cargar_indice import RUTA_POLITICA, _preparar_documentos


@lru_cache(maxsize=1)
def _referencia() -> dict[str, tuple[str, str]]:
    """Referencia independiente de Redis; no sustituye una recuperación."""
    documentos = _preparar_documentos(RUTA_POLITICA.read_text(encoding="utf-8"))
    return {doc["fuente"]: (doc["politica"], doc["texto_completo"]) for doc in documentos}


def coincide_con_referencia(fuente: str, politica: str, texto: str) -> bool:
    return _referencia().get(fuente) == (politica, texto.replace("\r\n", "\n").strip())
