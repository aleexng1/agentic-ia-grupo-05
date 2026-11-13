"""Pruebas del control de acceso (X-API-Key) y del manejo de errores, sin llamar a Gemini."""

import asyncio

import httpx
import pytest
from fastapi.testclient import TestClient

import app as modulo_app
from src.comun import errores, seguridad
from src.comun.errores import ErrorDeServicio, traducir_error

from tests.conftest import CLAVE_DE_PRUEBA


CABECERA = {"X-API-Key": CLAVE_DE_PRUEBA}
PREGUNTA = {"texto": "¿Qué actividades pongo?", "context_id": "prueba-seguridad"}
# Clave de Gemini falsa con la forma de una real. Se arma por partes a propósito: así el
# archivo no contiene ningún texto que un escáner de secretos confunda con una clave.
CLAVE_GEMINI_FALSA = "AI" "zaSyFALSA_PARA_PRUEBAS_0123456789abcdefg"


@pytest.fixture
def cliente():
    """Cliente HTTP en memoria; no se usa la red ni Gemini."""
    return TestClient(modulo_app.app)


def _detalle(respuesta) -> str:
    return respuesta.json()["detail"]


# ---------- acceso permitido y rechazado ----------


def test_sin_clave_responde_401_con_detail(cliente):
    respuesta = cliente.post("/panel/consultar", json=PREGUNTA)
    assert respuesta.status_code == 401
    assert _detalle(respuesta) == seguridad.MENSAJE_FALTA
    assert "X-API-Key" in _detalle(respuesta)


def test_clave_incorrecta_responde_401_con_detail(cliente):
    respuesta = cliente.post(
        "/panel/consultar", json=PREGUNTA, headers={"X-API-Key": "una-clave-que-no-es"}
    )
    assert respuesta.status_code == 401
    assert _detalle(respuesta) == seguridad.MENSAJE_INCORRECTA


def test_clave_vacia_se_trata_como_ausente(cliente):
    respuesta = cliente.post("/panel/consultar", json=PREGUNTA, headers={"X-API-Key": "  "})
    assert respuesta.status_code == 401
    assert _detalle(respuesta) == seguridad.MENSAJE_FALTA


def test_clave_con_caracteres_no_ascii_no_rompe(cliente):
    respuesta = cliente.post(
        "/panel/consultar",
        json=PREGUNTA,
        headers={"X-API-Key": "contraseña-ñandú".encode("latin-1")},
    )
    assert respuesta.status_code == 401


def test_clave_correcta_con_texto_vacio_responde_400(cliente):
    respuesta = cliente.post(
        "/panel/consultar", json={"texto": "", "context_id": "x"}, headers=CABECERA
    )
    assert respuesta.status_code == 400
    assert "pregunta" in _detalle(respuesta).lower()


def test_clave_correcta_con_solo_espacios_responde_400(cliente):
    respuesta = cliente.post(
        "/panel/consultar", json={"texto": "   \n  "}, headers=CABECERA
    )
    assert respuesta.status_code == 400


@pytest.mark.parametrize(
    "ruta",
    [
        "/salud",
        "/",
        "/.well-known/agent-card.json",
        "/agentes/matias/.well-known/agent-card.json",
        "/agentes/alex/.well-known/agent-card.json",
        "/agentes/eduardo/.well-known/agent-card.json",
        "/agentes/sebastian/.well-known/agent-card.json",
    ],
)
def test_lecturas_publicas_sin_clave_responden_200(cliente, ruta):
    assert cliente.get(ruta).status_code == 200


@pytest.mark.parametrize(
    "ruta",
    ["/", "/agentes/matias", "/agentes/alex", "/agentes/eduardo", "/agentes/sebastian"],
)
def test_jsonrpc_a2a_sin_clave_responde_401(cliente, ruta):
    """El JSON-RPC del coordinador y de cada agente también exige la clave."""
    cuerpo = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "SendMessage",
        "params": {
            "message": {
                "role": "ROLE_USER",
                "messageId": "m1",
                "contextId": "c1",
                "parts": [{"text": "hola"}],
            }
        },
    }
    respuesta = cliente.post(ruta, json=cuerpo, headers={"A2A-Version": "1.0"})
    assert respuesta.status_code == 401
    assert _detalle(respuesta) == seguridad.MENSAJE_FALTA


def test_la_respuesta_de_rechazo_no_revela_la_clave(cliente):
    respuesta = cliente.post("/panel/consultar", json=PREGUNTA, headers={"X-API-Key": "mala"})
    assert CLAVE_DE_PRUEBA not in respuesta.text
    assert "mala" not in respuesta.text


