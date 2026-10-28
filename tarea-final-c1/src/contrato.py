"""Contrato del proyecto: los tipos de datos que comparten todos los módulos.

ARCHIVO COMPARTIDO: no se cambia sin acuerdo del grupo (ver AGENTS.md).
Si cambias un nombre aquí, se rompe el trabajo de las otras personas.
"""

from typing import Annotated, Literal, NotRequired, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

# Máximo de vueltas del ciclo ReAct (LLM → herramienta → LLM ...) por turno.
MAX_PASOS = 6

# Las únicas tres decisiones que el agente puede tomar sobre un gasto.
DECISIONES = ("aprobar", "observar", "rechazar")

# Tipos de documento que puede traer un gasto.
TIPOS_DOCUMENTO = ("boleta", "factura", "voucher")

Decision = Literal["aprobar", "observar", "rechazar"]
TipoDocumento = Literal["boleta", "factura", "voucher"]


# ---------------------------------------------------------------------------
# Tipos de datos
# ---------------------------------------------------------------------------


# Un gasto rendido por un trabajador, tal como llega al agente.
class Gasto(TypedDict):
    id: str
    fecha_gasto: str  # AAAA-MM-DD, día en que se hizo el gasto
    fecha_rendicion: str  # AAAA-MM-DD, día en que se rindió
    monto: int  # pesos chilenos (CLP), sin decimales
    tipo_documento: TipoDocumento
    proveedor: str
    glosa: str  # descripción escrita por el trabajador
    politica_declarada: str  # política que eligió el trabajador
    categoria_declarada: str  # categoría que eligió el trabajador
    unidad_negocio: str  # código de la unidad: TIE, CD, TMA, CAF, OYM o ADM
    patente: NotRequired[str | None]  # opcional: obligatoria en P04 y P05
    numero_ot: NotRequired[str | None]  # opcional: número de orden de trabajo, obligatorio en P06
    vb_gerente_general: NotRequired[bool]  # opcional: visto bueno del Gerente General (RG-03)
    id_fondo: str  # fondo por rendir del que sale el dinero


# Un trozo de la política de gastos que encontró la búsqueda (RAG).
class Fragmento(TypedDict):
    politica: str
    texto: str
    fuente: str  # de dónde salió (archivo y sección)
    puntaje: float  # parecido con la consulta: mayor = más parecido


# Resultado del paso 1: qué política, categoría y cuenta corresponden al gasto.
class Clasificacion(TypedDict):
    politica: str
    categoria: str
    cuenta: str
    coincide_con_declarada: bool  # ¿el trabajador eligió bien?
    razon: str
    fragmentos: list[Fragmento]  # trozos de política que respaldan la decisión


# Una regla que el gasto no cumple, con el detalle de por qué.
class Incumplimiento(TypedDict):
    regla: str
    detalle: str


# Resultado del paso 2: revisión del gasto con reglas exactas.
class Validacion(TypedDict):
    cumple: bool
    incumplimientos: list[Incumplimiento]
    cuenta: str  # cuenta contable que corresponde a la política y categoría


# Decisión final del agente sobre el gasto, con su explicación.
class Veredicto(TypedDict):
    decision: Decision
    motivo: str  # qué regla se aplicó y por qué
    politica_sugerida: str
    categoria_sugerida: str
    cuenta_sugerida: str


# Estado del fondo por rendir: cuánto dinero queda y qué gastos se aprobaron.
class EstadoFondo(TypedDict):
    id_fondo: str
    responsable: str
    saldo_inicial: int
    saldo_actual: int
    gastos_aprobados: list[str]  # ids de los gastos aprobados


# Estado que LangGraph guarda y pasa entre los nodos del grafo.
class EstadoAgente(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]  # historial de la conversación
    gasto: NotRequired[Gasto | None]
    clasificacion: NotRequired[Clasificacion | None]
    validacion: NotRequired[Validacion | None]
    veredicto: NotRequired[Veredicto | None]
    fondo: NotRequired[EstadoFondo | None]
    pasos: NotRequired[int]  # vueltas del ciclo en este turno (condición de parada)
