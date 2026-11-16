"""Agente de postventa: pedidos, políticas y reclamos. Sin base de datos ni modelo real.

Los reclamos se guardan en memoria (sin Postgres) o en un pool FALSO que registra las consultas.
"""

import json
from datetime import date

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from main import correr
from src.memoria import Memoria, registrar_secretos
from src.router import graph as grafo_mod
from src.router import prompts, reclamos, tools
from src.router.graph import construir_grafo
from tests.fakes import LLMFalso, llamada

HOY = date(2026, 11, 16)


@pytest.fixture(autouse=True)
def reclamos_limpios(monkeypatch):
    """Cada prueba parte con el almacén de reclamos vacío y en memoria, y con una fecha de hoy fija."""
    reclamos.detener()
    monkeypatch.setattr(tools, "hoy", lambda: HOY)
    yield
    reclamos.detener()


def config(thread_id="hilo-1"):
    return {"configurable": {"thread_id": thread_id}}


# ── data/pedidos.json ────────────────────────────────────────────────────────

def test_hay_8_pedidos_y_faltan_los_que_deben_faltar():
    pedidos = json.loads(tools.PEDIDOS_JSON.read_text(encoding="utf-8"))
    assert len(pedidos) == 8
    numeros = [p["numero"] for p in pedidos]
    assert len(set(numeros)) == 8 and 4521 in numeros and 4530 in numeros and 9999 not in numeros
    assert {p["estado"] for p in pedidos} == {"preparando", "despachado", "entregado", "devuelto"}
    for p in pedidos:
        assert {"numero", "cliente", "productos", "fecha_compra", "estado", "fecha_estimada_entrega",
                "codigo_seguimiento"} <= set(p)
        assert p["productos"] and all(isinstance(x, str) for x in p["productos"])
        date.fromisoformat(p["fecha_compra"])
        date.fromisoformat(p["fecha_estimada_entrega"])


# ── estado_pedido ────────────────────────────────────────────────────────────

def test_estado_pedido_4521_existe_y_esta_despachado():
    pedido = tools.estado_pedido.invoke({"numero": "4521"})
    assert pedido["numero"] == 4521 and pedido["estado"] == "despachado"
    assert pedido["codigo_seguimiento"] and pedido["fecha_estimada_entrega"]
    assert "dias_desde_la_entrega" not in pedido  # todavía no se entrega


def test_estado_pedido_4530_esta_entregado_y_trae_los_dias_desde_la_entrega():
    pedido = tools.estado_pedido.invoke({"numero": "4530"})
    assert pedido["estado"] == "entregado"
    assert pedido["dias_desde_la_entrega"] == (HOY - date(2026, 11, 7)).days == 9


def test_estado_pedido_fuera_de_plazo():
    assert tools.estado_pedido.invoke({"numero": "4524"})["dias_desde_la_entrega"] == 53  # más de 30 días


def test_estado_pedido_9999_no_existe():
    assert tools.estado_pedido.invoke({"numero": "9999"}) == "no existe"


@pytest.mark.parametrize("texto", ["#4521", " 4521 ", "pedido 4521", "N°4521"])
def test_estado_pedido_acepta_el_numero_escrito_de_distintas_formas(texto):
    assert tools.estado_pedido.invoke({"numero": texto})["numero"] == 4521


def test_estado_pedido_sin_numero_lo_pide():
    assert "Falta el número" in tools.estado_pedido.invoke({"numero": "  "})
    assert "Falta el número" in tools.estado_pedido.invoke({"numero": "abc"})


def test_estado_pedido_no_modifica_los_datos():
    tools.estado_pedido.invoke({"numero": "4530"})
    original = json.loads(tools.PEDIDOS_JSON.read_text(encoding="utf-8"))
    assert "dias_desde_la_entrega" not in next(p for p in original if p["numero"] == 4530)


# ── politica ─────────────────────────────────────────────────────────────────

def test_politica_devoluciones_dice_30_dias():
    texto = tools.politica.invoke({"tema": "devoluciones"})
    assert texto.startswith("Devoluciones") and "30 días" in texto
    assert "Cambios" not in texto and "Garantía" not in texto  # solo la sección pedida


