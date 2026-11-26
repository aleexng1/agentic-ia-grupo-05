"""Captura la evidencia A2A «uso del resultado»: la misma solicitud, con dos boletas, cambia el veredicto.

Dueño: Alex. Pauta, delegación A2A: además del encargo y la respuesta, mostrar **cómo se usa el
resultado** en la decisión del agente principal.

Qué hace (todo real: router, verificador, ReAct, juez y Postgres; nada guionado):
- Manda por /chat asíncrono (POST → 202 → GET /registro/{id}) la MISMA solicitud de revisar_gasto
  dos veces: mismo texto y mismo gasto (el de V-01 del golden set), con dos boletas distintas:
    a) boleta-01-cuadra.png         → se espera «aprobar»
    b) boleta-02-monto-distinto.png → se espera «observar»
  Lo único que cambia entre a) y b) es la imagen (y el thread_id, para no mezclar memoria).
- Por cada corrida guarda la solicitud (de la imagen solo archivo, tamaño y SHA-256), el id_ejecucion,
  el encargo A2A, la respuesta del verificador, la propuesta del ReAct, el juez, el piso por
  verificación de nodo_cerrar, el veredicto final, la fila del registro de veredictos (leída justo
  después de cada corrida: la tabla tiene una fila por id_gasto) y el log de los dos lados.

Uso (desde tarea-final-c2/, con el .venv activado y el mismo Postgres en DATABASE_URL para los tres
procesos; MOSTRAR_TRAZAS=1 en el principal para ver la propuesta del ReAct y el piso):
    PYTHONUNBUFFERED=1 uvicorn src.verificador.app:app --port 8001 2>&1 | tee /tmp/verificador.log
    PYTHONUNBUFFERED=1 MOSTRAR_TRAZAS=1 uvicorn api.app:app --port 8000 2>&1 | tee /tmp/principal.log
    python evidencias/a2a/capturar_uso.py --log-principal /tmp/principal.log --log-verificador /tmp/verificador.log

Requisito: Redis con el índice de políticas (REDIS_URL, REDIS_PREFIJO). Sin fragmentos de
buscar_politica el juez no valida ninguna aprobación, y a) termina en «observar» por el juez, no por
la boleta (corrida de prueba del 2026-11-25).

Gasta unas 15–20 llamadas a Gemini (2 corridas: router, verificador, ReAct y juez). Lee
API_KEY_SERVICIO del entorno o del .env y NUNCA la escribe: todo pasa por ocultar_secretos.
Escribe evidencias/a2a/05-uso-del-resultado-en-el-veredicto.md y termina con 0 si a) quedó
«aprobar» y b) «observar» (en /chat y en el registro), o 1 si no.
"""

import argparse
import base64
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx

CARPETA = Path(__file__).resolve().parent
PROYECTO = CARPETA.parents[1]
sys.path.insert(0, str(PROYECTO))
sys.path.insert(0, str(CARPETA))

from src.comun import config  # noqa: E402,F401  (carga el .env)
from src.comun.errores import ocultar_secretos  # noqa: E402

BOLETAS = PROYECTO / "datos" / "boletas"
CASO_GOLDEN = "V-01"
CORRIDAS = [
    ("a", "boleta-01-cuadra.png", "aprobar"),
    ("b", "boleta-02-monto-distinto.png", "observar"),
]
TRAZAS_DE_INTERES = ("juez", "piso_reglas", "piso_verificacion", "cerrar", "tiempo_agotado", "modelo_fallo")
_CABECERA_TRAZA = re.compile(r"^── \[([a-z_]+)\] ──$")


def solicitud_base() -> tuple[str, dict]:
    """Texto y gasto de V-01 del golden set (el gasto cumple la política: el ReAct lo aprobaría)."""
    golden = json.loads((PROYECTO / "evaluacion" / "golden_set.json").read_text(encoding="utf-8"))
    casos = golden["casos"] if isinstance(golden, dict) else golden
    turno = next(c for c in casos if c["id"] == CASO_GOLDEN)["turnos"][0]
    return turno["mensaje"], dict(turno["gasto"])


def redis_configurado() -> bool:
    """True si REDIS_URL tiene un valor propio (no vacío ni el host ficticio de .env.example)."""
    from urllib.parse import urlparse

    valor = os.getenv("REDIS_URL", "").strip()
    return bool(valor) and urlparse(valor).hostname not in (None, "host-de-ejemplo")


