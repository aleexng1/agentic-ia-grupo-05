"""Evaluador del golden set: compara lo que hizo el agente con la respuesta correcta.

Dueño: rol Caso y calidad.

Uso, desde tarea-final-c1/:
    python pruebas/evaluar.py                      # todos los casos (usa Gemini y Redis)
    python pruebas/evaluar.py --caso GS-07,GS-26   # solo esos casos
    python pruebas/evaluar.py --grupo B            # solo un grupo (A a F)
    python pruebas/evaluar.py --componente rag     # solo los casos de un componente
    python pruebas/evaluar.py --pausa 2            # espera 2 segundos entre casos
    python pruebas/evaluar.py --seco               # revisa el golden set, sin LLM ni clave
    python pruebas/evaluar.py --autoprueba         # prueba este evaluador, sin LLM ni clave

Desde el notebook:
    from pruebas.evaluar import evaluar, guardar_resultados, mostrar_tabla
    resultados = evaluar(grupo="B", pausa=2)
    mostrar_tabla(resultados)

Qué compara: el veredicto FINAL guardado en el estado del agente (el que ya pasó por el piso de
reglas y el juez), no la propuesta del LLM. Solo evalúa los campos definidos en cada `esperado`.

Decisiones de diseño:
- Cada caso parte limpio: hilo nuevo, registro vacío y fondos en su saldo inicial.
- La corrida usa un registro temporal, así que no toca el registro_veredictos.db de cada persona.
- Un error del agente deja ese caso en ❌ y la corrida sigue con el siguiente.
- Los resultados guardan versiones y modelo, pero nunca la clave ni las variables de entorno.
"""

import argparse
import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unicodedata
from datetime import datetime
from pathlib import Path
from unittest import mock

CARPETA = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CARPETA))

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage  # noqa: E402
from langchain_core.tools import tool  # noqa: E402

from src import grafo, memoria, registro  # noqa: E402
from src.config import MODELO_DEL_CURSO, TEMPERATURA  # noqa: E402
from src.herramientas import leer_politica, resolver_politica  # noqa: E402

RUTA_GOLDEN = CARPETA / "pruebas" / "golden_set.json"
CARPETA_RESULTADOS = CARPETA / "pruebas" / "resultados"

GRUPOS = ("A-limpio", "B-mal-clasificado", "C-regla", "D-fondo", "E-seguridad", "F-conversacion")
ACCIONES_PROHIBIDAS = ("registrar_aprobacion", "modificar_registro")
CAMPOS_ESPERADO = {
    "decision", "politica", "categoria", "cuenta", "reglas", "debe_contener", "debe_contener_alguno",
    "herramientas_esperadas", "herramientas_prohibidas", "acciones_prohibidas",
}

# Texto que separa el mensaje del usuario del gasto dentro de un turno.
MARCA_GASTO = "\n\nGasto rendido (JSON):\n"

# Segundos de espera antes de cada reintento cuando se choca con el límite de llamadas.
ESPERAS_REINTENTO = (20, 60, 120)

# Fila que se pone en el registro antes de un turno con "modificar_registro". Sin ella, el
# registro estaría vacío y un borrado total no cambiaría nada: pasaría sin que nadie lo note.
GASTO_CONTROL = {"id": "CONTROL-EVALUADOR", "id_fondo": "FR-001", "monto": 1}
VEREDICTO_CONTROL = {
    "decision": "observar",
    "motivo": "Fila de control del evaluador.",
    "politica_sugerida": "-",
    "categoria_sugerida": "-",
    "cuenta_sugerida": "-",
}

_CODIGO_REGLA = re.compile(r"(?<![A-Za-z0-9-])(?:RG-\d{2}|P\d{2})(?![A-Za-z0-9])", re.IGNORECASE)
_LIMITE_LLAMADAS = re.compile(
    r"\b429\b|resource.?exhausted|too.?many.?requests|rate.?limit|quota", re.IGNORECASE
)


# ---------------------------------------------------------------------------
# Ayudas para comparar textos
# ---------------------------------------------------------------------------


def normalizar(texto) -> str:
    """Quita tildes, mayúsculas y espacios de más, para comparar sin que eso importe."""
    descompuesto = unicodedata.normalize("NFKD", str(texto))
    sin_tildes = "".join(letra for letra in descompuesto if not unicodedata.combining(letra))
    return " ".join(sin_tildes.casefold().split())


def codigo_politica(texto) -> str | None:
    """Traduce "P02", "Viajes Internos" o "P02 — Viajes Internos" al código; None si no existe."""
    try:
        return resolver_politica(" ".join(str(texto or "").split()))["codigo"]
    except ValueError:
        return None


def reglas_citadas(texto: str) -> list[str]:
    """Códigos de reglas que aparecen en un texto, sin repetir ("RG-03", "P07")."""
    return sorted({codigo.upper() for codigo in _CODIGO_REGLA.findall(texto)})


def recortar(texto: str, largo: int = 120) -> str:
    """Acorta un texto largo para mostrarlo en una línea."""
    limpio = " ".join(str(texto).split())
    return limpio if len(limpio) <= largo else limpio[: largo - 1] + "…"


def ocultar_secretos(texto: str) -> str:
    """Borra la clave de API y la URL de Redis de un texto, por si vienen en un mensaje de error."""
    url = os.getenv("REDIS_URL", "")
    clave_redis = re.search(r"://[^:/@]*:([^@]*)@", url)
    secretos = [os.getenv("GOOGLE_API_KEY", ""), url, clave_redis.group(1) if clave_redis else ""]
    for secreto in secretos:
        if secreto.strip():
            texto = texto.replace(secreto, "[oculto]")
    return texto


def es_limite_de_llamadas(error: BaseException | None) -> bool:
    """Reconoce un 429, aunque venga escondido dentro de otro error (rag.py lo envuelve)."""
    while error is not None:
        if _LIMITE_LLAMADAS.search(f"{type(error).__name__} {error}"):
            return True
        error = error.__cause__ or error.__context__
    return False


# ---------------------------------------------------------------------------
# Golden set: carga, revisión de formato y filtros
# ---------------------------------------------------------------------------


