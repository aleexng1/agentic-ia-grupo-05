#!/usr/bin/env bash
# Prueba el zip como lo haría quien lo corrige: lo descomprime en /tmp, crea un .venv
# nuevo, instala requirements.txt, copia el .env de Alex (no se muestra), corre pytest y
# una pregunta con --saltos a cada uno de los 4 agentes. Al terminar borra todo.
#
# Uso, desde taller-01-c2/:
#   bash entrega/probar_zip.sh

set -uo pipefail

BASE="$(cd "$(dirname "$0")/.." && pwd)"   # taller-01-c2/
ZIP="$BASE/entrega/grupo-5-taller-a2a.zip"
ENV_ORIGEN="$BASE/proyecto/.env"

[[ -f "$ZIP" ]] || { echo "Falta $ZIP. Ármalo con: bash entrega/armar_zip.sh" >&2; exit 1; }
[[ -f "$ENV_ORIGEN" ]] || { echo "Falta $ENV_ORIGEN (con GOOGLE_API_KEY)." >&2; exit 1; }
command -v python3.12 >/dev/null || { echo "Falta python3.12." >&2; exit 1; }

PRUEBA="$(mktemp -d /tmp/prueba-zip-XXXXXX)"
trap 'rm -rf "$PRUEBA"; echo "Carpeta de prueba borrada: $PRUEBA"' EXIT

echo "== 1. Descomprimir en $PRUEBA =="
unzip -q "$ZIP" -d "$PRUEBA"
cd "$PRUEBA/proyecto" || exit 1

echo "== 2. Entorno nuevo e instalación de requirements.txt =="
python3.12 -m venv .venv
.venv/bin/python -m pip install -q --upgrade pip
if ! .venv/bin/python -m pip install -q -r requirements.txt; then
  echo "✗ Falló la instalación de requirements.txt" >&2
  exit 1
fi
echo "✓ Dependencias instaladas"

echo "== 3. .env (copiado de proyecto/.env, sin túnel) =="
cp "$ENV_ORIGEN" .env
chmod 600 .env
sed -i -E 's#^URL_PUBLICA=.*#URL_PUBLICA=#' .env
echo "✓ .env listo (la clave no se muestra)"

export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
fallos=0

echo "== 4. pytest =="
if .venv/bin/python -m pytest tests -q -p no:cacheprovider; then
  echo "✓ pytest"
else
  echo "✗ pytest"; fallos=1
fi

preguntar() {  # agente pregunta
  echo
  echo "--- python main.py $1 \"$2\" --saltos"
  local salida
  salida="$(.venv/bin/python main.py "$1" "$2" --saltos 2>&1)"
  echo "$salida" | grep -E '^(Nodo|Herramienta|Saltos totales)' | sed 's/^/    /'
  echo "$salida" | grep -E '^Respuesta' | cut -c1-160 | sed 's/^/    /'
  if ! echo "$salida" | grep -q '^Herramienta:'; then
    echo "    ✗ no usó su herramienta"; fallos=1
  fi
}

echo
echo "== 5. Una pregunta de su tema a cada agente =="
preguntar matias "Necesito armar el programa de una feria infantil de 3 horas que parta a las 15:00."
preguntar alex "Voy a hacer una feria tecnológica para 150 personas, ¿dónde la hago?"
preguntar eduardo "¿Cuál es el presupuesto simulado de una feria tecnológica para 80 personas y 4 horas?"
preguntar sebastian "Voy a hacer una feria tecnológica de 4 horas desde las 10:00 para 150 personas, 12 son veganas. ¿Qué les sirvo?"

echo
if (( fallos )); then
  echo "RESULTADO: hubo fallos (revisa arriba)."
  exit 1
fi
echo "RESULTADO: el zip funciona desde cero."