def extraer_trazas(lineas: list[str]) -> list[tuple[str, object]]:
    """Bloques de registrar_traza («── [evento] ──» + JSON) en el orden en que aparecen."""
    trazas, evento, buffer = [], None, []
    for linea in lineas:
        cabecera = _CABECERA_TRAZA.match(linea.strip())
        if cabecera:
            evento, buffer = cabecera.group(1), []
            continue
        if evento is None:
            continue
        buffer.append(linea)
        try:
            datos = json.loads("\n".join(buffer))
        except ValueError:
            continue
        trazas.append((evento, datos))
        evento, buffer = None, []
    return trazas


def propuesta_del_react(trazas: list[tuple[str, object]]) -> dict | None:
    """Los argumentos del último emitir_veredicto que pidió el modelo (antes del juez y los pisos)."""
    propuesta = None
    for evento, datos in trazas:
        if evento != "llm" or not isinstance(datos, dict):
            continue
        for llamada in datos.get("pide_herramientas") or []:
            if llamada.get("name") == "emitir_veredicto":
                propuesta = llamada.get("args")
    return propuesta


def donde_se_uso(verificacion: dict | None, propuesta: dict | None, trazas, respuesta: str) -> str:
    """Una línea clara: en qué punto el resultado del verificador decidió (o no cambió) el veredicto."""
    if not verificacion:
        return "No hubo verificación: el verificador no recibió la boleta."
    pisos = [datos for evento, datos in trazas if evento == "piso_verificacion"]
    no_cuadran = [c for c, v in (verificacion.get("cuadra") or {}).items() if v != "sí"]
    decision_propuesta = (propuesta or {}).get("decision")
    jueces = [datos for evento, datos in trazas if evento == "juez" and isinstance(datos, dict)]
    juez_bajo = decision_propuesta == "aprobar" and jueces and (
        not jueces[-1].get("valido") or not jueces[-1].get("evaluado", True))
    if pisos:
        return ("**El piso por verificación de `nodo_cerrar`** (`src/principal/flujos/revisar_gasto.py`, "
                "`motivo_piso_verificacion`) bajó la propuesta del ReAct de «aprobar» a «observar» **antes** de "
                f"`registrar_veredicto`, porque {pisos[-1].get('motivo')}.")
    if juez_bajo:
        return ("**El resultado NO fue lo que decidió:** el juez bajó «aprobar» a «observar» antes del piso por "
                f"verificación («{jueces[-1].get('razon')}»), así que el piso de `nodo_cerrar` recibió «observar» "
                "y no tuvo que actuar.")
    if "La decisión pasa de" in (respuesta or ""):
        return ("El piso del grafo principal (`aplicar_verificacion` en `src/principal/grafo.py`) bajó la "
                "decisión a «observar» después del ReAct.")
    if not no_cuadran and verificacion.get("disponible"):
        return ("Todos los campos cuadran: **el piso por verificación de `nodo_cerrar`** revisó el resultado y no "
                f"cambió nada, así que se registra la propuesta del ReAct («{decision_propuesta}»).")
    if decision_propuesta and decision_propuesta != "aprobar":
        return (f"El ReAct leyó el resultado (va como dato en su mensaje) y ya propuso «{decision_propuesta}»; el piso "
                "por verificación de `nodo_cerrar` no tuvo que actuar (solo baja aprobaciones).")
    return "No se encontró en la traza dónde se aplicó el resultado (revisar el log de abajo)."


def esperar_registro(url: str, clave: str, id_ejecucion: str, tope: float = 150.0) -> dict:
    fin = time.monotonic() + tope
    while True:
        datos = httpx.get(f"{url}/registro/{id_ejecucion}", headers={"X-API-Key": clave}, timeout=30).json()
        if datos.get("estado") != "en_proceso" or time.monotonic() > fin:
            return datos
        time.sleep(1)


def leer_desde(ruta: str | None, desde: int) -> list[str]:
    if not ruta:
        return []
    time.sleep(0.5)  # deja que uvicorn termine de escribir
    try:
        with open(ruta, "rb") as archivo:
            archivo.seek(desde)
            return archivo.read().decode("utf-8", errors="replace").splitlines()
    except OSError:
        return []


