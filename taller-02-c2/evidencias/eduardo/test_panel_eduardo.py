r"""Comprobaciones LOCAL del panel; sin Gemini ni credenciales reales.

Desde proyecto: .venv\Scripts\python -m pytest ../evidencias/eduardo/test_panel_eduardo.py
Requiere playwright como dependencia de desarrollo y Chrome instalado (o
CANAL_NAVEGADOR=msedge). Las respuestas del navegador son SIMULADAS.
Las dos pruebas xfail registran la autorización pendiente, no la aprueban.
"""

import json
import os
from datetime import datetime
from pathlib import Path
import secrets
import socket
import threading

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from playwright.sync_api import expect, sync_playwright
import uvicorn

from src.comun.panel import crear_panel


CARPETA = Path(__file__).parent
CARPETA_CAPTURAS = Path(os.getenv("CARPETA_CAPTURAS", str(CARPETA)))
FECHA = datetime.now().astimezone().date().isoformat()
RESPUESTA_SIMULADA = (
    "Presupuesto simulado: $2.173.600 CLP.\n"
    "80 personas · 4 horas (240 minutos).\n"
    "Contingencia: 10 %; tarifas ficticias, sin impuestos.\n"
    "No autoriza compras, reservas ni pagos."
)
PREGUNTA = "¿Cuál es el presupuesto simulado de una feria tecnológica para 80 personas y 4 horas?"
RESPUESTA_MARKDOWN_SIMULADA = (
    "## **Programa simulado**\n"
    "**16:00–18:00** · 60 minutos libres informados.\n"
    "Servicios: **11:00** y **13:30**; dietas **65/10/5**; agua **88 L**.\n"
    "Total de prueba: **$2.173.600 CLP**.\n"
    "No autoriza compras, reservas ni pagos."
)
TEXTO_MARKDOWN_SIMULADO = (
    "Programa simulado\n"
    "16:00–18:00 · 60 minutos libres informados.\n"
    "Servicios: 11:00 y 13:30; dietas 65/10/5; agua 88 L.\n"
    "Total de prueba: $2.173.600 CLP.\n"
    "No autoriza compras, reservas ni pagos."
)


async def responder_simulado(texto, context_id):
    """Doble de prueba: no ejecuta el coordinador, A2A ni Gemini."""
    return {
        "respuesta": RESPUESTA_SIMULADA,
        "agente": "Agente de Eduardo",
        "motivo": "La consulta solicita un presupuesto simulado.",
    }


def app_de_prueba():
    aplicacion = FastAPI()
    aplicacion.include_router(crear_panel(responder_simulado))
    return aplicacion


@pytest.fixture(scope="session")
def direccion_panel():
    """Sirve el router real en un puerto libre, únicamente en loopback."""
    listo = threading.Event()

    class ServidorLocal(uvicorn.Server):
        async def startup(self, sockets=None):
            await super().startup(sockets=sockets)
            listo.set()

    with socket.socket() as conexion:
        conexion.bind(("127.0.0.1", 0))
        puerto = conexion.getsockname()[1]
        servidor = ServidorLocal(uvicorn.Config(
            app_de_prueba(), log_level="critical", access_log=False, lifespan="off"
        ))
        hilo = threading.Thread(target=servidor.run, kwargs={"sockets": [conexion]}, daemon=True)
        hilo.start()
        try:
            assert listo.wait(timeout=10), "El servidor local no inició a tiempo."
            yield f"http://127.0.0.1:{puerto}"
        finally:
            servidor.should_exit = True
            hilo.join(timeout=10)
            assert not hilo.is_alive(), "El servidor de pruebas no se detuvo."


@pytest.fixture(scope="session")
def navegador():
    with sync_playwright() as herramienta:
        instancia = herramienta.chromium.launch(
            channel=os.getenv("CANAL_NAVEGADOR", "chrome"), headless=True, timeout=30000
        )
        yield instancia
        instancia.close()


@pytest.fixture
def pagina(navegador, direccion_panel):
    contexto = navegador.new_context(
        viewport={"width": 1280, "height": 960}, locale="es-CL",
        reduced_motion="reduce", service_workers="block"
    )
    # Nunca permitir conexiones externas durante las pruebas del navegador.
    contexto.route("**/*", lambda ruta: ruta.continue_()
                   if ruta.request.url.startswith(direccion_panel + "/") else ruta.abort())
    hoja = contexto.new_page()
    hoja.set_default_timeout(7000)
    errores = []
    hoja.on("pageerror", lambda error: errores.append("Error de JavaScript"))
    hoja.goto(direccion_panel, wait_until="networkidle", timeout=15000)
    try:
        yield hoja
        assert not errores, "Hubo errores de JavaScript en el panel."
    finally:
        contexto.close()


