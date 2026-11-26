"""Captura RAG y GraphRAG por la API principal autorizada. Solo biblioteca estándar."""

import argparse
import getpass
import json
import re
import time
import warnings
from datetime import datetime, timezone
from http.client import HTTPException
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener
from uuid import uuid4

ESTADOS = {"ok", "bloqueado", "fallback", "error"}
RUTAS = {"consulta_politica", "revisar_gasto", "fuera_de_alcance", "sin_ruta"}
UUID4 = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}", re.I)
SENSIBLE = re.compile(
    r"\b(?:bearer|basic)\s+\S+|\b(?:AIza[\w-]{20,}|eyJ[\w-]+\.[\w-]+\.[\w-]+"
    r"|(?:gh[pousr]_|github_pat_|sk-)[\w-]{16,})\b|-----BEGIN [A-Z ]*PRIVATE KEY"
    r"|://[^/\s]*@|[?&][\w-]+=|[\{\[]\s*[\"'{\[]"
    r"|\b\w*(?:api[_ -]?key|authorization|token|secret|password|contraseña|"
    r"credentials?|credenciales|(?:database|redis)_url|datos_base64|payload|request[_ -]?body)"
    r"(?:[_-]\w+)?\s*[\"']?\s*[:=]",
    re.I,
)
CASOS = (
    ("ampliacion-rag", "¿Cuál es el tope de hotel para un viaje interno entre sedes (P02)?",
     "P02", ("$445.000 CLP por documento",), ["buscar_politica"]),
    ("ampliacion-graphrag", "¿Cuál es el tope de hotel para Jefe de tienda en P03?",
     "P03", ("Jefe de tienda → Jefatura → P03:hotel", "$325.000 CLP",
             "propuesta organizacional ficticia, pendiente de aprobación"), ["tope_para", "buscar_politica"]),
)


class Fallo(RuntimeError):
    """Mensaje controlado, apto para la consola y la evidencia."""