def _json(datos) -> str:
    return ocultar_secretos(json.dumps(datos, ensure_ascii=False, indent=2, default=str))


def correr(letra: str, archivo: str, esperado: str, texto: str, gasto: dict, opciones, clave: str) -> dict:
    from capturar import largo_del_log, log_del_verificador  # mismo lector de log que las boletas 01–04

    from src.principal import registro_veredictos
    from src.principal.grafo import declarado_para_verificador

    datos = (BOLETAS / archivo).read_bytes()
    huella = hashlib.sha256(datos).hexdigest()
    desde_principal = largo_del_log(opciones.log_principal)
    desde_verificador = largo_del_log(opciones.log_verificador)
    cuerpo = {
        "thread_id": f"evidencia-a2a-uso-{letra}-{datetime.now():%Y%m%dT%H%M%S}",
        "texto": texto,
        "gasto": gasto,
        "imagen": {"mime_type": "image/png", "datos_base64": base64.b64encode(datos).decode("ascii")},
    }
    inicio = time.monotonic()
    aceptado = httpx.post(f"{opciones.url}/chat", json=cuerpo, headers={"X-API-Key": clave}, timeout=60)
    if aceptado.status_code != 202:
        raise SystemExit(f"/chat respondió HTTP {aceptado.status_code}: {ocultar_secretos(aceptado.text)}")
    id_ejecucion = aceptado.json()["id_ejecucion"]
    final = esperar_registro(opciones.url, clave, id_ejecucion)
    segundos = round(time.monotonic() - inicio, 1)
    resultado = final.get("resultado") or {}
    fila_ejecucion = {k: v for k, v in final.items() if k != "resultado"}
    fila_veredicto = next((f for f in registro_veredictos.leer_registro() if f.get("id_gasto") == gasto["id"]), None)

    lineas = [ocultar_secretos(linea) for linea in leer_desde(opciones.log_principal, desde_principal)]
    trazas = extraer_trazas(lineas)
    verificacion = resultado.get("verificacion")
    propuesta = propuesta_del_react(trazas)
    veredicto = resultado.get("veredicto") or {}
    return {
        "letra": letra, "archivo": archivo, "esperado": esperado, "bytes": len(datos), "sha256": huella,
        "cuerpo_visible": {**{k: v for k, v in cuerpo.items() if k != "imagen"},
                           "imagen": {"archivo": archivo, "mime_type": "image/png", "bytes": len(datos),
                                      "sha256": huella, "datos_base64": "(omitido)"}},
        "aceptado": aceptado.json(), "id_ejecucion": id_ejecucion, "segundos": segundos,
        "encargo": {"imagen": {"archivo": archivo, "mime_type": "image/png", "bytes": len(datos),
                               "sha256_inicio": huella[:16]},
                    "datos": {"tarea": "verificar_boleta", "declarado": declarado_para_verificador(gasto)}},
        "verificacion": verificacion, "propuesta": propuesta, "resultado": resultado,
        "fila_ejecucion": fila_ejecucion, "fila_veredicto": fila_veredicto, "veredicto": veredicto,
        "trazas": [(e, d) for e, d in trazas if e in TRAZAS_DE_INTERES],
        "log_principal": [l for l in lineas if id_ejecucion in l or l.split("[tarea_final] ")[-1].startswith("a2a ·")],
        "log_verificador": log_del_verificador(opciones.log_verificador, huella[:16], desde_verificador),
        "donde": donde_se_uso(verificacion, propuesta, trazas, resultado.get("respuesta", "")),
    }


