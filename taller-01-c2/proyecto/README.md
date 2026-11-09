# Taller A2A · Grupo 5 · Planificador de ferias y eventos

Cada integrante construyó un agente con una habilidad concreta. Los agentes se
comunican por A2A y un coordinador (supervisor) lee sus fichas y elige a cuál derivar
cada pregunta.

## Identificación

**Grupo 5** · Taller 1 del Curso 2 · tema común: planificador de ferias y eventos.

| Integrante | Agente | Habilidad (skill) | Herramienta | Puerto | Carpeta |
|------------|--------|-------------------|-------------|--------|---------|
| Matias Muñoz | Agente de Matias | Programa, actividades y horarios | `armar_programa` | 8003 | `src/agente_matias/` |
| Alex Nail | Agente de Alex | Lugares y capacidad | `buscar_recintos` | 8004 | `src/agente_alex/` |
| Eduardo Basaure | Agente de Eduardo | Presupuesto y costos estimados | `estimar_presupuesto` | 8005 | `src/agente_eduardo/` |
| Sebastian Mardones | Agente de Sebastian | Comida y catering | `armar_catering` | 8006 | `src/agente_sebastian/` |
| (todos) | Coordinador | Elige el agente y delega por A2A | — | 8002 | `src/coordinador/` |

Cada agente corre en el computador de su dueño y se publica con un túnel de Cloudflare.
Las direcciones públicas y las fichas están en `compañeros.md`, junto a esta carpeta.

## Contenido del proyecto

- `main.py`: corre cualquier agente desde la terminal, sin servidor.
- `src/agente_matias/`, `src/agente_alex/`, `src/agente_eduardo/`, `src/agente_sebastian/`:
  un agente por integrante, cada uno con `tools.py` (la herramienta, que hace las
  cuentas con datos ficticios), `prompts.py`, `graph.py` y `server.py` (la ficha A2A).
  El de Eduardo trae además `demo.html`, una página de prueba en `/demo`.
- `src/coordinador/`: supervisor que descubre los agentes por su ficha y deriva cada pregunta.
- `src/comun/`: servidor A2A, ficha y panel web compartidos por todos los agentes.
- `src/agente_viajes/` y `src/agente_restaurantes/`: agentes de ejemplo de la clase.
  No se usan en el catálogo de este grupo.
- `tests/`: pruebas de las herramientas (`test_tools_alex.py`, `test_tools_eduardo.py`,
  `test_tools_sebastian.py`). No usan la clave de Gemini.
- `scripts/`: túnel de Cloudflare (`tunel.sh`, `tunel.ps1`) y scripts de verificación.

Junto a `proyecto/` (en la raíz de la entrega) van los `blueprint-NOMBRE.md`,
`compañeros.md`, `evidencias/NOMBRE/` y el `documento-entrega.pdf`. La pauta muestra una sola
carpeta `evidencias/`; usamos una subcarpeta por integrante porque los cuatro tienen archivos
con el mismo nombre (`01-saltos.png`, `02-ficha.json`, …).

## Instalación

Requiere Python 3.12. Desde esta carpeta (`proyecto/`):

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

```bash
# Linux (Ubuntu, Debian, Linux Mint)
sudo apt install python3.12-venv   # solo si "venv" no está disponible
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`requirements-crew.txt` solo sirve para el agente de restaurantes de la clase
(entorno `.venv-crew`); no es necesario para este taller.

## Configuración

Copia `.env.example` a `.env` y escribe tu clave de Gemini en `GOOGLE_API_KEY`:

```powershell
Copy-Item .env.example .env      # Windows
```

```bash
cp .env.example .env             # macOS y Linux
```

| Variable | Para qué sirve |
|----------|----------------|
| `GOOGLE_API_KEY` | Clave de Gemini. Nunca se entrega ni se sube. |
| `MODELO` | Modelo de Gemini que usa el proyecto. |
| `URL_COORDINADOR` | Dirección local del coordinador (`http://127.0.0.1:8002`). |
| `URL_MATIAS` | Dirección del agente de Matias (`http://127.0.0.1:8003`). Solo Matias la deja llena en la prueba grupal; los demás la dejan vacía. |
| `URL_ALEX`, `URL_EDUARDO`, `URL_SEBASTIAN` | Dirección local de cada agente (puertos 8004, 8005 y 8006). |
| `URL_PUBLICA` | Dirección HTTPS de **tu** túnel de Cloudflare; tu ficha la publica. Vacía si no hay túnel. |
| `URLS_AGENTES` | Direcciones que suma el coordinador, separadas por comas: tu agente local y los túneles de los compañeros. |

