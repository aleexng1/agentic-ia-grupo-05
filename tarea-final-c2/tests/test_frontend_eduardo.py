"""Pruebas locales de Rendiciones IA: Chromium real y API simulada, sin red externa."""

import base64
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import tempfile
import time
from pathlib import Path

import pytest

WEB = Path(__file__).resolve().parents[1] / "web" / "index.html"
CLAVE = "clave-ficticia-solo-tests"
ID = "e9137f48-8911-42c4-9020-e6e48e4aec0d"

MOCK = r"""
const $ = id => document.getElementById(id);
const m = window.mock = { cola: [], llamadas: [], plazos: [], revocadas: [] };
const esperaOriginal = window.setTimeout.bind(window);
window.setTimeout = (fn, ms, ...args) => {
  if (ms === 65000 || ms === 15000) m.plazos.push({fn, ms});
  return esperaOriginal(fn, ms, ...args);
};
const revocar = URL.revokeObjectURL.bind(URL);
URL.revokeObjectURL = url => { m.revocadas.push(url); revocar(url); };
window.fetch = async (url, opciones) => {
  const cuerpo = opciones.body ? JSON.parse(opciones.body) : null;
  const llamada = { url, cuerpo, opciones, resolver: null };
  m.llamadas.push(llamada);
  const plan = m.cola.shift() || {};
  if (plan.red) throw new TypeError("fallo de red simulado");
  const base = {id_ejecucion: "e9137f48-8911-42c4-9020-e6e48e4aec0d",
    thread_id: cuerpo?.thread_id, ruta: "consulta_politica", respuesta: "Respuesta simulada",
    estado_final: "ok"};
  const construir = () => new Response(plan.raw ?? JSON.stringify({...base, ...plan.datos}), {
    status: plan.status ?? 200,
    headers: {"Content-Type": plan.mime ?? "application/json"}});
  if (plan.tardia) return new Promise(resolve => { llamada.resolver = () => resolve(construir()); });
  return construir();
};
const guardar = (clave = "clave-ficticia-solo-tests") => {
  $("clave").value = clave; $("formulario-acceso").requestSubmit();
};
const escribir = texto => {
  $("pregunta").value = texto; $("pregunta").dispatchEvent(new Event("input"));
};
const enviar = texto => {
  if (texto !== undefined) escribir(texto);
  $("formulario").requestSubmit();
};
const adjuntar = archivo => {
  const datos = new DataTransfer();
  datos.items.add(archivo);
  $("archivo").files = datos.files;
  $("archivo").dispatchEvent(new Event("change"));
};
async function imagen(tipo) {
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = 2;
  const contexto = canvas.getContext("2d");
  contexto.fillStyle = "#126660";
  contexto.fillRect(0, 0, 2, 2);
  const blob = await new Promise(resolve => canvas.toBlob(resolve, tipo));
  const ext = tipo.split("/")[1];
  const base64 = canvas.toDataURL(tipo).split(",")[1];
  adjuntar(new File([blob], `boleta.${ext}`, {type: tipo}));
  return base64;
}
"""


class Chrome:
    def __init__(self, socket):
        self.socket = socket
        self.contador = 0
        self.sesion = None
        pestaña = self.cdp("Target.createTarget", url="about:blank")["targetId"]
        self.sesion = self.cdp("Target.attachToTarget", targetId=pestaña, flatten=True)["sessionId"]
        self.cdp("Page.enable")
        self.cdp("Network.enable")
        self.cdp("Network.setBlockedURLs", urls=["http://*", "https://*"])
        self.cdp("Page.addScriptToEvaluateOnNewDocument", source=MOCK)

    def cdp(self, metodo, **parametros):
        self.contador += 1
        mensaje = {"id": self.contador, "method": metodo, "params": parametros}
        if self.sesion and not metodo.startswith(("Target.", "Browser.")):
            mensaje["sessionId"] = self.sesion
        self.socket.send(json.dumps(mensaje))
        while True:
            resultado = json.loads(self.socket.recv(timeout=12))
            if resultado.get("id") == self.contador:
                assert "error" not in resultado, resultado
                return resultado.get("result", {})

    def js(self, expresion):
        datos = self.cdp("Runtime.evaluate", expression=expresion, returnByValue=True, awaitPromise=True)
        assert "exceptionDetails" not in datos, datos.get("exceptionDetails")
        return datos["result"].get("value")

    def espera(self, expresion):
        limite = time.monotonic() + 5
        while time.monotonic() < limite:
            if valor := self.js(expresion):
                return valor
            time.sleep(.025)
        pytest.fail(f"El navegador no alcanzó este estado: {expresion}")

    def abrir(self, ancho=1366, alto=768):
        self.cdp("Emulation.setDeviceMetricsOverride", width=ancho, height=alto,
                 deviceScaleFactor=1, mobile=ancho <= 800)
        self.cdp("Page.navigate", url=WEB.as_uri())
        self.espera("Boolean(window.mock && document.readyState === 'complete' && document.getElementById('clave'))")