def ingresar(pagina):
    """Valor efímero aleatorio, nunca una clave real ni guardada en evidencias."""
    valor = secrets.token_urlsafe(24)
    pagina.locator("#clave").fill(valor)
    pagina.locator("#clave").press("Enter")
    expect(pagina.locator("#pregunta")).to_be_focused()
    expect(pagina.locator("#clave")).to_have_value("")
    return valor


def enviar(pagina, texto=PREGUNTA):
    pagina.locator("#pregunta").fill(texto)
    pagina.locator("#pregunta").press("Enter")


def datos_simulados(contexto="contexto-simulado", agente="Agente de Eduardo"):
    return {
        "respuesta": RESPUESTA_SIMULADA, "context_id": contexto,
        "agente": agente, "motivo": "La consulta solicita un presupuesto simulado.",
    }


def simular_json(pagina, datos, estado=200):
    pagina.route("**/panel/consultar", lambda ruta: ruta.fulfill(
        status=estado, content_type="application/json", body=json.dumps(datos)
    ))


def capturar(pagina, nombre, descripcion):
    assert pagina.locator("#clave").input_value() == ""
    pagina.evaluate("""(descripcion) => {
      const aviso = document.createElement('div');
      aviso.id = 'aviso-evidencia';
      aviso.textContent = descripcion;
      aviso.style.cssText = 'padding:10px;background:#172b3a;color:white;font:14px system-ui';
      document.body.prepend(aviso);
    }""", f"LOCAL · {FECHA} · {descripcion}")
    CARPETA_CAPTURAS.mkdir(parents=True, exist_ok=True)
    pagina.screenshot(path=str(CARPETA_CAPTURAS / nombre), full_page=True, animations="disabled", timeout=15000)
    pagina.locator("#aviso-evidencia").evaluate("elemento => elemento.remove()")


def test_contrato_http_y_cache_sin_proveedor():
    with TestClient(app_de_prueba()) as cliente:
        pagina = cliente.get("/")
        assert pagina.status_code == 200
        assert pagina.headers["cache-control"] == "no-store"
        assert pagina.headers["referrer-policy"] == "no-referrer"
        assert pagina.headers["x-content-type-options"] == "nosniff"
        respuesta = cliente.post("/panel/consultar", json={"texto": PREGUNTA, "context_id": "prueba"})
        assert respuesta.status_code == 200
        assert respuesta.headers["cache-control"] == "no-store"
        assert respuesta.json() == datos_simulados("prueba")


@pytest.mark.parametrize("cuerpo,estado", [({"texto": "  "}, 400), ({}, 422), ({"texto": 42}, 422)])
def test_entrada_invalida_servidor_actual(cuerpo, estado):
    with TestClient(app_de_prueba()) as cliente:
        assert cliente.post("/panel/consultar", json=cuerpo).status_code == estado


def test_adaptacion_respuesta_simple_y_contexto_opcional():
    async def responder_texto(texto, context_id):
        assert texto == "Pregunta"
        return "Sin alterar: 10 %; 240 minutos."

    aplicacion = FastAPI()
    aplicacion.include_router(crear_panel(responder_texto))
    with TestClient(aplicacion) as cliente:
        resultado = cliente.post("/panel/consultar", json={"texto": "  Pregunta  "}).json()
        assert resultado["respuesta"] == "Sin alterar: 10 %; 240 minutos."
        assert resultado["context_id"]
        assert resultado["agente"] == resultado["motivo"] == ""


