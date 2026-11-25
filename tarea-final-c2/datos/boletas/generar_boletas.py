"""Genera 4 boletas FICTICIAS como imagen PNG y el JSON con lo declarado en cada rendición.

Todo es inventado: emisores, RUT (11.111.111-1, 22.222.222-2, 33.333.333-3, de ejemplo),
folios y montos. Cada imagen dice «DOCUMENTO DE PRUEBA» en grande.

    boleta-01-cuadra.png           todo coincide con lo declarado
    boleta-02-monto-distinto.png   la boleta dice $62.000; se declaró $52.000
    boleta-03-fecha-distinta.png   la boleta es del 12-09-2026; se declaró 2026-10-12
    boleta-04-ilegible.png         borrosa y con ruido: no se puede leer

Uso (desde tarea-final-c2/):  pip install Pillow && python datos/boletas/generar_boletas.py
Pillow solo hace falta para volver a generarlas; las imágenes ya están en el repo.
"""

import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

CARPETA = Path(__file__).resolve().parent
ANCHO, ALTO = 720, 960
ROJO, NEGRO, GRIS = (200, 30, 30), (20, 20, 20), (110, 110, 110)

BOLETAS = [
    {
        "archivo": "boleta-01-cuadra.png",
        "caso": "cuadra",
        "emisor": "Estación de Servicio El Roble (ficticia)",
        "rut": "11.111.111-1", "folio": "000123", "fecha_impresa": "02-10-2026",
        "items": [("Gasolina 95 octanos  32,1 L", 45000)], "total": 45000,
        "declarado": {"monto": 45000, "fecha": "2026-10-02", "rut_emisor": "11.111.111-1", "folio": "000123",
                      "categoria": "Gasolina (vehículo propio)"},
        "esperado_cuadra": {"monto": "sí", "fecha": "sí", "rut_emisor": "sí", "folio": "sí", "categoria": "sí"},
    },
    {
        "archivo": "boleta-02-monto-distinto.png",
        "caso": "monto distinto",
        "emisor": "Hotel Vista Lago (ficticio)",
        "rut": "22.222.222-2", "folio": "004512", "fecha_impresa": "14-10-2026",
        "items": [("Habitación single, 1 noche", 52000), ("Cena", 10000)], "total": 62000,
        "declarado": {"monto": 52000, "fecha": "2026-10-14", "rut_emisor": "22.222.222-2", "folio": "004512",
                      "categoria": "Hotel"},
        "esperado_cuadra": {"monto": "no", "fecha": "sí", "rut_emisor": "sí", "folio": "sí", "categoria": "sí"},
    },
    {
        "archivo": "boleta-03-fecha-distinta.png",
        "caso": "fecha distinta",
        "emisor": "Autopista Ruta Sur (ficticia)",
        "rut": "33.333.333-3", "folio": "078901", "fecha_impresa": "12-09-2026",
        "items": [("Peaje troncal Puerto Montt", 9800)], "total": 9800,
        "declarado": {"monto": 9800, "fecha": "2026-10-12", "rut_emisor": "33.333.333-3", "folio": "078901",
                      "categoria": "Peajes"},
        "esperado_cuadra": {"monto": "sí", "fecha": "no", "rut_emisor": "sí", "folio": "sí", "categoria": "sí"},
    },
    {
        "archivo": "boleta-04-ilegible.png",
        "caso": "ilegible",
        "emisor": "Ferretería Los Coihues (ficticia)",
        "rut": "11.111.111-1", "folio": "000456", "fecha_impresa": "20-10-2026",
        "items": [("Ampolletas LED x4", 15990)], "total": 15990,
        "declarado": {"monto": 15990, "fecha": "2026-10-20", "rut_emisor": "11.111.111-1", "folio": "000456",
                      "categoria": "Materiales de mantención"},
        "esperado_cuadra": {"monto": "no", "fecha": "no", "rut_emisor": "no", "folio": "no", "categoria": "no"},
        "ilegible": True,
    },
]


