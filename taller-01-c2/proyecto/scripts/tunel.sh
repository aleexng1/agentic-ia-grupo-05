#!/usr/bin/env bash

set -o pipefail

puerto="${1:-8000}"
if ! [[ "$puerto" =~ ^[0-9]+$ ]] || (( puerto < 1 || puerto > 65535 )); then
  printf 'Error: el puerto debe ser un número entre 1 y 65535.\n' >&2
  exit 2
fi

if ! command -v cloudflared >/dev/null 2>&1; then
  printf 'cloudflared no está instalado. Instálalo así:\n' >&2
  printf '  macOS: brew install cloudflared\n' >&2
  printf '  Linux (Ubuntu, Debian, Linux Mint): sigue las instrucciones de apt en https://pkg.cloudflare.com/\n' >&2
  printf '    o instala el .deb de https://github.com/cloudflare/cloudflared/releases/latest\n' >&2
  exit 1
fi

printf 'Abriendo un túnel al servidor local http://127.0.0.1:%s\n' "$puerto"
printf 'Mantén esta terminal abierta mientras uses el túnel.\n\n'

cloudflared tunnel --url "http://127.0.0.1:${puerto}" 2>&1 |
  while IFS= read -r linea; do
    printf '%s\n' "$linea"
    if [[ "$linea" =~ (https://[[:alnum:].-]+\.trycloudflare\.com) ]]; then
      direccion="${BASH_REMATCH[1]}"
      if [[ "${direccion_mostrada:-}" != "$direccion" ]]; then
        direccion_mostrada="$direccion"
        printf '\n%s\n' '============================================================'
        printf '%s\n' '                 DIRECCIÓN HTTPS PÚBLICA'
        printf '\033[1;32m%s\033[0m\n' "$direccion"
        printf '%s\n' '============================================================'
        printf '%s\n' 'Pega esta dirección en URL_PUBLICA de tu .env y reinicia tu agente; pásasela a tu compañero para que la ponga en su URLS_AGENTES.'
        printf '\n'
      fi
    fi
  done
