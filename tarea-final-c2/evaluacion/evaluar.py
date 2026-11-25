"""Corre el golden set de C2 contra el agente y calcula el porcentaje de aciertos.

Dueño: Alex (c2tf/alex-integracion). Referencia: tarea-final-c1/pruebas/evaluar.py.

Uso (desde tarea-final-c2/):
    python -m evaluacion.evaluar --validar                 # solo revisa el formato del set
    python -m evaluacion.evaluar                           # contra el grafo, en este proceso
    python -m evaluacion.evaluar --url http://127.0.0.1:8000   # contra /chat (usa API_KEY_SERVICIO)
    python -m evaluacion.evaluar --grupo R-router          # un grupo
    python -m evaluacion.evaluar --casos GS-01 V-02        # algunos casos

Compara la RUTA y, si el caso la trae, la DECISIÓN. Cada turno queda como:
- acierto: ruta (y decisión) iguales a lo esperado;
- fallo: la ruta o la decisión no coinciden;
- pendiente: la ruta es correcta, pero el flujo de otra persona todavía no está implementado
  (no cuenta como acierto ni como fallo);
- error: el turno no se pudo ejecutar (proveedor, red, clave): tampoco cuenta.
El % de aciertos es aciertos / (aciertos + fallos). Escribe el informe (.md y .json) en
evidencias/ampliacion-evaluacion/.
"""

import argparse
import base64
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from uuid import uuid4

CARPETA = Path(__file__).resolve().parents[1]
if str(CARPETA) not in sys.path:
    sys.path.insert(0, str(CARPETA))

RUTA_GOLDEN = CARPETA / "evaluacion" / "golden_set.json"
CARPETA_INFORMES = CARPETA / "evidencias" / "ampliacion-evaluacion"
RUTAS = ("consulta_politica", "revisar_gasto", "fuera_de_alcance")
DECISIONES = ("aprobar", "observar", "rechazar")
MARCA_PENDIENTE = "todavía no implementado"
RESULTADOS = ("acierto", "fallo", "pendiente", "error")


# ---------------------------------------------------------------------------
# Golden set
# ---------------------------------------------------------------------------


def revisar_formato(golden: dict) -> list[str]:
    """Errores de formato del set (lista vacía si está bien)."""
    errores = []
    if not str(golden.get("version", "")).strip():
        errores.append("falta version")
    ids = [caso.get("id") for caso in golden.get("casos", [])]
    if len(ids) != len(set(ids)):
        errores.append("hay ids repetidos")
    if not golden.get("casos"):
        errores.append("no hay casos")
    for caso in golden.get("casos", []):
        donde = caso.get("id", "?")
        if caso.get("grupo") not in golden.get("grupos", {}):
            errores.append(f"{donde}: grupo desconocido {caso.get('grupo')!r}")
        if not caso.get("turnos"):
            errores.append(f"{donde}: sin turnos")
        for n, turno in enumerate(caso.get("turnos", []), 1):
            esperado = turno.get("esperado", {})
            if not str(turno.get("mensaje", "")).strip():
                errores.append(f"{donde} turno {n}: mensaje vacío")
            if esperado.get("ruta") not in RUTAS:
                errores.append(f"{donde} turno {n}: ruta esperada no válida")
            if esperado.get("decision") not in (None, *DECISIONES):
                errores.append(f"{donde} turno {n}: decisión esperada no válida")
            if esperado.get("decision") and esperado.get("ruta") != "revisar_gasto":
                errores.append(f"{donde} turno {n}: hay decisión esperada fuera de revisar_gasto")
            if turno.get("imagen") and not (CARPETA / turno["imagen"]).is_file():
                errores.append(f"{donde} turno {n}: no existe la imagen {turno['imagen']}")
    return errores


def cargar_golden(ruta: str | Path = RUTA_GOLDEN) -> dict:
    """Lee el golden set versionado y revisa que cada caso tenga el formato de su README."""
    golden = json.loads(Path(ruta).read_text(encoding="utf-8"))
    errores = revisar_formato(golden)
    if errores:
        raise ValueError("golden set con errores de formato:\n- " + "\n- ".join(errores))
    return golden


