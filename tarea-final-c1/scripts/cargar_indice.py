"""Carga en Redis diez políticas y diez reglas, sin borrar claves ajenas."""

import argparse
import hashlib
import os
import re
import sys
from pathlib import Path

CARPETA_PROYECTO = Path(__file__).resolve().parents[1]
RUTA_POLITICA = CARPETA_PROYECTO / "datos" / "politica_ficticia.md"
PATRON_POLITICA = re.compile(r"(?m)^## (P\d{2}) — (.+?)\s*$")


def separar_politicas(texto: str) -> list[dict]:
    """Devuelve P01-P10; texto íntegro para LLM y sin exclusiones en embeddings."""
    encabezado_historial = re.search(r"(?m)^## Historial de cambios\s*$", texto)
    texto_indexable = texto[:encabezado_historial.start()] if encabezado_historial else texto

    encabezado_reglas = re.search(r"(?m)^## Reglas generales\s*$", texto)
    if encabezado_reglas is None:
        raise ValueError("No se encontró la sección de reglas generales.")
    inicio_reglas = encabezado_reglas.start()
    siguiente_seccion = re.search(
        r"(?m)^## ", texto_indexable[encabezado_reglas.end():]
    )
    fin_reglas = (
        encabezado_reglas.end() + siguiente_seccion.start()
        if siguiente_seccion
        else len(texto_indexable)
    )
    reglas = texto_indexable[inicio_reglas:fin_reglas].strip()
    codigos_regla = re.findall(r"(?m)^\*\*RG-(\d{2}) —", reglas)
    esperados = [f"{numero:02d}" for numero in range(1, 11)]
    if codigos_regla != esperados:
        raise ValueError("La sección general debe contener RG-01 a RG-10 exactamente una vez.")

    encabezados = list(PATRON_POLITICA.finditer(texto_indexable))
    if [coincidencia.group(1) for coincidencia in encabezados] != [
        f"P{numero:02d}" for numero in range(1, 11)
    ]:
        raise ValueError("Se esperaba exactamente una política para cada código P01-P10.")

    fragmentos = []
    for indice, encabezado in enumerate(encabezados):
        fin = (
            encabezados[indice + 1].start()
            if indice + 1 < len(encabezados)
            else len(texto_indexable)
        )
        politica = encabezado.group(1)
        nombre = encabezado.group(2).strip()
        texto_politica = texto_indexable[encabezado.start():fin].strip()
        texto_busqueda = re.sub(
            r"(?ms)^\*\*Cuándo NO usarla\.\*\*.*?(?=^\*\*|^## |\Z)",
            "",
            texto_politica,
        ).strip()
        fragmentos.append({
            "politica": nombre,
            "codigo": politica,
            # Las advertencias completas se conservan para que el LLM contraste.
            "texto": f"{reglas}\n\n{texto_politica}",
            "texto_busqueda": texto_busqueda,
            "fuente": f"datos/politica_ficticia.md#{politica}",
        })
    return fragmentos


def separar_reglas(texto: str) -> list[dict]:
    """Extrae las reglas generales sin incluir otras secciones del documento."""
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("El texto de la política debe ser una cadena no vacía.")

    encabezado = re.search(r"(?m)^## Reglas generales\s*$", texto)
    if encabezado is None:
        raise ValueError("No se encontró la sección de reglas generales.")
    siguiente_seccion = re.search(r"(?m)^## ", texto[encabezado.end():])
    fin_seccion = (
        encabezado.end() + siguiente_seccion.start()
        if siguiente_seccion
        else len(texto)
    )
    seccion = texto[encabezado.end():fin_seccion]
    coincidencias = list(re.finditer(r"(?m)^\*\*(RG-\d{2}) — [^\r\n*]+\*\*(.*)$", seccion))
    esperados = [f"RG-{numero:02d}" for numero in range(1, 11)]
    codigos = [coincidencia.group(1) for coincidencia in coincidencias]
    if codigos != esperados:
        raise ValueError("La sección general debe contener RG-01 a RG-10 exactamente una vez y en orden.")

    reglas = []
    for indice, coincidencia in enumerate(coincidencias):
        fin = coincidencias[indice + 1].start() if indice + 1 < len(coincidencias) else len(seccion)
        fragmento = seccion[coincidencia.start():fin].strip()
        # Elimina únicamente separadores markdown, no contenido normativo.
        fragmento = re.sub(r"(?:\r?\n\s*)+---\s*$", "", fragmento).strip()
        contenido = coincidencia.group(2) + seccion[coincidencia.end():fin]
        contenido = re.sub(r"(?:\r?\n\s*)+---\s*$", "", contenido).strip()
        if not contenido:
            raise ValueError(f"La regla {coincidencia.group(1)} está vacía.")
        reglas.append({
            "codigo": coincidencia.group(1),
            "texto": fragmento,
            "fuente": f"datos/politica_ficticia.md#reglas-generales/{coincidencia.group(1)}",
        })
    if len({regla["codigo"] for regla in reglas}) != len(reglas):
        raise ValueError("La sección general contiene códigos de regla duplicados.")
    return reglas


