"""Carga en Redis un documento por política, sin borrar claves ajenas."""

import hashlib
import os
import re
import sys

from src.config import CARPETA_PROYECTO

RUTA_POLITICA = CARPETA_PROYECTO / "datos" / "politica_ficticia.md"
PATRON_POLITICA = re.compile(r"(?m)^## (P\d{2}) — (.+?)\s*$")


def separar_politicas(texto: str) -> list[dict]:
    """Devuelve P01-P10, adjuntando RG-01-RG-09 a cada fragmento."""
    encabezado_reglas = re.search(r"(?m)^## Reglas generales\s*$", texto)
    if encabezado_reglas is None:
        raise ValueError("No se encontró la sección de reglas generales.")
    inicio_reglas = encabezado_reglas.start()
    siguiente_seccion = re.search(r"(?m)^## ", texto[encabezado_reglas.end():])
    fin_reglas = (
        encabezado_reglas.end() + siguiente_seccion.start()
        if siguiente_seccion
        else len(texto)
    )
    reglas = texto[inicio_reglas:fin_reglas].strip()
    if not all(re.search(rf"\bRG-{numero:02d}\b", reglas) for numero in range(1, 10)):
        raise ValueError("La sección general debe contener RG-01 a RG-09.")

    encabezados = list(PATRON_POLITICA.finditer(texto))
    if [coincidencia.group(1) for coincidencia in encabezados] != [
        f"P{numero:02d}" for numero in range(1, 11)
    ]:
        raise ValueError("Se esperaba exactamente una política para cada código P01-P10.")

    fragmentos = []
    for indice, encabezado in enumerate(encabezados):
        fin = encabezados[indice + 1].start() if indice + 1 < len(encabezados) else len(texto)
        politica = encabezado.group(1)
        nombre = encabezado.group(2).strip()
        texto_politica = texto[encabezado.start():fin].strip()
        fragmentos.append({
            "politica": nombre,
            "codigo": politica,
            # Este contenido se entrega al agente; no se usa para calcular embeddings.
            "texto": f"{reglas}\n\n{texto_politica}",
            "texto_busqueda": texto_politica,
            "fuente": f"datos/politica_ficticia.md#{politica}",
        })
    return fragmentos


def _configuracion() -> tuple[str, str, str]:
    """Valida configuración sin incluir sus valores en errores o trazas."""
    valores = tuple(os.getenv(nombre, "").strip() for nombre in (
        "REDIS_URL", "REDIS_PREFIJO", "EMBEDDING_MODEL"
    ))
    if not all(valores):
        raise RuntimeError("Falta REDIS_URL, REDIS_PREFIJO o EMBEDDING_MODEL en el entorno.")
    return valores


def _recursos(redis_url: str, prefijo: str, modelo: str):
    """Crea cliente y vector store con reintentos del proveedor desactivados."""
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from langchain_redis import RedisVectorStore

    embeddings = GoogleGenerativeAIEmbeddings(model=modelo, max_retries=0)
    vector_store = RedisVectorStore(
        embeddings=embeddings,
        index_name=prefijo,
        redis_url=redis_url,
    )
    return embeddings, vector_store


def main() -> None:
    """Indexa diez documentos con identificadores estables para actualizarlos."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    redis_url, prefijo, modelo = _configuracion()
    fragmentos = separar_politicas(RUTA_POLITICA.read_text(encoding="utf-8"))

    # Hash estable y ámbito de prefijo: reejecutar actualiza los mismos IDs.
    ids = [f"{prefijo}:{trozo['codigo']}" for trozo in fragmentos]
    try:
        from langchain_core.documents import Document

        _, vector_store = _recursos(redis_url, prefijo, modelo)
        documentos = [
            Document(
                page_content=trozo["texto_busqueda"],
                metadata={
                    "politica": trozo["politica"],
                    "codigo": trozo["codigo"],
                    "fuente": trozo["fuente"],
                    "texto_completo": trozo["texto"],
                    "contenido_sha256": hashlib.sha256(
                        trozo["texto"].encode("utf-8")
                    ).hexdigest(),
                },
            )
            for trozo in fragmentos
        ]
        vector_store.add_documents(documents=documentos, ids=ids)
    except Exception as error:
        # No propagar mensajes del SDK: algunos incluyen URLs o detalles sensibles.
        raise RuntimeError(
            f"No se pudo cargar el índice Redis ({type(error).__name__}). "
            "Verifica conexión, memoria y cuotas del proveedor de embeddings."
        ) from None

    print(f"Carga completa: {len(fragmentos)} políticas en el índice configurado.")


if __name__ == "__main__":
    main()