def filtrar(casos: list[dict], ids: list[str] | None = None, grupo: str | None = None) -> list[dict]:
    if ids:
        casos = [caso for caso in casos if caso["id"] in ids]
    if grupo:
        casos = [caso for caso in casos if caso["grupo"] == grupo]
    return casos


# ---------------------------------------------------------------------------
# Envío de un turno
# ---------------------------------------------------------------------------


def _imagen(ruta: str | None) -> dict | None:
    if not ruta:
        return None
    datos = (CARPETA / ruta).read_bytes()
    return {"mime_type": "image/png", "datos_base64": base64.b64encode(datos).decode("ascii")}


def enviar_en_proceso(turno: dict, thread_id: str) -> dict:
    """Corre el turno contra el grafo del agente principal en este proceso."""
    from src.principal.grafo import ejecutar

    return ejecutar(thread_id, turno["mensaje"], _imagen(turno.get("imagen")), turno.get("gasto"))


def crear_envio_http(url: str):
    """Corre el turno contra POST /chat de un servicio levantado (local o Heroku)."""
    import httpx

    clave = os.getenv("API_KEY_SERVICIO", "").strip()

    def enviar(turno: dict, thread_id: str) -> dict:
        cuerpo = {"thread_id": thread_id, "texto": turno["mensaje"]}
        if turno.get("gasto"):
            cuerpo["gasto"] = turno["gasto"]
        if turno.get("imagen"):
            cuerpo["imagen"] = _imagen(turno["imagen"])
        respuesta = httpx.post(f"{url.rstrip('/')}/chat", json=cuerpo, headers={"X-API-Key": clave}, timeout=180)
        if respuesta.status_code != 200:
            raise RuntimeError(f"HTTP {respuesta.status_code}: {respuesta.json().get('detail', respuesta.text)[:200]}")
        return respuesta.json()

    return enviar


# ---------------------------------------------------------------------------
# Comparación
# ---------------------------------------------------------------------------


def comparar_turno(esperado: dict, obtenido: dict) -> tuple[str, str]:
    """(resultado, detalle) de un turno. Solo se evalúan ruta y decisión."""
    ruta_ok = obtenido.get("ruta") == esperado["ruta"]
    if not ruta_ok:
        return "fallo", f"ruta {obtenido.get('ruta')} ≠ {esperado['ruta']}"
    if obtenido.get("estado_final") == "error" and MARCA_PENDIENTE in str(obtenido.get("respuesta", "")):
        return "pendiente", str(obtenido.get("respuesta", "")).split("\n")[0][:120]
    decision_esperada = esperado.get("decision")
    if decision_esperada:
        decision = (obtenido.get("veredicto") or {}).get("decision")
        if decision != decision_esperada:
            return "fallo", f"decisión {decision} ≠ {decision_esperada} (estado_final {obtenido.get('estado_final')})"
    return "acierto", ""


def resultado_del_caso(turnos: list[dict]) -> str:
    """Un caso es acierto si todos sus turnos lo son; si no, el peor resultado entre sus turnos."""
    resultados = {turno["resultado"] for turno in turnos}
    for resultado in ("fallo", "error", "pendiente"):
        if resultado in resultados:
            return resultado
    return "acierto"


def evaluar_caso(caso: dict, enviar) -> dict:
    """Corre los turnos del caso en un mismo hilo (thread_id) y compara cada uno."""
    thread_id = f"eval-{caso['id']}-{uuid4().hex[:8]}"
    turnos = []
    for n, turno in enumerate(caso["turnos"], 1):
        try:
            obtenido = enviar(turno, thread_id)
        except Exception as error:  # noqa: BLE001 (se registra como error del turno, no se oculta)
            from src.comun.errores import traducir_error

            turnos.append({"turno": n, "resultado": "error", "detalle": traducir_error(error), "id_ejecucion": None})
            continue
        resultado, detalle = comparar_turno(turno["esperado"], obtenido)
        turnos.append({
            "turno": n, "resultado": resultado, "detalle": detalle,
            "ruta": obtenido.get("ruta"), "decision": (obtenido.get("veredicto") or {}).get("decision"),
            "estado_final": obtenido.get("estado_final"), "id_ejecucion": obtenido.get("id_ejecucion"),
        })
    return {"id": caso["id"], "grupo": caso["grupo"], "resultado": resultado_del_caso(turnos), "turnos": turnos}


