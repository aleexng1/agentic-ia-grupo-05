"""Validación REMOTA dirigida; sin dotenv, claves locales, HAR, trazas ni cambios en Heroku.

Ejecutar con la .venv existente: validar_remoto.py publico | autenticado.
La fase autenticada abre Chrome y espera el ingreso privado de CLAVE_API por la persona.
Nunca lee el campo de clave ni cabeceras de solicitudes. No hay reintentos de consultas.
Cada fase rechaza sobrescribir sus resultados y guarda evidencia por caso inmediatamente.
"""

import argparse
import asyncio
from datetime import datetime
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.parse import urlsplit

import httpx
from playwright.async_api import async_playwright


DESTINO = Path(__file__).resolve().parent
RAIZ = DESTINO.parents[3]
URL = "https://grupo05-taller2-seba-94d12914f3eb.herokuapp.com/"
PR = "https://api.github.com/repos/aleexng1/agentic-ia-grupo-05/pulls/83"
FICTICIA = "clave-ficticia-validacion-remota-no-es-un-secreto"
PREGUNTAS = (
    ("matias", "Agente de Matias", "Necesito un programa para una feria cultural familiar de 3 horas, desde las 16:00. Indica actividades, horarios y cualquier tiempo libre, con las condiciones de demostración."),
    ("alex", "Agente de Alex", "Necesito un recinto interior para una feria tecnológica de 80 personas. Recomienda opciones con aforo, características, accesibilidad y advertencias de disponibilidad; no reserves nada."),
    ("eduardo", "Agente de Eduardo", "¿Cuál es el presupuesto simulado de una feria tecnológica para 80 personas y 4 horas? Indica partidas, total en CLP, supuestos y advertencias; no realices pagos."),
    ("sebastian", "Agente de Sebastian", "Necesito catering para una feria tecnológica de 80 personas, de 10:00 a 14:00 (4 horas), con 10 vegetarianas y 5 sin gluten. Indica servicios, horarios, dietas y litros de agua; datos simulados, sin contratar nada."),
)


def ahora():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def limpiar(texto):
    texto = re.sub(r"AIza[0-9A-Za-z_-]{20,}", "[credencial omitida]", texto)
    texto = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._-]{8,}", r"\1[credencial omitida]", texto)
    return re.sub(
        r"(?i)(x-api-key|authorization|google_api_key|clave_api)(\s*[:=]\s*)[^\s,;\"']+",
        r"\1\2[credencial omitida]", texto,
    )


def guardar(nombre, datos):
    texto = limpiar(json.dumps(datos, ensure_ascii=False, indent=2)) + "\n"
    with (DESTINO / nombre).open("x", encoding="utf-8", newline="\n") as salida:
        salida.write(texto)


def git(*argumentos):
    return subprocess.run(
        ["git", *argumentos], cwd=RAIZ, capture_output=True, check=True,
        text=True, encoding="utf-8", timeout=15,
    ).stdout.strip()


def metadatos(fase):
    return {
        "fecha_inicio": ahora(), "entorno": "REMOTO · Heroku · HTTPS", "url": URL,
        "fase": fase, "release_reportada": "v10",
        "fuente_release": "Sebastián, comunicado por Eduardo en la solicitud; no verificada en Heroku CLI",
        "commit_desplegado": None, "estado_commit_desplegado": "POR CONFIRMAR",
        "rama_local": git("branch", "--show-current"), "head_local": git("rev-parse", "HEAD"),
        "origin_main_referencia_local_no_despliegue": git("rev-parse", "origin/main"),
        "versiones": {"python": sys.version.split()[0], "playwright": version("playwright"), "httpx": version("httpx")},
        "restricciones": "Sin .env, claves locales, configuración/despliegues/reinicios remotos, fallas inducidas, mocks, interceptación HTTP, reloj virtual ni suites locales.",
    }


async def captura(pagina, nombre, alcance, manifiesto):
    # El campo se oculta por completo, incluso si accidentalmente siguiera visible.
    texto = await pagina.locator("body").inner_text(timeout=10000)
    if re.search(r"AIza[0-9A-Za-z_-]{20,}", texto):
        raise RuntimeError("Captura cancelada por posible credencial visible.")
    archivo = DESTINO / nombre
    if archivo.exists():
        raise FileExistsError("La captura ya existe; usar otra carpeta.")
    await pagina.screenshot(
        path=str(archivo), full_page=True, mask=[pagina.locator("#clave")],
        animations="disabled", timeout=15000,
    )
    manifiesto.append({
        "archivo": nombre, "fecha": ahora(), "url": pagina.url, "alcance": alcance,
        "viewport_configurado": pagina.viewport_size,
        "sha256": hashlib.sha256(archivo.read_bytes()).hexdigest(),
    })


