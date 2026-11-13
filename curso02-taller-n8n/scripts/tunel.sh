#!/usr/bin/env bash
# Levanta la API (uvicorn, puerto 8000) y un túnel rápido de Cloudflare hacia ella.
# Imprime la URL pública para n8n. Ctrl+C apaga las dos cosas.
#
#   ./scripts/tunel.sh

set -euo pipefail

PUERTO=8000
ESPERA_API=30      # segundos máximos esperando /health
ESPERA_TUNEL=60    # segundos máximos esperando la URL del túnel

CARPETA="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$CARPETA"

API_PID=""
TUNEL_PID=""
TMP="$(mktemp -d)"
LOG_TUNEL="$TMP/cloudflared.log"

apagar() {
    trap - EXIT
    echo
    echo "Apagando..."
    for pid in "$TUNEL_PID" "$API_PID"; do
        [[ -n "$pid" ]] && kill "$pid" 2>/dev/null || true
    done
    for pid in "$TUNEL_PID" "$API_PID"; do
        [[ -n "$pid" ]] && wait "$pid" 2>/dev/null || true
    done
    rm -rf "$TMP"
    echo "API y túnel apagados."
}
# Cualquier salida (fin normal, error o Ctrl+C) pasa por apagar().
trap apagar EXIT
trap 'exit 130' INT TERM

# ── Comprobaciones ───────────────────────────────────────────────────────────

command -v cloudflared >/dev/null || { echo "✘ No encuentro cloudflared. Instálalo primero."; exit 1; }
[[ -f .venv/bin/activate ]] || { echo "✘ No existe .venv en $CARPETA"; exit 1; }
[[ -f .env ]] || { echo "✘ No existe .env (copia .env.example y rellénalo)"; exit 1; }
if curl -s -o /dev/null "http://localhost:$PUERTO/health"; then
    echo "✘ Ya hay algo escuchando en el puerto $PUERTO. Apágalo antes de correr este script."
    exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate

# ── API ──────────────────────────────────────────────────────────────────────

echo "▶ Levantando la API en http://localhost:$PUERTO ..."
uvicorn api.app:app --port "$PUERTO" &
API_PID=$!

for ((i = 0; i < ESPERA_API * 2; i++)); do
    curl -s -o /dev/null "http://localhost:$PUERTO/health" && break
    kill -0 "$API_PID" 2>/dev/null || { echo "✘ La API se cayó al arrancar (mira el error de arriba)."; exit 1; }
    sleep 0.5
done
curl -s -o /dev/null "http://localhost:$PUERTO/health" || { echo "✘ /health no respondió en ${ESPERA_API}s."; exit 1; }
echo "✔ API arriba (/health responde)."

# ── Túnel ────────────────────────────────────────────────────────────────────

echo "▶ Abriendo el túnel de Cloudflare ..."
cloudflared tunnel --no-autoupdate --url "http://localhost:$PUERTO" >"$LOG_TUNEL" 2>&1 &
TUNEL_PID=$!

URL=""
for ((i = 0; i < ESPERA_TUNEL * 2; i++)); do
    URL="$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$LOG_TUNEL" | head -1 || true)"
    [[ -n "$URL" ]] && break
    kill -0 "$TUNEL_PID" 2>/dev/null || break
    sleep 0.5
done

if [[ -z "$URL" ]]; then
    echo "✘ No obtuve la URL del túnel. Salida de cloudflared:"
    cat "$LOG_TUNEL"
    exit 1
fi

cat <<EOF

════════════════════════════════════════════════════════════════════════
  Túnel listo

  URL pública :  $URL
  Para n8n    :  $URL/chat
                 (POST, cabecera X-API-Key con tu API_KEY)

  Probar      :  python scripts/probar_tunel.py $URL

  La URL cambia cada vez que reinicias este script.
  Ctrl+C para apagar la API y el túnel.
════════════════════════════════════════════════════════════════════════

EOF

# Espera hasta Ctrl+C o hasta que se caiga uno de los dos procesos.
set +e
wait -n "$API_PID" "$TUNEL_PID"
echo "✘ La API o el túnel se detuvo solo."
exit 1
