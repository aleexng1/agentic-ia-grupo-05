"""App única: el coordinador y los cuatro agentes en un solo servidor FastAPI.

Se levanta con: uvicorn app:app --reload --port 8000
(o con `python app.py`, que usa el puerto de PORT o PUERTO del .env)

- /                       panel web del coordinador (y su JSON-RPC A2A por POST)
- /.well-known/agent-card.json   ficha del coordinador
- /panel/consultar        consulta del panel: respuesta, context_id, agente y motivo
- /agentes/{nombre}       JSON-RPC A2A de matias, alex, eduardo y sebastian
- /agentes/{nombre}/.well-known/agent-card.json   ficha de cada agente
- /salud                  chequeo de salud

Control de acceso: todo POST (consulta del panel y JSON-RPC A2A) exige la cabecera
X-API-Key con la clave CLAVE_API; sin ella responde 401. La página, las fichas y /salud
son públicas. Ver src/comun/seguridad.py.

Cada consulta deja líneas de registro (logging) en la salida estándar:
pregunta, agente elegido y su motivo, envío A2A y tiempo de respuesta.

El coordinador descubre las fichas en la primera pregunta (no al arrancar), porque
las sirve esta misma app y durante el arranque sus rutas todavía no responden.
Las consulta por http://127.0.0.1:{puerto}/agentes/{nombre}; el puerto real debe
coincidir con PORT o PUERTO (uvicorn --port no lo informa al programa).
"""

import uvicorn

from src.agente_alex import server as agente_alex
from src.agente_eduardo import server as agente_eduardo
from src.agente_matias import server as agente_matias
from src.agente_sebastian import server as agente_sebastian
from src.comun.config import puerto, ruta_agente
from src.comun.registro import configurar_registro
from src.comun.seguridad import proteger_app
from src.comun.servidor import crear_app, registrar_agente
from src.coordinador.cliente import cerrar_clientes
from src.coordinador.graph import responder, responder_detallado
from src.coordinador.server import tarjeta as tarjeta_coordinador


configurar_registro()

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

# Control de acceso: todo POST exige la clave CLAVE_API en la cabecera X-API-Key.
proteger_app(app)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=puerto())
