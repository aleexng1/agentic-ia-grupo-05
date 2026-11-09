"""Arma el documento de entrega del Grupo 5 a partir de los documentos de cada integrante.

Genera entrega/documento-entrega.md y, si WeasyPrint está instalado, entrega/documento-entrega.pdf
con las capturas incrustadas. No modifica los documento-NOMBRE.md: los copia tal cual,
bajando solo el nivel de los títulos. Lo que todavía no existe (catálogo, ronda, análisis)
queda marcado como PENDIENTE en rojo.

No va en el zip. Las herramientas se instalan aparte, no en requirements.txt.
Uso, desde taller-01-c2/:

    python3.12 -m venv entrega/.venv-entrega
    entrega/.venv-entrega/bin/pip install markdown-it-py weasyprint
    entrega/.venv-entrega/bin/python entrega/armar_documento.py
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent  # taller-01-c2/
ENTREGA = BASE / "entrega"
EVIDENCIAS = BASE / "evidencias"
ANALISIS = ENTREGA / "analisis-ronda.md"  # respuestas del grupo a las 3 preguntas de la ronda
SALIDA_MD = ENTREGA / "documento-entrega.md"
SALIDA_PDF = ENTREGA / "documento-entrega.pdf"

# carpeta, nombre completo, rol, nombre del agente, puerto, herramienta
INTEGRANTES = [
    ("matias", "Matias Muñoz", "Programa, actividades y horarios", "Agente de Matias", 8003, "armar_programa"),
    ("alex", "Alex Nail", "Lugares y capacidad", "Agente de Alex", 8004, "buscar_recintos"),
    ("eduardo", "Eduardo Basaure", "Presupuesto y costos estimados", "Agente de Eduardo", 8005, "estimar_presupuesto"),
    ("sebastian", "Sebastian Mardones", "Comida y catering", "Agente de Sebastian", 8006, "armar_catering"),
]

_MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
          "septiembre", "octubre", "noviembre", "diciembre"]

_pendientes: list[str] = []
_SALTO = '<div class="nueva-pagina"></div>\n\n'
_INDICE = "<!-- INDICE -->"  # generar_pdf lo reemplaza por el índice con números de página


def _pendiente(texto: str) -> str:
    """Bloque rojo bien visible para lo que falta."""
    _pendientes.append(texto)
    return f'\n<div class="pendiente">PENDIENTE: {texto}</div>\n'


def _fecha_es(dia: date) -> str:
    return f"{dia.day} de {_MESES[dia.month - 1]} de {dia.year}"


def bajar_titulos(texto: str, niveles: int = 2) -> str:
    """Baja el nivel de los títulos Markdown, sin tocar los bloques de código."""
    salida, en_codigo = [], False
    for linea in texto.splitlines():
        if re.match(r"^\s*(```|~~~)", linea):
            en_codigo = not en_codigo
        elif not en_codigo:
            coincidencia = re.match(r"^(#{1,6})(\s.*)$", linea)
            if coincidencia:
                nivel = min(len(coincidencia.group(1)) + niveles, 6)
                linea = "#" * nivel + coincidencia.group(2)
        salida.append(linea)
    return "\n".join(salida)


def _imagen(ruta: Path, pie: str) -> str:
    relativa = ruta.relative_to(BASE).as_posix()
    return (
        f'\n<figure><img src="../{relativa}" alt="{pie}"/>'
        f"<figcaption>{pie} · <code>{relativa}</code></figcaption></figure>\n"
    )


def _documento(carpeta: str) -> Path:
    return BASE / f"documento-{carpeta}.md"


def _parrafo_herramienta(texto: str) -> str | None:
    """Devuelve, textual, el primer párrafo donde el integrante nombra su herramienta de IA."""
    for parrafo in re.split(r"\n\s*\n", texto):
        if re.search(r"Claude Code|OpenCode", parrafo) and not parrafo.lstrip().startswith(("```", "|", "#")):
            return " ".join(parrafo.split())
    return None


def _tabla_ronda(texto: str) -> str | None:
    """Busca la tabla oficial de la ronda (columna «A quién fue») y la devuelve si tiene datos."""
    lineas = texto.splitlines()
    for indice, linea in enumerate(lineas):
        if linea.startswith("|") and "Pregunta" in linea and "A quién fue" in linea:
            tabla = [linea]
            for siguiente in lineas[indice + 1:]:
                if not siguiente.startswith("|"):
                    break
                tabla.append(siguiente)
            filas = tabla[2:]
            columnas = [c.strip() for c in linea.strip("|").split("|")]
            posicion = columnas.index("A quién fue")
            llenas = [
                fila for fila in filas
                if len(fila.strip("|").split("|")) > posicion
                and fila.strip("|").split("|")[posicion].strip()
            ]
            return "\n".join(tabla) if llenas else None
    return None


def armar_markdown(fecha: str) -> str:
    partes: list[str] = []

    # 1. Portada
    nombres = "<br/>".join(nombre for _, nombre, *_ in INTEGRANTES)
    partes.append(
        '<div class="portada">\n'
        '<p class="curso">Certificado Profesional de Agentic IA · Curso 2 · Taller 1</p>\n'
        '<h1 class="titulo">Taller A2A · Grupo 5</h1>\n'
        '<p class="tema">Planificador de ferias y eventos</p>\n'
        '<p class="subtitulo">Tu skill es un agente y habla por A2A</p>\n'
        f'<p class="integrantes"><strong>Integrantes</strong><br/>{nombres}</p>\n'
        f'<p class="fecha">{fecha}</p>\n'
        "</div>\n"
    )

    # Índice (se arma en generar_pdf con los títulos ## del documento)
    partes.append(_SALTO + _INDICE + "\n")

    # Identificación
    partes.append(_SALTO + "## Identificación\n")
    partes.append("**Grupo 5** · tema común: planificador de ferias y eventos.\n")
    partes.append("| Integrante | Agente | Habilidad | Herramienta | Puerto | Carpeta |")
    partes.append("|---|---|---|---|---|---|")
    for carpeta, nombre, rol, agente, puerto, herramienta in INTEGRANTES:
        partes.append(f"| {nombre} | {agente} | {rol} | `{herramienta}` | {puerto} | `src/agente_{carpeta}/` |")
    partes.append("| (grupo) | Coordinador | Elige el agente y delega por A2A | — | 8002 | `src/coordinador/` |\n")

    # 2. Cómo funciona
    partes.append("## 1. Cómo funciona el sistema\n")
    partes.append(
        "Cada integrante construyó un agente con una sola habilidad. Cada agente corre en el "
        "computador de su dueño, publica su **ficha** (`/.well-known/agent-card.json`) y se "
        "abre a internet con un túnel de Cloudflare. El **coordinador** descarga las cuatro "
        "fichas, y para cada pregunta un supervisor (Gemini) lee las descripciones, elige el "
        "agente que corresponde (o «ninguno») y le reenvía la pregunta por A2A.\n"
    )
    partes.append(
        "```text\n"
        "                          Persona\n"
        "                             │ pregunta\n"
        "                             ▼\n"
        "              ┌───────────────────────────────┐\n"
        "              │  Coordinador · supervisor     │  :8002\n"
        "              │  lee las 4 fichas y elige     │\n"
        "              └───────────────┬───────────────┘\n"
        "                  A2A (SendMessage) por túnel HTTPS\n"
        "     ┌──────────────┬─────────┴────┬────────────────┐\n"
        "     ▼              ▼              ▼                ▼\n"
        " Matias :8003   Alex :8004    Eduardo :8005   Sebastian :8006\n"
        " programa y     lugares y     presupuesto     comida y\n"
        " horarios       capacidad     y costos        catering\n"
        " armar_         buscar_       estimar_        armar_\n"
        " programa       recintos      presupuesto     catering\n"
        "```\n"
    )
    partes.append(
        "Cada herramienta hace todas las cuentas con datos ficticios (los modelos de lenguaje "
        "calculan mal) y el modelo solo presenta el resultado. Si la pregunta no es de su "
        "tema, el agente la rechaza en una frase sin usar la herramienta.\n"
    )

    # 3. Diferencias con la guía
    partes.append("## 2. Diferencias con la guía del taller\n")
    partes.append(
        "El proyecto usa `a2a-sdk` 1.3, que cambia algunos nombres respecto de la guía:\n\n"
        "- El método JSON-RPC es `SendMessage`, no `message/send`.\n"
        "- Hay que enviar la cabecera `A2A-Version: 1.0`.\n"
        "- Los roles son `ROLE_USER` y `ROLE_AGENT`.\n"
        "- El texto de la respuesta viene en `result.message.parts`, no en `artifacts`.\n"
        "- `sse-starlette` se agregó a `requirements.txt`: sin ella el servidor A2A no arranca.\n\n"
        "**Evidencias por integrante.** La pauta muestra una sola carpeta `evidencias/`; usamos "
        "una subcarpeta por integrante (`evidencias/NOMBRE/`) porque los cuatro tienen archivos "
        "con el mismo nombre (`01-saltos.png`, `02-ficha.json`, …).\n\n"
        "**Tildes en el celular.** En las capturas de la ficha abierta desde el teléfono las "
        "tildes se ven mal («tecnolÃ³gicas»): el servidor responde `content-type: application/json` "
        "sin declarar `charset=utf-8` y el navegador del teléfono interpreta el texto en otro "
        "formato. La ficha es correcta (UTF-8 válido), como se ve en los `02-ficha.json`.\n"
    )

    # 4. Una sección por integrante
    partes.append("## 3. Agentes de cada integrante\n")
    partes.append(
        "Cada sección reproduce tal cual el documento del integrante (`documento-NOMBRE.md`); "
        "solo cambia el nivel de los títulos. Al final de cada una van sus capturas.\n"
    )
    for numero, (carpeta, nombre, rol, *_resto) in enumerate(INTEGRANTES, start=1):
        partes.append(_SALTO + f"## 3.{numero} {nombre} · {rol}\n")
        ruta = _documento(carpeta)
        if ruta.exists():
            partes.append(bajar_titulos(ruta.read_text(encoding="utf-8")) + "\n")
        else:
            partes.append(_pendiente(f"falta {ruta.name}"))
        capturas = sorted(
            p for p in (EVIDENCIAS / carpeta).glob("*.png")
            if not p.name.startswith(("04-catalogo", "05-ronda"))
        )
        partes.append(f"#### Capturas de {nombre}\n")
        if capturas:
            partes.extend(_imagen(p, p.stem) for p in capturas)
        else:
            partes.append(_pendiente(f"sin capturas en evidencias/{carpeta}/"))

    # 5. Catálogo
    partes.append(_SALTO + "## 4. Catálogo del supervisor\n")
    partes.append(
        "Cada integrante levantó el coordinador con las cuatro direcciones públicas y capturó "
        "el mensaje «Supervisor con 4 agentes» (`evidencias/NOMBRE/04-catalogo.png`).\n"
    )
    for carpeta, nombre, *_ in INTEGRANTES:
        partes.append(f"### {nombre}\n")
        ruta = EVIDENCIAS / carpeta / "04-catalogo.png"
        partes.append(_imagen(ruta, f"04-catalogo de {nombre}") if ruta.exists()
                      else _pendiente(f"evidencias/{carpeta}/04-catalogo.png (prueba grupal)"))

    # 6. Ronda
    partes.append(_SALTO + "## 5. Ronda de preguntas\n")
    partes.append(
        "Cada integrante hizo tres preguntas al coordinador: una de su tema, una del tema de "
        "otro compañero y una que nadie sabe.\n"
    )
    for carpeta, nombre, *_ in INTEGRANTES:
        partes.append(f"### {nombre}\n")
        ruta_doc = _documento(carpeta)
        tabla = _tabla_ronda(ruta_doc.read_text(encoding="utf-8")) if ruta_doc.exists() else None
        partes.append(tabla + "\n" if tabla else _pendiente(f"tabla de la ronda en documento-{carpeta}.md"))
        # Algunos integrantes usaron una captura por pregunta (05-ronda, 05-ronda-2, ...).
        rondas = sorted((EVIDENCIAS / carpeta).glob("05-ronda*.png"),
                        key=lambda p: (p.stem != "05-ronda", p.name))
        if rondas:
            partes.extend(_imagen(p, f"{p.stem} de {nombre}") for p in rondas)
        else:
            partes.append(_pendiente(f"evidencias/{carpeta}/05-ronda.png (prueba grupal)"))

    # 7. Análisis
    partes.append("## 6. Análisis de la ronda\n")
    if ANALISIS.exists():
        # Lo que diga «PENDIENTE: …» dentro del archivo sale como recuadro rojo.
        analisis = re.sub(r"PENDIENTE: *(.+)", lambda m: _pendiente(m.group(1).strip()),
                          ANALISIS.read_text(encoding="utf-8"))
        partes.append(analisis)
    else:
        for pregunta in (
            "¿Qué ficha eligió mejor el supervisor y qué decía?",
            "¿Hubo preguntas que dos agentes podían responder? ¿Cómo se resolvió?",
            "¿Qué cambiaría cada uno de su ficha?",
        ):
            partes.append(f"### {pregunta}\n")
            partes.append(_pendiente("se responde después de la ronda grupal"))

    # 8. Uso de IA
    partes.append("## 7. Uso de herramientas de IA\n")
    partes.append(
        "Cada integrante declara en su documento qué asistente usó. Se citan sus palabras:\n"
    )
    for carpeta, nombre, *_ in INTEGRANTES:
        ruta = _documento(carpeta)
        parrafo = _parrafo_herramienta(ruta.read_text(encoding="utf-8")) if ruta.exists() else None
        if parrafo:
            partes.append(f"- **{nombre}:** «{parrafo}»")
        else:
            partes.append(f"- **{nombre}:**" + _pendiente(f"documento-{carpeta}.md no dice qué herramienta usó"))
    partes.append(
        "\nLa integración del grupo (estructura base, revisión de los pull requests, README del "
        "proyecto y los scripts que arman este documento y el zip) la hizo Alex Nail con "
        "Claude Code. En todos los casos las personas dieron las instrucciones, revisaron los "
        "resultados y tomaron las decisiones.\n"
    )
    return "\n".join(partes)


_CSS = """
@page { size: A4; margin: 1.8cm 1.6cm 2cm;
  @bottom-center { content: "Grupo 5 · Taller A2A · página " counter(page) " de " counter(pages);
                   font-family: 'DejaVu Sans'; font-size: 7.5pt; color: #777; } }
@page :first { @bottom-center { content: none; } }
body { font-family: 'DejaVu Sans', sans-serif; font-size: 9.5pt; line-height: 1.4; color: #1a1a1a; }
h1, h2, h3, h4, h5, h6 { color: #12355b; line-height: 1.2; page-break-after: avoid; }
h2 { font-size: 15pt; border-bottom: 2px solid #12355b; padding-bottom: 3px; margin-top: 1.4em; }
h3 { font-size: 12.5pt; } h4 { font-size: 11pt; } h5 { font-size: 10pt; } h6 { font-size: 9.5pt; }
.nueva-pagina { page-break-before: always; }
pre { font-family: 'DejaVu Sans Mono', monospace; font-size: 7pt; background: #f4f5f7;
      border: 1px solid #dde; padding: 6px 8px; white-space: pre-wrap; word-wrap: break-word; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8pt; background: #f4f5f7; }
pre code { background: none; font-size: 7pt; }
table { border-collapse: collapse; width: 100%; margin: 6px 0; font-size: 8pt; }
th, td { border: 1px solid #c8ccd4; padding: 3px 5px; vertical-align: top; word-break: break-word; }
th { background: #e8edf4; }
blockquote { border-left: 3px solid #aab; margin-left: 0; padding-left: 10px; color: #333; }
figure { margin: 10px 0; text-align: center; page-break-inside: avoid; }
figure img { max-width: 100%; max-height: 19cm; border: 1px solid #ccc; }
figcaption { font-size: 7.5pt; color: #555; margin-top: 3px; }
.pendiente { border: 3px solid #c0161c; background: #fde8e8; color: #9b0d12; font-weight: bold;
             font-size: 11pt; padding: 10px 12px; margin: 10px 0; }
.indice-titulo { font-size: 18pt; font-weight: bold; color: #12355b; border-bottom: 2px solid #12355b;
                 padding-bottom: 3px; margin: 0 0 12px; }
.indice ul { list-style: none; padding: 0; margin: 0; font-size: 11pt; }
.indice li { margin: 7px 0; }
.indice li.sub { margin-left: 1.6em; font-size: 10pt; }
.indice a { color: #1a1a1a; text-decoration: none; }
.indice a::after { content: leader('.') target-counter(attr(href), page); }
.portada { text-align: center; padding-top: 5cm; }
.portada .curso { font-size: 11pt; color: #555; }
.portada .titulo { font-size: 30pt; margin: 0.6cm 0 0.2cm; border: none; }
.portada .tema { font-size: 17pt; color: #12355b; margin: 0; }
.portada .subtitulo { font-size: 12pt; font-style: italic; color: #555; }
.portada .integrantes { font-size: 12pt; margin-top: 2.5cm; line-height: 1.8; }
.portada .fecha { font-size: 11pt; margin-top: 1.5cm; color: #555; }
"""


_entradas_indice: list[tuple[str, str]] = []


def _anclar_titulos(cuerpo: str) -> str:
    """Da un id a cada título principal (h2) para que el índice pueda apuntar a él."""
    _entradas_indice.clear()

    def anclar(m: re.Match) -> str:
        ancla = f"sec-{len(_entradas_indice) + 1}"
        _entradas_indice.append((ancla, m.group(1)))
        return f'<h2 id="{ancla}">{m.group(1)}</h2>'

    return re.sub(r"<h2>(.*?)</h2>", anclar, cuerpo)


def _indice() -> str:
    """Lista de títulos principales; las secciones 3.x (una por integrante) van con sangría."""
    filas = []
    for ancla, titulo in _entradas_indice:
        clase = ' class="sub"' if re.match(r"3\.\d", titulo) else ""
        filas.append(f'<li{clase}><a href="#{ancla}">{titulo}</a></li>')
    return '<div class="indice"><p class="indice-titulo">Índice</p><ul>' + "".join(filas) + "</ul></div>"


def generar_pdf(texto_md: str) -> bool:
    try:
        from markdown_it import MarkdownIt
        from weasyprint import HTML
    except ImportError:
        print("No se generó el PDF: falta instalar markdown-it-py y weasyprint en "
              "entrega/.venv-entrega (ver instrucciones al inicio de este archivo).")
        return False
    # CommonMark con tablas: el mismo formato con que GitHub muestra los documentos.
    cuerpo = MarkdownIt("commonmark", {"html": True}).enable("table").render(texto_md)
    cuerpo = _anclar_titulos(cuerpo)
    cuerpo = cuerpo.replace(_INDICE, _indice())
    html = (
        '<!doctype html><html lang="es"><head><meta charset="utf-8">'
        f"<title>Taller A2A · Grupo 5</title><style>{_CSS}</style></head>"
        f"<body>{cuerpo}</body></html>"
    )
    HTML(string=html, base_url=str(ENTREGA)).write_pdf(SALIDA_PDF)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--fecha", help="Fecha de la portada (por defecto, hoy).")
    parser.add_argument("--sin-pdf", action="store_true", help="Genera solo el Markdown.")
    argumentos = parser.parse_args()

    fecha = argumentos.fecha or _fecha_es(date.today())
    texto = armar_markdown(fecha)
    SALIDA_MD.write_text(texto, encoding="utf-8")
    print(f"Markdown: {SALIDA_MD.relative_to(BASE)}")
    if not argumentos.sin_pdf and generar_pdf(texto):
        print(f"PDF:      {SALIDA_PDF.relative_to(BASE)}")
    if _pendientes:
        print(f"\nPendientes ({len(_pendientes)}):")
        for item in _pendientes:
            print(f"  - {item}")
    else:
        print("\nSin pendientes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
