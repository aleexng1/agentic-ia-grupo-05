"""App FastAPI del verificador (agente especialista A2A), separada del principal.

Se levanta con:  uvicorn src.verificador.app:app --port 8001
En Heroku es una app aparte con APP_MODULE=src.verificador.app:app (ver docs/reparto.md).

- GET  /health                       chequeo de salud (público)
- GET  /.well-known/agent-card.json  ficha A2A (pública)
- POST /                             JSON-RPC A2A (protegido)

Protección PROVISORIA: proteger_app (X-API-Key con API_KEY_SERVICIO). El contrato final es
TOKEN_A2A: cuando esté unido el PR de Matías (proteger_con_token_a2a en src/comun/seguridad.py),
se cambia la última línea por `proteger_con_token_a2a(app)`. El cliente (delegar_verificador)
ya manda las dos cabeceras: X-API-Key y, si TOKEN_A2A tiene valor, Authorization: Bearer.
"""

from fastapi import FastAPI

from src.comun.registro import configurar_registro
from src.comun.seguridad import proteger_app
from src.comun.servidor import registrar_agente
from src.verificador.agente import responder, responder_partes
from src.verificador.ficha import tarjeta

configurar_registro()

app = FastAPI(title="Verificador de boletas · Comercial Los Alerces SpA (ficticia)")


@app.get("/health")
async def health() -> dict[str, bool]:
    return {"ok": True}


registrar_agente(app, tarjeta, responder, responder_partes=responder_partes)
proteger_app(app)
