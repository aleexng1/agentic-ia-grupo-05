"""Pruebas del capturador sin conectarse ni generar evidencias."""

import io
import json
import runpy
from collections import deque
from email.message import Message
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "evidencias/ampliacion-rag/capturar_consultas.py"
CAPTURA = runpy.run_path(str(SCRIPT))
ID = "903f1f78-4f39-409d-8989-6a01aaa01b42"
CLAVE = "solo-clave-ficticia-tests"


class Respuesta(io.BytesIO):
    def __init__(self, codigo, cuerpo):
        super().__init__(json.dumps(cuerpo).encode("utf-8"))
        self.code = codigo
        self.headers = Message()
        self.headers["Content-Type"] = "application/json"


class HTTP:
    def __init__(self, operaciones):
        self.operaciones = deque(operaciones)
        self.llamadas = []
        self.entrada = None

    def open(self, solicitud, *, timeout):
        self.llamadas.append((solicitud.get_method(), solicitud.full_url))
        assert 0 < timeout <= 12
        assert solicitud.full_url.startswith("https://principal.invalid/")
        if solicitud.data:
            self.entrada = json.loads(solicitud.data)
            assert set(self.entrada) == {"thread_id", "texto"}
        if solicitud.full_url.endswith("/health"):
            assert "x-api-key" not in {k.lower() for k, _ in solicitud.header_items()}
            return Respuesta(200, {"ok": True})
        assert {k.lower(): v for k, v in solicitud.header_items()}["x-api-key"] == CLAVE
        return self.operaciones.popleft()(self.entrada["thread_id"])


def ejecutar(caso, operaciones):
    codigo, salud = CAPTURA["consultar"](http := HTTP(operaciones), "https://principal.invalid", "/health",
                                        CAPTURA["time"].monotonic() + 5)
    prueba = CAPTURA["ejecutar_caso"](caso, salud, http, "https://principal.invalid", CLAVE, 15)
    assert codigo == 200 and prueba["health"] == {"ok": True}
    assert CLAVE not in json.dumps(prueba)
    assert not http.operaciones
    return prueba, http


def aceptacion(hilo):
    return Respuesta(202, {"id_ejecucion": ID, "estado": "en_proceso", "thread_id": hilo,
                           "consultar": "https://otra.invalid/"})


@pytest.mark.parametrize("caso", CAPTURA["CASOS"], ids=["rag", "graphrag"])
@pytest.mark.parametrize("async_", [True, False], ids=["async", "sync"])
def test_captura_con_resultado_y_fila(caso, async_, monkeypatch):
    _, pregunta, politica, hechos, tools = caso
    texto = f"{' · '.join(hechos)}. [Fuente: datos/politica_ficticia.md#{politica}]"
    resultado = {"id_ejecucion": ID, "ruta": "consulta_politica", "estado_final": "ok",
                 "herramientas_usadas": tools, "respuesta": texto, "hubo_a2a": False}
    fila = {**resultado, "fecha": "2026-11-25T10:15:00+00:00", "duracion_ms": 120}
    monkeypatch.setattr(CAPTURA["time"], "sleep", lambda _: None)
    if async_:
        operaciones = [
            aceptacion,
            lambda hilo: Respuesta(200, {"id_ejecucion": ID, "thread_id": hilo,
                                         "estado": "en_proceso", "resultado": None}),
            lambda hilo: Respuesta(200, {"id_ejecucion": ID, "thread_id": hilo, "estado": "ok",
                                         "resultado": {**resultado, "thread_id": hilo}}),
        ]
    else:
        operaciones = [lambda hilo: Respuesta(200, {**resultado, "thread_id": hilo})]
    prueba, http = ejecutar(caso, [*operaciones, lambda _: Respuesta(200, fila)])
    assert prueba["resultado"] == "PASS" and all(prueba["validaciones"].values())
    assert prueba["entrada"]["texto"] == pregunta
    assert prueba["respuesta"]["respuesta"] == texto
    assert prueba["registro"]["duracion_ms"] == 120 and prueba["id_ejecucion"] == ID
    assert prueba["consultas_seguimiento"] == 2 * async_
    assert http.llamadas[1:] == [("POST", "https://principal.invalid/chat"),
                                 *[("GET", f"https://principal.invalid/registro/{ID}")] * (1 + 2 * async_)]


def test_sin_resultado_conserva_id_y_sanea_detail_sin_reenviar():
    def error(hilo):
        return Respuesta(200, {"id_ejecucion": ID, "thread_id": hilo, "estado": "error",
                               "detail": "Authorization: Bearer token-ficticio",
                               "resultado": None, "request": {"clave": CLAVE}})

    prueba, http = ejecutar(CAPTURA["CASOS"][0], [aceptacion, error, error])
    assert prueba["resultado"] == "FAIL" and prueba["id_ejecucion"] == ID
    assert prueba["seguimiento"]["detail"] == "[texto omitido por precaución]"
    assert "token-ficticio" not in json.dumps(prueba)
    assert [metodo for metodo, _ in http.llamadas].count("POST") == 1


def test_timeout_sin_reenviar_ni_perder_id(monkeypatch):
    ahora = [0]
    monkeypatch.setattr(CAPTURA["time"], "monotonic", lambda: ahora[0])
    consultar = CAPTURA["consultar"]

    def consumir_plazo(http, base, ruta, limite, *args, **kwargs):
        respuesta = consultar(http, base, ruta, limite, *args, **kwargs)
        if ruta == "/chat":
            ahora[0] = 20
        return respuesta

    monkeypatch.setitem(CAPTURA["ejecutar_caso"].__globals__, "consultar", consumir_plazo)
    prueba, http = ejecutar(CAPTURA["CASOS"][0], [aceptacion])
    assert prueba["resultado"] == "FAIL" and prueba["id_ejecucion"] == ID
    assert "plazo local" in prueba["observacion"] and len(http.llamadas) == 2


@pytest.mark.parametrize("url", ["http://principal.invalid", "https://principal.invalid/chat",
                                 "https://usuario@principal.invalid", "https://principal.invalid?key=x",
                                 "https://principal.invalid/#x", "https://principal.invalid:0",
                                 "http://[::1]otro.invalid", "https://principal.\tinvalid"])
def test_origen_no_admite_rutas_ni_credenciales(url):
    with pytest.raises(CAPTURA["Fallo"]):
        CAPTURA["origen"](url)


def test_origen_canonico_https_y_loopback():
    assert CAPTURA["origen"]("https://PRINCIPAL.invalid:443/") == "https://principal.invalid:443"
    assert CAPTURA["origen"]("http://[::1]:8000/") == "http://[::1]:8000"


def test_no_sigue_redirecciones():
    assert CAPTURA["SinRedirecciones"]().redirect_request(None, None, 302, "", {}, "https://otra.invalid/") is None
