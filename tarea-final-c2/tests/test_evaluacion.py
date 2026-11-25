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


# ---------------------------------------------------------------------------
# Corrida larga: avance parcial, retomar y corte por cuota (sin Gemini)
# ---------------------------------------------------------------------------

IDS_CORTOS = ["GS-32", "X-01", "X-02", "X-03", "X-04"]  # en el orden del set; GS-32 tiene 2 turnos


class AgenteFalso:
    """Responde la ruta esperada; desde `sin_cuota_en` (n.º de llamada) responde 429 hasta `vuelve_en`."""

    def __init__(self, golden, sin_cuota_en=None, vuelve_en=None):
        self.esperado = {t["mensaje"]: t["esperado"] for c in golden["casos"] for t in c["turnos"]}
        self.sin_cuota_en, self.vuelve_en = sin_cuota_en, vuelve_en
        self.llamadas, self.mensajes, self.hilos = 0, [], []

    def __call__(self, turno, thread_id):
        self.llamadas += 1
        self.mensajes.append(turno["mensaje"])
        self.hilos.append(thread_id)
        cortado = self.sin_cuota_en is not None and self.llamadas >= self.sin_cuota_en
        if cortado and (self.vuelve_en is None or self.llamadas < self.vuelve_en):
            raise RuntimeError("429 RESOURCE_EXHAUSTED: You exceeded your current quota")
        esperado = self.esperado[turno["mensaje"]]
        return {"ruta": esperado["ruta"], "estado_final": "ok", "id_ejecucion": f"e-{self.llamadas}",
                "veredicto": {"decision": esperado["decision"]} if esperado.get("decision") else None}


@pytest.mark.parametrize(("texto", "es_cuota"), [
    ("429 RESOURCE_EXHAUSTED", True),
    ("Gemini no tiene cuota disponible (límite de uso o créditos agotados).", True),
    ("GoogleRateLimitError: rate limit", True),
    ("503 UNAVAILABLE", False),
    ("Revisa el folio 004290 por $1.429", False),  # un 429 dentro de un monto o folio no es cuota
])
def test_es_error_de_cuota(texto, es_cuota):
    assert evaluar.es_error_de_cuota(texto) is es_cuota


def test_corte_por_cuota_reintenta_dos_veces_guarda_avance_y_no_cuenta_el_caso(golden, tmp_path):
    casos = evaluar.filtrar(golden["casos"], ids=IDS_CORTOS)
    agente = AgenteFalso(golden, sin_cuota_en=4)  # GS-32 (llamadas 1 y 2), X-01 (3), X-02 sin cuota
    esperas, guardados = [], []
    ruta = tmp_path / "avance.json"

    def al_guardar(avance):
        evaluar.guardar_avance(avance, ruta)
        guardados.append(len(avance["casos"]))

    with pytest.raises(evaluar.EvaluacionInterrumpida) as corte:
        evaluar.correr(golden, casos, agente, "simulado", pausa=0, al_guardar=al_guardar,
                       espera_cuota=10, dormir=esperas.append)
    assert esperas == [10, 20]  # 2 reintentos con espera creciente, y se detiene
    assert (corte.value.caso_id, corte.value.posicion) == ("X-02", 3)
    avance = evaluar.cargar_avance(ruta)
    assert [r["id"] for r in avance["casos"]] == ["GS-32", "X-01"]  # X-02 no cuenta como fallo ni error
    assert avance["corridas"][0]["corte"]["caso"] == "X-02"
    assert guardados[:2] == [1, 2]  # el avance se guarda después de cada caso


def test_cuota_en_el_segundo_turno_repite_el_caso_entero_en_hilo_nuevo(golden):
    casos = evaluar.filtrar(golden["casos"], ids=["GS-32"])
    agente = AgenteFalso(golden, sin_cuota_en=2)  # turno 1 bien, turno 2 sin cuota
    with pytest.raises(evaluar.EvaluacionInterrumpida) as corte:
        evaluar.correr(golden, casos, agente, "simulado", dormir=lambda s: None)
    assert corte.value.avance["casos"] == []  # no queda un caso a medias
    assert len(set(agente.hilos)) == 3  # intento original + 2 reintentos, cada uno desde el turno 1
    assert agente.mensajes[0] == agente.mensajes[2] == casos[0]["turnos"][0]["mensaje"]


