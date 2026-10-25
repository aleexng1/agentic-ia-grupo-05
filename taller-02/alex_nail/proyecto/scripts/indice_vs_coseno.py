# Compara "coseno a mano" (traer todos los vectores a Python) contra un índice vectorial, con los mismos datos.
# Uso: python scripts/indice_vs_coseno.py --n 2000 [--store redis|faiss]
import argparse
import io
import itertools
import json
import os
import random
import statistics
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.rag.storage import DATA, RAIZ, get_embeddings, get_redis_client, motor_actual  # noqa: E402

VECTORES = DATA / "vectores_demo.npy"
TEXTOS = DATA / "textos_demo.json"
PREGUNTAS_VEC = DATA / "preguntas_demo.npy"
PREGUNTAS_TXT = DATA / "preguntas_demo.json"
CAPTURAS = RAIZ.parent / "pruebas" / "capturas"

TAMANOS = (200, 2000, 20000)
MAX_REALES = 2000  # más allá de esto, los vectores se simulan (no se pagan más embeddings)
MAX_REDIS = 2000  # el Redis es compartido: 20000 no se corre ahí
LOTE = 100  # máximo de textos por llamada de embeddings en Gemini
RUIDO = 0.003  # desviación por componente del ruido de los vectores simulados
K = 3

TEMAS = {
    "internet": (
        ["El router", "El wifi", "La conexión", "El módem", "La señal", "El internet", "La red de la oficina", "La fibra óptica"],
        ["se cae a cada rato", "anda muy lento", "no da internet", "se desconecta", "pierde señal", "no prende la luz verde", "tarda en cargar páginas", "se reinicia solo"],
        ["en la noche", "desde ayer", "cuando llueve", "en el segundo piso", "los fines de semana", "al usar el celular", "después de la tormenta", "en horario punta"],
    ),
    "cocina": (
        ["El pan amasado", "La cazuela", "El pastel de choclo", "La sopaipilla", "El queque", "Las empanadas", "El arroz graneado", "La masa de pizza"],
        ["se prepara con harina y manteca", "necesita reposar una hora", "se hornea a 200 grados", "queda más rico con sal de mar", "se cocina a fuego lento", "lleva cebolla y comino", "se sirve bien caliente", "se amasa hasta que esté suave"],
        ["para la once", "en invierno", "según la receta de la abuela", "para diez personas", "en olla de greda", "para el domingo", "en horno de barro", "con ingredientes simples"],
    ),
    "futbol": (
        ["El delantero", "El arquero", "El equipo local", "La selección", "El entrenador", "El árbitro", "El capitán", "El club"],
        ["ganó el partido", "perdió por dos goles", "empató en el último minuto", "marcó un golazo", "fue expulsado", "celebró el campeonato", "cambió la táctica", "jugó muy bien"],
        ["en el clásico", "el domingo pasado", "en la final", "de visita", "con el estadio lleno", "por la copa", "bajo la lluvia", "en el segundo tiempo"],
    ),
    "salud": (
        ["El dolor de cabeza", "La fiebre", "La tos", "El resfrío", "El dolor de espalda", "La alergia", "El insomnio", "La presión alta"],
        ["se alivia con descanso", "requiere ir al médico", "empeora con el estrés", "mejora tomando agua", "aparece al despertar", "se controla con ejercicio", "dura varios días", "se trata con reposo"],
        ["en adultos mayores", "en invierno", "según el doctor", "en niños pequeños", "después de trabajar", "durante la semana", "en temporada de alergias", "si no se cuida"],
    ),
    "finanzas": (
        ["El ahorro mensual", "La tarjeta de crédito", "El sueldo", "El crédito hipotecario", "El presupuesto familiar", "La cuenta corriente", "El fondo de pensiones", "La deuda"],
        ["conviene revisarlo cada mes", "sube con los intereses", "se reparte en gastos fijos", "se puede renegociar con el banco", "crece si se invierte bien", "se paga en cuotas", "alcanza para lo básico", "necesita un plan claro"],
        ["a fin de mes", "este año", "con la inflación", "en pesos chilenos", "según el asesor", "antes de vacaciones", "en la familia", "para la jubilación"],
    ),
}

