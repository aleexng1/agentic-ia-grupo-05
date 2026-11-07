"""Pruebas del cliente A2A del coordinador. Sin red ni clave: el agente remoto está simulado en memoria."""

import asyncio

import httpx
import pytest
from google.protobuf.json_format import MessageToDict

import src.coordinador.cliente as cliente
from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta

URL = "http://remoto.test"
TARJETA = crear_tarjeta("Agente de mentira", "Repite lo que le dicen", URL, [("eco", "Eco", "Repite", "hola")])


@pytest.fixture(autouse=True)
def limpio(monkeypatch):
    cliente.CLIENTES.clear()
    cliente.FICHAS.clear()
    monkeypatch.setattr(cliente, "_transporte", None)
    monkeypatch.setenv("URL_VIAJES", URL)
    yield
    cliente.CLIENTES.clear()
    cliente.FICHAS.clear()


def _remoto_real(vistos):
    """Un agente remoto de verdad (el servidor de src/comun) conectado en memoria."""

    def responder(texto, context_id):
        vistos.append((texto, context_id))
        return f"eco: {texto}"

    return httpx.ASGITransport(app=crear_app(TARJETA, responder))


def _remoto_simulado(respuesta_post):
    """Un agente que entrega su ficha y responde a los mensajes con lo que se le indique."""

    def manejador(request):
        if request.method == "GET":
            return httpx.Response(200, json=MessageToDict(TARJETA))
        return respuesta_post(request)

    return httpx.MockTransport(manejador)


def _preguntar(texto="hola", context_id="ctx-1", url=URL):
    async def ejecutar():
        try:
            return await cliente.preguntar(await cliente.obtener_cliente(url), texto, context_id)
        finally:
            await cliente.cerrar_clientes()

    return asyncio.run(ejecutar())


def test_preguntar_devuelve_el_texto_y_manda_el_context_id(monkeypatch):
    vistos = []
    monkeypatch.setattr(cliente, "_transporte", _remoto_real(vistos))
    assert _preguntar("hola", "ctx-77") == "eco: hola"
    # Si el cliente no mandara la cabecera A2A-Version: 1.0, el servidor real habría rechazado el mensaje.
    assert vistos == [("hola", "ctx-77")]


def test_el_cliente_se_guarda_y_no_se_descarga_la_ficha_otra_vez(monkeypatch):
    monkeypatch.setattr(cliente, "_transporte", _remoto_real([]))

    async def ejecutar():
        primero = await cliente.obtener_cliente(URL)
        segundo = await cliente.obtener_cliente(URL + "/")
        await cliente.cerrar_clientes()
        return primero is segundo

    assert asyncio.run(ejecutar())


def test_error_remoto_con_http_200_sale_en_una_linea(monkeypatch):
    def con_error(request):
        return httpx.Response(200, json={"jsonrpc": "2.0", "id": 1, "error": {
            "code": -32009, "message": "version no soportada\ncon más detalle"}})

    monkeypatch.setattr(cliente, "_transporte", _remoto_simulado(con_error))
    with pytest.raises(cliente.ErrorRemoto) as error:
        _preguntar()
    linea = str(error.value)
    assert linea and "\n" not in linea and "Traceback" not in linea
    assert "version no soportada" in linea


def test_agente_caido_sale_en_una_linea(monkeypatch):
    def caido(request):
        raise httpx.ConnectError("sin conexión", request=request)

    monkeypatch.setattr(cliente, "_transporte", httpx.MockTransport(caido))
    with pytest.raises(cliente.ErrorRemoto) as error:
        _preguntar()
    assert "\n" not in str(error.value) and "levantado" in str(error.value)


def test_timeout_sale_en_una_linea(monkeypatch):
    def lento(request):
        raise httpx.ReadTimeout("lento", request=request)

    monkeypatch.setattr(cliente, "_transporte", _remoto_simulado(lento))
    with pytest.raises(cliente.ErrorRemoto) as error:
        _preguntar()
    assert "\n" not in str(error.value) and "a tiempo" in str(error.value)


def test_si_el_agente_responde_con_una_tarea_se_juntan_sus_artifacts(monkeypatch):
    def con_tarea(request):
        return httpx.Response(200, json={"jsonrpc": "2.0", "id": 1, "result": {"task": {
            "id": "t1", "contextId": "ctx-1", "status": {"state": "TASK_STATE_COMPLETED"},
            "artifacts": [
                {"artifactId": "a1", "parts": [{"text": "Primera parte."}]},
                {"artifactId": "a2", "parts": [{"text": "Segunda parte."}]},
            ]}}})

    monkeypatch.setattr(cliente, "_transporte", _remoto_simulado(con_tarea))
    assert _preguntar() == "Primera parte.\nSegunda parte."


def test_tarea_fallida_o_sin_texto_da_error_de_una_linea(monkeypatch):
    def tarea(estado):
        return lambda request: httpx.Response(200, json={"jsonrpc": "2.0", "id": 1, "result": {"task": {
            "id": "t1", "contextId": "ctx-1", "status": {"state": estado}}}})

    monkeypatch.setattr(cliente, "_transporte", _remoto_simulado(tarea("TASK_STATE_FAILED")))
    with pytest.raises(cliente.ErrorRemoto, match="falló"):
        _preguntar()
    cliente.CLIENTES.clear()
    monkeypatch.setattr(cliente, "_transporte", _remoto_simulado(tarea("TASK_STATE_WORKING")))
    with pytest.raises(cliente.ErrorRemoto, match="working"):
        _preguntar()
