# api/

API FastAPI del agente principal (`app.py`): `GET /health`, `POST /chat` y `GET /registro/{id_ejecucion}`.
Formatos en [../docs/contratos.md](../docs/contratos.md) (sección 2).

- **Dueño:** compartido (cambios por acuerdo). Clave: `src/comun/seguridad.py` (Matías).
- **Hecho:** `/health`; la clave en `/chat` y `/registro` (401/503); 501 mientras falten el router o la tabla.
- **Falta:** nada propio; empieza a responder 200 cuando existan `src/principal/grafo.responder` (Alex) y `leer_ejecucion` (Sebastián).