PREGUNTAS = [
    "no tengo internet en mi casa",
    "cómo hago pan amasado",
    "quién ganó el partido del domingo",
    "qué hago si tengo fiebre",
    "cómo ahorro plata cada mes",
]


class Tee(io.TextIOBase):
    """Escribe en pantalla y guarda una copia para la evidencia."""

    def __init__(self, pantalla):
        self.pantalla, self.copia = pantalla, io.StringIO()

    def write(self, s):
        self.pantalla.write(s)
        self.pantalla.flush()
        return self.copia.write(s)


def generar_textos(n: int) -> list[str]:
    """n frases cortas sobre 5 temas, siempre en el mismo orden (semilla fija) para que el caché sirva."""
    todas = [f"{s} {p} {c}." for s_, p_, c_ in TEMAS.values() for s, p, c in itertools.product(s_, p_, c_)]
    random.Random(42).shuffle(todas)
    if n > len(todas):
        raise ValueError(f"solo hay {len(todas)} frases distintas; usa a lo más ese número de vectores reales")
    return todas[:n]


def normalizar(m: np.ndarray) -> np.ndarray:
    return (m / np.linalg.norm(m, axis=-1, keepdims=True)).astype(np.float32)


def es_limite_de_uso(e: Exception) -> bool:
    return "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)


CUOTA_DIARIA = (
    "Gemini agotó la cuota DIARIA de embeddings (plan gratuito: 1000 textos por día). "
    "Reintentar hoy no sirve. Lo ya embebido quedó en data/; vuelve a correr el script "
    "cuando se reinicie la cuota (continúa desde ahí) o usa --max-reales con los que ya hay."
)


def es_cuota_diaria(e: Exception) -> bool:
    return "PerDay" in str(e) or "per day" in str(e).lower()


def embeber_lote(emb, lote: list[str], intentos: int = 8) -> list[list[float]]:
    for intento in range(intentos):
        try:
            return emb.embed_documents(lote)
        except Exception as e:
            if es_cuota_diaria(e):
                raise RuntimeError(CUOTA_DIARIA) from None
            if not es_limite_de_uso(e) or intento == intentos - 1:
                raise
            espera = min(60, 10 * 2**intento)
            print(f"    Gemini respondió 429 (límite de uso). Espero {espera} s y reintento ({intento + 1}/{intentos})...")
            time.sleep(espera)


def vectores_reales(n: int, emb) -> tuple[np.ndarray, list[str]]:
    """Devuelve n vectores reales, reutilizando el caché en data/ y embebiendo solo lo que falte."""
    textos = generar_textos(n)
    guardados = np.zeros((0, 0), dtype=np.float32)
    if VECTORES.exists() and TEXTOS.exists():
        textos_cache = json.loads(TEXTOS.read_text(encoding="utf-8"))
        guardados = np.load(VECTORES)
        comunes = min(len(textos_cache), len(guardados))
        if textos_cache[:comunes] != generar_textos(comunes):
            print("  El caché no corresponde a estos textos: se descarta y se vuelve a embeber.")
            guardados = np.zeros((0, 0), dtype=np.float32)
        else:
            guardados = guardados[:comunes]

    if len(guardados) >= n:
        print(f"  Reutilizo {n} vectores reales de {VECTORES.relative_to(RAIZ)} (no se pagan embeddings).")
        return normalizar(guardados[:n]), textos

    print(f"  Hay {len(guardados)} vectores en caché; embebo {n - len(guardados)} con Gemini en lotes de {LOTE}.")
    filas = list(guardados)
    for inicio in range(len(guardados), n, LOTE):
        filas.extend(np.asarray(embeber_lote(emb, textos[inicio : inicio + LOTE]), dtype=np.float32))
        # Se guarda después de cada lote: si algo falla, la próxima vez se continúa desde aquí.
        np.save(VECTORES, np.stack(filas))
        TEXTOS.write_text(json.dumps(textos[: len(filas)], ensure_ascii=False), encoding="utf-8")
        print(f"    avance: {len(filas)}/{n} vectores")
    return normalizar(np.stack(filas)), textos


