"""/chat asíncrono (Alex): 202 + GET /registro/{id}, tope global y ?esperar=true. Sin Gemini."""

import threading
import time

import pytest
from fastapi.testclient import TestClient

from src.principal import en_segundo_plano
from src.principal import grafo as modulo_grafo
from src.principal import router
from tests.conftest import CLAVE_DE_PRUEBA
from tests.test_grafo import filas, ruta_fija  # noqa: F401  (fixtures del grafo)

CABECERAS = {"X-API-Key": CLAVE_DE_PRUEBA}


@pytest.fixture
def cliente(monkeypatch):
    from api.app import app

    monkeypatch.setattr(modulo_grafo, "_GRAFO", modulo_grafo.construir_grafo())
    return TestClient(app)


def esperar_fin(cliente, id_ejecucion, segundos=5.0):
    """Consulta GET /registro/{id} como lo haría la web, hasta que deje de estar en proceso."""
    fin = time.monotonic() + segundos
    while time.monotonic() < fin:
        datos = cliente.get(f"/registro/{id_ejecucion}", headers=CABECERAS).json()
        if datos["estado"] != "en_proceso":
            return datos
        time.sleep(0.05)
    raise AssertionError(f"la ejecución {id_ejecucion} no terminó en {segundos} s")


def test_post_chat_responde_202_y_el_resultado_se_consulta_en_registro(cliente, ruta_fija, filas):
    ruta_fija("fuera_de_alcance")
    respuesta = cliente.post("/chat", json={"thread_id": "t-async", "texto": "Escríbeme un poema"}, headers=CABECERAS)
    assert respuesta.status_code == 202
    aceptado = respuesta.json()
    assert aceptado["estado"] == "en_proceso" and aceptado["thread_id"] == "t-async"
    assert aceptado["consultar"] == f"/registro/{aceptado['id_ejecucion']}"

    datos = esperar_fin(cliente, aceptado["id_ejecucion"])
    assert datos["estado"] == "ok" and datos["detail"] is None
    assert datos["resultado"]["ruta"] == "fuera_de_alcance"
    assert datos["resultado"]["id_ejecucion"] == aceptado["id_ejecucion"]  # el mismo id de punta a punta
    assert filas[0]["id_ejecucion"] == aceptado["id_ejecucion"] and filas[0]["estado_final"] == "ok"


def test_mientras_corre_registro_dice_en_proceso(cliente, ruta_fija, filas, monkeypatch):
    ruta_fija("fuera_de_alcance")
    sigue = threading.Event()
    original = modulo_grafo.ejecutar

    def lento(*args, **kwargs):
        sigue.wait(5)
        return original(*args, **kwargs)

    monkeypatch.setattr(modulo_grafo, "ejecutar", lento)
    aceptado = cliente.post("/chat", json={"texto": "hola"}, headers=CABECERAS).json()
    en_curso = cliente.get(aceptado["consultar"], headers=CABECERAS).json()
    assert en_curso["estado"] == "en_proceso" and en_curso["resultado"] is None
    assert en_curso["segundos"] >= 0
    sigue.set()
    assert esperar_fin(cliente, aceptado["id_ejecucion"])["estado"] == "ok"


def test_texto_invalido_responde_422_sin_aceptar(cliente, monkeypatch):
    monkeypatch.setattr(router, "clasificar", lambda *a, **k: pytest.fail("no debía llamar al router"))
    respuesta = cliente.post("/chat", json={"texto": "   "}, headers=CABECERAS)
    assert respuesta.status_code == 422 and "vacío" in respuesta.json()["detail"]


def test_falla_del_flujo_queda_en_error_con_mensaje_claro(cliente, filas, monkeypatch):
    def falla(*args, **kwargs):
        raise RuntimeError("503 UNAVAILABLE")

    monkeypatch.setattr(router, "clasificar", falla)
    aceptado = cliente.post("/chat", json={"texto": "hola"}, headers=CABECERAS).json()
    datos = esperar_fin(cliente, aceptado["id_ejecucion"])
    assert datos["estado"] == "error" and datos["resultado"] is None
    assert f"id_ejecucion: {aceptado['id_ejecucion']}" in datos["detail"]


