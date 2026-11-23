"""Paso 7: servidor local para preguntarle al grafo (GraphRAG).

Sirve revisar.html en "/" y expone la API que usa la pestaña "Preguntar al grafo".
Las claves (.env) se quedan aquí, en el servidor: la página nunca las ve.

    GET  /                               -> revisar.html
    POST /api/preguntar-con-grafo        -> busca por embeddings + conexiones del grafo, y responde Gemini
    POST /api/preguntar-sin-grafo        -> los mismos productos, pero solo con la fila cruda del Excel
    GET  /api/producto/{sku}/relaciones  -> nodos y flechas del producto en Neo4j (para dibujarlo)

Solo escucha en 127.0.0.1 (tu computador). Uso, desde curso02-taller-graphrag/:
    python servidor.py
"""

import sys
from contextlib import contextmanager
from functools import lru_cache
from threading import Lock
from typing import Optional

import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse
from google import genai
from google.genai import errors, types
from neo4j.exceptions import Neo4jError, ServiceUnavailable, SessionExpired
from pydantic import BaseModel

from comun import (BASE, NOMBRE_INDICE, ErrorConexion, ErrorConfiguracion, cargar_env, conectar,
                   formato_precio, pedir_embedding, reintentar)

HOST = "127.0.0.1"  # fijo a propósito: el servidor no se expone fuera de tu computador
PUERTO = 8000
PAGINA = BASE / "revisar.html"
EXCEL = BASE / "data" / "productos.xlsx"

TOP_K = 5  # productos más parecidos a la pregunta
N_PARECIDOS = 3  # parecidos por producto
N_ORIGINALES = 3  # originales (no réplicas) de la línea que imita una réplica
MAX_PREGUNTA = 500
TEMPERATURA = 0.2
# En una petición de la página no conviene esperar mucho: pocos reintentos y esperas cortas.
INTENTOS_WEB = 3
ESPERA_WEB = 3

# Mismas instrucciones con y sin grafo, para que la comparación sea justa.
INSTRUCCIONES = """\
Eres un vendedor de una tienda online chilena de celulares y televisores. Responde en español, de forma \
clara y breve, a la pregunta del cliente.

REGLAS
- Usa SOLO la información de la tienda que se te entrega. No inventes productos, precios ni características.
- Si algún producto es una réplica, avísalo claramente al cliente y, si el original aparece en la información \
entregada, ofrécelo.
- Cuando menciones un producto, di su SKU y su precio.
- Si en la información no hay nada útil para la pregunta, dilo con honestidad.
"""

ORDEN_CARACTERISTICAS = ["almacenamiento", "ram", "pantalla", "sistema"]


# ---------------------------------------------------------------------------
# Configuración y conexiones (se abren la primera vez que se necesitan)
# ---------------------------------------------------------------------------
_candado = Lock()
_estado: dict = {"config": None, "driver": None, "gemini": None}


def config() -> dict[str, str]:
    with _candado:
        if _estado["config"] is None:
            _estado["config"] = cargar_env(["NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD",
                                            "GOOGLE_API_KEY", "MODELO", "MODELO_EMBEDDINGS"])
        return _estado["config"]


def driver():
    c = config()
    with _candado:
        if _estado["driver"] is None:
            _estado["driver"] = conectar(c["NEO4J_URI"], c["NEO4J_USERNAME"], c["NEO4J_PASSWORD"])
        return _estado["driver"]


def olvidar_driver() -> None:
    """Descarta la conexión rota para que la próxima petición abra una nueva."""
    with _candado:
        if _estado["driver"] is not None:
            try:
                _estado["driver"].close()
            except Exception:
                pass
            _estado["driver"] = None


def gemini() -> genai.Client:
    c = config()
    with _candado:
        if _estado["gemini"] is None:
            _estado["gemini"] = genai.Client(api_key=c["GOOGLE_API_KEY"])
        return _estado["gemini"]


