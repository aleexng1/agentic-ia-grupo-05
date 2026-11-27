"""Captura la evidencia «dos recorridos»: solicitudes distintas activan flujos distintos.

Uso (desde tarea-final-c2/, con el principal corriendo y su salida guardada en un archivo):
    PYTHONUNBUFFERED=1 MOSTRAR_TRAZAS=1 uvicorn api.app:app --port 8000 2>&1 | tee /tmp/principal.log
    python evidencias/dos-recorridos/capturar.py --url http://127.0.0.1:8000 --log /tmp/principal.log

Lee la clave de API_KEY_SERVICIO (del entorno o del .env) y NUNCA la escribe: en los .md
aparece como «***». Por cada caso escribe un .md con la entrada, la ejecución observada (las
líneas del log con su id_ejecucion) y el resultado.

Traza del ReAct (revisar_gasto): los bloques de `registrar_traza` («── [evento] ──» + JSON) se
imprimen sin el id_ejecucion. Se asignan a la ejecución agrupando las líneas del log entre
«chat · <id> · aceptado» y «ejecución <id> · ruta=…», y solo si en esa ventana no empezó otra
ejecución. Además se comprueba que la traza calce con el registro (mismos pasos y herramientas).
PYTHONUNBUFFERED=1 hace falta para que los print() de la traza salgan en orden con el log.
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


# ---------------------------------------------------------------------------
# Traza del ReAct de esta ejecución
# ---------------------------------------------------------------------------

_CABECERA_TRAZA = re.compile(r"^── \[([a-z_]+)\] ──$")
_ACEPTADO = re.compile(r"chat · ([0-9a-f-]{36}) · aceptado")
_SONDEO = re.compile(r'"GET /registro/[0-9a-f-]{36} HTTP')
LARGO_RESULTADO = 700  # caracteres de cada resultado de herramienta en el paso a paso (completo más abajo)


def largo_del_log(ruta_log: str | None) -> int:
    """Bytes del log antes de mandar el caso: la ventana se busca solo desde ahí."""
    try:
        return Path(ruta_log).stat().st_size if ruta_log else 0
    except OSError:
        return 0


def leer_desde(ruta_log: str | None, desde: int) -> list[str]:
    if not ruta_log:
        return []
    time.sleep(0.5)  # deja que uvicorn termine de escribir
    try:
        with open(ruta_log, "rb") as archivo:
            archivo.seek(desde)
            return archivo.read().decode("utf-8", errors="replace").splitlines()
    except OSError:
        return []


def ventana_de_ejecucion(lineas: list[str], id_ejecucion: str) -> tuple[list[str], str | None]:
    """Las líneas entre el inicio y el fin de esta ejecución, o ([], motivo) si no se pueden atribuir.

    Inicio: «chat · <id> · aceptado en segundo plano». Fin: «ejecución <id> · ruta=…» (la escribe el
    grafo al registrar la fila). Si otra ejecución empezó dentro de la ventana, sus trazas podrían
    mezclarse con las de esta: entonces no se atribuye nada.
    """
    inicio = next((i for i, l in enumerate(lineas) if f"chat · {id_ejecucion} · aceptado" in l), None)
    fin = next((i for i, l in enumerate(lineas) if f"ejecución {id_ejecucion} · ruta=" in l), None)
    if inicio is None or fin is None or fin < inicio:
        return [], "no se encontró el inicio y el fin de la ejecución en el log"
    ventana = lineas[inicio : fin + 1]
    otras = {m.group(1) for l in ventana if (m := _ACEPTADO.search(l)) and m.group(1) != id_ejecucion}
    if otras:
        return [], f"otra ejecución empezó dentro de la ventana ({len(otras)}): la traza no se puede atribuir"
    return ventana, None


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


def herramientas_de_la_traza(trazas: list[tuple[str, object]]) -> list[str]:
    """Las herramientas que pidió el modelo, en orden y con repeticiones (como herramientas_usadas).

    Se cuentan los pedidos y no las observaciones: el ReAct imprime cada observación al empezar la
    vuelta siguiente del modelo, así que la de `emitir_veredicto` (la última) no sale en la traza.
    Si el turno terminó por `parada` o por un bloqueo, lo pedido en la última vuelta no se ejecutó.
    """
    eventos = {evento for evento, _ in trazas}
    vueltas = [d for e, d in trazas if e == "llm" and isinstance(d, dict)]
    if vueltas and eventos & {"parada", "accion_bloqueada", "tiempo_agotado"}:
        vueltas = vueltas[:-1]
    return [llamada.get("name") for d in vueltas for llamada in d.get("pide_herramientas") or []]


def comprobar_traza(trazas: list[tuple[str, object]], resultado: dict) -> list[str]:
    """Diferencias entre la traza y lo que devolvió /registro (lista vacía = calza)."""
    pasos = [d.get("paso") for e, d in trazas if e == "llm" and isinstance(d, dict)]
    diferencias = []
    if (max(pasos) if pasos else 0) != resultado.get("pasos"):
        diferencias.append(f"la traza tiene {max(pasos) if pasos else 0} pasos y el registro {resultado.get('pasos')}")
    if herramientas_de_la_traza(trazas) != list(resultado.get("herramientas_usadas") or []):
        diferencias.append("las herramientas de la traza no son las del registro")
    return diferencias


def _corto(valor, largo: int = LARGO_RESULTADO) -> str:
    texto = valor if isinstance(valor, str) else json.dumps(valor, ensure_ascii=False, default=str)
    texto = " ".join(texto.split())
    return texto if len(texto) <= largo else texto[: largo - 1].rstrip() + f"… ({len(texto)} caracteres en total)"


def _pedidos(datos: dict) -> str:
    llamadas = datos.get("pide_herramientas") or []
    if not llamadas:
        return "ninguna herramienta (responde texto)"
    return " y ".join(f"`{l.get('name')}`" for l in llamadas)


def paso_a_paso(trazas: list[tuple[str, object]]) -> list[str]:
    """Markdown: por cada vuelta del ReAct, qué pidió, con qué argumentos, qué devolvió y qué hizo después."""
    vueltas = []  # [(datos_llm, [observaciones], [otros eventos del paso])]
    cierre = []
    for evento, datos in trazas:
        if evento == "llm":
            vueltas.append((datos, [], []))
        elif not vueltas:
            continue
        elif evento == "observacion":
            vueltas[-1][1].append(datos)
        elif evento in ("juez", "piso_reglas", "piso_verificacion", "fondo", "registro", "cerrar", "parada",
                        "tiempo_agotado", "fondo_error", "accion_bloqueada"):
            cierre.append((evento, datos))
        else:
            vueltas[-1][2].append((evento, datos))
    md = []
    for n, (llm, observaciones, otros) in enumerate(vueltas):
        md += [f"### Paso {llm.get('paso', n + 1)}", ""]
        if llm.get("texto"):
            md.append(f"- **El modelo escribe:** {_corto(llm['texto'], 400)}")
        llamadas = llm.get("pide_herramientas") or []
        if not llamadas:
            md.append("- **Pide:** ninguna herramienta.")
        for llamada in llamadas:
            md.append(f"- **Pide** `{llamada.get('name')}` con:")
            md += ["  ```json", *("  " + l for l in json.dumps(llamada.get("args"), ensure_ascii=False, indent=2).splitlines()), "  ```"]
        for evento, datos in otros:
            md.append(f"- **Control del grafo** `[{evento}]`: {_corto(datos, 300)}")
        for observacion in observaciones:
            md.append(f"- **Devuelve** `{observacion.get('herramienta')}`: {_corto(observacion.get('resultado'))}")
        if not observaciones and any(l.get("name") == "emitir_veredicto" for l in llamadas):
            md.append("- **Devuelve** `emitir_veredicto`: el veredicto estructurado. El grafo lo valida y, como es"
                      " válido, no vuelve al modelo; por eso esta observación no sale en la traza (el ReAct"
                      " imprime cada observación al empezar la vuelta siguiente).")
        if n + 1 < len(vueltas):
            md.append(f"- **Decide después:** paso {vueltas[n + 1][0].get('paso', n + 2)}, pide {_pedidos(vueltas[n + 1][0])}.")
        elif any(l.get("name") == "emitir_veredicto" for l in llamadas):
            veredicto = next(l.get("args") for l in llamadas if l.get("name") == "emitir_veredicto")
            md.append(f"- **Decide después:** nada más: emitió el veredicto (**{str(veredicto.get('decision')).upper()}**"
                      f" / {veredicto.get('politica')} / {veredicto.get('categoria')} / {veredicto.get('cuenta')})"
                      " → **parada por veredicto válido**; el grafo pasa al cierre.")
        md.append("")
    if cierre:
        md += ["### Cierre (grafo, sin el modelo del ReAct)", ""]
        nombres = {"juez": "Juez", "piso_reglas": "Piso por reglas", "piso_verificacion": "Piso por verificación",
                   "fondo": "Fondo por rendir", "registro": "Registro de veredictos", "cerrar": "Cierre",
                   "parada": "Parada por MAX_PASOS_REACT", "tiempo_agotado": "Tiempo agotado"}
        for evento, datos in cierre:
            md.append(f"- **{nombres.get(evento, evento)}** `[{evento}]`: {_corto(datos, 500)}")
        md.append("")
    return md


def _linea_de(ruta: Path, texto: str) -> int | None:
    try:
        return next(i for i, l in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1) if texto in l)
    except (OSError, StopIteration):
        return None


def condicion_de_parada(trazas: list[tuple[str, object]]) -> list[str]:
    """Las dos paradas del ReAct en un solo lugar: la de esta corrida y la de MAX_PASOS_REACT."""
    codigo = CARPETA.parents[1] / "src" / "principal" / "flujos" / "revisar_gasto.py"
    corte = _linea_de(codigo, 'if estado.get("pasos", 0) >= MAX_PASOS:')
    parada = _linea_de(codigo, "def nodo_parada(")
    ultimo = next((d for e, d in reversed(trazas) if e == "llm" and isinstance(d, dict)), {})
    emitio = any(l.get("name") == "emitir_veredicto" for l in ultimo.get("pide_herramientas") or [])
    return [
        "## Condición de parada",
        "",
        "El ciclo ReAct de `revisar_gasto` termina por una condición explícita. Las dos que pide la pauta:",
        "",
        "1. **Por veredicto válido (la de esta corrida).** "
        + (f"En el paso {ultimo.get('paso')} el modelo pidió `emitir_veredicto`; el grafo valida el veredicto,"
           " no vuelve al modelo y pasa al cierre (juez, fondo y registro), con `estado_final = \"ok\"`."
           if emitio else "En esta corrida el modelo no emitió el veredicto: ver la traza de arriba."),
        f"2. **Por máximo de pasos (`MAX_PASOS_REACT`: {config.MAX_PASOS} en esta corrida, que cerró en"
        f" {ultimo.get('paso')} pasos).** En"
        f" `src/principal/flujos/revisar_gasto.py`, `elegir_siguiente` manda al nodo `parada` cuando"
        f" `pasos >= MAX_PASOS` (línea {corte}), y `nodo_parada` (línea {parada}) responde «Me detuve: alcancé"
        " el máximo de N pasos…», sin veredicto y sin registrar, con `estado_final = \"error\"`. Lo prueba:",
        "   ```bash",
        '   python -m pytest -q "tests/test_react_mcp.py::test_se_detiene_por_max_pasos_con_estado_error"',
        "   ```",
        "   (un modelo que nunca emite veredicto, `MAX_PASOS=2` → 2 pasos, 2 llamadas al modelo, `error`,"
        " sin veredicto y sin escribir en el registro). La corrida real con `MAX_PASOS_REACT=2` está en"
        " `evidencias/react/02-parada-max-pasos-gs01.txt`.",
        "",
    ]


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
        desde = largo_del_log(opciones.log)
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
        # Los sondeos GET /registro/{id} solo muestran que se esperó: se cuentan en vez de copiarlos.
        sondeos = [linea for linea in log if _SONDEO.search(linea)]
        log = [linea for linea in log if not _SONDEO.search(linea)]
        if sondeos:
            log.append(f"(más {len(sondeos)} consultas GET /registro/{id_ejecucion} → 200 mientras corría; omitidas)")
        trazas, aviso_traza = [], None
        if opciones.log and id_ejecucion:
            ventana, aviso_traza = ventana_de_ejecucion(leer_desde(opciones.log, desde), id_ejecucion)
            trazas = extraer_trazas(ventana)
            if trazas and exito:
                diferencias = comprobar_traza(trazas, datos)
                if diferencias:
                    aviso_traza, trazas = "la traza no calza con el registro: " + "; ".join(diferencias), []
        seccion_traza = []
        if trazas:
            pasos_llm = max(d.get("paso", 0) for e, d in trazas if e == "llm" and isinstance(d, dict))
            seccion_traza = [
                "## Paso a paso del ReAct (traza de esta ejecución)",
                "",
                f"`id_ejecucion = {id_ejecucion}`. Con `MOSTRAR_TRAZAS=1` el ReAct imprime cada paso"
                " (`registrar_traza`) sin el id; aquí van las líneas del log entre «chat · <id> · aceptado» y"
                " «ejecución <id> · ruta=…», sin otra ejecución en medio. **Calza con el registro:**"
                f" {pasos_llm} pasos y herramientas {', '.join(f'`{h}`' for h in herramientas_de_la_traza(trazas))}.",
                "",
                *paso_a_paso(trazas),
                *(condicion_de_parada(trazas) if esperada == "revisar_gasto" else []),
                "<details><summary>Traza completa (los bloques tal como salen en el log)</summary>",
                "",
                "```text",
                *(ocultar_secretos(f"── [{e}] ──\n" + json.dumps(d, ensure_ascii=False, indent=2, default=str))
                  for e, d in trazas),
                "```",
                "",
                "</details>",
                "",
            ]
        elif aviso_traza and esperada == "revisar_gasto":
            seccion_traza = ["## Paso a paso del ReAct", "", f"No se incluye la traza: {aviso_traza}.", ""]
        registro_http = None
        if id_ejecucion:  # la ruta y el estado_final también tienen que verse en el registro
            registro_http = httpx.get(f"{opciones.url}/registro/{id_ejecucion}", headers={"X-API-Key": clave}, timeout=30)
        md = [
            f"# Recorrido {nombre}: ruta esperada `{esperada}`",
            "",
            f"Capturado el {datetime.now().astimezone().isoformat(timespec='seconds')} contra `{opciones.url}`"
            f" con `evidencias/dos-recorridos/capturar.py`.",
            "",
            *([f"**id_ejecucion:** `{id_ejecucion}`", ""] if id_ejecucion else []),
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
            *seccion_traza,
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
