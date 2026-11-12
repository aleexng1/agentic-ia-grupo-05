"""Ficha A2A del agente de presupuestos de Eduardo; app.py lo publica en /agentes/eduardo."""

from src.agente_eduardo.graph import responder
from src.comun.config import url_agente
from src.comun.tarjeta import crear_tarjeta

tarjeta = crear_tarjeta(
    "Agente de Eduardo",
    "Estima presupuestos agregados y simulados para ferias y eventos usando únicamente tarifas ficticias. Incluye un costo de alimentación genérica por persona, pero no prepara menús (Sebastián), ni recomienda recintos (Alex); tampoco autoriza compras, reservas, pagos o contrataciones.",
    url_agente("eduardo"),
    [
        (
            "estimar_presupuesto",
            "Estimar presupuesto de evento",
            "Calcula partidas agregadas simuladas en CLP para un evento, según tipo, asistentes y duración.",
            "¿Cuál es el presupuesto simulado de una feria tecnológica para 80 personas y 4 horas?",
        ),
    ],
)
