import json
import os
import re
from typing import Annotated, Literal

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel
from typing_extensions import TypedDict

from .prompts import (
    BLOQUEOS,
    CORRECCION,
    DATOS_ENCONTRADOS,
    FUENTE,
    GUARDIA,
    GUARDIA_SALIDA,
    MAX_PALABRAS,
    NO_CONFIRMADO,
    NO_VERIFICADO_SALIDA,
    SIN_FUENTE,
    SISTEMA,
)
from .registro import registrar
from .tools import CONTADOR, cargar_herramientas

LINEA_FUENTE = re.compile(r"(?im)^[ \t>*_]*fuentes?\s*:.*$")
MENSAJES_DE_CONTEXTO = 2
MAX_DATOS_ENCONTRADOS = 8


class Veredicto(BaseModel):
    permitido: bool
    categoria: Literal["ok", "fuera_de_tema", "inyeccion", "datos_personales", "accion_no_soportada"]
    motivo: str


class Revision(BaseModel):
    aprobada: bool
    problemas: list[Literal["dato_no_respaldado", "formato", "lenguaje", "datos_personales"]]
    detalle: str


class Estado(TypedDict):
    messages: Annotated[list, add_messages]
    veredicto: dict | None
    revision: dict | None
    reintento: bool


def es_correccion(mensaje) -> bool:
    return isinstance(mensaje, HumanMessage) and bool(mensaje.additional_kwargs.get("correccion"))


def es_del_usuario(mensaje) -> bool:
    return isinstance(mensaje, HumanMessage) and not es_correccion(mensaje)


def mensajes_del_turno(mensajes: list) -> list:
    """Mensajes posteriores al último mensaje del usuario (las correcciones internas no cuentan)."""
    for i in range(len(mensajes) - 1, -1, -1):
        if es_del_usuario(mensajes[i]):
            return mensajes[i + 1 :]
    return mensajes


def thread_de(config: RunnableConfig) -> str:
    return config.get("configurable", {}).get("thread_id", "default")


def crear_guardia(modelo_guardia):
    clasificador = modelo_guardia.with_structured_output(Veredicto)

    async def guardia_entrada(estado: Estado, config: RunnableConfig) -> dict:
        CONTADOR.reiniciar(thread_de(config))  # pregunta nueva: se reinician los límites
        humanos = [m.text for m in estado["messages"] if es_del_usuario(m)]
        previos = humanos[-1 - MENSAJES_DE_CONTEXTO : -1]
        contexto = "".join(f"Mensaje previo del usuario: {t}\n" for t in previos)
        pedido = f"{contexto}<mensaje>\n{humanos[-1]}\n</mensaje>"
        try:
            v = await clasificador.ainvoke(
                [SystemMessage(GUARDIA), HumanMessage(pedido)]
            )
            if v is None:
                raise ValueError("el clasificador no devolvió un veredicto")
            veredicto = v.model_dump()
            veredicto["permitido"] = veredicto["permitido"] and veredicto["categoria"] == "ok"
        except Exception as exc:
            veredicto = {
                "permitido": False,
                "categoria": "no_verificado",
                "motivo": f"falló la guardia: {type(exc).__name__}",
            }
        registrar("entrada", veredicto["categoria"], veredicto["motivo"])
        return {"veredicto": veredicto, "revision": None, "reintento": False}

    return guardia_entrada


def decidir(estado: Estado) -> str:
    return "agente" if estado["veredicto"]["permitido"] else "respuesta_bloqueada"


def respuesta_bloqueada(estado: Estado) -> dict:
    return {"messages": [AIMessage(BLOQUEOS[estado["veredicto"]["categoria"]])]}


def datos_de_las_tools(resultados: list[str]) -> list[str]:
    """Nombres que aparecen en los resultados de las tools (sin repetir)."""
    nombres: list[str] = []
    for texto in resultados:
        try:
            datos = json.loads(texto)
        except ValueError:
            continue
        for item in datos if isinstance(datos, list) else [datos]:
            nombre = item.get("name") if isinstance(item, dict) else None
            if nombre and nombre not in nombres:
                nombres.append(nombre)
    return nombres[:MAX_DATOS_ENCONTRADOS]


