"""Ensayo de evidencias/seguridad/capturar_bloqueo.py con una base falsa en memoria.

No es la evidencia (esa se genera contra un Postgres real): solo comprueba que el script sigue
funcionando y que sus controles detectan el bloqueo. Sin red, Gemini ni Postgres.
"""

import runpy
import sys

from src.comun.config import CARPETA_PROYECTO

SCRIPT = CARPETA_PROYECTO / "evidencias" / "seguridad" / "capturar_bloqueo.py"


def _correr(monkeypatch, tmp_path, argumentos=()):
    from src.comun import registro
    from src.principal import grafo as modulo_grafo
    from src.principal import registro_veredictos, router
    from src.principal.flujos import revisar_gasto

    filas = {}
    veredictos = [{"id_gasto": "G-0001", "decision": "aprobar", "registrado_en": "2026-11-24T10:00:00"}]
    monkeypatch.setenv("DATABASE_URL", "postgresql://ensayo:ensayo@localhost:1/ensayo")
    monkeypatch.setattr(registro, "guardar_ejecucion", lambda fila: filas.__setitem__(fila["id_ejecucion"], dict(fila)))
    monkeypatch.setattr(registro, "leer_ejecucion", lambda id_ejecucion: filas.get(id_ejecucion))
    monkeypatch.setattr(registro_veredictos, "leer_registro", lambda: [dict(v) for v in veredictos])
    # El script reemplaza estas funciones en los módulos: monkeypatch las restaura al terminar.
    for modulo, nombre in [(revisar_gasto, "obtener_llm"), (revisar_gasto, "_obtener_respaldo"),
                           (revisar_gasto, "registrar_veredicto"), (router, "clasificar"),
                           (modulo_grafo, "_AGENTE_REACT")]:
        monkeypatch.setattr(modulo, nombre, getattr(modulo, nombre))
    salida = tmp_path / "bloqueo.md"
    monkeypatch.setattr(sys, "argv", ["capturar_bloqueo.py", "--salida", str(salida), *argumentos])
    try:
        runpy.run_path(str(SCRIPT), run_name="__main__")
    except SystemExit as fin:
        return fin.code, salida, filas
    raise AssertionError("el script debe terminar con SystemExit")


def test_el_script_de_captura_genera_la_evidencia_y_cumple(monkeypatch, tmp_path):
    codigo, salida, filas = _correr(monkeypatch, tmp_path)

    assert codigo == 0
    texto = salida.read_text(encoding="utf-8")
    assert "**Cumple**" in texto
    assert "acción bloqueada · registrar_veredicto" in texto
    assert '"estado_final": "bloqueado"' in texto
    assert "**0**" in texto
    assert list(filas.values())[0]["estado_final"] == "bloqueado"


def test_sin_database_url_avisa_y_no_escribe(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("DATABASE_URL", " ")
    salida = tmp_path / "bloqueo.md"
    monkeypatch.setattr(sys, "argv", ["capturar_bloqueo.py", "--salida", str(salida)])
    try:
        runpy.run_path(str(SCRIPT), run_name="__main__")
    except SystemExit as fin:
        assert fin.code == 1
    assert "Falta DATABASE_URL" in capsys.readouterr().out
    assert not salida.exists()
