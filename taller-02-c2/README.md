# Taller 2 del Curso 2 · Implementa y entrega tu agente

## Opción elegida

Una **página web con chat**, servida por una **API FastAPI protegida con clave**, que por
detrás usa el mismo coordinador y los cuatro agentes del taller anterior, comunicados por
A2A. Se entrega corriendo en local y además desplegada en Heroku, todo en **una sola app**.

## El problema que resuelve

Organizar una feria obliga a resolver cosas distintas: el programa y los horarios, el
lugar y su capacidad, el presupuesto y la comida. En el taller anterior cada tema tenía
su agente, pero para usarlos había que levantar cinco servidores y consultar desde la
terminal. Aquí una persona sin conocimientos técnicos abre una página, escribe su
pregunta y el coordinador elige al agente que corresponde, mostrando quién respondió y
por qué. Los datos son de demostración: no se reserva ni se paga nada.

## Qué se reutiliza del taller A2A

El proyecto parte de una copia de `taller-01-c2/proyecto` (ese taller queda intacto):

- Los cuatro agentes, cada uno con su `tools.py`, `prompts.py` y `graph.py`, y sus pruebas.
- El coordinador (grafo supervisor) y su cliente A2A, que descubre las fichas y delega.
- El código común de `src/comun` (ejecutor A2A, fichas, panel) y el contrato
  `responder(texto, context_id)`.
- `main.py` para correr cualquier agente desde la terminal (`--saltos`, `--diagrama`).

Lo que cambia: en vez de un servidor por agente hay una sola aplicación (`proyecto/app.py`)
con el coordinador en la raíz y cada agente bajo `/agentes/{nombre}`. Se quitaron los
agentes de ejemplo de la clase (viajes y restaurantes).

## Integrantes

| Integrante | Aporte |
| --- | --- |
| Alex | Base e integración |
| Matías | Seguridad y errores |
| Eduardo | Frontend del chat |
| Sebastián | Heroku y operación |

## Preparación manual

## Instalación

Requisitos: **Python 3.12**, `git` y conexión a internet. Todos los comandos se corren
desde la carpeta `taller-02-c2/proyecto` del repositorio.

**Linux y macOS**

```bash
cd taller-02-c2/proyecto
python3.12 -m venv .venv          # en macOS con Homebrew también sirve: python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

**Windows (PowerShell)**

```powershell
cd taller-02-c2\proyecto
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1      # si lo bloquea: Set-ExecutionPolicy -Scope Process Bypass
pip install -r requirements.txt
Copy-Item .env.example .env
```

Después abre `.env` y pega tu clave de Gemini en `GOOGLE_API_KEY` (ver Configuración).

## Configuración

Todas las variables van en `proyecto/.env`, que nunca se sube al repositorio
(`.env.example` es la plantilla, sin claves).

| Variable | Para qué sirve |
| --- | --- |
| `GOOGLE_API_KEY` | Clave propia de Gemini (Google AI Studio). Sin ella los agentes no pueden responder. |
| `MODELO` | Modelo de Gemini que usan el coordinador y los agentes (por defecto `gemini-3.5-flash-lite`). |
| `PUERTO` | Puerto local de la app (por defecto `8000`). Debe ser el mismo del `--port` de uvicorn; en Heroku manda `PORT`. |
| `URL_BASE` | Dirección pública de la app, sin barra final. Las fichas se publican como `URL_BASE/agentes/{nombre}`. En local, `http://127.0.0.1:8000`. |
| `CLAVE_API` | Clave de acceso a la API: ver la sección Seguridad, más abajo. |
| `URLS_AGENTES` | Vacía = el coordinador usa los cuatro agentes de esta misma app. Con direcciones separadas por comas = modo distribuido (un agente por computador, como en el taller anterior). |

## Cómo iniciar / probar / detener

**Iniciar** (con el entorno virtual activado, desde `taller-02-c2/proyecto`):

```bash
uvicorn app:app --reload --port 8000
```

El chat queda en **http://127.0.0.1:8000/**. La primera pregunta tarda un poco más: en ese
momento el coordinador descarga las fichas de los cuatro agentes.

**Probar**, en otra terminal (también con el entorno activado):

```bash
# La app está viva: responde {"ok":true}
curl http://127.0.0.1:8000/salud              # Windows: curl.exe http://127.0.0.1:8000/salud

# Ficha A2A de un agente
curl http://127.0.0.1:8000/agentes/alex/.well-known/agent-card.json

# Un agente por sí solo, sin servidor, mostrando nodos y herramientas
python main.py alex "Voy a hacer una feria tecnológica para 150 personas, ¿dónde la puedo hacer?" --saltos

# El coordinador completo (necesita la app levantada: consulta a los agentes por A2A)
python main.py coordinador "Necesito el programa de una feria infantil de 3 horas desde las 15:00" --saltos

# Pruebas automáticas (no usan la clave de Gemini)
python -m pytest
```

