"""Captura la evidencia «dos recorridos»: solicitudes distintas activan flujos distintos.

Uso (desde tarea-final-c2/, con el principal corriendo y su salida guardada en un archivo):
    uvicorn api.app:app --port 8000 2>&1 | tee /tmp/principal.log      # otra terminal
    python evidencias/dos-recorridos/capturar.py --url http://127.0.0.1:8000 --log /tmp/principal.log

Lee la clave de API_KEY_SERVICIO (del entorno o del .env) y NUNCA la escribe: en los .md
aparece como «***». Por cada caso escribe un .md con la entrada, la ejecución observada (las
líneas del log con su id_ejecucion) y el resultado.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx

CARPETA = Path(__file__).resolve().parent
sys.path.insert(0, str(CARPETA.parents[1]))

from src.comun import config  # noqa: E402,F401  (carga el .env)
from src.comun.errores import ocultar_secretos  # noqa: E402

# La pauta pide consulta_politica y revisar_gasto; fuera_de_alcance se deja como tercer recorrido.
# El gasto de 03 es el de GS-01 (golden set de c1, ficticio): peaje de $7.800, esperado «aprobar».
GASTO_GS01 = {
    "id": "G-0101", "fecha_gasto": "2026-10-06", "fecha_rendicion": "2026-10-09", "monto": 7800,
    "tipo_documento": "boleta", "proveedor": "Concesionaria Vial Lago Verde",
    "glosa": "peaje ida y vuelta CD - tienda Norte, camión de reparto", "politica_declarada": "Viajes Internos",
    "categoria_declarada": "Peaje", "unidad_negocio": "CD", "patente": "RZPT41", "numero_ot": None,
    "vb_gerente_general": False, "id_fondo": "FR-001",
}
CASOS = [
    ("01-consulta-politica", "consulta_politica", "¿Cuál es el plazo máximo para rendir un gasto que hice en octubre?", None),
    ("02-fuera-de-alcance", "fuera_de_alcance", "Escríbeme un poema sobre el lago Llanquihue.", None),
    ("03-revisar-gasto", "revisar_gasto", "Revisa este gasto rendido.", GASTO_GS01),
]


def lineas_del_log(ruta_log: str | None, id_ejecucion: str) -> list[str]:
    if not ruta_log or not id_ejecucion:
        return []
    time.sleep(0.5)  # deja que uvicorn termine de escribir
    try:
        texto = Path(ruta_log).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return [ocultar_secretos(linea) for linea in texto.splitlines() if id_ejecucion in linea]


def main() -> int:
    argumentos = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argumentos.add_argument("--url", default="http://127.0.0.1:8000")
    argumentos.add_argument("--log", help="archivo con la salida de uvicorn del principal")
    argumentos.add_argument("--salida", default=str(CARPETA))
    argumentos.add_argument("--solo", help="solo el recorrido cuyo nombre contiene este texto (ej. 03)")
    opciones = argumentos.parse_args()

    clave = os.getenv("API_KEY_SERVICIO", "").strip()
    if not clave:
        print("Falta API_KEY_SERVICIO en el entorno o en el .env.")
        return 1
    rutas_obtenidas = []
    for nombre, esperada, texto, gasto in CASOS:
        if opciones.solo and opciones.solo not in nombre:
            continue
        cuerpo = {"thread_id": f"evidencia-{nombre}", "texto": texto}
        if gasto:
            cuerpo["gasto"] = gasto
        respuesta = httpx.post(f"{opciones.url}/chat", json=cuerpo, headers={"X-API-Key": clave}, timeout=120)
        try:
            datos = respuesta.json()
        except ValueError:
            datos = {"texto_crudo": respuesta.text}
        id_ejecucion = datos.get("id_ejecucion", "")
        rutas_obtenidas.append(datos.get("ruta"))
        log = lineas_del_log(opciones.log, id_ejecucion)
        md = [
            f"# Recorrido {nombre}: ruta esperada `{esperada}`",
            "",
            f"Capturado el {datetime.now().astimezone().isoformat(timespec='seconds')} contra `{opciones.url}`"
            f" con `evidencias/dos-recorridos/capturar.py`.",
            "",
            "## Entrada",
            "```bash",
            f"curl -s -X POST {opciones.url}/chat -H 'Content-Type: application/json' -H 'X-API-Key: ***' \\",
            f"  -d '{json.dumps(cuerpo, ensure_ascii=False)}'",
            "```",
            "",
            "## Ejecución observada (log del servidor con este id_ejecucion)",
            "```text",
            *(log or ["(no se pasó --log o no hubo líneas con este id)"]),
            "```",
            "",
            f"## Resultado (HTTP {respuesta.status_code})",
            "```json",
            ocultar_secretos(json.dumps(datos, ensure_ascii=False, indent=2)),
            "```",
            "",
            f"Ruta obtenida: `{datos.get('ruta')}` · estado_final: `{datos.get('estado_final')}`"
            f" · {'coincide' if datos.get('ruta') == esperada else 'NO coincide'} con la esperada.",
            "",
        ]
        destino = Path(opciones.salida) / f"{nombre}.md"
        destino.write_text("\n".join(md), encoding="utf-8")
        print(f"{destino}: HTTP {respuesta.status_code}, ruta={datos.get('ruta')}")
    distintas = len(set(rutas_obtenidas)) == len(rutas_obtenidas)
    print("Flujos distintos en cada recorrido:", "sí" if distintas else "NO")
    return 0 if distintas else 1


if __name__ == "__main__":
    raise SystemExit(main())