def test_tope_global_deja_error_sin_resultado_y_registra_la_fila(cliente, ruta_fija, filas, monkeypatch):
    monkeypatch.setenv("TIEMPO_MAX_EJECUCION_SEG", "0.3")
    ruta_fija("fuera_de_alcance")
    sigue = threading.Event()
    original = modulo_grafo.ejecutar

    def colgado(*args, **kwargs):
        sigue.wait(5)  # como un modelo que no responde
        return original(*args, **kwargs)

    monkeypatch.setattr(modulo_grafo, "ejecutar", colgado)
    aceptado = cliente.post("/chat", json={"texto": "hola"}, headers=CABECERAS).json()
    datos = esperar_fin(cliente, aceptado["id_ejecucion"], segundos=3)
    assert datos["estado"] == "error" and datos["resultado"] is None
    assert "tiempo máximo de 0.3 s" in datos["detail"]
    assert filas[0]["id_ejecucion"] == aceptado["id_ejecucion"] and filas[0]["estado_final"] == "error"

    sigue.set()  # el turno termina tarde: su resultado no reemplaza al error
    time.sleep(0.5)
    tarde = cliente.get(aceptado["consultar"], headers=CABECERAS).json()
    assert tarde["estado"] == "error" and tarde["resultado"] is None
    assert all(f["estado_final"] == "error" for f in filas if f["id_ejecucion"] == aceptado["id_ejecucion"])


def test_ejecutar_con_limite_vencido_entrega_error(ruta_fija, filas):
    ruta_fija("fuera_de_alcance")
    salida = modulo_grafo.ejecutar("t-limite", "hola", grafo=modulo_grafo.construir_grafo(),
                                   id_ejecucion="id-fijo", limite=time.monotonic() - 1)
    assert salida["id_ejecucion"] == "id-fijo" and salida["estado_final"] == "error"
    assert "tiempo máximo" in salida["respuesta"] and filas[0]["estado_final"] == "error"


def test_esperar_true_es_sincrono_como_antes(cliente, ruta_fija, filas):
    ruta_fija("fuera_de_alcance")
    respuesta = cliente.post("/chat?esperar=true", json={"texto": "hola"}, headers=CABECERAS)
    assert respuesta.status_code == 200
    assert respuesta.json()["ruta"] == "fuera_de_alcance" and respuesta.json()["estado_final"] == "ok"


def test_registro_sin_memoria_usa_la_fila_de_postgres(cliente, monkeypatch):
    fila = {"id_ejecucion": "viejo", "fecha": "2026-11-25T00:00:00+00:00", "ruta": "revisar_gasto", "pasos": 5,
            "herramientas_usadas": [], "hubo_a2a": True, "estado_final": "fallback", "duracion_ms": 30000}
    monkeypatch.setattr("api.app.leer_ejecucion", lambda id_ejecucion: fila if id_ejecucion == "viejo" else None)
    datos = cliente.get("/registro/viejo", headers=CABECERAS).json()
    assert datos["estado"] == "fallback" and datos["resultado"] is None and datos["ruta"] == "revisar_gasto"
    assert cliente.get("/registro/no-existe", headers=CABECERAS).status_code == 404


def test_registro_sin_base_y_sin_memoria_dice_que_no_esta_disponible(cliente, monkeypatch):
    def sin_base(id_ejecucion):
        raise RuntimeError("Falta DATABASE_URL en .env")

    monkeypatch.setattr("api.app.leer_ejecucion", sin_base)
    respuesta = cliente.get("/registro/cualquiera", headers=CABECERAS)
    assert respuesta.status_code == 503 and "no está disponible" in respuesta.json()["detail"]


def test_registro_sigue_exigiendo_clave(cliente):
    assert cliente.get("/registro/cualquiera").status_code == 401


def test_tope_mal_configurado_se_avisa(monkeypatch):
    monkeypatch.setenv("TIEMPO_MAX_EJECUCION_SEG", "rapido")
    with pytest.raises(ValueError, match="TIEMPO_MAX_EJECUCION_SEG"):
        modulo_grafo.tiempo_max_ejecucion_seg()
    monkeypatch.delenv("TIEMPO_MAX_EJECUCION_SEG")
    assert modulo_grafo.tiempo_max_ejecucion_seg() == 90


def test_no_se_guardan_mas_de_max_guardadas(monkeypatch):
    monkeypatch.setattr(en_segundo_plano, "MAX_GUARDADAS", 3)
    monkeypatch.setattr(en_segundo_plano, "_EJECUCIONES", en_segundo_plano.OrderedDict())
    for n in range(5):
        en_segundo_plano._guardar(f"id-{n}", {"estado": "ok"})
    assert list(en_segundo_plano._EJECUCIONES) == ["id-2", "id-3", "id-4"]
