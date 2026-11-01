"""Juez del contrato: revisa que el proyecto respete lo que acordó el grupo.

Uso (desde la carpeta tarea-final-c1):
    python verificar.py            → revisión sin clave de API (la que exige /subir-cambios)
    python verificar.py --con-llm  → además conversa con el agente real (usa la clave del .env)

Muestra ✅ o ❌ por cada punto y termina con error si algo falla.
ARCHIVO COMPARTIDO: no se cambia sin acuerdo del grupo (ver AGENTS.md).
"""

import argparse
import contextlib
import copy
import csv
import functools
import importlib
import inspect
import io
import json
import re
import sys
from datetime import date
from pathlib import Path
from unittest import mock

CARPETA = Path(__file__).resolve().parent
sys.path.insert(0, str(CARPETA))
RUTA_POLITICA = CARPETA / "datos" / "politica_ficticia.md"

# Lista de resultados: True = pasó, False = falló.
resultados: list[bool] = []

# Módulos de src/ que se importan en el bloque 1.
modulos: dict = {}


def punto(nombre: str, revision, opcional_sin_servicios: bool = False) -> None:
    """Ejecuta una revisión y muestra ✅ o ❌.

    La revisión es una función que no devuelve nada (o un detalle corto) si todo
    está bien, y lanza un error con la explicación si algo está mal.
    Si `opcional_sin_servicios` es True y no estamos en modo --con-llm, un error
    se muestra como ⚠️ (omitido) porque esa parte necesita Redis o la clave de API.
    """
    try:
        detalle = revision()
        resultados.append(True)
        print(f"✅ {nombre}" + (f" — {detalle}" if detalle else ""))
    except Exception as error:  # noqa: BLE001 (queremos mostrar cualquier error)
        # Errores de formato (AssertionError, TypeError, ValueError...) siempre son ❌.
        error_de_formato = isinstance(error, (AssertionError, TypeError, KeyError, ValueError))
        if opcional_sin_servicios and not CON_LLM and not error_de_formato:
            print(f"⚠️  {nombre} — omitido: necesita Redis o clave de API ({type(error).__name__}: {error})")
            print("    Se revisa de verdad con: python verificar.py --con-llm")
            return
        resultados.append(False)
        print(f"❌ {nombre}\n    → {type(error).__name__}: {error}")


def exigir(condicion: bool, mensaje: str) -> None:
    """Lanza un error con `mensaje` si la condición no se cumple."""
    if not condicion:
        raise AssertionError(mensaje)


def titulo(texto: str) -> None:
    print(f"\n=== {texto} ===")


# ---------------------------------------------------------------------------
# Datos de ejemplo (ficticios) para llamar a las funciones
# ---------------------------------------------------------------------------

GASTO_EJEMPLO = {
    "id": "G-VERIF",
    "fecha_gasto": "2026-10-02",
    "fecha_rendicion": "2026-10-06",
    "monto": 45000,
    "tipo_documento": "boleta",
    "proveedor": "Estación de Servicio El Roble",
    "glosa": "Bencina auto propio para visitar tiendas de Temuco",
    "politica_declarada": "Vehículos Propios",
    "categoria_declarada": "Gasolina (vehículo propio)",
    "unidad_negocio": "TIE",
    "patente": None,
    "numero_ot": None,
    "vb_gerente_general": False,
    "id_fondo": "FR-001",
}

FRAGMENTO_EJEMPLO = {
    "politica": "Vehículos Propios",
    "texto": "Bono de Traslado | Gasolina (vehículo propio) | CTA-5100.",
    "fuente": "datos/politica_ficticia.md#P01",
    "puntaje": 0.9,
}

CLASIFICACION_EJEMPLO = {
    "politica": "Vehículos Propios",
    "categoria": "Gasolina (vehículo propio)",
    "cuenta": "CTA-5100",
    "coincide_con_declarada": True,
    "razon": "Bencina del auto propio para un traslado de trabajo.",
    "fragmentos": [FRAGMENTO_EJEMPLO],
}

VEREDICTO_EJEMPLO = {
    "decision": "aprobar",
    "motivo": "Cumple todas las reglas.",
    "politica_sugerida": "Vehículos Propios",
    "categoria_sugerida": "Gasolina (vehículo propio)",
    "cuenta_sugerida": "CTA-5100",
}