def test_el_rechazo_se_registra_sin_la_clave(cliente, caplog):
    import logging

    registro = logging.getLogger("coordinador")
    registro.propagate = True  # para que caplog lo vea; configurar_registro lo apaga
    try:
        with caplog.at_level(logging.WARNING, logger="coordinador"):
            cliente.post("/panel/consultar", json=PREGUNTA, headers={"X-API-Key": "intento-secreto"})
    finally:
        registro.propagate = False
    texto = caplog.text
    assert "acceso rechazado" in texto
    assert "intento-secreto" not in texto
    assert CLAVE_DE_PRUEBA not in texto


# ---------- servidor sin CLAVE_API ----------


def test_servidor_sin_clave_no_queda_abierto(cliente, monkeypatch):
    """Con CLAVE_API vacía no se acepta ninguna consulta, ni siquiera sin cabecera."""
    monkeypatch.setenv("CLAVE_API", "")
    for cabeceras in ({}, CABECERA, {"X-API-Key": ""}):
        respuesta = cliente.post("/panel/consultar", json=PREGUNTA, headers=cabeceras)
        assert respuesta.status_code == 503
        assert "CLAVE_API" in _detalle(respuesta)


def test_servidor_sin_clave_mantiene_publicas_la_salud_y_las_fichas(cliente, monkeypatch):
    monkeypatch.setenv("CLAVE_API", "")
    assert cliente.get("/salud").status_code == 200
    assert cliente.get("/.well-known/agent-card.json").status_code == 200


def test_aviso_de_arranque_si_falta_la_clave(monkeypatch, caplog):
    import logging

    monkeypatch.setenv("CLAVE_API", "")
    registro = logging.getLogger("coordinador")
    registro.propagate = True
    try:
        with caplog.at_level(logging.ERROR, logger="coordinador"):
            asyncio.run(seguridad.avisar_si_falta_clave())
    finally:
        registro.propagate = False
    assert "CLAVE_API está vacía" in caplog.text


def test_sin_aviso_de_arranque_si_hay_clave(caplog):
    import logging

    registro = logging.getLogger("coordinador")
    registro.propagate = True
    try:
        with caplog.at_level(logging.ERROR, logger="coordinador"):
            asyncio.run(seguridad.avisar_si_falta_clave())
    finally:
        registro.propagate = False
    assert "CLAVE_API" not in caplog.text


def test_revisar_clave_acepta_bytes_y_texto():
    assert seguridad.revisar_clave(CLAVE_DE_PRUEBA) is None
    assert seguridad.revisar_clave(CLAVE_DE_PRUEBA.encode()) is None
    assert seguridad.revisar_clave(None)[0] == 401
    assert seguridad.revisar_clave("otra")[0] == 401


# ---------- el coordinador se llama a sí mismo con la clave ----------


def _solicitud(url: str) -> httpx.Request:
    return httpx.Request("POST", url)


def test_el_cliente_interno_envia_la_clave_solo_a_esta_misma_app(monkeypatch):
    from src.coordinador import cliente as modulo_cliente

    monkeypatch.setenv("PORT", "5123")

    async def _probar():
        propia = _solicitud("http://127.0.0.1:5123/agentes/alex")
        await modulo_cliente._agregar_clave_interna(propia)
        return propia

    propia = asyncio.run(_probar())
    assert propia.headers["X-API-Key"] == CLAVE_DE_PRUEBA


@pytest.mark.parametrize(
    "url",
    [
        "https://otro-computador.trycloudflare.com/",  # agente de otro equipo
        "http://127.0.0.1:9999/agentes/alex",  # otro puerto local: no es esta app
        "http://localhost:5123/agentes/alex",  # otro nombre de host
        "https://api.example.com:5123/agentes/alex",
    ],
)
def test_el_cliente_interno_no_envia_la_clave_a_otras_direcciones(monkeypatch, url):
    from src.coordinador import cliente as modulo_cliente

    monkeypatch.setenv("PORT", "5123")

    async def _probar():
        ajena = _solicitud(url)
        await modulo_cliente._agregar_clave_interna(ajena)
        return ajena

    ajena = asyncio.run(_probar())
    assert "X-API-Key" not in ajena.headers


def test_el_cliente_interno_no_envia_nada_si_no_hay_clave(monkeypatch):
    from src.coordinador import cliente as modulo_cliente

    monkeypatch.setenv("PORT", "5123")
    monkeypatch.setenv("CLAVE_API", "")

    async def _probar():
        propia = _solicitud("http://127.0.0.1:5123/agentes/alex")
        await modulo_cliente._agregar_clave_interna(propia)
        return propia

    assert "X-API-Key" not in asyncio.run(_probar()).headers


