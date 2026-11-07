"""Pruebas de la página local (src/web). Los agentes están simulados: no se usa la red."""

import json

import httpx
import pytest
from fastapi.testclient import TestClient

import src.web.app as web

CLAVE_SECRETA = "CLAVE-SECRETA-NO-MOSTRAR"
URL_VIAJES = "http://viajes-secreto.test:8000"

FICHA_VIAJES = {
    "name": "Agente de viajes",
    "description": "Busca vuelos y hoteles.",
    "skills": [
        {"id": "v", "name": "Buscar vuelos", "description": "Vuelos", "examples": ["Vuelo a Lima"]}
    ],
}


def _agente_simulado(respuesta_mensaje, peticiones):
    """Simula el agente de viajes. Restaurantes y coordinador están caídos."""

    def manejador(request):
        if request.url.host != "viajes-secreto.test":
            raise httpx.ConnectError("sin conexión", request=request)
        if request.method == "GET":
            return httpx.Response(200, json=FICHA_VIAJES)
        peticiones.append(request)
        return respuesta_mensaje(request)

    return httpx.MockTransport(manejador)


def _respuesta_ok(request):
    mensaje = json.loads(request.content)["params"]["message"]
    return httpx.Response(200, json={
        "jsonrpc": "2.0", "id": 1,
        "result": {"message": {"contextId": mensaje["contextId"], "role": "ROLE_AGENT",
                               "parts": [{"text": "Hay 3 vuelos."}]}},
    })


@pytest.fixture
def peticiones():
    return []


@pytest.fixture
def cliente(monkeypatch, peticiones):
    monkeypatch.setenv("URL_VIAJES", URL_VIAJES)
    monkeypatch.setenv("URL_RESTAURANTES", "http://restaurantes-secreto.test:8001")
    monkeypatch.setenv("URL_COORDINADOR", "http://coordinador-secreto.test:8002")
    monkeypatch.setenv("GOOGLE_API_KEY", CLAVE_SECRETA)
    monkeypatch.setattr(web, "_transporte", _agente_simulado(_respuesta_ok, peticiones))
    return TestClient(web.app, base_url="http://127.0.0.1:8080")


def test_lista_muestra_disponible_y_no_disponible(cliente):
    agentes = {a["id"]: a for a in cliente.get("/api/agentes").json()}
    assert agentes["viajes"]["disponible"] is True
    assert agentes["viajes"]["nombre"] == "Agente de viajes"
    assert agentes["viajes"]["skills"][0]["ejemplo"] == "Vuelo a Lima"
    assert agentes["restaurantes"]["disponible"] is False
    assert agentes["coordinador"]["disponible"] is False
    assert "levantado" in agentes["restaurantes"]["motivo"]


def test_no_se_filtran_urls_ni_claves(cliente):
    cliente.post("/api/mensaje", json={"agente": "viajes", "texto": "hola"})
    textos = [cliente.get("/api/agentes").text, cliente.get("/").text]
    textos.append(cliente.post("/api/mensaje", json={"agente": "viajes", "texto": "hola"}).text)
    textos.append(cliente.post("/api/mensaje", json={"agente": "restaurantes", "texto": "hola"}).text)
    for texto in textos:
        for secreto in (CLAVE_SECRETA, "secreto.test"):
            assert secreto not in texto


def test_mensaje_usa_el_protocolo_de_la_1_3_0(cliente, peticiones):
    r = cliente.post("/api/mensaje", json={"agente": "viajes", "texto": "  Vuelo a Lima  "})
    assert r.status_code == 200
    assert r.json()["texto"] == "Hay 3 vuelos."
    enviada = peticiones[0]
    cuerpo = json.loads(enviada.content)
    assert enviada.headers["A2A-Version"] == "1.0"
    assert cuerpo["method"] == "SendMessage"
    assert cuerpo["params"]["message"]["role"] == "ROLE_USER"
    assert cuerpo["params"]["message"]["parts"] == [{"text": "Vuelo a Lima"}]


def test_el_servidor_inventa_context_id_y_lo_respeta(cliente, peticiones):
    primero = cliente.post("/api/mensaje", json={"agente": "viajes", "texto": "hola"}).json()
    assert primero["contextId"]
    segundo = cliente.post("/api/mensaje", json={
        "agente": "viajes", "texto": "otra", "contextId": primero["contextId"]}).json()
    assert segundo["contextId"] == primero["contextId"]
    enviados = [json.loads(p.content)["params"]["message"]["contextId"] for p in peticiones]
    assert enviados == [primero["contextId"], primero["contextId"]]


def test_error_con_http_200_se_muestra_en_una_linea(cliente, monkeypatch):
    def con_error(request):
        return httpx.Response(200, json={"jsonrpc": "2.0", "id": 1, "error": {
            "code": -32009, "message": "A2A version '0.3' is not\nsupported"}})

    monkeypatch.setattr(web, "_transporte", _agente_simulado(con_error, []))
    datos = cliente.post("/api/mensaje", json={"agente": "viajes", "texto": "hola"}).json()
    assert "texto" not in datos
    assert "-32009" in datos["error"] and "\n" not in datos["error"]


def test_respuesta_con_formato_inesperado(cliente, monkeypatch):
    monkeypatch.setattr(web, "_transporte", _agente_simulado(
        lambda r: httpx.Response(200, json={"result": {"task": {}}}), []))
    datos = cliente.post("/api/mensaje", json={"agente": "viajes", "texto": "hola"}).json()
    assert "parts[0].text" in datos["error"]


def test_agente_caido_y_timeout_dan_error_de_una_linea(cliente):
    caido = cliente.post("/api/mensaje", json={"agente": "restaurantes", "texto": "hola"}).json()
    assert "levantado" in caido["error"]


def test_timeout_del_agente(cliente, monkeypatch):
    def lento(request):
        raise httpx.ReadTimeout("lento", request=request)

    monkeypatch.setattr(web, "_transporte", _agente_simulado(lento, []))
    datos = cliente.post("/api/mensaje", json={"agente": "viajes", "texto": "hola"}).json()
    assert "demasiado" in datos["error"]


def test_agente_desconocido_y_texto_vacio(cliente):
    assert cliente.post("/api/mensaje", json={"agente": "otro", "texto": "hola"}).status_code == 404
    assert cliente.post("/api/mensaje", json={"agente": "viajes", "texto": "   "}).status_code == 400
    largo = "x" * (web.LARGO_MAX_TEXTO + 1)
    assert cliente.post("/api/mensaje", json={"agente": "viajes", "texto": largo}).status_code == 422


def test_rechaza_origen_y_host_ajenos(cliente):
    cuerpo = {"agente": "viajes", "texto": "hola"}
    assert cliente.post("/api/mensaje", json=cuerpo, headers={"Origin": "http://sitio-malo.com"}).status_code == 403
    assert cliente.post("/api/mensaje", json=cuerpo, headers={"Origin": "http://127.0.0.1:8080"}).status_code == 200
    assert cliente.get("/api/agentes", headers={"Host": "sitio-malo.com"}).status_code == 403
