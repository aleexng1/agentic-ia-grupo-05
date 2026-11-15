"""Repite únicamente R10/R12 tras dos límites del instrumental de Windows.

El chequeo de un puerto detenido acepta ConnectError y ConnectTimeout. Para
R12 no se espera indefinidamente response.text() de Playwright sobre un fetch
cuyo cuerpo el panel descarta: se comprueba primero la interfaz y se obtiene
el HTML con una segunda solicitud httpx, rotulada como tal. No usa Gemini.
"""

import argparse
import asyncio
import json
import os
from pathlib import Path
import re
import secrets
import sys
import time

import httpx
from dotenv import dotenv_values
from playwright.async_api import async_playwright, expect

ORIGEN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ORIGEN / "complemento"))
import verificar_complemento as complemento  # noqa: E402

anterior = complemento.anterior


async def r10(configuracion, contexto, clave, destino, sanitizador, procesos, instancias):
    registro = {"caso": "R10", "fecha": anterior.ahora(), "entorno": "LOCAL app:app de ensayo propia",
                "pregunta": anterior.PREGUNTA_R10, "aprobado": False,
                "esperado": "Desconexión real al detener solo el servidor propio: aviso, pregunta conservada y controles recuperados; restaurarlo en el mismo puerto."}
    original = complemento.ServidorPropio("r10-antes", configuracion, clave, destino, sanitizador, procesos)
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
        async with httpx.AsyncClient(timeout=5, trust_env=False) as cliente:
            try:
                await cliente.get(original.direccion + "/salud")
                raise AssertionError("El servidor debía estar detenido.")
            except (httpx.ConnectError, httpx.ConnectTimeout) as error:
                registro["salud_durante_detencion"] = type(error).__name__
        inicio = time.perf_counter()
        await anterior.enviar(pagina, anterior.PREGUNTA_R10)
        aviso = pagina.locator(".mensaje.asistente .burbuja").last
        await expect(aviso).to_contain_text("No se pudo conectar con el servidor.", timeout=30000)
        await anterior.verificar_recuperacion(pagina, anterior.PREGUNTA_R10)
        assert fallos
        registro.update(aviso=await aviso.inner_text(), fallos_red=fallos, pregunta_conservada=True,
                        controles_recuperados=True, espera_real_segundos=round(time.perf_counter() - inicio, 3))
        registro["captura"] = await anterior.captura(pagina, destino, "r10-desconexion-real.png",
            "R10 · desconexión REAL · se detuvo únicamente el árbol del servidor LOCAL propio · no se cortó la red", sanitizador)
        registro["aprobado"] = True
    except Exception as error:
        registro["error"] = sanitizador.limpiar(type(error).__name__ + ": " + " ".join(str(error).split()))
        registro["texto_observado"] = await pagina.locator("#conversacion").inner_text()
        registro["captura_error"] = await anterior.captura(pagina, destino, "r10-no-aprobado.png",
            "R10 · resultado NO APROBADO conservado sin alterar · solo servidor propio", sanitizador)
    finally:
        await original.detener()
        restaurado = complemento.ServidorPropio("r10-restaurado", configuracion, clave, destino, sanitizador, procesos,
                                                puerto=original.puerto)
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
                                   "limpieza_final": "Se restauró y comprobó primero; después se cerraron solo los procesos propios de esta validación."}
        await pagina.goto(restaurado.direccion, wait_until="networkidle", timeout=15000)
        registro["captura_restauracion"] = await anterior.captura(pagina, destino, "r10-restaurado.png",
            "R10 · servidor de ensayo RESTAURADO en el mismo puerto · /salud 200 · panel 200 · POST autorizado 400", sanitizador)
        await pagina.close()
        await restaurado.detener()
    return registro


async def r12(servidor, contexto, clave, destino, sanitizador):
    registro = {"caso": "R12", "fecha": anterior.ahora(), "entorno": "LOCAL aislado, servidor de ensayo sin proveedor",
                "clasificacion": "Falla inducida en entorno controlado; NO es falla real de Gemini ni Heroku.",
                "pregunta": anterior.PREGUNTA_R12,
                "esperado": "200 text/html real: aviso no JSON, cuerpo no insertado ni ejecutado, pregunta y controles recuperados."}
    pagina = await anterior.nueva_pagina(contexto, servidor.direccion, clave)
    async with pagina.expect_response(lambda r: r.url.endswith("/panel/consultar"), timeout=15000) as pendiente:
        await anterior.enviar(pagina, anterior.PREGUNTA_R12)
    respuesta = await pendiente.value
    registro["respuesta_al_panel"] = {"http": respuesta.status, "tipo": respuesta.headers.get("content-type")}
    aviso = pagina.locator(".mensaje.asistente .burbuja").last
    await expect(aviso).to_contain_text("El servidor devolvió una respuesta que no es JSON.", timeout=10000)
    await anterior.verificar_recuperacion(pagina, anterior.PREGUNTA_R12)
    assert respuesta.status == 200 and registro["respuesta_al_panel"]["tipo"].startswith("text/html")
    assert await pagina.locator("#html-ensayo").count() == 0
    assert await pagina.evaluate("window.htmlEnsayoEjecutado === undefined")
    assert "HTML_CONTROLADO_R12" not in await pagina.locator("#conversacion").inner_text()
    # Comprobación HTTP adicional: no se atribuye este cuerpo a una lectura del navegador.
    async with httpx.AsyncClient(timeout=10, trust_env=False) as cliente:
        directa = await cliente.post(servidor.direccion + "/panel/consultar", headers={"X-API-Key": clave},
                                     json={"texto": anterior.PREGUNTA_R12, "context_id": "r12-cliente-http-adicional"})
    assert directa.status_code == 200 and directa.text == anterior.HTML_ENSAYO
    registro["segunda_solicitud_httpx_al_mismo_ensayo"] = {"http": directa.status_code,
        "tipo": directa.headers.get("content-type"), "cuerpo_html_recibido": directa.text,
        "observacion": "Solicitud adicional para conservar el HTML crudo de ensayo; no es una segunda consulta a Gemini ni una captura del aviso del cliente HTTP."}
    registro.update(aviso=await aviso.inner_text(), html_no_insertado=True, script_no_ejecutado=True,
                    pregunta_conservada=True, controles_recuperados=True, aprobado=True)
    registro["captura"] = await anterior.captura(pagina, destino, "r12-html-controlado.png",
        "R12 · FALLA INDUCIDA en entorno controlado · HTTP real 200 text/html · sin Gemini ni Heroku", sanitizador)
    await pagina.close()
    return registro


