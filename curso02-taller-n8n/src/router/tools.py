"""Herramientas de los agentes del router.

Preventa: buscar_productos, ver_producto y mejores_ofertas consultan catalogo.productos_unicos (solo lectura).
El SQL se arma únicamente con fragmentos fijos de este archivo; lo que escribe el cliente o el modelo
(palabras, marca, precio, sku_id) viaja siempre como parámetro (%s). Ver src/router/catalogo.py.

Postventa: estado_pedido (data/pedidos.json), politica (data/politicas.md) y crear_reclamo (src/router/reclamos.py).
"""

import json
import logging
import re
import unicodedata
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Literal

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from src.router import catalogo, reclamos

log = logging.getLogger("uvicorn.error")

TABLA = catalogo.TABLA

COLUMNAS_LISTA = "sku_id, nombre, marca, precio_internet, descuento_pct, rating"
COLUMNAS_DETALLE = (
    "sku_id, nombre, marca, categoria, subcategoria, precio_normal, precio_internet, "
    "descuento_pct, rating, tienda_oficial, link, imagen"
)

MAX_RESULTADOS = 5
MAX_PALABRAS = 8
MAX_LARGO_TEXTO = 80


def _fila(fila: dict) -> dict:
    """Rating (numeric) a float para que se serialice bien. Lo que viene vacío queda en None."""
    return {k: (float(v) if isinstance(v, Decimal) else v) for k, v in fila.items()}


def _consultar(sql: str, params: list[Any]) -> list[dict] | str:
    """Consulta el catálogo; si no está disponible devuelve el texto 'catálogo no disponible'."""
    try:
        return [_fila(f) for f in catalogo.consultar(sql, params)]
    except catalogo.CatalogoNoDisponible as e:
        log.warning("catálogo no disponible: %s", e)  # el motivo ya viene sin secretos
        return catalogo.MENSAJE_NO_DISPONIBLE


def _texto(valor: str | None) -> str:
    return " ".join((valor or "").split())[:MAX_LARGO_TEXTO]


@tool
def buscar_productos(
    consulta: str,
    categoria: Literal["Smartphones", "Televisores"] | None = None,
    marca: str | None = None,
    precio_max: int | None = None,
) -> list[dict] | str:
    """Busca productos en el catálogo de la tienda. Devuelve hasta 5, los de mejor rating primero.

    Args:
        consulta: palabras que deben aparecer en el nombre del producto (por ejemplo "smart tv 55").
            Cada palabra debe estar en el nombre, sin distinguir mayúsculas.
        categoria: "Smartphones" o "Televisores". Opcional.
        marca: marca del producto (por ejemplo "Samsung"). Opcional. Se busca en la marca y en el nombre.
        precio_max: precio máximo en pesos chilenos (CLP), sin puntos. Opcional.

    Cada resultado trae sku_id, nombre, marca, precio_internet (CLP), descuento_pct y rating (1 a 5).
    Un dato en null significa que el catálogo no lo tiene.
    """
    palabras = [p for p in _texto(consulta).split(" ") if p][:MAX_PALABRAS]
    marca = _texto(marca)
    if not (palabras or categoria or marca or precio_max):
        return "Indica qué producto buscar (por ejemplo, 'smart tv 55')."

    sql = f"SELECT {COLUMNAS_LISTA} FROM {TABLA} WHERE TRUE"
    params: list[Any] = []
    for palabra in palabras:
        sql += " AND strpos(lower(nombre), lower(%s)) > 0"
        params.append(palabra)
    if marca:
        sql += " AND (strpos(lower(marca), lower(%s)) > 0 OR strpos(lower(nombre), lower(%s)) > 0)"
        params += [marca, marca]
    if categoria:
        sql += " AND categoria = %s"
        params.append(categoria)
    if precio_max:
        sql += " AND precio_internet <= %s"
        params.append(int(precio_max))
    sql += " ORDER BY rating DESC NULLS LAST, precio_internet ASC, sku_id ASC LIMIT %s"
    params.append(MAX_RESULTADOS)

    resultado = _consultar(sql, params)
    return resultado or "No encontré productos con esos criterios."


@tool
def ver_producto(sku_id: str) -> dict | str:
    """Devuelve todo el detalle de un producto, incluido su link (el link solo se obtiene aquí).

    Args:
        sku_id: el sku_id que entregó buscar_productos o mejores_ofertas.

    Trae sku_id, nombre, marca, categoria, subcategoria, precio_normal, precio_internet (CLP),
    descuento_pct, rating, tienda_oficial, link e imagen. Un dato en null significa que el catálogo no lo tiene.
    """
    sku = _texto(sku_id)
    if not sku:
        return "Falta el sku_id del producto."
    resultado = _consultar(f"SELECT {COLUMNAS_DETALLE} FROM {TABLA} WHERE sku_id = %s LIMIT %s", [sku, 1])
    if isinstance(resultado, str):
        return resultado
    return resultado[0] if resultado else "No encontré un producto con ese sku_id."


