# Ingesta de un PDF: limpiar, cortar, embeber (con caché) y guardar en el vector store (Redis o FAISS).
# Uso: python scripts/ingest.py ruta/al/archivo.pdf [--reset] [--solo-cortar]
import argparse
import os
import re
import shutil
import statistics
import sys
import textwrap
import time
from itertools import zip_longest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.indice_vs_coseno import CAPTURAS, Tee, es_cuota_diaria, es_limite_de_uso  # noqa: E402
from src.rag.storage import DATA, get_embeddings, get_redis_client, get_vector_store, guardar_faiss, motor_actual  # noqa: E402

LOTE = 100
ANCHO = 58  # ancho de cada columna al mostrar dos fragmentos lado a lado


class CuotaDiariaAgotada(Exception):
    pass


def cargar_paginas(ruta: Path):
    from langchain_community.document_loaders import PyPDFLoader

    return PyPDFLoader(str(ruta)).load()


def limpiar(paginas) -> tuple[int, int]:
    """El PDF se extrae con cada palabra separada por saltos de línea: todo bloque de espacios pasa a ser uno."""
    antes = despues = 0
    for p in paginas:
        antes += len(p.page_content)
        p.page_content = re.sub(r"\s+", " ", p.page_content).strip()
        despues += len(p.page_content)
    return antes, despues


def cortar(paginas, fuente: str, tamano: int, solape: int):
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=tamano,
        chunk_overlap=solape,
        separators=["\n\n", ". ", " ", ""],
        keep_separator="end",  # el ". " queda al final de la oración, no al inicio del fragmento siguiente
    )
    fragmentos = splitter.split_documents(paginas)
    for i, f in enumerate(fragmentos, 1):
        # Solo estos tres campos: la metadata de PyPDF trae la ruta local completa, que no debe ir al Redis compartido.
        f.metadata = {"fuente": fuente, "pagina": f.metadata["page"] + 1, "fragmento": i}
    return fragmentos


def faltantes_en_cache(emb, textos: list[str]) -> list[str]:
    """Textos sin embedding en data/cache_embeddings/: son los únicos que gastan cuota."""
    guardados = emb.document_embedding_store.mget(textos)
    return list(dict.fromkeys(t for t, v in zip(textos, guardados) if v is None))


def embeber_faltantes(emb, faltan: list[str], intentos: int = 8) -> None:
    """Embebe en lotes; cada lote queda en caché apenas llega."""
    for inicio in range(0, len(faltan), LOTE):
        lote = faltan[inicio : inicio + LOTE]
        for intento in range(intentos):
            try:
                emb.embed_documents(lote)
                break
            except Exception as e:
                if es_cuota_diaria(e):
                    raise CuotaDiariaAgotada(inicio) from None
                if not es_limite_de_uso(e) or intento == intentos - 1:
                    raise
                espera = min(60, 10 * 2**intento)
                print(f"    Gemini respondió 429 (límite por minuto). Espero {espera} s y reintento ({intento + 1}/{intentos})...")
                time.sleep(espera)
        print(f"    avance: {min(inicio + LOTE, len(faltan))}/{len(faltan)} embeddings nuevos")


def escapar_tag(valor: str) -> str:
    return re.sub(r"([^\w])", r"\\\1", valor)


def ya_ingestados(motor: str, prefijo: str, fuente: str, cliente) -> int:
    """Cuántos fragmentos de esta misma fuente ya hay en la base (sin recorrer claves del servidor)."""
    if motor == "redis":
        from redis.commands.search.query import Query
        from redis.exceptions import ResponseError

        try:
            return cliente.ft(prefijo).search(Query(f"@fuente:{{{escapar_tag(fuente)}}}").paging(0, 0)).total
        except ResponseError:
            return 0  # el índice todavía no existe
    carpeta = DATA / prefijo
    if not (carpeta / "index.faiss").exists():
        return 0
    store = get_vector_store(prefijo)
    return sum(d.metadata.get("fuente") == fuente for d in store.docstore._dict.values())


def resetear(motor: str, prefijo: str, cliente) -> None:
    if motor == "redis":
        from redis.exceptions import ResponseError

        try:
            cliente.execute_command("FT.DROPINDEX", prefijo, "DD")
            print(f"--reset: índice '{prefijo}' y sus documentos borrados (solo ese índice).")
        except ResponseError:
            print(f"--reset: el índice '{prefijo}' no existía.")
    else:
        carpeta = DATA / prefijo
        if carpeta.exists():
            shutil.rmtree(carpeta)
            print(f"--reset: borrado el índice FAISS en {carpeta.relative_to(DATA.parent)}/.")
        else:
            print(f"--reset: no había índice FAISS en {carpeta.relative_to(DATA.parent)}/.")


