"""/chat asíncrono: corre el grafo en segundo plano y guarda su estado para GET /registro/{id}.

Dueño: Alex (c2tf/alex-chat-async). Contrato en docs/contratos.md §11.1 («/chat asíncrono»).

Por qué: Heroku corta una solicitud a los 30 s y `revisar_gasto` tarda hoy 31–52 s
(docs/medicion-tiempos.md). POST /chat responde 202 de inmediato con el id_ejecucion, y el
cliente consulta GET /registro/{id} hasta que el estado deje de ser "en_proceso".

- Todo corre dentro del mismo proceso, con un grupo de hilos (MAX_EJECUCIONES_SIMULTANEAS, 4 por
  defecto). No hay servicios nuevos.
- El estado y la respuesta completa se guardan **en la memoria del proceso**, porque la tabla
  `ejecuciones` (Sebastián) no admite `en_proceso` ni guarda la respuesta. Se conservan las últimas
  MAX_GUARDADAS. Si el proceso se reinicia, de una ejecución vieja solo queda su fila en Postgres.
- Tope global, TIEMPO_MAX_EJECUCION_SEG (90 s): si una ejecución no termina a tiempo, queda en
  "error" con un mensaje claro y su fila se registra como "error" en ese momento. Python no
  permite matar un hilo: si el turno termina después, su resultado se descarta (nunca reemplaza
  al error) y su propio registro se ignora (mismo id_ejecucion).
"""

import os
import threading
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from uuid import uuid4

from src.comun.errores import traducir_error
from src.comun.registro import obtener_registro
from src.principal import grafo as modulo_grafo
from src.principal import router

ESTADOS = ("en_proceso", "ok", "bloqueado", "fallback", "error")
MAX_GUARDADAS = 500
MAX_SIMULTANEAS_POR_DEFECTO = 4

_REGISTRO = obtener_registro()
_EJECUCIONES: "OrderedDict[str, dict]" = OrderedDict()
_CANDADO = threading.Lock()
_GRUPO: ThreadPoolExecutor | None = None


def _max_simultaneas() -> int:
    valor = os.getenv("MAX_EJECUCIONES_SIMULTANEAS", "").strip()
    try:
        return max(1, int(valor)) if valor else MAX_SIMULTANEAS_POR_DEFECTO
    except ValueError:
        raise ValueError(f"MAX_EJECUCIONES_SIMULTANEAS debe ser un entero positivo; vale «{valor}».") from None


def _grupo() -> ThreadPoolExecutor:
    global _GRUPO
    with _CANDADO:
        if _GRUPO is None:
            _GRUPO = ThreadPoolExecutor(max_workers=_max_simultaneas(), thread_name_prefix="chat")
        return _GRUPO


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _guardar(id_ejecucion: str, datos: dict) -> None:
    with _CANDADO:
        _EJECUCIONES[id_ejecucion] = datos
        # Se descartan primero las más antiguas ya terminadas (nunca una en proceso).
        while len(_EJECUCIONES) > MAX_GUARDADAS:
            vieja = next((k for k, v in _EJECUCIONES.items() if v["estado"] != "en_proceso"), None)
            if vieja is None:
                break
            _EJECUCIONES.pop(vieja)


def _terminar(id_ejecucion: str, estado: str, *, resultado: dict | None = None, detail: str | None = None) -> bool:
    """Cierra una ejecución en proceso. False si ya estaba cerrada (por ejemplo, por el tope)."""
    with _CANDADO:
        datos = _EJECUCIONES.get(id_ejecucion)
        if datos is None or datos["estado"] != "en_proceso":
            return False
        datos.update(estado=estado, resultado=resultado, detail=detail, fin=_ahora(),
                     segundos=round(time.monotonic() - datos["_inicio"], 1))
        return True


