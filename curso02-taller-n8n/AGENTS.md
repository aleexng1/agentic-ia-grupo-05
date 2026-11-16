# AGENTS.md · reglas del taller

Reglas para cualquier persona o agente de código que trabaje en `curso02-taller-n8n/`.
Todo se ejecuta **desde esta carpeta** y con el entorno `.venv` activo (`source .venv/bin/activate`).

## Estructura

```
curso02-taller-n8n/
├── main.py              # CLI: ejecuta un agente
├── api/app.py           # API FastAPI
├── src/{nombre_agente}/
│   ├── graph.py         # estado, nodos y aristas
│   ├── prompts.py       # TODOS los prompts y reglas
│   └── tools.py         # herramientas del agente
├── scripts/             # scripts de apoyo (evaluaciones, utilidades)
├── tests/               # pruebas con pytest
└── bruno/               # colección de Bruno para probar la API
```

## Agentes

- Cada agente vive en `src/{nombre_agente}/` con `graph.py`, `prompts.py` y `tools.py`.
- Cada nodo tiene su prompt en `prompts.py`. **No se escriben reglas ni textos de prompt dentro de `graph.py`**: el grafo solo importa los prompts.
- La configuración (`GOOGLE_API_KEY`, `MODELO`, `PUBLIC_URL`) se lee desde `.env`. Nunca se escriben claves en el código.

## Ejecutar

```bash
python main.py {nombre_agente} "mensaje"             # ejecuta el agente
python main.py {nombre_agente} "mensaje" --saltos    # además imprime los nodos recorridos
python main.py {nombre_agente} --diagrama            # imprime el diagrama Mermaid sin ejecutar
```

## API

```bash
uvicorn api.app:app --reload --port 8000
```

La documentación interactiva queda en http://localhost:8000/docs.

## Scripts y pruebas

- Los scripts van en `scripts/`.
- Las pruebas van en `tests/` y se corren con `pytest`.

## Despliegue

- `Procfile`: `web: uvicorn api.app:app --host 0.0.0.0 --port $PORT`
- `.python-version`: `3.12`
- `requirements.txt` al día (regenerar con `pip freeze > requirements.txt` cuando se agregue una dependencia).

## Base de datos

- La base Postgres es compartida por todo el curso y el usuario de `DATABASE_URL` puede escribir en todo. Nunca se imprime, registra ni copia la URL, su clave ni el servidor.
- Las tablas propias (memoria) van solo en el esquema de `DB_SCHEMA` (por defecto `alex_nail`). No se crea, modifica ni borra nada en `public`, `catalogo` ni `alumnoNN`.
- `catalogo.productos_unicos` se consulta **solo** con `src/router/catalogo.py` (`consultar`): solo SELECT, con parámetros, en conexión de solo lectura y como máximo 1 conexión a la vez.
- Los reclamos de postventa van en la tabla `reclamos` del esquema propio (`src/router/reclamos.py`), con el pool de la memoria: entre memoria, catálogo y reclamos nunca más de 3 conexiones a la vez.
