# Variables del ensayo general local (todas en 127.0.0.1, sin túneles).
# Se cargan con: source scripts_ensayo/variables_ensayo.sh
# python-dotenv no pisa variables que ya existen, así que estas ganan sobre proyecto/.env
# (de ahí solo se usan GOOGLE_API_KEY y MODELO). El .env no se modifica.
export URL_PUBLICA=""
export URL_COORDINADOR="http://127.0.0.1:8002"
export URL_MATIAS="http://127.0.0.1:8003"
export URL_ALEX="http://127.0.0.1:8004"
export URL_EDUARDO="http://127.0.0.1:8005"
export URL_SEBASTIAN="http://127.0.0.1:8006"
export URLS_AGENTES="http://127.0.0.1:8004,http://127.0.0.1:8005,http://127.0.0.1:8006"
export PYTHONIOENCODING="utf-8"
export PYTHONUNBUFFERED="1"
export PYTHONDONTWRITEBYTECODE="1"
