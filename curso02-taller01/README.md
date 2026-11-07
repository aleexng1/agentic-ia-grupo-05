# Curso 2 · Taller 1 (pruebas personales)

Esta rama es solo de Alex. No se mergea a main ni se abre PR.

## Versiones instaladas

- a2a-sdk: 1.3.0 (instalado con el extra `[fastapi]`)

## Página para ver los agentes (extra, solo local)

Lista los agentes leyendo sus fichas y permite conversar con ellos. Corre solo en
`127.0.0.1`. Los agentes se levantan aparte (puertos 8000, 8001 y 8002).

```
source .venv/bin/activate
uvicorn src.web.app:app --host 127.0.0.1 --port 8080
```

Abrir http://127.0.0.1:8080. Pruebas (sin red): `python -m pytest tests`.
