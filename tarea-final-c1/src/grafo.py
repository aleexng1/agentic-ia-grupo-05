"""Ciclo ReAct del agente con historial de conversación (LangGraph).

Dueño: rol Núcleo. Esta es una versión mínima que ya funciona; el Núcleo la completa.

El ciclo es:
    LLM ──(pide herramienta)──> herramientas ──(observación)──> LLM ...
    LLM ──(responde sin pedir herramientas)──> FIN
    si se llega a MAX_PASOS ──> parada ──> FIN
"""

import json
import re

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from src.config import obtener_llm, registrar_traza
from src.contrato import MAX_PASOS, EstadoAgente, EstadoFondo
from src.herramientas import resolver_categoria, resolver_politica, validar_gasto
from src.memoria import anexar_revision_saldo, aplicar_veredicto
from src.rag import buscar_politica
from src.seguridad import PROMPT_SISTEMA

# Herramientas que el LLM puede pedir.
HERRAMIENTAS = [buscar_politica, validar_gasto]

_DECISION_EXPLICITA = re.compile(
    r"^\s*(?:decisi[oó]n|veredicto)\s*:\s*(aprobar|observar|rechazar)\b",
    re.IGNORECASE | re.MULTILINE,
)


def _leer_resultado_herramienta(mensaje: ToolMessage):
    """Convierte el contenido JSON de una herramienta a datos de Python."""
    contenido = mensaje.content
    if isinstance(contenido, dict):
        return contenido
    if isinstance(contenido, list):
        bloques_texto = [
            parte for parte in contenido
            if isinstance(parte, dict) and isinstance(parte.get("text"), str)
        ]
        if bloques_texto and len(bloques_texto) == len(contenido):
            contenido = "".join(parte["text"] for parte in bloques_texto)
        else:
            return contenido
    if not isinstance(contenido, str):
        return None
    try:
        return json.loads(contenido)
    except json.JSONDecodeError:
        return None


def _inicio_turno_actual(mensajes: list) -> int:
    """Devuelve la posición del último mensaje del usuario."""
    for indice in range(len(mensajes) - 1, -1, -1):
        if isinstance(mensajes[indice], HumanMessage):
            return indice
    return 0


def _fragmentos_en_historial(mensajes: list) -> list[dict]:
    """Recupera solo los fragmentos RAG del gasto consultado en este turno."""
    fragmentos = []
    inicio = _inicio_turno_actual(mensajes)
    for mensaje in mensajes[inicio + 1 :]:
        if isinstance(mensaje, ToolMessage) and mensaje.name == "buscar_politica":
            resultado = _leer_resultado_herramienta(mensaje)
            if isinstance(resultado, list):
                fragmentos.extend(item for item in resultado if isinstance(item, dict))
    return fragmentos


def _hay_validacion_exitosa_en_turno(mensajes: list) -> bool:
    """Evita reutilizar la validación de un gasto anterior en un turno nuevo."""
    inicio = _inicio_turno_actual(mensajes)
    for mensaje in mensajes[inicio + 1 :]:
        if not isinstance(mensaje, ToolMessage) or mensaje.name != "validar_gasto":
            continue
        resultado = _leer_resultado_herramienta(mensaje)
        if isinstance(resultado, dict) and {"cumple", "incumplimientos", "cuenta"} <= resultado.keys():
            return True
    return False