def fuente(tamano: int, negrita: bool = False):
    nombre = "DejaVuSans-Bold.ttf" if negrita else "DejaVuSans.ttf"
    for carpeta in ("/usr/share/fonts/truetype/dejavu", "/Library/Fonts", "C:/Windows/Fonts"):
        ruta = Path(carpeta) / nombre
        if ruta.exists():
            return ImageFont.truetype(str(ruta), tamano)
    return ImageFont.load_default(size=tamano)


def clp(monto: int) -> str:
    return "$" + f"{monto:,}".replace(",", ".")


def dibujar(boleta: dict) -> Image.Image:
    imagen = Image.new("RGB", (ANCHO, ALTO), "white")
    d = ImageDraw.Draw(imagen)
    d.rectangle([20, 20, ANCHO - 20, 130], outline=ROJO, width=5)
    d.text((ANCHO // 2, 52), "DOCUMENTO DE PRUEBA", font=fuente(46, True), fill=ROJO, anchor="mm")
    d.text((ANCHO // 2, 102), "Ficticio · sin validez tributaria", font=fuente(22), fill=ROJO, anchor="mm")
    y = 170
    for texto, tam, negrita in (
        (boleta["emisor"], 28, True), (f"RUT: {boleta['rut']}", 26, False),
        (f"BOLETA ELECTRÓNICA N° {boleta['folio']}", 28, True), (f"Fecha de emisión: {boleta['fecha_impresa']}", 26, False),
    ):
        d.text((50, y), texto, font=fuente(tam, negrita), fill=NEGRO)
        y += 50
    d.line([50, y, ANCHO - 50, y], fill=GRIS, width=2)
    y += 25
    for descripcion, monto in boleta["items"]:
        d.text((50, y), descripcion, font=fuente(24), fill=NEGRO)
        d.text((ANCHO - 50, y), clp(monto), font=fuente(24), fill=NEGRO, anchor="ra")
        y += 45
    d.line([50, y, ANCHO - 50, y], fill=GRIS, width=2)
    y += 25
    d.text((50, y), "TOTAL", font=fuente(34, True), fill=NEGRO)
    d.text((ANCHO - 50, y), clp(boleta["total"]), font=fuente(34, True), fill=NEGRO, anchor="ra")
    d.text((ANCHO // 2, ALTO - 60), "Comercial Los Alerces SpA · datos inventados", font=fuente(20), fill=GRIS, anchor="mm")
    if boleta.get("ilegible"):
        # Se mantiene visible el aviso de prueba; el resto queda irrecuperable.
        cuerpo = imagen.crop((0, 140, ANCHO, ALTO)).resize((ANCHO // 12, (ALTO - 140) // 12)).resize((ANCHO, ALTO - 140))
        cuerpo = cuerpo.filter(ImageFilter.GaussianBlur(9))
        azar = random.Random(4)
        ruido = ImageDraw.Draw(cuerpo)
        for _ in range(9000):
            x, yy = azar.randrange(ANCHO), azar.randrange(ALTO - 140)
            ruido.point((x, yy), fill=(azar.randrange(256),) * 3)
        imagen.paste(cuerpo, (0, 140))
    return imagen


def main() -> None:
    declarado = []
    for boleta in BOLETAS:
        dibujar(boleta).save(CARPETA / boleta["archivo"], optimize=True)
        declarado.append({
            "archivo": boleta["archivo"], "mime_type": "image/png", "caso": boleta["caso"],
            "declarado": boleta["declarado"], "esperado_cuadra": boleta["esperado_cuadra"],
        })
        print("generada", boleta["archivo"])
    (CARPETA / "declarado.json").write_text(
        json.dumps({"descripcion": "Boletas FICTICIAS para el verificador A2A. Todo es inventado.",
                    "boletas": declarado}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("escrito declarado.json")


if __name__ == "__main__":
    main()
