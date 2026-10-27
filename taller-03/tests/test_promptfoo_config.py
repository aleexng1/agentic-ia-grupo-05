"""El YAML de promptfoo es válido y sus fragmentos siguen coincidiendo con los textos fijos (sin LLM)."""
from pathlib import Path

import yaml

from src.colombia.prompts import BLOQUEOS

CONFIG = yaml.safe_load(
    (Path(__file__).resolve().parent.parent / "promptfoo" / "promptfooconfig.yaml").read_text(encoding="utf-8")
)
METRICAS = {"Precision", "Respaldo", "Completitud", "Consistencia", "Cumplimiento"}
TEXTOS_FIJOS = " ".join(BLOQUEOS.values())


def test_doce_casos_con_description_unica():
    descripciones = [t["description"] for t in CONFIG["tests"]]
    assert len(descripciones) == 12 and len(set(descripciones)) == 12
    assert all(t["vars"]["pregunta"] for t in CONFIG["tests"])


def test_metricas_con_el_nombre_exacto():
    asserts = CONFIG["defaultTest"]["assert"] + [a for t in CONFIG["tests"] for a in t["assert"]]
    usadas = {a["metric"] for a in asserts if "metric" in a}
    assert usadas <= METRICAS
    assert "Consistencia" not in usadas  # se mide con --repeat 3, no con assert


def test_los_fragmentos_de_bloqueo_existen_en_prompts():
    for caso in CONFIG["tests"]:
        for a in caso["assert"]:
            if a["type"] == "contains" and a["metric"] == "Cumplimiento":
                assert a["value"] in TEXTOS_FIJOS, a["value"]
            if a["type"] == "not-icontains":
                assert a["value"].lower() not in TEXTOS_FIJOS.lower()


def test_latencia_en_todos_los_casos_salvo_ninguno():
    umbrales = {t["description"][:2]: next(a["threshold"] for a in t["assert"] if a["type"] == "latency") for t in CONFIG["tests"]}
    contenido = {"01", "02", "03", "04", "09", "11", "12"}
    assert all(v == CONFIG["umbrales"]["contenido"] for k, v in umbrales.items() if k in contenido)
    assert all(v == CONFIG["umbrales"]["rapido"] for k, v in umbrales.items() if k not in contenido)