# Claves que debe tener cada tipo del contrato (src/contrato.py).
CLAVES_CONTRATO = {
    "Gasto": {
        "id", "fecha_gasto", "fecha_rendicion", "monto", "tipo_documento", "proveedor", "glosa",
        "politica_declarada", "categoria_declarada", "unidad_negocio", "patente", "numero_ot",
        "vb_gerente_general", "id_fondo",
    },
    "Fragmento": {"politica", "texto", "fuente", "puntaje"},
    "Clasificacion": {"politica", "categoria", "cuenta", "coincide_con_declarada", "razon", "fragmentos"},
    "Incumplimiento": {"regla", "detalle"},
    "Validacion": {"cumple", "incumplimientos", "cuenta"},
    "Veredicto": {"decision", "motivo", "politica_sugerida", "categoria_sugerida", "cuenta_sugerida"},
    "EstadoFondo": {"id_fondo", "responsable", "saldo_inicial", "saldo_actual", "gastos_aprobados"},
    "EstadoAgente": {"messages", "gasto", "clasificacion", "validacion", "veredicto", "fondo", "pasos"},
}

# Funciones acordadas: (módulo, nombre) → parámetros en orden.
FIRMAS = {
    ("config", "obtener_llm"): [],
    ("config", "registrar_traza"): ["evento", "datos"],
    ("herramientas", "validar_gasto"): ["gasto", "politica", "categoria"],
    ("rag", "buscar_politica"): ["consulta", "k"],
    ("memoria", "fondo_inicial"): ["id_fondo"],
    ("memoria", "aplicar_veredicto"): ["fondo", "gasto", "veredicto"],
    ("memoria", "resumen_fondo"): ["fondo"],
    ("registro", "registrar_veredicto"): ["gasto", "veredicto"],
    ("registro", "reiniciar_registro"): [],
    ("seguridad", "juzgar"): ["gasto", "clasificacion", "veredicto"],
    ("grafo", "construir_agente"): [],
    ("grafo", "conversar"): ["agente", "mensaje", "hilo"],
    ("grafo", "emitir_veredicto"): ["decision", "politica", "categoria", "cuenta", "motivo"],
}

# Estas dos son herramientas de LangChain (@tool), el LLM las puede pedir.
HERRAMIENTAS = {
    ("herramientas", "validar_gasto"),
    ("rag", "buscar_politica"),
    ("grafo", "emitir_veredicto"),
}

# Campos del Gasto que pueden faltar (NotRequired en el contrato).
CAMPOS_OPCIONALES_GASTO = {"patente", "numero_ot", "vb_gerente_general"}

# Formato del golden set (ver pruebas/README.md).
CAMPOS_CASO_GOLDEN = {"id", "grupo", "origen", "descripcion", "componentes", "turnos", "criterio"}
GRUPOS_GOLDEN = ("A-limpio", "B-mal-clasificado", "C-regla", "D-fondo", "E-seguridad", "F-conversacion")
ORIGENES_GOLDEN = ("patron_real", "mutacion", "diseñado")
LISTAS_ESPERADO = (
    "reglas", "debe_contener", "debe_contener_alguno",
    "herramientas_esperadas", "herramientas_prohibidas", "acciones_prohibidas",
)


# ---------------------------------------------------------------------------
# Ayudas para revisar formatos
# ---------------------------------------------------------------------------


def revisar_claves(datos, tipo: str) -> None:
    """Revisa que `datos` sea un diccionario con exactamente las claves del tipo del contrato."""
    exigir(isinstance(datos, dict), f"{tipo} debe ser un diccionario, llegó {type(datos).__name__}")
    esperadas = CLAVES_CONTRATO[tipo]
    obligatorias = esperadas - CAMPOS_OPCIONALES_GASTO if tipo == "Gasto" else esperadas
    faltan = obligatorias - set(datos)
    sobran = set(datos) - esperadas
    exigir(not faltan, f"{tipo}: faltan las claves {sorted(faltan)}")
    exigir(not sobran, f"{tipo}: sobran claves que no están en el contrato {sorted(sobran)}")