def vectores_preguntas(emb) -> np.ndarray:
    """Embebe las preguntas una sola vez y las deja en caché en data/."""
    if PREGUNTAS_VEC.exists() and PREGUNTAS_TXT.exists():
        if json.loads(PREGUNTAS_TXT.read_text(encoding="utf-8")) == PREGUNTAS:
            print(f"  Reutilizo las {len(PREGUNTAS)} preguntas embebidas de {PREGUNTAS_VEC.relative_to(RAIZ)}.")
            return normalizar(np.load(PREGUNTAS_VEC))
    print(f"  Embebo las {len(PREGUNTAS)} preguntas con Gemini.")
    vectores = []
    for p in PREGUNTAS:
        try:
            vectores.append(emb.embed_query(p))
        except Exception as e:
            if es_cuota_diaria(e):
                raise RuntimeError(CUOTA_DIARIA) from None
            raise
    np.save(PREGUNTAS_VEC, np.asarray(vectores, dtype=np.float32))
    PREGUNTAS_TXT.write_text(json.dumps(PREGUNTAS, ensure_ascii=False), encoding="utf-8")
    return normalizar(np.asarray(vectores, dtype=np.float32))


def ampliar_simulado(reales: np.ndarray, textos: list[str], n: int) -> tuple[np.ndarray, list[str]]:
    """Copia los vectores reales con un poco de ruido y los renormaliza a largo 1 (sin pagar embeddings)."""
    r = len(reales)
    rng = np.random.default_rng(7)
    origen = np.arange(r, n) % r
    simulados = reales[origen] + rng.standard_normal((n - r, reales.shape[1]), dtype=np.float32) * RUIDO
    textos_sim = [f"{textos[i]} (simulado #{j})" for j, i in enumerate(origen, start=r)]
    return np.vstack([reales, normalizar(simulados)]), textos + textos_sim


def top_k(sims: np.ndarray, k: int = K) -> list[int]:
    idx = np.argpartition(-sims, k)[:k]
    return idx[np.argsort(-sims[idx])].tolist()


# ---------- FAISS ----------

def correr_faiss(vectores: np.ndarray, consultas: np.ndarray) -> list[dict]:
    import faiss

    index = faiss.IndexFlatL2(vectores.shape[1])  # mismos vectores normalizados que la forma A
    index.add(vectores)
    filas = []
    for q in consultas:
        t0 = time.perf_counter()
        a = top_k(vectores @ q)
        t1 = time.perf_counter()
        _, ids = index.search(q[None, :], K)
        t2 = time.perf_counter()
        filas.append({"a": a, "b": ids[0].tolist(), "ms_a": (t1 - t0) * 1e3, "ms_b": (t2 - t1) * 1e3,
                      "viaje_a": len(vectores), "viaje_b": 0})
    return filas


# ---------- Redis ----------

def memoria_libre_redis(cliente) -> tuple[int, str]:
    info = cliente.info("memory")
    usada = info["used_memory"]
    maxima = info.get("maxmemory")
    if not maxima:
        try:
            maxima = int(cliente.config_get("maxmemory").get("maxmemory", 0))
        except Exception:
            maxima = 0
    if maxima:
        return maxima - usada, f"maxmemory {maxima / 1e6:.0f} MB − used_memory {usada / 1e6:.0f} MB"
    pico = info.get("used_memory_peak", usada)
    return pico - usada, (
        f"el servidor no informa maxmemory; uso la cota conservadora "
        f"used_memory_peak {pico / 1e6:.0f} MB − used_memory {usada / 1e6:.0f} MB (el límite es al menos el pico)"
    )


def mb_estimados(n: int, dim: int) -> float:
    # Cada HASH guarda el vector (dim·4 bytes) + texto y claves (~300 bytes); el índice FLAT de Redis
    # mantiene además su propia copia interna del vector (no la controlamos), así que se cuenta dos veces.
    return n * (2 * dim * 4 + 300) / 1e6