def _actualizar_estado_herramientas(estado: EstadoAgente, mensajes: list) -> dict:
    """Guarda los datos estructurados que devolvieron las herramientas."""
    if not mensajes or not estado.get("messages"):
        return {}

    ultima_respuesta = estado["messages"][-1]
    llamadas = {
        llamada.get("id"): llamada
        for llamada in getattr(ultima_respuesta, "tool_calls", [])
    }
    mensajes_actualizados = list(mensajes)
    fragmentos = _fragmentos_en_historial(estado["messages"])
    for mensaje in mensajes_actualizados:
        if isinstance(mensaje, ToolMessage) and mensaje.name == "buscar_politica":
            resultado = _leer_resultado_herramienta(mensaje)
            if isinstance(resultado, list):
                fragmentos.extend(item for item in resultado if isinstance(item, dict))
    actualizaciones = {}

    for indice, mensaje in enumerate(mensajes_actualizados):
        if not isinstance(mensaje, ToolMessage):
            continue
        llamada = llamadas.get(mensaje.tool_call_id, {})
        argumentos = llamada.get("args", {})
        resultado = _leer_resultado_herramienta(mensaje)

        if mensaje.name != "validar_gasto" or not isinstance(resultado, dict):
            continue

        gasto = argumentos.get("gasto")
        if not isinstance(gasto, dict):
            continue

        validacion = anexar_revision_saldo(resultado, estado.get("fondo"), gasto)
        mensajes_actualizados[indice] = ToolMessage(
            content=json.dumps(validacion, ensure_ascii=False),
            tool_call_id=mensaje.tool_call_id,
            name=mensaje.name,
            status=mensaje.status,
        )
        politica = resolver_politica(str(argumentos.get("politica", "")))
        codigo_politica = politica["codigo"]
        categoria = resolver_categoria(politica, str(argumentos.get("categoria", "")))
        try:
            codigo_declarado = resolver_politica(str(gasto.get("politica_declarada", "")))["codigo"]
        except ValueError:
            codigo_declarado = ""
        categoria_declarada = str(gasto.get("categoria_declarada", "")).strip().casefold()

        actualizaciones["gasto"] = gasto
        actualizaciones["validacion"] = validacion
        # Un gasto nuevo invalida el veredicto anterior mientras se decide este.
        actualizaciones["veredicto"] = None
        actualizaciones["clasificacion"] = {
            "politica": codigo_politica,
            "categoria": categoria,
            "cuenta": str(validacion.get("cuenta", "")),
            "coincide_con_declarada": (
                codigo_declarado == codigo_politica
                and categoria_declarada == categoria.strip().casefold()
            ),
            "razon": "Clasificación y validación solicitadas por el agente.",
            "fragmentos": fragmentos,
        }

    actualizaciones["messages"] = mensajes_actualizados
    return actualizaciones


def _actualizar_estado_veredicto(estado: EstadoAgente, texto: str) -> tuple[dict, str | None]:
    """Guarda un veredicto solo si el texto declara explícitamente una decisión."""
    clasificacion = estado.get("clasificacion")
    if not clasificacion:
        return {}, None

    actualizaciones = {"clasificacion": {**clasificacion, "razon": texto}}
    coincidencia = _DECISION_EXPLICITA.search(texto)
    if not coincidencia:
        return actualizaciones, None

    veredicto = {
        "decision": coincidencia.group(1).casefold(),
        "motivo": texto.strip(),
        "politica_sugerida": clasificacion["politica"],
        "categoria_sugerida": clasificacion["categoria"],
        "cuenta_sugerida": clasificacion["cuenta"],
    }
    respuesta_ajustada = None
    fondo = estado.get("fondo")
    gasto = estado.get("gasto")
    if fondo and gasto:
        try:
            actualizaciones["fondo"] = aplicar_veredicto(fondo, gasto, veredicto)
        except ValueError as error:
            # Aunque el modelo aprobara, nunca dejamos el fondo bajo cero.
            veredicto["decision"] = "observar"
            veredicto["motivo"] = f"Decisión ajustada a OBSERVAR: {error}"
            respuesta_ajustada = f"Decisión: OBSERVAR. {error}"
            actualizaciones["fondo"] = fondo
            registrar_traza("fondo_aprobacion_bloqueada", {"gasto": gasto.get("id"), "motivo": str(error)})
        else:
            registrar_traza(
                "fondo_actualizado",
                {"id_fondo": fondo["id_fondo"], "saldo_actual": actualizaciones["fondo"]["saldo_actual"]},
            )
    actualizaciones["veredicto"] = veredicto
    actualizaciones["clasificacion"] = {
        **clasificacion,
        "razon": respuesta_ajustada or texto,
    }
    return actualizaciones, respuesta_ajustada


def _trazar_observaciones(mensajes: list) -> None:
    """Muestra los resultados de herramientas que llegaron desde la última respuesta del LLM."""
    for mensaje in reversed(mensajes):
        if not isinstance(mensaje, ToolMessage):
            break
        registrar_traza("observacion", {"herramienta": mensaje.name, "resultado": mensaje.content})


