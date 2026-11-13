"""Toma las capturas de evidencia de Alex de forma automática, contra la app real.

Qué hace, de principio a fin:

1. Genera una CLAVE_API temporal en memoria (no se escribe en ningún archivo).
2. Levanta la app igual que Heroku: desde la raíz del repositorio, con el comando del
   Procfile y PORT=8000. La salida del servidor va a registro-local.txt.
3. Con Chrome sin ventana visible (Playwright, 1280x900) captura /salud, la pantalla de
   ingreso, un intento con clave incorrecta y, con la clave correcta, 6 preguntas reales a
   Gemini: una por cada agente, una que no es de nadie ("ninguno") y una con datos faltantes.
4. Detiene la app y depura registro-local.txt: cuenta cuántas veces aparece la clave (debe
   ser 0) y reemplaza las rutas del equipo por <carpeta-del-repo>.

Cada imagen lleva arriba una franja con la fecha y la hora de la captura. Para que la
respuesta completa quepa en la imagen, al capturar se quita el límite de altura del área de
conversación (solo estilo: el contenido no cambia).

Uso (desde la raíz del repositorio, con el entorno virtual del proyecto):

    taller-02-c2/proyecto/.venv/bin/python taller-02-c2/evidencias/alex/capturar_evidencias.py

    --sin-preguntas   solo /salud, el ingreso y la clave incorrecta (no usa Gemini)

Necesita Chrome y Playwright (pip install -r requirements-dev.txt, desde
taller-02-c2/proyecto). La clave de Gemini la lee la app desde taller-02-c2/proyecto/.env;
este script nunca abre ese archivo. Las 6 preguntas son reales: no se reintentan solas.
"""

import argparse
import getpass
import os
import secrets
import signal
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


CARPETA = Path(__file__).resolve().parent
RAIZ = CARPETA.parents[2]
PUERTO = 8000
URL = f"http://127.0.0.1:{PUERTO}"
REGISTRO = CARPETA / "registro-local.txt"
ANCHO, ALTO = 1280, 900
ESPERA_MAXIMA_MS = 100_000
CLAVE_INCORRECTA = "clave-incorrecta-de-prueba"
COMANDO_SERVIDOR = "cd taller-02-c2/proyecto && uvicorn app:app --host 0.0.0.0 --port $PORT"

# (archivo, pregunta exacta, texto que debe ir en «Agente: …»)
PREGUNTAS = [
    (
        "04a-matias-programa.png",
        "Necesito armar el programa de una feria infantil de 3 horas desde las 15:00.",
        "Matias",
    ),
    (
        "04b-alex-recintos.png",
        "Necesito un recinto interior para una feria tecnológica de 80 personas.",
        "Alex",
    ),
    (
        "04c-eduardo-presupuesto.png",
        "¿Cuál es el presupuesto simulado de una feria tecnológica para 80 personas y 4 horas?",
        "Eduardo",
    ),
    (
        "04d-sebastian-catering.png",
        "Necesito una propuesta de catering para una feria tecnológica de 80 personas, de 4 horas, "
        "comenzando a las 10:00. Hay 10 personas vegetarianas y otras 5 que requieren comida sin gluten.",
        "Sebastian",
    ),
    ("05-ninguno.png", "¿Cómo resuelvo una integral cuadrática?", "ninguno"),
    ("06-datos-faltantes.png", "¿Dónde hago una feria?", "Alex"),
]


def ahora() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")


# ---------- servidor ----------