def revisar_gasto(gasto: dict, donde: str) -> None:
    """Revisa que un gasto tenga las claves y los formatos acordados."""
    contrato = modulos["contrato"]
    revisar_claves(gasto, "Gasto")
    for campo in ("fecha_gasto", "fecha_rendicion"):
        try:
            date.fromisoformat(gasto[campo])
        except (TypeError, ValueError):
            raise AssertionError(f"{donde}: {campo}='{gasto[campo]}' no es una fecha AAAA-MM-DD") from None
    monto = gasto["monto"]
    exigir(isinstance(monto, int) and not isinstance(monto, bool), f"{donde}: monto debe ser entero (CLP)")
    exigir(
        gasto["tipo_documento"] in contrato.TIPOS_DOCUMENTO,
        f"{donde}: tipo_documento='{gasto['tipo_documento']}' no es uno de {contrato.TIPOS_DOCUMENTO}",
    )
    exigir(
        isinstance(gasto.get("numero_ot"), (str, type(None))), f"{donde}: numero_ot debe ser texto o vacío"
    )
    exigir(
        isinstance(gasto.get("vb_gerente_general", False), bool),
        f"{donde}: vb_gerente_general debe ser true o false",
    )
    unidades = leer_politica()["unidades"]
    exigir(
        gasto["unidad_negocio"] in unidades,
        f"{donde}: unidad_negocio='{gasto['unidad_negocio']}' no es uno de {sorted(unidades)}",
    )
    revisar_politica_categoria(gasto["politica_declarada"], gasto["categoria_declarada"], donde)


@functools.cache
def leer_politica() -> dict:
    """Lee datos/politica_ficticia.md y devuelve lo que se usa para comparar nombres.

    - "politicas": {nombre de política: {categoría: cuenta}}, de los títulos '## P01 — <nombre>'
      y de sus tablas Grupo / Categoría / Cuenta.
    - "unidades": códigos de la tabla de unidades de negocio (TIE, CD, ...).
    - "secciones": todos los títulos '## ...' (sin el código Pxx), por ejemplo "Reglas generales".
    - "codigos": {código de política: nombre}, por ejemplo {"P01": "Vehículos Propios"}.
    - "reglas": códigos de las reglas generales escritas como '**RG-01 — ...'.
    """
    texto = RUTA_POLITICA.read_text(encoding="utf-8")
    politicas, unidades, secciones, codigos = {}, set(), set(), {}
    reglas = set(re.findall(r"^\*\*(RG-\d{2})", texto, flags=re.MULTILINE))
    seccion_actual, en_tabla_unidades = None, False
    for linea in texto.splitlines():
        if linea.startswith("#"):
            # Un título nuevo: vemos si es una política, la tabla de unidades u otra sección.
            titulo = re.match(r"^## (?:P\d{2} — )?(.+)$", linea)
            if titulo:
                secciones.add(titulo.group(1).strip())
            politica = re.match(r"^## (P\d{2}) — (.+)$", linea)
            if politica:
                codigos[politica.group(1)] = politica.group(2).strip()
            seccion_actual = politicas.setdefault(politica.group(2).strip(), {}) if politica else None
            en_tabla_unidades = linea.startswith("### Unidades de negocio")
        elif fila := re.match(r"^\|[^|]+\|([^|]+)\|\s*(CTA-\d{4})\s*\|$", linea):
            if seccion_actual is not None:
                seccion_actual[fila.group(1).strip()] = fila.group(2)
        elif en_tabla_unidades and (fila := re.match(r"^\|\s*([A-Z]{2,4})\s*\|", linea)):
            unidades.add(fila.group(1))
    return {"politicas": politicas, "unidades": unidades, "secciones": secciones, "codigos": codigos, "reglas": reglas}


def revisar_politica_categoria(politica: str, categoria: str, donde: str) -> None:
    """Revisa que la política exista y que la categoría sea de esa política (nombres exactos)."""
    politicas = leer_politica()["politicas"]
    exigir(politica in politicas, f"{donde}: la política '{politica}' no existe. Válidas: {sorted(politicas)}")
    exigir(
        categoria in politicas[politica],
        f"{donde}: '{categoria}' no es una categoría de '{politica}'. Válidas: {sorted(politicas[politica])}",
    )


