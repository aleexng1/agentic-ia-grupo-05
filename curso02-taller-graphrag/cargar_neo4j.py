"""Paso 5 del taller: sube data/fichas.jsonl a Neo4j como grafo, con embeddings de Gemini.

Modelo del grafo:
    (:Producto {sku, nombre, precio, es_replica, texto, embedding})
    (:Producto)-[:DE_MARCA]->(:Marca {nombre})          ("Sin marca" también es una Marca)
    (:Producto)-[:EN_CATEGORIA]->(:Categoria {nombre})
    (:Producto)-[:DE_LINEA]->(:Linea {nombre})
    (:Linea)-[:DE_MARCA]->(:Marca)
    (:Producto)-[:IMITA]->(:Linea copiada)              (solo réplicas)
    (:Producto)-[:TIENE]->(:Caracteristica {tipo, valor})  (almacenamiento, ram, pantalla, sistema)

Los campos null no crean nodo ni flecha.

Se puede correr las veces que quieras sin duplicar nada:
  - MERGE + restricciones de unicidad en todos los nodos.
  - Las flechas de un producto se recrean desde su ficha actual (si la ficha cambió, el grafo la sigue).
  - Si un producto ya tiene embedding y su texto no cambió, no se vuelve a calcular.

Uso (desde curso02-taller-graphrag/, con el .venv activado):
    python cargar_neo4j.py                 # sube todo
    python cargar_neo4j.py --limit 5       # prueba con 5 productos
    python cargar_neo4j.py --recalcular    # fuerza recalcular todos los embeddings
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

import certifi
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from neo4j import GraphDatabase, TrustCustomCAs
from neo4j.exceptions import AuthError, ServiceUnavailable

BASE = Path(__file__).resolve().parent
FICHAS = BASE / "data" / "fichas.jsonl"
PENDIENTES = BASE / "data" / "pendientes_neo4j.json"

DIMENSIONES = 768
NOMBRE_INDICE = "producto_embedding"

INTENTOS = 4  # intentos por producto para el embedding
ESPERA_BASE = 5  # segundos; se duplica en cada reintento (5, 10, 20)
FALLOS_SEGUIDOS_MAX = 5  # si fallan tantos productos seguidos, se corta la corrida
CODIGOS_REINTENTABLES = {408, 429, 500, 502, 503, 504}

RELACIONES = "DE_MARCA|EN_CATEGORIA|DE_LINEA|IMITA|TIENE"

# Esquemas "seguros" de Neo4j -> esquema equivalente sin verificación incluida en la URI.
# Con certifi hay que pasar los certificados por separado, y eso solo se permite con estos.
ESQUEMAS_SEGUROS = {"neo4j+s": "neo4j", "bolt+s": "bolt"}

AYUDA_CONEXION = """\
No pude conectarme a Neo4j. Causas posibles:
  1. Python sin certificados raíz (pasa con el Python de python.org en Mac): el driver falla con
     «Unable to retrieve routing information». Este programa ya usa los certificados de certifi;
     si ves este mensaje, confirma que certifi está instalado (pip install -r requirements.txt).
  2. La instancia de Aura gratis está pausada (se pausa por inactividad): reanúdala en la consola de Aura.
  3. NEO4J_URI mal copiado (debe verse como neo4j+s://xxxxxxxx.databases.neo4j.io) o sin internet.
Detalle técnico: {detalle}"""


# ---------------------------------------------------------------------------
# Ficha -> texto, características y precio
# ---------------------------------------------------------------------------
def limpio(valor) -> Optional[str]:
    if valor is None:
        return None
    texto = str(valor).strip()
    return texto or None


def caracteristicas(f: dict) -> list[tuple[str, str]]:
    """(tipo, valor) de las características que la ficha sí trae; el valor es el nodo compartido."""
    resultado = []
    if f.get("almacenamiento_gb") is not None:
        resultado.append(("almacenamiento", f"{int(f['almacenamiento_gb'])} GB"))
    if f.get("ram_gb") is not None:
        resultado.append(("ram", f"{int(f['ram_gb'])} GB"))
    if f.get("pantalla_pulgadas") is not None:
        resultado.append(("pantalla", f'{float(f["pantalla_pulgadas"])}"'))
    if limpio(f.get("sistema")):
        resultado.append(("sistema", limpio(f["sistema"])))
    return resultado


def precio_de(f: dict) -> Optional[int]:
    """Precio que paga el cliente: el de oferta; si no hay, el normal."""
    precio = f.get("precio_oferta")
    if precio is None:
        precio = f.get("precio_normal")
    return None if precio is None else int(precio)


def formato_precio(n: int) -> str:
    return "$" + f"{n:,}".replace(",", ".")


def construir_texto(f: dict) -> str:
    """Frase que se guarda en Producto.texto y de la que sale el embedding."""
    partes = [(limpio(f.get("nombre")) or f["sku"]).rstrip(" .")]
    partes.append(f"Marca: {limpio(f.get('marca')) or 'Sin marca'}")
    if limpio(f.get("categoria")):
        partes.append(f"Categoría: {limpio(f['categoria'])}")
    if f.get("es_replica"):
        linea, marca = limpio(f.get("copia_linea")), limpio(f.get("copia_marca"))
        if linea and marca:
            partes.append(f"Réplica que imita {linea} de {marca}")
        elif linea:
            partes.append(f"Réplica que imita {linea}")
        elif marca:
            partes.append(f"Réplica que imita a {marca}")
        else:
            partes.append("Réplica")
    partes += [f"{tipo}: {valor}" for tipo, valor in caracteristicas(f)]
    precio = precio_de(f)
    if precio is not None:
        partes.append(f"Precio: {formato_precio(precio)}")
    return ". ".join(partes)


def leer_fichas() -> list[dict]:
    if not FICHAS.exists():
        sys.exit(f"No encuentro {FICHAS.relative_to(BASE)}. Corre primero extraer_fichas.py.")
    por_sku: dict[str, dict] = {}
    with FICHAS.open(encoding="utf-8") as archivo:
        for linea in archivo:
            if linea.strip():
                ficha = json.loads(linea)
                por_sku[ficha["sku"]] = ficha  # si un SKU se repite, gana el último
    return list(por_sku.values())


# ---------------------------------------------------------------------------
# Conexión a Neo4j
# ---------------------------------------------------------------------------
def conectar(uri: str, usuario: str, clave: str):
    """Abre el driver usando los certificados raíz de certifi para neo4j+s:// / bolt+s://."""
    esquema, _, resto = uri.partition("://")
    opciones: dict = {}
    if esquema in ESQUEMAS_SEGUROS:
        uri = f"{ESQUEMAS_SEGUROS[esquema]}://{resto}"
        opciones = {"encrypted": True, "trusted_certificates": TrustCustomCAs(certifi.where())}
    driver = GraphDatabase.driver(uri, auth=(usuario, clave), **opciones)
    try:
        driver.verify_connectivity()
    except AuthError:
        driver.close()
        sys.exit("Neo4j rechazó el usuario o la contraseña. En instancias nuevas de Aura el usuario "
                 "NO es «neo4j»: es el ID de la instancia (revisa el .txt que descargaste).")
    except Exception as e:  # ServiceUnavailable, errores de SSL, DNS, etc.
        driver.close()
        sys.exit(AYUDA_CONEXION.format(detalle=f"{type(e).__name__}: {str(e)[:300]}"))
    return driver


# ---------------------------------------------------------------------------
# Esquema: restricciones e índice vectorial
# ---------------------------------------------------------------------------
RESTRICCIONES = [
    "CREATE CONSTRAINT producto_sku_unico IF NOT EXISTS FOR (p:Producto) REQUIRE p.sku IS UNIQUE",
    "CREATE CONSTRAINT marca_nombre_unico IF NOT EXISTS FOR (m:Marca) REQUIRE m.nombre IS UNIQUE",
    "CREATE CONSTRAINT categoria_nombre_unico IF NOT EXISTS FOR (c:Categoria) REQUIRE c.nombre IS UNIQUE",
    "CREATE CONSTRAINT linea_nombre_unico IF NOT EXISTS FOR (l:Linea) REQUIRE l.nombre IS UNIQUE",
    "CREATE CONSTRAINT caracteristica_unica IF NOT EXISTS "
    "FOR (k:Caracteristica) REQUIRE (k.tipo, k.valor) IS UNIQUE",
]

CREAR_INDICE = (
    f"CREATE VECTOR INDEX {NOMBRE_INDICE} IF NOT EXISTS FOR (p:Producto) ON (p.embedding) "
    f"OPTIONS {{indexConfig: {{`vector.dimensions`: {DIMENSIONES}, "
    f"`vector.similarity_function`: 'cosine'}}}}"
)


def preparar_indice(sesion) -> None:
    """Crea el índice vectorial; si ya existe, comprueba que su configuración sea la esperada."""
    filas = sesion.run(
        "SHOW INDEXES YIELD name, type, labelsOrTypes, properties, options WHERE name = $nombre",
        nombre=NOMBRE_INDICE,
    ).data()
    if not filas:
        sesion.run(CREAR_INDICE).consume()
        print(f"Índice vectorial «{NOMBRE_INDICE}» creado ({DIMENSIONES} dimensiones, cosine).")
        return

    indice = filas[0]
    config = (indice.get("options") or {}).get("indexConfig") or {}
    dimensiones = config.get("vector.dimensions")
    # Aura devuelve la similitud como 'COSINE' (mayúsculas): se compara sin distinguir mayúsculas.
    similitud = str(config.get("vector.similarity_function", "")).lower()

    problemas = []
    if indice.get("type") != "VECTOR":
        problemas.append(f"no es un índice vectorial (es {indice.get('type')})")
    if indice.get("labelsOrTypes") != ["Producto"] or indice.get("properties") != ["embedding"]:
        problemas.append(f"está sobre {indice.get('labelsOrTypes')}.{indice.get('properties')} "
                         "y debería estar sobre Producto.embedding")
    if dimensiones != DIMENSIONES:
        problemas.append(f"tiene {dimensiones} dimensiones y deberían ser {DIMENSIONES}")
    if similitud != "cosine":
        problemas.append(f"usa similitud «{similitud}» y debería ser cosine")
    if problemas:
        sys.exit(f"El índice «{NOMBRE_INDICE}» ya existe pero no coincide: " + "; ".join(problemas) +
                 ".\nBórralo en Neo4j (DROP INDEX producto_embedding) y vuelve a correr el programa; "
                 "no lo borro yo para no perder datos sin que lo decidas.")
    print(f"Índice vectorial «{NOMBRE_INDICE}» ya existe y coincide ({DIMENSIONES} dim, cosine).")


def preparar_esquema(driver) -> None:
    with driver.session() as sesion:
        for sentencia in RESTRICCIONES:
            sesion.run(sentencia).consume()
        preparar_indice(sesion)
        sesion.run("CALL db.awaitIndexes(120)").consume()


# ---------------------------------------------------------------------------
# Embeddings con Gemini
# ---------------------------------------------------------------------------
def pedir_embedding(cliente: genai.Client, modelo: str, texto: str) -> list[float]:
    """Calcula el embedding con reintentos ante límite de uso o errores del servidor."""
    ultimo_error: Exception | None = None
    for intento in range(1, INTENTOS + 1):
        try:
            respuesta = cliente.models.embed_content(
                model=modelo,
                contents=texto,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    output_dimensionality=DIMENSIONES,
                ),
            )
            vector = list(respuesta.embeddings[0].values)
            break
        except errors.APIError as e:
            ultimo_error = e
            if e.code not in CODIGOS_REINTENTABLES:
                raise  # clave, modelo o petición mal: reintentar no ayuda
        except Exception as e:  # red caída, respuesta vacía, etc.
            ultimo_error = e
        if intento == INTENTOS:
            raise ultimo_error  # type: ignore[misc]
        espera = ESPERA_BASE * 2 ** (intento - 1)
        print(f"    embedding: intento {intento}/{INTENTOS} falló ({type(ultimo_error).__name__}); "
              f"espero {espera}s…")
        time.sleep(espera)

    if len(vector) != DIMENSIONES:
        sys.exit(f"El modelo de embeddings devolvió {len(vector)} dimensiones y el índice es de "
                 f"{DIMENSIONES}. Revisa MODELO_EMBEDDINGS en el .env.")
    return vector