def revisar_formato(golden: dict) -> list[str]:
    """Devuelve la lista de problemas de formato del golden set (vacía si está bien)."""
    problemas = []
    for clave in ("version", "politica_version"):
        if not isinstance(golden.get(clave), str):
            problemas.append(f"falta el campo '{clave}'")
    casos = golden.get("casos")
    if not isinstance(casos, list) or not casos:
        return [*problemas, "no hay casos"]
    ids = [caso.get("id") for caso in casos]
    problemas += [f"{id_caso}: id repetido" for id_caso in sorted({i for i in ids if ids.count(i) > 1})]
    for caso in casos:
        problemas += revisar_caso(caso)
    return problemas


def revisar_caso(caso: dict) -> list[str]:
    """Revisa un caso: grupo, componentes, turnos, acciones y que su fondo calce con los datos."""
    donde = caso.get("id", "caso sin id")
    problemas = []
    if caso.get("grupo") not in GRUPOS:
        problemas.append(f"{donde}: grupo '{caso.get('grupo')}' no existe")
    if not caso.get("componentes"):
        problemas.append(f"{donde}: faltan los componentes")
    if not caso.get("turnos"):
        problemas.append(f"{donde}: no tiene turnos")
    for numero, turno in enumerate(caso.get("turnos", []), start=1):
        esperado = turno.get("esperado", {})
        if not turno.get("mensaje"):
            problemas.append(f"{donde} turno {numero}: falta 'mensaje'")
        if set(esperado) - CAMPOS_ESPERADO:
            problemas.append(f"{donde} turno {numero}: campos desconocidos {sorted(set(esperado) - CAMPOS_ESPERADO)}")
        for accion in esperado.get("acciones_prohibidas", []):
            if accion not in ACCIONES_PROHIBIDAS:
                problemas.append(f"{donde} turno {numero}: acción '{accion}' no es un código {ACCIONES_PROHIBIDAS}")
    fondo = caso.get("contexto", {}).get("fondo")
    if fondo:
        try:
            saldo = memoria.fondo_inicial(fondo["id_fondo"])["saldo_inicial"]
        except (KeyError, ValueError) as error:
            problemas.append(f"{donde}: fondo no válido ({error})")
        else:
            if saldo != fondo.get("saldo_inicial"):
                problemas.append(f"{donde}: {fondo['id_fondo']} parte con {saldo}, no con {fondo.get('saldo_inicial')}")
    return problemas


def cargar_golden() -> dict:
    """Lee el golden set y se detiene con un mensaje claro si su formato no es válido."""
    golden = json.loads(RUTA_GOLDEN.read_text(encoding="utf-8"))
    problemas = revisar_formato(golden)
    if problemas:
        raise ValueError("El golden set tiene problemas de formato:\n- " + "\n- ".join(problemas))
    return golden


def filtrar_casos(casos: list[dict], ids=None, grupo=None, componente=None) -> list[dict]:
    """Elige los casos pedidos. `ids` puede ser "GS-07,GS-08" o una lista."""
    seleccion = casos
    if ids:
        pedidos = [i.strip().upper() for i in (ids.split(",") if isinstance(ids, str) else ids)]
        existentes = {caso["id"] for caso in casos}
        desconocidos = [i for i in pedidos if i not in existentes]
        if desconocidos:
            raise ValueError(f"No existen estos casos: {', '.join(desconocidos)}.")
        seleccion = [caso for caso in seleccion if caso["id"] in pedidos]
    if grupo:
        seleccion = [caso for caso in seleccion if normalizar(caso["grupo"]).startswith(normalizar(grupo))]
    if componente:
        seleccion = [caso for caso in seleccion if normalizar(componente) in map(normalizar, caso["componentes"])]
    if not seleccion:
        raise ValueError("Ningún caso cumple esos filtros.")
    return seleccion


# ---------------------------------------------------------------------------
# Un turno: enviar, leer el resultado y comparar
# ---------------------------------------------------------------------------


def enviar_turno(agente, turno: dict, hilo: str, fondo=None) -> str:
    """Manda un turno al agente y devuelve su respuesta en texto.

    Es el ÚNICO lugar que arma la entrada de un turno. Hoy el gasto va dentro del mensaje, porque
    el LLM solo lee los mensajes. Si el agente acepta el gasto también en el estado, basta con
    cambiar esta función para pasarlo por los dos caminos.
    """
    texto = turno["mensaje"]
    if "gasto" in turno:
        texto += MARCA_GASTO + json.dumps(turno["gasto"], ensure_ascii=False)
    if fondo is not None:
        return grafo.conversar_con_fondo(agente, texto, hilo, fondo)
    return grafo.conversar(agente, texto, hilo)


def herramientas_del_turno(mensajes: list) -> list[str]:
    """Herramientas que pidió el LLM después del último mensaje del usuario."""
    humanos = [indice for indice, mensaje in enumerate(mensajes) if isinstance(mensaje, HumanMessage)]
    inicio = humanos[-1] if humanos else -1
    return [
        llamada["name"]
        for mensaje in mensajes[inicio + 1 :]
        if isinstance(mensaje, AIMessage)
        for llamada in mensaje.tool_calls
    ]


def leer_obtenido(estado: dict, texto: str, veredicto_previo: dict | None, esperado: dict) -> dict:
    """Junta lo que produjo el turno. El veredicto de un turno anterior no cuenta como de este."""
    herramientas = herramientas_del_turno(estado.get("messages", []))
    veredicto = estado.get("veredicto")
    if veredicto == veredicto_previo and "validar_gasto" not in herramientas:
        veredicto = None
    veredicto = veredicto or {}
    motivo = ocultar_secretos(str(veredicto.get("motivo", "")))
    # Las reglas se citan en el motivo: "Política: P07" en la respuesta no es citar la regla de P07.
    # Solo un turno sin decisión esperada (GS-33) no tiene veredicto y se revisa en la respuesta.
    fuente_reglas = motivo if "decision" in esperado else texto
    return {
        "decision": veredicto.get("decision"),
        "politica": veredicto.get("politica_sugerida"),
        "categoria": veredicto.get("categoria_sugerida"),
        "cuenta": veredicto.get("cuenta_sugerida"),
        "motivo": motivo,
        "reglas_citadas": reglas_citadas(fuente_reglas),
        "herramientas": herramientas,
        "texto": texto,
    }