@pytest.mark.xfail(reason="DEPENDENCIA Matías: CLAVE_API aún no se valida en el servidor.", strict=False)
@pytest.mark.parametrize("cabecera", ["ausente", "incorrecta"])
def test_autorizacion_real_pendiente_en_app(cabecera, monkeypatch):
    """Rutas de app.py reales; solo el grafo/proveedor se sustituye para no usar red."""
    import app as modulo_app
    from src.coordinador import graph as modulo_graph

    llamadas = []

    async def sin_descubrir(imprimir=False):
        llamadas.append("coordinador ejecutado sin autorización")

    class GrafoSimulado:
        async def ainvoke(self, entrada, config):
            return await responder_simulado("", "")

    monkeypatch.setenv("CLAVE_API", secrets.token_urlsafe(24))
    monkeypatch.setattr(modulo_graph, "inicializar_supervisor", sin_descubrir)
    monkeypatch.setattr(modulo_graph, "graph", GrafoSimulado())
    cabeceras = {} if cabecera == "ausente" else {"X-API-Key": secrets.token_urlsafe(24)}
    with TestClient(modulo_app.app) as cliente:
        respuesta = cliente.post("/panel/consultar", headers=cabeceras,
                                 json={"texto": PREGUNTA, "context_id": "diagnostico-acceso"})
    assert respuesta.status_code == 401, "El servidor debe rechazar la consulta antes de invocar al coordinador."
    assert not llamadas


def test_ingreso_enmascarado_sin_validacion_ficticia(pagina):
    expect(pagina.locator("#acceso")).to_be_visible()
    expect(pagina.locator("#panel-chat")).to_be_hidden()
    assert pagina.locator("#clave").get_attribute("type") == "password"
    assert pagina.locator("#clave").get_attribute("autocomplete") == "off"
    capturar(pagina, "01-ingreso-local.png", "Pantalla real · acceso aún no verificado")
    solicitudes = []
    pagina.route("**/panel/consultar", lambda ruta: solicitudes.append(ruta))
    pagina.locator("#clave").fill("   ")
    pagina.locator("#clave").press("Enter")
    expect(pagina.locator("#error-acceso")).to_contain_text("Ingresa una clave")
    ingresar(pagina)
    expect(pagina.locator("#estado-global")).to_contain_text("acceso por verificar")
    assert not solicitudes, "Ingresar una clave no debe ejecutar consultas ni fingir validación."


def test_cabecera_contrato_memoria_y_recarga(pagina):
    clave = ingresar(pagina)
    solicitudes = []

    def responder(ruta):
        cabecera_correcta = secrets.compare_digest(ruta.request.headers.get("x-api-key", ""), clave)
        assert cabecera_correcta, "La cabecera debe corresponder a la clave ingresada."
        assert ruta.request.method == "POST"
        assert ruta.request.headers["content-type"] == "application/json"
        assert clave not in ruta.request.post_data
        assert clave not in ruta.request.url
        solicitudes.append(ruta.request.post_data_json)
        ruta.fulfill(content_type="application/json", body=json.dumps(datos_simulados()))

    pagina.route("**/panel/consultar", responder)
    enviar(pagina)
    expect(pagina.locator("#estado-consulta")).to_have_text("Respuesta recibida.")
    assert set(solicitudes[0]) == {"texto", "context_id"}
    assert solicitudes[0]["texto"] == PREGUNTA
    enviar(pagina, "Continúa con las mismas condiciones.")
    expect(pagina.locator(".mensaje.usuario")).to_have_count(2)
    expect(pagina.locator("#enviar")).to_be_enabled()
    assert solicitudes[1]["context_id"] == "contexto-simulado"
    assert pagina.evaluate("Object.keys(localStorage).length + Object.keys(sessionStorage).length") == 0
    assert not pagina.context.cookies()
    assert clave not in pagina.content()
    pagina.reload(wait_until="networkidle", timeout=15000)
    expect(pagina.locator("#acceso")).to_be_visible()
    expect(pagina.locator("#clave")).to_have_value("")
    expect(pagina.locator("#panel-chat")).to_be_hidden()
    clave = ingresar(pagina)
    enviar(pagina)
    expect(pagina.locator("#enviar")).to_be_enabled()
    assert solicitudes[2]["context_id"] != solicitudes[0]["context_id"]


@pytest.mark.parametrize("agente", ["Agente de Matias", "Agente de Alex", "Agente de Eduardo", "Agente de Sebastian", "ninguno"])
def test_muestra_agente_motivo_y_texto_literal_simulados(pagina, agente):
    ingresar(pagina)
    simular_json(pagina, datos_simulados(agente=agente))
    enviar(pagina)
    expect(pagina.locator(".mensaje.asistente .burbuja").last).to_have_text(RESPUESTA_SIMULADA)
    assert pagina.locator(".mensaje.asistente .burbuja").last.text_content() == RESPUESTA_SIMULADA
    expect(pagina.locator(".mensaje.asistente .hora").nth(1)).to_have_text(f"Agente: {agente}")
    expect(pagina.locator(".mensaje.asistente .hora").last).to_have_text("Motivo: La consulta solicita un presupuesto simulado.")
    if agente == "Agente de Eduardo":
        capturar(pagina, "02-respuesta-simulada-escritorio.png", "RESPUESTA SIMULADA · sin Gemini ni A2A")


