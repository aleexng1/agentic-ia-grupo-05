"""Herramienta de validación: revisa un gasto con reglas exactas de la política.

Dueño: rol Herramientas y estado.

Idea central: las reglas NO están escritas a mano en este archivo. Se leen de
datos/politica_ficticia.md (versión vigente 1.1): las reglas generales RG-01 a RG-10
con su efecto (rechaza u observa), y de cada política P01 a P10 sus unidades
permitidas, documentos, campos obligatorios, topes por documento, tabla de cuentas,
equipos vigentes y regla especial. Si Caso y calidad cambia la política, la
validación cambia sola.

Lo único que vive en código son los "puentes" entre el texto y los campos del gasto
(qué palabra de la política corresponde a qué campo). Están en la sección SUPUESTOS.

Qué revisa validar_gasto (código, no LLM):
    RG-01 / Pxx  documento permitido (voucher solo en transporte; P07 solo factura)
    RG-03        plazo de rendición (día límite del mes siguiente; con VB del GG se observa)
    RG-05        tope por documento de la categoría
    RG-06/RG-09  política o categoría declarada distinta de la correcta
    RG-07        política exclusiva de otra unidad de negocio
    RG-10        campos obligatorios (patente, código de equipo, número de OT)
    Pxx          regla especial de la política (por ejemplo, multas en P04)
Qué NO revisa (lo decide el LLM con el RAG, o lo revisa otra pieza):
    RG-02 gasto personal (requiere entender la glosa), RG-04 segregación (no hay dato),
    RG-08 saldo del fondo (src/memoria.py: revisar_saldo, lo aplica el Núcleo).
"""

import functools
import re
import unicodedata
from datetime import date

from langchain_core.tools import ToolException, tool

from src.config import CARPETA_PROYECTO
from src.contrato import DECISIONES, Decision, Gasto, Incumplimiento, Validacion

# Archivo de la política (dueño: Caso y calidad).
RUTA_POLITICA = CARPETA_PROYECTO / "datos" / "politica_ficticia.md"

# ---------------------------------------------------------------------------
# SUPUESTOS: puentes entre el texto de la política y los campos del gasto.
# Son las únicas decisiones escritas a mano; están documentadas aquí a propósito.
# ---------------------------------------------------------------------------

# RG-01 dice "voucher únicamente en taxi, aplicaciones de transporte y bus interurbano".
# El gasto no trae "tipo de comercio", así que se usa la categoría: solo las categorías
# de transporte de pasajeros admiten voucher. Se decide por categoría y no por la glosa,
# porque la glosa la escribe el trabajador (y puede traer instrucciones engañosas).
PALABRAS_CATEGORIA_VOUCHER = ("locomocion", "pasaje")

# En algunos sistemas el voucher aparece como "Otros" (RG-01): se trata igual.
SINONIMOS_DOCUMENTO = {"otros": "voucher", "otro": "voucher"}

# Texto de "Campos obligatorios" de la política → campo del gasto (src/contrato.py).
CAMPOS_POR_ETIQUETA = {"patente": "patente", "numero de ot": "numero_ot"}

# Orden de gravedad para combinar varios incumplimientos en una decisión.
GRAVEDAD = {"aprobar": 0, "observar": 1, "rechazar": 2}


# ---------------------------------------------------------------------------
# Lectura de la política (una sola vez por sesión, con caché)
# ---------------------------------------------------------------------------


def _normalizar(texto: str) -> str:
    """Minúsculas, sin tildes y sin espacios repetidos (para comparar nombres)."""
    sin_tildes = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", sin_tildes).strip().casefold()


def _efecto_en(texto: str) -> list[Decision]:
    """Efectos en negrita dentro de un párrafo: **rechaza** → rechazar, **observado** → observar."""
    efectos = []
    for palabra in re.findall(r"\*\*(rechaz\w*|observ\w*)\*\*", texto, flags=re.IGNORECASE):
        efectos.append("rechazar" if palabra.lower().startswith("rechaz") else "observar")
    return efectos


def _monto(texto: str) -> int:
    """'$10.000' → 10000."""
    return int(re.sub(r"\D", "", texto))


def _leer_reglas_generales(texto: str) -> dict:
    """{"RG-01": {"titulo", "texto", "efecto", "efecto_excepcion"}, ...}."""
    reglas = {}
    patron = r"^\*\*(RG-\d{2}) — ([^*]+?)\.\*\*(.*)$"
    for codigo, titulo, cuerpo in re.findall(patron, texto, flags=re.MULTILINE):
        efectos = _efecto_en(cuerpo)
        reglas[codigo] = {
            "titulo": titulo.strip(),
            "texto": cuerpo.strip(),
            # Primer efecto = regla general; segundo (si existe) = excepción (RG-03 con VB).
            "efecto": efectos[0] if efectos else None,
            "efecto_excepcion": efectos[1] if len(efectos) > 1 else None,
        }
    return reglas