def borrar_bench_redis(cliente, indice: str, n_claves: int) -> None:
    """FT.DROPINDEX ... DD y, por si quedó algo sin indexar, DEL de nuestras claves conocidas (sin SCAN)."""
    from redis.exceptions import ResponseError

    try:
        cliente.execute_command("FT.DROPINDEX", indice, "DD")
    except ResponseError as e:
        if "unknown index" not in str(e).lower() and "no such index" not in str(e).lower():
            raise
    for inicio in range(0, n_claves, 1000):
        cliente.delete(*[f"{indice}:{i}" for i in range(inicio, min(n_claves, inicio + 1000))])


def correr_redis(cliente, indice: str, vectores: np.ndarray, textos: list[str], consultas: np.ndarray) -> list[dict]:
    n, dim = vectores.shape
    claves = [f"{indice}:{i}" for i in range(n)]
    cliente.execute_command(
        "FT.CREATE", indice, "ON", "HASH", "PREFIX", "1", f"{indice}:",
        "SCHEMA", "texto", "TEXT",
        "embedding", "VECTOR", "FLAT", "6", "TYPE", "FLOAT32", "DIM", str(dim), "DISTANCE_METRIC", "COSINE",
    )
    for inicio in range(0, n, 200):
        pipe = cliente.pipeline(transaction=False)
        for i in range(inicio, min(n, inicio + 200)):
            pipe.hset(claves[i], mapping={"texto": textos[i], "embedding": vectores[i].tobytes()})
        pipe.execute()
    indexados = int(cliente.ft(indice).info()["num_docs"])
    if indexados != n:
        raise RuntimeError(f"el índice tiene {indexados} documentos y se esperaban {n}")

    from redis.commands.search.query import Query

    knn = Query(f"*=>[KNN {K} @embedding $v AS dist]").sort_by("dist").return_fields("dist").dialect(2)
    filas = []
    for q in consultas:
        t0 = time.perf_counter()
        # Forma A: traer TODOS los vectores desde los HASH y calcular el coseno en Python.
        pipe = cliente.pipeline(transaction=False)
        for c in claves:
            pipe.hget(c, "embedding")
        traidos = np.frombuffer(b"".join(pipe.execute()), dtype=np.float32).reshape(n, dim)
        a = top_k(traidos @ q)
        t1 = time.perf_counter()
        # Forma B: KNN en el servidor sobre los MISMOS HASH; solo vuelven 3 claves.
        res = cliente.ft(indice).search(knn, query_params={"v": q.tobytes()})  # FT.SEARCH ... KNN
        t2 = time.perf_counter()
        b = [int(doc.id.rsplit(":", 1)[1]) for doc in res.docs]
        filas.append({"a": a, "b": b, "ms_a": (t1 - t0) * 1e3, "ms_b": (t2 - t1) * 1e3, "viaje_a": n, "viaje_b": 0})
    return filas


# ---------- Reporte ----------

def coinciden(a: list[int], b: list[int]) -> str:
    if a == b:
        return "sí"
    return "sí (otro orden)" if set(a) == set(b) else "no"


def imprimir_tabla(n: int, filas: list[dict], textos: list[str]) -> None:
    print(f"\n  {'pregunta':<34}{'top-3 A':<20}{'top-3 B':<20}{'¿coinciden?':<17}{'ms A':>10}{'ms B':>10}{'vec→Py A':>10}{'vec→Py B':>10}")
    for pregunta, f in zip(PREGUNTAS, filas):
        ids_a = " ".join(f"#{i}" for i in f["a"])
        ids_b = " ".join(f"#{i}" for i in f["b"])
        print(f"  {pregunta:<34}{ids_a:<20}{ids_b:<20}{coinciden(f['a'], f['b']):<17}"
              f"{f['ms_a']:>10.3f}{f['ms_b']:>10.3f}{f['viaje_a']:>10}{f['viaje_b']:>10}")
    print("  top-1 (según B):")
    for pregunta, f in zip(PREGUNTAS, filas):
        print(f"    {pregunta!r} → #{f['b'][0]} {textos[f['b'][0]]!r}")