def test_retomar_sigue_sin_repetir_y_el_informe_dice_las_corridas(golden, tmp_path, monkeypatch):
    casos = evaluar.filtrar(golden["casos"], ids=IDS_CORTOS)
    ruta = tmp_path / "avance.json"
    monkeypatch.setenv("MODELO_PRINCIPAL", "modelo-a")
    monkeypatch.setenv("MODELO_RESPALDO", "modelo-r")
    with pytest.raises(evaluar.EvaluacionInterrumpida):
        evaluar.correr(golden, casos, AgenteFalso(golden, sin_cuota_en=4), "simulado",
                       al_guardar=lambda a: evaluar.guardar_avance(a, ruta), dormir=lambda s: None)

    monkeypatch.setenv("MODELO_PRINCIPAL", "modelo-b")
    agente = AgenteFalso(golden)
    datos = evaluar.correr(golden, casos, agente, "simulado", avance=evaluar.cargar_avance(ruta),
                           al_guardar=lambda a: evaluar.guardar_avance(a, ruta), dormir=lambda s: None)
    primeros = {t["mensaje"] for c in casos[:2] for t in c["turnos"]}
    assert not primeros & set(agente.mensajes)  # X-01 y X-02 no se repiten
    assert [c["id"] for c in datos["casos"]] == IDS_CORTOS
    assert datos["resumen"]["casos"]["acierto"] == 5 and datos["resumen"]["casos"]["error"] == 0
    assert len(datos["corridas"]) == 2 and datos["corridas"][0]["corte"]["caso"] == "X-02"
    assert datos["modelos"] == {"principal": ["modelo-a", "modelo-b"], "respaldo": ["modelo-r"]}
    md = evaluar.informe_markdown(datos)
    assert "| Corridas | 2 (retomada 1 vez/veces; 1 corte(s) por cuota) |" in md
    assert "modelo-a, modelo-b (respaldo: modelo-r)" in md and "sin cuota en X-02 (3 de 5)" in md


def test_una_sola_corrida_lo_dice_en_el_informe(golden):
    casos = evaluar.filtrar(golden["casos"], ids=["X-01"])
    datos = evaluar.correr(golden, casos, AgenteFalso(golden), "simulado")
    assert "| Corridas | 1 (una sola corrida) |" in evaluar.informe_markdown(datos)


@pytest.fixture
def main_simulado(monkeypatch, golden):
    """main() con un agente falso en vez del grafo (sin Gemini)."""
    monkeypatch.setenv("GOOGLE_API_KEY", "clave-falsa-de-prueba")
    agente = {"actual": AgenteFalso(golden)}
    monkeypatch.setattr(evaluar, "enviar_en_proceso", lambda turno, hilo: agente["actual"](turno, hilo))
    monkeypatch.setattr(evaluar.time, "sleep", lambda s: None)
    return agente


def test_main_corta_por_cuota_y_retoma(main_simulado, golden, tmp_path, capsys):
    base = ["--casos", *IDS_CORTOS, "--salida", str(tmp_path), "--espera-cuota", "0"]
    main_simulado["actual"] = AgenteFalso(golden, sin_cuota_en=4)
    assert evaluar.main(base) == 3
    salida = capsys.readouterr().out
    assert "caso X-02 (3 de 5)" in salida and "--retomar --casos GS-32 X-01 X-02 X-03 X-04" in salida
    assert (tmp_path / evaluar.NOMBRE_AVANCE).is_file() and not list(tmp_path.glob("informe-*"))

    assert evaluar.main(base) == 2  # sin --retomar no pisa el avance
    assert "--retomar" in capsys.readouterr().out

    main_simulado["actual"] = AgenteFalso(golden)
    assert evaluar.main([*base, "--retomar"]) == 0
    assert not (tmp_path / evaluar.NOMBRE_AVANCE).exists()  # el avance quedó dentro del informe
    informe = json.loads(next(tmp_path.glob("informe-*.json")).read_text(encoding="utf-8"))
    assert informe["casos_corridos"] == 5 and len(informe["corridas"]) == 2


def test_main_desde_omite_los_anteriores_sin_avance(main_simulado, golden, tmp_path):
    assert evaluar.main(["--casos", *IDS_CORTOS, "--salida", str(tmp_path), "--desde", "X-02"]) == 0
    informe = json.loads(next(tmp_path.glob("informe-*.json")).read_text(encoding="utf-8"))
    assert informe["omitidos"] == ["GS-32", "X-01"] and informe["casos_corridos"] == 3
    assert "Casos omitidos" in next(tmp_path.glob("informe-*.md")).read_text(encoding="utf-8")


def test_main_retomar_sin_avance_o_con_otra_seleccion_avisa(main_simulado, golden, tmp_path):
    assert evaluar.main(["--casos", "X-01", "--salida", str(tmp_path), "--retomar"]) == 2
    main_simulado["actual"] = AgenteFalso(golden, sin_cuota_en=1)
    assert evaluar.main(["--casos", "X-01", "X-02", "--salida", str(tmp_path), "--espera-cuota", "0"]) == 3
    assert evaluar.main(["--casos", "X-03", "--salida", str(tmp_path), "--retomar"]) == 2
    assert evaluar.posicion_desde("2", evaluar.filtrar(golden["casos"], ids=IDS_CORTOS)) == 1
