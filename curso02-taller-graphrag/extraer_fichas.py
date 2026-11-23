"""Paso 3 del taller: extrae una ficha por producto del Excel usando Gemini.

Lee data/productos.xlsx fila por fila, le pide a Gemini (salida estructurada,
temperatura 0) la marca, la línea, las características y si el producto es una
réplica, y guarda cada ficha en data/fichas.jsonl (una línea JSON por producto),
lista para subir a Neo4j más adelante.

Es reanudable: si se corta, al volver a correrlo salta los SKU que ya están en
data/fichas.jsonl. Las filas que fallaron quedan en data/pendientes.json y se
reintentan en la próxima corrida.

Uso (desde curso02-taller-graphrag/):
    python extraer_fichas.py              # procesa todo
    python extraer_fichas.py --limit 5    # prueba con las primeras 5 filas pendientes
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, Field

BASE = Path(__file__).resolve().parent
EXCEL = BASE / "data" / "productos.xlsx"
FICHAS = BASE / "data" / "fichas.jsonl"
PENDIENTES = BASE / "data" / "pendientes.json"

INTENTOS = 4  # intentos por fila antes de dejarla pendiente
ESPERA_BASE = 5  # segundos; se duplica en cada reintento (5, 10, 20)
FALLOS_SEGUIDOS_MAX = 5  # si fallan tantas filas seguidas, se corta la corrida
CODIGOS_REINTENTABLES = {408, 429, 500, 502, 503, 504}

CATEGORIAS = {"Celulares", "Televisores"}  # únicos valores válidos de la ficha

COLUMNAS_EXCEL = ["SKU", "Nombre", "Marca", "Categoría", "Precio normal", "Precio oferta"]

INSTRUCCIONES = """\
Eres un analista de catálogo de una tienda online chilena (precios en pesos chilenos, CLP).
Recibes UNA fila de producto (SKU, nombre, marca, categoría y precios) y devuelves su ficha.

REGLAS GENERALES
- Usa SOLO lo que dice la fila. No inventes datos. Si un dato no aparece en la fila, devuelve null.
- Tu conocimiento del mercado se usa únicamente para juzgar si es una réplica (ver abajo),
  nunca para rellenar características que la fila no trae.

CAMPOS
- marca: la marca de la fila si viene; si no viene, la que aparezca de forma explícita en el nombre
  y sea realmente el fabricante. Si no se puede determinar, "Sin marca".
  Si es réplica, NUNCA pongas la marca del modelo famoso que imita: usa la marca de la fila
  o, si no trae, "Sin marca".
- linea: la línea o modelo tal como aparece en el nombre (ej. "Pixel 8a", "iPhone 12 Pro Max", "Note 14").
  null si el nombre no permite identificarla.
- almacenamiento_gb: almacenamiento interno en GB (entero). 1 TB = 1024 GB.
- ram_gb: memoria RAM en GB (entero). Cuando el nombre trae dos cifras tipo "2 Gb 16 Gb", la menor
  es la RAM y la mayor el almacenamiento. Si hay una sola cifra y no se puede saber a cuál
  corresponde, déjala en null.
- pantalla_pulgadas: tamaño de pantalla en pulgadas (número decimal).
- sistema: sistema operativo solo si el nombre lo dice (ej. "Android", "iOS").

RÉPLICAS
- es_replica = true cuando el nombre usa un modelo famoso (ej. "S25 Ultra", "iPhone 17") pero
  (a) el precio es muy bajo para ese modelo original, o (b) las características no calzan con
  el original (ej. 2 GB de RAM en un supuesto S25 Ultra, pantalla o almacenamiento imposibles).
- Si hay duda razonable y no hay señales claras, es_replica = false.
- Si es_replica = true: copia_linea = línea original que imita (ej. "Galaxy S25 Ultra") y
  copia_marca = marca original que imita (ej. "Samsung").
