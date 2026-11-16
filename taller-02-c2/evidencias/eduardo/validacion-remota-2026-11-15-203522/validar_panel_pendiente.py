"""Una comprobación REMOTA del cliente con clave ficticia; no reintenta agentes.

La fase autenticada original ya finalizó sin solicitudes. Este caso no requiere
la clave remota y nunca lee el campo de clave ni cabeceras. Sin interceptación de
red, reloj virtual, cambios del servidor, credenciales locales ni fallas inducidas.
"""

import asyncio
import hashlib
import json
from pathlib import Path
import time

from playwright.async_api import async_playwright

from validar_remoto import (
    DESTINO, FICTICIA, URL, ahora, captura, cuerpo_seguro, guardar,
    metadatos, observar_solicitudes,
)


async def validar():
    nombre = "resultados-panel-pendiente.json"
    if (DESTINO / nombre).exists():
        raise FileExistsError("La prueba del panel ya tiene resultados; no reenviar.")
    original = json.loads((DESTINO / "resultados-autenticados.json").read_text(encoding="utf-8"))
    if original["solicitudes_panel_observadas"] or original["casos"]:
        raise RuntimeError("Revisar manualmente los casos originales antes de otra comprobación.")
    resultado = metadatos("panel pendiente; rechazo real con clave ficticia")
    resultado["alcance"] = "Espera y guardia del cliente durante un único rechazo 401; no autenticación válida ni respuesta de agente."
    resultado["sin_reintento_autenticado"] = True
    resultado["sha256_ejecutor"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    capturas, solicitudes = [], []
    pregunta = "Validación del panel: necesito el programa de una feria infantil de 3 horas desde las 15:00, con datos de demostración."
    resultado["pregunta"] = pregunta
    async with async_playwright() as p:
        navegador = await p.chromium.launch(channel="chrome", headless=True)
        resultado["navegador"] = {"canal": "chrome", "version": navegador.version, "sin_ventana": True}
        contexto = await navegador.new_context(viewport={"width": 1280, "height": 960}, locale="es-CL", service_workers="block")
        pagina = await contexto.new_page()
        pagina.set_default_timeout(10000)
        pagina.set_default_navigation_timeout(45000)
        observar_solicitudes(pagina, solicitudes)
        try:
            await pagina.goto(URL, wait_until="load", timeout=45000)
            await pagina.locator("#clave").fill(FICTICIA)
            await pagina.locator("#formulario-acceso button").click()
            resultado["post_antes_de_enviar"] = len(solicitudes)
            inicio = time.perf_counter()
            async with pagina.expect_response(lambda r: r.url == URL + "panel/consultar" and r.request.method == "POST", timeout=45000) as pendiente:
                resultado["espera_inmediata"] = await pagina.evaluate("""pregunta => {
                  const entrada=document.querySelector('#pregunta'), form=document.querySelector('#formulario');
                  entrada.value=pregunta; form.requestSubmit();
                  const estado={fecha:new Date().toISOString(), enviar_bloqueado:document.querySelector('#enviar').disabled,
                    sugerencias_bloqueadas:[...document.querySelectorAll('.sugerencia')].every(e=>e.disabled),
                    aria_busy:document.querySelector('#conversacion').getAttribute('aria-busy'),
                    indicador:!!document.querySelector('.indicador'), estado:document.querySelector('#estado-consulta').textContent};
                  entrada.value=pregunta;
                  entrada.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true,cancelable:true}));
                  form.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));
                  document.querySelector('#enviar').click();
                  document.querySelector('.sugerencia').click();
                  estado.intentos_extra=['Enter con texto no vacío','submit programático con texto no vacío','click sobre Enviar deshabilitado','click sobre sugerencia deshabilitada'];
                  return estado;
                }""", pregunta)
                resultado["aria_busy_antes_captura"] = await pagina.locator("#conversacion").get_attribute("aria-busy")
                await captura(pagina, "07-espera-panel-rechazo-real.png", "REMOTO; espera natural de una solicitud con clave ficticia, sin retener ni modificar respuestas. No consulta autorizada ni respuesta de agente.", capturas)
                resultado["aria_busy_despues_captura"] = await pagina.locator("#conversacion").get_attribute("aria-busy")
            respuesta = await pendiente.value
            resultado["http"] = respuesta.status
            resultado["cuerpo"] = await cuerpo_seguro(respuesta)
            resultado["segundos_hasta_cuerpo"] = round(time.perf_counter() - inicio, 3)
            await pagina.locator("#acceso").wait_for(state="visible", timeout=10000)
            resultado["rechazo"] = {
                "fecha": ahora(), "aviso": await pagina.locator("#error-acceso").inner_text(),
                "pregunta_conservada": await pagina.locator("#pregunta").input_value() == pregunta,
                "campo_clave_vacio": await pagina.locator("#clave").evaluate("e => e.value === ''"),
                "aria_busy": await pagina.locator("#conversacion").get_attribute("aria-busy"),
                "enviar_habilitado": await pagina.locator("#enviar").is_enabled(),
                "sugerencias_habilitadas": await pagina.locator(".sugerencia").evaluate_all("elementos => elementos.every(e => !e.disabled)"),
                "indicadores_restantes": await pagina.locator(".indicador").count(),
            }
            await captura(pagina, "08-panel-recuperado-tras-401.png", "REMOTO; rechazo 401 esperado tras la prueba de guardia; pregunta conservada y clave vacía. No error inducido de Heroku/Gemini.", capturas)
            resultado["numero_post_tras_rechazo"] = len(solicitudes)
            # Volver al historial con la misma clave ficticia no hace una consulta.
            await pagina.locator("#clave").fill(FICTICIA)
            await pagina.locator("#formulario-acceso button").click()
            resultado["antes_nueva_conversacion"] = {
                "mensajes_usuario": await pagina.locator(".mensaje.usuario").count(),
                "pregunta": await pagina.locator("#pregunta").input_value(),
            }
            antes = len(solicitudes)
            await pagina.locator("#nueva-conversacion").click()
            resultado["nueva_conversacion"] = {
                "fecha": ahora(), "mensajes_total": await pagina.locator(".mensaje").count(),
                "mensajes_usuario": await pagina.locator(".mensaje.usuario").count(),
                "entrada_vacia": await pagina.locator("#pregunta").input_value() == "",
                "indicadores_restantes": await pagina.locator(".indicador").count(),
                "historial": await pagina.locator("#conversacion").inner_text(),
                "post_adicionales": len(solicitudes) - antes,
            }
            await captura(pagina, "09-nueva-conversacion-tras-rechazo.png", "REMOTO; Nueva conversación elimina la pregunta real rechazada, su borrador y el historial; solo saludo. No consulta autorizada ni prueba de memoria del servidor.", capturas)
        except Exception as error:
            resultado["interrupcion_instrumental"] = {"fecha": ahora(), "tipo": type(error).__name__, "decision": "Sin reintento; no se atribuye automáticamente a Heroku ni se aprueban casos incompletos."}
        finally:
            resultado["solicitudes_panel_observadas"] = solicitudes
            resultado["numero_post_total"] = len(solicitudes)
            resultado["fecha_fin"] = ahora()
            guardar("capturas-panel-pendiente.json", capturas)
            guardar(nombre, resultado)
            await navegador.close()
    print("Comprobación única del panel finalizada; sin reintentos autenticados ni cabeceras guardadas.")


if __name__ == "__main__":
    asyncio.run(validar())