@contextmanager
def errores_claros():
    """Convierte cualquier falla en un error HTTP con un mensaje que se entienda (nunca en una respuesta exitosa)."""
    try:
        yield
    except HTTPException:
        raise
    except ErrorConfiguracion as e:
        raise HTTPException(500, str(e))
    except ErrorConexion as e:
        raise HTTPException(503, str(e))
    except (ServiceUnavailable, SessionExpired) as e:
        olvidar_driver()
        raise HTTPException(503, "Se perdió la conexión con Neo4j (¿la instancia de Aura está pausada?). "
                                 "Reanúdala en la consola de Aura y vuelve a intentar. "
                                 f"Detalle: {type(e).__name__}")
    except Neo4jError as e:
        texto = str(e).lower()
        if "no such" in texto and "index" in texto:
            raise HTTPException(503, f"No existe el índice vectorial «{NOMBRE_INDICE}» en Neo4j. "
                                     "Corre primero: python cargar_neo4j.py")
        raise HTTPException(502, f"Neo4j respondió con un error: {str(e)[:300]}")
    except errors.APIError as e:
        if e.code == 429:
            raise HTTPException(429, "Gemini alcanzó el límite de uso. Espera un momento y vuelve a intentar.")
        if e.code in (400, 401, 403, 404):
            raise HTTPException(502, f"Gemini rechazó la petición ({e.code}). Revisa GOOGLE_API_KEY, MODELO y "
                                     f"MODELO_EMBEDDINGS en el .env. Detalle: {str(e)[:200]}")
        raise HTTPException(502, f"Gemini no está respondiendo ahora ({e.code}). Vuelve a intentar en un momento.")
    except Exception as e:
        raise HTTPException(500, f"Error inesperado: {type(e).__name__}: {str(e)[:300]}")


# ---------------------------------------------------------------------------
# Búsqueda y datos del grafo
# ---------------------------------------------------------------------------
def leer(consulta: str, **parametros) -> list[dict]:
    with driver().session() as sesion:
        return sesion.execute_read(lambda tx: tx.run(consulta, **parametros).data())


def buscar_skus(pregunta: str) -> list[dict]:
    """Los TOP_K productos con embedding más parecido a la pregunta: [{sku, score}]."""
    c = config()
    vector = pedir_embedding(gemini(), c["MODELO_EMBEDDINGS"], pregunta, tarea="RETRIEVAL_QUERY",
                             intentos=INTENTOS_WEB, espera_base=ESPERA_WEB)
    filas = leer(
        "CALL db.index.vector.queryNodes($indice, $k, $vector) YIELD node, score "
        "RETURN node.sku AS sku, score ORDER BY score DESC",
        indice=NOMBRE_INDICE, k=TOP_K, vector=vector,
    )
    if not filas:
        raise HTTPException(404, "El grafo no tiene productos con embedding. Corre primero: python cargar_neo4j.py")
    return filas


def traer_contexto_grafo(encontrados: list[dict]) -> list[dict]:
    """Por cada producto: marca, categoría, línea, características, réplica y lo que copia,
    originales de la línea copiada y productos parecidos."""
    skus = [e["sku"] for e in encontrados]
    base = leer(
        """
        UNWIND $skus AS sku
        MATCH (p:Producto {sku: sku})
        RETURN p.sku AS sku, p.nombre AS nombre, p.precio AS precio, p.es_replica AS es_replica,
               head([(p)-[:DE_MARCA]->(m) | m.nombre]) AS marca,
               head([(p)-[:EN_CATEGORIA]->(c) | c.nombre]) AS categoria,
               head([(p)-[:DE_LINEA]->(l) | l.nombre]) AS linea,
               [(p)-[:TIENE]->(k) | {tipo: k.tipo, valor: k.valor}] AS caracteristicas,
               head([(p)-[:IMITA]->(li) | li.nombre]) AS copia_linea,
               head([(p)-[:IMITA]->(:Linea)-[:DE_MARCA]->(im) | im.nombre]) AS copia_marca
        """,
        skus=skus,
    )
    originales = leer(
        """
        UNWIND $skus AS sku
        MATCH (:Producto {sku: sku})-[:IMITA]->(:Linea)<-[:DE_LINEA]-(o:Producto)
        WHERE o.es_replica = false
        WITH sku, o ORDER BY o.precio DESC
        RETURN sku, collect({sku: o.sku, nombre: o.nombre, precio: o.precio})[..$n] AS originales
        """,
        skus=skus, n=N_ORIGINALES,
    )
    parecidos = leer(
        """
        UNWIND $skus AS sku
        MATCH (p:Producto {sku: sku}) WHERE p.embedding IS NOT NULL
        CALL db.index.vector.queryNodes($indice, $k, p.embedding) YIELD node, score
        WHERE node <> p
        WITH sku, node, score ORDER BY score DESC
        RETURN sku, collect({sku: node.sku, nombre: node.nombre, precio: node.precio,
                             es_replica: node.es_replica})[..$n] AS parecidos
        """,
        skus=skus, indice=NOMBRE_INDICE, k=N_PARECIDOS + 1, n=N_PARECIDOS,
    )
    por_sku = {f["sku"]: f for f in base}
    orig = {f["sku"]: f["originales"] for f in originales}
    pare = {f["sku"]: f["parecidos"] for f in parecidos}

    resultado = []
    for e in encontrados:
        ficha = por_sku.get(e["sku"])
        if ficha is None:
            continue
        ficha = dict(ficha)
        ficha["score"] = round(float(e["score"]), 4)
        ficha["originales"] = orig.get(e["sku"], [])
        ficha["parecidos"] = pare.get(e["sku"], [])
        ficha["caracteristicas"] = sorted(
            ficha["caracteristicas"],
            key=lambda k: ORDEN_CARACTERISTICAS.index(k["tipo"]) if k["tipo"] in ORDEN_CARACTERISTICAS else 99,
        )
        resultado.append(ficha)
    return resultado


