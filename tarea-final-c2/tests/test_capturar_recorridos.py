"""Pruebas del script de evidencia «dos recorridos» (evidencias/dos-recorridos/capturar.py).

Solo prueban cómo se atribuye la traza del ReAct a una ejecución y cómo se arma el paso a paso.
La evidencia en sí se captura contra los servicios reales. Sin Gemini, sin red y sin Postgres.
"""

import importlib.util
import json
from pathlib import Path

import pytest

RUTA = Path(__file__).resolve().parents[1] / "evidencias" / "dos-recorridos" / "capturar.py"
ID = "785ff949-e96b-43dc-bdf3-3088cda484bb"
OTRO = "11111111-2222-3333-4444-555555555555"


@pytest.fixture(scope="module")
def captura():
    especificacion = importlib.util.spec_from_file_location("capturar_recorridos_prueba", RUTA)
    modulo = importlib.util.module_from_spec(especificacion)
    especificacion.loader.exec_module(modulo)
    return modulo


def _bloque(evento, datos):
    return [f"── [{evento}] ──", *json.dumps(datos, ensure_ascii=False, indent=2).splitlines()]


PASO_1 = {"paso": 1, "texto": "", "pide_herramientas": [{"name": "buscar_politica", "args": {"consulta": "peaje"}, "id": "a"}]}
PASO_2 = {"paso": 2, "texto": "", "pide_herramientas": [
    {"name": "emitir_veredicto", "args": {"decision": "aprobar", "politica": "P02", "categoria": "Peaje", "cuenta": "CTA-6100"}, "id": "b"}]}


def _log(*medio):
    return [
        "INFO:     ruido de antes",
        f"2026-11-26 18:33:07 INFO    [tarea_final] chat · {ID} · aceptado en segundo plano (tope 90 s)",
        *_bloque("llm", PASO_1),
        *_bloque("observacion", {"herramienta": "buscar_politica", "resultado": "[P02] Peaje: hasta $10.000"}),
        *medio,
        *_bloque("llm", PASO_2),
        *_bloque("juez", {"valido": True}),
        f"2026-11-26 18:33:33 INFO    [tarea_final] ejecución {ID} · ruta=revisar_gasto · estado=ok · 25546 ms",
        *_bloque("llm", {"paso": 1, "pide_herramientas": []}),  # de una ejecución posterior: queda fuera
    ]


def test_la_ventana_va_del_inicio_al_fin_de_la_ejecucion(captura):
    ventana, aviso = captura.ventana_de_ejecucion(_log(), ID)
    assert aviso is None
    trazas = captura.extraer_trazas(ventana)
    assert [e for e, _ in trazas] == ["llm", "observacion", "llm", "juez"]
    resultado = {"pasos": 2, "herramientas_usadas": ["buscar_politica", "emitir_veredicto"]}
    assert captura.comprobar_traza(trazas, resultado) == []


def test_si_empieza_otra_ejecucion_en_medio_no_se_atribuye(captura):
    intrusa = f"2026-11-26 18:33:10 INFO    [tarea_final] chat · {OTRO} · aceptado en segundo plano (tope 90 s)"
    ventana, aviso = captura.ventana_de_ejecucion(_log(intrusa), ID)
    assert ventana == [] and "otra ejecución" in aviso


def test_sin_fin_en_el_log_no_hay_ventana(captura):
    ventana, aviso = captura.ventana_de_ejecucion(_log()[:5], ID)
    assert ventana == [] and "inicio y el fin" in aviso


def test_traza_que_no_calza_con_el_registro(captura):
    trazas = captura.extraer_trazas(captura.ventana_de_ejecucion(_log(), ID)[0])
    diferencias = captura.comprobar_traza(trazas, {"pasos": 4, "herramientas_usadas": ["buscar_politica"]})
    assert len(diferencias) == 2


def test_paso_a_paso_muestra_pedido_resultado_decision_y_parada(captura):
    trazas = captura.extraer_trazas(captura.ventana_de_ejecucion(_log(), ID)[0])
    texto = "\n".join(captura.paso_a_paso(trazas) + captura.condicion_de_parada(trazas))
    assert "### Paso 1" in texto and "**Pide** `buscar_politica`" in texto and '"consulta": "peaje"' in texto
    assert "**Devuelve** `buscar_politica`: [P02] Peaje" in texto
    assert "**Decide después:** paso 2, pide `emitir_veredicto`" in texto
    assert "parada por veredicto válido" in texto and "**APROBAR** / P02 / Peaje / CTA-6100" in texto
    assert "**Devuelve** `emitir_veredicto`: el veredicto estructurado" in texto
    assert "**Juez** `[juez]`" in texto
    assert "test_se_detiene_por_max_pasos_con_estado_error" in texto and "línea None" not in texto


def test_herramientas_con_repeticion_y_parada_por_max_pasos(captura):
    repetida = {"paso": 1, "pide_herramientas": [{"name": "buscar_politica", "args": {}}, {"name": "buscar_politica", "args": {}}]}
    sin_ejecutar = {"paso": 2, "pide_herramientas": [{"name": "validar_gasto", "args": {}}]}
    trazas = [("llm", repetida), ("llm", sin_ejecutar), ("parada", {"motivo": "MAX_PASOS", "pasos": 2})]
    assert captura.herramientas_de_la_traza(trazas) == ["buscar_politica", "buscar_politica"]