El `.env` solo se lee al arrancar: si lo cambias, reinicia el agente o el coordinador.

## Probar cada agente sin servidor

Con el entorno activo y desde `proyecto/`. `--saltos` muestra los nodos y la herramienta
usada; una pregunta de otro tema se rechaza en un solo salto. `--diagrama` imprime el
grafo en Mermaid sin llamar al modelo.

En Windows, antes de correrlos, para que las tildes se vean bien:

```powershell
$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

### Agente de Matias (programa y horarios)

```powershell
python main.py matias "Arma un programa de 4 horas para una feria tecnológica con público familiar desde las 10:00" --saltos
python main.py matias "¿Qué vuelos hay a Lima?" --saltos
python main.py matias --diagrama
```

### Agente de Alex (lugares y capacidad)

```bash
python main.py alex "Voy a hacer una feria tecnológica para 150 personas, ¿dónde la hago?" --saltos
python main.py alex "¿Cuánto cuesta arrendar un salón?" --saltos
python main.py alex --diagrama
```

`buscar_recintos` exige un 10 % de holgura, calcula ocupación, m² por persona y stands, y
avisa cuando un recinto "queda grande".

### Agente de Eduardo (presupuesto y costos)

```bash
python main.py eduardo "¿Cuál es el presupuesto simulado de una feria tecnológica para 80 personas y 4 horas?" --saltos
python main.py eduardo "¿Qué recinto me recomiendas para 100 personas?" --saltos
python main.py eduardo --diagrama
```

Los importes son ficticios (CLP) y no incluyen impuestos. Con el servidor arriba, la
página de prueba está en `http://127.0.0.1:8005/demo`.

### Agente de Sebastian (comida y catering)

```powershell
$env:PYTHONIOENCODING = "utf-8"
python main.py sebastian "Voy a hacer una feria tecnológica de 4 horas desde las 10:00 para 150 personas, 12 son veganas. ¿Qué les sirvo?" --saltos
python main.py sebastian "¿Qué vuelos hay a Lima?" --saltos
python main.py sebastian --diagrama
python -m pytest tests -q
python -m uvicorn src.agente_sebastian.server:app --port 8006
```

`armar_catering` calcula los servicios (uno cada 2,5 horas, almuerzo si el evento cruza el
mediodía), las cantidades con 10 % de margen, el agua y los menús especiales.
Las pruebas de su herramienta están en `tests/test_tools_sebastian.py`.

## Levantar un agente como servidor y ver su ficha

Cada uno levanta el suyo en su puerto (Matias 8003, Alex 8004, Eduardo 8005, Sebastian 8006):

```bash
python -m uvicorn src.agente_alex.server:app --port 8004
```

La ficha queda en `http://127.0.0.1:PUERTO/.well-known/agent-card.json`:

```powershell
Invoke-RestMethod http://127.0.0.1:8003/.well-known/agent-card.json | ConvertTo-Json -Depth 10   # Windows
```

```bash
curl -s http://127.0.0.1:8004/.well-known/agent-card.json   # macOS y Linux
```

### Mandar un mensaje A2A

