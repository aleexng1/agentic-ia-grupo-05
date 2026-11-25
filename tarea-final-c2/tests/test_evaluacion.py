"""Pruebas del golden set v1.0 y del evaluador (Alex), sin Gemini: respuestas simuladas."""

import json

import pytest

from evaluacion import evaluar
from tests.test_router import CASOS_ROUTER


@pytest.fixture(scope="module")
def golden():
    return evaluar.cargar_golden()


def test_golden_set_v1_tiene_formato_correcto(golden):
    assert golden["version"] == "1.0"
    assert evaluar.revisar_formato(golden) == []
    ids = {caso["id"] for caso in golden["casos"]}
    assert {f"GS-{n:02d}" for n in range(1, 35)} <= ids  # los 34 de c1, adaptados


def test_casos_r_son_los_mismos_de_test_router(golden):
    casos_r = [caso for caso in golden["casos"] if caso["grupo"] == "R-router"]
    assert [(c["turnos"][0]["mensaje"], bool(c["turnos"][0]["imagen"]), c["turnos"][0]["esperado"]["ruta"])
            for c in casos_r] == [(t, i, r) for t, i, r, _ in CASOS_ROUTER]


def test_todo_turno_con_gasto_va_a_revisar_gasto(golden):
    for caso in golden["casos"]:
        for turno in caso["turnos"]:
            if turno["gasto"] and caso["grupo"] != "R-router":
                assert turno["esperado"]["ruta"] == "revisar_gasto", caso["id"]


def test_formato_malo_se_detecta():
    malo = {"version": "1.0", "grupos": {"A": ""}, "casos": [
        {"id": "Z", "grupo": "A", "turnos": [{"mensaje": "x", "esperado": {"ruta": "aprobar_todo"}}]},
        {"id": "Z", "grupo": "B", "turnos": [{"mensaje": "", "esperado": {"ruta": "fuera_de_alcance", "decision": "aprobar"}}]},
    ]}
    errores = "\n".join(evaluar.revisar_formato(malo))
    for texto in ("ids repetidos", "ruta esperada no válida", "grupo desconocido", "mensaje vacío", "decisión esperada fuera"):
        assert texto in errores


@pytest.mark.parametrize(("esperado", "obtenido", "resultado"), [
    ({"ruta": "fuera_de_alcance"}, {"ruta": "fuera_de_alcance", "estado_final": "ok"}, "acierto"),
    ({"ruta": "fuera_de_alcance"}, {"ruta": "consulta_politica"}, "fallo"),
    ({"ruta": "consulta_politica"}, {"ruta": "consulta_politica", "estado_final": "error",
                                     "respuesta": "Flujo consulta_politica todavía no implementado."}, "pendiente"),
    ({"ruta": "revisar_gasto", "decision": "observar"},
     {"ruta": "revisar_gasto", "estado_final": "ok", "veredicto": {"decision": "observar"}}, "acierto"),
    ({"ruta": "revisar_gasto", "decision": "observar"},
     {"ruta": "revisar_gasto", "estado_final": "ok", "veredicto": {"decision": "aprobar"}}, "fallo"),
    ({"ruta": "revisar_gasto", "decision": "rechazar"},
     {"ruta": "revisar_gasto", "estado_final": "error", "respuesta": "Flujo revisar_gasto todavía no implementado."}, "pendiente"),
])
def test_comparar_turno(esperado, obtenido, resultado):
    assert evaluar.comparar_turno(esperado, obtenido)[0] == resultado


def test_corrida_simulada_e_informe(golden, tmp_path):
    """Un «agente» simulado: acierta la ruta salvo en R-01, y no tiene implementado consulta_politica."""
    casos = evaluar.filtrar(golden["casos"], ids=["R-01", "R-11", "GS-33", "GS-01", "X-01"])
    esperado_por_mensaje = {t["mensaje"]: t["esperado"] for c in casos for t in c["turnos"]}

    def enviar(turno, thread_id):
        esperado = esperado_por_mensaje[turno["mensaje"]]
        if turno["mensaje"].startswith("¿Cuál es el plazo máximo"):  # R-01: el router se equivoca
            return {"ruta": "fuera_de_alcance", "estado_final": "ok", "id_ejecucion": "e-1"}
        if esperado["ruta"] == "consulta_politica":
            return {"ruta": "consulta_politica", "estado_final": "error", "id_ejecucion": "e-2",
                    "respuesta": "Flujo consulta_politica todavía no implementado."}
        if esperado["ruta"] == "revisar_gasto":
            raise RuntimeError("503 UNAVAILABLE")
        return {"ruta": esperado["ruta"], "estado_final": "ok", "id_ejecucion": "e-3"}

    datos = evaluar.correr(golden, casos, enviar, "simulado")
    resumen = datos["resumen"]["casos"]
    assert (resumen["acierto"], resumen["fallo"], resumen["pendiente"], resumen["error"]) == (2, 1, 1, 1)
    assert resumen["porcentaje_aciertos"] == pytest.approx(66.7)
    ruta_md, ruta_json = evaluar.guardar_informe(datos, tmp_path)
    md = ruta_md.read_text(encoding="utf-8")
    assert "Versión del set | 1.0" in md and "**R-01** turno 1: ruta fuera_de_alcance ≠ consulta_politica" in md
    assert "Gemini no está disponible" in md or "503" in md  # el error queda a la vista, no se oculta
    assert json.loads(ruta_json.read_text(encoding="utf-8"))["resumen"]["por_grupo"]["R-router"]["fallo"] == 1


def test_sin_clave_no_escribe_informe(monkeypatch, tmp_path):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setattr("src.comun.config.load_dotenv", lambda *a, **k: None, raising=False)
    assert evaluar.main(["--salida", str(tmp_path)]) == 2
    assert list(tmp_path.iterdir()) == []