def _leer_politica_seccion(codigo: str, nombre: str, lineas: list[str]) -> dict:
    """Lee una sección '## Pxx — Nombre' de la política."""
    politica = {
        "codigo": codigo,
        "nombre": nombre,
        "unidades": None,  # None = todas las unidades
        "documentos": set(),
        "voucher_condicionado": False,
        "documento_exclusivo": False,  # "Solo factura": restricción propia de la política
        "campos": [],
        "valida_equipos": False,
        "topes": {},
        "categorias": {},
        "equipos": set(),
        "regla_especial": "",
    }
    en_equipos = False
    for linea in lineas:
        if linea.startswith("**Unidades permitidas.**"):
            codigos = re.findall(r"\*\*([A-Z]{2,4})\*\*", linea)
            politica["unidades"] = set(codigos) if codigos else None
        elif linea.startswith("**Documentos.**"):
            cuerpo = _normalizar(linea.removeprefix("**Documentos.**"))
            # La frase "una boleta no es válida" no debe contar boleta como permitida.
            cuerpo_permitido = re.split(r"no es valida", cuerpo)[0]
            for documento in ("boleta", "factura"):
                if re.search(rf"\b{documento}\b", cuerpo_permitido) and not re.search(
                    rf"una {documento} no", cuerpo
                ):
                    politica["documentos"].add(documento)
            politica["voucher_condicionado"] = "voucher" in cuerpo
            politica["documento_exclusivo"] = cuerpo.startswith("**solo") or cuerpo.startswith("solo")
        elif linea.startswith("**Campos obligatorios.**"):
            cuerpo = _normalizar(linea)
            politica["campos"] = [campo for etiqueta, campo in CAMPOS_POR_ETIQUETA.items() if etiqueta in cuerpo]
            politica["valida_equipos"] = "tabla de equipos" in cuerpo
        elif linea.startswith("**Topes"):
            for categoria, monto in re.findall(r"([A-Za-zÁÉÍÓÚÑáéíóúñ ]+):\s*(\$[\d.]+)", linea.split("**", 2)[-1]):
                politica["topes"][_normalizar(categoria)] = _monto(monto)
        elif linea.startswith("**Regla especial.**"):
            politica["regla_especial"] = linea.removeprefix("**Regla especial.**").strip()
        elif linea.startswith("**Equipos vigentes**"):
            en_equipos = True
        elif fila := re.match(r"^\|([^|]+)\|([^|]+)\|\s*(CTA-\d{4})\s*\|$", linea):
            grupo, categoria, cuenta = (parte.strip() for parte in fila.groups())
            politica["categorias"][categoria] = {"grupo": grupo, "cuenta": cuenta}
        elif en_equipos and (fila := re.match(r"^\|\s*([A-Z]{2}-\d{2})\s*\|", linea)):
            politica["equipos"].add(fila.group(1))
    return politica


@functools.cache
def leer_politica() -> dict:
    """Lee datos/politica_ficticia.md y devuelve reglas generales, políticas y plazo.

    Devuelve:
        "version":   versión de la política (por ejemplo "1.1 (2026-10)"),
        "reglas":    {"RG-01": {...}, ...} con su efecto leído del texto,
        "politicas": {"P01": {...}, ...} con unidades, documentos, campos, topes, cuentas,
        "dia_limite": día del mes siguiente hasta el que se puede rendir (RG-03).
    """
    texto = RUTA_POLITICA.read_text(encoding="utf-8")
    version = re.search(r"^\|\s*Versión\s*\|\s*([^|]+?)\s*\|", texto, flags=re.MULTILINE)
    reglas = _leer_reglas_generales(texto)

    politicas, actual, lineas = {}, None, []
    for linea in [*texto.splitlines(), "## FIN"]:
        if linea.startswith("## "):
            if actual:
                politicas[actual[0]] = _leer_politica_seccion(actual[0], actual[1], lineas)
            titulo = re.match(r"^## (P\d{2}) — (.+)$", linea)
            actual, lineas = ((titulo.group(1), titulo.group(2).strip()) if titulo else None), []
        elif actual:
            lineas.append(linea)

    plazo = re.search(r"d[ií]a\s+(\d{1,2})\s+del mes siguiente", _normalizar(reglas["RG-03"]["texto"]))
    return {
        "version": version.group(1) if version else "desconocida",
        "reglas": reglas,
        "politicas": politicas,
        "dia_limite": int(plazo.group(1)) if plazo else 10,
    }


