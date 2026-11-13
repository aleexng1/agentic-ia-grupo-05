"""Configuración común de las pruebas: una clave de acceso falsa, nunca la real."""

import pytest


CLAVE_DE_PRUEBA = "clave-de-prueba-solo-para-pytest"


@pytest.fixture(autouse=True)
def clave_de_acceso_de_prueba(monkeypatch):
    """Define CLAVE_API para cada prueba, sin depender del .env de quien las corre.

    Las pruebas que necesitan otro valor (vacío, por ejemplo) lo cambian con monkeypatch.
    """
    monkeypatch.setenv("CLAVE_API", CLAVE_DE_PRUEBA)
