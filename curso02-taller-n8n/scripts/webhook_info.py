"""Muestra el estado del webhook del bot de Telegram (getWebhookInfo).

    python scripts/webhook_info.py

Lee TELEGRAM_TOKEN desde .env y nunca lo imprime: el token va dentro de la URL de la
API de Telegram, así que cualquier mensaje de error se limpia antes de mostrarse.
"""

import json
import sys
from pathlib import Path

import httpx
from dotenv import dotenv_values

RAIZ = Path(__file__).resolve().parent.parent
TIMEOUT = 20


def leer_token() -> str:
    token = (dotenv_values(RAIZ / ".env").get("TELEGRAM_TOKEN") or "").strip()
    if not token:
        sys.exit(
            "✘ Falta TELEGRAM_TOKEN en .env.\n"
            "  Agrega la línea TELEGRAM_TOKEN=<token de @BotFather> en curso02-taller-n8n/.env y vuelve a correr."
        )
    return token


def sin_token(texto: str, token: str) -> str:
    return texto.replace(token, "<TELEGRAM_TOKEN>")


def main() -> None:
    token = leer_token()
    url = f"https://api.telegram.org/bot{token}/getWebhookInfo"

    try:
        r = httpx.get(url, timeout=TIMEOUT)
    except httpx.HTTPError as e:
        sys.exit(f"✘ No pude conectar con Telegram: {type(e).__name__}: {sin_token(str(e), token)}")

    try:
        datos = r.json()
    except ValueError:
        sys.exit(f"✘ Telegram respondió HTTP {r.status_code} sin JSON: {sin_token(r.text[:300], token)}")

    print(f"HTTP {r.status_code}")
    print(sin_token(json.dumps(datos, ensure_ascii=False, indent=2), token))

    if r.status_code == 401:
        sys.exit("✘ Telegram rechazó el token (401): revisa TELEGRAM_TOKEN en .env.")
    if not datos.get("ok"):
        sys.exit(1)


if __name__ == "__main__":
    main()
