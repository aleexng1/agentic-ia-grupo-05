"""Captura la evidencia de delegación A2A: encargo → verificador → respuesta, con el log de ambos lados.

Uso (desde tarea-final-c2/, con .env completo):
    uvicorn src.verificador.app:app --port 8001 2>&1 | tee /tmp/verificador.log    # terminal 1
    python evidencias/a2a/capturar.py --log-verificador /tmp/verificador.log         # terminal 2

Este script hace de lado principal: llama a delegar_verificador (la misma función que usa el
grafo) con cada boleta ficticia de datos/boletas/ y escribe un .md por boleta con:
- el encargo: de la imagen solo tipo, tamaño y SHA-256 (nunca la imagen), y lo declarado;
- la respuesta del verificador tal cual la entrega delegar_verificador;
- el log del principal (este proceso) y el del verificador (líneas con el hash de esa imagen).
No escribe claves: las cabeceras no se registran y todo pasa por ocultar_secretos.
"""

import argparse
import asyncio
import base64
import hashlib
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
PROYECTO = CARPETA.parents[1]
sys.path.insert(0, str(PROYECTO))

from src.comun import config  # noqa: E402  (carga el .env)
from src.comun.errores import ocultar_secretos  # noqa: E402
from src.comun.registro import configurar_registro  # noqa: E402
from src.principal.herramientas.delegar_verificador import delegar_verificador  # noqa: E402

BOLETAS = PROYECTO / "datos" / "boletas"


class Captura(logging.Handler):
    def __init__(self):
        super().__init__()
        self.lineas: list[str] = []

    def emit(self, registro):
        self.lineas.append(self.format(registro))


def log_del_verificador(ruta: str | None, huella: str) -> list[str]:
    """Líneas del verificador de este encargo: la del encargo (trae el hash) y la de su respuesta."""
    if not ruta:
        return ["(no se pasó --log-verificador)"]
    time.sleep(0.5)
    try:
        lineas = Path(ruta).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as error:
        return [f"(no se pudo leer el log: {error})"]
    elegidas = []
    for i, linea in enumerate(lineas):
        if f"sha256:{huella}" in linea:
            elegidas.append(linea)
            contexto = linea.split("encargo ", 1)[1].split(" ", 1)[0] if "encargo " in linea else None
            elegidas += [l for l in lineas[i + 1 :] if contexto and f"respuesta {contexto}" in l][:1]
            elegidas += [l for l in lineas[i + 1 : i + 6] if "ERROR" in l or "error" in l.lower()][:2]
    return [ocultar_secretos(l) for l in elegidas] or ["(no hubo líneas con el hash de esta imagen)"]


async def capturar(boleta: dict, opciones, captura: Captura, prefijo: str) -> Path:
    datos = (BOLETAS / boleta["archivo"]).read_bytes()
    huella = hashlib.sha256(datos).hexdigest()[:16]
    imagen = {"mime_type": boleta["mime_type"], "datos_base64": base64.b64encode(datos).decode("ascii")}
    captura.lineas.clear()
    inicio = time.monotonic()
    respuesta = await delegar_verificador(imagen, boleta["declarado"])
    duracion = int((time.monotonic() - inicio) * 1000)
    encargo = {
        "imagen": {"archivo": boleta["archivo"], "mime_type": boleta["mime_type"], "bytes": len(datos), "sha256_inicio": huella},
        "datos": {"tarea": "verificar_boleta", "declarado": boleta["declarado"]},
    }
    md = [
        f"# A2A · {boleta['archivo']} ({boleta['caso']})",
        "",
        f"Capturado el {datetime.now().astimezone().isoformat(timespec='seconds')} · verificador en "
        f"`{config.url_verificador()}` · tiempo límite {config.timeout_a2a_seg():g} s · duración {duracion} ms.",
        "",
        "## Encargo (principal → verificador)",
        "Parte de archivo (la imagen; aquí solo tipo, tamaño y hash) + parte de datos (lo declarado):",
        "```json",
        json.dumps(encargo, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Respuesta del verificador (lo que recibe el principal)",
        "```json",
        ocultar_secretos(json.dumps(respuesta, ensure_ascii=False, indent=2)),
        "```",
        "",
        f"Esperado según `datos/boletas/declarado.json`: `{json.dumps(boleta['esperado_cuadra'], ensure_ascii=False)}`",
        "",
        "## Dónde se usa",
        "En el nodo `revisar_gasto` del grafo principal: el resultado se pasa al ReAct como dato y, si algún "
        "campo no cuadra o el verificador no respondió, un «aprobar» baja a «observar» (`aplicar_verificacion`).",
        "",
        "## Log del principal (este proceso)",
        "```text",
        *[ocultar_secretos(l) for l in captura.lineas],
        "```",
        "",
        "## Log del verificador",
        "```text",
        *log_del_verificador(opciones.log_verificador, huella),
        "```",
        "",
    ]
    destino = Path(opciones.salida) / f"{prefijo}{boleta['archivo'].replace('.png', '')}.md"
    destino.write_text("\n".join(md), encoding="utf-8")
    return destino


async def principal(opciones) -> int:
    registro = configurar_registro()
    captura = Captura()
    captura.setFormatter(logging.Formatter("%(asctime)s %(levelname)-7s [%(name)s] %(message)s", "%Y-%m-%d %H:%M:%S"))
    registro.addHandler(captura)
    boletas = json.loads((BOLETAS / "declarado.json").read_text(encoding="utf-8"))["boletas"]
    if opciones.solo:
        boletas = [b for b in boletas if opciones.solo in b["archivo"]]
    for boleta in boletas:
        destino = await capturar(boleta, opciones, captura, opciones.prefijo)
        print("escrito", destino)
    return 0


if __name__ == "__main__":
    argumentos = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argumentos.add_argument("--log-verificador", help="archivo con la salida de uvicorn del verificador")
    argumentos.add_argument("--salida", default=str(CARPETA))
    argumentos.add_argument("--solo", help="solo la boleta cuyo nombre contiene este texto")
    argumentos.add_argument("--prefijo", default="", help="prefijo del nombre de los .md")
    raise SystemExit(asyncio.run(principal(argumentos.parse_args())))