async def principal(argumentos):
    destino = Path(argumentos.carpeta).resolve()
    if not destino.is_relative_to(anterior.EVIDENCIAS) or destino == anterior.EVIDENCIAS:
        raise RuntimeError("El destino debe estar en evidencias/eduardo.")
    destino.mkdir(parents=True, exist_ok=True)
    if any(p.suffix != ".py" for p in destino.iterdir()):
        raise RuntimeError("No se sobrescriben resultados anteriores.")
    configuracion = {**{k: v for k, v in dotenv_values(anterior.PROYECTO / ".env").items() if v is not None}, **os.environ}
    sanitizador = anterior.Sanitizador(configuracion)
    clave = secrets.token_urlsafe(32)
    sanitizador.agregar(clave)
    aislado = {k: v for k, v in os.environ.items() if not re.search(r"KEY|TOKEN|SECRET|PASSWORD|CLAVE|CREDENTIAL", k, re.I)}
    aislado.update(GOOGLE_API_KEY="", GEMINI_API_KEY="", GOOGLE_GENAI_USE_VERTEXAI="false", GOOGLE_APPLICATION_CREDENTIALS="")
    resultados = {"inicio": anterior.ahora(), "base": "d8cce1337b7caf0bcd63df2d9ce21d9dc96a3f91",
                  "sha256_panel_probado": anterior.huella(anterior.PANEL),
                  "sha256_ejecutor": anterior.huella(Path(__file__).resolve()),
                  "sha256_ejecutor_original": anterior.huella(ORIGEN / "verificar_pendientes.py"),
                  "sha256_ejecutor_complemento": anterior.huella(ORIGEN / "complemento/verificar_complemento.py"),
                  "consultas_a_gemini": 0, "suites_completas_repetidas": False, "casos": [], "procesos": []}
    instancias = []
    try:
        async with async_playwright() as herramienta:
            navegador = await herramienta.chromium.launch(channel="chrome", headless=True, timeout=30000)
            resultados["navegador"] = navegador.version
            contexto = await navegador.new_context(viewport={"width": 1280, "height": 960}, locale="es-CL",
                                                   reduced_motion="reduce", service_workers="block")
            try:
                for nombre in ("R10", "R12"):
                    try:
                        if nombre == "R10":
                            operacion = r10(configuracion, contexto, clave, destino, sanitizador, resultados["procesos"], instancias)
                        else:
                            servidor = complemento.ServidorPropio("r12-html", aislado, clave, destino, sanitizador,
                                                                  resultados["procesos"], modo="html")
                            instancias.append(servidor)
                            await servidor.iniciar()
                            operacion = r12(servidor, contexto, clave, destino, sanitizador)
                        registro = await asyncio.wait_for(operacion, timeout=90)
                    except Exception as error:
                        registro = {"caso": nombre, "aprobado": False,
                                    "error": sanitizador.limpiar(type(error).__name__ + ": " + " ".join(str(error).split()))}
                    resultados["casos"].append(registro)
                    anterior.escribir_nuevo(destino / f"{nombre.lower()}-resultado.json",
                        sanitizador.limpiar(json.dumps(registro, ensure_ascii=False, indent=2)) + "\n")
                    print(f"{nombre}: {'APROBADO' if registro['aprobado'] else 'NO APROBADO'}", flush=True)
                    if nombre == "R12":
                        await servidor.detener()
            finally:
                await asyncio.wait_for(contexto.close(), timeout=15)
                await asyncio.wait_for(navegador.close(), timeout=15)
    finally:
        for servidor in instancias:
            await servidor.detener()
        resultados["finalizacion"] = anterior.ahora()
        resultados["todos_los_hijos_detenidos"] = all(p["detenido"] for p in resultados["procesos"])
        anterior.escribir_nuevo(destino / "resultados-finalizacion.json",
            sanitizador.limpiar(json.dumps(resultados, ensure_ascii=False, indent=2)) + "\n")
    return int(not all(c["aprobado"] for c in resultados["casos"]))


if __name__ == "__main__":
    analizador = argparse.ArgumentParser(description="Finalización dirigida R10/R12, sin proveedor.")
    analizador.add_argument("--carpeta", required=True)
    try:
        sys.exit(asyncio.run(principal(analizador.parse_args())))
    except Exception:
        print("Verificación incompleta; revisar solo los registros sanitizados.")
        sys.exit(1)
