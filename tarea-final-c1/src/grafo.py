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
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from src.config import obtener_llm, registrar_traza
from src.contrato import DECISIONES, MAX_PASOS, Decision, EstadoAgente, EstadoFondo, Veredicto
from src.herramientas import (
    GRAVEDAD,
    decision_sugerida,
    efecto_de,
    resolver_categoria,
    resolver_politica,
    validar_gasto,
)
from src.memoria import (
    anexar_revision_saldo,
    aplicar_veredicto,
    fondo_inicial,
    resumen_fondo,
)
from src.rag import buscar_politica
from src.registro import registrar_veredicto
from src.seguridad import PROMPT_SISTEMA, juzgar

# Herramientas que el LLM puede pedir.
@tool
def emitir_veredicto(
    decision: Decision,
    politica: str,
    categoria: str,
    cuenta: str,
    motivo: str,
) -> Veredicto:
    """Cierra la revisión después de validar; entrega la decisión como datos estructurados.

    politica debe ser el código Pxx. El grafo verifica luego que la decisión no sea
    más permisiva que las reglas, el juez y el saldo del fondo.
    """
    if decision not in DECISIONES:
        raise ValueError(f"Decisión no permitida: {decision}.")
    datos_politica = resolver_politica(politica)
    categoria_exacta = resolver_categoria(datos_politica, categoria)
    cuenta = cuenta.strip()
    motivo = motivo.strip()
    if not cuenta or not motivo:
        raise ValueError("emitir_veredicto requiere cuenta y motivo no vacíos.")
    return {
        "decision": decision,
        "motivo": motivo,
        "politica_sugerida": datos_politica["codigo"],
        "categoria_sugerida": categoria_exacta,
        "cuenta_sugerida": cuenta,
    }


HERRAMIENTAS = [buscar_politica, validar_gasto, emitir_veredicto]


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