def etiqueta_precio(precio) -> str:
    return formato_precio(int(precio)) if precio is not None else "precio no disponible"


def contexto_con_grafo(productos: list[dict]) -> str:
    """Texto ordenado con lo que sabe el grafo de cada producto encontrado."""
    lineas = ["Productos de la tienda más parecidos a la pregunta (del más al menos parecido):", ""]
    for i, p in enumerate(productos, start=1):
        lineas.append(f"{i}. [{p['sku']}] {p['nombre']}")
        lineas.append(f"   Precio: {etiqueta_precio(p['precio'])}")
        lineas.append(f"   Marca: {p['marca'] or 'Sin marca'}")
        lineas.append(f"   Categoría: {p['categoria'] or 'no indicada'}")
        lineas.append(f"   Línea: {p['linea'] or 'no indicada'}")
        if p["caracteristicas"]:
            lineas.append("   Características: " + "; ".join(f"{k['tipo']}: {k['valor']}" for k in p["caracteristicas"]))
        if p["es_replica"]:
            imita = p["copia_linea"] or "un modelo famoso (línea no identificada)"
            marca = f" de la marca {p['copia_marca']}" if p["copia_marca"] else ""
            lineas.append(f"   ES UNA RÉPLICA: imita la línea {imita}{marca}.")
            if p["originales"]:
                lineas.append("   Originales de esa línea en la tienda:")
                lineas += [f"     - [{o['sku']}] {o['nombre']} ({etiqueta_precio(o['precio'])})" for o in p["originales"]]
            else:
                lineas.append("   Originales de esa línea en la tienda: ninguno.")
        else:
            lineas.append("   No es una réplica.")
        if p["parecidos"]:
            lineas.append("   Productos parecidos:")
            lineas += [f"     - [{q['sku']}] {q['nombre']} ({etiqueta_precio(q['precio'])})"
                       + (" [réplica]" if q["es_replica"] else "") for q in p["parecidos"]]
        lineas.append("")
    return "\n".join(lineas).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Contexto "sin grafo": solo la fila cruda del Excel
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def filas_excel() -> dict[str, dict]:
    if not EXCEL.exists():
        raise ErrorConfiguracion(f"No encuentro {EXCEL.relative_to(BASE)}.")
    df = pd.read_excel(EXCEL, sheet_name=0)
    filas = {}
    for _, r in df.iterrows():
        sku = str(r["SKU"]).strip()
        marca = None if pd.isna(r["Marca"]) else str(r["Marca"]).strip() or None
        filas[sku] = {
            "nombre": str(r["Nombre"]).strip(),
            "marca": marca,  # None si venía vacía
            "categoria": None if pd.isna(r["Categoría"]) else str(r["Categoría"]).strip(),
            "precio": None if pd.isna(r["Precio oferta"]) else int(r["Precio oferta"]),
        }
    return filas