def test_no_interpreta_html_ni_altera_espacios(pagina):
    ingresar(pagina)
    datos = datos_simulados()
    texto = '  **10 %**\n<img src="x" onerror="window.inyeccion=true">  CLP  '
    datos.update(respuesta=texto, agente="<b>Agente</b>", motivo="<script>malicioso</script>")
    simular_json(pagina, datos)
    enviar(pagina)
    expect(pagina.locator("#enviar")).to_be_enabled()
    burbuja = pagina.locator(".mensaje.asistente .burbuja").last
    assert burbuja.text_content() == '  10 %\n<img src="x" onerror="window.inyeccion=true">  CLP  '
    expect(burbuja.locator("strong")).to_have_text("10 %")
    assert pagina.locator("#conversacion img, #conversacion script, #conversacion b").count() == 0
    assert pagina.locator(".mensaje.asistente .hora").nth(1).text_content() == "Agente: <b>Agente</b>"
    assert pagina.locator(".mensaje.asistente .hora").last.text_content() == "Motivo: <script>malicioso</script>"
    assert pagina.evaluate("window.inyeccion === undefined")


@pytest.mark.parametrize("caso,markdown,visible", [
    ("eduardo", "# **Presupuesto simulado**\nTotal: **$2.173.600 CLP**.\n10 %; 240 minutos.",
     "Presupuesto simulado\nTotal: $2.173.600 CLP.\n10 %; 240 minutos."),
    ("matias", "## **Programa simulado**\n**16:00–18:00**; **60 minutos libres** informados.",
     "Programa simulado\n16:00–18:00; 60 minutos libres informados."),
    ("alex", "### **Recintos simulados**\n1. **A**: interior.\n2. **B**: accesible.\n3. **C**: cubierto.\nSin disponibilidad real.",
     "Recintos simulados\n1. A: interior.\n2. B: accesible.\n3. C: cubierto.\nSin disponibilidad real."),
    ("sebastian", "#### **Catering simulado**\nServicios **11:00** y **13:30**; dietas **65/10/5**; agua **88 L**.",
     "Catering simulado\nServicios 11:00 y 13:30; dietas 65/10/5; agua 88 L."),
], ids=["eduardo", "matias", "alex", "sebastian"])
def test_markdown_basico_seguro_sin_cambiar_datos(pagina, caso, markdown, visible):
    """Fixtures de regresión, NO transcripciones ni nuevas ejecuciones de agentes."""
    ingresar(pagina)
    datos = datos_simulados()
    datos["respuesta"] = markdown
    datos["agente"] = "Agente de " + {"eduardo": "Eduardo", "matias": "Matias", "alex": "Alex", "sebastian": "Sebastian"}[caso]
    datos["motivo"] = "Fixture de regresión Markdown; no ejecuta agentes."
    simular_json(pagina, datos)
    enviar(pagina, "**Pregunta literal de prueba**")
    expect(pagina.locator("#enviar")).to_be_enabled()
    burbuja = pagina.locator(".mensaje.asistente .burbuja").last
    assert burbuja.text_content() == visible
    assert burbuja.locator("h3, h4, h5, h6").count() == 1
    assert burbuja.locator("strong").count() >= 2
    assert "**" not in burbuja.text_content()
    assert pagina.locator(".mensaje.usuario .burbuja").last.text_content() == "**Pregunta literal de prueba**"
    assert pagina.locator(".mensaje.usuario strong").count() == 0
    if caso == "matias":
        capturar(pagina, "07-markdown-simulado-escritorio.png", "MARKDOWN SIMULADO · sin Gemini ni A2A")
    pagina.locator("#nueva-conversacion").click()
    expect(pagina.locator(".mensaje.asistente")).to_have_count(1)
    expect(pagina.locator(".mensaje.usuario")).to_have_count(0)
    expect(pagina.locator("#conversacion strong, #conversacion h3, #conversacion h4, #conversacion h5, #conversacion h6")).to_have_count(0)
    expect(pagina.locator("#pregunta")).to_be_focused()


