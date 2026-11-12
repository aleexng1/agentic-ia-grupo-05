"""App única: el coordinador y los cuatro agentes en un solo servidor FastAPI.

Se levanta con: uvicorn app:app --reload --port 8000

- /                       panel web del coordinador (y su JSON-RPC A2A por POST)
- /.well-known/agent-card.json   ficha del coordinador
- /panel/consultar        consulta del panel: respuesta, context_id, agente y motivo
- /agentes/{nombre}       JSON-RPC A2A de matias, alex, eduardo y sebastian
- /agentes/{nombre}/.well-known/agent-card.json   ficha de cada agente
- /salud                  chequeo de salud

El coordinador descubre las fichas en la primera pregunta (no al arrancar), porque
las sirve esta misma app y durante el arranque sus rutas todavía no responden.
"""

from src.agente_alex import server as agente_alex
from src.agente_eduardo import server as agente_eduardo
from src.agente_matias import server as agente_matias
from src.agente_sebastian import server as agente_sebastian
from src.comun.config import ruta_agente
from src.comun.servidor import crear_app, registrar_agente
from src.coordinador.cliente import cerrar_clientes
from src.coordinador.graph import responder, responder_detallado
from src.coordinador.server import tarjeta as tarjeta_coordinador


AGENTES = {
    "matias": agente_matias,
    "alex": agente_alex,
    "eduardo": agente_eduardo,
    "sebastian": agente_sebastian,
}

app = crear_app(tarjeta_coordinador, responder, responder_panel=responder_detallado)

for _nombre, _agente in AGENTES.items():
    registrar_agente(app, _agente.tarjeta, _agente.responder, prefijo=ruta_agente(_nombre))

app.router.on_shutdown.append(cerrar_clientes)