def contexto_sin_grafo(skus: list[str]) -> str:
    """Solo lo que trae el Excel: nombre, marca tal como venía, categoría y precio."""
    excel = filas_excel()
    lineas = ["Productos de la tienda más parecidos a la pregunta (del más al menos parecido):", ""]
    for i, sku in enumerate(skus, start=1):
        fila = excel.get(sku)
        if fila is None:
            lineas += [f"{i}. [{sku}] (no aparece en el Excel)", ""]
            continue
        lineas.append(f"{i}. [{sku}] {fila['nombre']}")
        lineas.append(f"   Marca: {fila['marca'] or '(vacía)'}")
        lineas.append(f"   Categoría: {fila['categoria'] or '(vacía)'}")
        lineas.append(f"   Precio: {etiqueta_precio(fila['precio'])}")
        lineas.append("")
    return "\n".join(lineas).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Respuesta de Gemini (idéntica con y sin grafo; solo cambia el contexto)
# ---------------------------------------------------------------------------
def responder(pregunta: str, contexto: str) -> str:
    c = config()
    contenido = f"Pregunta del cliente: {pregunta}\n\nInformación de la tienda:\n{contexto}"

    def llamar() -> str:
        respuesta = gemini().models.generate_content(
            model=c["MODELO"],
            contents=contenido,
            config=types.GenerateContentConfig(system_instruction=INSTRUCCIONES, temperature=TEMPERATURA),
        )
        if not respuesta.text:
            raise RuntimeError("Gemini devolvió una respuesta vacía")
        return respuesta.text.strip()

    return reintentar(llamar, INTENTOS_WEB, ESPERA_WEB, etiqueta="respuesta")


# ---------------------------------------------------------------------------
# Relaciones de un producto, con el mismo formato que dibuja revisar.html
# ---------------------------------------------------------------------------
def armar_relaciones(r: dict) -> dict:
    """Convierte lo que hay en Neo4j en {nodos, aristas} (mismos ids, tipos y nombres que fichaARelaciones)."""
    nodos: list[dict] = []
    aristas: list[dict] = []
    conocidos: set[str] = set()

    def nodo(id_: str, tipo: str, etiqueta: str, valor: str, roja: bool = False) -> str:
        if id_ not in conocidos:  # igual que MERGE: el mismo nombre es el mismo nodo
            conocidos.add(id_)
            nodos.append({"id": id_, "tipo": tipo, "etiqueta": etiqueta, "valor": str(valor), "roja": roja})
        return id_

    def arista(desde: str, hasta: str, relacion: str, roja: bool = False) -> None:
        aristas.append({"desde": desde, "hasta": hasta, "relacion": relacion, "roja": roja})

    ids_categoria = [nodo(f"categoria:{c}", "categoria", "CATEGORÍA", c) for c in r["categorias"]]
    caracteristicas = sorted(
        r["caracteristicas"],
        key=lambda k: ORDEN_CARACTERISTICAS.index(k["tipo"]) if k["tipo"] in ORDEN_CARACTERISTICAS else 99,
    )
    ids_caracteristicas = [
        nodo(f"carac:{k['tipo']}:{k['valor']}", "caracteristica", k["tipo"].upper(), k["valor"]) for k in caracteristicas
    ]
    ids_marca = {m: nodo(f"marca:{m}", "marca", "MARCA", m) for m in r["marcas"]}
    ids_linea = {}
    for item in r["lineas"]:
        ids_linea[item["linea"]] = nodo(f"linea:{item['linea']}", "linea", "LÍNEA", item["linea"])
        for m in item["marcas"]:
            ids_marca.setdefault(m, nodo(f"marca:{m}", "marca", "MARCA", m))
    copias = []
    for item in r["copias"]:
        id_linea = nodo(f"linea:{item['linea']}", "copia", "LÍNEA COPIADA", item["linea"], True)
        id_marcas = [nodo(f"marca:{m}", "copia", "MARCA COPIADA", m, True) for m in item["marcas"]]
        copias.append((id_linea, id_marcas))

    for m in r["marcas"]:
        arista("producto", ids_marca[m], "DE_MARCA")
    for id_ in ids_categoria:
        arista("producto", id_, "EN_CATEGORIA")
    for item in r["lineas"]:
        arista("producto", ids_linea[item["linea"]], "DE_LINEA")
        for m in item["marcas"]:
            arista(ids_linea[item["linea"]], ids_marca[m], "DE_MARCA")
    for id_ in ids_caracteristicas:
        arista("producto", id_, "TIENE")
    for id_linea, id_marcas in copias:
        arista("producto", id_linea, "IMITA", True)
        for id_marca in id_marcas:
            arista(id_linea, id_marca, "DE_MARCA", True)
    return {"nodos": nodos, "aristas": aristas}