async def geometria(pagina):
    return await pagina.evaluate("""() => {
      const caja = selector => {
        const e = document.querySelector(selector), r = e.getBoundingClientRect();
        return {x:r.x, y:r.y, ancho:r.width, alto:r.height, scrollWidth:e.scrollWidth, clientWidth:e.clientWidth};
      };
      return {ancho_interior:innerWidth, ancho_pagina:document.documentElement.scrollWidth,
        desborde_horizontal:document.documentElement.scrollWidth > innerWidth,
        chat:caja('.chat'), agentes:caja('.columna'), entrada:caja('#pregunta'),
        botones:[...document.querySelectorAll('#panel-chat button')].map(e => ({texto:e.textContent.trim(), alto:e.getBoundingClientRect().height})),
        fuente_entrada:getComputedStyle(document.querySelector('#pregunta')).fontSize};
    }""")


def observar_solicitudes(pagina, registro):
    def recibir(solicitud):
        if solicitud.method != "POST" or solicitud.url != URL + "panel/consultar":
            return
        # Lista positiva: solamente cuerpo del contrato; nunca headers/all_headers.
        cuerpo = solicitud.post_data_json or {}
        registro.append({
            "fecha": ahora(), "url": solicitud.url, "metodo": "POST",
            "cuerpo": {k: cuerpo[k] for k in ("texto", "context_id") if k in cuerpo},
        })
    pagina.on("request", recibir)


async def cuerpo_seguro(respuesta):
    tipo = respuesta.headers.get("content-type", "")
    if "json" not in tipo.lower():
        return {"no_json": True, "content_type": tipo}
    try:
        datos = await asyncio.wait_for(respuesta.json(), timeout=15)
    except Exception:
        return {"json_no_legible": True}
    if not isinstance(datos, dict):
        return {"contrato_no_objeto": True}
    return {k: datos[k] for k in ("respuesta", "context_id", "agente", "motivo", "detail") if k in datos}