def confirmar(pregunta: str) -> bool:
    print(f"{pregunta} [s/N] ", end="")
    try:
        respuesta = input().strip().lower()
    except EOFError:
        respuesta = ""
        print("(sin respuesta)")
    else:
        print(respuesta)  # para que quede en la captura
    return respuesta in ("s", "si", "sí", "y", "yes")


def solape(a: str, b: str) -> int:
    """Largo del texto que se repite: el final de a que es también el inicio de b."""
    for k in range(min(len(a), len(b)), 0, -1):
        if a.endswith(b[:k]):
            return k
    return 0


def lado_a_lado(fa, fb, titulo: str) -> None:
    a, b = fa.page_content, fb.page_content
    k = solape(a, b)
    if k:
        a = f"{a[:-k]}⟦{a[-k:]}⟧"
        b = f"⟦{b[:k]}⟧{b[k:]}"
    izq, der = textwrap.wrap(a, ANCHO), textwrap.wrap(b, ANCHO)
    print(f"\n{titulo}")
    cab_a = f"fragmento {fa.metadata['fragmento']} (pág. {fa.metadata['pagina']}, {len(fa.page_content)} car.)"
    cab_b = f"fragmento {fb.metadata['fragmento']} (pág. {fb.metadata['pagina']}, {len(fb.page_content)} car.)"
    print(f"  {cab_a:<{ANCHO}} │ {cab_b}")
    print(f"  {'─' * ANCHO}─┼─{'─' * ANCHO}")
    for l, r in zip_longest(izq, der, fillvalue=""):
        print(f"  {l:<{ANCHO}} │ {r}")
    if k:
        print(f"  ⟦…⟧ = texto repetido entre ambos (solape de {k} caracteres)")
    else:
        print("  (no hay texto repetido entre estos dos fragmentos)")