# ---------------------------------------------------------------------------
# La aplicación
# ---------------------------------------------------------------------------
app = FastAPI(title="Preguntar al grafo", docs_url=None, redoc_url=None)
# Protege contra páginas externas que apunten su dominio a tu 127.0.0.1 (DNS rebinding).
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])


class Pregunta(BaseModel):
    pregunta: str


class PreguntaSinGrafo(Pregunta):
    skus: Optional[list[str]] = None  # los productos que ya encontró la consulta con grafo


def validar_pregunta(texto: str) -> str:
    texto = (texto or "").strip()
    if not texto:
        raise HTTPException(400, "Escribe una pregunta antes de enviar.")
    if len(texto) > MAX_PREGUNTA:
        raise HTTPException(400, f"La pregunta es muy larga (máximo {MAX_PREGUNTA} caracteres).")
    return texto


@app.get("/", include_in_schema=False)
def pagina():
    if not PAGINA.exists():
        raise HTTPException(404, f"No encuentro {PAGINA.name}.")
    return FileResponse(PAGINA, media_type="text/html; charset=utf-8")


@app.post("/api/preguntar-con-grafo")
def preguntar_con_grafo(datos: Pregunta):
    pregunta = validar_pregunta(datos.pregunta)
    with errores_claros():
        productos = traer_contexto_grafo(buscar_skus(pregunta))
        contexto = contexto_con_grafo(productos)
        return {
            "respuesta": responder(pregunta, contexto),
            "contexto": contexto,
            "productos": [
                {k: p[k] for k in ("sku", "nombre", "precio", "es_replica", "marca", "categoria", "linea",
                                   "copia_linea", "copia_marca", "score")}
                for p in productos
            ],
        }


@app.post("/api/preguntar-sin-grafo")
def preguntar_sin_grafo(datos: PreguntaSinGrafo):
    pregunta = validar_pregunta(datos.pregunta)
    with errores_claros():
        if datos.skus:
            skus = [s.strip() for s in datos.skus[:TOP_K * 2] if s and s.strip()]
        else:
            skus = [e["sku"] for e in buscar_skus(pregunta)]
        contexto = contexto_sin_grafo(skus)
        return {"respuesta": responder(pregunta, contexto), "contexto": contexto, "skus": skus}


@app.get("/api/producto/{sku}/relaciones")
def relaciones_producto(sku: str):
    with errores_claros():
        filas = leer(
            """
            MATCH (p:Producto {sku: $sku})
            RETURN p.sku AS sku, p.nombre AS nombre, p.precio AS precio, p.es_replica AS es_replica,
                   [(p)-[:DE_MARCA]->(m) | m.nombre] AS marcas,
                   [(p)-[:EN_CATEGORIA]->(c) | c.nombre] AS categorias,
                   [(p)-[:DE_LINEA]->(l) | {linea: l.nombre, marcas: [(l)-[:DE_MARCA]->(lm) | lm.nombre]}] AS lineas,
                   [(p)-[:IMITA]->(li) | {linea: li.nombre, marcas: [(li)-[:DE_MARCA]->(im) | im.nombre]}] AS copias,
                   [(p)-[:TIENE]->(k) | {tipo: k.tipo, valor: k.valor}] AS caracteristicas
            """,
            sku=sku,
        )
        if not filas:
            raise HTTPException(404, f"El producto {sku} no está en Neo4j. ¿Ya corriste cargar_neo4j.py?")
        r = filas[0]
        return {
            "producto": {k: r[k] for k in ("sku", "nombre", "precio", "es_replica")},
            **armar_relaciones(r),
        }


if __name__ == "__main__":
    try:
        config()  # falla rápido y con claridad si falta algo en el .env
    except ErrorConfiguracion as e:
        sys.exit(str(e))
    print(f"Abre http://{HOST}:{PUERTO} en tu navegador (Ctrl+C para detener).")
    uvicorn.run(app, host=HOST, port=PUERTO, log_level="warning")