def test_politica_cambios_y_garantia():
    cambios = tools.politica.invoke({"tema": "cambios"})
    garantia = tools.politica.invoke({"tema": "garantia"})
    assert cambios.startswith("Cambios") and "diferencia" in cambios
    assert garantia.startswith("Garantía") and "12 meses" in garantia


def test_politica_acepta_tilde_y_mayusculas():
    assert tools.politica.func("Garantía").startswith("Garantía")  # sin pasar por la validación del esquema
    assert tools.politica.func("DEVOLUCIONES").startswith("Devoluciones")


def test_politica_tema_desconocido():
    assert "No tengo una política" in tools.politica.func("envios")


def test_politicas_md_tiene_las_tres_secciones():
    texto = tools.POLITICAS_MD.read_text(encoding="utf-8")
    assert [l for l in texto.splitlines() if l.startswith("## ")] == ["## Devoluciones", "## Cambios", "## Garantía"]


# ── crear_reclamo ────────────────────────────────────────────────────────────

def test_el_modelo_no_ve_ni_puede_fijar_el_thread_id():
    assert set(tools.crear_reclamo.args) == {"numero_pedido", "motivo", "detalle"}


def test_crear_reclamo_en_memoria_da_tickets_consecutivos_y_toma_el_hilo_de_la_config():
    r1 = tools.crear_reclamo.invoke(
        {"numero_pedido": "4521", "motivo": "producto llegó roto", "detalle": "la pantalla venía rota"},
        config("hilo-A"))
    r2 = tools.crear_reclamo.invoke(
        {"numero_pedido": "4530", "motivo": "no enciende", "detalle": "no enciende"}, config("hilo-B"))
    assert r1["ticket"] == "R-0001" and r2["ticket"] == "R-0002"
    guardados = reclamos.en_memoria()
    assert [(g["numero_pedido"], g["thread_id"]) for g in guardados] == [("4521", "hilo-A"), ("4530", "hilo-B")]
    assert guardados[0]["detalle"] == "la pantalla venía rota"


def test_crear_reclamo_de_un_pedido_inexistente_no_se_crea():
    r = tools.crear_reclamo.invoke({"numero_pedido": "9999", "motivo": "x", "detalle": "y"}, config())
    assert "no existe" in r and reclamos.en_memoria() == []


def test_crear_reclamo_sin_numero_ni_motivo_no_se_crea():
    assert "Falta el número" in tools.crear_reclamo.invoke({"numero_pedido": "", "motivo": "x", "detalle": ""}, config())
    assert "Falta el motivo" in tools.crear_reclamo.invoke({"numero_pedido": "4521", "motivo": " ", "detalle": ""}, config())
    assert reclamos.en_memoria() == []


def test_derivar_a_persona_no_exige_pedido():
    r = tools.crear_reclamo.invoke(
        {"numero_pedido": "", "motivo": "derivar a persona", "detalle": "quiere hablar con alguien"}, config("h"))
    assert r["ticket"] == "R-0001" and r["numero_pedido"] == "sin pedido"
    assert reclamos.en_memoria()[0]["numero_pedido"] == "sin pedido"


# ── Reclamos en Postgres (pool FALSO que registra las consultas) ─────────────

class FilaFalsa:
    def __init__(self, fila):
        self.fila = fila

    def fetchone(self):
        return self.fila


class ConexionFalsa:
    def __init__(self, pool):
        self.pool = pool

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.pool.cerradas += 1
        return False

    def execute(self, consulta, params=None):
        if self.pool.falla:
            raise RuntimeError('connection to server at "10.1.2.3", port 5432 failed: clave claveSecreta99')
        self.pool.consultas.append((consulta.as_string(), params))
        return FilaFalsa({"ticket": 4})


class PoolFalso:
    def __init__(self, falla=False):
        self.consultas, self.cerradas, self.falla = [], 0, False
        self.falla_al_crear = falla

    def connection(self):
        return ConexionFalsa(self)


def memoria_postgres(pool, esquema="alex_nail"):
    return Memoria(checkpointer=None, tipo="postgres", esquema=esquema, pool=pool)


def test_configurar_crea_la_tabla_en_el_esquema_propio():
    pool = PoolFalso()
    assert reclamos.configurar(memoria_postgres(pool)) == "postgres"
    (ddl, _), = pool.consultas
    assert ddl.startswith('CREATE TABLE IF NOT EXISTS "alex_nail".reclamos')
    for columna in ("ticket serial PRIMARY KEY", "numero_pedido", "motivo", "detalle", "thread_id", "creado_en"):
        assert columna in ddl
    assert "public" not in ddl and "catalogo" not in ddl
    assert pool.cerradas == 1  # la conexión del pool se devuelve