def revisar_turno_golden(turno: dict, donde: str) -> None:
    """Revisa un turno del golden set: gasto válido, decisión permitida y nombres que existen."""
    exigir("mensaje" in turno or "gasto" in turno, f"{donde}: el turno necesita 'mensaje' o 'gasto'")
    esperado = turno.get("esperado")
    exigir(isinstance(esperado, dict), f"{donde}: falta 'esperado'")
    if "gasto" in turno:
        revisar_gasto(turno["gasto"], donde)
        decisiones = modulos["contrato"].DECISIONES
        exigir(esperado.get("decision") in decisiones, f"{donde}: decision '{esperado.get('decision')}' no es una de {decisiones}")
    if "politica" in esperado:
        # En "esperado" la política va con su código (P02) y debe calzar con categoría y cuenta.
        codigos = leer_politica()["codigos"]
        exigir(esperado["politica"] in codigos, f"{donde}: política '{esperado['politica']}' no es un código {sorted(codigos)}")
        nombre = codigos[esperado["politica"]]
        revisar_politica_categoria(nombre, esperado.get("categoria"), f"{donde} (esperado)")
        cuenta = leer_politica()["politicas"][nombre][esperado["categoria"]]
        exigir(esperado.get("cuenta") == cuenta, f"{donde}: la cuenta de '{esperado['categoria']}' es {cuenta}, no {esperado.get('cuenta')}")
    for lista in LISTAS_ESPERADO:
        exigir(isinstance(esperado.get(lista, []), list), f"{donde}: '{lista}' debe ser una lista")
    # Reglas: RG-xx de las reglas generales o Pxx (regla propia de una política).
    validas = leer_politica()["reglas"] | set(leer_politica()["codigos"])
    for regla in esperado.get("reglas", []):
        exigir(regla in validas, f"{donde}: la regla '{regla}' no existe en la política")
    # Herramientas: deben ser nombres de funciones acordadas en src/ (ver FIRMAS).
    conocidas = {nombre for _, nombre in FIRMAS}
    for lista in ("herramientas_esperadas", "herramientas_prohibidas"):
        for herramienta in esperado.get(lista, []):
            exigir(herramienta in conocidas, f"{donde}: '{herramienta}' no es una función de src/")


def cuentas_validas() -> set:
    """Todas las cuentas contables (CTA-xxxx) que aparecen en las tablas de la política."""
    return {cuenta for categorias in leer_politica()["politicas"].values() for cuenta in categorias.values()}


def funcion_real(objeto):
    """Si es una herramienta @tool, devuelve la función de Python que tiene adentro."""
    return getattr(objeto, "func", None) or objeto


@contextlib.contextmanager
def silencio():
    """Esconde lo que imprimen las funciones (por ejemplo las trazas) para no ensuciar el resumen."""
    with contextlib.redirect_stdout(io.StringIO()):
        yield


# ---------------------------------------------------------------------------
# LLM falso: imita al modelo para probar el grafo SIN internet ni clave.
# Si el Núcleo usa otras funciones del LLM (por ejemplo with_structured_output),
# hay que agregarlas aquí, con acuerdo del grupo.
# ---------------------------------------------------------------------------


class LLMFalso:
    """Valida el gasto y cierra con emitir_veredicto, sin respuestas finales en texto."""

    def __init__(self, siempre_pide_herramienta: bool = False):
        self.siempre_pide_herramienta = siempre_pide_herramienta
        self.llamadas = 0

    def bind_tools(self, herramientas, **opciones):
        return self

    def invoke(self, mensajes, *args, **opciones):
        from langchain_core.messages import AIMessage, ToolMessage

        self.llamadas += 1
        # Freno de seguridad: si el grafo no para solo, cortamos aquí con un error claro.
        if self.llamadas > 3 * modulos["contrato"].MAX_PASOS:
            raise AssertionError(f"el grafo no se detuvo: llamó al LLM {self.llamadas} veces")
        recien_observo = isinstance(mensajes[-1], ToolMessage)
        if self.siempre_pide_herramienta or not recien_observo:
            pedido = {
                "name": "validar_gasto",
                "args": {
                    "gasto": GASTO_EJEMPLO,
                    "politica": CLASIFICACION_EJEMPLO["politica"],
                    "categoria": CLASIFICACION_EJEMPLO["categoria"],
                },
                "id": f"llamada-{self.llamadas}",
                "type": "tool_call",
            }
            return AIMessage("", tool_calls=[pedido])
        if mensajes[-1].name == "validar_gasto":
            pedido = {
                "name": "emitir_veredicto",
                "args": {
                    "decision": VEREDICTO_EJEMPLO["decision"],
                    "politica": "P01",
                    "categoria": CLASIFICACION_EJEMPLO["categoria"],
                    "cuenta": CLASIFICACION_EJEMPLO["cuenta"],
                    "motivo": VEREDICTO_EJEMPLO["motivo"],
                },
                "id": f"emitir-{self.llamadas}",
                "type": "tool_call",
            }
            return AIMessage("", tool_calls=[pedido])
        return AIMessage("El veredicto ya se emitió como herramienta.")


