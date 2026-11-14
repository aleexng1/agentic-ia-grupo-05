"""Verificación de Eduardo, sin modificar .env, otros aportes ni Heroku.

Desde proyecto (con .venv):
  python ../evidencias/eduardo/validar_cierre_local.py pruebas --carpeta RUTA_NUEVA
  python ../evidencias/eduardo/validar_cierre_local.py casos --carpeta RUTA_NUEVA

La primera fase no usa claves reales ni Gemini. La segunda hace una sola consulta
R05 real al proveedor configurado; R06/R07 son rechazos HTTP reales y R09 usa otro
proceso sin configuración de Gemini. No hay dobles, reintentos de consultas ni cambios
de respuestas HTTP en esa segunda fase. Las claves temporales solo viven en memoria
y en el entorno de los hijos; nunca se pasan como argumentos ni se guardan.
Los registros se sanitizan en memoria antes de escribirlos. No se sobrescriben archivos.
"""

import argparse
import asyncio
from contextlib import asynccontextmanager
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
import time
from urllib.parse import quote

from dotenv import dotenv_values
import httpx
from playwright.async_api import async_playwright, expect


CARPETA = Path(__file__).resolve().parent
TALLER = CARPETA.parents[1]
RAIZ = TALLER.parent
PROYECTO = TALLER / "proyecto"
PREGUNTA = "¿Cuál es el presupuesto simulado de una feria tecnológica para 80 personas y 4 horas?"
ARCHIVOS_PROBADOS = (
    PROYECTO / "src/comun/panel.html",
    CARPETA / "test_panel_eduardo.py",
    Path(__file__).resolve(),
)


def ahora():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def huella(archivo):
    return hashlib.sha256(archivo.read_bytes()).hexdigest() if archivo.exists() else None


def escribir_nuevo(archivo, texto):
    archivo.parent.mkdir(parents=True, exist_ok=True)
    with archivo.open("x", encoding="utf-8", newline="\n") as salida:
        salida.write(texto)


class Sanitizador:
    def __init__(self, configuracion):
        self.valores = set()
        for nombre, valor in configuracion.items():
            if re.search(r"KEY|TOKEN|SECRET|PASSWORD|CLAVE|CREDENTIAL", nombre, re.I):
                self.agregar(valor)

    def agregar(self, valor):
        if valor and len(valor) >= 4:
            self.valores.update((valor, quote(valor, safe="")))

    def limpiar(self, texto):
        for valor in sorted(self.valores, key=len, reverse=True):
            texto = texto.replace(valor, "[secreto oculto]")
        texto = re.sub(r"AIza[0-9A-Za-z_-]{20,}", "[secreto oculto]", texto)
        texto = re.sub(
            r"(?i)(x-api-key|api[_-]?key|authorization|clave_api|google_api_key|[?&]key)"
            r"(\s*[:=]\s*)([^\s,;\"']+)",
            r"\1\2[secreto oculto]", texto,
        )
        texto = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._-]{8,}", r"\1[secreto oculto]", texto)
        for ruta, reemplazo in ((RAIZ, "<REPOSITORIO>"), (Path.home(), "<CARPETA_PERSONAL>")):
            texto = texto.replace(str(ruta), reemplazo).replace(ruta.as_posix(), reemplazo)
        return texto

    def comprobar_pantalla(self, texto):
        if any(valor in texto for valor in self.valores):
            raise RuntimeError("Captura cancelada: contenido sensible detectado.")
        if re.search(r"AIza[0-9A-Za-z_-]{20,}", texto):
            raise RuntimeError("Captura cancelada: posible credencial detectada.")


def metadatos():
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=RAIZ, capture_output=True,
        text=True, check=True, timeout=10,
    ).stdout.strip()
    return {
        "fecha": ahora(), "entorno": "LOCAL", "commit_base": commit,
        "cambios_sin_commit": True,
        "sha256_archivos_probados": {
            archivo.relative_to(RAIZ).as_posix(): huella(archivo)
            for archivo in ARCHIVOS_PROBADOS
        },
        "demo_taller_2_retirada": not (PROYECTO / "src/agente_eduardo/demo.html").exists(),
    }


