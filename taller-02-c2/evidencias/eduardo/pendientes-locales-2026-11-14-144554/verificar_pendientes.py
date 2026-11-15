"""Casos dirigidos de Eduardo; no ejecuta pytest ni modifica la aplicación.

Desde proyecto, con .venv y una carpeta NUEVA dentro de evidencias/eduardo:
  python -B ../evidencias/eduardo/pendientes-locales-2026-11-14-144554/verificar_pendientes.py \
    --carpeta ../evidencias/eduardo/OTRA_CARPETA --linea-base RUTA_PRIVADA_JSON

R08/R10 usan app:app real. Las tres consultas sí consumen Gemini por el
coordinador y A2A, sin reintentos del ejecutor. R11/R12 usan este servidor de
ensayo, sin proveedor: demora REAL de 70 s y HTML deliberado. No son averías de
Gemini ni Heroku. Solo se detienen los procesos hijos creados por este ejecutor.
La línea base privada contiene huellas, nunca valores de credenciales.
"""

import argparse
import asyncio
from datetime import datetime
from importlib.metadata import version
import json
import os
from pathlib import Path
import re
import secrets
import socket
import sys
import time

from dotenv import dotenv_values
import httpx
from playwright.async_api import async_playwright, expect


EVIDENCIAS = Path(__file__).resolve().parents[1]
TALLER = EVIDENCIAS.parents[1]
RAIZ = TALLER.parent
PROYECTO = TALLER / "proyecto"
PANEL = PROYECTO / "src/comun/panel.html"
sys.path.insert(0, str(EVIDENCIAS))
from validar_cierre_local import (  # noqa: E402
    Sanitizador, actividad, ahora, capturar, escribir_nuevo, huella, ingresar,
)

PREGUNTAS = (
    ("R01-actual", "Matías", "Agente de Matias",
     "Necesito un programa para una feria cultural familiar de 3 horas, desde las 16:00. "
     "Indica actividades, horarios y cualquier tiempo libre, con las condiciones de demostración."),
    ("R02-actual", "Alex", "Agente de Alex",
     "Necesito un recinto interior para una feria tecnológica de 80 personas. Recomienda opciones "
     "con aforo, características, accesibilidad y advertencias de disponibilidad; no reserves nada."),
    ("R04-actual", "Sebastián", "Agente de Sebastian",
     "Necesito catering para una feria tecnológica de 80 personas, de 10:00 a 14:00 (4 horas), "
     "con 10 vegetarianas y 5 sin gluten. Indica servicios, horarios, dietas y litros de agua; "
     "datos simulados, sin contratar nada."),
)
PREGUNTA_R10 = "Comprobación LOCAL R10: ¿puedes recibir esta pregunta?"
PREGUNTA_R11 = "Ensayo aislado R11: mantener esta consulta pendiente durante 70 segundos reales."
PREGUNTA_R12 = "Ensayo aislado R12: devolver HTML deliberadamente, sin consultar proveedores."
RESPUESTA_TARDIA = "RESPUESTA_TARDIA_R11_ENSAYO"
RESPUESTA_NUEVA = "Respuesta de ensayo para la conversación nueva; sin proveedor."
HTML_ENSAYO = ('<!doctype html><html><body><h1 id="html-ensayo">HTML_CONTROLADO_R12</h1>'
               '<script>window.htmlEnsayoEjecutado = true;</script></body></html>')