def test_crear_en_postgres_usa_parametros_y_el_esquema_propio():
    pool = PoolFalso()
    reclamos.configurar(memoria_postgres(pool))
    r = tools.crear_reclamo.invoke(
        {"numero_pedido": "4521", "motivo": "roto'; DROP TABLE reclamos; --", "detalle": "d"}, config("hilo-9"))

    assert r["ticket"] == "R-0004"  # el número lo pone la base (serial) y se muestra como R-000N
    insercion, params = pool.consultas[-1]
    assert insercion.startswith('INSERT INTO "alex_nail".reclamos')
    assert "RETURNING ticket" in insercion and insercion.count("%s") == 4
    assert params == ["4521", "roto'; DROP TABLE reclamos; --", "d", "hilo-9"]  # el texto viaja aparte del SQL
    assert "DROP" not in insercion
    assert reclamos.en_memoria() == []  # no se duplicó en memoria


def test_si_la_base_falla_no_hay_ticket_falso_y_no_se_filtran_secretos(caplog):
    registrar_secretos("postgresql://usuario:claveSecreta99@10.1.2.3:5432/base")  # como al leer DATABASE_URL
    pool = PoolFalso()
    reclamos.configurar(memoria_postgres(pool))
    pool.falla = True
    r = tools.crear_reclamo.invoke({"numero_pedido": "4521", "motivo": "roto", "detalle": "d"}, config())
    assert isinstance(r, str) and "No pude registrar" in r and "R-" not in r
    assert reclamos.en_memoria() == []
    for secreto in ("claveSecreta99", "10.1.2.3"):
        assert secreto not in r + caplog.text  # ni en la respuesta ni en el log


def test_sin_postgres_los_reclamos_van_a_memoria_y_se_avisa_en_el_log(caplog):
    caplog.set_level("WARNING")
    assert reclamos.configurar(Memoria(checkpointer=None, tipo="ram", motivo="DATABASE_URL no está definida")) == "memoria"
    assert reclamos.donde_se_guarda() == "memoria"
    assert "Reclamos solo en memoria" in caplog.text and "DATABASE_URL no está definida" in caplog.text
    tools.crear_reclamo.invoke({"numero_pedido": "4521", "motivo": "roto", "detalle": "d"}, config())
    assert "guardado solo en memoria" in caplog.text


def test_si_no_se_puede_crear_la_tabla_se_usa_memoria(caplog):
    caplog.set_level("WARNING")

    class PoolQueFalla:
        def connection(self):
            raise RuntimeError('connection to server at "10.1.2.3", port 5432 failed')

    assert reclamos.configurar(memoria_postgres(PoolQueFalla())) == "memoria"
    assert "10.1.2.3" not in caplog.text  # el servidor no llega al log


def test_formato_de_ticket():
    assert [reclamos.formato_ticket(n) for n in (1, 2, 37, 1234, 12345)] == ["R-0001", "R-0002", "R-0037", "R-1234", "R-12345"]


# ── scripts/ver_reclamos.py ──────────────────────────────────────────────────

def test_ver_reclamos_lista_con_el_formato_de_ticket(monkeypatch, capsys):
    from scripts import ver_reclamos

    visto = {}

    class Conn:
        def execute(self, consulta, params):
            visto["sql"], visto["params"] = consulta.as_string(), params

            class R:
                def fetchall(self_):
                    return [{"ticket": 2, "numero_pedido": "4521", "motivo": "roto", "detalle": "la pantalla",
                             "thread_id": "hilo-1", "creado_en": __import__("datetime").datetime(2026, 11, 16, 12, 0,
                             tzinfo=__import__("datetime").timezone.utc)}]
            return R()

    monkeypatch.setattr(ver_reclamos, "nombre_esquema", lambda: "alex_nail")
    ver_reclamos.listar(Conn(), 20)
    salida = capsys.readouterr().out
    assert "R-0002" in salida and "pedido 4521" in salida and "hilo-1" in salida and "la pantalla" in salida
    assert visto["sql"].startswith("SELECT ticket") and '"alex_nail".reclamos' in visto["sql"]
    assert visto["params"] == [20]


