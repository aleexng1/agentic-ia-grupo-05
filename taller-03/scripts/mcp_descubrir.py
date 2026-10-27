"""Descubre qué ofrece el servidor MCP de API Colombia y hace llamadas de prueba."""
import asyncio
import json
import os
import time
import unicodedata
from pathlib import Path

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = Path(__file__).resolve().parent / "mcp_descubrir_salida.txt"
MAX_CHARS = 600

lineas: list[str] = []


def imprimir(texto: str = "") -> None:
    print(texto)
    lineas.append(texto)


def recortar(texto: str, maximo: int = MAX_CHARS) -> str:
    texto = texto.strip()
    if len(texto) <= maximo:
        return texto
    return f"{texto[:maximo]}... [recortado, {len(texto)} caracteres en total]"


def a_texto(resultado) -> str:
    """Normaliza la respuesta de una tool (str o lista de bloques) a texto."""
    if isinstance(resultado, str):
        return resultado
    if isinstance(resultado, list):
        partes = []
        for bloque in resultado:
            if isinstance(bloque, dict) and "text" in bloque:
                partes.append(bloque["text"])
            else:
                partes.append(str(bloque))
        return "\n".join(partes)
    return str(resultado)


def sin_acentos(texto: str) -> str:
    base = unicodedata.normalize("NFD", texto)
    return "".join(c for c in base if not unicodedata.combining(c)).lower()


def buscar_id(resultados, nombre: str):
    """Id del resultado cuyo name coincide con `nombre` (search_items también
    encuentra textos que solo mencionan la palabra, así que no sirve el primero)."""
    if not isinstance(resultados, list):
        return None
    for item in resultados:
        if isinstance(item, dict) and sin_acentos(str(item.get("name", ""))) == sin_acentos(nombre):
            return item.get("id")
    return None


def tipo_de(prop: dict) -> str:
    if "type" in prop:
        return str(prop["type"])
    for clave in ("anyOf", "oneOf"):
        if clave in prop:
            return "|".join(tipo_de(p) for p in prop[clave])
    return "?"


def argumentos_de(herramienta) -> str:
    esquema = herramienta.args_schema if isinstance(herramienta.args_schema, dict) else {}
    props = esquema.get("properties", {})
    requeridos = set(esquema.get("required", []))
    if not props:
        return "-"
    return ", ".join(
        f"{nombre}: {tipo_de(prop)}{'' if nombre in requeridos else '?'}"
        for nombre, prop in props.items()
    )


async def llamar(herramientas: dict, nombre: str, **args) -> tuple[str, float]:
    inicio = time.perf_counter()
    resultado = await herramientas[nombre].ainvoke(args)
    ms = (time.perf_counter() - inicio) * 1000
    return a_texto(resultado), ms


async def principal() -> None:
    load_dotenv(RAIZ / ".env")
    url = os.getenv("API_COLOMBIA_MCP_URL")
    if not url:
        imprimir("Falta API_COLOMBIA_MCP_URL en el .env de taller-03/.")
        return

    cliente = MultiServerMCPClient(
        {"api_colombia": {"url": url, "transport": "streamable_http"}}
    )

    imprimir(f"Servidor MCP: {url}")
    inicio = time.perf_counter()
    try:
        lista = await cliente.get_tools()
    except Exception as exc:
        causa = exc.exceptions[0] if hasattr(exc, "exceptions") and exc.exceptions else exc
        imprimir(f"No se pudo conectar al servidor MCP ({type(causa).__name__}: {causa}).")
        imprimir("Revisa la URL en .env y tu conexión a internet.")
        return
    ms = (time.perf_counter() - inicio) * 1000
    herramientas = {h.name: h for h in lista}

    imprimir(f"\n== Herramientas ({len(lista)}) — conexión y listado: {ms:.0f} ms ==")
    imprimir(f"{'NOMBRE':<40} {'ARGUMENTOS':<55} DESCRIPCIÓN")
    for h in sorted(lista, key=lambda x: x.name):
        descripcion = (h.description or "").strip().splitlines()
        primera = descripcion[0] if descripcion else ""
        imprimir(f"{h.name:<40} {argumentos_de(h):<55} {primera}")

    async def paso(titulo: str, nombre: str, **args):
        imprimir(f"\n== {titulo} ==")
        if nombre not in herramientas:
            imprimir(f"La herramienta {nombre} no existe en este servidor.")
            return None
        try:
            texto, ms = await llamar(herramientas, nombre, **args)
        except Exception as exc:
            imprimir(f"Falló {nombre}({args}): {type(exc).__name__}: {exc}")
            return None
        imprimir(f"{nombre}({args}) — {ms:.0f} ms")
        imprimir(recortar(texto))
        return texto

    texto = await paso("Recursos disponibles", "list_colombia_resources")
    if texto:
        try:
            datos = json.loads(texto)
            if isinstance(datos, list):
                imprimir("\nClaves y descripciones:")
                for r in sorted(datos, key=lambda x: x["resource"]):
                    imprimir(f"  {r['resource']:<28} {r['description']}")
        except ValueError:
            pass

    await paso(
        "Convenciones de búsqueda y paginación",
        "get_api_reference",
        resource="department",
    )

    texto = await paso(
        "Prueba 1: buscar Antioquia",
        "search_items",
        resource="department",
        keyword="Antioquia",
    )
    id_depto = None
    if texto:
        try:
            id_depto = buscar_id(json.loads(texto), "Antioquia")
        except ValueError:
            pass
    if id_depto is None:
        imprimir("\nNo se pudo obtener el id de Antioquia; se omite la prueba 2.")
        return

    await paso(
        f"Prueba 2: áreas naturales del departamento {id_depto}",
        "get_natural_areas_by_department",
        departmentId=id_depto,
    )


if __name__ == "__main__":
    try:
        asyncio.run(principal())
    finally:
        SALIDA.write_text("\n".join(lineas) + "\n", encoding="utf-8")
        print(f"\n(Salida guardada en {SALIDA.relative_to(RAIZ)})")