async def servir_ensayo(modo):
    """Servidor separado: sirve el panel intacto y condiciones inducidas explícitas."""
    import uvicorn
    from fastapi import FastAPI, Request
    from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

    aplicacion = FastAPI()
    eventos = []
    clave = os.environ["CLAVE_API"]

    @aplicacion.get("/")
    async def mostrar_panel():
        return FileResponse(PANEL, media_type="text/html", headers={"Cache-Control": "no-store"})

    @aplicacion.get("/salud")
    async def salud():
        return {"ok": True}

    @aplicacion.get("/estado-ensayo")
    async def estado():
        return {"modo": modo, "eventos": eventos}

    @aplicacion.post("/panel/consultar")
    async def consultar(solicitud: Request):
        if not secrets.compare_digest(solicitud.headers.get("X-API-Key", ""), clave):
            return JSONResponse({"detail": "Acceso rechazado por el servidor de ensayo."}, status_code=401)
        datos = await solicitud.json()
        evento = {"fecha": ahora(), "context_id": datos.get("context_id"),
                  "texto": datos.get("texto"), "finalizado": False}
        eventos.append(evento)
        inicio = time.perf_counter()
        print(f"ENSAYO {modo}: solicitud {len(eventos)} recibida; sin proveedor", flush=True)
        if modo == "html":
            evento.update(finalizado=True, http=200, tipo="text/html")
            return HTMLResponse(HTML_ENSAYO, headers={"Cache-Control": "no-store"})
        if datos.get("texto") == PREGUNTA_R11:
            await asyncio.sleep(70)  # Tiempo real; no se altera el reloj del navegador.
            respuesta = RESPUESTA_TARDIA
        else:
            respuesta = RESPUESTA_NUEVA
        evento.update(finalizado=True, duracion_real_segundos=round(time.perf_counter() - inicio, 6),
                      finalizacion=ahora(), respuesta_generada=respuesta)
        print(f"ENSAYO {modo}: respuesta generada tras {evento['duracion_real_segundos']:.3f} s reales", flush=True)
        return {"respuesta": respuesta, "context_id": datos["context_id"],
                "agente": "Servidor de ensayo aislado", "motivo": "Condición inducida; no usa Gemini ni Heroku."}

    servidor = uvicorn.Server(uvicorn.Config(
        aplicacion, host="127.0.0.1", port=int(os.environ["PORT"]),
        log_level="info", timeout_graceful_shutdown=10,
    ))
    await servidor.serve()


def puerto_libre():
    with socket.socket() as conexion:
        conexion.bind(("127.0.0.1", 0))
        return conexion.getsockname()[1]