def construir_agente():
    """Arma y devuelve el grafo compilado, con memoria de conversación por hilo."""
    llm = obtener_llm().bind_tools(HERRAMIENTAS)
    nodo_herramientas = ToolNode(HERRAMIENTAS)

    def nodo_llm(estado: EstadoAgente) -> dict:
        # Una vuelta del ciclo: el LLM lee el historial y decide (pensar → actuar).
        _trazar_observaciones(estado["messages"])
        pasos = estado.get("pasos", 0) + 1
        respuesta = llm.invoke([SystemMessage(PROMPT_SISTEMA), *estado["messages"]])
        registrar_traza(
            "llm",
            {"paso": pasos, "pide_herramientas": respuesta.tool_calls, "texto": respuesta.text},
        )
        actualizaciones = {"messages": [respuesta], "pasos": pasos}
        if not respuesta.tool_calls and _hay_validacion_exitosa_en_turno(estado["messages"]):
            cambios_veredicto, respuesta_ajustada = _actualizar_estado_veredicto(
                estado, respuesta.text
            )
            actualizaciones.update(cambios_veredicto)
            if respuesta_ajustada:
                actualizaciones["messages"] = [
                    respuesta.model_copy(update={"content": respuesta_ajustada})
                ]
        return actualizaciones

    def nodo_ejecutar_herramientas(estado: EstadoAgente) -> dict:
        resultado = nodo_herramientas.invoke(estado)
        mensajes = resultado.get("messages", [])
        actualizaciones = {"messages": mensajes}
        actualizaciones.update(_actualizar_estado_herramientas(estado, mensajes))
        return actualizaciones

    def nodo_parada(estado: EstadoAgente) -> dict:
        # Se llegó al máximo de pasos: se cierran las llamadas pendientes y se avisa.
        pendientes = estado["messages"][-1].tool_calls
        cierres = [
            ToolMessage("No ejecutada: se alcanzó el máximo de pasos.", tool_call_id=llamada["id"])
            for llamada in pendientes
        ]
        aviso = AIMessage(f"Me detuve: alcancé el máximo de {MAX_PASOS} pasos sin una decisión final.")
        registrar_traza("parada", {"motivo": "MAX_PASOS", "pasos": estado.get("pasos", 0)})
        return {"messages": [*cierres, aviso]}

    def elegir_siguiente(estado: EstadoAgente) -> str:
        # Condición de parada: sin herramientas pedidas → fin; demasiados pasos → parada.
        if not estado["messages"][-1].tool_calls:
            return END
        if estado.get("pasos", 0) >= MAX_PASOS:
            return "parada"
        return "herramientas"

    grafo = StateGraph(EstadoAgente)
    grafo.add_node("llm", nodo_llm)
    grafo.add_node("herramientas", nodo_ejecutar_herramientas)
    grafo.add_node("parada", nodo_parada)
    grafo.add_edge(START, "llm")
    grafo.add_conditional_edges("llm", elegir_siguiente, ["herramientas", "parada", END])
    grafo.add_edge("herramientas", "llm")
    grafo.add_edge("parada", END)
    return grafo.compile(checkpointer=InMemorySaver())


def conversar(agente, mensaje: str, hilo: str) -> str:
    """Envía un mensaje al agente y devuelve su respuesta en texto.

    El mismo `hilo` mantiene el historial entre turnos (segundo turno, tercero, ...).
    """
    return _conversar_con_estado(agente, mensaje, hilo, {})


def conversar_con_fondo(
    agente, mensaje: str, hilo: str, fondo: EstadoFondo
) -> str:
    """Inicia un turno cargando el fondo en el estado antes de llamar al LLM.

    Para los siguientes turnos del mismo caso, usa `conversar` con el mismo hilo;
    LangGraph conservará el fondo junto con el historial.
    """
    return _conversar_con_estado(agente, mensaje, hilo, {"fondo": fondo})


def _conversar_con_estado(agente, mensaje: str, hilo: str, estado_inicial: dict) -> str:
    """Ejecuta un turno y conserva los campos existentes del hilo."""
    # recursion_limit es un freno de respaldo de LangGraph, por si falla la parada propia.
    configuracion = {"configurable": {"thread_id": hilo}, "recursion_limit": 3 * MAX_PASOS}
    # pasos vuelve a 0 en cada turno: el límite es por turno, no por conversación.
    entrada = {"messages": [HumanMessage(mensaje)], "pasos": 0, **estado_inicial}
    resultado = agente.invoke(entrada, configuracion)
    return resultado["messages"][-1].text
