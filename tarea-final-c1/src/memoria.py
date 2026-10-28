"""Memoria del fondo por rendir: cuánto dinero queda y qué gastos se aprobaron.

Dueño: rol Herramientas y estado.
"""

from src.contrato import EstadoFondo, Gasto, Veredicto


def fondo_inicial(id_fondo: str) -> EstadoFondo:
    """Devuelve el estado inicial (ficticio) del fondo por rendir indicado."""
    # TODO(herramientas): reemplazar stub (leer fondos ficticios de datos/)
    return {
        "id_fondo": id_fondo,
        "responsable": "Persona Ficticia",
        "saldo_inicial": 200000,
        "saldo_actual": 200000,
        "gastos_aprobados": [],
    }


def aplicar_veredicto(fondo: EstadoFondo, gasto: Gasto, veredicto: Veredicto) -> EstadoFondo:
    """Devuelve el fondo actualizado después de decidir un gasto.

    Si el gasto se aprueba, se descuenta su monto del saldo y se anota su id.
    No modifica el fondo recibido: devuelve una copia nueva.
    """
    # TODO(herramientas): reemplazar stub (descontar monto si se aprueba)
    return {**fondo, "gastos_aprobados": list(fondo["gastos_aprobados"])}


def resumen_fondo(fondo: EstadoFondo) -> str:
    """Describe el fondo en una frase, para mostrarla al LLM o en el notebook."""
    # TODO(herramientas): reemplazar stub
    return (
        f"Fondo {fondo['id_fondo']} ({fondo['responsable']}): saldo "
        f"{fondo['saldo_actual']} de {fondo['saldo_inicial']} CLP, "
        f"{len(fondo['gastos_aprobados'])} gastos aprobados."
    )
