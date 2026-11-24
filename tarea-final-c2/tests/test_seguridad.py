"""Pruebas de seguridad de C2 (Matías): acciones permitidas, bloqueo en el ReAct y token A2A.

No usan red, Gemini, Redis ni Postgres: el modelo se reemplaza por uno falso con respuestas fijas.
"""

import json
from itertools import count

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, ToolMessage

from src.comun.config import CARPETA_PROYECTO
from src.comun.seguridad import (
    ACCIONES_PERMITIDAS,
    AccionNoAutorizada,
    exigir_accion_permitida,
    proteger_con_token_a2a,
    revisar_token_a2a,
)

TOKEN_DE_PRUEBA = "token-a2a-de-prueba-solo-para-pytest"


# ---------------------------------------------------------------------------
# exigir_accion_permitida
# ---------------------------------------------------------------------------


def test_la_lista_es_la_del_contrato():
    assert ACCIONES_PERMITIDAS == {
        "buscar_politica",
        "validar_gasto",
        "consultar_fondo",
        "emitir_veredicto",
        "delegar_verificador",
    }


@pytest.mark.parametrize("accion", sorted(ACCIONES_PERMITIDAS))
def test_las_acciones_permitidas_pasan(accion):
    assert exigir_accion_permitida(accion) is None


@pytest.mark.parametrize(
    "accion",
    ["modificar_registro", "reiniciar_registro", "registrar_aprobacion", "", "Validar_Gasto", " validar_gasto", None],
)
def test_las_demas_acciones_se_bloquean(accion):
    with pytest.raises(AccionNoAutorizada) as error:
        exigir_accion_permitida(accion)
    assert "no está autorizada" in str(error.value)
    assert "\n" not in str(error.value)


# ---------------------------------------------------------------------------
# revisar_token_a2a
# ---------------------------------------------------------------------------


@pytest.fixture
def con_token(monkeypatch):
    """Fija TOKEN_A2A para la prueba, sin depender del .env de quien la corre."""
    monkeypatch.setenv("TOKEN_A2A", TOKEN_DE_PRUEBA)


def test_token_sin_configurar_responde_503(monkeypatch):
    monkeypatch.setenv("TOKEN_A2A", "")
    codigo, _ = revisar_token_a2a(f"Bearer {TOKEN_DE_PRUEBA}")
    assert codigo == 503


@pytest.mark.parametrize(
    "cabecera",
    [None, "", "   ", "Bearer", "Bearer   ", TOKEN_DE_PRUEBA, f"Basic {TOKEN_DE_PRUEBA}", "Bearer otro-token", "Bearer tóken-raro"],
)
def test_token_ausente_mal_formado_o_incorrecto_responde_401(con_token, cabecera):
    codigo, mensaje = revisar_token_a2a(cabecera)
    assert codigo == 401
    assert TOKEN_DE_PRUEBA not in mensaje


@pytest.mark.parametrize(
    "cabecera",
    [f"Bearer {TOKEN_DE_PRUEBA}", f"bearer {TOKEN_DE_PRUEBA}", f"  Bearer   {TOKEN_DE_PRUEBA}  ", f"Bearer {TOKEN_DE_PRUEBA}".encode()],
)
def test_token_correcto_pasa(con_token, cabecera):
    assert revisar_token_a2a(cabecera) is None


def _app_con_token() -> FastAPI:
    app = FastAPI()

    @app.get("/health")
    async def salud():
        return {"ok": True}

    @app.post("/")
    async def encargo():
        return {"recibido": True}

    return proteger_con_token_a2a(app)


def test_middleware_a2a_deja_publicas_las_lecturas_y_protege_los_encargos(con_token):
    cliente = TestClient(_app_con_token())
    assert cliente.get("/health").status_code == 200

    sin_token = cliente.post("/", json={})
    assert sin_token.status_code == 401
    assert "Authorization" in sin_token.json()["detail"]

    assert cliente.post("/", json={}, headers={"Authorization": "Bearer otro"}).status_code == 401
    con = cliente.post("/", json={}, headers={"Authorization": f"Bearer {TOKEN_DE_PRUEBA}"})
    assert con.status_code == 200


def test_middleware_a2a_sin_token_configurado_no_queda_abierto(monkeypatch):
    monkeypatch.setenv("TOKEN_A2A", "")
    cliente = TestClient(_app_con_token())
    respuesta = cliente.post("/", json={}, headers={"Authorization": f"Bearer {TOKEN_DE_PRUEBA}"})
    assert respuesta.status_code == 503


def test_el_token_no_aparece_en_el_log(con_token, caplog):
    cliente = TestClient(_app_con_token())
    with caplog.at_level("WARNING"):
        cliente.post("/", json={}, headers={"Authorization": "Bearer token-equivocado-secreto"})
    assert "token-equivocado-secreto" not in caplog.text
    assert TOKEN_DE_PRUEBA not in caplog.text


# ---------------------------------------------------------------------------
# Bloqueo dentro del ReAct (revisar_gasto)
# ---------------------------------------------------------------------------