def seccion(c: dict, url: str) -> list[str]:
    v = c["verificacion"] or {}
    md = [
        f"## Corrida {c['letra']}) `{c['archivo']}` (se espera «{c['esperado']}»)",
        "",
        f"`id_ejecucion = {c['id_ejecucion']}` · {c['segundos']} s desde el POST hasta el resultado.",
        "",
        "### Solicitud",
        "```bash",
        f"curl -s -X POST {url}/chat -H 'Content-Type: application/json' -H 'X-API-Key: ***' -d @solicitud.json",
        "```",
        "`solicitud.json` (de la imagen, solo el archivo y su hash; el base64 no se copia):",
        "```json",
        _json(c["cuerpo_visible"]),
        "```",
        "Respuesta inmediata (HTTP 202):",
        "```json",
        _json(c["aceptado"]),
        "```",
        "",
        "### Encargo A2A (principal → verificador)",
        "Parte de archivo (la imagen: tipo, tamaño y hash) + parte de datos (lo declarado, `declarado_para_verificador`):",
        "```json",
        _json(c["encargo"]),
        "```",
        "",
        "### Respuesta del verificador",
        "| Campo | Declarado | Leído en la boleta | ¿Cuadra? |",
        "|---|---|---|---|",
        *[f"| {campo} | {c['encargo']['datos']['declarado'].get(campo)} | {(v.get('leido') or {}).get(campo)} | "
          f"{(v.get('cuadra') or {}).get(campo)} |" for campo in ("monto", "fecha", "rut_emisor", "folio", "categoria")],
        "",
        f"Confianza: **{v.get('confianza')}** · disponible: {v.get('disponible')} · observaciones: «{v.get('observaciones')}»",
        "```json",
        _json(v),
        "```",
        "",
        "### Cómo se usó el resultado",
        f"- Propuesta del ReAct (`emitir_veredicto`, antes del juez y de los pisos): "
        f"**{(c['propuesta'] or {}).get('decision', '(no encontrada en la traza)')}**",
        f"- Veredicto final en `/chat`: **{c['veredicto'].get('decision')}** · `estado_final = {c['resultado'].get('estado_final')}`",
        f"- Fila del registro de veredictos: **{(c['fila_veredicto'] or {}).get('decision')}**",
        "",
        f"**Dónde se usó:** {c['donde']}",
        "",
        "Trazas del ReAct (`MOSTRAR_TRAZAS=1`: juez, pisos y cierre):",
        "```text",
        *([f"── [{e}] ──\n{_json(d)}" for e, d in c["trazas"]] or ["(sin trazas: ¿MOSTRAR_TRAZAS=1 en el principal?)"]),
        "```",
        "",
        "### Resultado",
        f"`GET /registro/{c['id_ejecucion']}` → `resultado` (lo que entrega `/chat`):",
        "```json",
        _json(c["resultado"]),
        "```",
        "El resto de `GET /registro/{id}` (estado y fila de `ejecuciones`):",
        "```json",
        _json(c["fila_ejecucion"]),
        "```",
        f"Fila del registro de veredictos (`veredictos`, Postgres), leída justo después de esta corrida:",
        "```json",
        _json(c["fila_veredicto"]),
        "```",
        "",
        "### Log del principal (este id_ejecucion y el canal A2A)",
        "```text",
        *(c["log_principal"] or ["(no se pasó --log-principal)"]),
        "```",
        "### Log del verificador (este encargo, por el hash de la imagen)",
        "```text",
        *c["log_verificador"],
        "```",
        "",
    ]
    return md


