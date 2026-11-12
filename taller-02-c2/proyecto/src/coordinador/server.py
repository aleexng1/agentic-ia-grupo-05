"""Ficha A2A del coordinador; app.py lo publica en la raíz de la app única."""

from src.comun.config import url_base
from src.comun.tarjeta import crear_tarjeta


tarjeta = crear_tarjeta(
    "Coordinador",
    "Recibe preguntas sobre la organización de una feria o evento y las delega por A2A al agente que corresponde: programa y horarios (Matias), lugares y capacidad (Alex), presupuesto y costos (Eduardo) o comida y catering (Sebastian). No tiene conocimiento propio sobre esos temas ni reserva ni confirma nada.",
    url_base(),
    [
        (
            "delegar_consulta",
            "Consultar al agente del planificador de eventos",
            "Elige el agente especializado según la pregunta (programa, lugares, presupuesto o comida), se la envía por A2A y repite su respuesta indicando cuál respondió.",
            "Estoy organizando una feria tecnológica: ¿qué actividades puedo incluir en 4 horas?",
        ),
    ],
)
