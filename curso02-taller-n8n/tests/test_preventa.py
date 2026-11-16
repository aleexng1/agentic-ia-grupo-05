"""Agente de preventa (ReAct) y router con continuidad, con modelo y catálogo FALSOS.

No llama al modelo real ni a la base: valida la mecánica (ciclo de herramientas, historial, saltos,
fallo del catálogo, contexto del router). Que el modelo real use bien el prompt se prueba aparte.
"""

from decimal import Decimal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from main import correr
from src.router import catalogo, prompts, tools
from src.router import graph as grafo_mod
from src.router.graph import construir_grafo
from tests.fakes import LLMFalso, llamada

TV = {"sku_id": "tv1", "nombre": "Smart TV Samsung 55", "marca": "Samsung", "precio_internet": 299990,
      "descuento_pct": 20, "rating": Decimal("4.7")}
DETALLE = {**TV, "categoria": "Televisores", "link": "https://tienda.example/p/tv1", "imagen": "https://img/1"}


def armar(monkeypatch, rutas, guion=(), **kw):
    llm = LLMFalso(rutas=list(rutas), guion=list(guion), **kw)
    monkeypatch.setattr(grafo_mod, "crear_llm", lambda temperatura=0: llm)
    return llm, construir_grafo()


def hilo(nombre="t1"):
    return {"configurable": {"thread_id": nombre}}


def catalogo_falso(monkeypatch):
    def consultar(sql, params=()):
        return [DETALLE] if "WHERE sku_id" in sql else [TV]

    monkeypatch.setattr(tools.catalogo, "consultar", consultar)


# ── El ciclo del agente ──────────────────────────────────────────────────────

def test_preventa_usa_herramientas_y_responde(monkeypatch):
    catalogo_falso(monkeypatch)
    llm, g = armar(monkeypatch, ["preventa"], guion=[
        llamada("buscar_productos", {"consulta": "tv", "categoria": "Televisores", "precio_max": 400000}, "c1"),
        llamada("ver_producto", {"sku_id": "tv1"}, "c2"),
        "Te recomiendo el Smart TV Samsung 55 a $299.990: https://tienda.example/p/tv1",
    ])
    saltos = correr(g, "busco una tv de 55 hasta 400 mil", hilo())
    estado = g.get_state(hilo()).values

    assert saltos == ["router", "agente_preventa", "buscar_productos", "ver_producto"]  # lo que muestra --saltos
    assert estado["ruta"] == "preventa" and estado["motivo"]
    assert estado["respuesta"] == "Te recomiendo el Smart TV Samsung 55 a $299.990: https://tienda.example/p/tv1"

    # El modelo recibió el prompt de preventa y vio los resultados de las herramientas.
    primera, segunda, tercera = llm.recibidos
    assert isinstance(primera[0], SystemMessage) and primera[0].content == prompts.PROMPT_PREVENTA
    assert [type(m) for m in primera[1:]] == [HumanMessage]
    assert "Smart TV Samsung 55" in [m for m in segunda if isinstance(m, ToolMessage)][0].content
    assert "https://tienda.example/p/tv1" in [m for m in tercera if isinstance(m, ToolMessage)][-1].content


def test_el_historial_guarda_solo_el_mensaje_y_la_respuesta(monkeypatch):
    catalogo_falso(monkeypatch)
    _, g = armar(monkeypatch, ["preventa"], guion=[
        llamada("buscar_productos", {"consulta": "tv"}), "Mira el Samsung."])
    g.invoke({"mensaje": "una tv"}, hilo())

    mensajes = g.get_state(hilo()).values["messages"]
    assert [type(m) for m in mensajes] == [HumanMessage, AIMessage]  # sin llamadas a herramientas ni ToolMessage
    assert [m.content for m in mensajes] == ["una tv", "Mira el Samsung."]
    assert not any(getattr(m, "tool_calls", None) for m in mensajes)


def test_el_agente_recibe_el_historial_no_solo_el_ultimo_mensaje(monkeypatch):
    catalogo_falso(monkeypatch)
    llm, g = armar(monkeypatch, ["preventa", "preventa"], guion=["¿Qué presupuesto tienes?", "Listo."])
    g.invoke({"mensaje": "quiero un celular"}, hilo())
    g.invoke({"mensaje": "hasta 300 mil"}, hilo())

    segunda_vuelta = llm.recibidos[1]  # lo que vio el agente en el segundo turno
    assert [type(m) for m in segunda_vuelta] == [SystemMessage, HumanMessage, AIMessage, HumanMessage]
    assert [m.content for m in segunda_vuelta[1:]] == [
        "quiero un celular", "¿Qué presupuesto tienes?", "hasta 300 mil"]