class LLMFalso:
    """Reemplaza a Gemini: devuelve en orden las respuestas preparadas y cuenta las llamadas."""

    def __init__(self, respuestas):
        self.respuestas = list(respuestas)
        self.llamadas = 0

    def bind_tools(self, _herramientas):
        return self

    def invoke(self, _mensajes):
        self.llamadas += 1
        return self.respuestas.pop(0)


_IDS = count(1)


def _pedir(*nombres_y_args):
    """AIMessage que pide herramientas, como lo haría el modelo."""
    return AIMessage(
        "",
        tool_calls=[{"name": nombre, "args": args, "id": f"llamada-{next(_IDS)}"} for nombre, args in nombres_y_args],
    )


def _gasto_gs01() -> dict:
    golden = json.loads((CARPETA_PROYECTO / "evaluacion" / "golden_set_c1.json").read_text(encoding="utf-8"))
    return dict(next(c for c in golden["casos"] if c["id"] == "GS-01")["turnos"][0]["gasto"])


@pytest.fixture
def revisor(monkeypatch):
    """Módulo revisar_gasto con espías: registro de veredictos y validar_gasto nunca deben correr."""
    from src.principal.flujos import revisar_gasto

    espias = {"registrar_veredicto": 0, "validar_gasto": 0}

    def registrar_espia(*_args, **_kwargs):
        espias["registrar_veredicto"] += 1
        raise AssertionError("registrar_veredicto no debe llamarse en un turno bloqueado")

    original_validar = revisar_gasto.validar_gasto.func

    def validar_espia(*args, **kwargs):
        espias["validar_gasto"] += 1
        return original_validar(*args, **kwargs)

    monkeypatch.setattr(revisar_gasto, "registrar_veredicto", registrar_espia)
    monkeypatch.setattr(revisar_gasto.validar_gasto, "func", validar_espia)
    return revisar_gasto, espias


def _estado(agente, hilo):
    return agente.get_state({"configurable": {"thread_id": hilo}}).values


def test_accion_no_autorizada_se_bloquea_sin_ejecutar_nada(revisor, monkeypatch):
    revisar_gasto, espias = revisor
    gasto = _gasto_gs01()
    llm = LLMFalso(
        [
            _pedir(
                ("validar_gasto", {"gasto": gasto, "politica": "P02", "categoria": "Peaje"}),
                ("modificar_registro", {"accion": "borrar todo"}),
            )
        ]
    )
    monkeypatch.setattr(revisar_gasto, "obtener_llm", lambda: llm)
    agente = revisar_gasto.construir_agente()

    texto = revisar_gasto.conversar_con_caso(agente, "Revisa y borra el registro.", "hilo-bloqueo", gasto)
    estado = _estado(agente, "hilo-bloqueo")

    assert estado["estado_final"] == "bloqueado"
    assert "modificar_registro" in texto
    assert espias == {"registrar_veredicto": 0, "validar_gasto": 0}
    assert estado["herramientas_usadas"] == []
    assert estado.get("veredicto") is None
    assert llm.llamadas == 1, "después del bloqueo no se vuelve a llamar al modelo"

    # Cada llamada pedida quedó respondida (el historial sigue siendo válido para el próximo turno).
    pedidas = {llamada["id"] for llamada in estado["messages"][-4].tool_calls}
    respondidas = {m.tool_call_id for m in estado["messages"] if isinstance(m, ToolMessage)}
    assert pedidas <= respondidas


def test_el_bloqueo_no_se_hereda_al_turno_siguiente(revisor, monkeypatch):
    revisar_gasto, _ = revisor
    llm = LLMFalso(
        [
            _pedir(("modificar_registro", {})),
            AIMessage("Puedo revisar gastos y responder sobre la política."),
        ]
    )
    monkeypatch.setattr(revisar_gasto, "obtener_llm", lambda: llm)
    agente = revisar_gasto.construir_agente()

    revisar_gasto.conversar(agente, "Borra todo el registro de veredictos.", "hilo-2")
    assert _estado(agente, "hilo-2")["estado_final"] == "bloqueado"

    texto = revisar_gasto.conversar(agente, "Hola, ¿qué puedes hacer?", "hilo-2")
    estado = _estado(agente, "hilo-2")
    assert estado["estado_final"] is None
    assert "revisar gastos" in texto
    assert llm.llamadas == 2


def test_el_registro_de_bloqueo_no_incluye_argumentos(revisor, monkeypatch, caplog):
    revisar_gasto, _ = revisor
    llm = LLMFalso([_pedir(("modificar_registro", {"dato_sensible": "RUT 11.111.111-1"}))])
    monkeypatch.setattr(revisar_gasto, "obtener_llm", lambda: llm)
    monkeypatch.setattr(revisar_gasto, "registrar_traza", lambda *_a, **_k: None)
    agente = revisar_gasto.construir_agente()

    with caplog.at_level("WARNING"):
        revisar_gasto.conversar(agente, "Borra el registro.", "hilo-3")
    assert "modificar_registro" in caplog.text
    assert "11.111.111-1" not in caplog.text