def test_el_gancho_del_coordinador_hace_pasar_el_control_de_acceso(monkeypatch):
    """Contra la app real en memoria: la misma llamada al JSON-RPC de un agente recibe 401
    sin el gancho y pasa el control de acceso con él (el cliente del coordinador lo usa)."""
    from src.coordinador import cliente as modulo_cliente

    monkeypatch.setenv("PORT", "5123")
    llamada = {
        "url": "http://127.0.0.1:5123/agentes/matias",
        "json": {"jsonrpc": "2.0", "id": "1", "method": "SendMessage", "params": {}},
        "headers": {"A2A-Version": "1.0"},
    }

    async def _probar():
        transporte = httpx.ASGITransport(app=modulo_app.app)
        async with httpx.AsyncClient(transport=transporte) as sin_gancho:
            rechazada = await sin_gancho.post(**llamada)
        async with httpx.AsyncClient(
            transport=transporte, event_hooks={"request": [modulo_cliente._agregar_clave_interna]}
        ) as con_gancho:
            aceptada = await con_gancho.post(**llamada)
        return rechazada, aceptada

    rechazada, aceptada = asyncio.run(_probar())
    assert rechazada.status_code == 401
    assert aceptada.status_code != 401
    assert aceptada.status_code != 503


# ---------- errores: nunca como respuesta exitosa ----------


class _GrafoQueFalla:
    def __init__(self, error: Exception):
        self.error = error

    async def ainvoke(self, entrada, config):
        raise self.error


@pytest.fixture
def grafo_que_falla(monkeypatch):
    """Reemplaza el grafo por uno que falla; así no se usa Gemini."""
    from src.coordinador import graph as modulo_graph

    async def _sin_descubrir(imprimir=False):
        return None

    monkeypatch.setattr(modulo_graph, "inicializar_supervisor", _sin_descubrir)

    def _poner(error: Exception):
        monkeypatch.setattr(modulo_graph, "graph", _GrafoQueFalla(error))

    return _poner


def test_clave_de_gemini_invalida_responde_502_claro(cliente, grafo_que_falla):
    grafo_que_falla(
        Exception(
            "400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'API key not valid. "
            "Please pass a valid API key.', 'status': 'INVALID_ARGUMENT'}}"
        )
    )
    respuesta = cliente.post("/panel/consultar", json=PREGUNTA, headers=CABECERA)
    assert respuesta.status_code == 502
    assert errores.MENSAJE_CLAVE_GEMINI in _detalle(respuesta)
    assert "Traceback" not in respuesta.text


def test_gemini_sin_cuota_responde_502_claro(cliente, grafo_que_falla):
    grafo_que_falla(
        Exception("402 RESOURCE_EXHAUSTED. Your prepayment credits are depleted.")
    )
    respuesta = cliente.post("/panel/consultar", json=PREGUNTA, headers=CABECERA)
    assert respuesta.status_code == 502
    assert errores.MENSAJE_SIN_CUOTA in _detalle(respuesta)


def test_sin_conexion_responde_502_claro(cliente, grafo_que_falla):
    grafo_que_falla(httpx.ConnectError("All connection attempts failed"))
    respuesta = cliente.post("/panel/consultar", json=PREGUNTA, headers=CABECERA)
    assert respuesta.status_code == 502
    assert errores.MENSAJE_SIN_CONEXION in _detalle(respuesta)


def test_una_falla_no_se_presenta_como_respuesta_exitosa(cliente, grafo_que_falla):
    grafo_que_falla(RuntimeError("falla inesperada"))
    respuesta = cliente.post("/panel/consultar", json=PREGUNTA, headers=CABECERA)
    assert respuesta.status_code == 502
    assert "respuesta" not in respuesta.json()