def archivos_privados_y_taller_1():
    return {
        nombre: huella(RAIZ / nombre) for nombre in (
            "taller-02-c2/proyecto/.env",
            "taller-01-c2/evidencias/eduardo/03-ficha-telefono.jpg",
            "taller-01-c2/proyecto/src/agente_eduardo/demo.html",
        )
    }


async def ejecutar_pruebas(destino, sanitizador):
    resultados = {**metadatos(), "tipo": "automatizadas; proveedor y respuestas simulados", "suites": []}
    entorno = {
        **os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1",
        "PYTHON_DOTENV_DISABLED": "1", "GOOGLE_API_KEY": "", "GEMINI_API_KEY": "",
        "GOOGLE_GENAI_USE_VERTEXAI": "false", "GOOGLE_APPLICATION_CREDENTIALS": "",
        "CLAVE_API": secrets.token_urlsafe(32),
        "CARPETA_CAPTURAS": str(destino / "capturas-regresion"),
    }
    sanitizador.agregar(entorno["CLAVE_API"])
    for nombre, argumentos in (
        ("proyecto", ["-q"]),
        ("frontend", [str(CARPETA / "test_panel_eduardo.py"), "-v", "-rx"]),
    ):
        archivo = destino / f"pytest-{nombre}.txt"
        if archivo.exists():
            raise RuntimeError("Ya existe el registro de pruebas; elige otra carpeta.")
        comando = [sys.executable, "-m", "pytest", *argumentos, "--tb=short",
                   "--show-capture=no", "-p", "no:cacheprovider"]
        proceso = await asyncio.create_subprocess_exec(
            *comando, cwd=PROYECTO, env=entorno,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
        )
        try:
            salida, _ = await asyncio.wait_for(proceso.communicate(), timeout=300)
        except asyncio.TimeoutError:
            proceso.kill()
            salida, _ = await proceso.communicate()
        texto = sanitizador.limpiar(salida.decode("utf-8", errors="replace"))
        escribir_nuevo(archivo, f"LOCAL · {ahora()} · base {resultados['commit_base']} + cambios sin commit\n"
                       "Sin credenciales reales; CARPETA_CAPTURAS en carpeta nueva.\n\n" + texto)
        resumen = next((linea for linea in reversed(texto.splitlines())
                        if re.search(r"\d+ (passed|failed|error|skipped|xfailed|xpassed)", linea)), "Sin resumen de pytest")
        resultados["suites"].append({"suite": nombre, "codigo_salida": proceso.returncode, "resumen": resumen})
        print(f"{nombre}: {resumen.strip('= ')} · salida {proceso.returncode}", flush=True)
    return resultados


async def esperar_linea(lineas, fragmento):
    async with asyncio.timeout(5):
        while not any(fragmento in linea for linea in lineas):
            await asyncio.sleep(0.02)


@asynccontextmanager
async def servidor_local(configuracion, clave, destino, nombre, sanitizador, sin_gemini=False):
    archivo = destino / f"servidor-{nombre}.txt"
    if archivo.exists():
        raise RuntimeError("Ya existe el registro del servidor; elige otra carpeta.")
    with socket.socket() as conexion:
        conexion.bind(("127.0.0.1", 0))
        puerto = conexion.getsockname()[1]
    direccion = f"http://127.0.0.1:{puerto}"
    entorno = {
        **configuracion, "CLAVE_API": clave, "PORT": str(puerto), "PUERTO": str(puerto),
        "URL_BASE": direccion, "URLS_AGENTES": "", "PYTHON_DOTENV_DISABLED": "1",
        "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1", "PYTHONUNBUFFERED": "1",
    }
    if sin_gemini:
        entorno.update(GOOGLE_API_KEY="", GEMINI_API_KEY="", GOOGLE_GENAI_USE_VERTEXAI="false",
                       GOOGLE_APPLICATION_CREDENTIALS="", GOOGLE_CLOUD_PROJECT="")
    proceso = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1",
        "--port", str(puerto), "--log-level", "info", cwd=PROYECTO, env=entorno,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
    )
    lineas = []

    async def leer_salida():
        while linea := await proceso.stdout.readline():
            lineas.append(sanitizador.limpiar(linea.decode("utf-8", errors="replace")))

    lector = asyncio.create_task(leer_salida())
    try:
        async with httpx.AsyncClient(timeout=2, trust_env=False) as cliente:
            async with asyncio.timeout(60):
                while True:
                    if proceso.returncode is not None:
                        raise RuntimeError("La app local terminó antes de responder /salud.")
                    try:
                        respuesta = await cliente.get(direccion + "/salud")
                        if respuesta.status_code == 200 and respuesta.json() == {"ok": True}:
                            break
                    except httpx.HTTPError:
                        pass
                    await asyncio.sleep(0.2)
        yield direccion, lineas
    finally:
        if proceso.returncode is None:
            proceso.terminate()
        try:
            await asyncio.wait_for(proceso.wait(), timeout=15)
        except asyncio.TimeoutError:
            proceso.kill()
            await proceso.wait()
        await lector
        escribir_nuevo(archivo, f"LOCAL · {ahora()} · proceso {nombre} · {direccion}\n"
                       "App real app:app, sin dobles. Configuración solo en el entorno del hijo.\n"
                       "Registro sanitizado antes de escribir; salida UTF-8.\n\n" + "".join(lineas))