# ---------------------------------------------------------------------------
# Escritura de un producto (una transacción por producto)
# ---------------------------------------------------------------------------
def subir_producto(tx, f: dict, texto: str, embedding: Optional[list[float]]) -> None:
    sku = f["sku"]
    marca = limpio(f.get("marca")) or "Sin marca"
    categoria = limpio(f.get("categoria"))
    linea = limpio(f.get("linea"))

    # 1. El producto y sus propiedades (embedding solo si hay uno nuevo)
    tx.run(
        "MERGE (p:Producto {sku: $sku}) "
        "SET p.nombre = $nombre, p.precio = $precio, p.es_replica = $es_replica, p.texto = $texto",
        sku=sku, nombre=limpio(f.get("nombre")), precio=precio_de(f),
        es_replica=bool(f.get("es_replica")), texto=texto,
    )
    if embedding is not None:
        tx.run("MATCH (p:Producto {sku: $sku}) SET p.embedding = $embedding", sku=sku, embedding=embedding)

    # 2. Borra sus flechas anteriores para recrearlas desde la ficha actual (evita flechas viejas)
    tx.run(f"MATCH (:Producto {{sku: $sku}})-[r:{RELACIONES}]->() DELETE r", sku=sku)

    # 3. Marca (siempre; "Sin marca" es una marca más)
    tx.run(
        "MATCH (p:Producto {sku: $sku}) "
        "MERGE (m:Marca {nombre: $marca}) MERGE (p)-[:DE_MARCA]->(m)",
        sku=sku, marca=marca,
    )

    # 4. Categoría
    if categoria:
        tx.run(
            "MATCH (p:Producto {sku: $sku}) "
            "MERGE (c:Categoria {nombre: $categoria}) MERGE (p)-[:EN_CATEGORIA]->(c)",
            sku=sku, categoria=categoria,
        )

    # 5. Línea del producto, conectada a su marca
    if linea:
        tx.run(
            "MATCH (p:Producto {sku: $sku}) MATCH (m:Marca {nombre: $marca}) "
            "MERGE (l:Linea {nombre: $linea}) "
            "MERGE (p)-[:DE_LINEA]->(l) MERGE (l)-[:DE_MARCA]->(m)",
            sku=sku, marca=marca, linea=linea,
        )

    # 6. Réplica: la línea que imita, conectada a la marca que imita
    copia_linea = limpio(f.get("copia_linea")) if f.get("es_replica") else None
    copia_marca = limpio(f.get("copia_marca")) if f.get("es_replica") else None
    if copia_linea:
        tx.run(
            "MATCH (p:Producto {sku: $sku}) "
            "MERGE (lc:Linea {nombre: $copia_linea}) MERGE (p)-[:IMITA]->(lc)",
            sku=sku, copia_linea=copia_linea,
        )
        if copia_marca:
            tx.run(
                "MATCH (lc:Linea {nombre: $copia_linea}) "
                "MERGE (mc:Marca {nombre: $copia_marca}) MERGE (lc)-[:DE_MARCA]->(mc)",
                copia_linea=copia_linea, copia_marca=copia_marca,
            )

    # 7. Características: un nodo por (tipo, valor), compartido entre productos
    cs = [{"tipo": tipo, "valor": valor} for tipo, valor in caracteristicas(f)]
    if cs:
        tx.run(
            "MATCH (p:Producto {sku: $sku}) UNWIND $cs AS c "
            "MERGE (k:Caracteristica {tipo: c.tipo, valor: c.valor}) MERGE (p)-[:TIENE]->(k)",
            sku=sku, cs=cs,
        )