@contextlib.contextmanager
def usar_llm(llm):
    """Hace que construir_agente() use `llm` en vez del Gemini real."""
    with contextlib.ExitStack() as pila:
        for nombre_modulo in ("config", "grafo"):
            if hasattr(modulos[nombre_modulo], "obtener_llm"):
                pila.enter_context(mock.patch.object(modulos[nombre_modulo], "obtener_llm", lambda: llm))
        yield


# ---------------------------------------------------------------------------
# Bloques de revisión
# ---------------------------------------------------------------------------


def bloque_1_importar() -> None:
    # ¿Se pueden cargar todos los archivos de src/ sin errores?
    titulo("1. Importar los módulos de src/")
    for nombre in ("contrato", "config", "herramientas", "rag", "memoria", "registro", "seguridad", "grafo"):

        def importar(nombre=nombre):
            modulos[nombre] = importlib.import_module(f"src.{nombre}")

        punto(f"src/{nombre}.py se importa", importar)


def bloque_2_contrato() -> None:
    # ¿src/contrato.py tiene los tipos y constantes acordados, con las claves exactas?
    titulo("2. Contrato (src/contrato.py)")

    def constantes():
        contrato = modulos["contrato"]
        exigir(contrato.MAX_PASOS == 6, f"MAX_PASOS debe ser 6, es {contrato.MAX_PASOS}")
        exigir(
            tuple(contrato.DECISIONES) == ("aprobar", "observar", "rechazar"),
            f"DECISIONES debe ser ('aprobar', 'observar', 'rechazar'), es {contrato.DECISIONES}",
        )

    punto("MAX_PASOS y DECISIONES", constantes)

    for tipo, claves in CLAVES_CONTRATO.items():

        def revisar_tipo(tipo=tipo, claves=claves):
            definidas = set(getattr(modulos["contrato"], tipo).__annotations__)
            exigir(definidas == claves, f"claves distintas: sobran {definidas - claves}, faltan {claves - definidas}")

        punto(f"tipo {tipo}", revisar_tipo)


def bloque_3_firmas() -> None:
    # ¿Existen las funciones con esos nombres y parámetros exactos?
    titulo("3. Firmas de las funciones")
    from langchain_core.tools import BaseTool

    for (nombre_modulo, nombre), parametros in FIRMAS.items():

        def revisar_firma(nombre_modulo=nombre_modulo, nombre=nombre, parametros=parametros):
            objeto = getattr(modulos[nombre_modulo], nombre, None)
            exigir(objeto is not None, f"no existe {nombre} en src/{nombre_modulo}.py")
            if (nombre_modulo, nombre) in HERRAMIENTAS:
                exigir(isinstance(objeto, BaseTool), f"{nombre} debe ser una herramienta (@tool)")
                exigir(objeto.name == nombre, f"la herramienta debe llamarse '{nombre}', se llama '{objeto.name}'")
            reales = list(inspect.signature(funcion_real(objeto)).parameters)
            exigir(reales == parametros, f"parámetros {reales}, se esperaban {parametros}")

        punto(f"{nombre_modulo}.{nombre}({', '.join(parametros)})", revisar_firma)

    def prompt():
        texto = getattr(modulos["seguridad"], "PROMPT_SISTEMA", None)
        exigir(isinstance(texto, str) and texto.strip(), "PROMPT_SISTEMA debe ser un texto no vacío")

    punto("seguridad.PROMPT_SISTEMA", prompt)