class SinRedirecciones(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def origen(url):
    try:
        partes = urlsplit(url)
        host, puerto = partes.hostname, partes.port
        autoridad = f"[{host}]" if host and ":" in host else host or ""
        if puerto is not None:
            autoridad += f":{puerto}"
        if (host and puerto != 0 and partes.netloc.lower() == autoridad and
                re.fullmatch(r"[A-Za-z0-9.\-:\[\]/]+", url) and
                partes.path in ("", "/") and "?" not in url and "#" not in url and
                (partes.scheme == "https" or partes.scheme == "http" and
                 host in {"localhost", "127.0.0.1", "::1"})):
            return f"{partes.scheme}://{autoridad}"
    except ValueError:
        pass
    raise Fallo("Usa el origen HTTPS autorizado (HTTP solo en loopback), sin ruta ni credenciales.")


def uuid_valido(valor):
    return isinstance(valor, str) and bool(UUID4.fullmatch(valor))


def texto_seguro(valor, clave):
    if isinstance(valor, str):
        if len(valor) > 6000 or clave in valor or SENSIBLE.search(valor):
            return "[texto omitido por precaución]"
        return valor
    return None


def proyeccion(datos, clave, hilo):
    """Permitir solo campos del contrato; no copiar cuerpos, cabeceras ni verificaciones."""
    salida = {}
    if uuid_valido(datos.get("id_ejecucion")):
        salida["id_ejecucion"] = datos["id_ejecucion"]
    if datos.get("thread_id") == hilo:
        salida["thread_id"] = hilo
    for campo, validos in (("estado", ESTADOS | {"en_proceso"}), ("estado_final", ESTADOS), ("ruta", RUTAS)):
        valor = datos.get(campo)
        if isinstance(valor, str) and valor in validos:
            salida[campo] = valor
    for campo in ("pasos", "duracion_ms"):
        if type(datos.get(campo)) is int and datos[campo] >= 0:
            salida[campo] = datos[campo]
    if type(datos.get("hubo_a2a")) is bool:
        salida["hubo_a2a"] = datos["hubo_a2a"]
    herramientas = datos.get("herramientas_usadas")
    if isinstance(herramientas, list):
        salida["herramientas_usadas"] = [
            h if h in ("buscar_politica", "tope_para") else "[herramienta no esperada]"
            for h in herramientas[:16]
        ]
    for campo in ("fecha", "inicio", "fin"):
        valor = datos.get(campo)
        if isinstance(valor, str) and re.fullmatch(r"\d{4}-\d\d-\d\dT[0-9:.+Z-]{8,24}", valor):
            salida[campo] = valor
    for campo in ("respuesta", "detail"):
        if isinstance(datos.get(campo), str):
            salida[campo] = texto_seguro(datos[campo], clave)
    return salida


def consultar(http, base, ruta, limite, clave=None, cuerpo=None):
    restante = limite - time.monotonic()
    if restante <= 0:
        raise Fallo("Se agotó el plazo local; la ejecución del servidor podría seguir activa.")
    headers = {"Accept": "application/json"}
    datos = None
    if clave is not None:
        headers["X-API-Key"] = clave
    if cuerpo is not None:
        headers["Content-Type"] = "application/json"
        datos = json.dumps(cuerpo).encode("utf-8")
    request = Request(base + ruta, data=datos, headers=headers)
    try:
        try:
            respuesta = http.open(request, timeout=min(restante, 12))
        except HTTPError as error:
            respuesta = error
        with respuesta:
            codigo = respuesta.code
            if respuesta.headers.get_content_type() != "application/json":
                return codigo, {}
            buf = bytearray()
            while len(buf) <= 262144:
                if time.monotonic() >= limite:
                    raise Fallo("Se agotó el plazo local mientras se leía la respuesta.")
                bloque = respuesta.read1(8192)
                if not bloque:
                    objeto = json.loads(buf)
                    return codigo, objeto if isinstance(objeto, dict) else {}
                buf.extend(bloque)
            raise Fallo("Respuesta demasiado grande; no se conservó el cuerpo.")
    except (URLError, OSError, ValueError, HTTPException):
        raise Fallo("No se pudo obtener una respuesta JSON válida del origen autorizado.") from None


def ejecutar_caso(caso, health, http, base, clave, segundos):
    _, pregunta, politica, hechos, herramientas = caso
    inicio = time.monotonic()
    limite = inicio + segundos
    hilo = f"evidencia-{uuid4()}"
    entrada = {"thread_id": hilo, "texto": pregunta}  # Sin gasto, imagen, fondos ni veredictos.
    fuente = f"datos/politica_ficticia.md#{politica}"
    prueba = {"health": health, "entrada": entrada, "fuente_esperada": fuente,
              "herramientas_esperadas": herramientas, "consultas_seguimiento": 0, "resultado": "FAIL"}

    def leer(ruta, espera=200, **kwargs):
        codigo, recibido = consultar(http, base, ruta, limite, clave, **kwargs)
        etapa = "post" if ruta == "/chat" else "get_registro"
        prueba[f"http_{etapa}"] = codigo
        if codigo not in ((espera,) if isinstance(espera, int) else espera):
            prueba["error_servidor"] = proyeccion(recibido, clave, hilo)
            raise Fallo(f"HTTP {codigo} inesperado en {etapa}. No se reenviará el POST.")
        return codigo, recibido

    try:
        codigo, recibido = leer("/chat", (200, 202), cuerpo=entrada)
        prueba["aceptacion" if codigo == 202 else "respuesta"] = proyeccion(recibido, clave, hilo)
        id_ = recibido.get("id_ejecucion")
        if not uuid_valido(id_) or recibido.get("thread_id") != hilo:
            raise Fallo("POST sin UUIDv4 o thread_id válido.")
        prueba["id_ejecucion"] = id_
        ruta = f"/registro/{id_}"  # Nunca se sigue `consultar` ni una redirección.
        if codigo == 202:
            if recibido.get("estado") != "en_proceso":
                raise Fallo("HTTP 202 sin estado en_proceso.")
            while True:
                prueba["consultas_seguimiento"] += 1
                _, avance = leer(ruta)
                prueba["seguimiento"] = proyeccion(avance, clave, hilo)
                if avance.get("id_ejecucion") != id_ or ("thread_id" in avance and avance["thread_id"] != hilo):
                    raise Fallo("El registro no corresponde a la ejecución aceptada.")
                if avance.get("estado") != "en_proceso":
                    break
                if avance.get("thread_id") != hilo or avance.get("resultado", False) is not None:
                    raise Fallo("Progreso en_proceso incompatible con el contrato.")
                time.sleep(min(1.5, max(0, limite - time.monotonic())))
            recibido = avance.get("resultado")
            if not isinstance(recibido, dict):
                _, fila = leer(ruta)
                prueba["registro"] = proyeccion(fila, clave, hilo)
                raise Fallo("Sin respuesta completa; no se acredita esta consulta.")
            prueba["respuesta"] = proyeccion(recibido, clave, hilo)
            if avance.get("estado") != recibido.get("estado_final"):
                raise Fallo("El estado terminal no coincide con la respuesta.")

        _, fila = leer(ruta)
        prueba["registro"] = proyeccion(fila, clave, hilo)
        texto = prueba["respuesta"].get("respuesta") or ""
        controles = {
            "id_ejecucion": recibido.get("id_ejecucion") == fila.get("id_ejecucion") == id_,
            "thread_id": recibido.get("thread_id") == hilo and fila.get("thread_id", hilo) == hilo,
            "ruta": recibido.get("ruta") == fila.get("ruta") == "consulta_politica",
            "estado_final": recibido.get("estado_final") == fila.get("estado_final") == "ok",
            "herramientas": recibido.get("herramientas_usadas") == fila.get("herramientas_usadas") == herramientas,
            "fuente": f"[Fuente: {fuente}]" in texto,
            "respuesta": all(hecho in texto for hecho in hechos),
            "solo_consulta": recibido.get("hubo_a2a") is False and fila.get("hubo_a2a") is False
            and recibido.get("veredicto") is None,
            "fila_persistida": isinstance(prueba["registro"].get("fecha"), str)
            and type(fila.get("duracion_ms")) is int and fila["duracion_ms"] >= 0,
        }
        prueba["validaciones"] = controles
        if all(controles.values()):
            prueba["resultado"] = "PASS"
        else:
            raise Fallo("Uno o más controles no se cumplieron.")
    except Fallo as error:
        prueba["observacion"] = str(error)
    except KeyboardInterrupt:
        prueba["observacion"] = "Espera local interrumpida. No se canceló la ejecución en el servidor."
        prueba["interrumpida"] = True
    finally:
        prueba["duracion_cliente_s"] = round(time.monotonic() - inicio, 3)
    return prueba


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url_base", help="Origen autorizado del agente principal, sin ruta")
    parser.add_argument("--espera", type=int, choices=range(15, 601), metavar="15..600", default=105,
                        help="Plazo local por consulta; por defecto 105 s (90 + 15 de margen)")
    args = parser.parse_args()
    try:
        base = origen(args.url_base)
        http = build_opener(ProxyHandler({}), SinRedirecciones())
        codigo, salud = consultar(http, base, "/health", time.monotonic() + 12)
        if codigo != 200 or salud.get("ok") is not True:
            raise Fallo(f"/health no confirmó disponibilidad (HTTP {codigo}).")
        with warnings.catch_warnings():
            warnings.simplefilter("error", getpass.GetPassWarning)
            clave = getpass.getpass("API Key del principal (no se guarda): ").strip()
        if not clave or not re.fullmatch(r"[!-~]+", clave):
            raise Fallo("Falta una API Key válida.")
    except (Fallo, getpass.GetPassWarning, EOFError, OSError, KeyboardInterrupt) as error:
        print(str(error) if isinstance(error, Fallo) else "No se obtuvo una clave mediante una terminal protegida.")
        return 1

    raiz = Path(__file__).resolve().parents[1]
    sello = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    correcto = True
    for caso in CASOS:
        prueba = ejecutar_caso(caso, {"http": codigo, "ok": True}, http, base, clave, args.espera)
        prueba["captura_utc"] = datetime.now(timezone.utc).isoformat()
        destino = raiz / caso[0] / f"captura-{sello}.json"
        try:
            with destino.open("x", encoding="utf-8") as archivo:
                json.dump(prueba, archivo, ensure_ascii=False, indent=2)
                archivo.write("\n")
        except OSError:
            print(f"No se pudo guardar {caso[0]}/{destino.name}; no se sobrescriben archivos.")
            return 1
        print(f"{caso[0]}/{destino.name}: {prueba['resultado']}")
        correcto = correcto and prueba["resultado"] == "PASS"
        if prueba.get("interrumpida"):
            return 130
    return 0 if correcto else 1


if __name__ == "__main__":
    raise SystemExit(main())