def _ruta_chromium():
    raiz86 = os.environ.get("ProgramFiles(x86)", "")
    raiz64 = os.environ.get("ProgramFiles", "")
    rutas = [
        shutil.which("chromium"), shutil.which("google-chrome"), shutil.which("chrome"),
        str(Path(raiz64) / "Google/Chrome/Application/chrome.exe"),
        str(Path(raiz86) / "Microsoft/Edge/Application/msedge.exe"),
    ]
    return next((r for r in rutas if r and Path(r).is_file()), None)


@pytest.fixture(scope="module")
def chrome():
    ruta = _ruta_chromium()
    if not ruta:
        pytest.skip("No hay Chromium/Chrome/Edge local; no se instala nada.")
    socket_web = pytest.importorskip("websockets.sync.client")
    with tempfile.TemporaryDirectory(prefix=".frontend-chromium-", dir=WEB.parent, ignore_cleanup_errors=False) as perfil:
        proceso = subprocess.Popen([
            ruta, "--headless", "--no-first-run", "--no-default-browser-check",
            "--disable-background-networking", "--disable-component-update", "--disable-sync",
            "--disable-extensions", "--disable-crash-reporter", "--no-proxy-server",
            "--host-resolver-rules=MAP * ~NOTFOUND", f"--user-data-dir={perfil}",
            "--remote-debugging-address=127.0.0.1", "--remote-debugging-port=0", "about:blank",
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            env={**os.environ, "TEMP": perfil, "TMP": perfil})
        try:
            puerto = Path(perfil) / "DevToolsActivePort"
            limite = time.monotonic() + 15
            while not puerto.exists() and proceso.poll() is None and time.monotonic() < limite:
                time.sleep(.05)
            assert puerto.exists(), "Chromium no abrió la sesión de pruebas local."
            numero, ruta_ws = puerto.read_text(encoding="utf-8").splitlines()
            with socket_web.connect(f"ws://127.0.0.1:{numero}{ruta_ws}", proxy=None) as socket:
                navegador = Chrome(socket)
                try:
                    yield navegador
                finally:
                    navegador.cdp("Browser.close")
        finally:
            try:
                proceso.wait(timeout=8)
            except subprocess.TimeoutExpired:
                proceso.terminate()
                proceso.wait(timeout=8)


@pytest.fixture
def pagina(chrome):
    chrome.abrir()
    return chrome


def test_pagina_autocontenida_sin_componentes_antiguos_o_persistencia():
    html = WEB.read_text(encoding="utf-8")
    minusculas = html.lower()
    assert all(x not in minusculas for x in ("/panel/consultar", "context_id", "feria", "catering", "google_api_key"))
    assert all(x not in html for x in ("localStorage", "sessionStorage", "document.cookie", ".innerHTML", "eval(", "console."))
    assert not re.search(r'<(?:script|link|img)[^>]+\b(?:src|href)=["\']https?://', html)
    for etiqueta in ("script", "style"):
        texto, = re.findall(fr"<{etiqueta}>(.*?)</{etiqueta}>", html, re.S)
        csp = base64.b64encode(hashlib.sha256(texto.encode()).digest()).decode()
        assert f"{etiqueta}-src 'sha256-{csp}'" in html


def test_fastapi_sirve_la_pagina_publica_y_protege_chat(monkeypatch):
    from fastapi.testclient import TestClient

    from api.app import app

    monkeypatch.setenv("API_KEY_SERVICIO", CLAVE)
    cliente = TestClient(app)
    portada = cliente.get("/")
    assert portada.status_code == 200 and portada.content == WEB.read_bytes()
    assert portada.headers["cache-control"] == "no-store"
    assert cliente.post("/chat", json={"thread_id": "conv-prueba", "texto": "Consulta de prueba"}).status_code == 401


def test_clave_solo_header_y_acceso_verificado_por_respuesta_valida(pagina):
    assert pagina.js("$('acceso-chip').dataset.acceso") in (None, "sin-clave")
    pagina.js("guardar()")
    assert pagina.js("$('acceso-chip').dataset.acceso") == "cargada"
    assert pagina.js("mock.llamadas.length === 0 && $('clave').value === ''")
    pagina.js("enviar('  ¿Hasta cuándo?  ')")
    pagina.espera("$('acceso-chip').dataset.acceso === 'verificado'")
    llamada = pagina.js("mock.llamadas[0]")
    assert llamada["url"] == "/chat" and llamada["opciones"]["method"] == "POST"
    assert set(llamada["cuerpo"]) == {"thread_id", "texto"} and llamada["cuerpo"]["texto"] == "¿Hasta cuándo?"
    assert CLAVE not in llamada["opciones"]["body"]
    assert llamada["opciones"]["headers"] == {
        "Accept": "application/json", "Content-Type": "application/json", "X-API-Key": CLAVE,
    }
    assert llamada["opciones"]["credentials"] == "omit" and llamada["opciones"]["redirect"] == "error"
    assert pagina.js("localStorage.length === 0 && sessionStorage.length === 0 && document.cookie === ''")
    pagina.js("$('cambiar-clave').click()")
    pagina.espera("!$('acceso').hidden && $('acceso-chip').dataset.acceso === 'sin-clave'")
    pagina.js("guardar('otra-ficticia'); enviar('Siguiente')")
    pagina.espera("mock.llamadas.length === 2")
    assert pagina.js("mock.llamadas[1].opciones.headers['X-API-Key']") == "otra-ficticia"
    pagina.abrir()
    assert pagina.js("!$('acceso').hidden && $('clave').value === '' && mock.llamadas.length === 0")


def test_sugerencias_y_thread_id_continuo_hasta_nueva_conversacion(pagina):
    pagina.js("guardar(); document.querySelector('.atajos').open = true; document.querySelector('.sugerencia').click()")
    assert pagina.js("$('pregunta').value") == "¿Hasta cuándo puedo rendir un gasto?"
    assert pagina.js("mock.llamadas.length") == 0
    pagina.js("enviar()")
    pagina.espera("!$('pregunta').readOnly")
    pagina.js("enviar('Otra consulta')")
    pagina.espera("!$('pregunta').readOnly")
    pagina.js("$('nueva-conversacion').click(); enviar('Hilo nuevo')")
    pagina.espera("!$('pregunta').readOnly")
    ids = pagina.js("mock.llamadas.map(l => l.cuerpo.thread_id)")
    assert ids[0] == ids[1] != ids[2]
    assert all(re.fullmatch(r"conv-[a-f0-9-]{32,36}", id_) and len(id_) <= 100 for id_ in ids)
    assert pagina.js("document.querySelectorAll('.mensaje.usuario').length") == 1


@pytest.mark.parametrize("mime", ["image/jpeg", "image/png", "image/webp"])
def test_imagen_base64_sin_prefijo_y_revocacion(pagina, mime):
    pagina.js("guardar()")
    esperado = pagina.js(f"imagen({json.dumps(mime)})")
    pagina.espera("!$('adjunto').hidden && $('vista-adjunto').naturalWidth === 2")
    assert pagina.js("$('nombre-adjunto').textContent").startswith("boleta.")
    assert pagina.js("Boolean($('tamano-adjunto').textContent)")
    pagina.js("enviar('Revisar boleta')")
    pagina.espera("mock.llamadas.length === 1 && !$('pregunta').readOnly")
    assert pagina.js("mock.llamadas[0].cuerpo.imagen") == {"mime_type": mime, "datos_base64": esperado}
    assert pagina.js("$('adjunto').hidden && !$('vista-adjunto').hasAttribute('src') && mock.revocadas.length === 1")


def test_quitar_imagen_la_omite_de_la_solicitud(pagina):
    pagina.js("guardar(); imagen('image/png')")
    pagina.espera("!$('adjunto').hidden")
    pagina.js("$('quitar-adjunto').click(); enviar('Texto solo')")
    assert not pagina.js("Object.hasOwn(mock.llamadas[0].cuerpo, 'imagen')")
    assert pagina.js("mock.revocadas.length === 1")


@pytest.mark.parametrize("archivo,mensaje", [
    ("new File(['<svg/>'], 'prueba.svg', {type: 'image/svg+xml'})", "debe ser JPEG"),
    ("new File(['no es binario PNG'], 'prueba.png', {type: 'image/png'})", "formato real"),
    ("new File([new Uint8Array(5*1024*1024+1)], 'grande.jpg', {type: 'image/jpeg'})", "5 MiB"),
])
def test_rechaza_mime_falso_y_archivos_grandes(pagina, archivo, mensaje):
    pagina.js(f"guardar(); adjuntar({archivo})")
    pagina.espera("!$('aviso-entrada').hidden")
    assert mensaje in pagina.js("$('aviso-entrada').textContent")
    assert pagina.js("$('adjunto').hidden && mock.llamadas.length === 0")


def test_limite_de_texto_en_puntos_de_codigo_como_la_api(pagina):
    pagina.js("guardar(); enviar(' ');")
    assert pagina.js("mock.llamadas.length === 0 && $('pregunta').getAttribute('aria-invalid') === 'true'")
    pagina.js("enviar('a'.repeat(4001))")
    assert pagina.js("mock.llamadas.length === 0 && $('contador').textContent === '4001 / 4000'")
    pagina.js("enviar('😀'.repeat(4000))")
    pagina.espera("!$('pregunta').readOnly")
    assert pagina.js("[...mock.llamadas[0].cuerpo.texto].length") == 4000


@pytest.mark.parametrize("ruta,estado,decision", [
    ("consulta_politica", "ok", None), ("fuera_de_alcance", "bloqueado", None),
    ("revisar_gasto", "fallback", "observar"), ("revisar_gasto", "error", None),
    ("revisar_gasto", "ok", "aprobar"), ("revisar_gasto", "ok", "rechazar"),
])
def test_rutas_estados_y_veredictos_del_servidor(pagina, ruta, estado, decision):
    datos = {"ruta": ruta, "estado_final": estado,
             "respuesta": "Texto simulado: [Fuente: datos/politica_ficticia.md#P02]"}
    if decision:
        datos["veredicto"] = {"decision": decision, "motivo": "Motivo simulado", "politica_sugerida": "P02",
                              "categoria_sugerida": "Hotel", "cuenta_sugerida": "Cuenta de prueba"}
    pagina.js(f"guardar(); mock.cola.push({{datos: {json.dumps(datos)}}}); enviar('Consulta')")
    pagina.espera(f"Boolean(document.querySelector('.etiqueta.{estado}'))")
    assert estado in pagina.js("$('estado-consulta').textContent")
    assert ruta in pagina.js("document.querySelector('.detalles').textContent")
    assert len(pagina.js("Array.from(document.querySelectorAll('.veredicto'), n => n.textContent)")) == int(bool(decision))
    assert "[Fuente: datos/politica_ficticia.md#P02]" in pagina.js("$('conversacion').textContent")
    if decision:
        tarjeta = pagina.js("document.querySelector('.veredicto').textContent")
        assert all(x in tarjeta for x in (decision.capitalize(), "Motivo simulado", "P02", "Hotel", "Cuenta de prueba"))


def test_registro_solo_bajo_demanda_y_valores_reales_del_mock(pagina):
    fila = {
        "id_ejecucion": ID, "fecha": "2026-11-24T10:15:00-03:00", "ruta": "consulta_politica",
        "estado_final": "ok", "pasos": 0, "herramientas_usadas": ["buscar_politica"],
        "hubo_a2a": False, "duracion_ms": 5320,
    }
    pagina.js("guardar(); enviar('Consulta')")
    pagina.espera("Boolean(document.querySelector('.detalles'))")
    assert pagina.js("mock.llamadas.length") == 1
    pagina.js(f"mock.cola.push({{datos: {json.dumps(fila)}}}); document.querySelector('.detalles summary').click(); "
              "document.querySelector('.detalles button').click()")
    pagina.espera("document.querySelector('.detalles [role=status]').textContent === 'Registro recibido.'")
    assert pagina.js("mock.llamadas[1].url") == f"/registro/{ID}"
    assert pagina.js("mock.llamadas[1].opciones.method") == "GET"
    assert pagina.js("mock.llamadas[1].opciones.headers['X-API-Key']") == CLAVE
    detalles = pagina.js("document.querySelector('.detalles').textContent")
    assert all(x in detalles for x in ("2026-11-24", "buscar_politica", "No", "5320 ms", "Pasos"))


@pytest.mark.parametrize("estado", [404, 501])
def test_registro_inexistente_o_sin_integrar(pagina, estado):
    pagina.js("guardar(); enviar('Consulta')")
    pagina.espera("Boolean(document.querySelector('.detalles'))")
    pagina.js(f"mock.cola.push({{status:{estado}}}); document.querySelector('.detalles button').click()")
    assert pagina.espera(f"document.querySelector('.detalles [role=status]').textContent.includes('{estado}')")
    assert "Duración" not in pagina.js("document.querySelector('.detalles').textContent")


@pytest.mark.parametrize("estado", [422, 501, 502, 503])
def test_error_http_preserva_borrador_sin_verificar_acceso(pagina, estado):
    pagina.js(f"guardar(); mock.cola.push({{status:{estado}, raw:'detalle interno simulado', mime:'text/html'}}); "
              "enviar('Borrador para corregir')")
    pagina.espera("!$('aviso-entrada').hidden")
    aviso = pagina.js("$('aviso-entrada').textContent")
    assert f"HTTP {estado}" in aviso and "detalle interno" not in aviso
    if estado == 501:
        assert "aún no está integrado" in aviso
    assert pagina.js("$('pregunta').value") == "Borrador para corregir"
    assert pagina.js("$('acceso-chip').dataset.acceso") == "cargada"
    assert pagina.js("mock.llamadas.length === 1")


def test_401_conserva_texto_e_imagen_y_obliga_a_recargar_clave(pagina):
    pagina.js("guardar(); imagen('image/png')")
    pagina.espera("!$('adjunto').hidden")
    pagina.js("mock.cola.push({status:401}); enviar('Borrador para reintentar')")
    pagina.espera("!$('acceso').hidden && $('error-acceso').textContent.includes('401')")
    assert pagina.js("$('acceso-chip').dataset.acceso === 'sin-clave' && $('clave').value === ''")
    pagina.js("guardar('clave-nueva-ficticia'); enviar()")
    pagina.espera("mock.llamadas.length === 2")
    assert pagina.js("mock.llamadas[1].opciones.headers['X-API-Key']") == "clave-nueva-ficticia"
    assert pagina.js("mock.llamadas[1].cuerpo.texto") == "Borrador para reintentar"
    assert pagina.js("mock.llamadas[1].cuerpo.imagen.mime_type") == "image/png"


@pytest.mark.parametrize("plan,mensaje", [
    ({"mime": "text/html", "raw": "<h1>texto</h1>"}, "no devolvió JSON"),
    ({"raw": "{"}, "no se pudo leer"),
    ({"datos": {"id_ejecucion": "../registro?ajeno"}}, "no coinciden con el contrato"),
    ({"datos": {"thread_id": "otro"}}, "no coinciden con el contrato"),
    ({"datos": {"ruta": ["consulta_politica"]}}, "no coinciden con el contrato"),
    ({"datos": {"ruta": "revisar_gasto", "veredicto": {"decision": "inventado"}}}, "no coinciden con el contrato"),
    ({"red": True}, "No se pudo conectar"),
])
def test_respuestas_invalidas_y_red_no_se_muestran_ni_verifican_clave(pagina, plan, mensaje):
    pagina.js(f"guardar(); mock.cola.push({json.dumps(plan)}); enviar('Borrador')")
    pagina.espera("!$('aviso-entrada').hidden")
    assert mensaje in pagina.js("$('aviso-entrada').textContent")
    assert pagina.js("$('pregunta').value === 'Borrador' && $('acceso-chip').dataset.acceso === 'cargada'")
    assert pagina.js("!document.querySelector('.detalles') && mock.llamadas.length === 1")


@pytest.mark.parametrize("accion,aviso", [
    ("$('cancelar').click()", "Cancelaste la espera"),
    ("mock.plazos.find(p => p.ms === 65000).fn()", "65 segundos"),
    ("$('nueva-conversacion').click()", ""),
])
def test_cancelacion_timeout_doble_envio_y_respuesta_tardia(pagina, accion, aviso):
    pagina.js("guardar(); mock.cola.push({tardia:true, datos:{respuesta:'Respuesta anterior'}}); "
              "enviar('Primer borrador'); enviar()")
    assert pagina.js("mock.llamadas.length") == 1
    pagina.js(accion)
    assert pagina.js("mock.llamadas[0].opciones.signal.aborted")
    if aviso:
        assert aviso in pagina.js("$('aviso-entrada').textContent")
        assert pagina.js("$('pregunta').value") == "Primer borrador"
    else:
        assert pagina.js("$('pregunta').value") == ""
    pagina.js("enviar('Turno siguiente'); mock.llamadas[0].resolver()")
    pagina.espera("Boolean(document.querySelector('.detalles'))")
    assert not pagina.js("$('conversacion').textContent.includes('Respuesta anterior')")
    assert pagina.js("mock.llamadas.length === 2 && document.querySelectorAll('.detalles').length === 1")


def test_un_temporizador_viejo_no_interrumpe_un_turno_nuevo(pagina):
    pagina.js("guardar(); mock.cola.push({tardia:true}, {tardia:true}); enviar('Primero'); "
              "$('nueva-conversacion').click(); enviar('Segundo'); mock.plazos[0].fn()")
    assert pagina.js("mock.llamadas.length === 2 && !mock.llamadas[1].opciones.signal.aborted && $('pregunta').readOnly")
    pagina.js("mock.llamadas[1].resolver(); mock.llamadas[0].resolver()")
    pagina.espera("Boolean(document.querySelector('.detalles'))")
    assert pagina.js("document.querySelector('.mensaje.usuario .burbuja').textContent") == "Segundo"


def test_teclado_foco_y_movimiento_reducido_en_chromium(pagina):
    pagina.cdp("Emulation.setEmulatedMedia", features=[{"name": "prefers-reduced-motion", "value": "reduce"}])
    try:
        pagina.js("guardar(); escribir('Consulta por teclado')")
        assert pagina.js("document.activeElement === $('pregunta')")
        assert pagina.js("getComputedStyle($('pregunta')).outlineStyle") == "solid"
        pagina.cdp("Input.dispatchKeyEvent", type="keyDown", key="Enter", code="Enter",
                   windowsVirtualKeyCode=13, modifiers=8)
        pagina.cdp("Input.dispatchKeyEvent", type="keyUp", key="Enter", code="Enter",
                   windowsVirtualKeyCode=13, modifiers=8)
        assert pagina.js("mock.llamadas.length === 0")
        pagina.cdp("Input.dispatchKeyEvent", type="keyDown", key="Enter", code="Enter", windowsVirtualKeyCode=13)
        pagina.cdp("Input.dispatchKeyEvent", type="keyUp", key="Enter", code="Enter", windowsVirtualKeyCode=13)
        pagina.espera("Boolean(document.querySelector('.mensaje.usuario'))")
        assert pagina.js("mock.llamadas.length === 1")
        assert pagina.js("getComputedStyle(document.querySelector('.mensaje.usuario')).animationName") == "none"
    finally:
        pagina.cdp("Emulation.setEmulatedMedia", features=[])


def test_respuesta_con_html_se_muestra_como_texto_y_conserva_markdown_seguro(pagina):
    literal = '<img src="https://prueba.invalid/x" alt="marca"><a href="https://prueba.invalid">ejemplo</a>'
    datos = {"respuesta": "## Título seguro\n**Negrita** y `código`.\n" + literal}
    pagina.js(f"guardar(); mock.cola.push({{datos: {json.dumps(datos)}}}); enviar('Consulta')")
    pagina.espera("Boolean(document.querySelector('.mensaje.asistente .burbuja strong'))")
    assert literal in pagina.js("$('conversacion').textContent")
    assert pagina.js("!$('conversacion').querySelector('img,a,script') && Boolean($('conversacion').querySelector('code'))")


@pytest.mark.parametrize("ancho,alto", [(1920, 1080), (1366, 768), (768, 1024), (390, 844), (320, 640)])
def test_responsive_en_chromium_con_adjunto_y_trazabilidad(chrome, ancho, alto):
    chrome.abrir(ancho, alto)
    assert chrome.js("document.documentElement.scrollWidth <= innerWidth")
    chrome.js("guardar(); enviar('Consulta anterior')")
    chrome.espera("Boolean(document.querySelector('.detalles'))")
    chrome.js("document.querySelector('.detalles').open = true; document.querySelector('.atajos').open = true; imagen('image/png')")
    chrome.espera("!$('adjunto').hidden && $('vista-adjunto').naturalWidth === 2")
    assert chrome.js("document.documentElement.scrollWidth <= innerWidth && innerWidth") == ancho
    assert chrome.js("""
    ['pregunta', 'enviar', 'adjuntar', 'nueva-conversacion', 'cambiar-clave', 'quitar-adjunto'].every(id => {
      const e = $(id); e.scrollIntoView({block:'center'});
      const caja = e.getBoundingClientRect();
      const centro = document.elementFromPoint(caja.left + caja.width / 2, caja.top + caja.height / 2);
      return caja.left >= 0 && caja.right <= innerWidth && caja.height >= 44 && e.contains(centro);
    })
    """)
    captura = base64.b64decode(chrome.cdp("Page.captureScreenshot", format="png")["data"])
    assert captura[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", captura[16:24]) == (ancho, alto)