async def ingresar(pagina, clave):
    await pagina.locator("#clave").fill(clave)
    await pagina.locator("#clave").press("Enter")
    await expect(pagina.locator("#panel-chat")).to_be_visible()
    await expect(pagina.locator("#clave")).to_have_value("")


async def consultar(pagina):
    async with pagina.expect_response(
        lambda respuesta: respuesta.url.endswith("/panel/consultar") and respuesta.request.method == "POST",
        timeout=75000,
    ) as pendiente:
        await pagina.locator("#pregunta").fill(PREGUNTA)
        await pagina.locator("#pregunta").press("Enter")
    respuesta = await pendiente.value
    datos = await respuesta.json()
    return respuesta.status, datos


async def capturar(pagina, destino, nombre, descripcion, sanitizador):
    if await pagina.locator("#clave").input_value():
        raise RuntimeError("Captura cancelada: el campo de clave no está vacío.")
    sanitizador.comprobar_pantalla(await pagina.content())
    await pagina.evaluate("""descripcion => {
        const franja = document.createElement('div');
        franja.textContent = descripcion;
        franja.style.cssText = 'padding:12px;background:#172b3a;color:white;font:14px system-ui';
        document.body.prepend(franja);
    }""", f"LOCAL · {ahora()} · {descripcion}")
    # Solo ampliar la altura para que la captura conserve todo el contenido original.
    await pagina.add_style_tag(content=".conversacion{max-height:none!important;overflow:visible!important}")
    await pagina.screenshot(path=str(destino / nombre), full_page=True, animations="disabled", timeout=15000)


def actividad(lineas):
    return {
        "preguntas_coordinador": sum("pregunta recibida" in linea for linea in lineas),
        "envios_a2a": sum("A2A →" in linea for linea in lineas),
        "recepciones_a2a": sum("A2A ←" in linea for linea in lineas),
        "rechazos": sum("acceso rechazado" in linea for linea in lineas),
    }