def bloque_4_llamadas() -> None:
    # Llama a cada función con el gasto de ejemplo y revisa que devuelva lo acordado.
    titulo("4. Llamadas con un gasto de ejemplo")
    herramientas, rag, memoria = modulos["herramientas"], modulos["rag"], modulos["memoria"]
    registro, seguridad, config = modulos["registro"], modulos["seguridad"], modulos["config"]

    def traza():
        with silencio():
            config.registrar_traza("verificar", {"gasto": GASTO_EJEMPLO["id"]})

    punto("registrar_traza no falla", traza)

    def validar():
        resultado = herramientas.validar_gasto.invoke(
            {
                "gasto": GASTO_EJEMPLO,
                "politica": CLASIFICACION_EJEMPLO["politica"],
                "categoria": CLASIFICACION_EJEMPLO["categoria"],
            }
        )
        revisar_claves(resultado, "Validacion")
        exigir(isinstance(resultado["cumple"], bool), "cumple debe ser True o False")
        exigir(resultado["cuenta"] in cuentas_validas(), f"la cuenta '{resultado['cuenta']}' no está en la política")
        exigir(isinstance(resultado["incumplimientos"], list), "incumplimientos debe ser una lista")
        for incumplimiento in resultado["incumplimientos"]:
            revisar_claves(incumplimiento, "Incumplimiento")
        return f"cumple={resultado['cumple']}, cuenta={resultado['cuenta']}"

    punto("validar_gasto devuelve una Validacion", validar)

    def buscar():
        resultado = rag.buscar_politica.invoke({"consulta": "bencina auto propio visita a tiendas", "k": 3})
        exigir(isinstance(resultado, list) and resultado, "debe devolver una lista con al menos un Fragmento")
        exigir(len(resultado) <= 3, f"pidió k=3 y devolvió {len(resultado)}")
        secciones = leer_politica()["secciones"]
        for fragmento in resultado:
            revisar_claves(fragmento, "Fragmento")
            exigir(
                fragmento["politica"] in secciones,
                f"politica='{fragmento['politica']}' no es un título de la política. Válidos: {sorted(secciones)}",
            )
        return f"{len(resultado)} fragmento(s), primero: {resultado[0]['politica']}"

    punto("buscar_politica devuelve Fragmentos", buscar, opcional_sin_servicios=True)

    def fondo():
        inicial = memoria.fondo_inicial("FR-001")
        revisar_claves(inicial, "EstadoFondo")
        exigir(inicial["id_fondo"] == "FR-001", "el fondo devuelto debe tener el id pedido")
        copia = copy.deepcopy(inicial)
        nuevo = memoria.aplicar_veredicto(inicial, GASTO_EJEMPLO, VEREDICTO_EJEMPLO)
        revisar_claves(nuevo, "EstadoFondo")
        exigir(inicial == copia, "aplicar_veredicto no debe modificar el fondo recibido (debe devolver uno nuevo)")
        resumen = memoria.resumen_fondo(nuevo)
        exigir(isinstance(resumen, str) and resumen.strip(), "resumen_fondo debe devolver un texto")
        return resumen

    punto("memoria del fondo (fondo_inicial, aplicar_veredicto, resumen_fondo)", fondo)

    def registrar():
        exigir(registro.reiniciar_registro() is None, "reiniciar_registro no debe devolver nada")
        resultado = registro.registrar_veredicto(GASTO_EJEMPLO, VEREDICTO_EJEMPLO)
        exigir(isinstance(resultado, dict), "registrar_veredicto debe devolver un diccionario")
        exigir({"antes", "despues"} <= set(resultado), "debe incluir las claves 'antes' y 'despues'")
        registro.reiniciar_registro()  # dejar la base de prueba limpia
        return f"antes={resultado['antes']} → despues={resultado['despues']}"

    punto("registro de veredictos (registrar_veredicto, reiniciar_registro)", registrar)

    def juez():
        resultado = seguridad.juzgar(GASTO_EJEMPLO, CLASIFICACION_EJEMPLO, VEREDICTO_EJEMPLO)
        exigir(isinstance(resultado, dict), "juzgar debe devolver un diccionario")
        exigir(set(resultado) >= {"valido", "razon"}, "debe incluir las claves 'valido' y 'razon'")
        exigir(isinstance(resultado["valido"], bool), "valido debe ser True o False")
        return f"valido={resultado['valido']}"

    punto("juzgar devuelve {valido, razon}", juez, opcional_sin_servicios=True)