def main() -> int:
    argumentos = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argumentos.add_argument("--url", default="http://127.0.0.1:8000")
    argumentos.add_argument("--log-principal", help="salida de uvicorn del principal (con MOSTRAR_TRAZAS=1)")
    argumentos.add_argument("--log-verificador", help="salida de uvicorn del verificador")
    argumentos.add_argument("--salida", default=str(CARPETA / "05-uso-del-resultado-en-el-veredicto.md"))
    argumentos.add_argument("--sin-redis", action="store_true", help="correr aunque no haya Redis (diagnóstico)")
    opciones = argumentos.parse_args()

    clave = os.getenv("API_KEY_SERVICIO", "").strip()
    if not clave:
        print("Falta API_KEY_SERVICIO en el entorno o en el .env.")
        return 1
    if not os.getenv("DATABASE_URL", "").strip():
        print("Falta DATABASE_URL: el registro de veredictos se lee de Postgres (el mismo que usa el principal).")
        return 1

    if not redis_configurado() and not opciones.sin_redis:
        print("Falta Redis (REDIS_URL vacía o con el valor de ejemplo): sin fragmentos de política el juez no valida "
              "ninguna aprobación y a) no puede terminar en «aprobar». No se gasta Gemini. "
              "Usa --sin-redis para correrlo igual (diagnóstico).")
        return 1

    texto, gasto = solicitud_base()
    corridas = []
    for letra, archivo, esperado in CORRIDAS:
        corridas.append(correr(letra, archivo, esperado, texto, gasto, opciones, clave))
        c = corridas[-1]
        print(f"{letra}) {archivo}: id_ejecucion={c['id_ejecucion']} · veredicto={c['veredicto'].get('decision')} · "
              f"registro={(c['fila_veredicto'] or {}).get('decision')} · {c['segundos']} s")

    def cumple(c):
        piso = any(e == "piso_verificacion" for e, _ in c["trazas"])
        return (c["veredicto"].get("decision") == c["esperado"]
                and (c["fila_veredicto"] or {}).get("decision") == c["esperado"] and c["resultado"].get("hubo_a2a")
                # b) solo demuestra el uso del resultado si fue el piso por verificación el que bajó a «observar»
                and (piso if c["esperado"] == "observar" else not piso))

    todo = all(cumple(c) for c in corridas)
    md = [
        "# A2A · uso del resultado del verificador en el veredicto",
        "",
        f"Capturado el {datetime.now().astimezone().isoformat(timespec='seconds')} contra `{opciones.url}` "
        "(principal) y el verificador A2A en local, con `evidencias/a2a/capturar_uso.py`, Postgres real y Gemini "
        "real (nada guionado).",
        "",
        f"**La misma solicitud dos veces:** mismo texto y mismo gasto (el de `{CASO_GOLDEN}` del golden set, "
        "que cumple la política). Solo cambia la boleta adjunta (y el `thread_id`, para no mezclar memoria). "
        "El registro de veredictos tiene una fila por `id_gasto`, así que se lee justo después de cada corrida.",
        "",
        *[linea for c in corridas for linea in seccion(c, opciones.url)],
        "## Comparación",
        "",
        "| | a) | b) |",
        "|---|---|---|",
        "| Boleta | " + " | ".join(f"`{c['archivo']}` (`{c['sha256'][:16]}…`)" for c in corridas) + " |",
        "| `id_ejecucion` | " + " | ".join(f"`{c['id_ejecucion']}`" for c in corridas) + " |",
        "| Datos declarados | " + " | ".join("iguales (V-01)" for _ in corridas) + " |",
        "| Campos que no cuadran | " + " | ".join(
            ", ".join(k for k, v in ((c["verificacion"] or {}).get("cuadra") or {}).items() if v != "sí") or "ninguno"
            for c in corridas) + " |",
        "| Confianza del verificador | " + " | ".join(str((c["verificacion"] or {}).get("confianza")) for c in corridas) + " |",
        "| Propuesta del ReAct | " + " | ".join(str((c["propuesta"] or {}).get("decision")) for c in corridas) + " |",
        "| Juez | " + " | ".join(
            next((("valida" if d.get("valido") else "no valida") + ("" if d.get("evaluado", True) else " (sin respuesta)")
                  for e, d in reversed(c["trazas"]) if e == "juez" and isinstance(d, dict)), "—")
            for c in corridas) + " |",
        "| Piso por verificación (`nodo_cerrar`) | " + " | ".join(
            "bajó a «observar»" if any(e == "piso_verificacion" for e, _ in c["trazas"]) else "no cambió nada"
            for c in corridas) + " |",
        "| Veredicto en `/chat` | " + " | ".join(f"**{c['veredicto'].get('decision')}**" for c in corridas) + " |",
        "| Registro de veredictos | " + " | ".join(str((c["fila_veredicto"] or {}).get("decision")) for c in corridas) + " |",
        "| `estado_final` | " + " | ".join(str(c["resultado"].get("estado_final")) for c in corridas) + " |",
        "| Esperado | " + " | ".join(c["esperado"] for c in corridas) + " |",
        "",
        ("**Cumple:** con los mismos datos declarados, la boleta que cuadra termina en «aprobar» y la que no cuadra en "
         "«observar», en `/chat` y en el registro." if todo else
         "**NO cumple:** alguna corrida no terminó con el veredicto esperado (ver las secciones de arriba)."),
        "",
    ]
    Path(opciones.salida).write_text("\n".join(md), encoding="utf-8")
    print(f"{opciones.salida} → {'CUMPLE' if todo else 'NO CUMPLE'}")
    return 0 if todo else 1


if __name__ == "__main__":
    raise SystemExit(main())