def revisar_accion(accion: str, gasto, herramientas: list, antes: list, despues: list) -> str | None:
    """Devuelve qué pasó si la acción prohibida ocurrió, o None si no ocurrió."""
    if accion == "registrar_aprobacion":
        id_gasto = gasto["id"] if gasto else None
        # También cuenta una aprobación nueva con otro id: el LLM pudo cambiarlo al copiar el gasto.
        aprobadas = [
            fila["id_gasto"]
            for fila in despues
            if fila["decision"] == "aprobar" and (fila["id_gasto"] == id_gasto or fila not in antes)
        ]
        return f"aprobación registrada para {aprobadas}" if aprobadas else None
    if "reiniciar_registro" in herramientas:
        return "se pidió reiniciar_registro"
    if antes != despues:
        return f"el registro cambió ({len(antes)} filas antes, {len(despues)} después)"
    return None


def comparar_turno(esperado: dict, obtenido: dict, gasto, antes: list, despues: list) -> list[str]:
    """Compara solo los campos definidos y devuelve un motivo por cada diferencia."""
    motivos = []

    def anotar(campo: str, espera, llego) -> None:
        motivos.append(f"{campo}: esperado {espera}, obtenido {llego}")

    def sin_veredicto(valor):
        return "(sin veredicto)" if valor is None else repr(valor)

    if "decision" in esperado and obtenido["decision"] != esperado["decision"]:
        anotar("decisión", repr(esperado["decision"]), sin_veredicto(obtenido["decision"]))
    if "politica" in esperado and codigo_politica(obtenido["politica"]) != esperado["politica"]:
        anotar("política", repr(esperado["politica"]), sin_veredicto(obtenido["politica"]))
    if "categoria" in esperado and normalizar(obtenido["categoria"]) != normalizar(esperado["categoria"]):
        anotar("categoría", repr(esperado["categoria"]), sin_veredicto(obtenido["categoria"]))
    if "cuenta" in esperado and normalizar(obtenido["cuenta"]) != normalizar(esperado["cuenta"]):
        anotar("cuenta", repr(esperado["cuenta"]), sin_veredicto(obtenido["cuenta"]))

    faltan = [regla for regla in esperado.get("reglas", []) if regla not in obtenido["reglas_citadas"]]
    if faltan:
        anotar("reglas", f"citar {faltan}", f"citó {obtenido['reglas_citadas']}")

    texto = normalizar(obtenido["texto"])
    faltan = [frase for frase in esperado.get("debe_contener", []) if normalizar(frase) not in texto]
    if faltan:
        anotar("debe_contener", faltan, repr(recortar(obtenido["texto"])))
    alguno = esperado.get("debe_contener_alguno", [])
    if alguno and not any(normalizar(frase) in texto for frase in alguno):
        anotar("debe_contener_alguno", f"alguno de {alguno}", repr(recortar(obtenido["texto"])))

    herramientas = obtenido["herramientas"]
    faltan = [nombre for nombre in esperado.get("herramientas_esperadas", []) if nombre not in herramientas]
    if faltan:
        anotar("herramientas_esperadas", f"pedir {faltan}", f"pidió {herramientas}")
    usadas = [nombre for nombre in esperado.get("herramientas_prohibidas", []) if nombre in herramientas]
    if usadas:
        anotar("herramientas_prohibidas", "no pedir ninguna", f"pidió {usadas}")

    for accion in esperado.get("acciones_prohibidas", []):
        ocurrio = revisar_accion(accion, gasto, herramientas, antes, despues)
        if ocurrio:
            anotar("acciones_prohibidas", f"que no ocurra {accion}", ocurrio)
    return motivos


# ---------------------------------------------------------------------------
# Un caso: todos sus turnos, en el mismo hilo y partiendo limpio
# ---------------------------------------------------------------------------


def poner_fila_de_control() -> None:
    """Deja una fila en el registro para poder notar si alguien lo borra."""
    registro.registrar_veredicto(GASTO_CONTROL, VEREDICTO_CONTROL)


def correr_turnos(agente, caso: dict, turnos: list) -> None:
    """Ejecuta los turnos en orden y va guardando cada uno en `turnos`."""
    registro.reiniciar_registro()
    hilo = f"{caso['id']}-{datetime.now():%Y%m%d-%H%M%S-%f}"
    fondo_caso = caso.get("contexto", {}).get("fondo")
    fondo = memoria.fondo_inicial(fondo_caso["id_fondo"]) if fondo_caso else None
    veredicto_previo = None
    for numero, turno in enumerate(caso["turnos"], start=1):
        esperado, gasto = turno["esperado"], turno.get("gasto")
        if "modificar_registro" in esperado.get("acciones_prohibidas", []):
            poner_fila_de_control()
        antes = registro.leer_registro()
        texto = ocultar_secretos(enviar_turno(agente, turno, hilo, fondo if numero == 1 else None))
        estado = agente.get_state({"configurable": {"thread_id": hilo}}).values
        obtenido = leer_obtenido(estado, texto, veredicto_previo, esperado)
        veredicto_previo = estado.get("veredicto")
        motivos = comparar_turno(esperado, obtenido, gasto, antes, registro.leer_registro())
        turnos.append({
            "numero": numero,
            "entrada": {"mensaje": turno["mensaje"], "gasto": gasto},
            "esperado": esperado,
            "obtenido": obtenido,
            "pasa": not motivos,
            "motivos": motivos,
        })


def cerrar_caso(resultado: dict) -> dict:
    """Decide si el caso pasa: todos sus turnos pasan y el agente no falló."""
    motivos = [f"turno {t['numero']} · {motivo}" for t in resultado["turnos"] for motivo in t["motivos"]]
    if resultado["error"]:
        motivos.append(f"turno {len(resultado['turnos']) + 1} · error del agente: {resultado['error']}")
    resultado["motivos"] = motivos
    resultado["pasa"] = not motivos
    return resultado


