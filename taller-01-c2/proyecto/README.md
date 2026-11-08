# Taller A2A · Grupo 5 · Planificador de ferias y eventos

Cada integrante construyó un agente con una habilidad concreta. Los agentes se
comunican por A2A y un coordinador (supervisor) elige a cuál derivar cada pregunta.

## Identificación

**Grupo 5**

| Integrante | Agente | Habilidad |
|------------|--------|-----------|
| Matias Muñoz | Agente de Matias (`src/agente_matias/`) | Programa, actividades y horarios de la feria |
| Alex Nail | Agente de Alex (`src/agente_alex/`) | Lugares y capacidad |
| Eduardo Basaure | Agente de Eduardo (`src/agente_eduardo/`) | Presupuesto y costos estimados |
| Sebastian Mardones | Agente de Sebastian (`src/agente_sebastian/`) | Comida y opciones de catering |

Los agentes de Alex, Eduardo y Sebastian se ejecutan en sus computadores y se suman
por su dirección pública (ver `compañeros.md`).

## Contenido del proyecto

- `blueprint-Matias.md`: tabla del agente de Matias (qué hace, qué no hace, herramienta).
- `src/agente_matias/`: `tools.py`, `prompts.py`, `graph.py` y `server.py`.
- `src/coordinador/`: supervisor que lee las fichas de los agentes y deriva cada pregunta.
- `src/comun/`: servidor A2A, ficha y panel web compartidos por todos los agentes.
- `src/agente_viajes/` y `src/agente_restaurantes/`: agentes de ejemplo de la clase.
  No se usan en el catálogo del coordinador de este grupo.
- `scripts/`: túnel de Cloudflare y scripts de prueba.
- `evidencias/`: capturas y archivos de respaldo de cada paso.

## Instalación

Requiere Python 3.12. Desde la raíz del proyecto:

```powershell
# Windows (PowerShell)
py -3.12 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

```bash
# macOS
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`requirements-crew.txt` solo sirve para el agente de restaurantes de la clase
(entorno `.venv-crew`); no es necesario para este taller.

## Configuración

Copia `.env.example` a `.env` y escribe tu clave de Gemini en `GOOGLE_API_KEY`:

```powershell
Copy-Item .env.example .env
```

| Variable | Para qué sirve |
|----------|----------------|
| `GOOGLE_API_KEY` | Clave de Gemini. Nunca se entrega ni se sube. |
| `MODELO` | Modelo de Gemini que usa el proyecto. |
| `URL_MATIAS` | Dirección local del agente de Matias (`http://127.0.0.1:8003`). |
| `URL_COORDINADOR` | Dirección local del coordinador (`http://127.0.0.1:8002`). |
| `URL_PUBLICA` | Dirección HTTPS del túnel de Cloudflare; la ficha la publica. |
| `URLS_AGENTES` | Direcciones HTTPS de los agentes de los compañeros, separadas por comas. |

## Probar el agente de Matias sin servidor

Con el entorno activo y desde la raíz:

```powershell
$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
python main.py matias "Arma un programa de 4 horas para una feria tecnológica con público familiar desde las 10:00" --saltos
python main.py matias "¿Qué vuelos hay a Lima?" --saltos
python main.py matias --diagrama
```

`--saltos` muestra los nodos y la herramienta usada (`armar_programa`); la segunda
pregunta no es de su tema y la rechaza. `--diagrama` imprime el grafo en Mermaid.

## Levantar el servidor y ver la ficha

```powershell
# terminal 1
python -m uvicorn src.agente_matias.server:app --port 8003

# terminal 2: la ficha
Invoke-RestMethod http://127.0.0.1:8003/.well-known/agent-card.json | ConvertTo-Json -Depth 10
```

Este proyecto usa `a2a-sdk` 1.x: el método JSON-RPC se llama `SendMessage` y requiere
la cabecera `A2A-Version: 1.0`:

```powershell
$cuerpo = @{ jsonrpc="2.0"; id="1"; method="SendMessage"; params=@{ message=@{ role="ROLE_USER"; messageId="m1"; contextId=[guid]::NewGuid().ToString(); parts=@(@{ text="Arma un programa de 3 horas para una feria infantil desde las 15:00" }) } } } | ConvertTo-Json -Depth 10
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8003/ -ContentType "application/json; charset=utf-8" -Headers @{ "A2A-Version" = "1.0" } -Body ([System.Text.Encoding]::UTF8.GetBytes($cuerpo)) | ConvertTo-Json -Depth 10
```

La respuesta viene en `message.parts[0].text`.

## Publicar el agente con Cloudflare

```powershell
# terminal 1: el agente corriendo en el 8003
# terminal 2: el túnel
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\scripts\tunel.ps1 8003
```

Copia la dirección HTTPS que imprime a `URL_PUBLICA` en `.env` y reinicia el agente.
Cierra el túnel con `Ctrl+C` al terminar: mientras esté abierto, cualquiera con la
dirección puede usar el agente y gastar la clave.

## Coordinador con los agentes del grupo

Pega en `URLS_AGENTES` las direcciones de Alex, Eduardo y Sebastian y reinicia el coordinador:

```powershell
python -m uvicorn src.coordinador.server:app --port 8002
# → Supervisor con N agentes

python main.py coordinador "¿Qué actividades puede tener una feria infantil de 3 horas?" --saltos
```

El coordinador siempre incluye al agente de Matias (`URL_MATIAS`) y suma los de `URLS_AGENTES`.

## Qué no se entrega

`.env`, `.venv/`, `.venv-crew/` y `__pycache__/`. Sí va `.env.example`, sin claves.