def test_codigo_y_sintaxis_no_admitida_quedan_inertes(pagina):
    ingresar(pagina)
    datos = datos_simulados()
    datos["respuesta"] = (
        '`**16:00** <b>CLP</b>` y __88 L__\r\n'
        '[enlace](javascript:window.inyeccion=true) ![imagen](https://example.invalid/x)\n'
        '***literal***; **sin cierre; 2 * 3; 65/10/5; $2.173.600 CLP\n'
        '```texto\n# **Literal dentro de un bloque**\n```\n'
        '~~~\n__También literal__\n~~~'
    )
    simular_json(pagina, datos)
    enviar(pagina)
    expect(pagina.locator("#enviar")).to_be_enabled()
    burbuja = pagina.locator(".mensaje.asistente .burbuja").last
    assert burbuja.text_content() == (
        '**16:00** <b>CLP</b> y 88 L\r\n'
        '[enlace](javascript:window.inyeccion=true) ![imagen](https://example.invalid/x)\n'
        '***literal***; **sin cierre; 2 * 3; 65/10/5; $2.173.600 CLP\n'
        '```texto\n# **Literal dentro de un bloque**\n```\n'
        '~~~\n__También literal__\n~~~'
    )
    expect(burbuja.locator("code")).to_have_text("**16:00** <b>CLP</b>")
    expect(burbuja.locator("strong")).to_have_text("88 L")
    assert burbuja.locator("h3, h4, h5, h6").count() == 0
    assert burbuja.locator("a, img, b, script").count() == 0
    assert pagina.evaluate("window.inyeccion === undefined")


@pytest.mark.parametrize("estado,tipo", [(401, "application/json"), (401, "text/html"), (403, "text/html")])
def test_rechazo_de_acceso_simulado(pagina, estado, tipo):
    ingresar(pagina)
    pagina.route("**/panel/consultar", lambda ruta: ruta.fulfill(
        status=estado, content_type=tipo, body="DETALLE_INTERNO_NO_MOSTRAR"
    ))
    enviar(pagina)
    expect(pagina.locator("#error-acceso")).to_contain_text(f"Acceso rechazado ({estado})")
    expect(pagina.locator("#clave")).to_be_focused()
    expect(pagina.locator("#clave")).to_have_value("")
    expect(pagina.locator("#pregunta")).to_have_value(PREGUNTA)
    assert "DETALLE_INTERNO_NO_MOSTRAR" not in pagina.content()
    if estado == 401 and tipo == "application/json":
        capturar(pagina, "04-acceso-rechazado-simulado.png", "401 SIMULADO · no demuestra protección real")


@pytest.mark.parametrize("estado,esperado", [
    (400, "Entrada inválida"), (422, "Entrada inválida"), (413, "demasiado larga"),
    (429, "límite de consultas"), (502, "proveedor o al agente"), (503, "proveedor o al agente"),
    (500, "servidor no pudo"), (408, "tiempo de espera del servidor"),
    (504, "tiempo de espera del servidor"), (404, "HTTP 404"),
])
def test_errores_http_simulados_sin_detalles_crudos(pagina, estado, esperado):
    ingresar(pagina)
    pagina.route("**/panel/consultar", lambda ruta: ruta.fulfill(
        status=estado, content_type="text/html", body="DETALLE_INTERNO_NO_MOSTRAR\nTRAZA"
    ))
    enviar(pagina)
    aviso = pagina.locator(".mensaje.asistente .burbuja").last
    expect(aviso).to_contain_text(esperado)
    assert "\n" not in aviso.text_content()
    assert "DETALLE_INTERNO_NO_MOSTRAR" not in pagina.content()
    expect(pagina.locator("#pregunta")).to_have_value(PREGUNTA)
    expect(pagina.locator("#enviar")).to_be_enabled()
    if estado == 502:
        capturar(pagina, "05-proveedor-fallido-simulado.png", "502 SIMULADO · sin fallo real del proveedor")


