"""Prueba la API a través del túnel.

    python scripts/probar_tunel.py https://xxxx.trycloudflare.com

Lee API_KEY desde .env (nunca la imprime) y hace 3 pruebas:
GET /health (200), POST /chat sin clave (401) y POST /chat con clave (200).
"""

import json
import sys
from pathlib import Path

import httpx
from dotenv import dotenv_values

RAIZ = Path(__file__).resolve().parent.parent
TIMEOUT = 60
TEXTO = "quiero comprar un televisor"


def leer_api_key() -> str:
    clave = (dotenv_values(RAIZ / ".env").get("API_KEY") or "").strip()
    if not clave:
        sys.exit("✘ API_KEY no está en .env")
    return clave


def base_url(arg: str) -> str:
    url = arg.strip().rstrip("/")
    if url.endswith("/chat"):
        url = url[: -len("/chat")]
    if not url.startswith(("http://", "https://")):
        sys.exit(f"✘ URL inválida: {arg!r} (debe empezar con https://)")
    return url


def mostrar(r: httpx.Response) -> str:
    try:
        return json.dumps(r.json(), ensure_ascii=False)
    except ValueError:
        return r.text[:300]


def probar(nombre: str, esperado: int, peticion, validar=None) -> bool:
    print(f"▶ {nombre}")
    try:
        r = peticion()
    except httpx.HTTPError as e:
        print(f"  ✘ error de conexión: {type(e).__name__}: {e}\n")
        return False
    ok = r.status_code == esperado and (validar is None or validar(r))
    print(f"  código   : {r.status_code} (esperado {esperado})")
    print(f"  respuesta: {mostrar(r)}")
    print(f"  {'✔ OK' if ok else '✘ FALLÓ'}\n")
    return ok


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Uso: python scripts/probar_tunel.py https://xxxx.trycloudflare.com")
    url = base_url(sys.argv[1])
    clave = leer_api_key()
    body = {"user_id": "probar-tunel", "texto": TEXTO}

    print(f"Probando {url}  (timeout {TIMEOUT}s)\n")
    with httpx.Client(timeout=TIMEOUT) as c:
        resultados = [
            probar("GET /health", 200, lambda: c.get(f"{url}/health")),
            probar("POST /chat sin clave", 401, lambda: c.post(f"{url}/chat", json=body)),
            probar(
                f"POST /chat con clave · {TEXTO!r}", 200,
                lambda: c.post(f"{url}/chat", json=body, headers={"X-API-Key": clave}),
                validar=lambda r: {"ruta", "motivo", "respuesta"} <= set(r.json()),
            ),
        ]

    print(f"Resultado: {sum(resultados)}/{len(resultados)} pruebas OK")
    sys.exit(0 if all(resultados) else 1)


if __name__ == "__main__":
    main()