async def ejecutar_casos(destino, configuracion, sanitizador):
    resultados = {**metadatos(), "tipo": "HTTP y app integrada reales, sin dobles", "casos": []}
    clave = secrets.token_urlsafe(32)
    incorrecta = secrets.token_urlsafe(32)
    sanitizador.agregar(clave)
    sanitizador.agregar(incorrecta)
    async with async_playwright() as herramienta:
        navegador = await herramienta.chromium.launch(
            channel=os.getenv("CANAL_NAVEGADOR", "chrome"), headless=True, timeout=30000,
        )
        contexto = await navegador.new_context(
            viewport={"width": 1280, "height": 960}, locale="es-CL",
            reduced_motion="reduce", service_workers="block",
        )
        pagina = await contexto.new_page()
        pagina.set_default_timeout(10000)
        try:
            async with servidor_local(configuracion, clave, destino, "integrado", sanitizador) as (direccion, lineas):
                # Los rechazos van primero para comprobar que aún no hubo consultas al grafo.
                for caso in ("R06", "R07", "R05"):
                    registro = {"caso": caso, "fecha": ahora(), "pregunta": PREGUNTA, "aprobado": False}
                    resultados["casos"].append(registro)
                    await pagina.goto(direccion, wait_until="networkidle", timeout=15000)
                    try:
                        if caso == "R06":
                            async with httpx.AsyncClient(timeout=10, trust_env=False) as cliente:
                                respuesta = await cliente.post(direccion + "/panel/consultar", json={"texto": PREGUNTA, "context_id": "r06-sin-cabecera"})
                            estado, datos = respuesta.status_code, respuesta.json()
                            await esperar_linea(lineas, "sin clave")
                            registro.update(http=estado, cuerpo=datos, actividad_acumulada=actividad(lineas))
                            # R06 no tiene flujo nativo en el panel: se rotula el resultado HTTP real.
                            await pagina.evaluate("""texto => {
                                const resultado = document.createElement('pre');
                                resultado.textContent = texto;
                                resultado.style.cssText = 'white-space:pre-wrap;padding:20px;background:white';
                                document.querySelector('main').append(resultado);
                            }""", sanitizador.limpiar(f"R06 · Cliente HTTP real sin X-API-Key\nHTTP {estado}\n" + json.dumps(datos, ensure_ascii=False, indent=2)))
                            assert estado == 401 and actividad(lineas)["preguntas_coordinador"] == 0
                            assert actividad(lineas)["envios_a2a"] == 0
                        else:
                            await ingresar(pagina, incorrecta if caso == "R07" else clave)
                            estado, datos = await consultar(pagina)
                            registro.update(http=estado, cuerpo=datos)
                            if caso == "R07":
                                await expect(pagina.locator("#error-acceso")).to_contain_text("Acceso rechazado (401)")
                                await expect(pagina.locator("#acceso")).to_be_visible()
                                await expect(pagina.locator("#pregunta")).to_have_value(PREGUNTA)
                                await expect(pagina.locator("#clave")).to_have_value("")
                                await esperar_linea(lineas, "clave incorrecta")
                                registro.update(aviso=await pagina.locator("#error-acceso").inner_text(), pregunta_conservada=True, campo_clave_vacio=True)
                                assert estado == 401 and actividad(lineas)["preguntas_coordinador"] == 0
                                assert actividad(lineas)["envios_a2a"] == 0
                            else:
                                await expect(pagina.locator("#enviar")).to_be_enabled(timeout=70000)
                                registro.update(texto_visible=await pagina.locator(".mensaje.asistente .burbuja").last.inner_text(), uso_proveedor="consulta real; sin reintento")
                                assert estado == 200 and set(datos) == {"respuesta", "context_id", "agente", "motivo"}
                                assert datos["agente"] == "Agente de Eduardo" and datos["respuesta"] and datos["motivo"]
                                await expect(pagina.locator(".mensaje.asistente .hora").nth(1)).to_have_text("Agente: Agente de Eduardo")
                                await esperar_linea(lineas, "A2A ←")
                            registro["actividad_acumulada"] = actividad(lineas)
                        registro["aprobado"] = True
                    except Exception as error:
                        registro["error"] = sanitizador.limpiar(" ".join(str(error).split()) or type(error).__name__)
                    nombre = {"R05": "r05-acceso-permitido.png", "R06": "r06-sin-clave.png", "R07": "r07-clave-incorrecta.png"}[caso]
                    registro["captura"] = nombre
                    descripcion = f"{caso} · HTTP real · {'APROBADO' if registro['aprobado'] else 'NO APROBADO'}"
                    if caso == "R06":
                        descripcion += " · visualización del resultado del cliente HTTP, no aviso nativo del panel"
                    await capturar(pagina, destino, nombre, descripcion, sanitizador)
                    print(f"{caso}: HTTP {registro.get('http', 'sin respuesta')} · {'aprobado' if registro['aprobado'] else 'no aprobado'}", flush=True)

            registro = {"caso": "R09", "fecha": ahora(), "pregunta": PREGUNTA, "aprobado": False,
                        "configuracion": "otro proceso; CLAVE_API temporal activa; GOOGLE_API_KEY y GEMINI_API_KEY vacías; dotenv deshabilitado",
                        "limite": "falla real de configuración del proveedor; no acredita rechazo remoto, cuota ni indisponibilidad de Gemini"}
            resultados["casos"].append(registro)
            async with servidor_local(configuracion, clave, destino, "r09-aislado", sanitizador, sin_gemini=True) as (direccion, lineas):
                await pagina.goto(direccion, wait_until="networkidle", timeout=15000)
                try:
                    await ingresar(pagina, clave)
                    estado, datos = await consultar(pagina)
                    registro.update(http=estado, cuerpo=datos)
                    await expect(pagina.locator("#enviar")).to_be_enabled(timeout=70000)
                    aviso = await pagina.locator(".mensaje.asistente .burbuja").last.inner_text()
                    registro["aviso"] = aviso
                    await expect(pagina.locator("#pregunta")).to_have_value(PREGUNTA)
                    assert estado == 502 and isinstance(datos.get("detail"), str)
                    assert "GOOGLE_API_KEY" in datos["detail"] and "Falta configurar" in datos["detail"]
                    assert aviso == datos["detail"] and "\n" not in aviso and "Traceback" not in aviso
                    sanitizador.comprobar_pantalla(json.dumps(datos, ensure_ascii=False))
                    await esperar_linea(lineas, "consulta fallida")
                    registro.update(aprobado=True, pregunta_conservada=True, actividad_acumulada=actividad(lineas))
                except Exception as error:
                    registro["error"] = sanitizador.limpiar(" ".join(str(error).split()) or type(error).__name__)
                registro["captura"] = "r09-proveedor-sin-configuracion.png"
                await capturar(pagina, destino, registro["captura"], f"R09 · HTTP real · proceso aislado sin configuración de Gemini · {'APROBADO' if registro['aprobado'] else 'NO APROBADO'}", sanitizador)
                print(f"R09: HTTP {registro.get('http', 'sin respuesta')} · {'aprobado' if registro['aprobado'] else 'no aprobado'}", flush=True)
        finally:
            await contexto.close()
            await navegador.close()
    return resultados


