"""Captura la evidencia de seguridad del canal A2A: el verificador exige el Bearer de TOKEN_A2A.

Uso (desde tarea-final-c2/, con .env completo):
    uvicorn src.verificador.app:app --port 8001 2>&1 | tee /tmp/verificador.log    # terminal 1
    python evidencias/a2a/capturar_token.py --log-verificador /tmp/verificador.log  # terminal 2

Prueba, contra el verificador levantado (URL_VERIFICADOR):
1. GET /health y la ficha: públicos (200).
2. POST del encargo sin token, con un token incorrecto, sin «Bearer» y con la X-API-Key del
   servicio (la protección provisoria anterior): todos rechazados (401), sin leer la boleta.
3. El encargo real con delegar_verificador (token correcto): responde.
Nunca escribe el token ni la clave: en el .md aparecen como «***» y todo pasa por ocultar_secretos.
"""

import argparse
import asyncio
import base64
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx

CARPETA = Path(__file__).resolve().parent
PROYECTO = CARPETA.parents[1]
sys.path.insert(0, str(PROYECTO))

from src.comun import config, seguridad  # noqa: E402  (carga el .env)
from src.comun.errores import ocultar_secretos  # noqa: E402
from src.principal.herramientas.delegar_verificador import delegar_verificador  # noqa: E402

BOLETA = PROYECTO / "datos" / "boletas" / "boleta-01-cuadra.png"
ENCARGO_MINIMO = {"jsonrpc": "2.0", "id": "evidencia-token", "method": "SendMessage", "params": {}}


def _intento(url: str, nombre: str, cabeceras: dict, mostradas: dict) -> list[str]:
    respuesta = httpx.post(url + "/", json=ENCARGO_MINIMO, headers=cabeceras, timeout=15)
    return [
        f"### {nombre}",
        f"Cabeceras enviadas: `{json.dumps(mostradas, ensure_ascii=False)}`",
        f"→ **HTTP {respuesta.status_code}** `{ocultar_secretos(respuesta.text)[:200]}`",
        "",
    ]


def _log_desde(ruta: str | None, desde: int) -> list[str]:
    if not ruta:
        return ["(no se pasó --log-verificador)"]
    time.sleep(0.5)
    with open(ruta, "rb") as archivo:
        archivo.seek(desde)
        lineas = archivo.read().decode("utf-8", errors="replace").splitlines()
    elegidas = [l for l in lineas if "[tarea_final]" in l or "POST / " in l or "GET /" in l]
    return [ocultar_secretos(l) for l in elegidas] or ["(sin líneas nuevas)"]


def main() -> int:
    argumentos = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argumentos.add_argument("--log-verificador", help="archivo con la salida de uvicorn del verificador")
    argumentos.add_argument("--salida", default=str(CARPETA / "seguridad-token-a2a.md"))
    opciones = argumentos.parse_args()

    token = seguridad.token_a2a_configurado()
    clave = seguridad.clave_configurada()
    if not token or not clave:
        print("Faltan TOKEN_A2A o API_KEY_SERVICIO en el .env.")
        return 1
    url = config.url_verificador()
    desde = Path(opciones.log_verificador).stat().st_size if opciones.log_verificador else 0

    md = [
        "# A2A · seguridad del canal: el verificador exige `Authorization: Bearer <TOKEN_A2A>`",
        "",
        f"Capturado el {datetime.now().astimezone().isoformat(timespec='seconds')} contra `{url}` con "
        "`evidencias/a2a/capturar_token.py`. El token y la clave se muestran como `***`.",
        "",
        "## 1. Lecturas públicas",
        f"- `GET /health` → HTTP {httpx.get(url + '/health', timeout=10).status_code}",
        f"- `GET /.well-known/agent-card.json` → HTTP {httpx.get(url + '/.well-known/agent-card.json', timeout=10).status_code}",
        "",
        "## 2. Encargos rechazados (no se ejecuta nada)",
        "",
        *_intento(url, "Sin token", {}, {}),
        *_intento(url, "Token incorrecto", {"Authorization": "Bearer token-equivocado"},
                  {"Authorization": "Bearer token-equivocado"}),
        *_intento(url, "Token correcto pero sin «Bearer»", {"Authorization": token}, {"Authorization": "***"}),
        *_intento(url, "Solo la X-API-Key del servicio (protección provisoria anterior)",
                  {seguridad.CABECERA: clave}, {seguridad.CABECERA: "***"}),
    ]

    imagen = {"mime_type": "image/png", "datos_base64": base64.b64encode(BOLETA.read_bytes()).decode("ascii")}
    declarado = {"monto": 45000, "fecha": "2026-10-02", "rut_emisor": "11.111.111-1", "folio": "000123",
                 "categoria": "Gasolina"}
    inicio = time.monotonic()
    respuesta = asyncio.run(delegar_verificador(imagen, declarado))
    duracion = int((time.monotonic() - inicio) * 1000)
    md += [
        "## 3. Encargo real con el token correcto (`delegar_verificador`, `boleta-01-cuadra.png`)",
        "Cabeceras enviadas: `{\"Authorization\": \"Bearer ***\"}` (la `X-API-Key` ya no sale del principal).",
        f"Duración: {duracion} ms.",
        "```json",
        ocultar_secretos(json.dumps(respuesta, ensure_ascii=False, indent=2)),
        "```",
        "",
        "## Log del verificador (estas peticiones)",
        "```text",
        *_log_desde(opciones.log_verificador, desde),
        "```",
        "",
    ]
    texto = "\n".join(md)
    if token in texto or clave in texto:  # última barrera: nunca escribir el token ni la clave
        print("La evidencia contenía el token o la clave: no se escribió.")
        return 1
    Path(opciones.salida).write_text(texto, encoding="utf-8")
    print(f"escrito {opciones.salida} · encargo real disponible={respuesta.get('disponible')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