class ProcesoLocal:
    def __init__(self, nombre, configuracion, clave, destino, sanitizador, procesos,
                 modo="integrado", puerto=None):
        self.nombre = nombre
        self.puerto = puerto or puerto_libre()
        self.direccion = f"http://127.0.0.1:{self.puerto}"
        self.destino = destino
        self.sanitizador = sanitizador
        self.modo = modo
        self.lineas = []
        self.proceso = None
        self.configuracion = {
            **configuracion, "CLAVE_API": clave, "PORT": str(self.puerto), "PUERTO": str(self.puerto),
            "URL_BASE": self.direccion, "URLS_AGENTES": "", "PYTHON_DOTENV_DISABLED": "1",
            "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1", "PYTHONUNBUFFERED": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        self.registro = {"nombre": nombre, "modo": modo, "direccion": self.direccion,
                         "propio": True, "detenido": False}
        procesos.append(self.registro)

    async def iniciar(self):
        archivo = self.destino / f"servidor-{self.nombre}.txt"
        if archivo.exists():
            raise RuntimeError("No se sobrescriben registros existentes.")
        argumentos = (["-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", str(self.puerto)]
                      if self.modo == "integrado" else [str(Path(__file__).resolve()), "--servidor", self.modo])
        self.proceso = await asyncio.create_subprocess_exec(
            sys.executable, "-B", *argumentos, cwd=PROYECTO, env=self.configuracion,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
        )
        self.registro.update(pid=self.proceso.pid, inicio=ahora())

        async def leer():
            while linea := await self.proceso.stdout.readline():
                self.lineas.append(self.sanitizador.limpiar(linea.decode("utf-8", errors="replace")))

        self.lector = asyncio.create_task(leer())
        async with httpx.AsyncClient(timeout=2, trust_env=False) as cliente:
            async with asyncio.timeout(60):
                while True:
                    if self.proceso.returncode is not None:
                        raise RuntimeError("El proceso local finalizó antes del chequeo de salud.")
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
        if self.proceso.returncode is None:
            self.proceso.terminate()  # Solo el PID hijo creado aquí; nunca por nombre/puerto.
        try:
            await asyncio.wait_for(self.proceso.wait(), timeout=15)
        except asyncio.TimeoutError:
            self.proceso.kill()
            await self.proceso.wait()
        await self.lector
        self.registro.update(detenido=True, fin=ahora(), codigo_salida=self.proceso.returncode)
        procedencia = ("App real app:app, sin dobles" if self.modo == "integrado"
                       else f"FALLA INDUCIDA EN ENTORNO CONTROLADO · {self.modo} · sin Gemini ni Heroku")
        escribir_nuevo(self.destino / f"servidor-{self.nombre}.txt",
                       f"LOCAL · {self.direccion} · PID propio {self.proceso.pid}\n{procedencia}\n"
                       "Registro sanitizado en memoria; no se guardan cabeceras.\n\n" + "".join(self.lineas))


async def nueva_pagina(contexto, direccion, clave):
    pagina = await contexto.new_page()
    pagina.set_default_timeout(10000)
    await pagina.goto(direccion, wait_until="networkidle", timeout=15000)
    await ingresar(pagina, clave)
    return pagina


async def enviar(pagina, pregunta):
    await pagina.locator("#pregunta").fill(pregunta)
    await pagina.locator("#pregunta").press("Enter")


async def verificar_recuperacion(pagina, pregunta):
    await expect(pagina.locator("#enviar")).to_be_enabled()
    await expect(pagina.locator("#pregunta")).to_have_value(pregunta)
    assert await pagina.locator(".sugerencia:disabled").count() == 0
    assert await pagina.locator("#conversacion").get_attribute("aria-busy") == "false"


async def captura(pagina, destino, nombre, descripcion, sanitizador):
    if (destino / nombre).exists():
        raise RuntimeError("No se sobrescriben capturas existentes.")
    await pagina.locator("#procedencia-evidencia").evaluate_all("nodos => nodos.forEach(nodo => nodo.remove())")
    await capturar(pagina, destino, nombre, descripcion, sanitizador)
    await pagina.evaluate("document.body.firstElementChild.id = 'procedencia-evidencia'")
    return nombre


async def comprobar_r08(servidor, contexto, clave, destino, sanitizador):
    registro = {"caso": "R08", "fecha": ahora(), "entorno": "LOCAL app:app integrada real",
                "esperado": "Con autorización válida: 400 para espacios y 422 si falta texto; sin invocar el grafo.",
                "autorizacion": "X-API-Key temporal válida; valor no guardado", "solicitudes": []}
    async with httpx.AsyncClient(timeout=10, trust_env=False, headers={"X-API-Key": clave}) as cliente:
        for nombre, cuerpo, esperado in (
            ("espacios", {"texto": "   ", "context_id": "r08-espacios-protegido"}, 400),
            ("sin-texto", {"context_id": "r08-sin-texto-protegido"}, 422),
        ):
            respuesta = await cliente.post(servidor.direccion + "/panel/consultar", json=cuerpo)
            datos = respuesta.json()
            registro["solicitudes"].append({"nombre": nombre, "cuerpo_enviado": cuerpo,
                                               "http_esperado": esperado, "http_obtenido": respuesta.status_code,
                                               "cuerpo_recibido": datos})
            assert respuesta.status_code == esperado
            assert "Traceback" not in respuesta.text
            if esperado == 400:
                assert datos == {"detail": "Escribe una pregunta para continuar."}
            else:
                assert datos["detail"][0]["loc"] == ["body", "texto"]
    registro["actividad_antes_de_consultas"] = actividad(servidor.lineas)
    assert registro["actividad_antes_de_consultas"]["preguntas_coordinador"] == 0
    assert registro["actividad_antes_de_consultas"]["envios_a2a"] == 0
    pagina = await nueva_pagina(contexto, servidor.direccion, clave)
    await pagina.evaluate("""texto => {
        const resultado = document.createElement('pre');
        resultado.textContent = texto;
        resultado.style.cssText = 'white-space:pre-wrap;padding:20px;background:white';
        document.querySelector('main').append(resultado);
    }""", json.dumps(registro["solicitudes"], ensure_ascii=False, indent=2))
    registro["captura"] = await captura(pagina, destino, "r08-entrada-protegida.png",
        "R08 · 400/422 reales con autorización válida · visualización del cliente HTTP, no aviso nativo del panel", sanitizador)
    await pagina.close()
    return {**registro, "aprobado": True}


async def consultar_agente(servidor, contexto, clave, destino, sanitizador, caso, persona, agente, pregunta):
    registro = {"caso": caso, "fecha": ahora(), "entorno": "LOCAL app:app integrada; panel actual",
                "persona": persona, "pregunta": pregunta,
                "esperado": f"200, contrato de cuatro campos, {agente}, motivo y respuesta íntegra visibles.",
                "procedencia": "Consulta real al coordinador, A2A y Gemini; no hay dobles ni interceptación HTTP.",
                "reintentos_del_ejecutor": 0}
    pagina = await nueva_pagina(contexto, servidor.direccion, clave)
    antes = actividad(servidor.lineas)
    inicio = time.perf_counter()
    async with pagina.expect_response(lambda r: r.url.endswith("/panel/consultar") and r.request.method == "POST",
                                     timeout=75000) as pendiente:
        await enviar(pagina, pregunta)
    respuesta = await pendiente.value
    datos = await respuesta.json()
    registro.update(http=respuesta.status, cuerpo=datos, duracion_real_segundos=round(time.perf_counter() - inicio, 3))
    # Conservar también el intercambio si una comprobación posterior no se aprueba.
    escribir_nuevo(destino / f"{caso.lower()}-intercambio.json",
                   sanitizador.limpiar(json.dumps(registro, ensure_ascii=False, indent=2)) + "\n")
    await expect(pagina.locator("#enviar")).to_be_enabled(timeout=10000)
    registro["texto_visible"] = await pagina.locator(".mensaje.asistente .burbuja").last.inner_text()
    assert respuesta.status == 200 and set(datos) == {"respuesta", "context_id", "agente", "motivo"}
    assert datos["agente"] == agente and datos["motivo"].strip() and datos["respuesta"].strip()
    pies = await pagina.locator(".mensaje.asistente").last.locator(".hora").all_text_contents()
    assert pies == [f"Agente: {agente}", f"Motivo: {datos['motivo']}"]
    registro["agente"] = datos["agente"]
    registro["motivo"] = datos["motivo"]
    registro["respuesta"] = datos["respuesta"]
    despues = actividad(servidor.lineas)
    registro["actividad_de_esta_consulta"] = {k: despues[k] - antes[k] for k in antes}
    assert registro["actividad_de_esta_consulta"]["envios_a2a"] == 1
    assert registro["actividad_de_esta_consulta"]["recepciones_a2a"] == 1
    registro["formato_dom"] = {"negritas": await pagina.locator(".mensaje.asistente .burbuja strong").count(),
                               "titulos": await pagina.locator(".mensaje.asistente .burbuja :is(h3,h4,h5,h6)").count()}
    registro["captura"] = await captura(pagina, destino, f"{caso.lower()}-consulta-real.png",
        f"{caso} · {persona} · CONSULTA REAL LOCAL · coordinador/A2A/Gemini · datos de demostración", sanitizador)
    await pagina.close()
    return {**registro, "aprobado": True}


async def comprobar_r10(configuracion, contexto, clave, destino, sanitizador, procesos, instancias):
    registro = {"caso": "R10", "fecha": ahora(), "entorno": "LOCAL app:app de ensayo propia",
                "pregunta": PREGUNTA_R10,
                "esperado": "Al detener solo el hijo propio: aviso de conexión, pregunta conservada y controles recuperados; restaurar después."}
    original = ProcesoLocal("r10-antes", configuracion, clave, destino, sanitizador, procesos)
    instancias.append(original)
    await original.iniciar()
    pagina = await nueva_pagina(contexto, original.direccion, clave)
    fallos = []
    pagina.on("requestfailed", lambda solicitud: fallos.append({"ruta": "/panel/consultar", "fallo": solicitud.failure})
              if solicitud.url.endswith("/panel/consultar") else None)
    try:
        await original.detener()
        registro.update(pid_detenido=original.proceso.pid, direccion=original.direccion)
        async with httpx.AsyncClient(timeout=2, trust_env=False) as cliente:
            try:
                await cliente.get(original.direccion + "/salud")
                raise AssertionError("El servidor debía estar detenido.")
            except httpx.ConnectError:
                registro["salud_durante_detencion"] = "conexión rechazada"
        await enviar(pagina, PREGUNTA_R10)
        aviso = pagina.locator(".mensaje.asistente .burbuja").last
        await expect(aviso).to_contain_text("No se pudo conectar con el servidor.")
        await verificar_recuperacion(pagina, PREGUNTA_R10)
        registro.update(aviso=await aviso.inner_text(), fallos_red=fallos, pregunta_conservada=True, controles_recuperados=True)
        assert fallos
        registro["captura"] = await captura(pagina, destino, "r10-servidor-propio-detenido.png",
            "R10 · desconexión real: solo se detuvo el servidor LOCAL propio de ensayo · sin cortar la red", sanitizador)
    finally:
        await original.detener()
        restaurado = ProcesoLocal("r10-restaurado", configuracion, clave, destino, sanitizador, procesos, puerto=original.puerto)
        instancias.append(restaurado)
        await restaurado.iniciar()
        async with httpx.AsyncClient(timeout=10, trust_env=False) as cliente:
            salud = await cliente.get(restaurado.direccion + "/salud")
            portada = await cliente.get(restaurado.direccion + "/")
            validacion = await cliente.post(restaurado.direccion + "/panel/consultar", headers={"X-API-Key": clave}, json={"texto": "   "})
        assert salud.status_code == 200 and portada.status_code == 200 and validacion.status_code == 400
        registro["restauracion"] = {"fecha": ahora(), "pid_nuevo": restaurado.proceso.pid,
                                   "mismo_puerto": restaurado.puerto == original.puerto, "salud_http": salud.status_code,
                                   "portada_http": portada.status_code, "post_autorizado_espacios_http": validacion.status_code,
                                   "limpieza_final": "Después de verificar la restauración, se cierran solo los hijos propios."}
        await pagina.goto(restaurado.direccion, wait_until="networkidle", timeout=15000)
        registro["captura_restauracion"] = await captura(pagina, destino, "r10-servidor-restaurado.png",
            "R10 · servidor propio RESTAURADO en el mismo puerto · /salud 200 · panel 200 · POST autorizado 400", sanitizador)
        await pagina.close()
        await restaurado.detener()
    return {**registro, "aprobado": True}


async def comprobar_r11(servidor, contexto, clave, destino, sanitizador):
    registro = {"caso": "R11", "fecha": ahora(), "entorno": "LOCAL aislado, servidor de ensayo sin proveedor",
                "clasificacion": "Falla inducida en entorno controlado; NO es falla real de Gemini ni Heroku.",
                "pregunta": PREGUNTA_R11, "retardo_configurado_segundos": 70, "reloj_virtual": False,
                "esperado": "Timeout tras más de 65 s REALES; recuperar controles y no recibir la respuesta vieja en la conversación nueva."}
    pagina = await nueva_pagina(contexto, servidor.direccion, clave)
    inicio = time.perf_counter()
    fecha_inicio = datetime.now().astimezone().isoformat(timespec="milliseconds")
    await enviar(pagina, PREGUNTA_R11)
    await expect(pagina.locator("#enviar")).to_be_disabled()
    assert await pagina.locator(".sugerencia:disabled").count() == 4
    registro["captura_espera"] = await captura(pagina, destino, "r11-espera-real-inducida.png",
        "R11 · FALLA INDUCIDA en entorno controlado · demora real de 70 s · sin Gemini ni Heroku · reloj sin alterar", sanitizador)
    aviso = pagina.locator(".mensaje.asistente .burbuja").last
    await expect(aviso).to_contain_text("La consulta superó los 65 segundos de espera.", timeout=80000)
    transcurrido = time.perf_counter() - inicio
    assert transcurrido > 65
    await verificar_recuperacion(pagina, PREGUNTA_R11)
    registro.update(inicio_espera=fecha_inicio, fin_espera=datetime.now().astimezone().isoformat(timespec="milliseconds"),
                    espera_real_hasta_aviso_segundos=round(transcurrido, 6), aviso=await aviso.inner_text(),
                    pregunta_conservada=True, controles_recuperados=True)
    registro["captura_timeout"] = await captura(pagina, destino, "r11-timeout-real-inducido.png",
        f"R11 · FALLA INDUCIDA · timeout observado tras {transcurrido:.3f} s REALES · sin Gemini ni Heroku", sanitizador)
    await pagina.locator("#nueva-conversacion").click()
    async with pagina.expect_response(lambda r: r.url.endswith("/panel/consultar"), timeout=15000) as pendiente:
        await enviar(pagina, "Consulta inmediata de ensayo en la conversación NUEVA de R11.")
    respuesta = await pendiente.value
    datos_nuevos = await respuesta.json()
    assert respuesta.status == 200 and datos_nuevos["respuesta"] == RESPUESTA_NUEVA
    await expect(pagina.locator("#enviar")).to_be_enabled()
    async with httpx.AsyncClient(timeout=3, trust_env=False) as cliente:
        async with asyncio.timeout(20):
            while True:
                respuesta_estado = await cliente.get(servidor.direccion + "/estado-ensayo")
                estado = respuesta_estado.json()
                if estado["eventos"][0]["finalizado"]:
                    break
                await asyncio.sleep(0.2)
    primero, segundo = estado["eventos"]
    assert primero["duracion_real_segundos"] >= 70
    assert primero["context_id"] != segundo["context_id"] == datos_nuevos["context_id"]
    assert RESPUESTA_TARDIA not in await pagina.locator("#conversacion").inner_text()
    await expect(pagina.locator(".mensaje.asistente .burbuja").last).to_have_text(RESPUESTA_NUEVA)
    registro.update(eventos_servidor=estado["eventos"], nueva_conversacion={"http": respuesta.status, "cuerpo": datos_nuevos},
                    contexto_nuevo=True, respuesta_vieja_ausente=True,
                    observacion="El navegador abortó la petición a los 65 s. El ensayo generó la respuesta vieja a los 70 s, pero no llegó a la conversación nueva; no se forzó a fetch a ignorar AbortSignal.")
    registro["captura_nueva"] = await captura(pagina, destino, "r11-nueva-sin-respuesta-vieja.png",
        "R11 · ensayo controlado · respuesta vieja generada tras 70 s REALES, ausente de la conversación nueva", sanitizador)
    await pagina.close()
    return {**registro, "aprobado": True}


async def comprobar_r12(servidor, contexto, clave, destino, sanitizador):
    registro = {"caso": "R12", "fecha": ahora(), "entorno": "LOCAL aislado, servidor de ensayo sin proveedor",
                "clasificacion": "Falla inducida en entorno controlado; NO es falla real de Gemini ni Heroku.",
                "pregunta": PREGUNTA_R12,
                "esperado": "Al recibir 200 text/html por HTTP real: aviso no JSON, no insertar/ejecutar el HTML y recuperar controles."}
    pagina = await nueva_pagina(contexto, servidor.direccion, clave)
    async with pagina.expect_response(lambda r: r.url.endswith("/panel/consultar"), timeout=15000) as pendiente:
        await enviar(pagina, PREGUNTA_R12)
    respuesta = await pendiente.value
    registro.update(http=respuesta.status, tipo=respuesta.headers.get("content-type"), cuerpo_html_de_ensayo=await respuesta.text())
    aviso = pagina.locator(".mensaje.asistente .burbuja").last
    await expect(aviso).to_contain_text("El servidor devolvió una respuesta que no es JSON.")
    await verificar_recuperacion(pagina, PREGUNTA_R12)
    assert respuesta.status == 200 and registro["tipo"].startswith("text/html")
    assert await pagina.locator("#html-ensayo").count() == 0
    assert await pagina.evaluate("window.htmlEnsayoEjecutado === undefined")
    assert "HTML_CONTROLADO_R12" not in await pagina.locator("#conversacion").inner_text()
    registro.update(aviso=await aviso.inner_text(), html_no_insertado=True, script_no_ejecutado=True,
                    pregunta_conservada=True, controles_recuperados=True)
    registro["captura"] = await captura(pagina, destino, "r12-html-inducido.png",
        "R12 · FALLA INDUCIDA en entorno controlado · HTTP real 200 text/html · sin Gemini ni Heroku", sanitizador)
    await pagina.close()
    return {**registro, "aprobado": True}


async def principal(argumentos):
    destino = Path(argumentos.carpeta).resolve()
    if not destino.is_relative_to(EVIDENCIAS) or destino == EVIDENCIAS:
        raise RuntimeError("El destino debe estar dentro de evidencias/eduardo.")
    destino.mkdir(parents=True, exist_ok=True)
    if any(p.name != Path(__file__).name for p in destino.iterdir()):
        raise RuntimeError("Elige una carpeta nueva, sin evidencias previas.")
    linea_base = json.loads(Path(argumentos.linea_base).read_text(encoding="utf-8"))
    configuracion = {**{k: v for k, v in dotenv_values(PROYECTO / ".env").items() if v is not None}, **os.environ}
    sanitizador = Sanitizador(configuracion)
    clave = secrets.token_urlsafe(32)
    sanitizador.agregar(clave)
    configuracion_aislada = {k: v for k, v in os.environ.items()
                            if not re.search(r"KEY|TOKEN|SECRET|PASSWORD|CLAVE|CREDENTIAL", k, re.I)}
    configuracion_aislada.update(GOOGLE_API_KEY="", GEMINI_API_KEY="", GOOGLE_GENAI_USE_VERTEXAI="false",
                                GOOGLE_APPLICATION_CREDENTIALS="", GOOGLE_CLOUD_PROJECT="")
    resultados = {"inicio": ahora(), "entorno": "LOCAL Windows", "base": linea_base["head"],
                  "rama": "c2t2/eduardo-frontend", "pr_existente": 82,
                  "estado_git_previo": linea_base["estado_git"], "codigo_produccion_modificado": False,
                  "suites_completas_repetidas": False, "python": sys.version.split()[0],
                  "playwright": version("playwright"), "sha256_panel_probado": huella(PANEL),
                  "sha256_ejecutor": huella(Path(__file__).resolve()), "procesos": [], "casos": []}
    instancias = []

    async def caso(nombre, operacion):
        try:
            registro = await operacion
        except Exception as error:
            registro = {"caso": nombre, "aprobado": False,
                        "error": sanitizador.limpiar(" ".join(str(error).split()) or type(error).__name__)}
        resultados["casos"].append(registro)
        print(f"{nombre}: {'APROBADO' if registro['aprobado'] else 'NO APROBADO'}", flush=True)

    try:
        async with async_playwright() as herramienta:
            navegador = await herramienta.chromium.launch(channel=os.getenv("CANAL_NAVEGADOR", "chrome"), headless=True, timeout=30000)
            resultados["navegador"] = navegador.version
            contexto = await navegador.new_context(viewport={"width": 1280, "height": 960}, locale="es-CL",
                                                   reduced_motion="reduce", service_workers="block")
            try:
                integrado = ProcesoLocal("integrado-consultas", configuracion, clave, destino, sanitizador, resultados["procesos"])
                instancias.append(integrado)
                await integrado.iniciar()
                await caso("R08", comprobar_r08(integrado, contexto, clave, destino, sanitizador))
                for nombre, persona, agente, pregunta in PREGUNTAS:
                    await caso(nombre, consultar_agente(integrado, contexto, clave, destino, sanitizador, nombre, persona, agente, pregunta))
                await integrado.detener()
                await caso("R10", comprobar_r10(configuracion, contexto, clave, destino, sanitizador, resultados["procesos"], instancias))
                for modo, nombre, funcion in (("lento", "R11", comprobar_r11), ("html", "R12", comprobar_r12)):
                    servidor = ProcesoLocal(nombre.lower() + "-ensayo", configuracion_aislada, clave, destino, sanitizador,
                                            resultados["procesos"], modo=modo)
                    instancias.append(servidor)
                    await servidor.iniciar()
                    await caso(nombre, funcion(servidor, contexto, clave, destino, sanitizador))
                    await servidor.detener()
            finally:
                await contexto.close()
                await navegador.close()
    except Exception as error:
        resultados["error_general"] = sanitizador.limpiar(" ".join(str(error).split()) or type(error).__name__)
    finally:
        for instancia in instancias:
            await instancia.detener()
        resultados["finalizacion"] = ahora()
        resultados["conservacion"] = {ruta: huella(RAIZ / ruta) == valor for ruta, valor in linea_base["huellas"].items()}
        resultados["todos_los_protegidos_identicos"] = all(resultados["conservacion"].values())
        resultados["todos_los_hijos_detenidos"] = all(p["detenido"] for p in resultados["procesos"])
        escribir_nuevo(destino / "resultados-locales.json", sanitizador.limpiar(json.dumps(resultados, ensure_ascii=False, indent=2)) + "\n")
    return int("error_general" in resultados or len(resultados["casos"]) != 7
               or not all(c["aprobado"] for c in resultados["casos"])
               or not resultados["todos_los_protegidos_identicos"] or not resultados["todos_los_hijos_detenidos"])


if __name__ == "__main__":
    analizador = argparse.ArgumentParser(description="Verificación dirigida LOCAL, sin secretos en argumentos.")
    analizador.add_argument("--servidor", choices=("lento", "html"))
    analizador.add_argument("--carpeta")
    analizador.add_argument("--linea-base")
    argumentos = analizador.parse_args()
    try:
        if argumentos.servidor:
            asyncio.run(servir_ensayo(argumentos.servidor))
        else:
            if not argumentos.carpeta or not argumentos.linea_base:
                raise RuntimeError("Se necesitan una carpeta nueva y la línea base privada.")
            sys.exit(asyncio.run(principal(argumentos)))
    except Exception:
        print("No se completó la verificación; consulta únicamente los registros sanitizados, sin publicar configuración privada.")
        sys.exit(1)
