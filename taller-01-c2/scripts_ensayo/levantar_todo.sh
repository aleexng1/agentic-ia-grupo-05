#!/usr/bin/env bash
# Ensayo general local del Grupo 5: levanta los 4 agentes (8003-8006) y el coordinador
# (8002) en esta terminal. Ctrl+C apaga todo. No es evidencia y no va en el zip.
#
# Uso (Terminal de Mint, desde taller-01-c2/):
#   bash scripts_ensayo/levantar_todo.sh

set -u

AQUI="$(cd "$(dirname "$0")" && pwd)"
PROYECTO="$(cd "$AQUI/../proyecto" && pwd)"
LOGS="$AQUI/logs"
UVICORN="$PROYECTO/.venv/bin/uvicorn"

if [[ ! -x "$UVICORN" ]]; then
  echo "Falta el entorno: $PROYECTO/.venv (créalo e instala requirements.txt)." >&2
  exit 1
fi
if [[ ! -f "$PROYECTO/.env" ]]; then
  echo "Falta $PROYECTO/.env con GOOGLE_API_KEY y MODELO." >&2
  exit 1
fi
for puerto in 8002 8003 8004 8005 8006; do
  if ss -ltn 2>/dev/null | grep -q ":$puerto "; then
    echo "El puerto $puerto ya está ocupado. Apaga lo que esté corriendo ahí y vuelve a intentar." >&2
    exit 1
  fi
done

# shellcheck source=variables_ensayo.sh
source "$AQUI/variables_ensayo.sh"
mkdir -p "$LOGS"
cd "$PROYECTO" || exit 1

PIDS=()

apagar() {
  echo
  echo "Apagando los servidores..."
  kill "${PIDS[@]}" 2>/dev/null
  wait 2>/dev/null
  echo "Todo apagado."
  exit 0
}
trap apagar INT TERM

levantar() {  # nombre módulo puerto
  "$UVICORN" "$2:app" --host 127.0.0.1 --port "$3" >"$LOGS/$1.log" 2>&1 &
  PIDS+=("$!")
}

esperar() {  # nombre puerto
  for _ in $(seq 1 60); do
    if curl -s -m 2 -o /dev/null "http://127.0.0.1:$2/salud"; then
      echo "  ✓ $1 responde en el $2"
      return 0
    fi
    sleep 0.5
  done
  echo "  ✗ $1 no respondió en el $2 (revisa $LOGS/$1.log)"
  return 1
}

echo "Levantando los 4 agentes..."
levantar matias    src.agente_matias.server    8003
levantar alex      src.agente_alex.server      8004
levantar eduardo   src.agente_eduardo.server   8005
levantar sebastian src.agente_sebastian.server 8006
esperar matias 8003
esperar alex 8004
esperar eduardo 8005
esperar sebastian 8006

echo "Levantando el coordinador (descubre los agentes al arrancar)..."
levantar coordinador src.coordinador.server 8002
esperar coordinador 8002
# El coordinador imprime «Supervisor con N agentes» al terminar de descubrir las fichas.
for _ in $(seq 1 40); do
  grep -q "Supervisor con" "$LOGS/coordinador.log" && break
  sleep 0.5
done
grep -h -E "Supervisor con|No se pudo descubrir" "$LOGS/coordinador.log" | sed 's/^/  /'

echo
echo "Listo. Deja esta terminal abierta mientras dure el ensayo."
echo "Registros: $LOGS/   ·   Ctrl+C apaga todo."
wait