def _configuracion() -> tuple[str, str, str]:
    """Valida configuración sin incluir sus valores en errores o trazas."""
    valores = tuple(os.getenv(nombre, "").strip() for nombre in (
        "REDIS_URL", "REDIS_PREFIJO", "EMBEDDING_MODEL"
    ))
    if not all(valores):
        raise RuntimeError("Falta REDIS_URL, REDIS_PREFIJO o EMBEDDING_MODEL en el entorno.")
    return valores


def _recursos(redis_url: str, prefijo: str, modelo: str):
    """Crea cliente con el esquema vectorial explícito y reintentos apagados."""
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from langchain_redis import RedisConfig, RedisVectorStore

    embeddings = GoogleGenerativeAIEmbeddings(model=modelo, max_retries=0)
    configuracion = RedisConfig(
        index_name=prefijo,
        redis_url=redis_url,
        embedding_dimensions=3072,
        distance_metric="COSINE",
        indexing_algorithm="FLAT",
        legacy_key_format=False,
    )
    vector_store = RedisVectorStore(
        embeddings=embeddings,
        config=configuracion,
    )
    return embeddings, vector_store


def _preparar_documentos(texto: str) -> list[dict]:
    """Combina políticas y reglas manteniendo texto embebible y texto completo."""
    politicas = separar_politicas(texto)
    reglas = separar_reglas(texto)
    documentos = [
        {**politica, "texto_completo": politica["texto"]}
        for politica in politicas
    ]
    documentos.extend(
        {
            "politica": "Reglas generales",
            "codigo": regla["codigo"],
            "texto": regla["texto"],
            "texto_busqueda": regla["texto"],
            "texto_completo": regla["texto"],
            "fuente": regla["fuente"],
        }
        for regla in reglas
    )
    return documentos


def main() -> None:
    """Previsualiza el índice offline o mantiene bloqueada la carga real."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Previsualiza el índice sin servicios externos.")
    parser.add_argument("--plan", action="store_true", help="valida documentos y muestra claves previstas")
    argumentos = parser.parse_args()
    if not argumentos.plan:
        raise RuntimeError(
            "Carga bloqueada: compatibilidad Redis pendiente. Completa y autoriza "
            "scripts/MIGRACION_INDICE_REDIS_PENDIENTE.md antes de habilitar escrituras."
        )
    texto = RUTA_POLITICA.read_text(encoding="utf-8")
    try:
        documentos = _preparar_documentos(texto)
        _validar_plan(documentos)
    except ValueError as error:
        parser.error(str(error))
    print(f"Plan offline: {len(documentos)} documentos; prefijo de prueba grupo05")
    print("Claves previstas (grupo05:<código>; predicción, no verificada en Redis):")
    for documento in documentos:
        print(f"- {documento['codigo']}: grupo05:{documento['codigo']}")
    print("ADVERTENCIA: las claves antiguas documentadas no han sido verificadas en Redis.")
    print("No se crearon clientes, embeddings ni se escribieron datos.")


def _validar_plan(documentos: list[dict]) -> None:
    """Comprueba códigos, campos requeridos y exclusiones de texto."""
    esperados = {
        *(f"P{numero:02d}" for numero in range(1, 11)),
        *(f"RG-{numero:02d}" for numero in range(1, 11)),
    }
    codigos = [documento.get("codigo") for documento in documentos]
    if len(documentos) != 20 or set(codigos) != esperados:
        raise ValueError("Se requieren exactamente las políticas P01-P10 y reglas RG-01 a RG-10.")
    if len(set(codigos)) != len(codigos):
        raise ValueError("Hay códigos duplicados entre los documentos preparados.")
    for documento in documentos:
        codigo = documento.get("codigo", "documento")
        for campo in ("texto_busqueda", "texto_completo", "fuente"):
            valor = documento.get(campo)
            if not isinstance(valor, str) or not valor.strip():
                raise ValueError(f"Falta {campo} en {codigo}.")
            if campo != "fuente" and "Historial de cambios" in valor:
                raise ValueError(f"Historial de cambios aparece en {codigo}.")
        if codigo.startswith("P"):
            if "Cuándo NO usarla." in documento["texto_busqueda"]:
                raise ValueError(f"Cuándo NO usarla debe excluirse de embeddings ({codigo}).")
            if "Cuándo NO usarla." not in documento["texto_completo"]:
                raise ValueError(f"Cuándo NO usarla debe conservarse en texto completo ({codigo}).")


def _cargar_documentos(
    documentos_fuente: list[dict], redis_url: str, prefijo: str, modelo: str
) -> None:
    """Construye documentos con metadatos e IDs estables y los carga en Redis."""
    # Redis añade key_prefix; IDs desnudos evitan prefijos duplicados.
    ids = [trozo["codigo"] for trozo in documentos_fuente]
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
            for trozo in documentos_fuente
        ]
        vector_store.add_documents(documents=documentos, ids=ids)
    except Exception as error:
        # No propagar mensajes del SDK: algunos incluyen URLs o detalles sensibles.
        raise RuntimeError(
            f"No se pudo cargar el índice Redis ({type(error).__name__}). "
            "Verifica conexión, memoria y cuotas del proveedor de embeddings."
        ) from None

    print(f"Carga completa: {len(documentos_fuente)} documentos en el índice configurado.")


if __name__ == "__main__":
    main()