def bloque_5_datos() -> None:
    # ¿datos/ y pruebas/ tienen el formato acordado?
    titulo("5. Formato de datos/ y pruebas/")
    contrato = modulos["contrato"]

    def politica():
        texto = RUTA_POLITICA.read_text(encoding="utf-8")
        leida = leer_politica()
        politicas, unidades = leida["politicas"], leida["unidades"]
        exigir(politicas, "no hay títulos '## P01 — <nombre>'")
        sin_tabla = [nombre for nombre, categorias in politicas.items() if not categorias]
        exigir(not sin_tabla, f"políticas sin tabla Grupo / Categoría / Cuenta: {sin_tabla}")
        exigir(unidades, "falta la tabla '### Unidades de negocio' con códigos (TIE, CD, ...)")
        exigir("Reglas generales" in leida["secciones"], "falta la sección '## Reglas generales'")
        reglas = re.findall(r"^\*\*(RG-\d{2})", texto, flags=re.MULTILINE)
        exigir(reglas, "no hay reglas generales con formato **RG-01 — ...**")
        categorias = sum(len(c) for c in politicas.values())
        return (
            f"{len(politicas)} políticas, {categorias} categorías, {len(reglas)} reglas "
            f"({reglas[0]} a {reglas[-1]}), unidades {', '.join(sorted(unidades))}"
        )

    punto("datos/politica_ficticia.md", politica)

    def rendiciones():
        columnas = list(contrato.Gasto.__annotations__)
        with open(CARPETA / "datos" / "rendiciones_prueba.csv", encoding="utf-8", newline="") as archivo:
            lector = csv.DictReader(archivo)
            exigir(lector.fieldnames == columnas, f"columnas {lector.fieldnames}, se esperaban {columnas}")
            filas = list(lector)
        exigir(filas, "el archivo no tiene gastos")
        for numero, fila in enumerate(filas, start=2):
            try:
                fila["monto"] = int(fila["monto"])
            except ValueError:
                raise AssertionError(f"línea {numero}: monto '{fila['monto']}' no es un entero") from None
            fila["patente"] = fila["patente"] or None
            fila["numero_ot"] = fila["numero_ot"] or None
            vb = fila["vb_gerente_general"].strip().lower()
            exigir(vb in ("true", "false", ""), f"línea {numero}: vb_gerente_general debe ser true, false o vacío")
            fila["vb_gerente_general"] = vb == "true"
            revisar_gasto(fila, f"línea {numero}")
        return f"{len(filas)} gastos"

    punto("datos/rendiciones_prueba.csv", rendiciones)

    def golden():
        # Formato v1.0 (ver pruebas/README.md): cada caso tiene uno o más turnos; cada turno trae
        # un "esperado" y, si corresponde, un "mensaje" y/o un "gasto".
        datos = json.loads((CARPETA / "pruebas" / "golden_set.json").read_text(encoding="utf-8"))
        exigir(isinstance(datos.get("version"), str), "falta el campo 'version'")
        casos = datos.get("casos")
        exigir(isinstance(casos, list) and casos, "falta la lista 'casos'")
        ids = [caso.get("id") for caso in casos]
        exigir(len(ids) == len(set(ids)), "hay ids de casos repetidos")
        turnos = 0
        for caso in casos:
            faltan = CAMPOS_CASO_GOLDEN - set(caso)
            exigir(not faltan, f"caso {caso.get('id')}: faltan los campos {sorted(faltan)}")
            exigir(caso["grupo"] in GRUPOS_GOLDEN, f"caso {caso['id']}: grupo '{caso['grupo']}' no es uno de {GRUPOS_GOLDEN}")
            exigir(caso["origen"] in ORIGENES_GOLDEN, f"caso {caso['id']}: origen '{caso['origen']}' no es uno de {ORIGENES_GOLDEN}")
            exigir(isinstance(caso["turnos"], list) and caso["turnos"], f"caso {caso['id']}: 'turnos' debe ser una lista no vacía")
            for numero, turno in enumerate(caso["turnos"], start=1):
                revisar_turno_golden(turno, f"caso {caso['id']} turno {numero}")
                turnos += 1
        return f"versión {datos['version']}, {len(casos)} casos, {turnos} turnos"

    punto("pruebas/golden_set.json", golden)


