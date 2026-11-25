"""App FastAPI del verificador (agente especialista A2A), separada del principal.

Se levanta con:  uvicorn src.verificador.app:app --port 8001
En Heroku es una app aparte con APP_MODULE=src.verificador.app:app (ver docs/reparto.md).

- GET  /health                       chequeo de salud (público)
- GET  /.well-known/agent-card.json  ficha A2A (pública)
- POST /                             JSON-RPC A2A (protegido)

Protección del canal A2A (docs/contratos.md §6 y §11.2): proteger_con_token_a2a (Matías,
src/comun/seguridad.py) exige `Authorization: Bearer <TOKEN_A2A>` en todo POST/PUT/PATCH/DELETE;
GET /health y la ficha quedan públicos. Sin TOKEN_A2A configurado, el verificador rechaza todo
encargo con 503 y lo avisa al arrancar. El principal (delegar_verificador) manda el Bearer con
el mismo TOKEN_A2A; en Heroku, las dos apps tienen que tener el mismo valor.
"""

from fastapi import FastAPI

from src.comun.registro import configurar_registro
from src.comun.seguridad import proteger_con_token_a2a
from src.comun.servidor import registrar_agente
from src.verificador.agente import responder, responder_partes
from src.verificador.ficha import tarjeta

configurar_registro()

app = FastAPI(title="Verificador de boletas · Comercial Los Alerces SpA (ficticia)")


@app.get("/health")
async def health() -> dict[str, bool]:
    return {"ok": True}


registrar_agente(app, tarjeta, responder, responder_partes=responder_partes)
proteger_con_token_a2a(app)