async def publico():
    if (DESTINO / "resultados-publicos.json").exists():
        raise FileExistsError("La fase pública ya tiene resultados.")
    resultados = metadatos("publica")
    resultados["estado_git_inicial"] = git("status", "--porcelain=v1", "--untracked-files=all")
    capturas, solicitudes = [], []
    async with httpx.AsyncClient(timeout=45, follow_redirects=False, trust_env=False) as cliente:
        for nombre, direccion in (("salud", URL + "salud"), ("pr83", PR)):
            inicio = time.perf_counter()
            respuesta = await cliente.get(direccion)
            dato = respuesta.json()
            if nombre == "pr83":
                dato = {k: dato.get(k) for k in ("number", "state", "merged", "merged_at", "updated_at", "html_url")}
            resultados[nombre] = {"fecha": ahora(), "url": direccion, "http": respuesta.status_code, "segundos": round(time.perf_counter() - inicio, 3), "cuerpo": dato}
    async with async_playwright() as p:
        navegador = await p.chromium.launch(channel="chrome", headless=True)
        resultados["navegador"] = {"canal": "chrome", "version": navegador.version, "sin_ventana": True}
        contexto = await navegador.new_context(viewport={"width": 1280, "height": 960}, locale="es-CL", service_workers="block")
        pagina = await contexto.new_page()
        pagina.set_default_timeout(10000)
        pagina.set_default_navigation_timeout(45000)
        observar_solicitudes(pagina, solicitudes)
        respuesta = await pagina.goto(URL, wait_until="load", timeout=45000)
        html = await asyncio.wait_for(respuesta.body(), timeout=15)
        local = RAIZ / "taller-02-c2/proyecto/src/comun/panel.html"
        resultados["panel"] = {
            "fecha": ahora(), "url_final": pagina.url, "http": respuesta.status,
            "titulo": await pagina.title(), "tls": await respuesta.security_details(),
            "cabeceras_respuesta_publicas": {k: v for k, v in respuesta.headers.items() if k in ("content-type", "cache-control", "x-content-type-options", "referrer-policy", "date")},
            "sha256_html_remoto": hashlib.sha256(html).hexdigest(),
            "html_identico_archivo_local": html == local.read_bytes(),
            "limite_identidad": "La coincidencia de un HTML no identifica el commit ni verifica la release.",
        }
        await captura(pagina, "01-ingreso-escritorio.png", "Panel REMOTO real; Chrome escritorio 1280×960; sin clave ni autenticación.", capturas)
        await pagina.locator("#formulario-acceso button").click()
        resultados["ingreso_vacio_interfaz"] = {
            "fecha": ahora(),
            "campo_requerido_invalido": await pagina.locator("#clave").evaluate("e => e.validity.valueMissing"),
            "panel_oculto": await pagina.locator("#panel-chat").is_hidden(),
            "post_panel": len(solicitudes),
            "limite": "Validación de formulario; no sustituye el rechazo HTTP sin cabecera.",
        }
        resultados["sin_clave_http"] = await pagina.evaluate("""async () => {
          const inicio = performance.now();
          const r = await fetch('/panel/consultar', {method:'POST', headers:{'Content-Type':'application/json'},
            body:JSON.stringify({texto:'¿Cuál es el presupuesto simulado de una feria tecnológica para 80 personas y 4 horas?',context_id:'eduardo-remoto-sin-clave-20261115'}),
            cache:'no-store', credentials:'omit', redirect:'error', signal:AbortSignal.timeout(45000)});
          const tipo = r.headers.get('content-type') || '';
          const datos = tipo.includes('json') ? await r.json() : {};
          return {fecha:new Date().toISOString(), http:r.status, content_type:tipo, detail:datos.detail || null, segundos:(performance.now()-inicio)/1000};
        }""")
        guardar("r06-sin-clave.json", resultados["sin_clave_http"])
        await pagina.locator("#clave").fill(FICTICIA)
        await pagina.locator("#formulario-acceso button").click()
        pregunta = PREGUNTAS[2][2]
        await pagina.locator("#pregunta").fill(pregunta)
        async with pagina.expect_response(lambda r: r.url == URL + "panel/consultar" and r.request.method == "POST", timeout=45000) as pendiente:
            await pagina.locator("#enviar").click()
        respuesta = await pendiente.value
        cuerpo = await cuerpo_seguro(respuesta)
        await pagina.locator("#acceso").wait_for(state="visible", timeout=10000)
        resultados["clave_ficticia_panel"] = {
            "fecha": ahora(), "http": respuesta.status, "cuerpo": cuerpo,
            "aviso": await pagina.locator("#error-acceso").inner_text(),
            "pregunta_conservada": await pagina.locator("#pregunta").input_value() == pregunta,
            "campo_clave_vacio": await pagina.locator("#clave").evaluate("e => e.value === ''"),
            "panel_oculto": await pagina.locator("#panel-chat").is_hidden(),
        }
        guardar("r07-clave-ficticia.json", resultados["clave_ficticia_panel"])
        await captura(pagina, "02-clave-ficticia-rechazada.png", "401 real de Heroku con clave ficticia; aviso nativo; sin acceso autorizado.", capturas)
        await pagina.locator("#clave").fill(FICTICIA)
        await pagina.locator("#formulario-acceso button").click()
        antes = len(solicitudes)
        await pagina.locator("#pregunta").fill("Borrador de prueba de limpieza; no se envía.")
        await pagina.locator("#nueva-conversacion").click()
        resultados["nueva_conversacion_solo_interfaz"] = {
            "fecha": ahora(), "mensajes_usuario": await pagina.locator(".mensaje.usuario").count(),
            "mensajes_total": await pagina.locator(".mensaje").count(),
            "borrador_vacio": await pagina.locator("#pregunta").input_value() == "",
            "post_adicionales": len(solicitudes) - antes,
            "geometria_escritorio": await geometria(pagina),
            "limite": "Sin consulta autorizada; no acredita todavía el cambio de context_id enviado al servidor.",
        }
        await captura(pagina, "03-nueva-conversacion-solo-interfaz.png", "Panel REMOTO; limpieza de interfaz con clave ficticia cargada, sin enviar consulta; escritorio.", capturas)
        movil = await navegador.new_context(**p.devices["Pixel 7"], locale="es-CL", service_workers="block")
        pm = await movil.new_page()
        pm.set_default_timeout(10000)
        await pm.goto(URL, wait_until="load", timeout=45000)
        await captura(pm, "04-ingreso-movil-emulado.png", "Panel REMOTO; emulación Pixel 7 en Chrome sin ventana, no teléfono físico; sin clave.", capturas)
        await pm.locator("#clave").fill(FICTICIA)
        await pm.locator("#formulario-acceso button").click()
        resultados["movil_emulado"] = {"dispositivo_emulado": "Pixel 7", "fisico": False, "consulta_autorizada": False, "geometria": await geometria(pm)}
        await captura(pm, "05-chat-movil-emulado-sin-consulta.png", "Panel REMOTO; emulación Pixel 7; clave ficticia cargada, sin consulta; solo saludo inicial.", capturas)
        await pm.set_viewport_size({"width": 320, "height": 800})
        resultados["movil_320_emulado"] = await geometria(pm)
        await captura(pm, "06-chat-320-emulado-sin-consulta.png", "Panel REMOTO; ancho emulado 320 px en contexto móvil Chrome; sin consulta autorizada; no dispositivo real.", capturas)
        await navegador.close()
    resultados["solicitudes_panel_observadas"] = solicitudes
    resultados["fecha_fin"] = ahora()
    guardar("capturas-publicas.json", capturas)
    guardar("resultados-publicos.json", resultados)
    print("Fase pública completada. Resultados guardados; sin cabeceras ni claves.", flush=True)


