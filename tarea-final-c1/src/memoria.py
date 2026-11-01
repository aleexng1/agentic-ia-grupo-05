"""Memoria del fondo por rendir: cuánto dinero queda y qué gastos se aprobaron.

Dueño: rol Herramientas y estado.

Es memoria de ESTADO, no de conversación: el fondo vive en EstadoAgente["fondo"] y
LangGraph lo guarda por hilo (checkpointer). Por eso un gasto posterior del mismo
hilo se decide con el saldo actualizado y no con el inicial (RG-08, caso GS-26).

Todas las funciones son puras: reciben un fondo y devuelven uno nuevo, sin modificar
el recibido ni guardar nada global. Así dos hilos (o dos casos del golden set) nunca
comparten saldo.

Cómo lo usa el Núcleo (src/grafo.py):
    1. Al empezar un caso:   estado["fondo"] = fondo_inicial(gasto["id_fondo"])
    2. Tras validar_gasto:   validacion = anexar_revision_saldo(validacion, estado["fondo"], gasto)
    3. Tras el veredicto:    estado["fondo"] = aplicar_veredicto(estado["fondo"], gasto, veredicto)
"""

import copy
import json

from src.config import CARPETA_PROYECTO
from src.contrato import EstadoFondo, Gasto, Incumplimiento, Validacion, Veredicto
from src.herramientas import crear_incumplimiento, leer_politica

# Fondos ficticios (dueño: Caso y calidad).
RUTA_FONDOS = CARPETA_PROYECTO / "datos" / "fondos_ficticios.json"


def _clp(monto: int) -> str:
    """45000 → '$45.000'."""
    return "$" + f"{monto:,}".replace(",", ".")


def fondo_inicial(id_fondo: str) -> EstadoFondo:
    """Devuelve el estado inicial (ficticio) del fondo por rendir indicado.

    Lee datos/fondos_ficticios.json. Lanza ValueError si el fondo no existe.
    """
    datos = json.loads(RUTA_FONDOS.read_text(encoding="utf-8"))
    for fondo in datos["fondos"]:
        if fondo["id_fondo"] == id_fondo:
            return {
                "id_fondo": fondo["id_fondo"],
                "responsable": fondo["responsable"],
                "saldo_inicial": int(fondo["saldo_inicial"]),
                "saldo_actual": int(fondo["saldo_inicial"]),
                "gastos_aprobados": [],
            }
    validos = ", ".join(fondo["id_fondo"] for fondo in datos["fondos"])
    raise ValueError(f"El fondo '{id_fondo}' no existe. Fondos ficticios disponibles: {validos}.")


def revisar_saldo(fondo: EstadoFondo | None, gasto: Gasto) -> Incumplimiento | None:
    """RG-08: devuelve un incumplimiento si el monto supera el saldo disponible del fondo.

    No revisa nada (devuelve None) si no hay fondo cargado, si el fondo es otro o si el
    gasto ya fue aprobado antes (su monto ya está descontado).
    """
    if not fondo or fondo["id_fondo"] != gasto.get("id_fondo"):
        return None
    if gasto.get("id") in fondo["gastos_aprobados"]:
        return None
    monto = int(gasto.get("monto", 0))
    if monto <= fondo["saldo_actual"]:
        return None
    efecto = leer_politica()["reglas"]["RG-08"]["efecto"] or "observar"
    return crear_incumplimiento(
        "RG-08",
        f"El gasto de {_clp(monto)} supera el saldo disponible del fondo {fondo['id_fondo']} "
        f"({_clp(fondo['saldo_actual'])} de {_clp(fondo['saldo_inicial'])}).",
        efecto,
    )


def anexar_revision_saldo(validacion: Validacion, fondo: EstadoFondo | None, gasto: Gasto) -> Validacion:
    """Devuelve una validación nueva con RG-08 agregado si corresponde (no modifica la recibida)."""
    incumplimiento = revisar_saldo(fondo, gasto)
    if incumplimiento is None:
        return copy.deepcopy(validacion)
    return {
        "cumple": False,
        "incumplimientos": [*copy.deepcopy(validacion["incumplimientos"]), incumplimiento],
        "cuenta": validacion["cuenta"],
    }


def aplicar_veredicto(fondo: EstadoFondo, gasto: Gasto, veredicto: Veredicto) -> EstadoFondo:
    """Devuelve el fondo actualizado después de decidir un gasto.

    Si el gasto se aprueba, se descuenta su monto del saldo y se anota su id.
    No modifica el fondo recibido: devuelve una copia nueva.
    Es idempotente: aplicar dos veces el mismo gasto aprobado no descuenta dos veces.
    Lanza ValueError si se intenta aprobar un gasto de otro fondo o sin saldo (RG-08).
    """
    nuevo = copy.deepcopy(fondo)
    if veredicto["decision"] != "aprobar" or gasto["id"] in nuevo["gastos_aprobados"]:
        return nuevo
    if gasto.get("id_fondo") != fondo["id_fondo"]:
        raise ValueError(f"El gasto {gasto['id']} es del fondo {gasto.get('id_fondo')}, no de {fondo['id_fondo']}.")
    if int(gasto["monto"]) > fondo["saldo_actual"]:
        raise ValueError(
            f"RG-08: no se puede aprobar {gasto['id']} por {_clp(int(gasto['monto']))}; "
            f"el saldo del fondo {fondo['id_fondo']} es {_clp(fondo['saldo_actual'])}."
        )
    nuevo["saldo_actual"] -= int(gasto["monto"])
    nuevo["gastos_aprobados"].append(gasto["id"])
    return nuevo


def resumen_fondo(fondo: EstadoFondo) -> str:
    """Describe el fondo en una frase, para mostrarla al LLM o en el notebook."""
    aprobados = fondo["gastos_aprobados"]
    detalle = f" ({', '.join(aprobados)})" if aprobados else ""
    return (
        f"Fondo {fondo['id_fondo']} ({fondo['responsable']}): saldo disponible "
        f"{_clp(fondo['saldo_actual'])} de {_clp(fondo['saldo_inicial'])} CLP; "
        f"{len(aprobados)} gasto(s) aprobado(s){detalle}."
    )