def _emitio_veredicto_en_turno(mensajes: list) -> bool:
    """Detecta el cierre estructurado del caso actual, no el de un hilo anterior."""
    inicio = _inicio_turno_actual(mensajes)
    return any(
        isinstance(mensaje, ToolMessage) and mensaje.name == "emitir_veredicto"
        for mensaje in mensajes[inicio + 1 :]
    )


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

        fondo = estado.get("fondo")
        if not fondo or fondo["id_fondo"] != gasto.get("id_fondo"):
            fondo = fondo_inicial(gasto["id_fondo"])
        validacion = anexar_revision_saldo(resultado, fondo, gasto)
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
        actualizaciones["fondo"] = fondo
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

    mensajes_del_turno = [*estado["messages"], *mensajes_actualizados]
    if _hay_validacion_exitosa_en_turno(mensajes_del_turno):
        for mensaje in mensajes_actualizados:
            if not isinstance(mensaje, ToolMessage) or mensaje.name != "emitir_veredicto":
                continue
            resultado = _leer_resultado_herramienta(mensaje)
            if isinstance(resultado, dict) and {
                "decision",
                "motivo",
                "politica_sugerida",
                "categoria_sugerida",
                "cuenta_sugerida",
            } <= resultado.keys():
                actualizaciones["veredicto"] = resultado

    actualizaciones["messages"] = mensajes_actualizados
    return actualizaciones


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
        return {"messages": [respuesta], "pasos": pasos}

    def nodo_ejecutar_herramientas(estado: EstadoAgente) -> dict:
        resultado = nodo_herramientas.invoke(estado)
        mensajes = resultado.get("messages", [])
        actualizaciones = {"messages": mensajes}
        actualizaciones.update(_actualizar_estado_herramientas(estado, mensajes))
        return actualizaciones

    def nodo_cerrar(estado: EstadoAgente) -> dict:
        """Aplica el piso de reglas, el juez, el fondo y el registro al veredicto final."""
        if not _hay_validacion_exitosa_en_turno(estado["messages"]):
            registrar_traza("cerrar", {"registrado": False, "motivo": "sin validar_gasto en este turno"})
            if _emitio_veredicto_en_turno(estado["messages"]):
                return {
                    "messages": [
                        AIMessage(
                            "Decisión: OBSERVAR\n\n"
                            "No puedo registrar ni decidir un gasto que no se validó en este turno."
                        )
                    ]
                }
            return {}

        veredicto = estado.get("veredicto")
        gasto = estado.get("gasto")
        validacion = estado.get("validacion")
        clasificacion = estado.get("clasificacion")
        if not veredicto or not gasto or not validacion or not clasificacion:
            registrar_traza("cerrar", {"registrado": False, "motivo": "falta emitir_veredicto estructurado"})
            return {
                "messages": [
                    AIMessage(
                        "No recibí un veredicto estructurado válido; no apliqué el fondo ni registré el gasto."
                    )
                ]
            }

        veredicto = dict(veredicto)
        propuesta = veredicto["decision"]
        ajustes = []
        sugerencias_correctas = {
            "politica_sugerida": clasificacion["politica"],
            "categoria_sugerida": clasificacion["categoria"],
            "cuenta_sugerida": validacion["cuenta"],
        }
        for campo, valor_correcto in sugerencias_correctas.items():
            if veredicto.get(campo) != valor_correcto:
                ajustes.append(f"se corrigió {campo} según clasificación y validación")
                veredicto[campo] = valor_correcto

        piso = decision_sugerida(validacion)
        incumplimientos = validacion.get("incumplimientos", [])
        if (incumplimientos or not validacion.get("cumple", True)) and veredicto["decision"] == "aprobar":
            decision_segura = piso if piso != "aprobar" else "observar"
            veredicto["decision"] = decision_segura
            reglas = ", ".join(item.get("regla", "regla sin código") for item in incumplimientos)
            registrar_traza(
                "aprobacion_bloqueada",
                {"decision_sugerida": decision_segura, "reglas": reglas},
            )
            ajustes.append(
                "validar_gasto encontró incumplimientos"
                + (f" ({reglas})" if reglas else "")
            )
        if GRAVEDAD[veredicto["decision"]] < GRAVEDAD[piso]:
            registrar_traza("piso_reglas", {"llm": veredicto["decision"], "reglas": piso})
            veredicto["decision"] = piso
            reglas = ", ".join(
                incumplimiento["regla"]
                for incumplimiento in validacion["incumplimientos"]
                if efecto_de(incumplimiento) == piso
            )
            ajustes.append(f"las reglas exactas exigen {piso.upper()} ({reglas})")

        juicio = juzgar(gasto, clasificacion, veredicto)
        registrar_traza("juez", juicio)
        if not juicio["valido"] and veredicto["decision"] == "aprobar":
            veredicto["decision"] = "observar"
            ajustes.append(f"el juez no validó la aprobación: {juicio['razon']}")

        fondo = estado.get("fondo") or fondo_inicial(gasto["id_fondo"])
        try:
            nuevo_fondo = aplicar_veredicto(fondo, gasto, veredicto)
        except ValueError as error:
            registrar_traza("fondo_error", {"error": str(error)})
            veredicto["decision"] = "observar"
            ajustes.append(f"el fondo no permite aprobar ({error})")
            nuevo_fondo = aplicar_veredicto(fondo, gasto, veredicto)

        respuesta_ajustada = None
        if ajustes:
            veredicto["motivo"] += (
                f" [Ajustado de {propuesta.upper()} a {veredicto['decision'].upper()}: "
                f"{'; '.join(ajustes)}.]"
            )
            respuesta_ajustada = (
                f"Decisión: {veredicto['decision'].upper()}\n\n"
                f"Ajusté la propuesta del agente ({propuesta.upper()}): {'; '.join(ajustes)}."
            )

        registro = registrar_veredicto(gasto, veredicto)
        registrar_traza(
            "fondo",
            {"antes": resumen_fondo(fondo), "despues": resumen_fondo(nuevo_fondo)},
        )
        registrar_traza(
            "registro",
            {
                "antes": registro["antes"],
                "despues": registro["despues"],
                "id_gasto": registro["id_gasto"],
                "decision": registro["decision"],
                "operacion": registro["operacion"],
            },
        )
        respuesta_final = (
            f"Decisión: {veredicto['decision'].upper()}\n"
            f"Política: {veredicto['politica_sugerida']}\n"
            f"Categoría: {veredicto['categoria_sugerida']}\n"
            f"Cuenta: {veredicto['cuenta_sugerida']}\n"
            f"Motivo: {veredicto['motivo']}"
        )
        actualizaciones = {
            "veredicto": veredicto,
            "fondo": nuevo_fondo,
            "clasificacion": {**clasificacion, "razon": veredicto["motivo"]},
            "messages": [AIMessage(respuesta_ajustada or respuesta_final)],
        }
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
        if not estado["messages"][-1].tool_calls:
            # Si el agente termina sin emitir estructura tras validar, se cierra de forma segura.
            if _hay_validacion_exitosa_en_turno(estado["messages"]):
                return "cerrar"
            return END
        if estado.get("pasos", 0) >= MAX_PASOS:
            return "parada"
        return "herramientas"

    def elegir_despues_herramientas(estado: EstadoAgente) -> str:
        if _emitio_veredicto_en_turno(estado["messages"]):
            return "cerrar"
        return "llm"

    grafo = StateGraph(EstadoAgente)
    grafo.add_node("llm", nodo_llm)
    grafo.add_node("herramientas", nodo_ejecutar_herramientas)
    grafo.add_node("cerrar", nodo_cerrar)
    grafo.add_node("parada", nodo_parada)
    grafo.add_edge(START, "llm")
    grafo.add_conditional_edges("llm", elegir_siguiente, ["herramientas", "cerrar", "parada", END])
    grafo.add_conditional_edges("herramientas", elegir_despues_herramientas, ["cerrar", "llm"])
    grafo.add_edge("cerrar", END)
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
