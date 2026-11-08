#!/usr/bin/env bash
# Arma grupo-5-taller-a2a.zip con la estructura de la pauta:
#   documento-entrega.pdf, blueprint-NOMBRE.md, compañeros.md, proyecto/, evidencias/
# Sin .env, .venv*, __pycache__, .pytest_cache, ni archivos internos del grupo
# (README del taller, PRUEBA-GRUPAL.md, entrega/, scripts_ensayo/, documento-NOMBRE.md sueltos).
# Al final lista el contenido y busca claves o .env dentro del zip.
#
# Uso, desde taller-01-c2/ (primero arma el PDF con entrega/armar_documento.py):
#   bash entrega/armar_zip.sh

set -euo pipefail

BASE="$(cd "$(dirname "$0")/.." && pwd)"   # taller-01-c2/
ZIP="$BASE/entrega/grupo-5-taller-a2a.zip"
PDF="$BASE/entrega/documento-entrega.pdf"

if [[ ! -f "$PDF" ]]; then
  echo "Falta $PDF. Arma primero el documento:" >&2
  echo "  entrega/.venv-entrega/bin/python entrega/armar_documento.py" >&2
  exit 1
fi

TEMPORAL="$(mktemp -d)"
trap 'rm -rf "$TEMPORAL"' EXIT
DESTINO="$TEMPORAL/zip"
mkdir -p "$DESTINO"

# 1. Copia solo lo que pide la pauta.
cp "$PDF" "$DESTINO/"
cp "$BASE"/blueprint-*.md "$DESTINO/"
cp "$BASE/compañeros.md" "$DESTINO/"
rsync -a \
  --exclude='.env' --exclude='.venv*' --exclude='__pycache__' --exclude='*.pyc' \
  --exclude='.pytest_cache' --exclude='.gitkeep' --exclude='*.log' \
  "$BASE/proyecto" "$DESTINO/"
rsync -a --exclude='.gitkeep' "$BASE/evidencias" "$DESTINO/"

# 2. Arma el zip (sin carpeta raíz extra: al abrirlo se ven directamente los archivos).
rm -f "$ZIP"
(cd "$DESTINO" && zip -qrX "$ZIP" .)

# 3. Revisión del contenido (el listado se lee una vez y se revisa sobre esa copia).
LISTA="$(unzip -Z1 "$ZIP" | sort)"
echo "== Contenido de $(basename "$ZIP") =="
sed 's/^/  /' <<<"$LISTA"
echo
echo "Archivos: $(grep -vc '/$' <<<"$LISTA")  ·  Tamaño: $(du -h "$ZIP" | cut -f1)"

problemas=0
prohibidos="$(grep -E '(^|/)(\.env$|\.venv[^/]*/|__pycache__/|\.pytest_cache/)|\.pyc$' <<<"$LISTA" || true)"
if [[ -n "$prohibidos" ]]; then
  echo "✗ Archivos que no deben ir:"; echo "$prohibidos" | sed 's/^/    /'; problemas=1
else
  echo "✓ Sin .env, .venv, __pycache__ ni .pytest_cache"
fi

# Busca claves en los archivos de texto (-I salta las imágenes y el PDF).
claves="$(grep -rIlE 'AIza[0-9A-Za-z_-]{20,}|^GOOGLE_API_KEY=.+' "$DESTINO" || true)"
if [[ -n "$claves" ]]; then
  echo "✗ Posibles claves en:"; echo "$claves" | sed "s#$DESTINO/#    #"; problemas=1
else
  echo "✓ Sin claves (AIza… ni GOOGLE_API_KEY con valor)"
fi

for requerido in documento-entrega.pdf compañeros.md proyecto/main.py proyecto/requirements.txt \
                 proyecto/.env.example proyecto/README.md; do
  grep -qx "$requerido" <<<"$LISTA" || { echo "✗ Falta $requerido"; problemas=1; }
done
for nombre in Matias Alex Eduardo Sebastian; do
  grep -qx "blueprint-$nombre.md" <<<"$LISTA" || { echo "✗ Falta blueprint-$nombre.md"; problemas=1; }
done
for carpeta in matias alex eduardo sebastian; do
  grep -q "^evidencias/$carpeta/." <<<"$LISTA" || { echo "✗ Falta evidencias/$carpeta/"; problemas=1; }
done

if (( problemas )); then
  echo "El zip tiene problemas: se borra." >&2
  rm -f "$ZIP"
  exit 1
fi
echo "✓ Estructura completa"
echo "Listo: $ZIP"