def estadisticas(paginas, fragmentos) -> None:
    largos = [len(f.page_content) for f in fragmentos]
    print("\n== Resumen ==")
    print(f"  Páginas leídas:          {len(paginas)}")
    print(f"  Fragmentos generados:    {len(fragmentos)}")
    print(f"  Tamaño promedio:         {statistics.mean(largos):.0f} caracteres (mín. {min(largos)}, máx. {max(largos)})")

    if len(fragmentos) < 2:
        return
    misma_pagina = [(a, b) for a, b in zip(fragmentos, fragmentos[1:]) if a.metadata["pagina"] == b.metadata["pagina"]]
    con_solape = [(a, b) for a, b in misma_pagina if solape(a.page_content, b.page_content)]
    print(f"  Pares consecutivos de una misma página: {len(misma_pagina)}, de los cuales {len(con_solape)} comparten texto")

    f1, f2 = fragmentos[0], fragmentos[1]
    lado_a_lado(f1, f2, "== Fragmentos 1 y 2 ==")
    if f1.metadata["pagina"] != f2.metadata["pagina"]:
        print(f"  Están en páginas distintas ({f1.metadata['pagina']} y {f2.metadata['pagina']}): el cortador trabaja "
              "página por página, así que entre ellos no hay solape.")
    elif not solape(f1.page_content, f2.page_content):
        print("  Están en la misma página pero no repiten texto: el solape se arma con trozos completos (oraciones, o\n"
              "  palabras si una oración no cabe) que sumen a lo más CHUNK_OVERLAP caracteres; si la última oración\n"
              "  del fragmento es más larga que eso, no se repite nada.")
    else:
        return
    if con_solape:
        lado_a_lado(*con_solape[0], "== Primer par de fragmentos consecutivos de una misma página con texto repetido ==")
    else:
        print("  Ningún par de fragmentos de una misma página comparte texto, así que no hay solape que mostrar.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingesta de un PDF al vector store")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--reset", action="store_true", help="borra SOLO el índice PREFIJO antes de ingestar")
    parser.add_argument("--solo-cortar", action="store_true", help="corta y muestra estadísticas, sin embeber ni guardar")
    args = parser.parse_args()

    tamano = int(os.getenv("CHUNK_SIZE", "800"))
    solape_cfg = int(os.getenv("CHUNK_OVERLAP", "120"))
    salida = CAPTURAS / f"ingesta_{tamano}_{solape_cfg}.txt"
    tee = Tee(sys.stdout)
    sys.stdout = tee
    try:
        modo = "solo cortar (sin embeber ni guardar)" if args.solo_cortar else f"ingesta en {motor_actual()}"
        print(f"== Ingesta de {args.pdf} · CHUNK_SIZE={tamano} · CHUNK_OVERLAP={solape_cfg} · {modo} ==\n")

        if not args.pdf.is_file():
            print(f"FALLÓ: no existe el archivo {args.pdf}.")
            return 1
        try:
            paginas = cargar_paginas(args.pdf)
        except Exception as e:
            print(f"FALLÓ: no se pudo leer el PDF ({type(e).__name__}: {e}).")
            return 1

        antes, despues = limpiar(paginas)
        print(f"Páginas cargadas: {len(paginas)}")
        print(f"Limpieza de espacios: {antes} → {despues} caracteres ({antes - despues} espacios/saltos sobrantes quitados)")
        vacias = [p.metadata["page"] + 1 for p in paginas if not p.page_content]
        if despues == 0:
            print("FALLÓ: el PDF no tiene texto extraíble (¿es un PDF escaneado?). Habría que pasarlo por OCR primero.")
            return 1
        if vacias:
            print(f"Aviso: páginas sin texto (se omiten): {vacias}")
        paginas = [p for p in paginas if p.page_content]

        fragmentos = cortar(paginas, args.pdf.name, tamano, solape_cfg)
        textos = [f.page_content for f in fragmentos]
        emb = get_embeddings()
        faltan = faltantes_en_cache(emb, textos)
        print(f"Fragmentos: {len(fragmentos)} · ya en caché: {len(fragmentos) - len(faltan)} · "
              f"NO están en caché (gastan cuota): {len(faltan)}")

        if args.solo_cortar:
            print(f"\n--solo-cortar: no se embebió ni guardó nada. La ingesta real gastaría {len(faltan)} embeddings "
                  "(+1 consulta para medir la dimensión del índice, solo la primera vez).")
            estadisticas(paginas, fragmentos)
            return 0

        motor = motor_actual()
        prefijo = os.getenv("PREFIJO")
        if not prefijo:
            print("FALLÓ: falta PREFIJO en .env.")
            return 1
        cliente = get_redis_client() if motor == "redis" else None

        if not args.reset:
            previos = ya_ingestados(motor, prefijo, args.pdf.name, cliente)
            if previos and not confirmar(
                f"'{args.pdf.name}' ya tiene {previos} fragmentos en el índice '{prefijo}'. "
                "Si continúas se duplicarán (usa --reset para reemplazarlos). ¿Continuar?"
            ):
                print("Cancelado: no se agregó nada.")
                return 1

        if faltan:
            print(f"\nEmbebiendo {len(faltan)} fragmentos nuevos en lotes de {LOTE}...")
            try:
                embeber_faltantes(emb, faltan)
            except CuotaDiariaAgotada as e:
                hechos = e.args[0]
                print(f"\nDETENIDO: Gemini agotó la cuota DIARIA de embeddings (plan gratuito: ~1000 textos por día).\n"
                      f"  {hechos} de {len(faltan)} embeddings nuevos alcanzaron a quedar en la caché (data/cache_embeddings/).\n"
                      f"  No se tocó la base{' (el --reset no se aplicó)' if args.reset else ''}. Al reintentar mañana con el mismo\n"
                      f"  comando, la caché evita volver a pagar lo ya convertido y solo se embeben los {len(faltan) - hechos} que faltan.")
                return 1

        # El reset va recién aquí, con todos los embeddings listos: si la cuota se corta, la base queda intacta.
        if args.reset:
            resetear(motor, prefijo, cliente)

        store = get_vector_store(prefijo)  # todos los embeddings ya están en caché: esto no gasta cuota
        store.add_texts(textos, metadatas=[f.metadata for f in fragmentos])
        if motor == "faiss":
            carpeta = guardar_faiss(store, prefijo)
            print(f"\nGuardados {len(fragmentos)} fragmentos en el índice FAISS {carpeta.relative_to(DATA.parent)}/")
        else:
            print(f"\nGuardados {len(fragmentos)} fragmentos en el índice Redis '{prefijo}' (COSINE)")

        estadisticas(paginas, fragmentos)
        print("\nOK")
        return 0
    except Exception as e:
        print(f"\nFALLÓ: {type(e).__name__}: {e}")
        return 1
    finally:
        sys.stdout = tee.pantalla
        CAPTURAS.mkdir(parents=True, exist_ok=True)
        salida.write_text(tee.copia.getvalue(), encoding="utf-8")
        print(f"\nSalida guardada en {salida}")


if __name__ == "__main__":
    sys.exit(main())
