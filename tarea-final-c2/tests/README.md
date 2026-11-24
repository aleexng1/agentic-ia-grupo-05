# tests/

Pruebas de humo sin red ni Gemini. Se corren desde `tarea-final-c2/` con `python -m pytest`.
`conftest.py` (de taller-02-c2) pone una clave falsa en `API_KEY_SERVICIO`.

- **Dueño:** compartido. Cada uno suma las pruebas de su parte.
- **Ojo:** `test_chat_sin_router_responde_501` se cambia cuando exista el router.
