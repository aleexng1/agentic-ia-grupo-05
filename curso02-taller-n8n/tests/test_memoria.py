"""Pruebas de la memoria sin tocar la base real (ni gastar cuota del modelo)."""

import logging

import pytest
from fastapi.testclient import TestClient
from langgraph.checkpoint.memory import MemorySaver

import api.app as api_app
from src.memoria import (
    Memoria,
    _Redactor,
    abrir_memoria,
    nombre_esquema,
    ocultar,
    registrar_secretos,
)

URL_FALSA = "postgresql://usuario:claveSecreta99@servidor-privado.example.com:5432/base"


# ── Elección de la memoria ───────────────────────────────────────────────────

def test_sin_database_url_usa_ram():
    m = abrir_memoria()
    assert m.tipo == "ram"
    assert isinstance(m.checkpointer, MemorySaver)
    assert "DATABASE_URL" in m.motivo
    m.cerrar()  # no falla aunque no haya pool


def test_base_inalcanzable_cae_a_ram_sin_exponer_secretos(monkeypatch):
    # Puerto 1 de localhost: rechaza la conexión al instante, sin tocar la base real.
    monkeypatch.setenv("DATABASE_URL", "postgresql://usuario:claveSecreta99@127.0.0.1:1/base")
    m = abrir_memoria()
    assert m.tipo == "ram"
    assert isinstance(m.checkpointer, MemorySaver)
    assert m.motivo
    for secreto in ("claveSecreta99", "127.0.0.1", "postgresql://"):
        assert secreto not in m.motivo


def test_esquema_ajeno_cae_a_ram_sin_conectar(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", URL_FALSA)
    monkeypatch.setenv("DB_SCHEMA", "public")
    m = abrir_memoria()
    assert m.tipo == "ram"
    assert "no está permitido" in m.motivo


# ── Esquema propio ───────────────────────────────────────────────────────────

def test_esquema_por_defecto_es_alex_nail():
    assert nombre_esquema() == "alex_nail"


def test_esquema_configurable(monkeypatch):
    monkeypatch.setenv("DB_SCHEMA", "alumno_mio")
    assert nombre_esquema() == "alumno_mio"


@pytest.mark.parametrize(
    "esquema",
    ["public", "catalogo", "alumno01", "alumno12", "pg_catalog", "information_schema",
     "Mayusculas", "con espacio", "x;drop schema public", "1empieza_con_numero", ""],
)
def test_esquemas_ajenos_o_invalidos_se_rechazan(monkeypatch, esquema):
    monkeypatch.setenv("DB_SCHEMA", esquema)
    if esquema == "":
        assert nombre_esquema() == "alex_nail"  # vacío = valor por defecto
    else:
        with pytest.raises(ValueError):
            nombre_esquema()


# ── Ocultar secretos ─────────────────────────────────────────────────────────

def test_ocultar_tapa_url_clave_y_servidor():
    registrar_secretos(URL_FALSA)
    texto = (f'connection to server at "servidor-privado.example.com", port 5432 failed: '
             f"password claveSecreta99 ({URL_FALSA})")
    limpio = ocultar(texto)
    for secreto in ("claveSecreta99", "servidor-privado", "postgresql://"):
        assert secreto not in limpio


def test_filtro_de_logs_tapa_secretos_en_mensaje_y_traceback():
    registrar_secretos(URL_FALSA)
    try:
        raise RuntimeError('connection to server at "servidor-privado.example.com", port 5432 failed: clave claveSecreta99')
    except RuntimeError:
        import sys
        registro = logging.LogRecord("psycopg.pool", logging.WARNING, __file__, 1,
                                     "error connecting: %s", ("servidor-privado.example.com claveSecreta99",), sys.exc_info())
    _Redactor().filter(registro)
    salida = logging.Formatter().format(registro)
    for secreto in ("servidor-privado", "claveSecreta99"):
        assert secreto not in salida


# ── /health informa la memoria ───────────────────────────────────────────────

def test_health_informa_ram_sin_database_url():
    with TestClient(api_app.app) as c:
        r = c.get("/health")  # sin clave, como siempre
    assert r.status_code == 200
    assert r.json()["memoria"] == "ram"


def test_health_informa_postgres_cuando_la_memoria_es_postgres(monkeypatch):
    monkeypatch.setattr(api_app, "abrir_memoria",
                        lambda: Memoria(MemorySaver(), "postgres", esquema="alex_nail"))
    with TestClient(api_app.app) as c:
        r = c.get("/health")
    assert r.status_code == 200
    assert r.json()["memoria"] == "postgres"


def test_api_arranca_aunque_la_memoria_falle(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://usuario:claveSecreta99@127.0.0.1:1/base")
    with TestClient(api_app.app) as c:
        r = c.get("/health")
    assert r.status_code == 200
    assert r.json()["memoria"] == "ram"