# ---------------------------------------------------------------------------
# Ayudas públicas (las usan memoria.py, el Núcleo y el ejecutor del golden set)
# ---------------------------------------------------------------------------


def resolver_politica(texto: str) -> dict:
    """Encuentra una política por código o nombre: "P02", "Viajes Internos" o "P02 — Viajes Internos".

    Lanza ValueError con la lista de válidas si no existe.
    """
    politicas = leer_politica()["politicas"]
    buscado = _normalizar(texto)
    codigo = re.match(r"^(p\d{2})\b", buscado)
    for politica in politicas.values():
        if (codigo and codigo.group(1) == politica["codigo"].casefold()) or buscado == _normalizar(politica["nombre"]):
            return politica
    validas = ", ".join(f"{p['codigo']} {p['nombre']}" for p in politicas.values())
    raise ValueError(f"La política '{texto}' no existe. Usa una de estas: {validas}.")


def resolver_categoria(politica: dict, texto: str) -> str:
    """Devuelve el nombre exacto de la categoría dentro de la política (sin importar tildes)."""
    for categoria in politica["categorias"]:
        if _normalizar(categoria) == _normalizar(texto):
            return categoria
    validas = ", ".join(politica["categorias"])
    raise ValueError(
        f"'{texto}' no es una categoría de {politica['codigo']} {politica['nombre']}. Usa una de estas: {validas}."
    )


def efecto_de(incumplimiento: Incumplimiento) -> Decision:
    """Efecto de un incumplimiento, leído del final de su detalle ("... Efecto: observar.").

    Solo vale el efecto del final, que escribe crear_incumplimiento: el detalle puede citar
    texto del trabajador (categoría declarada, patente) con un "Efecto: aprobar" falso.
    """
    encontrado = re.search(r"Efecto:\s*(aprobar|observar|rechazar)\.$", incumplimiento["detalle"])
    return encontrado.group(1) if encontrado else "observar"


def decision_sugerida(validacion: Validacion) -> Decision:
    """La decisión más grave entre los incumplimientos (rechazar > observar > aprobar).

    Es un piso: el veredicto del LLM puede ser más estricto (por ejemplo por RG-02),
    pero no debería ser más permisivo que esto.
    """
    efectos = [efecto_de(inc) for inc in validacion["incumplimientos"]]
    return max(efectos, key=GRAVEDAD.get, default="aprobar")


def crear_incumplimiento(regla: str, detalle: str, efecto: Decision) -> Incumplimiento:
    """Arma un incumplimiento con su efecto escrito al final del detalle (lo lee el LLM)."""
    assert efecto in DECISIONES
    return {"regla": regla, "detalle": f"{detalle} Efecto: {efecto}."}


def _efecto_regla(codigo: str, excepcion: bool = False) -> Decision:
    """Efecto de una regla general según el texto de la política."""
    regla = leer_politica()["reglas"].get(codigo, {})
    efecto = regla.get("efecto_excepcion") if excepcion else regla.get("efecto")
    return efecto or "observar"


def _clp(monto: int) -> str:
    """45000 → '$45.000'."""
    return "$" + f"{monto:,}".replace(",", ".")


# ---------------------------------------------------------------------------
# Revisiones (cada una devuelve una lista de incumplimientos, vacía si cumple)
# ---------------------------------------------------------------------------


def _revisar_documento(gasto: dict, politica: dict, categoria: str) -> list[Incumplimiento]:
    """RG-01 y documentos exigidos por la política."""
    tipo = _normalizar(gasto.get("tipo_documento", ""))
    tipo = SINONIMOS_DOCUMENTO.get(tipo, tipo)
    if tipo == "voucher":
        es_transporte = any(palabra in _normalizar(categoria) for palabra in PALABRAS_CATEGORIA_VOUCHER)
        if politica["voucher_condicionado"] and es_transporte:
            return []
        return [
            crear_incumplimiento(
                "RG-01",
                f"Voucher no válido para '{categoria}' en {politica['codigo']}: el voucher solo se acepta "
                "en taxi, aplicaciones de transporte o bus interurbano.",
                _efecto_regla("RG-01"),
            )
        ]
    if tipo in politica["documentos"]:
        return []
    permitidos = " o ".join(sorted(politica["documentos"]))
    # Si la política restringe el documento ("Solo factura"), la regla es propia de la política.
    regla = politica["codigo"] if politica["documento_exclusivo"] else "RG-01"
    return [
        crear_incumplimiento(
            regla,
            f"Documento '{tipo or 'vacío'}' no válido en {politica['codigo']} {politica['nombre']}: "
            f"solo se acepta {permitidos}.",
            _efecto_regla("RG-01"),
        )
    ]