- Si es_replica = false: copia_linea = null y copia_marca = null.
"""


class Ficha(BaseModel):
    """Esquema fijo que Gemini debe devolver para cada producto."""

    marca: str = Field(description='Marca real del producto o "Sin marca"')
    linea: Optional[str] = Field(description="Línea o modelo según el nombre, o null")
    es_replica: bool = Field(description="True si imita un modelo famoso")
    copia_linea: Optional[str] = Field(description="Línea que imita, o null si no es réplica")
    copia_marca: Optional[str] = Field(description="Marca que imita, o null si no es réplica")
    almacenamiento_gb: Optional[int] = Field(description="Almacenamiento en GB, o null")
    ram_gb: Optional[int] = Field(description="RAM en GB, o null")
    pantalla_pulgadas: Optional[float] = Field(description="Pantalla en pulgadas, o null")
    sistema: Optional[str] = Field(description="Sistema operativo si el nombre lo dice, o null")


def texto_o_none(valor) -> Optional[str]:
    if pd.isna(valor):
        return None
    texto = str(valor).strip()
    return texto or None


def entero_o_none(valor) -> Optional[int]:
    return None if pd.isna(valor) else int(valor)


def cargar_excel() -> pd.DataFrame:
    if not EXCEL.exists():
        sys.exit(f"No encuentro el Excel: {EXCEL}")
    df = pd.read_excel(EXCEL, sheet_name=0)
    faltan = [c for c in COLUMNAS_EXCEL if c not in df.columns]
    if faltan:
        sys.exit(f"Al Excel le faltan columnas: {faltan}. Tiene: {list(df.columns)}")
    # La categoría de la ficha sale del Excel (no se le pide a Gemini): solo dos valores válidos.
    invalidas = df.loc[~df["Categoría"].isin(CATEGORIAS), ["SKU", "Categoría"]]
    if not invalidas.empty:
        sys.exit(f"Categorías fuera de {sorted(CATEGORIAS)} en el Excel:\n"
                 f"{invalidas.head(10).to_string(index=False)}")
    return df


def skus_ya_listos() -> set[str]:
    """SKU que ya tienen ficha guardada (para no repetir trabajo)."""
    if not FICHAS.exists():
        return set()
    listos = set()
    with FICHAS.open(encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if linea:
                listos.add(json.loads(linea)["sku"])
    return listos


def construir_prompt(fila: dict) -> str:
    return (
        "Ficha del siguiente producto:\n"
        f"SKU: {fila['sku']}\n"
        f"Nombre: {fila['nombre']}\n"
        f"Marca (columna del Excel): {fila['marca_excel'] or '(vacía)'}\n"
        f"Categoría: {fila['categoria'] or '(vacía)'}\n"
        f"Precio normal: {fila['precio_normal']} CLP\n"
        f"Precio oferta: {fila['precio_oferta']} CLP\n"
    )


def pedir_ficha(cliente: genai.Client, modelo: str, fila: dict) -> Ficha:
    """Llama a Gemini con reintentos. Lanza la última excepción si no lo logra."""
    ultimo_error: Exception | None = None
    for intento in range(1, INTENTOS + 1):
        try:
            respuesta = cliente.models.generate_content(
                model=modelo,
                contents=construir_prompt(fila),
                config=types.GenerateContentConfig(
                    system_instruction=INSTRUCCIONES,
                    temperature=0,
                    response_mime_type="application/json",
                    response_schema=Ficha,
                ),
            )
            return Ficha.model_validate_json(respuesta.text)
        except errors.APIError as e:
            ultimo_error = e
            if e.code not in CODIGOS_REINTENTABLES:
                raise  # error de configuración (clave, modelo, petición): reintentar no ayuda
        except Exception as e:  # red caída, respuesta vacía o JSON inválido
            ultimo_error = e
        if intento < INTENTOS:
            espera = ESPERA_BASE * 2 ** (intento - 1)
            print(f"    intento {intento}/{INTENTOS} falló ({type(ultimo_error).__name__}); "
                  f"espero {espera}s…")
            time.sleep(espera)
    raise ultimo_error  # type: ignore[misc]


def armar_ficha(fila: dict, g: Ficha) -> dict:
    """Une los datos originales de la fila con lo que extrajo Gemini."""
    marca = (g.marca or "").strip() or "Sin marca"
    copia_linea, copia_marca = g.copia_linea, g.copia_marca

    if g.es_replica:
        # Una réplica nunca lleva la marca del modelo famoso que imita.
        if copia_marca and marca.lower() == copia_marca.lower():
            marca = fila["marca_excel"] if fila["marca_excel"] and \
                fila["marca_excel"].lower() != copia_marca.lower() else "Sin marca"
    else:
        copia_linea = copia_marca = None

    return {
        "sku": fila["sku"],
        "nombre": fila["nombre"],
        "precio_normal": fila["precio_normal"],
        "precio_oferta": fila["precio_oferta"],
        "categoria": fila["categoria"],  # viene del Excel, no de Gemini
        "marca": marca,
        "linea": g.linea,
        "es_replica": g.es_replica,
        "copia_linea": copia_linea,
        "copia_marca": copia_marca,
        "almacenamiento_gb": g.almacenamiento_gb,
        "ram_gb": g.ram_gb,
        "pantalla_pulgadas": g.pantalla_pulgadas,
        "sistema": g.sistema,
    }


def mensaje_error(e: Exception) -> str:
    return f"{type(e).__name__}: {str(e)[:300]}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrae fichas de productos con Gemini.")
    parser.add_argument("--limit", type=int, default=None,
                        help="procesar solo las primeras N filas que falten (para probar)")
    args = parser.parse_args()

    load_dotenv(BASE / ".env")
    api_key = os.getenv("GOOGLE_API_KEY")
    modelo = os.getenv("MODELO")
    if not api_key or not modelo:
        sys.exit("Faltan GOOGLE_API_KEY y/o MODELO en el archivo .env (ver .env.example).")

    cliente = genai.Client(api_key=api_key)
    df = cargar_excel()
    listos = skus_ya_listos()

    filas = []
    for _, r in df.iterrows():
        sku = texto_o_none(r["SKU"])
        if sku is None or sku in listos:
            continue
        filas.append({
            "sku": sku,
            "nombre": texto_o_none(r["Nombre"]) or "",
            "marca_excel": texto_o_none(r["Marca"]),
            "categoria": texto_o_none(r["Categoría"]),
            "precio_normal": entero_o_none(r["Precio normal"]),
            "precio_oferta": entero_o_none(r["Precio oferta"]),
        })
    if args.limit is not None:
        filas = filas[: args.limit]

    print(f"Modelo: {modelo} | Excel: {len(df)} filas | ya listas: {len(listos)} | "
          f"por procesar ahora: {len(filas)}")

    pendientes: list[dict] = []
    fallos_seguidos = 0
    cortado = False
    intentadas = 0

    with FICHAS.open("a", encoding="utf-8") as salida:
        for i, fila in enumerate(filas, start=1):
            intentadas = i
            try:
                g = pedir_ficha(cliente, modelo, fila)
            except Exception as e:
                pendientes.append({"sku": fila["sku"], "nombre": fila["nombre"],
                                   "error": mensaje_error(e)})
                fallos_seguidos += 1
                print(f"[{i}/{len(filas)}] {fila['sku']}: PENDIENTE ({mensaje_error(e)})")
                if fallos_seguidos >= FALLOS_SEGUIDOS_MAX:
                    print(f"\n{FALLOS_SEGUIDOS_MAX} filas seguidas fallaron: corto la corrida. "
                          "Revisa la clave, el modelo o el límite de uso y vuelve a correrlo; "
                          "retoma donde quedó.")
                    cortado = True
                    break
                continue

            fallos_seguidos = 0
            ficha = armar_ficha(fila, g)
            salida.write(json.dumps(ficha, ensure_ascii=False) + "\n")
            salida.flush()  # guardado fila a fila: si se corta, no se pierde nada
            marca_replica = f" RÉPLICA de {ficha['copia_marca']} {ficha['copia_linea']}" \
                if ficha["es_replica"] else ""
            print(f"[{i}/{len(filas)}] {fila['sku']}: {ficha['marca']} / "
                  f"{ficha['linea']}{marca_replica}")

    # Resumen sobre el total acumulado en data/fichas.jsonl
    total_fichas = replicas = 0
    with FICHAS.open(encoding="utf-8") as f:
        for linea in f:
            if linea.strip():
                total_fichas += 1
                replicas += json.loads(linea)["es_replica"]

    # Si se cortó la corrida, las filas que no alcanzaron a intentarse también quedan pendientes.
    if cortado:
        for f in filas[intentadas:]:
            pendientes.append({"sku": f["sku"], "nombre": f["nombre"],
                               "error": "no intentada (corrida cortada)"})

    if pendientes:
        PENDIENTES.write_text(json.dumps(pendientes, ensure_ascii=False, indent=2), encoding="utf-8")
    elif PENDIENTES.exists():
        PENDIENTES.unlink()  # ya no queda nada pendiente

    print("\n===== RESUMEN =====")
    print(f"Fichas listas (acumuladas): {total_fichas}")
    print(f"  de las cuales réplicas:   {replicas}")
    print(f"Pendientes:                 {len(pendientes)}"
          + (f"  (detalle en {PENDIENTES.relative_to(BASE)})" if pendientes else ""))
    print(f"Archivo de resultados:      {FICHAS.relative_to(BASE)}")


if __name__ == "__main__":
    main()
