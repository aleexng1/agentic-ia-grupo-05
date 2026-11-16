"""Ninguna prueba debe tocar la base compartida del curso.

src/config.py y src/memoria.py cargan .env al importarse, así que DATABASE_URL llegaría a las pruebas.
Esta fixture la quita en cada prueba; la que necesite una URL la fija ella misma con monkeypatch.
"""

import pytest


@pytest.fixture(autouse=True)
def sin_base_de_datos(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DB_SCHEMA", raising=False)