def conclusion(resumen: dict[int, dict], store: str) -> list[str]:
    ns = sorted(resumen)
    total = sum(r["preguntas"] for r in resumen.values())
    iguales = sum(r["coinciden"] for r in resumen.values())
    n0, n1 = ns[0], ns[-1]
    a0, b0, a1, b1 = resumen[n0]["ms_a"], resumen[n0]["ms_b"], resumen[n1]["ms_a"], resumen[n1]["ms_b"]

    if n1 > n0:
        rapida, lenta, veces = ("B", "A", a1 / b1) if b1 < a1 else ("A", "B", b1 / a1)
        linea1 = (f"De n={n0} a n={n1} (×{n1 / n0:.0f} datos) la forma A pasó de {a0:.2f} a {a1:.2f} ms (×{a1 / a0:.1f}) "
                  f"y la B de {b0:.2f} a {b1:.2f} ms (×{b1 / b0:.1f}); con n={n1} {rapida} es {veces:.1f}× más rápida que {lenta}, "
                  f"y ambas dieron el mismo top-3 en {iguales}/{total} búsquedas.")
    else:
        linea1 = f"Con n={n0} A tardó {a0:.2f} ms y B {b0:.2f} ms; el mismo top-3 en {iguales}/{total} búsquedas."

    if 200 not in resumen:
        return [linea1, "No se midió n=200, así que no se puede decir con datos cuándo conviene A."]
    a200, b200 = resumen[200]["ms_a"], resumen[200]["ms_b"]
    if a200 <= b200:
        hasta = max(n for n in ns if resumen[n]["ms_a"] <= resumen[n]["ms_b"])
        linea2 = (f"Con n=200 A tarda {a200:.3f} ms vs {b200:.3f} ms de B: con pocos vectores ya en memoria A conviene "
                  f"(igual de exacta y sin mantener un índice); en estas mediciones siguió ganando hasta n={hasta}.")
    else:
        motivo = "traer 200 vectores por la red ya cuesta más que el KNN en el servidor" if store == "redis" else "el índice ya gana con pocos datos"
        linea2 = (f"Incluso con n=200 A tarda {a200:.3f} ms vs {b200:.3f} ms de B ({motivo}): "
                  f"A solo conviene con muy pocos vectores que ya estén en memoria, o para verificar los resultados del índice.")
    return [linea1, linea2]