Este proyecto usa `a2a-sdk` 1.3: el método JSON-RPC se llama `SendMessage` y requiere
la cabecera `A2A-Version: 1.0`:

```powershell
$cuerpo = @{ jsonrpc="2.0"; id="1"; method="SendMessage"; params=@{ message=@{ role="ROLE_USER"; messageId="m1"; contextId=[guid]::NewGuid().ToString(); parts=@(@{ text="Arma un programa de 3 horas para una feria infantil desde las 15:00" }) } } } | ConvertTo-Json -Depth 10
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8003/ -ContentType "application/json; charset=utf-8" -Headers @{ "A2A-Version" = "1.0" } -Body ([System.Text.Encoding]::UTF8.GetBytes($cuerpo)) | ConvertTo-Json -Depth 10
```

```bash
curl -s http://127.0.0.1:8004/ -H 'Content-Type: application/json' -H 'A2A-Version: 1.0' \
  -d '{"jsonrpc":"2.0","id":"1","method":"SendMessage","params":{"message":{"messageId":"m1","role":"ROLE_USER","parts":[{"text":"Feria gastronómica al aire libre para 200 personas, ¿dónde la hago?"}]}}}'
```

La respuesta viene en `result.message.parts[0].text`.

## Publicar el agente con Cloudflare

Se usa el túnel rápido de trycloudflare, sin cuenta. Instalación de `cloudflared`:
Windows `winget install Cloudflare.cloudflared`, macOS `brew install cloudflared`,
Linux con apt según https://pkg.cloudflare.com/.

```powershell
# Windows. Terminal 1: tu agente corriendo. Terminal 2: el túnel.
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\scripts\tunel.ps1 8003
```

```bash
# macOS y Linux. Terminal 1: tu agente corriendo. Terminal 2: el túnel.
bash scripts/tunel.sh 8004
```

Copia la dirección HTTPS que aparece en verde a `URL_PUBLICA` en `.env` y reinicia tu
agente. Si la dirección se pierde entre los registros, `curl -s http://127.0.0.1:20241/quicktunnel`
la devuelve. Cierra el túnel con `Ctrl+C` al terminar: mientras esté abierto, cualquiera
con la dirección puede usar el agente y gastar la clave.

## Coordinador con los agentes del grupo

En `.env`, `URLS_AGENTES` lleva tu agente local y los túneles de los compañeros,
separados por comas. `URL_MATIAS` queda vacía, salvo en el computador de Matias
(el coordinador la suma por su cuenta). Después levanta el coordinador:

```bash
python -m uvicorn src.coordinador.server:app --port 8002
# → Supervisor con 4 agentes

python main.py coordinador "¿Qué actividades puede tener una feria infantil de 3 horas?" --saltos
python main.py coordinador --diagrama
```

`--saltos` muestra el agente elegido y el motivo del supervisor. Para revisar que todos
respondan: `python -m scripts.verificar_agentes`.

## Pruebas

```bash
python -m pytest tests -q
```

Prueban las herramientas de Alex, Eduardo y Sebastian sin llamar al modelo.

## Diferencias con la guía del taller

El proyecto usa `a2a-sdk` 1.3, que cambia algunos nombres respecto de la guía:

- El método JSON-RPC es `SendMessage`, no `message/send`.
- Hay que enviar la cabecera `A2A-Version: 1.0`.
- Los roles son `ROLE_USER` y `ROLE_AGENT`.
- El texto de la respuesta viene en `result.message.parts`, no en `artifacts`.
- `sse-starlette` está en `requirements.txt`: sin ella el servidor A2A no arranca.
- En el navegador del celular las tildes de la ficha se ven mal ("tecnolÃ³gicas"): el
  servidor responde `application/json` sin `charset=utf-8`. La ficha es correcta (UTF-8).

## Qué no se entrega

`.env`, `.venv/`, `.venv-crew/`, `__pycache__/` y `.pytest_cache/`. Sí va `.env.example`, sin claves.