@pytest.mark.parametrize("tipo,cuerpo,esperado", [
    ("text/html", "<h1>Proxy</h1>", "no es JSON"),
    ("application/json", "{", "JSON inválido"),
    ("application/json", "null", "formato inesperado"),
    ("application/json", '{"respuesta": "incompleta"}', "formato inesperado"),
])
def test_respuesta_no_json_o_incompleta_simulada(pagina, tipo, cuerpo, esperado):
    ingresar(pagina)
    pagina.route("**/panel/consultar", lambda ruta: ruta.fulfill(content_type=tipo, body=cuerpo))
    enviar(pagina)
    expect(pagina.locator(".mensaje.asistente .burbuja").last).to_contain_text(esperado)
    expect(pagina.locator("#enviar")).to_be_enabled()


def test_desconexion_simulada(pagina):
    ingresar(pagina)
    pagina.route("**/panel/consultar", lambda ruta: ruta.abort("internetdisconnected"))
    enviar(pagina)
    expect(pagina.locator(".mensaje.asistente .burbuja").last).to_contain_text("Revisa tu conexión")
    expect(pagina.locator("#enviar")).to_be_enabled()


def test_timeout_simulado_con_reloj_virtual(pagina):
    ingresar(pagina)
    pagina.clock.install()
    pagina.clock.pause_at(pagina.evaluate("Date.now() + 100"))
    pendientes = []
    pagina.route("**/panel/consultar", lambda ruta: pendientes.append(ruta))
    enviar(pagina)
    expect(pagina.locator(".indicador")).to_be_visible()
    pagina.clock.fast_forward(65001)
    expect(pagina.locator(".mensaje.asistente .burbuja").last).to_contain_text("65 segundos de espera")
    expect(pagina.locator("#enviar")).to_be_enabled()
    expect(pagina.locator("#pregunta")).to_have_value(PREGUNTA)


def test_espera_y_prevencion_de_duplicados(pagina):
    ingresar(pagina)
    pendientes = []
    pagina.route("**/panel/consultar", lambda ruta: pendientes.append(ruta))
    enviar(pagina)
    expect(pagina.locator("#enviar")).to_be_disabled()
    expect(pagina.locator(".sugerencia:disabled")).to_have_count(4)
    expect(pagina.locator("#conversacion")).to_have_attribute("aria-busy", "true")
    expect(pagina.locator(".indicador")).to_be_visible()
    capturar(pagina, "06-espera-simulada.png", "ESPERA SIMULADA · petición retenida por la prueba")
    pagina.locator("#pregunta").fill("Otro borrador")
    pagina.locator("#pregunta").press("Enter")
    pagina.evaluate("document.getElementById('formulario').requestSubmit()")
    expect(pagina.locator(".mensaje.usuario")).to_have_count(1)
    assert len(pendientes) == 1
    pendientes[0].fulfill(content_type="application/json", body=json.dumps(datos_simulados()))
    expect(pagina.locator("#enviar")).to_be_enabled()
    expect(pagina.locator("#pregunta")).to_have_value("Otro borrador")


@pytest.mark.parametrize("etapa", ["red", "json"])
def test_nueva_conversacion_descarta_respuesta_tardia_aun_sin_abort(pagina, etapa):
    ingresar(pagina)
    # Doble deliberadamente adverso: ignora AbortSignal para probar también la
    # carrera entre fetch resuelto y lectura JSON, no solo el aborto de la red.
    pagina.evaluate("""(etapa) => {
      window.pendientesPrueba = [];
      window.fetch = (url, opciones) => {
        const cuerpo = JSON.parse(opciones.body);
        if (etapa === 'red') return new Promise(resolver => pendientesPrueba.push({cuerpo, resolver}));
        return Promise.resolve({status: 200, ok: true, headers: new Headers({'Content-Type':'application/json'}),
          json: () => new Promise(resolver => pendientesPrueba.push({cuerpo, resolver}))});
      };
      window.resolverPrueba = (indice, datos) => pendientesPrueba[indice].resolver(
        etapa === 'red' ? new Response(JSON.stringify(datos), {headers:{'Content-Type':'application/json'}}) : datos
      );
    }""", etapa)
    enviar(pagina, "Pregunta anterior")
    pagina.wait_for_function("pendientesPrueba.length === 1", timeout=7000)
    anterior = pagina.evaluate("pendientesPrueba[0].cuerpo.context_id")
    pagina.locator("#nueva-conversacion").click()
    expect(pagina.locator("#pregunta")).to_be_focused()
    enviar(pagina, "Pregunta nueva")
    pagina.wait_for_function("pendientesPrueba.length === 2", timeout=7000)
    nuevo = pagina.evaluate("pendientesPrueba[1].cuerpo.context_id")
    assert anterior != nuevo
    viejo = datos_simulados("contexto-anterior")
    viejo["respuesta"] = "RESPUESTA ANTERIOR QUE NO DEBE APARECER"
    pagina.evaluate("datos => resolverPrueba(0, datos)", viejo)
    expect(pagina.locator("#enviar")).to_be_disabled()
    expect(pagina.locator(".indicador")).to_have_count(1)
    assert "RESPUESTA ANTERIOR" not in pagina.locator("#conversacion").inner_text()
    pagina.evaluate("datos => resolverPrueba(1, datos)", datos_simulados(nuevo))
    expect(pagina.locator("#enviar")).to_be_enabled()
    expect(pagina.locator("#conversacion")).to_contain_text(RESPUESTA_SIMULADA)
    enviar(pagina, "Continuación nueva")
    pagina.wait_for_function("pendientesPrueba.length === 3", timeout=7000)
    assert pagina.evaluate("pendientesPrueba[2].cuerpo.context_id") == nuevo


