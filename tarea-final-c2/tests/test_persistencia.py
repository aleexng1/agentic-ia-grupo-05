"""Pruebas de persistencia en Postgres (tabla ejecuciones y registro de veredictos) y de respaldo.

Dueño: Sebastián. Estas pruebas borran y recrean tablas, así que usan TEST_DATABASE_URL
(una base de pruebas, nunca la de Heroku). Si no está definida, se omiten.
Ejemplo local con Docker:  TEST_DATABASE_URL=postgresql://postgres:devpass@localhost:5433/tarea_final_c2
"""

import os
from datetime import datetime, timezone

import pytest

from src.comun import registro
from src.comun.modelos import obtener_llm_con_respaldo
from src.principal import registro_veredictos

URL_PRUEBA = os.getenv("TEST_DATABASE_URL", "").strip()

requiere_postgres = pytest.mark.skipif(not URL_PRUEBA, reason="define TEST_DATABASE_URL para probar Postgres")


@pytest.fixture
def base_limpia(monkeypatch):
    """Apunta DATABASE_URL a la base de pruebas y vacía las tablas antes de cada prueba."""
    monkeypatch.setenv("DATABASE_URL", URL_PRUEBA)
    with registro.conectar_postgres() as conexion:
        conexion.execute("DROP TABLE IF EXISTS ejecuciones")
        conexion.execute("DROP TABLE IF EXISTS veredictos")
    registro._tabla_lista = False
    yield
    registro._tabla_lista = False


def _ejecucion(id_ejecucion: str, estado: str = "ok") -> dict:
    return {
        "id_ejecucion": id_ejecucion,
        "fecha": datetime.now(timezone.utc),
        "ruta": "revisar_gasto",
        "pasos": 3,
        "herramientas_usadas": ["buscar_politica", "validar_gasto"],
        "hubo_a2a": False,
        "estado_final": estado,
        "duracion_ms": 1200,
    }


def _gasto() -> dict:
    return {"id": "G-1", "id_fondo": "F-1", "monto": 45000}


def _veredicto(decision: str = "aprobar", motivo: str = "Cumple la política.") -> dict:
    return {
        "decision": decision,
        "motivo": motivo,
        "politica_sugerida": "Política de combustible",
        "categoria_sugerida": "Gasolina",
        "cuenta_sugerida": "5101",
    }


@requiere_postgres
def test_ejecucion_se_guarda_y_se_lee(base_limpia):
    registro.guardar_ejecucion(_ejecucion("E-1"))
    fila = registro.leer_ejecucion("E-1")
    assert fila is not None
    assert fila["ruta"] == "revisar_gasto"
    assert fila["herramientas_usadas"] == ["buscar_politica", "validar_gasto"]
    assert fila["estado_final"] == "ok"


@requiere_postgres
def test_ejecucion_inexistente_devuelve_none(base_limpia):
    assert registro.leer_ejecucion("no-existe") is None


@requiere_postgres
def test_ejecucion_repetida_no_duplica(base_limpia):
    registro.guardar_ejecucion(_ejecucion("E-2"))
    registro.guardar_ejecucion(_ejecucion("E-2", estado="error"))
    assert registro.leer_ejecucion("E-2")["estado_final"] == "ok"


def test_estado_final_invalido_se_rechaza():
    with pytest.raises(ValueError):
        registro.guardar_ejecucion(_ejecucion("E-3", estado="inventado"))


@requiere_postgres
def test_fallo_de_base_no_rompe_guardar(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://nadie:mal@127.0.0.1:1/no_existe")
    registro._tabla_lista = False
    registro.guardar_ejecucion(_ejecucion("E-4"))  # no debe lanzar excepción


@requiere_postgres
def test_veredicto_insertado_sin_cambios_y_actualizado(base_limpia):
    primero = registro_veredictos.registrar_veredicto(_gasto(), _veredicto())
    assert primero["operacion"] == "insertado"
    assert primero["antes"]["registros"] == 0
    assert primero["despues"]["registros"] == 1

    igual = registro_veredictos.registrar_veredicto(_gasto(), _veredicto())
    assert igual["operacion"] == "sin_cambios"
    assert igual["despues"]["registros"] == 1

    cambiado = registro_veredictos.registrar_veredicto(_gasto(), _veredicto("observar", "Falta la boleta."))
    assert cambiado["operacion"] == "actualizado"
    assert cambiado["despues"]["por_decision"] == {"observar": 1}


@requiere_postgres
def test_reiniciar_registro_vacia_la_tabla(base_limpia):
    registro_veredictos.registrar_veredicto(_gasto(), _veredicto())
    registro_veredictos.reiniciar_registro()
    assert registro_veredictos.leer_registro() == []


def test_respaldo_sin_modelo_devuelve_solo_el_principal(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "clave-falsa-solo-para-pruebas")
    monkeypatch.setenv("MODELO_PRINCIPAL", "gemini-3.5-flash-lite")
    monkeypatch.setenv("MODELO_RESPALDO", "")
    modelo = obtener_llm_con_respaldo()
    assert type(modelo).__name__ == "ChatGoogleGenerativeAI"


def test_respaldo_con_modelo_une_los_dos(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "clave-falsa-solo-para-pruebas")
    monkeypatch.setenv("MODELO_PRINCIPAL", "gemini-3.5-flash-lite")
    monkeypatch.setenv("MODELO_RESPALDO", "gemini-3.5-flash-lite")
    modelo = obtener_llm_con_respaldo()
    assert type(modelo).__name__ == "RunnableWithFallbacks"