def porcentaje(cuenta: Counter) -> float | None:
    evaluados = cuenta["acierto"] + cuenta["fallo"]
    return round(100 * cuenta["acierto"] / evaluados, 1) if evaluados else None


def resumir(casos: list[dict]) -> dict:
    total = Counter(caso["resultado"] for caso in casos)
    por_grupo = defaultdict(Counter)
    for caso in casos:
        por_grupo[caso["grupo"]][caso["resultado"]] += 1
    turnos = Counter(turno["resultado"] for caso in casos for turno in caso["turnos"])
    rutas = Counter()
    for caso in casos:
        for turno in caso["turnos"]:
            if turno["resultado"] != "error":
                rutas["ruta_ok" if not str(turno.get("detalle", "")).startswith("ruta ") else "ruta_mal"] += 1
    return {
        "casos": {**{r: total[r] for r in RESULTADOS}, "total": len(casos), "porcentaje_aciertos": porcentaje(total)},
        "turnos": {**{r: turnos[r] for r in RESULTADOS}, "porcentaje_aciertos": porcentaje(turnos)},
        "router": {"rutas_correctas": rutas["ruta_ok"], "rutas_incorrectas": rutas["ruta_mal"],
                   "porcentaje": round(100 * rutas["ruta_ok"] / sum(rutas.values()), 1) if sum(rutas.values()) else None},
        "por_grupo": {
            grupo: {**{r: cuenta[r] for r in RESULTADOS}, "porcentaje_aciertos": porcentaje(cuenta)}
            for grupo, cuenta in sorted(por_grupo.items())
        },
    }


# ---------------------------------------------------------------------------
# Informe
# ---------------------------------------------------------------------------


def _commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=CARPETA, capture_output=True,
                              text=True, timeout=5).stdout.strip() or "desconocido"
    except (OSError, subprocess.SubprocessError):
        return "desconocido"


def texto_porcentaje(valor) -> str:
    return "—" if valor is None else f"{valor:.1f} %".replace(".", ",")


def informe_markdown(datos: dict) -> str:
    r = datos["resumen"]
    lineas = [
        f"# Evaluación con golden set · {datos['fecha']}",
        "",
        "| Dato | Valor |", "|---|---|",
        f"| Versión del set | {datos['version_set']} ({datos['casos_corridos']} de {datos['casos_en_set']} casos) |",
        f"| Modelo | {datos['modelo']} |",
        f"| Modo | {datos['modo']} |",
        f"| Commit | {datos['commit']} |",
        f"| % de aciertos (casos) | **{texto_porcentaje(r['casos']['porcentaje_aciertos'])}** "
        f"({r['casos']['acierto']} aciertos / {r['casos']['acierto'] + r['casos']['fallo']} evaluados) |",
        f"| % de aciertos (turnos) | {texto_porcentaje(r['turnos']['porcentaje_aciertos'])} |",
        f"| Router: rutas correctas | {r['router']['rutas_correctas']} de {r['router']['rutas_correctas'] + r['router']['rutas_incorrectas']}"
        f" ({texto_porcentaje(r['router']['porcentaje'])}) |",
        f"| Pendientes (flujo de otra persona sin implementar) | {r['casos']['pendiente']} casos |",
        f"| Errores de ejecución | {r['casos']['error']} casos |",
        "",
        "El % se calcula sobre aciertos + fallos; los pendientes y los errores no suman ni restan.",
        "",
        "## Por grupo",
        "", "| Grupo | Aciertos | Fallos | Pendientes | Errores | % aciertos |", "|---|---|---|---|---|---|",
        *[f"| {g} | {c['acierto']} | {c['fallo']} | {c['pendiente']} | {c['error']} | {texto_porcentaje(c['porcentaje_aciertos'])} |"
          for g, c in r["por_grupo"].items()],
        "",
        "## Fallos",
        "",
    ]
    fallos = [(caso, t) for caso in datos["casos"] for t in caso["turnos"] if t["resultado"] == "fallo"]
    lineas += [f"- **{caso['id']}** turno {t['turno']}: {t['detalle']} · id_ejecucion `{t.get('id_ejecucion')}`"
               for caso, t in fallos] or ["(ninguno)"]
    errores = [(caso, t) for caso in datos["casos"] for t in caso["turnos"] if t["resultado"] == "error"]
    if errores:
        lineas += ["", "## Errores de ejecución", ""]
        lineas += [f"- **{caso['id']}** turno {t['turno']}: {t['detalle']}" for caso, t in errores[:20]]
    pendientes = Counter(t["detalle"] for caso in datos["casos"] for t in caso["turnos"] if t["resultado"] == "pendiente")
    if pendientes:
        lineas += ["", "## Pendientes", ""] + [f"- {n} turno(s): {detalle}" for detalle, n in pendientes.most_common()]
    return "\n".join(lineas) + "\n"