def levantar_servidor(clave: str) -> subprocess.Popen:
    """Arranca la app como Heroku, con la clave solo en el entorno del proceso."""
    entorno = {
        **os.environ,
        "CLAVE_API": clave,
        "PORT": str(PUERTO),
        "PYTHONUNBUFFERED": "1",  # el registro llega al archivo línea a línea
        "URLS_AGENTES": "",  # modo interno: el coordinador llama a las rutas de esta app
        "PATH": str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", ""),
    }
    REGISTRO.write_text(
        f"# Registro del servidor · LOCAL · {ahora()}\n"
        "# Comando, desde la raíz del repositorio y con PORT=8000 (igual que el Procfile):\n"
        f"#   sh -c '{COMANDO_SERVIDOR}'\n"
        "# CLAVE_API temporal solo en el entorno del proceso. La salida sigue tal cual; solo se\n"
        "# reemplazan rutas del equipo por <carpeta-del-repo>.\n"
        "# ------------------------------------------------------------------------------\n",
        encoding="utf-8",
    )
    salida = open(REGISTRO, "ab")
    proceso = subprocess.Popen(
        ["sh", "-c", COMANDO_SERVIDOR],
        cwd=RAIZ,
        env=entorno,
        stdout=salida,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    limite = time.time() + 60
    while time.time() < limite:
        if proceso.poll() is not None:
            raise RuntimeError("El servidor se cerró al arrancar; revisa registro-local.txt.")
        try:
            with urllib.request.urlopen(f"{URL}/salud", timeout=2) as respuesta:
                if respuesta.status == 200:
                    return proceso
        except OSError:
            time.sleep(0.5)
    raise RuntimeError("El servidor no respondió /salud en 60 segundos.")


def detener_servidor(proceso: subprocess.Popen) -> None:
    """Detiene el servidor y todo su grupo de procesos (como un Ctrl+C)."""
    if proceso.poll() is not None:
        return
    for senal, espera in ((signal.SIGINT, 15), (signal.SIGTERM, 5), (signal.SIGKILL, 5)):
        try:
            os.killpg(proceso.pid, senal)
        except ProcessLookupError:
            return
        try:
            proceso.wait(timeout=espera)
            return
        except subprocess.TimeoutExpired:
            continue


def depurar_registro(clave: str) -> dict:
    """Cuenta la clave (debe ser 0) y reemplaza las rutas del equipo en el registro."""
    texto = REGISTRO.read_text(encoding="utf-8", errors="replace")
    resultado = {"clave": texto.count(clave)}
    if resultado["clave"]:
        texto = texto.replace(clave, "[clave oculta]")
    inicio = str(Path.home())
    resultado["rutas_repo"] = texto.count(str(RAIZ))
    texto = texto.replace(str(RAIZ), "<carpeta-del-repo>")
    resultado["rutas_personales"] = texto.count(inicio)
    texto = texto.replace(inicio, "<carpeta-personal>")
    usuario = getpass.getuser()
    resultado["usuario"] = texto.count(usuario)
    if usuario:
        texto = texto.replace(usuario, "<usuario>")
    REGISTRO.write_text(texto, encoding="utf-8")
    resultado["lineas_a2a"] = sum(1 for linea in texto.splitlines() if "A2A →" in linea or "A2A ←" in linea)
    return resultado


# ---------- navegador ----------


def capturar(pagina, nombre: str) -> None:
    """Agrega la franja con fecha y hora, expande la conversación y guarda la página completa."""
    pagina.evaluate(
        """(texto) => {
            document.getElementById('franja-captura')?.remove();
            const franja = document.createElement('div');
            franja.id = 'franja-captura';
            franja.textContent = texto;
            franja.style.cssText = 'background:#0f2a3d;color:#fff;font:600 14px/1.3 ui-monospace,Menlo,Consolas,monospace;'
                + 'padding:10px 16px;text-align:center;letter-spacing:.2px;width:100%;box-sizing:border-box;'
                + 'position:relative;z-index:2147483647;';  // por encima de la barra del visor JSON de Chrome
            document.body.prepend(franja);
        }""",
        f"LOCAL · captura automática (Playwright) contra la app real · {ahora()}",
    )
    pagina.add_style_tag(content=".conversacion{max-height:none!important;overflow:visible!important}")
    pagina.screenshot(path=str(CARPETA / nombre), full_page=True)
    print(f"  captura: {nombre}")


def enviar_y_esperar(pagina, texto: str) -> None:
    """Escribe la pregunta y espera a que termine (respuesta o aviso)."""
    pagina.locator("#pregunta").fill(texto)
    pagina.locator("#pregunta").press("Enter")
    expect(pagina.locator("#enviar")).to_be_enabled(timeout=ESPERA_MAXIMA_MS)


def tomar_capturas(solo_sin_gemini: bool, clave: str) -> list[dict]:
    resumen = []
    with sync_playwright() as pw:
        navegador = pw.chromium.launch(channel="chrome", headless=True, timeout=30000)
        contexto = navegador.new_context(
            viewport={"width": ANCHO, "height": ALTO},
            locale="es-CL",
            reduced_motion="reduce",
            service_workers="block",
        )
        pagina = contexto.new_page()
        pagina.set_default_timeout(20000)

        # 01 · /salud
        pagina.goto(f"{URL}/salud")
        capturar(pagina, "01-salud.png")

        # 02 · pantalla de ingreso con la clave escrita (el campo es password: se ve tapada)
        pagina.goto(URL + "/", wait_until="networkidle")
        pagina.locator("#clave").fill(clave)
        capturar(pagina, "02-ingreso.png")

        # 03 · intento con clave incorrecta: el servidor responde 401 antes de llamar a nadie
        pagina.locator("#clave").fill(CLAVE_INCORRECTA)
        pagina.locator("#clave").press("Enter")
        enviar_y_esperar(pagina, PREGUNTAS[0][1])
        expect(pagina.locator("#error-acceso")).to_be_visible()
        capturar(pagina, "03-clave-incorrecta.png")
        resumen.append({"captura": "03-clave-incorrecta.png", "aviso": " ".join(pagina.locator("#error-acceso").inner_text().split())})

        if solo_sin_gemini:
            navegador.close()
            return resumen

        # 04–06 · preguntas reales, cada una en una conversación nueva
        pagina.locator("#clave").fill(clave)
        pagina.locator("#clave").press("Enter")
        for archivo, pregunta, agente in PREGUNTAS:
            pagina.locator("#nueva-conversacion").click()
            print(f"  pregunta real → {archivo}")
            enviar_y_esperar(pagina, pregunta)
            ultimo = pagina.locator(".mensaje.asistente").last
            pies = [" ".join(t.split()) for t in ultimo.locator(".hora").all_inner_texts()]
            respuesta = " ".join(ultimo.locator(".burbuja").inner_text().split())
            if not any(p.startswith("Agente:") for p in pies):
                capturar(pagina, archivo.replace(".png", "-ERROR.png"))
                raise RuntimeError(f"{archivo}: no hubo respuesta de un agente ({pies} · {respuesta[:160]}).")
            capturar(pagina, archivo)
            resumen.append({"captura": archivo, "esperado": agente, "pies": pies, "respuesta": respuesta})
        navegador.close()
    return resumen


def main() -> int:
    analizador = argparse.ArgumentParser(description="Toma las capturas de evidencia de Alex.")
    analizador.add_argument("--sin-preguntas", action="store_true", help="no usa Gemini: solo /salud, ingreso y clave incorrecta")
    argumentos = analizador.parse_args()

    clave = secrets.token_urlsafe(32)  # solo en memoria
    servidor = None
    resumen: list[dict] = []
    error = None
    try:
        print("Levantando la app como Heroku (CLAVE_API temporal solo en el entorno)…")
        servidor = levantar_servidor(clave)
        print("App lista. Tomando capturas…")
        resumen = tomar_capturas(argumentos.sin_preguntas, clave)
    except Exception as excepcion:  # noqa: BLE001 - se informa en una línea y se limpia igual
        error = " ".join(str(excepcion).split())
        if clave in error:
            error = error.replace(clave, "[clave oculta]")
    finally:
        if servidor is not None:
            print("Deteniendo la app…")
            detener_servidor(servidor)
        revision = depurar_registro(clave) if REGISTRO.exists() else {}

    print("\nRESUMEN")
    for elemento in resumen:
        print(f"  {elemento['captura']}")
        for clave_dato in ("aviso", "pies", "respuesta"):
            if clave_dato in elemento:
                valor = elemento[clave_dato]
                valor = " | ".join(valor) if isinstance(valor, list) else valor
                print(f"      {clave_dato}: {valor[:150]}")
    print("\nREGISTRO registro-local.txt")
    print(f"  apariciones de la clave: {revision.get('clave', '?')}  (debe ser 0)")
    print(f"  rutas del repo reemplazadas por <carpeta-del-repo>: {revision.get('rutas_repo', '?')}")
    print(f"  otras rutas personales reemplazadas: {revision.get('rutas_personales', '?')}")
    print(f"  apariciones del nombre de usuario reemplazadas: {revision.get('usuario', '?')}")
    print(f"  líneas A2A (→ y ←): {revision.get('lineas_a2a', '?')}")
    if error:
        print(f"\nERROR: {error}")
        return 1
    return 0 if revision.get("clave", 1) == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
