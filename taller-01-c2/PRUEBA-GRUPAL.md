# Prueba grupal · domingo 8 de noviembre, 19:00 · Grupo 5

Guion para el catálogo y la ronda (pasos 7 y 8 del taller). Este archivo es interno del
grupo: no va en el zip.

**Qué tiene que quedar al final**, cada uno en su carpeta `evidencias/NOMBRE/`:

- `04-catalogo.png`: la terminal del coordinador con **«Supervisor con 4 agentes»**.
- `05-ronda.png`: las 3 preguntas de la ronda con el agente elegido y el motivo.
- La tabla de la ronda llena en tu `documento-NOMBRE.md` (plantilla al final).

| Integrante | Agente | Puerto | Rama |
|---|---|---|---|
| Matias Muñoz | Agente de Matias · programa y horarios | 8003 | `c2t1/matias-programa` |
| Alex Nail | Agente de Alex · lugares y capacidad | 8004 | `c2t1/alex-lugares` |
| Eduardo Basaure | Agente de Eduardo · presupuesto y costos | 8005 | `c2t1/eduardo-presupuesto` |
| Sebastian Mardones | Agente de Sebastian · comida y catering | 8006 | `c2t1/sebastian-catering` |

## 0. Antes de las 19:00: código al día

Cada uno, en su rama, trae lo último de `main` (ahí están los 4 agentes):

```bash
git switch c2t1/NOMBRE-ROL
git pull origin main
```

## 1. Levantar tu agente (terminal 1)

```powershell
# Windows (PowerShell), desde taller-01-c2\proyecto
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.venv\Scripts\Activate.ps1
$env:PYTHONIOENCODING = "utf-8"
python -m uvicorn src.agente_NOMBRE.server:app --port PUERTO
```

```bash
# Linux / macOS, desde taller-01-c2/proyecto
source .venv/bin/activate
python -m uvicorn src.agente_NOMBRE.server:app --port PUERTO
```

## 2. Abrir tu túnel (terminal 2)

```powershell
# Windows
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\scripts\tunel.ps1 PUERTO
```

```bash
# Linux / macOS
bash scripts/tunel.sh PUERTO
```

Copia la dirección que sale en verde. Si se perdió entre los registros:
`curl -s http://127.0.0.1:20241/quicktunnel` (en Windows, `Invoke-RestMethod` a la misma dirección).

## 3. Pegar tu línea en el chat del grupo

Una línea por persona, con este formato:

```
Agente de NOMBRE · tema · https://palabras-al-azar.trycloudflare.com
```

## 4. Tu `.env`

| Variable | Matias | Alex, Eduardo y Sebastian |
|---|---|---|
| `URL_PUBLICA` | su túnel | tu túnel |
| `URL_MATIAS` | `http://127.0.0.1:8003` | **vacía** (`URL_MATIAS=`) |
| `URLS_AGENTES` | los 3 túneles de los demás | `http://127.0.0.1:TU_PUERTO` + los 3 túneles de los demás |

Ejemplo para Alex (separadas por comas, sin espacios):

```
URL_PUBLICA=https://tunel-de-alex.trycloudflare.com
URL_MATIAS=
URLS_AGENTES=http://127.0.0.1:8004,https://tunel-de-matias.trycloudflare.com,https://tunel-de-eduardo.trycloudflare.com,https://tunel-de-sebastian.trycloudflare.com
```

El `.env` solo se lee al arrancar: después de guardarlo, **reinicia tu agente** en la
terminal 1 (Ctrl+C, flecha arriba, Enter) para que tu ficha publique tu túnel.

Antes de seguir, abre las 4 fichas en el navegador
(`https://TUNEL/.well-known/agent-card.json`). Si alguna no abre, avisa en el chat: el
coordinador la saltaría y diría «Supervisor con 3 agentes».

## 5. Catálogo: `04-catalogo.png` (terminal 3)

```bash
python -m uvicorn src.coordinador.server:app --port 8002
```

Espera la línea **«Supervisor con 4 agentes»** y saca la captura de esa terminal:

- Windows: `Win + Shift + S`, guarda como `taller-01-c2\evidencias\NOMBRE\04-catalogo.png`.
- Linux: desde otra terminal,
  `gnome-screenshot -w -d 5 -f ~/Escritorio/agentic-ia-grupo-05/taller-01-c2/evidencias/NOMBRE/04-catalogo.png`
  y en esos 5 segundos haz clic en la terminal del coordinador.

## 6. Ronda: `05-ronda.png` (terminal 4)

Cada uno hace sus 3 preguntas (tabla de abajo) con:

```bash
python main.py coordinador "PREGUNTA" --saltos
```