def guardar_informe(datos: dict, carpeta: Path = CARPETA_INFORMES) -> tuple[Path, Path]:
    from src.comun.errores import ocultar_secretos

    carpeta.mkdir(parents=True, exist_ok=True)
    nombre = f"informe-{datos['fecha'].replace(':', '').replace('-', '')[:15]}"
    ruta_md, ruta_json = carpeta / f"{nombre}.md", carpeta / f"{nombre}.json"
    ruta_md.write_text(ocultar_secretos(informe_markdown(datos)), encoding="utf-8")
    ruta_json.write_text(ocultar_secretos(json.dumps(datos, ensure_ascii=False, indent=2, default=str)) + "\n", encoding="utf-8")
    return ruta_md, ruta_json


def correr(golden: dict, casos: list[dict], enviar, modo: str) -> dict:
    resultados = []
    for caso in casos:
        resultado = evaluar_caso(caso, enviar)
        resultados.append(resultado)
        print(f"{resultado['id']:6} {resultado['grupo']:20} {resultado['resultado']}", flush=True)
    return {
        "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
        "version_set": golden["version"],
        "casos_en_set": len(golden["casos"]),
        "casos_corridos": len(casos),
        "modelo": os.getenv("MODELO_PRINCIPAL", "").strip() or "sin MODELO_PRINCIPAL",
        "modo": modo,
        "commit": _commit(),
        "resumen": resumir(resultados),
        "casos": resultados,
    }


def main(argumentos: list[str] | None = None) -> int:
    """Corre todos los casos, muestra la tabla y el % de aciertos y guarda el resultado."""
    parser = argparse.ArgumentParser(description="Evaluación con el golden set de C2")
    parser.add_argument("--validar", action="store_true", help="solo revisa el formato del set")
    parser.add_argument("--url", help="evaluar contra POST /chat de este servicio")
    parser.add_argument("--grupo")
    parser.add_argument("--casos", nargs="*")
    parser.add_argument("--salida", default=str(CARPETA_INFORMES))
    opciones = parser.parse_args(argumentos)

    from src.comun import config  # noqa: F401  (carga el .env)

    golden = cargar_golden()
    casos = filtrar(golden["casos"], opciones.casos, opciones.grupo)
    if opciones.validar:
        print(f"golden set v{golden['version']}: formato correcto, {len(golden['casos'])} casos "
              f"({sum(len(c['turnos']) for c in golden['casos'])} turnos).")
        return 0
    if opciones.url:
        if not os.getenv("API_KEY_SERVICIO", "").strip():
            print("Falta API_KEY_SERVICIO para llamar a /chat.")
            return 2
        enviar, modo = crear_envio_http(opciones.url), f"HTTP {opciones.url}/chat"
    else:
        if not os.getenv("GOOGLE_API_KEY", "").strip():
            print("Falta GOOGLE_API_KEY: el router necesita Gemini. No se escribe informe (usa --validar para el formato).")
            return 2
        enviar, modo = enviar_en_proceso, "en proceso (src.principal.grafo.ejecutar)"

    datos = correr(golden, casos, enviar, modo)
    ruta_md, _ = guardar_informe(datos, Path(opciones.salida))
    r = datos["resumen"]["casos"]
    print(f"\n% de aciertos: {texto_porcentaje(r['porcentaje_aciertos'])} · aciertos {r['acierto']} · fallos {r['fallo']}"
          f" · pendientes {r['pendiente']} · errores {r['error']}\nInforme: {ruta_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
