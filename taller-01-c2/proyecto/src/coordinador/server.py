"""Aplicación HTTP del coordinador A2A."""

import os

from dotenv import load_dotenv

from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta
from src.coordinador.cliente import cerrar_clientes
from src.coordinador.graph import inicializar_supervisor, responder


load_dotenv()
URL_COORDINADOR = os.getenv("URL_COORDINADOR", "http://127.0.0.1:8002")

tarjeta = crear_tarjeta(
    "Coordinador",
    "Recibe preguntas sobre la organización de una feria o evento y las delega por A2A al agente que corresponde: programa y horarios (Matias), lugares y capacidad (Alex), presupuesto y costos (Eduardo) o comida y catering (Sebastian). No tiene conocimiento propio sobre esos temas ni reserva ni confirma nada.",
    URL_COORDINADOR,
    [
        (
            "delegar_consulta",
            "Consultar al agente del planificador de eventos",
            "Elige el agente especializado según la pregunta (programa, lugares, presupuesto o comida), se la envía por A2A y repite su respuesta indicando cuál respondió.",
            "Estoy organizando una feria tecnológica: ¿qué actividades puedo incluir en 4 horas?",
        ),
    ],
)

app = crear_app(tarjeta, responder)


async def _iniciar_supervisor() -> None:
    """Descubre los agentes una vez, durante el inicio de FastAPI."""
    await inicializar_supervisor(imprimir=True)


app.router.on_startup.append(_iniciar_supervisor)
app.router.on_shutdown.append(cerrar_clientes)
