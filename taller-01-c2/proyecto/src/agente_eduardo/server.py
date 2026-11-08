"""Aplicación HTTP A2A del agente de presupuestos de Eduardo."""

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi.responses import FileResponse

from src.agente_eduardo.graph import responder
from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta

load_dotenv()
URL_EDUARDO = os.getenv("URL_EDUARDO", "http://127.0.0.1:8005")

tarjeta = crear_tarjeta(
    "Agente de Eduardo",
    "Estima presupuestos agregados y simulados para ferias y eventos usando únicamente tarifas ficticias. No prepara menús ni cotiza catering (Sebastián), ni recomienda recintos (Alex); tampoco autoriza compras, reservas, pagos o contrataciones.",
    URL_EDUARDO,
    [
        (
            "estimar_presupuesto",
            "Estimar presupuesto de evento",
            "Calcula partidas agregadas simuladas en CLP para un evento, según tipo, asistentes y duración.",
            "¿Cuál es el presupuesto simulado de una feria tecnológica para 80 personas y 4 horas?",
        ),
    ],
)

app = crear_app(tarjeta, responder)

_ARCHIVO_DEMO = Path(__file__).with_name("demo.html")


@app.get("/demo", include_in_schema=False)
async def mostrar_demo() -> FileResponse:
    """Sirve la interfaz de demostración del agente de Eduardo."""
    return FileResponse(_ARCHIVO_DEMO, media_type="text/html; charset=utf-8")
