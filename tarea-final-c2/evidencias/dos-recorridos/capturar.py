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
import re
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


def esperar_registro(url: str, clave: str, id_ejecucion: str, tope: float = 150.0) -> dict:
    """/chat es asíncrono (202): consulta GET /registro/{id} hasta que deje de estar en proceso."""
    fin = time.monotonic() + tope
    while True:
        datos = httpx.get(f"{url}/registro/{id_ejecucion}", headers={"X-API-Key": clave}, timeout=30).json()
        if datos.get("estado") != "en_proceso" or time.monotonic() > fin:
            return datos
        time.sleep(1)


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
        # Hilo nuevo en cada captura: con memoria persistente, un hilo repetido arrastra el turno anterior.
        cuerpo = {"thread_id": f"evidencia-{nombre}-{datetime.now():%Y%m%dT%H%M%S}", "texto": texto}
        if gasto:
            cuerpo["gasto"] = gasto
        respuesta = httpx.post(f"{opciones.url}/chat", json=cuerpo, headers={"X-API-Key": clave}, timeout=120)
        try:
            datos = respuesta.json()
        except ValueError:
            datos = {"texto_crudo": respuesta.text}
        aceptado = None
        exito = respuesta.status_code == 200
        if respuesta.status_code == 202:  # /chat asíncrono: el resultado se lee en GET /registro/{id}
            aceptado = datos
            final = esperar_registro(opciones.url, clave, aceptado["id_ejecucion"])
            datos = final.get("resultado") or {"estado": final.get("estado"), "detail": final.get("detail")}
            exito = bool(final.get("resultado"))
        id_ejecucion = (aceptado or datos).get("id_ejecucion", "")
        if not id_ejecucion and isinstance(datos.get("detail"), str):
            # En un 502 el id viene al final del mensaje: «… (id_ejecucion: <uuid>)».
            encontrado = re.search(r"id_ejecucion: ([0-9a-f-]{36})", datos["detail"])
            id_ejecucion = encontrado.group(1) if encontrado else ""
        rutas_obtenidas.append(datos.get("ruta"))
        log = lineas_del_log(opciones.log, id_ejecucion)
        registro_http = None
        if id_ejecucion:  # la ruta y el estado_final también tienen que verse en el registro
            registro_http = httpx.get(f"{opciones.url}/registro/{id_ejecucion}", headers={"X-API-Key": clave}, timeout=30)
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
            *(
                [f"Respuesta inmediata (HTTP 202, `/chat` asíncrono):", "```json",
                 json.dumps(aceptado, ensure_ascii=False, indent=2), "```", ""]
                if aceptado else []
            ),
            "## Ejecución observada (log del servidor con este id_ejecucion)",
            "```text",
            *(log or ["(no se pasó --log o no hubo líneas con este id)"]),
            "```",
            "",
            (f"## Resultado (`GET /registro/{id_ejecucion}` al terminar → `resultado`)" if aceptado
             else f"## Resultado (HTTP {respuesta.status_code})"),
            "```json",
            ocultar_secretos(json.dumps(datos, ensure_ascii=False, indent=2)),
            "```",
            "",
            *(
                [
                    f"## Registro (`GET /registro/{id_ejecucion}` con `X-API-Key: ***` → HTTP {registro_http.status_code})",
                    "```json",
                    ocultar_secretos(registro_http.text if registro_http.status_code != 200 else json.dumps(
                        {k: v for k, v in registro_http.json().items() if k != "resultado"}, ensure_ascii=False, indent=2)),
                    "```",
                    "",
                ]
                if registro_http is not None
                else []
            ),
            (
                f"Ruta obtenida: `{datos.get('ruta')}` · estado_final: `{datos.get('estado_final')}`"
                f" · {'coincide' if datos.get('ruta') == esperada else 'NO coincide'} con la esperada."
                if exito
                else f"La ejecución falló (estado `{datos.get('estado') or respuesta.status_code}`) con un mensaje claro y sin datos inventados;"
                " la ruta que eligió el router y su `estado_final` quedan en el log de arriba y en `ejecuciones`."
            ),
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
