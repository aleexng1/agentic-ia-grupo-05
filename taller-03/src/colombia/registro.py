import logging
from pathlib import Path

RUTA_LOG = Path(__file__).resolve().parents[2] / "logs" / "guardrails.log"

_logger = logging.getLogger("guardrails")
if not _logger.handlers:
    RUTA_LOG.parent.mkdir(exist_ok=True)
    manejador = logging.FileHandler(RUTA_LOG, encoding="utf-8")
    manejador.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
    _logger.addHandler(manejador)
    _logger.setLevel(logging.INFO)


def registrar(nodo: str, categoria: str, motivo: str, nivel: int = logging.INFO) -> None:
    """Una línea por evento. Nunca se pasa el texto del usuario."""
    _logger.log(nivel, "%s | %s | %s", nodo, categoria, motivo)