def _revisar_plazo(gasto: dict) -> list[Incumplimiento]:
    """RG-03: mismo mes o hasta el día límite del mes siguiente."""
    try:
        fecha_gasto = date.fromisoformat(str(gasto.get("fecha_gasto")))
        fecha_rendicion = date.fromisoformat(str(gasto.get("fecha_rendicion")))
    except ValueError:
        return [
            crear_incumplimiento(
                "RG-10", "Las fechas deben venir en formato AAAA-MM-DD.", _efecto_regla("RG-10")
            )
        ]
    if fecha_rendicion < fecha_gasto:
        return [
            crear_incumplimiento(
                "RG-10",
                f"La fecha de rendición ({fecha_rendicion}) es anterior a la del gasto ({fecha_gasto}).",
                _efecto_regla("RG-10"),
            )
        ]
    anio, mes = (fecha_gasto.year + 1, 1) if fecha_gasto.month == 12 else (fecha_gasto.year, fecha_gasto.month + 1)
    limite = date(anio, mes, leer_politica()["dia_limite"])
    if fecha_rendicion <= limite:
        return []
    detalle = f"Se rindió el {fecha_rendicion}; el plazo para un gasto del {fecha_gasto} vencía el {limite}."
    if gasto.get("vb_gerente_general"):
        return [
            crear_incumplimiento(
                "RG-03",
                detalle + " Trae visto bueno del Gerente General, por eso queda para revisión.",
                _efecto_regla("RG-03", excepcion=True),
            )
        ]
    return [crear_incumplimiento("RG-03", detalle, _efecto_regla("RG-03"))]


def _revisar_tope(gasto: dict, politica: dict, categoria: str) -> list[Incumplimiento]:
    """RG-05: tope por documento de la categoría, si la política lo define."""
    tope = politica["topes"].get(_normalizar(categoria))
    monto = int(gasto.get("monto", 0))
    if tope is None or monto <= tope:
        return []
    return [
        crear_incumplimiento(
            "RG-05",
            f"{_clp(monto)} supera el tope por documento de '{categoria}' en {politica['codigo']} "
            f"({_clp(tope)}); el colaborador debe justificar el exceso.",
            _efecto_regla("RG-05"),
        )
    ]


def _revisar_unidad(gasto: dict, politica: dict) -> list[Incumplimiento]:
    """RG-07: políticas exclusivas de una unidad de negocio."""
    unidades = politica["unidades"]
    unidad = str(gasto.get("unidad_negocio", "")).strip().upper()
    if unidades is None or unidad in unidades:
        return []
    return [
        crear_incumplimiento(
            "RG-07",
            f"{politica['codigo']} {politica['nombre']} es exclusiva de {', '.join(sorted(unidades))}; "
            f"el gasto es de la unidad {unidad or 'sin unidad'} y debe reclasificarse.",
            _efecto_regla("RG-07"),
        )
    ]


def _revisar_campos(gasto: dict, politica: dict) -> list[Incumplimiento]:
    """RG-10: campos obligatorios presentes y válidos."""
    incumplimientos = []
    for campo in politica["campos"]:
        valor = str(gasto.get(campo) or "").strip()
        nombre = campo.replace("_", " ").replace("numero ot", "número de OT")
        if not valor:
            incumplimientos.append(
                crear_incumplimiento(
                    "RG-10", f"Falta el campo obligatorio '{nombre}' en {politica['codigo']}.", _efecto_regla("RG-10")
                )
            )
        elif campo == "patente" and politica["valida_equipos"] and valor.upper() not in politica["equipos"]:
            incumplimientos.append(
                crear_incumplimiento(
                    "RG-10",
                    f"El código de equipo '{valor}' no está en la tabla de equipos vigentes de "
                    f"{politica['codigo']} ({', '.join(sorted(politica['equipos']))}).",
                    _efecto_regla("RG-10"),
                )
            )
    return incumplimientos