def test_el_error_no_filtra_claves_ni_trazas(cliente, grafo_que_falla, monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", CLAVE_GEMINI_FALSA)
    grafo_que_falla(
        RuntimeError(
            f"fallo raro con key={CLAVE_GEMINI_FALSA}\nTraceback (most recent call last):\n"
            f'  File "x.py", line 1, in <module>\nX-API-Key: {CLAVE_DE_PRUEBA}'
        )
    )
    respuesta = cliente.post("/panel/consultar", json=PREGUNTA, headers=CABECERA)
    assert respuesta.status_code == 502
    assert CLAVE_GEMINI_FALSA not in respuesta.text
    assert CLAVE_DE_PRUEBA not in respuesta.text
    assert "\n" not in _detalle(respuesta)


def test_sin_agentes_disponibles_es_un_error_y_no_una_respuesta(cliente, monkeypatch):
    """Si no responde ningún agente, la pregunta falla con 502 (no «No tengo un agente»)."""
    from src.coordinador import graph as modulo_graph

    async def _descubrir_nada():
        return []

    monkeypatch.setattr(modulo_graph, "descubrir", _descubrir_nada)
    monkeypatch.setattr(modulo_graph, "_INICIALIZADO", False)
    monkeypatch.setattr(modulo_graph, "_CATALOGO", [])
    monkeypatch.setattr(modulo_graph, "graph", modulo_graph._crear_grafo([]))
    respuesta = cliente.post("/panel/consultar", json=PREGUNTA, headers=CABECERA)
    assert respuesta.status_code == 502
    assert "No hay agentes disponibles" in _detalle(respuesta)


def test_un_agente_que_falla_se_informa_como_error_a2a():
    """El ejecutor de un agente ya no convierte la falla en un mensaje normal."""
    from fastapi import FastAPI

    from src.comun.servidor import registrar_agente
    from src.agente_matias.server import tarjeta

    async def _responder_que_falla(texto, context_id):
        raise Exception("429 RESOURCE_EXHAUSTED: quota exceeded")

    chico = FastAPI()
    registrar_agente(chico, tarjeta, _responder_que_falla, prefijo="/agentes/prueba")
    respuesta = TestClient(chico).post(
        "/agentes/prueba",
        json={
            "jsonrpc": "2.0",
            "id": "1",
            "method": "SendMessage",
            "params": {
                "message": {
                    "role": "ROLE_USER",
                    "messageId": "m1",
                    "contextId": "c1",
                    "parts": [{"text": "hola"}],
                }
            },
        },
        headers={"A2A-Version": "1.0"},
    )
    cuerpo = respuesta.json()
    assert "error" in cuerpo and "result" not in cuerpo
    assert errores.MENSAJE_SIN_CUOTA in cuerpo["error"]["message"]


# ---------- traducción de errores ----------


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("API key not valid. Please pass a valid API key.", errores.MENSAJE_CLAVE_GEMINI),
        ("API_KEY_INVALID", errores.MENSAJE_CLAVE_GEMINI),
        ("402 RESOURCE_EXHAUSTED credits depleted", errores.MENSAJE_SIN_CUOTA),
        ("429 Too Many Requests: quota exceeded", errores.MENSAJE_SIN_CUOTA),
        ("403 PERMISSION_DENIED", errores.MENSAJE_SIN_PERMISO),
        ("404 NOT_FOUND: model gemini-x is not found", errores.MENSAJE_MODELO),
        ("Request timed out.", errores.MENSAJE_TIEMPO),
        ("All connection attempts failed", errores.MENSAJE_SIN_CONEXION),
        ("[Errno 11001] getaddrinfo failed", errores.MENSAJE_SIN_CONEXION),
        ("503 UNAVAILABLE: the model is overloaded", errores.MENSAJE_NO_DISPONIBLE),
    ],
)
def test_traducir_error_reconoce_las_fallas_del_proveedor(texto, esperado):
    assert traducir_error(Exception(texto)) == esperado


def test_traducir_error_deja_pasar_los_mensajes_ya_claros():
    """Si una capa recibe el mensaje de otra (coordinador ← agente), no lo reescribe."""
    envuelto = Exception(f"Error del agente remoto: {errores.MENSAJE_SIN_CUOTA} (código -32603)")
    assert traducir_error(envuelto) == errores.MENSAJE_SIN_CUOTA
    assert traducir_error(ErrorDeServicio("Mensaje propio.")) == "Mensaje propio."


def test_traducir_error_desconocido_es_una_linea_recortada_y_sin_secretos():
    texto = "algo raro " + "x" * 500 + f" api_key={CLAVE_GEMINI_FALSA}\nsegunda línea"
    resultado = traducir_error(Exception(texto))
    assert resultado.startswith("No se pudo completar la consulta: ")
    assert "\n" not in resultado
    assert CLAVE_GEMINI_FALSA not in resultado
    assert len(resultado) < 300


def test_ocultar_secretos_no_toca_frases_normales():
    assert errores.ocultar_secretos("API key not valid") == "API key not valid"
    assert "oculta" in errores.ocultar_secretos("Authorization: Bearer abcdefgh12345678")
    assert CLAVE_GEMINI_FALSA not in errores.ocultar_secretos(f"usé {CLAVE_GEMINI_FALSA}")