Mientras la app corre, su terminal muestra una línea por cada paso de una consulta:

```text
2026-11-12 20:40:10 INFO    [coordinador] pregunta recibida · context_id=demo-registro-1 · «Voy a hacer una feria tecnológica para 150 personas, ¿dónde la puedo hacer?»
2026-11-12 20:40:12 INFO    [coordinador] supervisor eligió Agente de Alex · motivo: El usuario solicita recomendaciones de recintos para una feria tecnológica.
2026-11-12 20:40:12 INFO    [coordinador] A2A → http://127.0.0.1:8000/agentes/alex · enviando
2026-11-12 20:40:17 INFO    [coordinador] A2A ← Agente de Alex · respuesta recibida en 5,0 s
```

Si un agente falla, la última línea es `A2A ✗ <agente> · error: <motivo en una línea>`.
El registro nunca incluye claves ni cabeceras, y de la pregunta guarda como máximo 80
caracteres.

**Detener**: `Ctrl+C` en la terminal donde corre uvicorn.

## Cómo funciona

```text
 Navegador (panel del chat)
        │  POST /panel/consultar   {texto, context_id}
        ▼
┌──────────────────── app única: app.py (FastAPI, 1 proceso, 1 puerto) ────────────────────┐
│                                                                                           │
│  Coordinador  (raíz "/": panel, ficha y JSON-RPC)                                         │
│    supervisor con Gemini → elige agente y motivo                                          │
│        │                                                                                  │
│        │  A2A (JSON-RPC por HTTP) a http://127.0.0.1:{puerto}/agentes/{nombre}            │
│        ▼                                                                                  │
│  /agentes/matias     /agentes/alex     /agentes/eduardo     /agentes/sebastian            │
│  programa/horarios   lugares/capacidad presupuesto/costos   comida/catering               │
│  (cada uno: LangGraph + sus herramientas + Gemini, con su ficha en .well-known)           │
│                                                                                           │
└───────────────────────────────────────────────────────────────────────────────────────────┘
        │
        ▼  respuesta, agente y motivo de vuelta al panel
```

**Por qué una sola app.** En el taller anterior había cinco servidores, cada uno en su
puerto. Heroku entrega a cada aplicación **un solo proceso web y un solo puerto público**
(`$PORT`), así que cinco servidores exigirían cinco apps de Heroku, cinco despliegues y
cinco direcciones que mantener sincronizadas. Con la app única hay un despliegue, una
variable `URL_BASE` y un solo lugar donde mirar los registros. El protocolo no cambia: el
coordinador sigue leyendo las fichas A2A y hablando JSON-RPC por HTTP con cada agente,
solo que dentro de la misma app. Por eso con `URLS_AGENTES` se puede volver al modo
distribuido sin tocar el código.

Las llamadas internas van a `127.0.0.1` y no a `URL_BASE` para no salir a internet y
volver a entrar por el router de Heroku, que corta las peticiones a los 30 segundos.

## Dependencias externas

- **Gemini (Google)**: el coordinador y los cuatro agentes lo usan para entender la
  pregunta y redactar la respuesta. Requiere **conexión a internet** y una **clave propia**
  (`GOOGLE_API_KEY`, gratuita en Google AI Studio, con límites de uso). Sin clave o sin
  internet, la app arranca y responde `/salud`, pero las preguntas devuelven un error.
- Los datos de recintos, programas, menús y costos son de demostración y vienen dentro
  del código: no se consulta ningún otro servicio.

## Seguridad

Pendiente: Matías (validación de `CLAVE_API` y manejo de errores en el servidor).

## Operación en Heroku

Pendiente: Sebastián.

## Límites conocidos

- **La memoria de la conversación vive en la RAM del servidor.** Se pierde al reiniciar
  la app y también cuando Heroku la duerme por inactividad: después de eso el chat parte
  de cero aunque el navegador conserve su `context_id`.
- **En Heroku debe usarse `WEB_CONCURRENCY=1`** (`heroku config:set WEB_CONCURRENCY=1`).
  Así corre una sola copia del programa; con varias, cada pregunta puede caer en una copia
  distinta, con otra memoria, y el chat pierde el hilo.
- Dentro de la app única el coordinador llama a los agentes por
  `http://127.0.0.1:{puerto}/agentes/{nombre}` (puerto de `PORT`, o de `PUERTO` en local),
  para no volver a pasar por el router de Heroku, que corta las peticiones a los 30
  segundos. En local, `PUERTO` debe coincidir con el `--port` de uvicorn.