def bloque_6_grafo_sin_internet() -> None:
    # Prueba el ciclo ReAct con el LLM falso: herramienta → observación → respuesta,
    # historial entre turnos y parada por MAX_PASOS.
    titulo("6. Ciclo ReAct con LLM falso (sin internet)")
    from langchain_core.messages import ToolMessage

    grafo, contrato = modulos["grafo"], modulos["contrato"]

    def caso_normal_e_historial():
        llm = LLMFalso()
        with usar_llm(llm), silencio():
            agente = grafo.construir_agente()
            respuesta = grafo.conversar(agente, "Revisa el gasto G-VERIF", "hilo-verificar")
            exigir(isinstance(respuesta, str) and respuesta.strip(), "conversar debe devolver un texto")
            mensajes = agente.get_state({"configurable": {"thread_id": "hilo-verificar"}}).values["messages"]
            exigir(any(isinstance(m, ToolMessage) for m in mensajes), "la observación de la herramienta no volvió al LLM")
            cantidad_turno_1 = len(mensajes)
            grafo.conversar(agente, "¿Qué gasto revisaste?", "hilo-verificar")
            mensajes = agente.get_state({"configurable": {"thread_id": "hilo-verificar"}}).values["messages"]
        exigir(len(mensajes) > cantidad_turno_1, "el segundo turno no conserva el historial del primero")
        return f"turno 1: {cantidad_turno_1} mensajes, turno 2: {len(mensajes)}"

    punto("herramienta → observación → respuesta, y segundo turno con historial", caso_normal_e_historial)

    def parada():
        llm = LLMFalso(siempre_pide_herramienta=True)
        with usar_llm(llm), silencio():
            agente = grafo.construir_agente()
            grafo.conversar(agente, "Revisa el gasto G-VERIF", "hilo-parada")
        exigir(llm.llamadas <= contrato.MAX_PASOS, f"el LLM se llamó {llm.llamadas} veces (máximo {contrato.MAX_PASOS})")
        return f"se detuvo tras {llm.llamadas} llamadas al LLM"

    punto("parada por MAX_PASOS si el LLM pide herramientas sin fin", parada)


def bloque_7_con_llm() -> None:
    # Conversación corta con el Gemini real: un gasto y una pregunta sobre el historial.
    titulo("7. Conversación con el agente real (--con-llm)")
    grafo = modulos["grafo"]

    def conversacion_real():
        agente = grafo.construir_agente()
        mensaje = "Revisa este gasto rendido:\n" + json.dumps(GASTO_EJEMPLO, ensure_ascii=False, indent=2)
        respuesta_1 = grafo.conversar(agente, mensaje, "hilo-real")
        print(f"\n[Respuesta turno 1]\n{respuesta_1}\n")
        respuesta_2 = grafo.conversar(agente, "¿De qué monto era el gasto que acabas de revisar?", "hilo-real")
        print(f"\n[Respuesta turno 2]\n{respuesta_2}\n")
        exigir(respuesta_1.strip() and respuesta_2.strip(), "el agente respondió vacío")
        exigir(re.search(r"45[.,\s]?000", respuesta_2), "en el segundo turno no recordó el monto (45.000)")

    punto("conversación de dos turnos con Gemini", conversacion_real)


def main() -> None:
    global CON_LLM
    sys.stdout.reconfigure(encoding="utf-8")  # para que ✅ ❌ se vean bien en Windows
    argumentos = argparse.ArgumentParser(description="Revisa el contrato del proyecto.")
    argumentos.add_argument("--con-llm", action="store_true", help="además conversa con el agente real")
    CON_LLM = argumentos.parse_args().con_llm

    bloque_1_importar()
    if not all(resultados):
        print("\n❌ No se pudieron importar todos los módulos: corrige eso primero.")
        sys.exit(1)
    bloque_2_contrato()
    bloque_3_firmas()
    bloque_4_llamadas()
    bloque_5_datos()
    bloque_6_grafo_sin_internet()
    if CON_LLM:
        bloque_7_con_llm()

    fallas = resultados.count(False)
    print(f"\nResumen: {resultados.count(True)} ✅  {fallas} ❌")
    if fallas:
        print("Hay puntos que fallan: revisa los ❌ de arriba antes de subir cambios.")
        sys.exit(1)
    print("Todo en orden: el proyecto respeta el contrato.")


CON_LLM = False

if __name__ == "__main__":
    main()