Muestra `Agente elegido`, `Motivo` y la respuesta. Corre las 3 seguidas en la misma
terminal y saca una captura donde se vean las tres: `evidencias/NOMBRE/05-ronda.png`.
Revisa que no se vean correos, rutas con tu usuario ni notificaciones (en Windows, para
ocultar la ruta: `function prompt {"PS> "}`).

### Preguntas propuestas

Cada uno: una de su tema, una del tema de otro compañero (escrita como la haría alguien
que no sabe, y cada uno apunta a un compañero distinto) y una que nadie sabe.

| Quién pregunta | Tipo | Pregunta | Debería ir a |
|---|---|---|---|
| Matias | su tema | Tengo una feria cultural de 3 horas desde las 16:00 para público familiar, ¿qué actividades pongo y a qué hora? | Agente de Matias |
| Matias | de otro | Vamos a hacer una feria gastronómica para unas 250 personas y queremos que sea al aire libre, ¿qué lugar nos sirve? | Agente de Alex |
| Matias | nadie | ¿Quién ganó el mundial de 1962? | ninguno |
| Alex | su tema | Voy a hacer una feria tecnológica para 150 personas, ¿dónde la hago? | Agente de Alex |
| Alex | de otro | ¿Cuánta plata necesito más o menos para una feria gastronómica de 120 personas que dura 3 horas? | Agente de Eduardo |
| Alex | nadie | ¿Qué vuelos hay a Lima? | ninguno |
| Eduardo | su tema | ¿Cuál es el presupuesto simulado de una feria infantil para 60 personas y 2 horas? | Agente de Eduardo |
| Eduardo | de otro | Van a venir 80 niños a una feria infantil de 3 horas que parte a las 11:00 y 6 son celíacos, ¿qué les damos de comer? | Agente de Sebastian |
| Eduardo | nadie | ¿Cuál es la capital de Australia? | ninguno |
| Sebastian | su tema | Feria gastronómica de 5 horas desde las 11:00 para 200 personas, 20 son vegetarianas, ¿qué servimos? | Agente de Sebastian |
| Sebastian | de otro | Para una feria tecnológica de 4 horas con estudiantes, ¿qué charlas o talleres hago y en qué orden? | Agente de Matias |
| Sebastian | nadie | ¿Cómo configuro el wifi de mi casa? | ninguno |

En el ensayo local del 8 de noviembre (los 4 agentes en un computador, sin túneles) las
8 preguntas de «su tema» y «de otro» fueron al agente esperado, y la del mundial fue a
«ninguno». Las preguntas de «nadie» de esta tabla son del mismo estilo.

Si sobra tiempo, para el análisis («¿hubo preguntas que dos agentes podían responder?»),
estas tres salieron interesantes en el ensayo:

- «¿Cuánto cuesta el catering para 100 personas?» → el supervisor eligió a **Eduardo**
  (es un costo), pero Eduardo la rechazó («eso corresponde a Sebastián») y Sebastian no
  da precios: **nadie la respondió**.
- «¿A qué hora conviene el almuerzo?» → eligió a **Sebastian** (su ficha dice «con la
  hora de cada servicio»), pero Sebastian la rechazó como «horario de actividades».
- «¿Qué lugar sirve para una feria con food trucks?» → eligió a **Alex**, que pidió la
  cantidad de personas. Bien.

### Plantilla de la tabla (pegar en tu `documento-NOMBRE.md`, sección de la ronda)

```markdown
| # | Pregunta | A quién fue | Motivo del supervisor | ¿Estuvo bien? |
|---|----------|-------------|-----------------------|---------------|
| 1 | (de mi tema) | | | |
| 2 | (del tema de otro) | | | |
| 3 | (que nadie sabe) | | | |
```

La columna **«A quién fue»** es la que lee el script del documento de entrega: si queda
vacía, la ronda aparece como pendiente.

## 7. Análisis (conversarlo antes de cerrar)

- ¿Qué ficha eligió mejor el supervisor y qué decía?
- ¿Hubo preguntas que dos agentes podían responder? ¿Cómo se resolvió?
- ¿Qué cambiaría cada uno de su ficha?

Alex anota las respuestas del grupo para el documento de entrega.

## 8. Cerrar

- **Cierra tu túnel con Ctrl+C** en la terminal 2: mientras esté abierto, cualquiera con la
  dirección puede usar tu agente y gastar tu clave de Gemini.
- Apaga el agente y el coordinador (Ctrl+C).
- Deja `URL_PUBLICA=` vacía en tu `.env`.
- Sube `04-catalogo.png`, `05-ronda.png` y tu tabla en tu rama y abre el PR hacia `main`.