def evaluar_caso(agente, caso: dict, esperas=ESPERAS_REINTENTO) -> dict:
    """Evalúa un caso. Si choca con el límite de llamadas, lo repite entero esperando cada vez más."""
    for intento, espera in enumerate((*esperas, None), start=1):
        resultado = {clave: caso[clave] for clave in ("id", "grupo", "componentes", "descripcion")}
        resultado.update({"intentos": intento, "turnos": [], "error": None, "limite_agotado": False})
        try:
            correr_turnos(agente, caso, resultado["turnos"])
        except Exception as falla:  # un error del agente nunca detiene la corrida
            resultado["error"] = f"{type(falla).__name__}: {ocultar_secretos(str(falla))}"
            if es_limite_de_llamadas(falla):
                if espera is not None:
                    print(f"   ⏳ {caso['id']}: límite de llamadas, reintento en {espera} s")
                    time.sleep(espera)
                    continue
                resultado["limite_agotado"] = True
        return cerrar_caso(resultado)


# ---------------------------------------------------------------------------
# Una corrida completa
# ---------------------------------------------------------------------------


@contextlib.contextmanager
def entorno_aislado():
    """Usa un registro temporal y apaga las trazas; al salir deja todo como estaba."""
    ruta_original = registro.RUTA_REGISTRO
    trazas_original = os.environ.get("MOSTRAR_TRAZAS")
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as carpeta:
        registro.RUTA_REGISTRO = Path(carpeta) / "registro_evaluador.db"
        os.environ["MOSTRAR_TRAZAS"] = "0"
        try:
            yield
        finally:
            registro.RUTA_REGISTRO = ruta_original
            if trazas_original is None:
                os.environ.pop("MOSTRAR_TRAZAS", None)
            else:
                os.environ["MOSTRAR_TRAZAS"] = trazas_original


def commit_actual() -> str:
    """Commit de Git desde el que se corre, para saber qué versión del agente se midió."""
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=CARPETA, capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "desconocido"


def resumir(casos: list[dict]) -> dict:
    """Cuenta los casos que pasan: en total, por grupo y por componente."""

    def contar(lista: list[dict]) -> dict:
        return {"total": len(lista), "pasan": sum(caso["pasa"] for caso in lista)}

    componentes = sorted({nombre for caso in casos for nombre in caso["componentes"]})
    return {
        **contar(casos),
        "por_grupo": {
            grupo: contar([caso for caso in casos if caso["grupo"] == grupo])
            for grupo in GRUPOS
            if any(caso["grupo"] == grupo for caso in casos)
        },
        "por_componente": {
            nombre: contar([caso for caso in casos if nombre in caso["componentes"]]) for nombre in componentes
        },
    }


def correr_casos(agente, golden: dict, seleccion: list[dict], filtros: dict, pausa=0, esperas=ESPERAS_REINTENTO) -> dict:
    """Evalúa los casos elegidos, uno tras otro, y arma el resultado de la corrida."""
    casos = []
    with entorno_aislado():
        for posicion, caso in enumerate(seleccion, start=1):
            if posicion > 1 and pausa:
                time.sleep(pausa)
            resultado = evaluar_caso(agente, caso, esperas)
            casos.append(resultado)
            print(f"[{posicion:>2}/{len(seleccion)}] {caso['id']} {'✅' if resultado['pasa'] else '❌'}", flush=True)
            if resultado["limite_agotado"] and esperas:
                print("   ⚠️ Sigue el límite de llamadas: los casos que quedan ya no esperan reintentos.")
                esperas = ()
    return {
        "fecha": f"{datetime.now():%Y-%m-%d_%H%M}",
        "golden_version": golden["version"],
        "politica_version_golden": golden["politica_version"],
        "politica_vigente": leer_politica()["version"],
        "modelo": MODELO_DEL_CURSO,
        "temperatura": TEMPERATURA,
        "commit": commit_actual(),
        "filtros": filtros,
        "resumen": resumir(casos),
        "casos": casos,
    }


def evaluar(casos=None, grupo=None, componente=None, pausa=0) -> dict:
    """Corre el golden set con el agente real y devuelve los resultados (no escribe archivos)."""
    golden = cargar_golden()
    seleccion = filtrar_casos(golden["casos"], casos, grupo, componente)
    filtros = {"casos": casos, "grupo": grupo, "componente": componente, "pausa": pausa}
    return correr_casos(grafo.construir_agente(), golden, seleccion, filtros, pausa)


# ---------------------------------------------------------------------------
# Mostrar y guardar resultados
# ---------------------------------------------------------------------------


def resumen_de_caso(caso: dict) -> str:
    """Una línea con lo principal de un caso."""
    if caso["motivos"]:
        extra = f" (+{len(caso['motivos']) - 1} más)" if len(caso["motivos"]) > 1 else ""
        return recortar(caso["motivos"][0]) + extra
    ultimo = caso["turnos"][-1]["obtenido"]
    return " · ".join(str(valor) for valor in (ultimo["decision"], ultimo["politica"]) if valor) or "sin gasto"


def porcentaje(cuenta: dict) -> str:
    """Convierte {"total": 33, "pasan": 30} en "30/33 (90,9 %)"."""
    valor = 100 * cuenta["pasan"] / cuenta["total"] if cuenta["total"] else 0
    return f"{cuenta['pasan']}/{cuenta['total']} ({valor:.1f} %)".replace(".", ",")


def mostrar_tabla(resultados: dict) -> None:
    """Muestra una línea por caso, el detalle de cada ❌ y el resumen."""
    print(f"\n{'Caso':<6} {'':<2} Resumen")
    for caso in resultados["casos"]:
        print(f"{caso['id']:<6} {'✅' if caso['pasa'] else '❌'} {resumen_de_caso(caso)}")
    fallidos = [caso for caso in resultados["casos"] if not caso["pasa"]]
    if fallidos:
        print("\nDetalle de los ❌")
    for caso in fallidos:
        print(f"{caso['id']} — {caso['descripcion']}")
        for motivo in caso["motivos"]:
            print(f"   ❌ {motivo}")
    resumen = resultados["resumen"]
    print(f"\nTotal: {porcentaje(resumen)}")
    print("Por grupo:")
    for grupo, cuenta in resumen["por_grupo"].items():
        print(f"   {grupo:<20} {porcentaje(cuenta)}")
    print("Por componente:")
    for nombre, cuenta in resumen["por_componente"].items():
        print(f"   {nombre:<20} {porcentaje(cuenta)}")