@tool
def mejores_ofertas(
    categoria: Literal["Smartphones", "Televisores"] | None = None,
    limite: int = 5,
) -> list[dict] | str:
    """Devuelve los productos con mayor descuento_pct del catálogo.

    Args:
        categoria: "Smartphones" o "Televisores". Opcional: sin ella mira toda la tienda.
        limite: cuántos devolver (por defecto 5, máximo 10).

    Cada resultado trae sku_id, nombre, marca, precio_internet (CLP), descuento_pct y rating (1 a 5).
    """
    limite = max(1, min(int(limite), 10))
    sql = f"SELECT {COLUMNAS_LISTA} FROM {TABLA} WHERE descuento_pct IS NOT NULL"
    params: list[Any] = []
    if categoria:
        sql += " AND categoria = %s"
        params.append(categoria)
    sql += " ORDER BY descuento_pct DESC, rating DESC NULLS LAST, sku_id ASC LIMIT %s"
    params.append(limite)

    resultado = _consultar(sql, params)
    return resultado or "No encontré productos con descuento."


TOOLS_PREVENTA = [buscar_productos, ver_producto, mejores_ofertas]


# ── Postventa ────────────────────────────────────────────────────────────────

DATOS = Path(__file__).resolve().parents[2] / "data"
PEDIDOS_JSON = DATOS / "pedidos.json"
POLITICAS_MD = DATOS / "politicas.md"

NO_EXISTE = "no existe"
MOTIVO_DERIVAR = "derivar a persona"
MAX_MOTIVO = 200
MAX_DETALLE = 1000


def hoy() -> date:
    """La fecha de hoy (aparte para poder fijarla en las pruebas)."""
    return date.today()


def _pedidos() -> dict[str, dict]:
    pedidos = json.loads(PEDIDOS_JSON.read_text(encoding="utf-8"))
    return {str(p["numero"]): p for p in pedidos}


def _sin_tildes(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn").lower().strip()


@tool
def estado_pedido(numero: str) -> dict | str:
    """Devuelve el pedido de un cliente: estado, fechas y código de seguimiento. Si no existe, devuelve "no existe".

    Args:
        numero: el número del pedido, por ejemplo "4521".

    El estado es preparando, despachado, entregado o devuelto. Trae cliente, productos, fecha_compra,
    fecha_estimada_entrega, fecha_entrega (solo si ya se entregó), codigo_seguimiento (null si aún no sale) y
    dias_desde_la_entrega (solo si ya se entregó). Un dato en null significa que no existe todavía.
    """
    digitos = re.sub(r"\D", "", numero or "")
    if not digitos:
        return "Falta el número del pedido."
    pedido = _pedidos().get(digitos)
    if pedido is None:
        return NO_EXISTE
    pedido = dict(pedido)
    if pedido.get("fecha_entrega"):
        pedido["dias_desde_la_entrega"] = (hoy() - date.fromisoformat(pedido["fecha_entrega"])).days
    return pedido


@tool
def politica(tema: Literal["devoluciones", "cambios", "garantia"]) -> str:
    """Devuelve la política de la tienda sobre un tema, tal como está escrita.

    Args:
        tema: "devoluciones", "cambios" o "garantia".
    """
    buscado = _sin_tildes(tema or "")
    secciones = re.split(r"^## +", POLITICAS_MD.read_text(encoding="utf-8"), flags=re.MULTILINE)[1:]
    for seccion in secciones:
        titulo, _, cuerpo = seccion.partition("\n")
        if _sin_tildes(titulo) == buscado:
            return f"{titulo.strip()}\n{cuerpo.strip()}"
    return "No tengo una política sobre ese tema. Los temas son: devoluciones, cambios y garantia."


@tool
def crear_reclamo(numero_pedido: str, motivo: str, detalle: str, config: RunnableConfig) -> dict | str:
    """Crea un reclamo y devuelve su número de ticket (R-0001...). Úsala solo cuando el cliente ya confirmó el motivo.

    Si el cliente pide hablar con una persona, o su caso no cabe en las políticas, crea el reclamo con motivo
    exactamente "derivar a persona" (en ese caso el número de pedido puede ir vacío).

    Args:
        numero_pedido: número del pedido del reclamo, por ejemplo "4521".
        motivo: el motivo en una frase corta, el que confirmó el cliente.
        detalle: lo que contó el cliente, con sus palabras y los datos que importan.
    """
    motivo = " ".join((motivo or "").split())[:MAX_MOTIVO]
    detalle = " ".join((detalle or "").split())[:MAX_DETALLE]
    if not motivo:
        return "Falta el motivo del reclamo."
    derivar = _sin_tildes(motivo) == MOTIVO_DERIVAR

    numero = re.sub(r"\D", "", numero_pedido or "")
    if not derivar:
        if not numero:
            return "Falta el número del pedido: no se creó el reclamo."
        if numero not in _pedidos():
            return f"El pedido {numero} no existe: no se creó el reclamo."
    # El hilo de la conversación sale de la configuración del grafo, nunca de lo que diga el modelo.
    thread_id = str(((config or {}).get("configurable") or {}).get("thread_id") or "desconocido")

    try:
        ticket = reclamos.crear(numero or "sin pedido", motivo, detalle, thread_id)
    except reclamos.ReclamoNoGuardado as e:
        log.warning("No se pudo guardar un reclamo: %s", e)  # el motivo ya viene sin secretos
        return "No pude registrar el reclamo ahora. Pide al cliente que lo intente de nuevo en unos minutos."
    return {"ticket": ticket, "numero_pedido": numero or "sin pedido", "motivo": motivo}


TOOLS_POSTVENTA = [estado_pedido, politica, crear_reclamo]
