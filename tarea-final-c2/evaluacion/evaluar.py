"""Corre el golden set de C2 contra el agente y calcula el porcentaje de aciertos.

Dueño: Alex (c2tf/alex-integracion). Referencia: tarea-final-c1/pruebas/evaluar.py.

Uso (desde tarea-final-c2/):
    python -m evaluacion.evaluar --validar                 # solo revisa el formato del set
    python -m evaluacion.evaluar                           # contra el grafo, en este proceso
    python -m evaluacion.evaluar --url http://127.0.0.1:8000   # contra /chat (usa API_KEY_SERVICIO)
    python -m evaluacion.evaluar --grupo R-router          # un grupo
    python -m evaluacion.evaluar --casos GS-01 V-02        # algunos casos
    python -m evaluacion.evaluar --pausa 20                # 20 s entre casos (cuota por minuto de Gemini)
    python -m evaluacion.evaluar --retomar                 # sigue desde el avance parcial guardado
    python -m evaluacion.evaluar --desde GS-17             # (re)corre desde ese caso (id o posición 1..N)

Corrida larga y cuota: después de cada caso se guarda el avance en
evidencias/ampliacion-evaluacion/avance-parcial.json. Si Gemini responde sin cuota (429 /
RESOURCE_EXHAUSTED), el caso se reintenta hasta 2 veces con espera creciente; si sigue sin cuota,
la corrida se detiene sola (código 3), guarda el avance y dice desde qué caso seguir. Ese caso no
se cuenta como fallo ni como error del agente: se vuelve a correr completo al retomar. El informe
final se escribe solo cuando están todos los casos, e indica en cuántas corridas se armó y con qué
modelos (y entonces se borra el avance parcial).

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
import re
import subprocess
import sys
import time
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
NOMBRE_AVANCE = "avance-parcial.json"
ESPERA_CUOTA_SEG = 30.0  # primera espera ante un 429; la segunda es el doble
REINTENTOS_CUOTA = 2
# Señales de cuota agotada: el texto crudo del proveedor y el mensaje de src/comun/errores.py.
MARCAS_CUOTA = ("resource_exhausted", "quota", "rate limit", "rate_limit", "ratelimit", "no tiene cuota")
_CODIGO_429 = re.compile(r"(?<![\d.])429(?![\d.])")  # el código HTTP, no un 429 dentro de un monto o folio


class CorteCuota(Exception):
    """Un turno no se pudo correr porque Gemini no tiene cuota. No es un resultado del agente."""

    def __init__(self, caso_id: str, detalle: str):
        super().__init__(detalle)
        self.caso_id = caso_id
        self.detalle = detalle


class EvaluacionInterrumpida(Exception):
    """La corrida se detuvo por cuota después de los reintentos; el avance ya quedó guardado."""

    def __init__(self, avance: dict, caso_id: str, posicion: int, detalle: str):
        super().__init__(f"sin cuota en el caso {caso_id} ({posicion} de {len(avance['seleccion'])})")
        self.avance = avance
        self.caso_id = caso_id
        self.posicion = posicion
        self.detalle = detalle


def es_error_de_cuota(texto: str) -> bool:
    """True si el texto de un error (crudo o traducido) indica cuota agotada (429 / RESOURCE_EXHAUSTED)."""
    crudo = str(texto).lower()
    return any(marca in crudo for marca in MARCAS_CUOTA) or bool(_CODIGO_429.search(crudo))


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
    """Corre el turno contra POST /chat de un servicio levantado (local o Heroku).

    /chat es asíncrono: responde 202 y el resultado se consulta en GET /registro/{id} cada 1 s,
    sin quedar atado a los 30 s de Heroku. Si la ejecución termina en error, se lanza con su
    mensaje (así una falta de cuota se reconoce y corta la corrida).
    """
    import httpx

    clave = os.getenv("API_KEY_SERVICIO", "").strip()

    def enviar(turno: dict, thread_id: str) -> dict:
        cuerpo = {"thread_id": thread_id, "texto": turno["mensaje"]}
        if turno.get("gasto"):
            cuerpo["gasto"] = turno["gasto"]
        if turno.get("imagen"):
            cuerpo["imagen"] = _imagen(turno["imagen"])
        base = url.rstrip("/")
        respuesta = httpx.post(f"{base}/chat", json=cuerpo, headers={"X-API-Key": clave}, timeout=60)
        if respuesta.status_code == 200:  # servicio antiguo, síncrono
            return respuesta.json()
        if respuesta.status_code != 202:
            raise RuntimeError(f"HTTP {respuesta.status_code}: {respuesta.json().get('detail', respuesta.text)[:200]}")
        consultar = f"{base}{respuesta.json()['consultar']}"
        fin = time.monotonic() + 300
        while time.monotonic() < fin:
            datos = httpx.get(consultar, headers={"X-API-Key": clave}, timeout=30).json()
            if datos.get("estado") != "en_proceso":
                if datos.get("resultado"):
                    return datos["resultado"]
                raise RuntimeError(str(datos.get("detail") or f"la ejecución terminó en {datos.get('estado')} sin resultado"))
            time.sleep(1)
        raise RuntimeError("la ejecución siguió en proceso más de 300 s")

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
    """Corre los turnos del caso en un mismo hilo (thread_id) y compara cada uno.

    Lanza CorteCuota si un turno falla por cuota: el caso entero se repite después (hilo nuevo),
    así que no queda a medias ni cuenta como error del agente.
    """
    thread_id = f"eval-{caso['id']}-{uuid4().hex[:8]}"
    turnos = []
    for n, turno in enumerate(caso["turnos"], 1):
        try:
            obtenido = enviar(turno, thread_id)
        except Exception as error:  # noqa: BLE001 (se registra como error del turno, no se oculta)
            from src.comun.errores import traducir_error

            detalle = traducir_error(error)
            if es_error_de_cuota(f"{error.__class__.__name__} {error} {detalle}"):
                raise CorteCuota(caso["id"], detalle) from None
            turnos.append({"turno": n, "resultado": "error", "detalle": detalle, "id_ejecucion": None})
            continue
        if obtenido.get("estado_final") == "error" and es_error_de_cuota(obtenido.get("respuesta", "")):
            raise CorteCuota(caso["id"], str(obtenido.get("respuesta", ""))[:200])
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
        "turnos_fallback": sum(1 for caso in casos for t in caso["turnos"] if t.get("estado_final") == "fallback"),
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


def _texto_corridas(corridas: list[dict]) -> str:
    if len(corridas) <= 1:
        return "1 (una sola corrida)"
    cortes = sum(1 for c in corridas if c.get("corte"))
    return f"{len(corridas)} (retomada {len(corridas) - 1} vez/veces; {cortes} corte(s) por cuota)"


def informe_markdown(datos: dict) -> str:
    r = datos["resumen"]
    corridas = datos.get("corridas") or []
    lineas = [
        f"# Evaluación con golden set · {datos['fecha']}",
        "",
        "| Dato | Valor |", "|---|---|",
        f"| Versión del set | {datos['version_set']} ({datos['casos_corridos']} de {datos['casos_en_set']} casos) |",
        f"| Modelo | {datos['modelo']} |",
        f"| Corridas | {_texto_corridas(corridas)} |",
        f"| Modo | {datos['modo']} |",
        f"| Commit | {datos['commit']} |",
        f"| % de aciertos (casos) | **{texto_porcentaje(r['casos']['porcentaje_aciertos'])}** "
        f"({r['casos']['acierto']} aciertos / {r['casos']['acierto'] + r['casos']['fallo']} evaluados) |",
        f"| % de aciertos (turnos) | {texto_porcentaje(r['turnos']['porcentaje_aciertos'])} |",
        f"| Router: rutas correctas | {r['router']['rutas_correctas']} de {r['router']['rutas_correctas'] + r['router']['rutas_incorrectas']}"
        f" ({texto_porcentaje(r['router']['porcentaje'])}) |",
        f"| Pendientes (flujo de otra persona sin implementar) | {r['casos']['pendiente']} casos |",
        f"| Errores de ejecución | {r['casos']['error']} casos |",
        f"| Turnos con `estado_final = fallback` (respaldo o A2A caído) | {r.get('turnos_fallback', 0)} |",
        *([f"| Casos omitidos (antes de `--desde`, sin avance previo) | {', '.join(datos['omitidos'])} |"]
          if datos.get("omitidos") else []),
        "",
        "El % se calcula sobre aciertos + fallos; los pendientes y los errores no suman ni restan.",
        "Los casos cortados por cuota no cuentan: se volvieron a correr completos al retomar.",
        "",
    ]
    if corridas:
        lineas += [
            "## Corridas", "",
            "| # | Inicio | Fin | Casos terminados | Modelo principal | Modelo de respaldo | Commit | Corte |",
            "|---|---|---|---|---|---|---|---|",
            *[
                f"| {n} | {c.get('inicio')} | {c.get('fin') or '—'} | {len(c.get('casos', []))} | "
                f"{c.get('modelo_principal') or '—'} | {c.get('modelo_respaldo') or '—'} | {c.get('commit')} | "
                + (f"sin cuota en {c['corte']['caso']} ({c['corte']['posicion']} de {len(datos.get('seleccion', []))})"
                   if c.get("corte") else "—")
                + " |"
                for n, c in enumerate(corridas, 1)
            ],
            "",
        ]
    lineas += [
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


# ---------------------------------------------------------------------------
# Avance parcial (para retomar una corrida cortada)
# ---------------------------------------------------------------------------


def _ahora() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def nuevo_avance(golden: dict, casos: list[dict]) -> dict:
    """Avance vacío para la selección de casos (en su orden)."""
    return {"version_set": golden["version"], "seleccion": [c["id"] for c in casos],
            "omitidos": [], "corridas": [], "casos": []}


def cargar_avance(ruta: Path) -> dict | None:
    if not Path(ruta).is_file():
        return None
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def guardar_avance(avance: dict, ruta: Path) -> None:
    """Escribe el avance de forma atómica (archivo temporal + reemplazo), sin claves."""
    from src.comun.errores import ocultar_secretos

    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_suffix(".tmp")
    temporal.write_text(ocultar_secretos(json.dumps(avance, ensure_ascii=False, indent=2, default=str)) + "\n",
                        encoding="utf-8")
    temporal.replace(ruta)


def posicion_desde(desde: str, casos: list[dict]) -> int:
    """Índice (0..N-1) del caso desde el que se corre: `desde` es un id (GS-17) o una posición 1..N."""
    ids = [c["id"] for c in casos]
    if desde in ids:
        return ids.index(desde)
    if str(desde).isdigit() and 1 <= int(desde) <= len(ids):
        return int(desde) - 1
    raise ValueError(f"--desde {desde}: no es un id de la selección ni una posición entre 1 y {len(ids)}.")


def armar_datos(golden: dict, avance: dict, modo: str) -> dict:
    """Datos del informe final a partir del avance completo (casos en el orden de la selección)."""
    orden = {caso_id: n for n, caso_id in enumerate(avance["seleccion"])}
    resultados = sorted(avance["casos"], key=lambda r: orden.get(r["id"], len(orden)))
    corridas = avance["corridas"]
    principales = list(dict.fromkeys(c.get("modelo_principal") or "sin MODELO_PRINCIPAL" for c in corridas))
    respaldos = list(dict.fromkeys(c["modelo_respaldo"] for c in corridas if c.get("modelo_respaldo")))
    modelo = ", ".join(principales) or os.getenv("MODELO_PRINCIPAL", "").strip() or "sin MODELO_PRINCIPAL"
    if respaldos:
        modelo += f" (respaldo: {', '.join(respaldos)})"
    return {
        "fecha": _ahora(),
        "version_set": golden["version"],
        "casos_en_set": len(golden["casos"]),
        "casos_corridos": len(resultados),
        "seleccion": avance["seleccion"],
        "omitidos": avance.get("omitidos", []),
        "modelo": modelo,
        "modelos": {"principal": principales, "respaldo": respaldos},
        "modo": modo,
        "commit": _commit(),
        "corridas": corridas,
        "resumen": resumir(resultados),
        "casos": resultados,
    }


def correr(golden: dict, casos: list[dict], enviar, modo: str, pausa: float = 0.0, *,
           avance: dict | None = None, al_guardar=None, espera_cuota: float = ESPERA_CUOTA_SEG,
           reintentos_cuota: int = REINTENTOS_CUOTA, dormir=time.sleep) -> dict:
    """Corre los casos que faltan en `avance` y devuelve los datos del informe.

    - `pausa`: segundos entre casos, para no chocar con el límite por minuto de Gemini.
    - `al_guardar(avance)`: se llama después de cada caso terminado (y al cortar), para retomar.
    - Sin cuota: hasta `reintentos_cuota` reintentos del caso con espera creciente
      (`espera_cuota`, luego el doble). Si sigue sin cuota, guarda el avance y lanza
      EvaluacionInterrumpida: ese caso no se cuenta y se corre completo al retomar.
    """
    avance = avance if avance is not None else nuevo_avance(golden, casos)
    guardar = al_guardar or (lambda _avance: None)
    corrida = {
        "inicio": _ahora(), "fin": None, "modo": modo, "commit": _commit(),
        "modelo_principal": os.getenv("MODELO_PRINCIPAL", "").strip() or None,
        "modelo_respaldo": os.getenv("MODELO_RESPALDO", "").strip() or None,
        "casos": [], "corte": None,
    }
    avance["corridas"].append(corrida)
    listos = {r["id"] for r in avance["casos"]} | set(avance.get("omitidos", []))
    por_correr = [caso for caso in casos if caso["id"] not in listos]
    for n, caso in enumerate(por_correr):
        if pausa > 0 and n:
            dormir(pausa)
        for intento in range(reintentos_cuota + 1):
            try:
                resultado = evaluar_caso(caso, enviar)
                break
            except CorteCuota as corte:
                if intento == reintentos_cuota:
                    posicion = avance["seleccion"].index(caso["id"]) + 1
                    corrida["fin"] = _ahora()
                    corrida["corte"] = {"caso": caso["id"], "posicion": posicion, "detalle": corte.detalle}
                    guardar(avance)
                    raise EvaluacionInterrumpida(avance, caso["id"], posicion, corte.detalle) from None
                espera = espera_cuota * (intento + 1)
                print(f"{caso['id']:6} sin cuota de Gemini: reintento {intento + 1} de {reintentos_cuota} en {espera:g} s",
                      flush=True)
                dormir(espera)
        avance["casos"].append(resultado)
        corrida["casos"].append(caso["id"])
        corrida["fin"] = _ahora()
        guardar(avance)
        print(f"{resultado['id']:6} {resultado['grupo']:20} {resultado['resultado']}", flush=True)
    corrida["fin"] = corrida["fin"] or _ahora()
    guardar(avance)
    return armar_datos(golden, avance, modo)


def main(argumentos: list[str] | None = None) -> int:
    """Corre todos los casos, muestra la tabla y el % de aciertos y guarda el resultado."""
    parser = argparse.ArgumentParser(description="Evaluación con el golden set de C2")
    parser.add_argument("--validar", action="store_true", help="solo revisa el formato del set")
    parser.add_argument("--url", help="evaluar contra POST /chat de este servicio")
    parser.add_argument("--grupo")
    parser.add_argument("--casos", nargs="*")
    parser.add_argument("--salida", default=str(CARPETA_INFORMES))
    parser.add_argument("--pausa", type=float, default=0.0,
                        help="segundos de espera entre casos (ej. 20) para no agotar la cuota por minuto")
    parser.add_argument("--retomar", action="store_true", help="sigue desde el avance parcial guardado")
    parser.add_argument("--desde", help="(re)corre desde este caso: id (GS-17) o posición 1..N de la selección")
    parser.add_argument("--nuevo", action="store_true", help="descarta el avance parcial y empieza de cero")
    parser.add_argument("--avance", help=f"archivo de avance parcial (por defecto <salida>/{NOMBRE_AVANCE})")
    parser.add_argument("--espera-cuota", type=float, default=ESPERA_CUOTA_SEG,
                        help="segundos de la primera espera ante un 429 (la segunda es el doble)")
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

    ruta_avance = Path(opciones.avance) if opciones.avance else Path(opciones.salida) / NOMBRE_AVANCE
    avance = None if opciones.nuevo else cargar_avance(ruta_avance)
    if avance is not None and not (opciones.retomar or opciones.desde):
        print(f"Hay un avance parcial ({len(avance['casos'])} de {len(avance['seleccion'])} casos) en {ruta_avance}.\n"
              "Usa --retomar para seguir desde ahí, o --nuevo para empezar de cero.")
        return 2
    if opciones.retomar and avance is None:
        print(f"No hay avance parcial en {ruta_avance}: corre sin --retomar para empezar.")
        return 2
    if avance is not None and (avance.get("version_set") != golden["version"]
                               or avance.get("seleccion") != [c["id"] for c in casos]):
        print("El avance parcial es de otra versión del set o de otra selección de casos (--grupo/--casos).\n"
              "Repite los mismos filtros, o usa --nuevo para empezar de cero.")
        return 2
    avance = avance or nuevo_avance(golden, casos)
    if opciones.desde:
        try:
            inicio = posicion_desde(opciones.desde, casos)
        except ValueError as error:
            print(error)
            return 2
        anteriores = [c["id"] for c in casos[:inicio]]
        avance["casos"] = [r for r in avance["casos"] if r["id"] in anteriores]
        hechos = {r["id"] for r in avance["casos"]}
        avance["omitidos"] = [caso_id for caso_id in anteriores if caso_id not in hechos]

    try:
        datos = correr(golden, casos, enviar, modo, pausa=max(opciones.pausa, 0.0), avance=avance,
                       al_guardar=lambda a: guardar_avance(a, ruta_avance),
                       espera_cuota=max(opciones.espera_cuota, 0.0))
    except EvaluacionInterrumpida as corte:
        terminados = len(corte.avance["casos"])
        filtros = (f" --grupo {opciones.grupo}" if opciones.grupo else "") + (
            f" --casos {' '.join(opciones.casos)}" if opciones.casos else "") + (
            f" --url {opciones.url}" if opciones.url else "") + (
            f" --salida {opciones.salida}" if opciones.salida != str(CARPETA_INFORMES) else "") + (
            f" --avance {opciones.avance}" if opciones.avance else "")
        print(f"\nSe detuvo: Gemini sigue sin cuota en el caso {corte.caso_id} ({corte.posicion} de "
              f"{len(corte.avance['seleccion'])}) después de {REINTENTOS_CUOTA} reintentos. Ese caso no se cuenta.\n"
              f"Avance guardado ({terminados} casos terminados): {ruta_avance}\n"
              f"Para seguir desde {corte.caso_id}, cuando vuelva la cuota:\n"
              f"    python -m evaluacion.evaluar --retomar{filtros} --pausa {max(opciones.pausa, 20):g}")
        return 3
    ruta_md, _ = guardar_informe(datos, Path(opciones.salida))
    ruta_avance.unlink(missing_ok=True)  # ya quedó todo en el informe (incluidas las corridas)
    r = datos["resumen"]["casos"]
    print(f"\n% de aciertos: {texto_porcentaje(r['porcentaje_aciertos'])} · aciertos {r['acierto']} · fallos {r['fallo']}"
          f" · pendientes {r['pendiente']} · errores {r['error']} · corridas {len(datos['corridas'])}\nInforme: {ruta_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