def test_historial_sin_huecos_en_varios_turnos_con_herramientas(monkeypatch):
    catalogo_falso(monkeypatch)
    _, g = armar(monkeypatch, ["preventa", "preventa"], guion=[
        llamada("mejores_ofertas", {}), "Primera.", llamada("buscar_productos", {"consulta": "tv"}), "Segunda."])
    g.invoke({"mensaje": "uno"}, hilo())
    estado = g.invoke({"mensaje": "dos"}, hilo())
    assert [(type(m), m.content) for m in estado["messages"]] == [
        (HumanMessage, "uno"), (AIMessage, "Primera."), (HumanMessage, "dos"), (AIMessage, "Segunda.")]
    assert estado["respuesta"] == "Segunda."


# ── Si el catálogo falla o el agente no dice nada ────────────────────────────

def test_si_el_catalogo_no_responde_el_agente_lo_sabe_y_la_api_no_se_cae(monkeypatch):
    def cae(sql, params=()):
        raise catalogo.CatalogoNoDisponible("remaining connection slots are reserved")

    monkeypatch.setattr(tools.catalogo, "consultar", cae)
    llm, g = armar(monkeypatch, ["preventa"], guion=[
        llamada("buscar_productos", {"consulta": "tv"}),
        "Ahora mismo no puedo consultar el catálogo; prueba de nuevo en unos minutos."])
    estado = g.invoke({"mensaje": "una tv"}, hilo())  # no lanza

    resultado_herramienta = [m for m in llm.recibidos[1] if isinstance(m, ToolMessage)][0]
    assert resultado_herramienta.content == "catálogo no disponible"  # lo que le llega al modelo
    assert "no puedo consultar el catálogo" in estado["respuesta"]


def test_si_el_agente_termina_sin_texto_hay_una_respuesta_de_respaldo(monkeypatch):
    _, g = armar(monkeypatch, ["preventa"], guion=["   "])
    estado = g.invoke({"mensaje": "hola, quiero comprar"}, hilo())
    assert estado["respuesta"] == prompts.RESPUESTA_PREVENTA_VACIA
    assert [m.content for m in estado["messages"]] == ["hola, quiero comprar", prompts.RESPUESTA_PREVENTA_VACIA]


def test_el_prompt_de_preventa_trae_las_reglas():
    p = prompts.PROMPT_PREVENTA.lower()
    for regla in ("siempre de una herramienta", "stock", "una sola pregunta", "link", "máximo 4 líneas",
                  "punto de miles", "postventa", "catálogo no disponible", "ver_producto"):
        assert regla in p, regla
    for herramienta in ("buscar_productos", "ver_producto", "mejores_ofertas"):
        assert herramienta in prompts.PROMPT_PREVENTA


# ── El router mira el historial reciente y la ruta anterior ──────────────────

def test_el_router_ve_la_ruta_anterior_y_los_ultimos_4_mensajes(monkeypatch):
    catalogo_falso(monkeypatch)
    llm, g = armar(monkeypatch, ["preventa"] * 4 + ["preventa"], respuesta="ok")
    for texto in ("uno", "dos", "tres", "cuatro"):
        g.invoke({"mensaje": texto}, hilo())
    g.invoke({"mensaje": "Samsung"}, hilo())

    primero, *_, ultimo = llm.clasificaciones
    assert "ninguna" in primero[0].content  # primer mensaje: sin ruta anterior
    assert len(primero) == 2  # sistema + el mensaje (no hay historial todavía)

    sistema, *historial, actual = ultimo
    assert isinstance(sistema, SystemMessage)
    assert "Ruta anterior de esta conversación: preventa" in sistema.content
    assert sistema.content.startswith(prompts.PROMPT_ROUTER)  # conserva sus reglas
    assert len(historial) == 4  # solo los últimos 4 mensajes del hilo
    assert [m.content for m in historial] == ["tres", "ok", "cuatro", "ok"]
    assert actual.content == "Samsung"


def test_el_router_sigue_en_la_ruta_de_una_respuesta_corta(monkeypatch):
    """La regla de continuidad está en el prompt que recibe el router (el modelo real la aplica)."""
    p = prompts.PROMPT_ROUTER
    assert "ruta anterior" in p.lower() and '"Samsung"' in p and '"hasta 300 mil"' in p
    assert "si la ruta anterior fue generica" in p.lower()
    # Las reglas anteriores se conservan.
    assert "YA compró, es postventa" in p and "intención de compra de CUALQUIER producto" in p


def test_la_ruta_anterior_no_viene_de_las_otras_rutas_al_cambiar(monkeypatch):
    _, g = armar(monkeypatch, ["generica", "postventa"])
    g.invoke({"mensaje": "hola"}, hilo())
    g.invoke({"mensaje": "mi pedido llegó roto"}, hilo())
    llm_clasif = g.get_state(hilo()).values
    assert llm_clasif["ruta"] == "postventa"