def embeddings_guardados(driver) -> dict[str, Optional[str]]:
    """sku -> texto con el que se calculó el embedding que ya está en Neo4j."""
    with driver.session() as sesion:
        filas = sesion.run(
            "MATCH (p:Producto) WHERE p.embedding IS NOT NULL RETURN p.sku AS sku, p.texto AS texto"
        )
        return {fila["sku"]: fila["texto"] for fila in filas}


# ---------------------------------------------------------------------------
# Resumen
# ---------------------------------------------------------------------------
def mostrar_resumen(driver, pendientes: list[dict], calculados: int, reutilizados: int) -> None:
    with driver.session() as sesion:
        nodos = {fila["tipo"]: fila["n"] for fila in sesion.run(
            "MATCH (n) UNWIND labels(n) AS tipo RETURN tipo, count(*) AS n")}
        relaciones = {fila["tipo"]: fila["n"] for fila in sesion.run(
            f"MATCH ()-[r:{RELACIONES}]->() RETURN type(r) AS tipo, count(*) AS n")}
        con_embedding = sesion.run(
            "MATCH (p:Producto) WHERE p.embedding IS NOT NULL RETURN count(p) AS n").single()["n"]
        replicas = sesion.run(
            "MATCH (p:Producto) WHERE p.es_replica = true RETURN count(p) AS n").single()["n"]
        lineas_ambiguas = sesion.run(
            "MATCH (l:Linea)-[:DE_MARCA]->(m:Marca) WITH l, collect(m.nombre) AS marcas "
            "WHERE size(marcas) > 1 RETURN l.nombre AS linea, marcas LIMIT 10").data()

    print("\n===== RESUMEN =====")
    print("Nodos por tipo:")
    for tipo in ["Producto", "Marca", "Categoria", "Linea", "Caracteristica"]:
        print(f"  {tipo:<15} {nodos.get(tipo, 0)}")
    print(f"Relaciones (total): {sum(relaciones.values())}")
    for tipo, n in sorted(relaciones.items()):
        print(f"  {tipo:<15} {n}")
    print(f"Productos con embedding: {con_embedding} de {nodos.get('Producto', 0)} "
          f"(esta corrida: {calculados} calculados, {reutilizados} reutilizados)")
    print(f"Réplicas: {replicas}")
    print(f"Pendientes: {len(pendientes)}"
          + (f"  (detalle en {PENDIENTES.relative_to(BASE)})" if pendientes else ""))
    if lineas_ambiguas:
        print("\nAviso: estas líneas quedaron conectadas a más de una marca (el nombre de Linea es único):")
        for fila in lineas_ambiguas:
            print(f"  {fila['linea']}: {', '.join(fila['marcas'])}")


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Sube las fichas a Neo4j con embeddings de Gemini.")
    parser.add_argument("--limit", type=int, default=None, help="procesar solo los primeros N productos")
    parser.add_argument("--recalcular", action="store_true", help="recalcular todos los embeddings")
    args = parser.parse_args()

    load_dotenv(BASE / ".env")
    faltan = [v for v in ["NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD", "GOOGLE_API_KEY",
                          "MODELO_EMBEDDINGS"] if not os.getenv(v)]
    if faltan:
        sys.exit(f"Faltan variables en el .env: {', '.join(faltan)} (ver .env.example).")
    modelo_emb = os.environ["MODELO_EMBEDDINGS"]

    fichas = leer_fichas()
    if args.limit is not None:
        fichas = fichas[: args.limit]

    driver = conectar(os.environ["NEO4J_URI"], os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"])
    cliente = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    pendientes: list[dict] = []
    calculados = reutilizados = 0
    try:
        preparar_esquema(driver)
        guardados = {} if args.recalcular else embeddings_guardados(driver)
        print(f"Modelo de embeddings: {modelo_emb} | fichas a subir: {len(fichas)}")

        fallos_seguidos = 0
        for i, ficha in enumerate(fichas, start=1):
            sku = ficha["sku"]
            texto = construir_texto(ficha)
            try:
                if guardados.get(sku) == texto:
                    embedding = None  # ya tiene embedding de este mismo texto: se conserva
                else:
                    embedding = pedir_embedding(cliente, modelo_emb, texto)
                with driver.session() as sesion:
                    sesion.execute_write(subir_producto, ficha, texto, embedding)
            except ServiceUnavailable as e:
                raise SystemExit(AYUDA_CONEXION.format(detalle=f"{type(e).__name__}: {str(e)[:300]}"))
            except Exception as e:  # límite de uso agotado tras reintentos, error de Neo4j, etc.
                detalle = f"{type(e).__name__}: {str(e)[:300]}"
                pendientes.append({"sku": sku, "error": detalle})
                fallos_seguidos += 1
                print(f"[{i}/{len(fichas)}] {sku}: PENDIENTE ({detalle})")
                if fallos_seguidos >= FALLOS_SEGUIDOS_MAX:
                    print(f"\n{FALLOS_SEGUIDOS_MAX} productos seguidos fallaron: corto la corrida. "
                          "Revisa la clave, el modelo o el límite de uso y vuelve a correrlo; "
                          "lo ya subido no se repite.")
                    pendientes += [{"sku": f["sku"], "error": "no intentado (corrida cortada)"}
                                   for f in fichas[i:]]
                    break
                continue

            fallos_seguidos = 0
            if embedding is None:
                reutilizados += 1
            else:
                calculados += 1
            estado = "embedding reutilizado" if embedding is None else "embedding nuevo"
            print(f"[{i}/{len(fichas)}] {sku}: subido ({estado})")

        if pendientes:
            PENDIENTES.write_text(json.dumps(pendientes, ensure_ascii=False, indent=2), encoding="utf-8")
        elif PENDIENTES.exists():
            PENDIENTES.unlink()
        mostrar_resumen(driver, pendientes, calculados, reutilizados)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
