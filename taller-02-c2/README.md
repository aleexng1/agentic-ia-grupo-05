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
| `CLAVE_API` | **Obligatoria.** Clave de acceso a la API: toda consulta debe enviarla en la cabecera `X-API-Key`. Si está vacía, el servidor avisa al arrancar y rechaza todas las consultas con 503. Distinta de `GOOGLE_API_KEY`; cómo elegirla, en la sección Seguridad. |
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

**Comprobaciones del frontend (opcionales).** Son pruebas del chat en un navegador real
(Chrome), escritas por Eduardo en `evidencias/eduardo/test_panel_eduardo.py`. Son
**opcionales**: no hacen falta para usar ni desplegar la app, y **necesitan Chrome instalado**
(con Edge: `CANAL_NAVEGADOR=msedge`). Playwright, que las maneja, no está en
`requirements.txt` (Heroku no lo necesita) sino en `requirements-dev.txt`:

```bash
# desde taller-02-c2/proyecto, con el entorno virtual activado
pip install -r requirements-dev.txt
pytest ../evidencias/eduardo/test_panel_eduardo.py -v -rx
```

No usan Gemini ni la red: las respuestas del servidor son simuladas. Por defecto **regeneran
las capturas PNG** de `evidencias/eduardo/`; para no sobrescribir las de la entrega, apunta
`CARPETA_CAPTURAS` a una carpeta temporal antes de correrlas
(Linux y macOS: `CARPETA_CAPTURAS=/tmp/capturas pytest ...`;
PowerShell: `$env:CARPETA_CAPTURAS = "$env:TEMP\capturas"`).

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

La app es una API con clave: cualquiera puede ver la página y las fichas, pero solo quien
tiene la clave puede hacer consultas.

### La clave de acceso (`CLAVE_API`)

`CLAVE_API` es la contraseña que el servidor exige para aceptar una consulta. **No es la
clave de Gemini** (`GOOGLE_API_KEY`): esa la usa el servidor para hablar con Google y no se
comparte con nadie; la de acceso es la que se le da a quien puede usar el chat.

**Cómo elegirla.** Larga y al azar, no una palabra ni una contraseña que uses en otro lado.
Una forma de generarla (sirve en Windows, Linux y macOS):

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Pégala en `CLAVE_API=` del `.env` (local) o en las Config Vars de Heroku. No la escribas en
el código, en capturas ni en el chat del grupo. Para cambiarla, cambia el valor y reinicia
la app: la anterior deja de servir.

### Qué se protege

| Ruta | Acceso |
| --- | --- |
| `POST /panel/consultar` (la consulta del chat) | Con clave |
| `POST /` y `POST /agentes/{nombre}` (JSON-RPC A2A del coordinador y de cada agente) | Con clave |
| `GET /` (la página), las fichas `/.well-known/agent-card.json` y `GET /salud` | Públicas |

La clave viaja en la cabecera `X-API-Key`:

```bash
curl -i -X POST http://127.0.0.1:8000/panel/consultar \
  -H "Content-Type: application/json" \
  -H "X-API-Key: TU_CLAVE_API" \
  -d '{"texto": "¿Qué actividades pongo en una feria infantil de 3 horas?"}'
```

```powershell
# Windows (PowerShell)
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/panel/consultar `
  -Headers @{ "X-API-Key" = "TU_CLAVE_API" } -ContentType "application/json; charset=utf-8" `
  -Body ([System.Text.Encoding]::UTF8.GetBytes('{"texto": "¿Qué actividades pongo en una feria infantil de 3 horas?"}'))
```

### Respuestas y errores

Todo error tiene la forma `{"detail": "mensaje en español, en una sola línea"}`, sin trazas
de Python ni claves. Un error nunca se presenta como una respuesta exitosa.

| Código | Cuándo | Ejemplo de `detail` |
| --- | --- | --- |
| 200 | La consulta se respondió. | (el JSON con `respuesta`, `agente` y `motivo`) |
| 400 | La pregunta está vacía. | `Escribe una pregunta para continuar.` |
| 401 | Falta la clave o es incorrecta. | `Falta la clave de acceso. Envíala en la cabecera X-API-Key.` / `La clave de acceso es incorrecta.` |
| 502 | Falló Gemini, la conexión o un agente. | `No se pudo consultar al agente: La clave de Gemini (GOOGLE_API_KEY) no es válida. Revísala en el .env o en las Config Vars de Heroku.` |
| 503 | El servidor no tiene `CLAVE_API`. | `El servidor no tiene configurada la clave de acceso (CLAVE_API), así que no acepta consultas. Avisa a quien lo administra.` |

Las fallas del proveedor que se reconocen con un mensaje propio son: clave de Gemini
inválida o ausente, sin cuota o créditos, sin permiso, modelo inexistente, tiempo de espera
agotado, sin conexión y servicio no disponible. Cualquier otra falla se resume en una línea.

### Cómo está hecho

- La clave se compara con `secrets.compare_digest`, para no revelarla por el tiempo que
  tarda en fallar (`src/comun/seguridad.py`).
- La clave nunca aparece en el código, en la página ni en los registros. Cuando se rechaza
  una petición, el registro guarda solo la ruta y el motivo (`sin clave`, `clave incorrecta`).
- El coordinador se llama a sí mismo por A2A, así que su cliente interno envía la cabecera,
  **solo** hacia esta misma app (`127.0.0.1` y el puerto real). A los agentes de otros
  computadores del modo distribuido (`URLS_AGENTES`) nunca se les envía.
- Si `CLAVE_API` está vacía, la app no queda abierta: avisa con un error al arrancar y
  responde 503 a toda consulta. `/salud` y las fichas siguen respondiendo, para poder
  diagnosticarla.
- Los errores se traducen en `src/comun/errores.py`. El registro del servidor conserva el
  detalle técnico original (sin claves), útil en la terminal y en `heroku logs`.

### Límites de la seguridad

- Hay **una sola clave** para todas las personas: no distingue quién consulta.
- No hay límite de intentos ni bloqueo tras varias claves incorrectas.
- En local la conexión es HTTP; en Heroku la plataforma entrega HTTPS.
- La seguridad de la clave depende de cómo se comparta: quien la tenga puede gastar la cuota
  de Gemini del servidor.

Pruebas automáticas: `python -m pytest tests/test_seguridad.py`. Evidencias de acceso
permitido y rechazado, y de las fallas del proveedor: `evidencias/matias/`.

## Operación en Heroku

Pendiente: Sebastián.

## Límites conocidos

- **La memoria de la conversación vive en la RAM del servidor.** Se pierde al reiniciar
  la app y también cuando Heroku la duerme por inactividad: después de eso el chat parte
  de cero aunque el navegador conserve su `context_id`.
- **En Heroku debe usarse `WEB_CONCURRENCY=1`** (`heroku config:set WEB_CONCURRENCY=1`).
  Así corre una sola copia del programa; con varias, cada pregunta puede caer en una copia
  distinta, con otra memoria, y el chat pierde el hilo.
- **El modo distribuido no funciona con agentes protegidos de otros computadores.** Cada
  app exige su propia `CLAVE_API` y el coordinador solo envía la suya a esta misma app
  (nunca a direcciones de terceros, a propósito), así que un agente remoto que también la
  exija lo rechazará con 401.
- Dentro de la app única el coordinador llama a los agentes por
  `http://127.0.0.1:{puerto}/agentes/{nombre}` (puerto de `PORT`, o de `PUERTO` en local),
  para no volver a pasar por el router de Heroku, que corta las peticiones a los 30
  segundos. En local, `PUERTO` debe coincidir con el `--port` de uvicorn.