def crear_guardia_salida(modelo_revisor):
    revisor = modelo_revisor.with_structured_output(Revision)

    async def guardia_salida(estado: Estado) -> dict:
        turno = mensajes_del_turno(estado["messages"])
        finales = [m for m in turno if isinstance(m, AIMessage) and not m.tool_calls]
        if not finales:
            return {}
        borrador = finales[-1]
        texto = LINEA_FUENTE.sub("", borrador.text).strip()
        resultados = [(m.name, m.text) for m in turno if isinstance(m, ToolMessage)]
        pregunta = next((m.text for m in reversed(estado["messages"]) if es_del_usuario(m)), "")
        bloques = "\n\n".join(f"[{nombre}]\n{contenido}" for nombre, contenido in resultados)
        pedido = (
            f"Pregunta del usuario:\n{pregunta}\n\n"
            f"Resultados de las herramientas ({len(resultados)}):\n{bloques or '(ninguno)'}\n\n"
            f"<borrador>\n{texto}\n</borrador>"
        )
        previo = bool(estado.get("reintento"))
        base = {"chars_enviados": len(pedido), "reintento_previo": previo}

        try:
            rev = await revisor.ainvoke([SystemMessage(GUARDIA_SALIDA), HumanMessage(pedido)])
            if rev is None:
                raise ValueError("el revisor no devolvió una revisión")
        except Exception as exc:
            detalle = f"falló la guardia: {type(exc).__name__}"
            registrar("salida", "no_verificada", detalle)
            revision = {**base, "aprobada": False, "problemas": [], "detalle": detalle, "accion": "bloquear"}
            return {"revision": revision, "messages": [AIMessage(NO_VERIFICADO_SALIDA, id=borrador.id)]}

        # el largo se mide en código; el modelo no opina de formato
        palabras = len(texto.split())
        problemas = [p for p in rev.problemas if p != "formato"]
        detalle = rev.detalle
        if palabras > MAX_PALABRAS:
            problemas.append("formato")
            detalle += f" El borrador tiene {palabras} palabras y el máximo es {MAX_PALABRAS}."
        aprobada = (rev.aprobada or set(rev.problemas) <= {"formato"}) and not problemas
        revision = {**base, "aprobada": aprobada, "problemas": problemas, "detalle": detalle}
        registrar("salida", "ok" if aprobada else ",".join(problemas) or "sin_clasificar", detalle)

        if aprobada:
            return {"revision": {**revision, "accion": "aprobar"}}
        if not previo:
            correccion = HumanMessage(
                CORRECCION.format(detalle=detalle.rstrip(". "), max_palabras=MAX_PALABRAS),
                additional_kwargs={"correccion": True},
            )
            return {
                "revision": {**revision, "accion": "reintentar"},
                "reintento": True,
                "messages": [correccion],
            }
        datos = datos_de_las_tools([contenido for _, contenido in resultados])
        respuesta = NO_CONFIRMADO
        if datos:
            respuesta += " " + DATOS_ENCONTRADOS.format(datos=", ".join(datos))
        return {
            "revision": {**revision, "accion": "bloquear"},
            "messages": [AIMessage(respuesta, id=borrador.id)],
        }

    return guardia_salida


def decidir_salida(estado: Estado) -> str:
    accion = (estado.get("revision") or {}).get("accion")
    return "agente" if accion == "reintentar" else "agregar_fuente"


def agregar_fuente(estado: Estado) -> dict:
    turno = mensajes_del_turno(estado["messages"])
    usadas = list(dict.fromkeys(m.name for m in turno if isinstance(m, ToolMessage)))
    finales = [m for m in turno if isinstance(m, AIMessage) and not m.tool_calls]
    if not finales:
        return {}
    ultimo = finales[-1]
    texto = LINEA_FUENTE.sub("", ultimo.text).rstrip()
    linea = FUENTE.format(herramientas=", ".join(usadas)) if usadas else SIN_FUENTE
    # mismo id: add_messages reemplaza el mensaje del modelo por el corregido
    return {"messages": [AIMessage(f"{texto}\n\n{linea}", id=ultimo.id)]}


def crear_modelo(nombre: str, clave: str | None, **extra):
    return ChatGoogleGenerativeAI(model=nombre, google_api_key=clave, **extra)


async def construir_agente(api_key: str | None = None):
    herramientas = await cargar_herramientas()
    clave = api_key or os.environ.get("GOOGLE_API_KEY")
    modelo_base = os.environ["MODELO"]
    modelo_revisor = os.environ.get("MODELO_GUARDIA") or modelo_base
    agente_react = create_agent(
        crear_modelo(modelo_base, clave), herramientas, system_prompt=SISTEMA
    )

    grafo = StateGraph(Estado)
    grafo.add_node("guardia_entrada", crear_guardia(crear_modelo(modelo_base, clave, temperature=0)))
    grafo.add_node("agente", agente_react)
    grafo.add_node(
        "guardia_salida", crear_guardia_salida(crear_modelo(modelo_revisor, clave, temperature=0))
    )
    grafo.add_node("agregar_fuente", agregar_fuente)
    grafo.add_node("respuesta_bloqueada", respuesta_bloqueada)
    grafo.add_edge(START, "guardia_entrada")
    grafo.add_conditional_edges(
        "guardia_entrada",
        decidir,
        {"agente": "agente", "respuesta_bloqueada": "respuesta_bloqueada"},
    )
    grafo.add_edge("agente", "guardia_salida")
    grafo.add_conditional_edges(
        "guardia_salida",
        decidir_salida,
        {"agente": "agente", "agregar_fuente": "agregar_fuente"},
    )
    grafo.add_edge("agregar_fuente", END)
    grafo.add_edge("respuesta_bloqueada", END)
    return grafo.compile(checkpointer=MemorySaver())