def _revisar_clasificacion(gasto: dict, politica: dict, categoria: str, cuenta: str) -> list[Incumplimiento]:
    """RG-09 (y RG-06 en arriendo de auto liviano): lo declarado distinto de lo correcto."""
    try:
        declarada = resolver_politica(gasto.get("politica_declarada", ""))
        mismo_codigo = declarada["codigo"] == politica["codigo"]
    except ValueError:
        declarada, mismo_codigo = None, False
    misma_categoria = _normalizar(gasto.get("categoria_declarada", "")) == _normalizar(categoria)
    if mismo_codigo and misma_categoria:
        return []
    texto_declarado = f"{gasto.get('politica_declarada', '')} / {gasto.get('categoria_declarada', '')}"
    incumplimientos = [
        crear_incumplimiento(
            "RG-09",
            f"El trabajador declaró '{texto_declarado}'; corresponde {politica['codigo']} "
            f"{politica['nombre']} / {categoria}, cuenta {cuenta}.",
            _efecto_regla("RG-09"),
        )
    ]
    # RG-06 nombra la política de destino del arriendo de autos livianos ("P01 Vehículos Propios").
    destino_rg06 = re.search(r"\b(P\d{2})\b", leer_politica()["reglas"].get("RG-06", {}).get("texto", ""))
    if destino_rg06 and politica["codigo"] == destino_rg06.group(1) and "arriendo" in _normalizar(categoria):
        incumplimientos.append(
            crear_incumplimiento(
                "RG-06",
                f"El arriendo de un auto liviano y sus gastos asociados se rinden en {politica['codigo']} "
                f"{politica['nombre']}, aunque el viaje sea de trabajo.",
                _efecto_regla("RG-09"),
            )
        )
    return incumplimientos


def _revisar_regla_especial(politica: dict, categoria: str) -> list[Incumplimiento]:
    """Regla especial de la política (P04: las multas quedan observadas como Gasto Rechazado)."""
    especial = politica["regla_especial"]
    if not especial:
        return []
    # La regla aplica a las categorías que nombra (por ejemplo "Multa" en "multas de tránsito").
    raiz = _normalizar(categoria)
    if not re.search(rf"\b{re.escape(raiz)}", _normalizar(especial)):
        return []
    efectos = _efecto_en(especial)
    return [
        crear_incumplimiento(
            politica["codigo"],
            f"Regla especial de {politica['codigo']}: {re.sub(r'[*]', '', especial)}",
            efectos[0] if efectos else "observar",
        )
    ]


# ---------------------------------------------------------------------------
# Herramienta que el LLM puede pedir
# ---------------------------------------------------------------------------


def _validar(gasto: Gasto, politica: str, categoria: str) -> Validacion:
    """Lógica de validar_gasto, sin el envoltorio @tool (más fácil de probar)."""
    datos_politica = resolver_politica(politica)
    categoria_exacta = resolver_categoria(datos_politica, categoria)
    cuenta = datos_politica["categorias"][categoria_exacta]["cuenta"]
    gasto = dict(gasto)

    incumplimientos = [
        *_revisar_clasificacion(gasto, datos_politica, categoria_exacta, cuenta),
        *_revisar_documento(gasto, datos_politica, categoria_exacta),
        *_revisar_plazo(gasto),
        *_revisar_unidad(gasto, datos_politica),
        *_revisar_campos(gasto, datos_politica),
        *_revisar_tope(gasto, datos_politica, categoria_exacta),
        *_revisar_regla_especial(datos_politica, categoria_exacta),
    ]
    return {"cumple": not incumplimientos, "incumplimientos": incumplimientos, "cuenta": cuenta}


@tool
def validar_gasto(gasto: Gasto, politica: str, categoria: str) -> Validacion:
    """Revisa un gasto con las reglas exactas de la política de gastos.

    Usa esta herramienta DESPUÉS de decidir la política y la categoría correctas.
    Revisa: tipo de documento permitido, plazo de rendición, campos obligatorios
    (por ejemplo la patente en vehículos) y si la política es exclusiva de una
    unidad de negocio. Devuelve si cumple, la lista de reglas incumplidas y la
    cuenta contable que corresponde. Cada incumplimiento termina con su efecto
    ("Efecto: rechazar" u "Efecto: observar"); la decisión final es la más grave.

    Args:
        gasto: el gasto rendido, con todos sus campos.
        politica: código o nombre de la política que corresponde al gasto (por ejemplo "P02" o "Viajes Internos").
        categoria: nombre de la categoría dentro de esa política, tal como aparece en su tabla.
    """
    try:
        return _validar(gasto, politica, categoria)
    except (ValueError, KeyError, TypeError) as error:
        # El mensaje vuelve al LLM como observación para que corrija la política o la categoría.
        raise ToolException(f"No pude validar: {error}") from error


# Un error de entrada vuelve al LLM como texto (no rompe el grafo) y puede reintentar.
validar_gasto.handle_tool_error = True
