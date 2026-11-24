"""Corre el golden set de C2 contra el agente y calcula el porcentaje de aciertos.

Dueño: Alex (c2tf/alex-integracion). Uso previsto:  python -m evaluacion.evaluar
Referencia: tarea-final-c1/pruebas/evaluar.py (no se copió: está amarrado al agente de c1).
"""


def cargar_golden(ruta: str = "evaluacion/golden_set.json") -> dict:
    """Lee el golden set versionado y revisa que cada caso tenga el formato de su README."""
    raise NotImplementedError("cargar_golden: pendiente (Alex).")


def correr_caso(caso: dict) -> dict:
    """Envía el caso al agente (POST /chat o src.principal.grafo.responder) y compara.

    Compara ruta, decisión y estado_final con lo esperado. Devuelve
    {"id", "acierto": bool, "esperado", "obtenido", "id_ejecucion"}.
    """
    raise NotImplementedError("correr_caso: pendiente (Alex).")


def main() -> int:
    """Corre todos los casos, muestra la tabla y el % de aciertos y guarda el resultado."""
    raise NotImplementedError("evaluar: pendiente (Alex).")


if __name__ == "__main__":
    raise SystemExit(main())