def test_cambiar_clave_cancela_pendiente_y_limpia_historial(pagina):
    ingresar(pagina)
    pagina.route("**/panel/consultar", lambda ruta: None)
    enviar(pagina)
    expect(pagina.locator("#enviar")).to_be_disabled()
    pagina.locator("#cambiar-clave").click()
    expect(pagina.locator("#acceso")).to_be_visible()
    expect(pagina.locator("#clave")).to_be_focused()
    expect(pagina.locator(".mensaje.usuario")).to_have_count(0)
    expect(pagina.locator(".indicador")).to_have_count(0)
    expect(pagina.locator("#pregunta")).to_have_value("")


def test_teclado_validacion_local_y_sugerencias(pagina):
    ingresar(pagina)
    simular_json(pagina, datos_simulados())
    enviar(pagina, "   ")
    expect(pagina.locator("#aviso-entrada")).to_contain_text("solo espacios")
    expect(pagina.locator(".mensaje.usuario")).to_have_count(0)
    pagina.locator("#pregunta").fill("Primera línea")
    pagina.locator("#pregunta").press("Shift+Enter")
    expect(pagina.locator("#pregunta")).to_have_value("Primera línea\n")
    pagina.locator("#pregunta").press("Enter")
    expect(pagina.locator("#enviar")).to_be_enabled()
    pagina.locator(".sugerencia").first.focus()
    pagina.locator(".sugerencia").first.press("Enter")
    expect(pagina.locator(".mensaje.usuario")).to_have_count(2)
    expect(pagina.locator("#enviar")).to_be_enabled()


@pytest.mark.parametrize("ancho", [320, 390])
def test_movil_sin_desborde_y_controles_tactiles(pagina, ancho):
    pagina.set_viewport_size({"width": ancho, "height": 844})
    assert pagina.evaluate("document.documentElement.scrollWidth <= innerWidth")
    ingresar(pagina)
    datos = datos_simulados()
    datos["respuesta"] = RESPUESTA_MARKDOWN_SIMULADA
    datos["agente"] = "ninguno"
    datos["motivo"] = "Fixture mixto de regresión Markdown; no ejecuta agentes."
    simular_json(pagina, datos)
    enviar(pagina)
    expect(pagina.locator("#enviar")).to_be_enabled()
    burbuja = pagina.locator(".mensaje.asistente .burbuja").last
    assert burbuja.text_content() == TEXTO_MARKDOWN_SIMULADO
    assert burbuja.locator("strong").count() == 7
    assert burbuja.evaluate("elemento => elemento.scrollWidth <= elemento.clientWidth")
    assert pagina.evaluate("document.documentElement.scrollWidth <= innerWidth")
    assert pagina.locator(".chat").bounding_box()["y"] < pagina.locator(".columna").bounding_box()["y"]
    for selector in ("#enviar", "#nueva-conversacion", "#cambiar-clave", ".sugerencia"):
        for boton in pagina.locator(selector).all():
            assert boton.bounding_box()["height"] >= 44
    assert pagina.locator("#pregunta").evaluate("e => getComputedStyle(e).fontSize") == "16px"
    if ancho == 390:
        capturar(pagina, "08-markdown-simulado-movil.png", "390 px · MARKDOWN SIMULADO · no teléfono físico")
