#!/usr/bin/env bash
# Hace 12 preguntas al coordinador (con los 4 agentes ya levantados por levantar_todo.sh)
# y muestra a quién fue cada una y el motivo del supervisor. No es evidencia.
#
# Uso, en otra terminal y desde taller-01-c2/:
#   bash scripts_ensayo/preguntas_ensayo.sh

set -u
AQUI="$(cd "$(dirname "$0")" && pwd)"
PROYECTO="$(cd "$AQUI/../proyecto" && pwd)"
# shellcheck source=variables_ensayo.sh
source "$AQUI/variables_ensayo.sh"
cd "$PROYECTO" || exit 1

# tipo|esperado|pregunta
PREGUNTAS=(
  "clara|Matias|Tengo una feria cultural de 3 horas desde las 16:00 para público familiar, ¿qué actividades pongo y a qué hora?"
  "clara|Matias|Para una feria tecnológica de 4 horas con estudiantes, ¿qué charlas o talleres hago y en qué orden?"
  "clara|Alex|Voy a hacer una feria tecnológica para 150 personas, ¿dónde la hago?"
  "clara|Alex|Vamos a hacer una feria gastronómica para unas 250 personas y queremos que sea al aire libre, ¿qué lugar nos sirve?"
  "clara|Eduardo|¿Cuál es el presupuesto simulado de una feria infantil para 60 personas y 2 horas?"
  "clara|Eduardo|¿Cuánta plata necesito más o menos para una feria gastronómica de 120 personas que dura 3 horas?"
  "clara|Sebastian|Feria gastronómica de 5 horas desde las 11:00 para 200 personas, 20 son vegetarianas, ¿qué servimos?"
  "clara|Sebastian|Van a venir 80 niños a una feria infantil de 3 horas que parte a las 11:00 y 6 son celíacos, ¿qué les damos de comer?"
  "ambigua|Eduardo o Sebastian|¿Cuánto cuesta el catering para 100 personas?"
  "ambigua|Alex o Sebastian|¿Qué lugar sirve para una feria con food trucks?"
  "ambigua|Matias o Sebastian|¿A qué hora conviene el almuerzo?"
  "nadie|ninguno|¿Quién ganó el mundial de 1962?"
)

numero=0
for linea in "${PREGUNTAS[@]}"; do
  numero=$((numero + 1))
  IFS='|' read -r tipo esperado pregunta <<<"$linea"
  salida="$(.venv/bin/python main.py coordinador "$pregunta" --saltos 2>&1)"
  elegido="$(grep -m1 '^Agente elegido:' <<<"$salida" | sed 's/^Agente elegido: //')"
  motivo="$(grep -m1 '^Motivo:' <<<"$salida" | sed 's/^Motivo: //')"
  respuesta="$(grep -m1 -A3 '^Respuesta:' <<<"$salida" | grep -v '^\[' | tr '\n' ' ' | cut -c1-220)"
  echo "#$numero [$tipo] esperado: $esperado"
  echo "  Pregunta:  $pregunta"
  echo "  Elegido:   ${elegido:-(sin decisión)}"
  echo "  Motivo:    ${motivo:-(sin motivo)}"
  echo "  Respuesta: $respuesta"
  grep -m1 -E '^No se pudo' <<<"$salida" | sed 's/^/  ERROR:     /'
  echo
done