# ── El agente completo, con modelo falso ─────────────────────────────────────

def armar(monkeypatch, rutas, guion=(), **kw):
    llm = LLMFalso(rutas=list(rutas), guion=list(guion), **kw)
    monkeypatch.setattr(grafo_mod, "crear_llm", lambda temperatura=0: llm)
    return llm, construir_grafo()


def test_postventa_consulta_el_pedido_y_responde(monkeypatch):
    llm, g = armar(monkeypatch, ["postventa"], guion=[
        llamada("estado_pedido", {"numero": "4521"}),
        "Tu pedido 4521 va despachado y llega el 17 de noviembre. Seguimiento: EA-CL-884201."])
    saltos = correr(g, "¿dónde está mi pedido 4521?", config())
    estado = g.get_state(config()).values

    assert saltos == ["router", "agente_postventa", "estado_pedido"]  # lo que muestra --saltos
    assert estado["ruta"] == "postventa" and estado["motivo"] and "EA-CL-884201" in estado["respuesta"]
    primera = llm.recibidos[0]
    assert isinstance(primera[0], SystemMessage) and primera[0].content == prompts.PROMPT_POSTVENTA
    resultado = [m for m in llm.recibidos[1] if isinstance(m, ToolMessage)][0]
    assert "despachado" in resultado.content and "EA-CL-884201" in resultado.content


def test_el_hilo_del_reclamo_sale_del_grafo_y_el_historial_queda_limpio(monkeypatch):
    llm, g = armar(monkeypatch, ["postventa", "postventa"], guion=[
        "¿Creo un reclamo por pantalla rota del pedido 4521?",
        llamada("crear_reclamo", {"numero_pedido": "4521", "motivo": "pantalla rota", "detalle": "llegó rota"}),
        "Listo, creé tu reclamo. Tu ticket es R-0001."])
    g.invoke({"mensaje": "mi pedido 4521 llegó con la pantalla rota"}, config("conversacion-77"))
    saltos = correr(g, "sí, créalo", config("conversacion-77"))
    estado = g.get_state(config("conversacion-77")).values

    assert saltos == ["router", "agente_postventa", "crear_reclamo"]
    assert reclamos.en_memoria()[0]["thread_id"] == "conversacion-77"  # lo tomó la configuración del grafo
    assert "R-0001" in estado["respuesta"]
    resultado = [m for m in llm.recibidos[-1] if isinstance(m, ToolMessage)][0]
    assert "R-0001" in resultado.content  # el modelo recibe el ticket de la herramienta
    assert [type(m) for m in estado["messages"]] == [HumanMessage, AIMessage, HumanMessage, AIMessage]  # sin ToolMessage
    # En el segundo turno el agente vio la pregunta de confirmación y el "sí" del cliente.
    segundo = llm.recibidos[1]
    assert [m.content for m in segundo[1:]] == [
        "mi pedido 4521 llegó con la pantalla rota", "¿Creo un reclamo por pantalla rota del pedido 4521?", "sí, créalo"]


def test_si_el_agente_termina_sin_texto_hay_respuesta_de_respaldo(monkeypatch):
    _, g = armar(monkeypatch, ["postventa"], guion=["  "])
    estado = g.invoke({"mensaje": "hola, tengo un problema"}, config())
    assert estado["respuesta"] == prompts.RESPUESTA_POSTVENTA_VACIA


def test_las_tres_herramientas_de_postventa_estan_registradas():
    assert [t.name for t in tools.TOOLS_POSTVENTA] == ["estado_pedido", "politica", "crear_reclamo"]


def test_el_prompt_de_postventa_trae_las_reglas():
    p = prompts.PROMPT_POSTVENTA.lower()
    for regla in ("necesitas su número", "siempre de una herramienta", "no sabes qué día es hoy",
                  "reconoce el problema en una línea", "confirma el motivo", "solo lo creas cuando el cliente confirma",
                  "número de ticket", "derivar a persona", "alguien del equipo le va a escribir", "máximo 4 líneas"):
        assert regla in p, regla
    for herramienta in ("estado_pedido", "politica", "crear_reclamo"):
        assert herramienta in prompts.PROMPT_POSTVENTA