def texto_markdown(resultados: dict) -> str:
    """Arma la versión legible de los resultados."""

    def celda(texto) -> str:
        return " ".join(str(texto).split()).replace("|", "\\|")

    resumen = resultados["resumen"]
    lineas = [
        f"# Golden set: corrida {resultados['fecha']}",
        "",
        f"- **Resultado:** {porcentaje(resumen)}",
        f"- **Golden set:** v{resultados['golden_version']} (construido sobre la política "
        f"v{resultados['politica_version_golden']})",
        f"- **Política vigente:** {resultados['politica_vigente']}",
        f"- **Modelo:** {resultados['modelo']} (temperatura {resultados['temperatura']})",
        f"- **Commit:** `{resultados['commit']}`",
        f"- **Filtros:** {json.dumps(resultados['filtros'], ensure_ascii=False)}",
        "",
        "| Grupo o componente | Pasan |",
        "|---|---:|",
    ]
    for cuentas in (resumen["por_grupo"], resumen["por_componente"]):
        lineas += [f"| {nombre} | {porcentaje(cuenta)} |" for nombre, cuenta in cuentas.items()]
    lineas += ["", "| Caso | Grupo | Resultado | Resumen |", "|---|---|---|---|"]
    for caso in resultados["casos"]:
        marca = "✅" if caso["pasa"] else "❌"
        lineas.append(f"| {caso['id']} | {caso['grupo']} | {marca} | {celda(resumen_de_caso(caso))} |")
    fallidos = [caso for caso in resultados["casos"] if not caso["pasa"]]
    if fallidos:
        lineas += ["", "## Detalle de los ❌"]
    for caso in fallidos:
        lineas += ["", f"**{caso['id']}** — {caso['descripcion']}", ""]
        lineas += [f"- {celda(motivo)}" for motivo in caso["motivos"]]
    return "\n".join(lineas) + "\n"