async def autenticado():
    if (DESTINO / "resultados-autenticados.json").exists():
        raise FileExistsError("La fase autenticada ya tiene resultados; no repetir consultas.")
    resultados = metadatos("autenticada con ingreso privado en navegador")
    capturas, solicitudes, casos = [], [], []
    resultados["casos"] = casos
    async with async_playwright() as p:
        navegador = await p.chromium.launch(channel="chrome", headless=False)
        resultados["navegador"] = {"canal": "chrome", "version": navegador.version, "sin_ventana": False}
        contexto = await navegador.new_context(viewport={"width": 1280, "height": 960}, locale="es-CL", service_workers="block")
        pagina = await contexto.new_page()
        pagina.set_default_timeout(10000)
        pagina.set_default_navigation_timeout(45000)
        observar_solicitudes(pagina, solicitudes)
        try:
            await pagina.goto(URL, wait_until="load", timeout=45000)
            print("Chrome abierto: ingresar privadamente SOLO CLAVE_API vigente de Heroku y pulsar Continuar al chat. No enviar preguntas. Cerrar esta ventana si la clave no está disponible.", flush=True)
            # Solo observa la visibilidad del chat: no lee ni transfiere la clave.
            await pagina.locator("#panel-chat").wait_for(state="visible", timeout=900000)
            resultados["ingreso_privado_detectado"] = ahora()
            for nombre, esperado, pregunta in PREGUNTAS:
                await pagina.locator("#nueva-conversacion").click()
                limpieza = {
                    "fecha": ahora(), "mensajes_usuario": await pagina.locator(".mensaje.usuario").count(),
                    "mensajes_total": await pagina.locator(".mensaje").count(),
                    "borrador_vacio": await pagina.locator("#pregunta").input_value() == "",
                }
                antes = len(solicitudes)
                inicio = time.perf_counter()
                caso = {"caso": nombre, "fecha_inicio": ahora(), "pregunta": pregunta, "agente_esperado": esperado, "nueva_conversacion_previa": limpieza}
                async with pagina.expect_response(lambda r: r.url == URL + "panel/consultar" and r.request.method == "POST", timeout=70000) as pendiente:
                    # Los intentos extra ocurren en el mismo turno JS, con una pregunta
                    # no vacía, antes de que pueda llegar la respuesta: no se retrasa la red.
                    caso["espera_inmediata"] = await pagina.evaluate("""pregunta => {
                      const entrada=document.querySelector('#pregunta'), form=document.querySelector('#formulario');
                      entrada.value=pregunta; form.requestSubmit();
                      const estado={enviar_bloqueado:document.querySelector('#enviar').disabled,
                        sugerencias_bloqueadas:[...document.querySelectorAll('.sugerencia')].every(e=>e.disabled),
                        aria_busy:document.querySelector('#conversacion').getAttribute('aria-busy'),
                        indicador:!!document.querySelector('.indicador'), estado:document.querySelector('#estado-consulta').textContent};
                      entrada.value=pregunta;
                      entrada.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true,cancelable:true}));
                      form.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));
                      estado.intentos_extra=2;
                      return estado;
                    }""", pregunta)
                    await captura(pagina, f"{nombre}-espera-real.png", f"Consulta REMOTA real para {nombre}; espera natural sin demoras inducidas; escritorio.", capturas)
                respuesta = await pendiente.value
                caso["http"] = respuesta.status
                caso["cuerpo"] = await cuerpo_seguro(respuesta)
                await pagina.wait_for_function("document.querySelector('#conversacion').getAttribute('aria-busy') === 'false'", timeout=70000)
                caso["segundos"] = round(time.perf_counter() - inicio, 3)
                caso["solicitudes_observadas"] = solicitudes[antes:]
                caso["numero_post"] = len(solicitudes) - antes
                caso["estado_consulta"] = await pagina.locator("#estado-consulta").inner_text()
                caso["historial_dom"] = await pagina.locator("#conversacion").inner_text()
                caso["metadatos_dom"] = await pagina.locator(".mensaje.asistente .hora").all_text_contents()
                caso["controles_recuperados"] = await pagina.locator("#enviar").is_enabled()
                cuerpo = caso["cuerpo"]
                caso["contrato_completo"] = all(isinstance(cuerpo.get(k), str) and cuerpo[k].strip() for k in ("respuesta", "context_id", "agente", "motivo"))
                caso["agente_correcto"] = cuerpo.get("agente") == esperado
                caso["agente_motivo_visibles"] = f"Agente: {cuerpo.get('agente')}" in caso["metadatos_dom"] and f"Motivo: {cuerpo.get('motivo')}" in caso["metadatos_dom"]
                caso["aprobacion_automatica_contrato"] = respuesta.status == 200 and caso["contrato_completo"] and caso["agente_correcto"] and caso["agente_motivo_visibles"] and caso["numero_post"] == 1
                caso["fecha_fin"] = ahora()
                casos.append(caso)
                guardar(f"{nombre}-intercambio.json", caso)
                await captura(pagina, f"{nombre}-resultado-escritorio.png", f"Resultado REMOTO real para {nombre}; interfaz nativa, scroll interno al final; escritorio.", capturas)
                if respuesta.status != 200 or caso["numero_post"] != 1:
                    resultados["detencion"] = "No se reintenta ni se envían más consultas tras rechazo, error remoto o envíos duplicados. Los restantes quedan pendientes."
                    break
                # Evidencia completa mediante expansión CSS temporal: no cambia texto ni respuestas.
                estilo = await pagina.add_style_tag(content="#conversacion {max-height:none !important; overflow:visible !important;}")
                await captura(pagina, f"{nombre}-respuesta-completa.png", f"Respuesta REMOTA íntegra para {nombre}; solo altura del historial expandida por el instrumental; no diseño nativo.", capturas)
                await estilo.evaluate("e => e.remove()")
                if nombre == "sebastian":
                    for ancho, alto in ((390, 844), (320, 800)):
                        await pagina.set_viewport_size({"width": ancho, "height": alto})
                        resultados[f"respuesta_vista_responsive_{ancho}"] = await geometria(pagina)
                        await captura(pagina, f"sebastian-respuesta-movil-{ancho}-emulado.png", f"Respuesta REMOTA real ya recibida; viewport {ancho}×{alto} emulado en Chrome escritorio, sin nueva consulta. No teléfono físico ni prueba de teclado virtual.", capturas)
                    await pagina.set_viewport_size({"width": 1280, "height": 960})
            if casos and all(c.get("http") == 200 for c in casos):
                antes = len(solicitudes)
                await pagina.locator("#nueva-conversacion").click()
                resultados["limpieza_final"] = {
                    "fecha": ahora(), "mensajes_total": await pagina.locator(".mensaje").count(),
                    "mensajes_usuario": await pagina.locator(".mensaje.usuario").count(),
                    "post_adicionales": len(solicitudes) - antes,
                    "historial": await pagina.locator("#conversacion").inner_text(),
                }
                await captura(pagina, "nueva-conversacion-final.png", "Panel REMOTO; limpieza tras consultas autorizadas, solo saludo inicial; escritorio.", capturas)
        except Exception as error:
            # No guardar mensajes de excepciones que podrían incluir estado del navegador.
            resultados["interrupcion_instrumental"] = {"fecha": ahora(), "tipo": type(error).__name__, "detalle": "Ejecución interrumpida o ventana cerrada; los casos no registrados siguen pendientes. Sin reintentos automáticos."}
        finally:
            resultados["solicitudes_panel_observadas"] = solicitudes
            resultados["agentes_no_ejecutados"] = [n for n, _, _ in PREGUNTAS if n not in {c["caso"] for c in casos}]
            resultados["fecha_fin"] = ahora()
            guardar("capturas-autenticadas.json", capturas)
            guardar("resultados-autenticados.json", resultados)
            if navegador.is_connected():
                await navegador.close()
    print("Fase autenticada finalizada; consultar resultados sin atribuir aprobación a pendientes.", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fase", choices=("publico", "autenticado"))
    argumentos = parser.parse_args()
    try:
        asyncio.run(publico() if argumentos.fase == "publico" else autenticado())
    except Exception as error:
        print(f"Instrumental detenido ({type(error).__name__}); no se imprime detalle ni se reintenta.", flush=True)
        raise SystemExit(1)