def _vencer(id_ejecucion: str, segundos: float) -> None:
    """Lo llama el temporizador del tope: si sigue en proceso, queda en "error" sin resultado."""
    mensaje = f"{modulo_grafo.mensaje_tope(segundos)} (id_ejecucion: {id_ejecucion})"
    if _terminar(id_ejecucion, "error", detail=mensaje):
        datos = _EJECUCIONES.get(id_ejecucion, {})
        try:
            modulo_grafo.registrar_vencida(id_ejecucion, datos.get("thread_id", ""), datos["_fecha"], int(segundos * 1000))
        except Exception as error:  # noqa: BLE001 (el registro nunca rompe la respuesta)
            _REGISTRO.error("ejecución %s · no se pudo registrar el tope · %s", id_ejecucion, traducir_error(error))


def _trabajar(id_ejecucion: str, thread_id: str, texto: str, imagen, gasto, limite: float, temporizador) -> None:
    try:
        if time.monotonic() > limite:  # esperó en la cola más que el tope: ni siquiera se empieza
            return
        resultado = modulo_grafo.ejecutar(thread_id, texto, imagen, gasto, id_ejecucion=id_ejecucion, limite=limite)
        if not _terminar(id_ejecucion, resultado.get("estado_final", "error"), resultado=resultado):
            _REGISTRO.warning("ejecución %s · terminó después del tope: se descarta su resultado", id_ejecucion)
    except modulo_grafo.ErrorDeEjecucion as error:
        _terminar(id_ejecucion, "error", detail=f"{error} (id_ejecucion: {id_ejecucion})")
    except router.MensajeInvalido as error:
        _terminar(id_ejecucion, "error", detail=str(error))
    except NotImplementedError as error:
        _terminar(id_ejecucion, "error", detail=f"Todavía no implementado: {error} (id_ejecucion: {id_ejecucion})")
    except Exception as error:  # noqa: BLE001 (cualquier falla queda como error claro, nunca como resultado)
        mensaje = traducir_error(error)
        _REGISTRO.error("ejecución %s · falla en segundo plano · %s", id_ejecucion, mensaje)
        _terminar(id_ejecucion, "error", detail=f"{mensaje} (id_ejecucion: {id_ejecucion})")
    finally:
        temporizador.cancel()


def lanzar(thread_id: str | None, texto: str, imagen: dict | None = None, gasto: dict | None = None) -> dict:
    """Valida el texto, deja la ejecución en "en_proceso" y la corre en segundo plano.

    Lanza router.MensajeInvalido antes de aceptar, para que la API responda 422 y no 202.
    Devuelve el cuerpo del 202: {id_ejecucion, estado, consultar, thread_id}.
    """
    router.validar_mensaje(texto)
    tope = modulo_grafo.tiempo_max_ejecucion_seg()
    thread_id = (thread_id or "").strip() or str(uuid4())
    id_ejecucion = str(uuid4())
    inicio = time.monotonic()
    _guardar(id_ejecucion, {
        "id_ejecucion": id_ejecucion, "estado": "en_proceso", "thread_id": thread_id, "inicio": _ahora(),
        "fin": None, "segundos": None, "resultado": None, "detail": None,
        "_inicio": inicio, "_fecha": datetime.now(timezone.utc),
    })
    temporizador = threading.Timer(tope, _vencer, args=(id_ejecucion, tope))
    temporizador.daemon = True
    temporizador.start()
    _grupo().submit(_trabajar, id_ejecucion, thread_id, texto, imagen, gasto, inicio + tope, temporizador)
    _REGISTRO.info("chat · %s · aceptado en segundo plano (tope %g s)", id_ejecucion, tope)
    return {"id_ejecucion": id_ejecucion, "estado": "en_proceso", "consultar": f"/registro/{id_ejecucion}",
            "thread_id": thread_id}


def consultar(id_ejecucion: str) -> dict | None:
    """Estado de una ejecución de este proceso (sin campos internos), o None si no está."""
    with _CANDADO:
        datos = _EJECUCIONES.get(id_ejecucion)
        if datos is None:
            return None
        copia = {k: v for k, v in datos.items() if not k.startswith("_")}
        if copia["estado"] == "en_proceso":
            copia["segundos"] = round(time.monotonic() - datos["_inicio"], 1)
        return copia
