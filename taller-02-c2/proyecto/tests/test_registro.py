"""Registro de una consulta del coordinador, sin llamar a Gemini ni a la red."""

import asyncio
import logging

import pytest

from src.comun import registro as modulo_registro
from src.coordinador import graph as modulo_graph


class _Captura(logging.Handler):
    """Guarda los mensajes del registro del coordinador."""

    def __init__(self):
        super().__init__()
        self.lineas = []

    def emit(self, record):
        self.lineas.append(record.getMessage())


@pytest.fixture
def lineas():
    registro = modulo_registro.obtener_registro()
    captura = _Captura()
    nivel_anterior = registro.level
    registro.addHandler(captura)
    registro.setLevel(logging.INFO)
    yield captura.lineas
    registro.removeHandler(captura)
    registro.setLevel(nivel_anterior)


def _preparar(monkeypatch, preguntar_falso):
    """Grafo real con un supervisor y un envío A2A de mentira."""
    catalogo = [
        {
            "nombre": "Agente de Alex",
            "descripcion": "Lugares y capacidad.",
            "cliente": object(),
            "url": "http://127.0.0.1:8000/agentes/alex",
        }
    ]

    class _SupervisorFalso:
        def with_structured_output(self, esquema):
            class _Estructurado:
                async def ainvoke(self, mensajes):
                    return esquema(
                        agente="Agente de Alex",
                        motivo="Pregunta por recintos\ny capacidad.",
                    )

            return _Estructurado()

    async def _sin_descubrir(imprimir=False):
        return None

    monkeypatch.setattr(modulo_graph, "_MODELO_SUPERVISOR", _SupervisorFalso())
    monkeypatch.setattr(modulo_graph, "preguntar", preguntar_falso)
    monkeypatch.setattr(modulo_graph, "inicializar_supervisor", _sin_descubrir)
    monkeypatch.setattr(modulo_graph, "graph", modulo_graph._crear_grafo(catalogo))


def test_registro_de_una_consulta_exitosa(monkeypatch, lineas):
    async def _preguntar(cliente, texto, context_id):
        return "Hay tres recintos."

    _preparar(monkeypatch, _preguntar)
    pregunta = "¿Dónde hago una feria tecnológica para 150 personas? " * 5
    resultado = asyncio.run(modulo_graph.responder_detallado(pregunta, "ctx-1"))

    assert resultado["respuesta"] == "Hay tres recintos."
    assert len(lineas) == 4
    assert lineas[0].startswith("pregunta recibida · context_id=ctx-1 · «")
    assert len(lineas[0].split("«", 1)[1].rstrip("»")) <= 80
    assert lineas[1] == "supervisor eligió Agente de Alex · motivo: Pregunta por recintos y capacidad."
    assert lineas[2] == "A2A → http://127.0.0.1:8000/agentes/alex · enviando"
    assert lineas[3].startswith("A2A ← Agente de Alex · respuesta recibida en ")
    assert lineas[3].endswith(" s") and "," in lineas[3]


def test_registro_de_un_error_a2a(monkeypatch, lineas):
    async def _preguntar(cliente, texto, context_id):
        raise TimeoutError("La tarea A2A no terminó\nen 60 segundos.")

    _preparar(monkeypatch, _preguntar)
    asyncio.run(modulo_graph.responder("¿Dónde hago la feria?", "ctx-2"))

    assert lineas[-1] == "A2A ✗ Agente de Alex · error: La tarea A2A no terminó en 60 segundos."


def test_configurar_registro_no_duplica_manejadores():
    registro = modulo_registro.configurar_registro()
    cantidad = len(registro.handlers)
    modulo_registro.configurar_registro()
    assert len(registro.handlers) == cantidad


def test_formato_de_segundos_y_recorte():
    assert modulo_registro.segundos(2.345) == "2,3 s"
    assert modulo_registro.recortar("a" * 100) == "a" * 79 + "…"
    assert modulo_registro.recortar("hola\nmundo") == "hola mundo"
