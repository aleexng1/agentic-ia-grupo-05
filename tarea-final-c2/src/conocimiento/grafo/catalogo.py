"""Modelo y validación offline del catálogo académico de GraphRAG de Eduardo."""

import json
import re
from pathlib import Path
from typing import Literal
from unicodedata import category, normalize

from pydantic import BaseModel, ConfigDict, Field, ValidationError

DATOS = Path(__file__).resolve().parents[3] / "datos"
RUTA_CATALOGO = DATOS / "cargos_niveles.json"
RUTA_POLITICA = DATOS / "politica_ficticia.md"
PROYECTO = "grupo05-tarea-final-c2-graphrag"
DOCUMENTO = "POL-RG-01"
VERSION = "1.6"
POLITICAS = frozenset({"P02", "P03"})
ESTADO_PROPUESTA = "propuesta_academica_pendiente_de_aprobacion"
RELACIONES = ("TIENE_NIVEL", "PUEDE_RENDIR", "TIENE_TOPE")
_ESTADIA = {"desayuno", "almuerzo", "cena", "hotel", "hostal"}


class ErrorCatalogo(ValueError):
    """Catálogo inválido; el mensaje no contiene datos ingresados."""


class _Estricto(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")


class _Entidad(_Estricto):
    id: str = Field(min_length=1, max_length=100)
    nombre: str = Field(min_length=1, max_length=100)


class _Cargo(_Entidad):
    nivel_id: str


class _Categoria(_Entidad):
    tope_clp: int = Field(gt=0, le=2**63 - 1)
    fuente: str


class _Elegibilidad(_Estricto):
    nivel_id: str
    categorias: list[str] = Field(min_length=1)


class _Normativa(_Estricto):
    codigo: Literal["POL-RG-01"]
    version: Literal["1.6"]
    categorias: list[_Categoria] = Field(min_length=10, max_length=10)


class _Organizacion(_Estricto):
    niveles: list[_Entidad] = Field(min_length=1)
    cargos: list[_Cargo] = Field(min_length=1)
    elegibilidad_propuesta: list[_Elegibilidad] = Field(min_length=1)


class Catalogo(_Estricto):
    proyecto: Literal["grupo05-tarea-final-c2-graphrag"]
    version_catalogo: int = Field(gt=0)
    estado: Literal["propuesta_academica_pendiente_de_aprobacion"]
    normativa: _Normativa
    organizacion_ficticia: _Organizacion


def normalizar(texto: str) -> str:
    """Normaliza espacios, mayúsculas y diacríticos; no elimina puntuación."""
    texto = "".join(c for c in normalize("NFD", texto.casefold()) if category(c) != "Mn")
    return " ".join(texto.split())


def slug(texto: str) -> str:
    return normalizar(texto).replace(" ", "-")


def fuente_para(politica: str) -> str:
    return f"datos/politica_ficticia.md#{politica}"


def id_tope(categoria_id: str) -> str:
    return f"tope:{DOCUMENTO}:{VERSION}:{categoria_id}"


def _topes_documentados(texto: str) -> dict:
    codigo = re.findall(r"^\| Código \| ([^|]+) \|\s*$", texto, re.M)
    version = re.findall(r"^\| Versión \| ([0-9.]+)(?: \([^|\n]+\))? \|\s*$", texto, re.M)
    if codigo != [DOCUMENTO] or version != [VERSION]:
        raise ErrorCatalogo("La fuente no corresponde a POL-RG-01 v1.6.")
    topes = {}
    secciones = re.split(r"^## (P[0-9]{2}) — [^\n]+$", texto, flags=re.M)
    leidas = set()
    for politica, contenido in zip(secciones[1::2], secciones[2::2], strict=True):
        if politica not in POLITICAS:
            continue
        lineas = re.findall(r"^\*\*Topes \(por documento\)\.\*\* ([^\n]+)$", contenido, re.M)
        if politica in leidas or len(lineas) != 1:
            raise ErrorCatalogo("La fuente no tiene una sección de topes única para P02/P03.")
        leidas.add(politica)
        nombres = set()
        for item in re.split(r"\.\s+", lineas[0].strip().removesuffix(".")):
            coincidencia = re.fullmatch(r"([^:]+): \$([0-9]{1,3}(?:\.[0-9]{3})*)", item)
            if coincidencia is None:
                raise ErrorCatalogo("La fuente contiene un formato de tope inesperado.")
            nombre, monto = coincidencia.groups()
            clave = slug(nombre)
            if clave in nombres:
                raise ErrorCatalogo("La fuente contiene topes duplicados.")
            nombres.add(clave)
            topes[f"{politica}:{clave}"] = (nombre, int(monto.replace(".", "")), fuente_para(politica))
        if nombres != _ESTADIA:
            raise ErrorCatalogo("La fuente no contiene las cinco categorías de estadía esperadas.")
    if leidas != POLITICAS:
        raise ErrorCatalogo("No se encontraron ambas secciones de viajes en la fuente normativa.")
    return topes


def _ids_entidades(entidades, prefijo: str) -> set[str]:
    ids, claves = set(), set()
    for entidad in entidades:
        clave = normalizar(entidad.nombre)
        if entidad.id in ids or clave in claves:
            raise ErrorCatalogo("El catálogo contiene cargos o niveles duplicados.")
        if not re.fullmatch(rf"{prefijo}:[a-z0-9]+(?:-[a-z0-9]+)*", entidad.id):
            raise ErrorCatalogo("El catálogo contiene un identificador organizacional inválido.")
        if not clave or not entidad.nombre.isprintable() or entidad.nombre != " ".join(entidad.nombre.split()):
            raise ErrorCatalogo("El catálogo contiene un nombre organizacional inválido.")
        ids.add(entidad.id)
        claves.add(clave)
    return ids


def validar_catalogo(datos: object, politica: str) -> Catalogo:
    """Rechaza una propuesta incoherente antes de crear cualquier driver."""
    try:
        catalogo = Catalogo.model_validate(datos)
    except ValidationError:
        raise ErrorCatalogo("La estructura o los tipos del catálogo son inválidos.") from None

    esperados = _topes_documentados(politica)
    categorias = {}
    for categoria in catalogo.normativa.categorias:
        if categoria.id in categorias:
            raise ErrorCatalogo("El catálogo contiene una categoría duplicada.")
        categorias[categoria.id] = (categoria.nombre, categoria.tope_clp, categoria.fuente)
    if categorias != esperados:
        raise ErrorCatalogo("Las categorías, montos o fuentes no coinciden con la política P02/P03.")

    org = catalogo.organizacion_ficticia
    niveles = _ids_entidades(org.niveles, "nivel")
    _ids_entidades(org.cargos, "cargo")
    if any(cargo.nivel_id not in niveles for cargo in org.cargos):
        raise ErrorCatalogo("Un cargo referencia un nivel inexistente.")

    vistos = set()
    for relacion in org.elegibilidad_propuesta:
        if relacion.nivel_id in vistos or len(set(relacion.categorias)) != len(relacion.categorias):
            raise ErrorCatalogo("La propuesta contiene relaciones de elegibilidad duplicadas.")
        if relacion.nivel_id not in niveles or set(relacion.categorias) - categorias.keys():
            raise ErrorCatalogo("Una elegibilidad referencia un nivel o categoría inexistente.")
        vistos.add(relacion.nivel_id)
    return catalogo


def _objeto_sin_duplicados(pares):
    objeto = dict(pares)
    if len(objeto) != len(pares):
        raise ErrorCatalogo("El JSON contiene claves duplicadas.")
    return objeto


def leer_catalogo(ruta_datos: str) -> Catalogo:
    try:
        ruta = Path(ruta_datos).resolve()
        if not ruta.is_relative_to(DATOS) or ruta.suffix.lower() != ".json":
            raise ErrorCatalogo("El catálogo debe ser un archivo JSON dentro de datos/.")
        datos = json.loads(ruta.read_text(encoding="utf-8"), object_pairs_hook=_objeto_sin_duplicados)
        politica = RUTA_POLITICA.read_text(encoding="utf-8")
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError):
        raise ErrorCatalogo("No se pudo leer el catálogo JSON o la fuente normativa.") from None
    return validar_catalogo(datos, politica)


def conteos(catalogo: Catalogo) -> dict[str, int]:
    org = catalogo.organizacion_ficticia
    categorias = len(catalogo.normativa.categorias)
    return {
        "nodos": len(org.cargos) + len(org.niveles) + 2 * categorias,
        "relaciones": len(org.cargos) + categorias + sum(len(r.categorias) for r in org.elegibilidad_propuesta),
    }
