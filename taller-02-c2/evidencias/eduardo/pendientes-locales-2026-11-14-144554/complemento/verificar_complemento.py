"""Completa solo R10/R11/R12; nunca repite consultas al proveedor.

Usa el servidor de ensayo y las comprobaciones de verificar_pendientes.py.
En Windows termina únicamente el árbol del PID propio (incluido el lanzador
de .venv). Guarda cada resultado y cada línea sanitizada inmediatamente, sin
depender del cierre del ejecutor para conservar la evidencia.
"""

import argparse
import asyncio
import json
import os
from pathlib import Path
import re
import secrets
import socket
import subprocess
import sys
import threading
import time

import httpx
from dotenv import dotenv_values
from playwright.async_api import async_playwright, expect

ORIGEN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ORIGEN))
import verificar_pendientes as anterior  # noqa: E402


class ServidorPropio:
    def __init__(self, nombre, configuracion, clave, destino, sanitizador, procesos,
                 modo="integrado", puerto=None):
        self.nombre, self.destino, self.sanitizador, self.modo = nombre, destino, sanitizador, modo
        self.puerto = puerto or anterior.puerto_libre()
        self.direccion = f"http://127.0.0.1:{self.puerto}"
        self.lineas = []
        self.proceso = None
        self.registro = {"nombre": nombre, "modo": modo, "direccion": self.direccion,
                         "propio": True, "detenido": False}
        procesos.append(self.registro)
        self.entorno = {
            **configuracion, "CLAVE_API": clave, "PORT": str(self.puerto), "PUERTO": str(self.puerto),
            "URL_BASE": self.direccion, "URLS_AGENTES": "", "PYTHON_DOTENV_DISABLED": "1",
            "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1", "PYTHONUNBUFFERED": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
        }

    async def iniciar(self):
        argumentos = (["-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", str(self.puerto)]
                      if self.modo == "integrado" else [str(ORIGEN / "verificar_pendientes.py"), "--servidor", self.modo])
        self.archivo = (self.destino / f"servidor-{self.nombre}.txt").open("x", encoding="utf-8", newline="\n")
        self.archivo.write(f"LOCAL · {self.direccion} · {'app:app real' if self.modo == 'integrado' else 'FALLA INDUCIDA en entorno controlado; sin Gemini ni Heroku'}\n")
        self.archivo.flush()
        self.proceso = subprocess.Popen([sys.executable, "-B", *argumentos], cwd=anterior.PROYECTO,
                                        env=self.entorno, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.registro.update(pid_raiz_propio=self.proceso.pid, inicio=anterior.ahora())

        def leer():
            for linea in iter(self.proceso.stdout.readline, b""):
                texto = self.sanitizador.limpiar(linea.decode("utf-8", errors="replace"))
                self.lineas.append(texto)
                self.archivo.write(texto)
                self.archivo.flush()
                if coincidencia := re.search(r"Started server process \[(\d+)\]", texto):
                    self.registro["pid_servidor_propio"] = int(coincidencia[1])

        self.lector = threading.Thread(target=leer, daemon=True)
        self.lector.start()
        async with httpx.AsyncClient(timeout=2, trust_env=False) as cliente:
            async with asyncio.timeout(40):
                while True:
                    if self.proceso.poll() is not None:
                        raise RuntimeError("El servidor propio terminó antes de responder salud; revisar registro sanitizado.")
                    try:
                        respuesta = await cliente.get(self.direccion + "/salud")
                        if respuesta.status_code == 200 and respuesta.json() == {"ok": True}:
                            self.registro["salud_inicial"] = 200
                            return
                    except httpx.HTTPError:
                        pass
                    await asyncio.sleep(0.2)

    async def detener(self):
        if self.proceso is None or self.registro["detenido"]:
            return
        if self.proceso.poll() is None:
            # El PID proviene de Popen, no de un puerto ni de una búsqueda por nombre.
            resultado = await asyncio.to_thread(subprocess.run,
                [str(Path(os.environ["SystemRoot"]) / "System32/taskkill.exe"), "/PID", str(self.proceso.pid), "/T", "/F"],
                capture_output=True, timeout=15, check=False)
            self.registro["taskkill_arbol_propio_salida"] = resultado.returncode
        await asyncio.to_thread(self.proceso.wait, timeout=15)
        await asyncio.to_thread(self.lector.join, timeout=5)
        if self.lector.is_alive():
            raise RuntimeError("El árbol propio no cerró su salida; no se terminarán procesos ajenos.")
        self.archivo.close()
        self.registro.update(detenido=True, fin=anterior.ahora(), codigo_salida=self.proceso.returncode)


async def r10(configuracion, contexto, clave, destino, sanitizador, procesos, instancias):
    registro = {"caso": "R10", "fecha": anterior.ahora(), "entorno": "LOCAL app:app de ensayo propia",
                "pregunta": anterior.PREGUNTA_R10, "aprobado": False,
                "esperado": "Aviso de conexión al detener solo el servidor propio; pregunta y controles recuperados; restaurarlo en el mismo puerto."}
    original = ServidorPropio("r10-antes", configuracion, clave, destino, sanitizador, procesos)
    instancias.append(original)
    await original.iniciar()
    pagina = await anterior.nueva_pagina(contexto, original.direccion, clave)
    fallos = []
    pagina.on("requestfailed", lambda solicitud: fallos.append({"ruta": "/panel/consultar", "fallo": solicitud.failure})
              if solicitud.url.endswith("/panel/consultar") else None)
    try:
        await original.detener()
        registro.update(direccion=original.direccion, pid_raiz_detenido=original.proceso.pid,
                        pid_servidor_detenido=original.registro.get("pid_servidor_propio"))
        async with httpx.AsyncClient(timeout=2, trust_env=False) as cliente:
            try:
                await cliente.get(original.direccion + "/salud")
                raise AssertionError("El servidor debía estar detenido.")
            except httpx.ConnectError:
                registro["salud_durante_detencion"] = "conexión rechazada"
        inicio = time.perf_counter()
        await anterior.enviar(pagina, anterior.PREGUNTA_R10)
        aviso = pagina.locator(".mensaje.asistente .burbuja").last
        try:
            await expect(aviso).to_contain_text("No se pudo conectar con el servidor.", timeout=20000)
        finally:
            registro.update(texto_visible=await pagina.locator("#conversacion").inner_text(),
                            fallos_red=fallos, espera_observada_segundos=round(time.perf_counter() - inicio, 3))
            registro["captura"] = await anterior.captura(pagina, destino, "r10-desconexion-servidor-propio.png",
                "R10 · desconexión real · solo se detuvo el árbol del servidor LOCAL propio de ensayo · no se cortó la red", sanitizador)
        await anterior.verificar_recuperacion(pagina, anterior.PREGUNTA_R10)
        assert fallos
        registro.update(aviso=await aviso.inner_text(), pregunta_conservada=True, controles_recuperados=True, aprobado=True)
    except Exception as error:
        registro["error"] = sanitizador.limpiar(type(error).__name__ + ": " + " ".join(str(error).split()))
    finally:
        await original.detener()
        restaurado = ServidorPropio("r10-restaurado", configuracion, clave, destino, sanitizador, procesos, puerto=original.puerto)
        instancias.append(restaurado)
        await restaurado.iniciar()
        async with httpx.AsyncClient(timeout=10, trust_env=False) as cliente:
            salud = await cliente.get(restaurado.direccion + "/salud")
            portada = await cliente.get(restaurado.direccion + "/")
            post = await cliente.post(restaurado.direccion + "/panel/consultar", headers={"X-API-Key": clave}, json={"texto": "   "})
        assert salud.status_code == 200 and portada.status_code == 200 and post.status_code == 400
        registro["restauracion"] = {"fecha": anterior.ahora(), "mismo_puerto": True,
                                   "pid_raiz_nuevo": restaurado.proceso.pid,
                                   "pid_servidor_nuevo": restaurado.registro.get("pid_servidor_propio"),
                                   "salud_http": 200, "portada_http": 200, "post_autorizado_espacios_http": 400,
                                   "limpieza_final": "Restauración verificada; después se cierran exclusivamente los procesos propios."}
        await pagina.goto(restaurado.direccion, wait_until="networkidle", timeout=15000)
        registro["captura_restauracion"] = await anterior.captura(pagina, destino, "r10-restaurado-mismo-puerto.png",
            "R10 · servidor propio RESTAURADO · mismo puerto · /salud 200 · panel 200 · POST autorizado 400", sanitizador)
        await pagina.close()
        await restaurado.detener()
    return registro


async def principal(argumentos):
    destino = Path(argumentos.carpeta).resolve()
    if not destino.is_relative_to(anterior.EVIDENCIAS) or destino == anterior.EVIDENCIAS:
        raise RuntimeError("El destino debe estar dentro de evidencias/eduardo.")
    destino.mkdir(parents=True, exist_ok=True)
    if any(p.suffix != ".py" for p in destino.iterdir()):
        raise RuntimeError("Elegir una carpeta nueva, sin resultados anteriores.")
    configuracion = {**{k: v for k, v in dotenv_values(anterior.PROYECTO / ".env").items() if v is not None}, **os.environ}
    sanitizador = anterior.Sanitizador(configuracion)
    clave = secrets.token_urlsafe(32)
    sanitizador.agregar(clave)
    aislado = {k: v for k, v in os.environ.items() if not re.search(r"KEY|TOKEN|SECRET|PASSWORD|CLAVE|CREDENTIAL", k, re.I)}
    aislado.update(GOOGLE_API_KEY="", GEMINI_API_KEY="", GOOGLE_GENAI_USE_VERTEXAI="false", GOOGLE_APPLICATION_CREDENTIALS="")
    resultados = {"inicio": anterior.ahora(), "entorno": "LOCAL Windows", "base": "d8cce1337b7caf0bcd63df2d9ce21d9dc96a3f91",
                  "sha256_panel_probado": anterior.huella(anterior.PANEL), "sha256_ejecutor": anterior.huella(Path(__file__).resolve()),
                  "sha256_ejecutor_original": anterior.huella(ORIGEN / "verificar_pendientes.py"),
                  "consultas_a_gemini": 0, "suites_completas_repetidas": False, "casos": [], "procesos": []}
    instancias = []
    try:
        async with async_playwright() as herramienta:
            navegador = await herramienta.chromium.launch(channel="chrome", headless=True, timeout=30000)
            resultados["navegador"] = navegador.version
            contexto = await navegador.new_context(viewport={"width": 1280, "height": 960}, locale="es-CL",
                                                   reduced_motion="reduce", service_workers="block")
            try:
                for nombre in argumentos.casos:
                    try:
                        if nombre == "R10":
                            operacion = r10(configuracion, contexto, clave, destino, sanitizador, resultados["procesos"], instancias)
                        else:
                            servidor = ServidorPropio(nombre.lower(), aislado, clave, destino, sanitizador, resultados["procesos"],
                                                      modo="lento" if nombre == "R11" else "html")
                            instancias.append(servidor)
                            await servidor.iniciar()
                            funcion = anterior.comprobar_r11 if nombre == "R11" else anterior.comprobar_r12
                            operacion = funcion(servidor, contexto, clave, destino, sanitizador)
                        registro = await asyncio.wait_for(operacion, timeout=120)
                    except Exception as error:
                        registro = {"caso": nombre, "aprobado": False,
                                    "error": sanitizador.limpiar(type(error).__name__ + ": " + " ".join(str(error).split()))}
                    resultados["casos"].append(registro)
                    anterior.escribir_nuevo(destino / f"{nombre.lower()}-resultado.json",
                        sanitizador.limpiar(json.dumps(registro, ensure_ascii=False, indent=2)) + "\n")
                    print(f"{nombre}: {'APROBADO' if registro['aprobado'] else 'NO APROBADO'}", flush=True)
                    if nombre != "R10":
                        await servidor.detener()
            finally:
                await asyncio.wait_for(contexto.close(), timeout=15)
                await asyncio.wait_for(navegador.close(), timeout=15)
    except Exception as error:
        resultados["error_general"] = sanitizador.limpiar(type(error).__name__ + ": " + " ".join(str(error).split()))
    finally:
        for servidor in instancias:
            await servidor.detener()
        resultados["finalizacion"] = anterior.ahora()
        resultados["todos_los_hijos_detenidos"] = all(p["detenido"] for p in resultados["procesos"])
        anterior.escribir_nuevo(destino / "resultados-complemento.json",
            sanitizador.limpiar(json.dumps(resultados, ensure_ascii=False, indent=2)) + "\n")
    return int("error_general" in resultados or not all(c["aprobado"] for c in resultados["casos"]))


if __name__ == "__main__":
    analizador = argparse.ArgumentParser(description="Complemento dirigido, sin consultas reales al proveedor.")
    analizador.add_argument("--carpeta", required=True)
    analizador.add_argument("--casos", nargs="+", choices=("R10", "R11", "R12"), default=["R10", "R11", "R12"])
    try:
        sys.exit(asyncio.run(principal(analizador.parse_args())))
    except Exception:
        print("Verificación incompleta; revisar solo los registros sanitizados.")
        sys.exit(1)
