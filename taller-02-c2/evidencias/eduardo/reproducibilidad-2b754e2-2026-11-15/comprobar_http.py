"""Arranque y seis comprobaciones HTTP, sin preguntas al proveedor ni suites."""

import argparse
import asyncio
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import socket
import subprocess
import sys
import threading

import httpx


def fecha():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def guardar(ruta, datos):
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


async def comprobar(proyecto, destino, etiqueta):
    proyecto, destino = proyecto.resolve(), destino.resolve()
    clave, incorrecta = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    with socket.socket() as reserva:
        reserva.bind(("127.0.0.1", 0))
        puerto = reserva.getsockname()[1]
    base = f"http://127.0.0.1:{puerto}"
    entorno = os.environ.copy()
    for variable in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV", "GOOGLE_APPLICATION_CREDENTIALS"):
        entorno.pop(variable, None)
    entorno.update(PORT=str(puerto), PUERTO=str(puerto), URL_BASE=base, URLS_AGENTES="",
                   CLAVE_API=clave, GOOGLE_API_KEY="", GEMINI_API_KEY="",
                   GOOGLE_GENAI_USE_VERTEXAI="false", PYTHON_DOTENV_DISABLED="1",
                   PYTHONNOUSERSITE="1", PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1",
                   LANGSMITH_TRACING="false", LANGCHAIN_TRACING_V2="false",
                   LANGSMITH_API_KEY="", LANGCHAIN_API_KEY="", OTEL_SDK_DISABLED="true")
    argumentos = [sys.executable, "-B", "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", str(puerto)]
    datos = {"inicio": fecha(), "etiqueta": etiqueta,
             "python": sys.version, "puerto": puerto,
             "comando": f"<VENV_NUEVO>/Scripts/python.exe -B -m uvicorn app:app --host 127.0.0.1 --port {puerto}",
             "entorno_no_secreto": {n: entorno[n] for n in ("PORT", "PUERTO", "URL_BASE", "URLS_AGENTES", "PYTHON_DOTENV_DISABLED", "GOOGLE_GENAI_USE_VERTEXAI")},
             "proveedor": "Sin credenciales; solo GET y POST con texto vacío/espacios. No se consulta Gemini.",
             "clave": "Temporal aleatoria, solo en memoria y entorno del hijo; no se guarda su valor.",
             "casos": []}
    listo = threading.Event()
    lineas = []

    def registrar():
        with (destino / f"arranque-{etiqueta}.txt").open("w", encoding="utf-8") as archivo:
            for binaria in iter(proceso.stdout.readline, b""):
                linea = binaria.decode("utf-8", errors="replace")
                linea = linea.replace(clave, "<CLAVE_TEMPORAL>").replace(incorrecta, "<CLAVE_INCORRECTA>")
                linea = linea.replace(str(proyecto), "<COPIA>/taller-02-c2/proyecto")
                linea = linea.replace(str(Path.home()), "<USUARIO>")
                lineas.append(linea)
                archivo.write(linea)
                archivo.flush()
                if "Application startup complete." in linea:
                    listo.set()
        listo.set()

    proceso = subprocess.Popen(argumentos, cwd=proyecto, env=entorno,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    datos["pid_lanzador_propio"] = proceso.pid
    lector = threading.Thread(target=registrar, daemon=True)
    lector.start()
    try:
        await asyncio.to_thread(listo.wait, 60)
        datos["arranque_completo"] = any("Application startup complete." in l for l in lineas)
        if datos["arranque_completo"]:
            async with httpx.AsyncClient(base_url=base, timeout=10, trust_env=False) as cliente:
                salud = await cliente.get("/salud")
                datos["casos"].append({"caso": "salud", "metodo": "GET", "ruta": "/salud",
                                        "estado": salud.status_code, "cuerpo": salud.json(),
                                        "aprobado": salud.status_code == 200 and salud.json() == {"ok": True}})
                panel = await cliente.get("/")
                archivo_panel = proyecto / "src/comun/panel.html"
                coincide = hashlib.sha256(panel.content).hexdigest() == hashlib.sha256(archivo_panel.read_bytes()).hexdigest()
                datos["casos"].append({"caso": "panel_http", "metodo": "GET", "ruta": "/",
                                        "estado": panel.status_code, "tipo": panel.headers.get("content-type"),
                                        "titulo": re.search(r"<title>(.*?)</title>", panel.text, re.S).group(1),
                                        "cache_control": panel.headers.get("cache-control"),
                                        "html_identico_al_commit": coincide,
                                        "aprobado": panel.status_code == 200 and coincide})
                for nombre, cabecera, cuerpo, esperado, detalle in (
                    ("sin_clave", None, {"texto": "   "}, 401, "Falta la clave de acceso. Envíala en la cabecera X-API-Key."),
                    ("clave_incorrecta", incorrecta, {"texto": "   "}, 401, "La clave de acceso es incorrecta."),
                    ("vacio_autorizado", clave, {"texto": ""}, 400, "Escribe una pregunta para continuar."),
                    ("espacios_autorizados", clave, {"texto": "   "}, 400, "Escribe una pregunta para continuar."),
                ):
                    recibida = await cliente.post("/panel/consultar", json=cuerpo,
                                                  headers={"X-API-Key": cabecera} if cabecera else {})
                    datos["casos"].append({"caso": nombre, "metodo": "POST", "ruta": "/panel/consultar",
                                            "solicitud": cuerpo, "autorizacion": nombre,
                                            "esperado": esperado, "estado": recibida.status_code,
                                            "cuerpo": recibida.json(),
                                            "aprobado": recibida.status_code == esperado and recibida.json() == {"detail": detalle}})
        else:
            datos["casos_pendientes"] = ["salud", "panel_http", "sin_clave", "clave_incorrecta", "vacio_autorizado", "espacios_autorizados"]
    except Exception as error:
        datos["error_instrumental"] = type(error).__name__
    finally:
        if proceso.poll() is None:
            cierre = await asyncio.to_thread(subprocess.run, ["taskkill", "/PID", str(proceso.pid), "/T", "/F"],
                                             capture_output=True, timeout=15)
            datos["cierre_arbol_propio"] = cierre.returncode == 0
        proceso.wait(timeout=15)
        lector.join(timeout=10)
        datos["salida_proceso"] = proceso.returncode
        with socket.socket() as verificador:
            verificador.settimeout(2)
            datos["puerto_propio_cerrado"] = verificador.connect_ex(("127.0.0.1", puerto)) != 0
        registro = "".join(lineas)
        datos["preguntas_coordinador_en_log"] = registro.count("pregunta recibida")
        datos["envios_a2a_en_log"] = registro.count("A2A →")
        datos["fin"] = fecha()
        datos["aprobado"] = bool(datos.get("arranque_completo") and len(datos["casos"]) == 6
                                 and all(c["aprobado"] for c in datos["casos"]))
        guardar(destino / f"resultado-{etiqueta}.json", datos)
    print(json.dumps(datos, ensure_ascii=False, indent=2))
    return 0 if datos["aprobado"] else 1


if __name__ == "__main__":
    analizador = argparse.ArgumentParser()
    analizador.add_argument("--proyecto", type=Path, required=True)
    analizador.add_argument("--destino", type=Path, required=True)
    analizador.add_argument("--etiqueta", required=True)
    opciones = analizador.parse_args()
    opciones.destino.mkdir(parents=True, exist_ok=True)
    if any((opciones.destino / nombre).exists() for nombre in (
        f"resultado-{opciones.etiqueta}.json", f"arranque-{opciones.etiqueta}.txt"
    )):
        raise SystemExit("No se sobrescribe una comprobación anterior")
    sys.exit(asyncio.run(comprobar(opciones.proyecto, opciones.destino, opciones.etiqueta)))