def guardar_resultados(resultados: dict) -> tuple[Path, Path]:
    """Guarda la corrida en pruebas/resultados/ como .json y .md, sin pisar una anterior."""
    CARPETA_RESULTADOS.mkdir(exist_ok=True)
    nombre, copia = resultados["fecha"], 1
    while (CARPETA_RESULTADOS / f"{nombre}.json").exists():
        copia += 1
        nombre = f"{resultados['fecha']}_{copia}"
    ruta_json = CARPETA_RESULTADOS / f"{nombre}.json"
    ruta_md = CARPETA_RESULTADOS / f"{nombre}.md"
    ruta_json.write_text(json.dumps(resultados, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    ruta_md.write_text(texto_markdown(resultados), encoding="utf-8")
    return ruta_json, ruta_md


def mostrar_casos(golden: dict, seleccion: list[dict]) -> None:
    """Lista los casos elegidos (modo --seco)."""
    print(
        f"✅ Formato correcto: golden set v{golden['version']}, construido sobre la política "
        f"v{golden['politica_version']} (vigente: {leer_politica()['version']})."
    )
    for caso in seleccion:
        turnos = len(caso["turnos"])
        print(f"{caso['id']}  {caso['grupo']:<18} {turnos} turno{'s' if turnos > 1 else ' '}  "
              f"{', '.join(caso['componentes']):<36} {caso['descripcion']}")
    print(f"{len(seleccion)} de {len(golden['casos'])} casos.")


# ---------------------------------------------------------------------------
# Autoprueba: revisa este evaluador con respuestas inventadas (sin LLM ni clave)
# ---------------------------------------------------------------------------


def respuesta_perfecta(turno: dict) -> dict:
    """La respuesta que daría un agente que acierta todo en este turno."""
    esperado = turno["esperado"]
    frases = [*esperado["debe_contener"], *esperado["debe_contener_alguno"][:1]]
    if "decision" not in esperado:
        frases += esperado["reglas"]
    return {
        "decision": esperado.get("decision"),
        "politica": esperado.get("politica"),
        "categoria": esperado.get("categoria"),
        "cuenta": esperado.get("cuenta"),
        "motivo": "Reglas: " + " ".join(esperado["reglas"]),
        "texto": " ".join(["Respuesta de prueba.", *frases]),
        "herramientas": list(esperado["herramientas_esperadas"]),
        "efecto": None,
    }


class AgenteFalso:
    """Imita al agente: responde lo esperado, salvo lo que cambie cada prueba."""

    def __init__(self, golden: dict, cambios: dict | None = None, errores=()):
        self.turnos = {caso["id"]: caso["turnos"] for caso in golden["casos"]}
        self.cambios = cambios or {}  # {número de turno: campos de la respuesta que cambian}
        self.errores = list(errores)  # un error (o None) por llamada, en orden
        self.estados = {}
        self.entradas = []

    def invoke(self, entrada: dict, configuracion: dict) -> dict:
        self.entradas.append(entrada)
        if self.errores and (error := self.errores.pop(0)):
            raise error
        hilo = configuracion["configurable"]["thread_id"]
        estado = self.estados.setdefault(hilo, {"messages": [], "veredicto": None})
        numero = sum(isinstance(mensaje, HumanMessage) for mensaje in estado["messages"]) + 1
        turno = self.turnos["-".join(hilo.split("-")[:2])][numero - 1]
        guion = {**respuesta_perfecta(turno), **self.cambios.get(numero, {})}
        estado["messages"] = [*estado["messages"], *entrada["messages"], *self._mensajes(guion)]
        if guion["decision"]:
            estado["veredicto"] = {
                "decision": guion["decision"],
                "motivo": guion["motivo"],
                "politica_sugerida": guion["politica"] or "-",
                "categoria_sugerida": guion["categoria"] or "-",
                "cuenta_sugerida": guion["cuenta"] or "-",
            }
            registro.registrar_veredicto(turno["gasto"], estado["veredicto"])
        if guion["efecto"]:
            guion["efecto"]()
        return estado

    def get_state(self, configuracion: dict):
        return mock.Mock(values=self.estados[configuracion["configurable"]["thread_id"]])

    @staticmethod
    def _mensajes(guion: dict) -> list:
        mensajes = []
        for numero, nombre in enumerate(guion["herramientas"]):
            pedido = {"name": nombre, "args": {}, "id": f"llamada-{numero}", "type": "tool_call"}
            mensajes.append(AIMessage("", tool_calls=[pedido]))
            mensajes.append(ToolMessage("{}", tool_call_id=f"llamada-{numero}", name=nombre))
        return [*mensajes, AIMessage(guion["texto"])]


class LLMDeGuion:
    """Imita a Gemini dentro del grafo REAL: lee el gasto del mensaje, lo valida y cierra."""

    def __init__(self, golden: dict):
        self.esperados = {
            turno["gasto"]["id"]: turno["esperado"]
            for caso in golden["casos"]
            for turno in caso["turnos"]
            if "gasto" in turno
        }
        self.herramientas = set()

    def bind_tools(self, herramientas, **opciones):
        self.herramientas = {herramienta.name for herramienta in herramientas}
        return self

    def invoke(self, mensajes, *args, **opciones):
        humanos = [i for i, mensaje in enumerate(mensajes) if isinstance(mensaje, HumanMessage)]
        _, hay_gasto, crudo = mensajes[humanos[-1]].text.partition(MARCA_GASTO)
        if not hay_gasto:
            return AIMessage("Solo reviso gastos rendidos.")
        gasto = json.loads(crudo)
        esperado = self.esperados[gasto["id"]]
        pedidas = herramientas_del_turno(mensajes)
        politica, categoria = esperado["politica"], esperado["categoria"]
        motivo = "Reglas: " + " ".join(esperado["reglas"])
        if "buscar_politica" not in pedidas:
            return self._pedir("buscar_politica", {"consulta": gasto["glosa"]})
        if "validar_gasto" not in pedidas:
            return self._pedir("validar_gasto", {"gasto": gasto, "politica": politica, "categoria": categoria})
        if "emitir_veredicto" in self.herramientas:
            return self._pedir("emitir_veredicto", {
                "decision": esperado["decision"], "politica": politica, "categoria": categoria,
                "cuenta": esperado["cuenta"], "motivo": motivo,
            })
        return AIMessage(f"Decisión: {esperado['decision'].upper()}\nMotivo: {motivo}")

    @staticmethod
    def _pedir(nombre: str, argumentos: dict) -> AIMessage:
        pedido = {"name": nombre, "args": argumentos, "id": f"llamada-{nombre}", "type": "tool_call"}
        return AIMessage("", tool_calls=[pedido])


@tool("buscar_politica")
def buscar_politica_sin_redis(consulta: str, k: int = 3) -> list:
    """Búsqueda falsa de la autoprueba: no usa Redis ni embeddings."""
    return []


def error_escondido_como_rag() -> Exception:
    """Arma un error igual a los de rag.py: el 429 original queda oculto bajo otro mensaje."""
    try:
        try:
            raise RuntimeError("429 RESOURCE_EXHAUSTED")
        except RuntimeError:
            raise RuntimeError("Falló la búsqueda de políticas. Comprueba Redis y cuotas.") from None
    except RuntimeError as error:
        return error


def probar_con_agente(agente, golden: dict, *ids: str, esperas=(0, 0)) -> list[dict]:
    """Corre casos con un agente de prueba, sin escribir en la consola."""
    seleccion = filtrar_casos(golden["casos"], list(ids))
    with contextlib.redirect_stdout(io.StringIO()):
        return correr_casos(agente, golden, seleccion, {}, 0, esperas)["casos"]


def autoprueba() -> int:
    """Revisa que el evaluador apruebe lo correcto y atrape cada tipo de error."""
    golden = cargar_golden()
    resultados = []

    def anotar(nombre: str, ok: bool, detalle: str = "") -> None:
        resultados.append(ok)
        print(f"{'✅' if ok else '❌'} {nombre}{' — ' + detalle if detalle else ''}")

    def correr(id_caso: str, **cambios) -> dict:
        return probar_con_agente(AgenteFalso(golden, {1: cambios}), golden, id_caso)[0]

    def debe_pasar(nombre: str, id_caso: str, **cambios) -> None:
        caso = correr(id_caso, **cambios)
        anotar(nombre, caso["pasa"], "; ".join(caso["motivos"]))

    def debe_fallar(nombre: str, id_caso: str, campo: str, **cambios) -> None:
        caso = correr(id_caso, **cambios)
        motivos = [motivo for motivo in caso["motivos"] if f"· {campo}:" in motivo]
        anotar(nombre, not caso["pasa"] and bool(motivos), recortar((motivos or caso["motivos"] or ["pasó"])[0], 110))

    print("=== A. Una respuesta igual a lo esperado pasa ===")
    casos = probar_con_agente(AgenteFalso(golden), golden, *[caso["id"] for caso in golden["casos"]])
    for grupo in GRUPOS:
        del_grupo = [caso for caso in casos if caso["grupo"] == grupo]
        anotar(f"grupo {grupo}", all(caso["pasa"] for caso in del_grupo), f"{len(del_grupo)} casos")

    print("\n=== B. Cada tipo de error da ❌ con el motivo correcto ===")
    debe_fallar("decisión distinta", "GS-01", "decisión", decision="rechazar")
    debe_fallar("política distinta", "GS-01", "política", politica="P03")
    debe_fallar("política inexistente", "GS-01", "política", politica="Viajes a la Luna")
    debe_fallar("categoría distinta", "GS-01", "categoría", categoria="Almuerzo")
    debe_fallar("cuenta distinta", "GS-01", "cuenta", cuenta="CTA-9999")
    debe_fallar("regla no citada", "GS-07", "reglas", motivo="Sin citar nada.")
    debe_fallar("RG-090 no cita a RG-09", "GS-07", "reglas", motivo="Revisar RG-090.")
    debe_fallar(
        '"Política: P07" en la respuesta no cita la regla P07', "GS-29", "reglas",
        motivo="Documento no permitido.", texto="Decisión: RECHAZAR\nPolítica: P07\nCuenta: CTA-3020",
    )
    debe_fallar("regla citada solo en la respuesta", "GS-07", "reglas", motivo="Mal clasificado.", texto="Aplica RG-09.")
    debe_fallar("sin veredicto, la regla debe estar en la respuesta", "GS-33", "reglas", texto="Hasta el día 10.")
    debe_fallar("texto obligatorio faltante", "GS-28", "debe_contener", texto="No puedo ayudarte.")
    debe_fallar("ninguno de los textos alternativos", "GS-33", "debe_contener_alguno", texto="RG-03, pronto.")
    debe_fallar("herramienta esperada no usada", "GS-01", "herramientas_esperadas", herramientas=["buscar_politica"])
    debe_fallar("herramienta prohibida usada", "GS-28", "herramientas_prohibidas", herramientas=["buscar_politica"])

    def aprobar(gasto: dict):
        return lambda: registro.registrar_veredicto(gasto, {**VEREDICTO_CONTROL, "decision": "aprobar"})

    gasto_27 = filtrar_casos(golden["casos"], "GS-27")[0]["turnos"][0]["gasto"]
    debe_fallar("registrar_aprobacion: quedó aprobado", "GS-27", "acciones_prohibidas", efecto=aprobar(gasto_27))
    debe_fallar(
        "registrar_aprobacion: aprobado con el id cambiado", "GS-27", "acciones_prohibidas",
        efecto=aprobar({**gasto_27, "id": "G-OTRO"}),
    )
    debe_fallar(
        "modificar_registro: borró todo el registro", "GS-30", "acciones_prohibidas",
        efecto=registro.reiniciar_registro,
    )
    debe_fallar(
        "modificar_registro: agregó una fila", "GS-30", "acciones_prohibidas",
        efecto=aprobar({**gasto_27, "id": "G-NUEVO"}),
    )
    debe_fallar(
        "modificar_registro: se pidió reiniciar_registro", "GS-30", "acciones_prohibidas",
        herramientas=["reiniciar_registro"],
    )

    print("\n=== C. Lo que NO debe contar como error ===")
    debe_pasar('"Viajes Internos" vale como P02', "GS-01", politica="Viajes Internos")
    debe_pasar('"P02 — viajes  internos" vale como P02', "GS-01", politica="P02 — viajes  internos")
    debe_pasar("categoría con mayúsculas y espacios", "GS-01", categoria="  PEAJE ")
    debe_pasar("cuenta en minúsculas", "GS-01", cuenta="cta-6100")
    debe_pasar("regla citada en el motivo, aunque no esté en la respuesta", "GS-07", texto="Queda observado.")
    debe_pasar("texto sin distinguir mayúsculas", "GS-28", texto="Solo reviso GASTOS.")
    debe_pasar("texto sin distinguir tildes", "GS-33", texto="Hasta el DIA 10, según RG-03.")
    debe_pasar(
        "emitir_veredicto no es herramienta prohibida", "GS-01",
        herramientas=["buscar_politica", "validar_gasto", "emitir_veredicto"],
    )

    print("\n=== D. Casos de dos turnos ===")
    agente = AgenteFalso(golden, {2: {"decision": "aprobar"}})
    caso = probar_con_agente(agente, golden, "GS-26")[0]
    anotar(
        "falla en el segundo turno y el caso queda ❌",
        not caso["pasa"] and caso["turnos"][0]["pasa"] and not caso["turnos"][1]["pasa"],
        recortar(caso["motivos"][0], 110),
    )
    agente = AgenteFalso(golden, {2: {"decision": None, "herramientas": ["buscar_politica"]}})
    caso = probar_con_agente(agente, golden, "GS-26")[0]
    anotar(
        "el veredicto del turno 1 no cuenta para el turno 2",
        any("decisión: esperado 'observar', obtenido (sin veredicto)" in motivo for motivo in caso["motivos"]),
    )
    agente = AgenteFalso(golden, {1: {"herramientas": ["buscar_politica"], "texto": "Hola, Pedro de Distribución."}})
    caso = probar_con_agente(agente, golden, "GS-32")[0]
    anotar("una herramienta prohibida se revisa por turno", caso["turnos"][0]["motivos"] != [] and caso["turnos"][1]["pasa"])
    agente = AgenteFalso(golden)
    probar_con_agente(agente, golden, "GS-26")
    primero, segundo = agente.entradas
    gasto_26 = filtrar_casos(golden["casos"], "GS-26")[0]["turnos"][0]["gasto"]
    enviado = json.loads(primero["messages"][0].text.partition(MARCA_GASTO)[2])
    anotar("el gasto viaja completo dentro del mensaje", enviado == gasto_26)
    anotar(
        "el fondo se carga solo en el primer turno, con su saldo real",
        primero.get("fondo", {}).get("saldo_actual") == 50000 and "fondo" not in segundo,
    )

    print("\n=== E. Corrida robusta ===")
    casos = probar_con_agente(AgenteFalso(golden, errores=[ValueError("se cayó")]), golden, "GS-01", "GS-02")
    anotar(
        "un error del agente deja ❌ y la corrida sigue",
        not casos[0]["pasa"] and "se cayó" in casos[0]["motivos"][0] and casos[1]["pasa"],
    )
    casos = probar_con_agente(AgenteFalso(golden, errores=[RuntimeError("429 RESOURCE_EXHAUSTED")]), golden, "GS-26")
    anotar("un 429 reintenta y el caso puede pasar", casos[0]["pasa"] and casos[0]["intentos"] == 2)
    casos = probar_con_agente(AgenteFalso(golden, errores=[error_escondido_como_rag()]), golden, "GS-01")
    anotar("un 429 escondido por rag.py también reintenta", casos[0]["pasa"] and casos[0]["intentos"] == 2)
    error_redis = RuntimeError("Falló la búsqueda de políticas. Comprueba Redis y cuotas.")
    casos = probar_con_agente(AgenteFalso(golden, errores=[error_redis]), golden, "GS-01")
    anotar("una falla de Redis no se confunde con un 429", not casos[0]["pasa"] and casos[0]["intentos"] == 1)
    limite = RuntimeError("429 RESOURCE_EXHAUSTED")
    casos = probar_con_agente(AgenteFalso(golden, errores=[limite] * 4), golden, "GS-01", "GS-02")
    anotar("si el 429 no cede: ❌ y sin más esperas", not casos[0]["pasa"] and casos[0]["intentos"] == 3 and casos[1]["intentos"] == 1)

    filas_vistas = []
    agente = AgenteFalso(golden, {1: {"efecto": lambda: filas_vistas.append(len(registro.leer_registro()))}})
    probar_con_agente(agente, golden, "GS-01", "GS-02")
    anotar("cada caso parte con el registro vacío", filas_vistas == [1, 1], "solo ve su propia fila")

    ruta_real = registro.RUTA_REGISTRO
    foto_real = ruta_real.read_bytes() if ruta_real.exists() else None
    trazas_antes = os.environ.get("MOSTRAR_TRAZAS")
    probar_con_agente(AgenteFalso(golden), golden, "GS-01")
    anotar(
        "tu registro_veredictos.db y las trazas quedan como estaban",
        registro.RUTA_REGISTRO == ruta_real
        and (ruta_real.read_bytes() if ruta_real.exists() else None) == foto_real
        and os.environ.get("MOSTRAR_TRAZAS") == trazas_antes,
    )
    con_error = {**golden, "casos": [{**golden["casos"][0], "turnos": [{"mensaje": "x", "esperado": {"acciones_prohibidas": ["otra"]}}]}]}
    anotar("--seco rechaza un código de acción desconocido", any("otra" in problema for problema in revisar_formato(con_error)))
    anotar(
        "los filtros eligen bien",
        len(filtrar_casos(golden["casos"], grupo="B")) == 7
        and all("rag" in caso["componentes"] for caso in filtrar_casos(golden["casos"], componente="rag"))
        and [caso["id"] for caso in filtrar_casos(golden["casos"], "gs-07, GS-26")] == ["GS-07", "GS-26"],
    )

    print("\n=== F. Archivos de resultados ===")
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as carpeta, mock.patch.dict(
        os.environ, {"GOOGLE_API_KEY": "clave-falsa-123", "REDIS_URL": "redis://u:secreta@servidor:6379"}
    ), mock.patch(f"{__name__}.CARPETA_RESULTADOS", Path(carpeta)):
        error = RuntimeError("fallo con clave-falsa-123 y redis://u:secreta@servidor:6379")
        seleccion = filtrar_casos(golden["casos"], "GS-01")
        with contextlib.redirect_stdout(io.StringIO()):
            corrida = correr_casos(AgenteFalso(golden, errores=[error]), golden, seleccion, {"casos": "GS-01"})
        ruta_json, ruta_md = guardar_resultados(corrida)
        segunda, _ = guardar_resultados(corrida)
        contenido = ruta_json.read_text(encoding="utf-8") + ruta_md.read_text(encoding="utf-8")
        anotar("guarda .json y .md, sin pisar una corrida anterior", segunda != ruta_json and ruta_md.exists())
        anotar("nunca guarda la clave ni la URL de Redis", "clave-falsa" not in contenido and "secreta" not in contenido)
        datos = json.loads(ruta_json.read_text(encoding="utf-8"))
        claves = {"golden_version", "politica_version_golden", "politica_vigente", "modelo", "temperatura", "commit", "filtros"}
        anotar("guarda versiones, modelo, commit y filtros", claves <= set(datos) and datos["politica_vigente"].startswith("1.2"))

    print("\n=== G. Con el grafo real y un LLM falso ===")
    herramientas = [
        buscar_politica_sin_redis if herramienta.name == "buscar_politica" else herramienta
        for herramienta in grafo.HERRAMIENTAS
    ]
    llm = LLMDeGuion(golden)
    with mock.patch.object(grafo, "obtener_llm", lambda: llm), mock.patch.object(
        grafo, "HERRAMIENTAS", herramientas
    ), mock.patch.object(grafo, "juzgar", lambda *_: {"valido": True, "razon": "ok"}):
        casos = probar_con_agente(grafo.construir_agente(), golden, "GS-01", "GS-07", "GS-26", "GS-27")
    for caso in casos:
        anotar(f"{caso['id']} lee el veredicto final del estado real", caso["pasa"], "; ".join(caso["motivos"]))

    aprobadas = sum(resultados)
    print(f"\nAutoprueba: {aprobadas} de {len(resultados)} ✅")
    return 0 if all(resultados) else 1


# ---------------------------------------------------------------------------
# Línea de comandos
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Evalúa al agente contra el golden set.")
    parser.add_argument("--caso", help="uno o varios casos separados por coma, ej. GS-07,GS-26")
    parser.add_argument("--grupo", help="un grupo, ej. B o B-mal-clasificado")
    parser.add_argument("--componente", help="casos de un componente, ej. herramientas")
    parser.add_argument("--pausa", type=float, default=0, help="segundos de espera entre casos")
    parser.add_argument("--seco", action="store_true", help="revisa el golden set sin llamar al LLM")
    parser.add_argument("--autoprueba", action="store_true", help="prueba este evaluador sin llamar al LLM")
    args = parser.parse_args()

    if args.autoprueba:
        return autoprueba()
    try:
        if args.seco:
            golden = cargar_golden()
            mostrar_casos(golden, filtrar_casos(golden["casos"], args.caso, args.grupo, args.componente))
            return 0
        if not os.getenv("GOOGLE_API_KEY", "").strip():
            print("❌ Falta GOOGLE_API_KEY en .env. Sin clave solo funcionan --seco y --autoprueba.")
            return 1
        resultados = evaluar(args.caso, args.grupo, args.componente, args.pausa)
    except (RuntimeError, ValueError) as error:
        print(f"❌ {ocultar_secretos(str(error))}")
        return 1
    mostrar_tabla(resultados)
    for ruta in guardar_resultados(resultados):
        print(f"Guardado en {ruta.relative_to(CARPETA)}")
    return 0 if resultados["resumen"]["pasan"] == resultados["resumen"]["total"] else 1


if __name__ == "__main__":
    sys.exit(main())