async def principal(argumentos):
    destino = Path(argumentos.carpeta).resolve()
    if not destino.is_relative_to(CARPETA) or destino == CARPETA:
        raise RuntimeError("La carpeta nueva debe estar dentro de evidencias/eduardo.")
    destino.mkdir(parents=True, exist_ok=True)
    configuracion = {**{nombre: valor for nombre, valor in dotenv_values(PROYECTO / ".env").items() if valor is not None}, **os.environ}
    sanitizador = Sanitizador(configuracion)
    protegidos = archivos_privados_y_taller_1()
    archivo = destino / f"resultados-{'pruebas' if argumentos.fase == 'pruebas' else 'locales'}.json"
    if archivo.exists():
        raise RuntimeError("Esta fase ya tiene resultados; elige otra carpeta.")
    inicio = time.perf_counter()
    try:
        funcion = ejecutar_pruebas if argumentos.fase == "pruebas" else ejecutar_casos
        resultados = await funcion(destino, sanitizador) if argumentos.fase == "pruebas" else await funcion(destino, configuracion, sanitizador)
    except Exception as error:
        resultados = {**metadatos(), "error": sanitizador.limpiar(" ".join(str(error).split()) or type(error).__name__)}
    resultados["duracion_segundos"] = round(time.perf_counter() - inicio, 2)
    resultados["finalizacion"] = ahora()
    resultados["archivos_conservados"] = {
        nombre: valor == archivos_privados_y_taller_1()[nombre] for nombre, valor in protegidos.items()
    }
    escribir_nuevo(archivo, sanitizador.limpiar(json.dumps(resultados, ensure_ascii=False, indent=2)) + "\n")
    if "error" in resultados:
        print("Ejecución incompleta; consulta el resultado sanitizado.")
        return 1
    if not all(resultados["archivos_conservados"].values()):
        print("Atención: cambió un archivo protegido durante la ejecución.")
        return 1
    if argumentos.fase == "pruebas":
        return int(any(suite["codigo_salida"] != 0 for suite in resultados["suites"]))
    return int(any(not caso["aprobado"] for caso in resultados["casos"]))


if __name__ == "__main__":
    analizador = argparse.ArgumentParser(description="Verificación LOCAL de Eduardo, sin secretos en argumentos.")
    analizador.add_argument("fase", choices=("pruebas", "casos"))
    analizador.add_argument("--carpeta", required=True, help="Carpeta nueva dentro de evidencias/eduardo.")
    argumentos = analizador.parse_args()
    try:
        sys.exit(asyncio.run(principal(argumentos)))
    except Exception:
        print("No se pudo iniciar la verificación; revisa la ruta o las dependencias, sin publicar configuración privada.")
        sys.exit(1)