def main() -> int:
    parser = argparse.ArgumentParser(description="Coseno a mano vs índice vectorial")
    parser.add_argument("--n", type=int, default=2000, help="tamaño máximo a probar (200, 2000, 20000)")
    parser.add_argument("--store", choices=["redis", "faiss"], default=None, help="por defecto, VECTOR_STORE del .env")
    parser.add_argument("--max-reales", type=int, default=MAX_REALES,
                        help=f"vectores reales a usar (por defecto {MAX_REALES}); sobre eso se simulan")
    args = parser.parse_args()
    store = args.store or motor_actual()

    tee = Tee(sys.stdout)
    sys.stdout = tee
    salida = CAPTURAS / f"indice_vs_coseno_{store}.txt"
    cliente, indice, claves_creadas = None, None, 0
    try:
        print(f"== Coseno a mano (A) vs índice vectorial (B) · store={store} · n hasta {args.n} ==")
        tamanos = [t for t in TAMANOS if t <= args.n] or [args.n]
        if store == "redis" and any(t > MAX_REDIS for t in tamanos):
            print(f"Aviso: en redis no se corre n > {MAX_REDIS} (el servidor es compartido y su memoria no alcanza para todos).")
            tamanos = [t for t in tamanos if t <= MAX_REDIS]

        emb = get_embeddings()
        n_reales = min(max(tamanos), args.max_reales)
        print(f"\nVectores reales necesarios: {n_reales}")
        consultas = vectores_preguntas(emb)
        reales, textos_reales = vectores_reales(n_reales, emb)
        print(f"  {len(reales)} vectores de {reales.shape[1]} números, más {len(consultas)} preguntas embebidas.")

        if store == "redis":
            cliente = get_redis_client()
            indice = f"{os.getenv('PREFIJO')}_bench"
            print(f"Redis: PING={cliente.ping()} · índice y claves con prefijo '{indice}'")

        resumen = {}
        for n in tamanos:
            print(f"\n--- n = {n} ---")
            if n > len(reales):
                vectores, textos = ampliar_simulado(reales, textos_reales, n)
                print(f"  ATENCIÓN: escala SIMULADA. Solo {len(reales)} vectores son reales; los otros {n - len(reales)} "
                      f"son copias con ruido (σ={RUIDO}) renormalizadas a largo 1. Los tiempos valen, los textos se repiten.")
            else:
                vectores, textos = reales[:n], textos_reales[:n]

            if store == "faiss":
                filas = correr_faiss(vectores, consultas)
            else:
                libre, origen = memoria_libre_redis(cliente)
                necesario = mb_estimados(n, vectores.shape[1])
                print(f"  Memoria: ocuparía ~{necesario:.1f} MB; libre ≈ {libre / 1e6:.0f} MB ({origen}).")
                if necesario > libre / 2e6:
                    print(f"  NO se guarda: {necesario:.1f} MB es más de la mitad de lo libre ({libre / 2e6:.0f} MB) "
                          f"y el servidor es compartido con otros grupos.")
                    continue
                borrar_bench_redis(cliente, indice, n)  # por si quedó algo de una corrida anterior
                claves_creadas = n
                try:
                    filas = correr_redis(cliente, indice, vectores, textos, consultas)
                finally:
                    borrar_bench_redis(cliente, indice, n)
                    claves_creadas = 0
                    print(f"  Limpieza: índice '{indice}' y sus {n} HASH borrados.")

            imprimir_tabla(n, filas, textos)
            resumen[n] = {
                "ms_a": statistics.median(f["ms_a"] for f in filas),
                "ms_b": statistics.median(f["ms_b"] for f in filas),
                "viaje_a": filas[0]["viaje_a"],
                "preguntas": len(filas),
                "coinciden": sum(set(f["a"]) == set(f["b"]) for f in filas),
            }

        if not resumen:
            print("\nNo se pudo medir ningún tamaño.")
            return 1

        print("\n== Cómo crece el tiempo (mediana de las 5 preguntas) ==")
        print(f"  {'n':>7}{'ms A':>12}{'ms B':>12}{'A / B':>9}{'vec→Py A':>10}{'vec→Py B':>10}")
        previo = None
        for n, r in sorted(resumen.items()):
            crece = ""
            if previo:
                pn, pr = previo
                crece = f"   (datos ×{n / pn:.0f}: A ×{r['ms_a'] / pr['ms_a']:.1f}, B ×{r['ms_b'] / pr['ms_b']:.1f})"
            print(f"  {n:>7}{r['ms_a']:>12.3f}{r['ms_b']:>12.3f}{r['ms_a'] / r['ms_b']:>9.1f}{r['viaje_a']:>10}{0:>10}{crece}")
            previo = (n, r)
        if store == "faiss":
            print("  (en faiss los vectores ya están en la RAM de Python: 'vec→Py A' = cuántos recorre numpy; B solo devuelve 3 ids)")
        else:
            print("  (en redis la forma A descarga cada vez todos los HASH; la B solo recibe 3 claves y su distancia)")

        print("\n== Conclusión ==")
        for linea in conclusion(resumen, store):
            print(linea)
        return 0
    except Exception as e:
        print(f"\nFALLÓ: {type(e).__name__}: {e}")
        return 1
    finally:
        if cliente is not None and claves_creadas:
            borrar_bench_redis(cliente, indice, claves_creadas)
        sys.stdout = tee.pantalla
        CAPTURAS.mkdir(parents=True, exist_ok=True)
        salida.write_text(tee.copia.getvalue(), encoding="utf-8")
        print(f"\nSalida guardada en {salida}")


if __name__ == "__main__":
    sys.exit(main())
