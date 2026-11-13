# Guion de capturas · Alex · base e integración (LOCAL)

Objetivo: demostrar que la base funciona **de punta a punta en LOCAL**: la app arranca como
en Heroku, el coordinador elige al agente correcto, cada agente responde, una pregunta que no
es de nadie va a «ninguno», una pregunta con datos faltantes se contesta pidiendo el dato, y
el registro A2A deja cada paso.

**Las capturas se tomaron automáticamente** (2026-11-13), con un script de Playwright y
Chrome sin ventana visible, **contra la app real**: no hay respuestas simuladas, y las 6
preguntas son reales a Gemini (el máximo). Nadie las tomó a mano. Todo es LOCAL: nada de
esto es producción.

## Cómo repetirlas

Desde la **raíz del repositorio** (la carpeta que contiene `Procfile` y `taller-02-c2/`):

```bash
taller-02-c2/proyecto/.venv/bin/python taller-02-c2/evidencias/alex/capturar_evidencias.py
```

Para ensayar sin gastar preguntas de Gemini (solo `/salud`, el ingreso y la clave
incorrecta): agrega `--sin-preguntas` al final.

Requisitos:

- El entorno virtual del proyecto con `requirements-dev.txt` instalado
  (`pip install -r requirements-dev.txt`, desde `taller-02-c2/proyecto`).
- Chrome instalado. No hace falta `playwright install`.
- La `GOOGLE_API_KEY` en `taller-02-c2/proyecto/.env`; la lee la app, el script nunca abre
  ese archivo.
- El puerto 8000 libre.
- Linux o macOS: el script usa `sh` y grupos de procesos.

Cada corrida **usa 6 preguntas reales a Gemini** y **sobrescribe** las imágenes y
`registro-local.txt`. Las respuestas de Gemini no son idénticas entre corridas: el texto
puede variar un poco; el agente elegido y la forma de la respuesta deberían mantenerse.

## Qué hace el script

1. Genera una `CLAVE_API` temporal **en memoria**: no la escribe en ningún archivo, ni
   temporal, y solo existe en el entorno del servidor y en el campo de ingreso del navegador.
2. Levanta la app **igual que Heroku**: desde la raíz, con `PORT=8000` y el comando del
   Procfile (`cd taller-02-c2/proyecto && uvicorn app:app --host 0.0.0.0 --port $PORT`).
   Su salida va a `registro-local.txt`.
3. Con Chrome sin ventana visible, a 1280x900, toma las capturas de la tabla de abajo.
4. Detiene la app y depura `registro-local.txt`: cuenta cuántas veces aparece la clave
   (debe ser 0) y reemplaza las rutas del equipo por `<carpeta-del-repo>`.

Dos cosas que el script agrega a las imágenes, y que no son parte de la app:

- **Una franja arriba** con «LOCAL · captura automática (Playwright) contra la app real ·
  fecha y hora» (la hora es la de cada captura).
- **El área de conversación se expande**: se quita su límite de altura (solo estilo) para
  que la respuesta completa, con el agente y el motivo, quepa en una imagen sin desplazarse.
  El contenido no cambia.

## Capturas

Todas están en `taller-02-c2/evidencias/alex/`.

| Archivo | Qué hace el script | Qué debe verse |
| --- | --- | --- |
| `01-salud.png` | Abre `http://127.0.0.1:8000/salud`. | `{"ok":true}`. |
| `02-ingreso.png` | Abre el panel y escribe la clave temporal en el campo de ingreso, sin enviarla. | La pantalla de ingreso con la clave **tapada** (el campo es tipo *password*: se ve como puntos). |
| `03-clave-incorrecta.png` | Entra con una clave incorrecta y envía una pregunta. | El servidor responde 401: vuelve al ingreso con «Acceso rechazado (401). La clave de acceso es incorrecta…». No se llamó a ningún agente. |
| `04a-matias-programa.png` | Clave correcta, «Nueva conversación» y la pregunta de abajo. | La pregunta, el programa con horas de inicio y término desde las 15:00, **Agente: Agente de Matias** y su motivo. |
| `04b-alex-recintos.png` | Ídem. | Hasta tres recintos con capacidad, % de ocupación, m² por persona, estacionamientos y accesibilidad; el aviso de que la disponibilidad la confirma una persona; **Agente: Agente de Alex** y su motivo. |
| `04c-eduardo-presupuesto.png` | Ídem. | Partidas en CLP, subtotal, contingencia y total, la advertencia de importes ficticios, **Agente: Agente de Eduardo** y su motivo. |
| `04d-sebastian-catering.png` | Ídem. | Servicios con su hora, cantidades por dieta (65/10/5), litros de agua y los supuestos; **Agente: Agente de Sebastian** y su motivo. |
| `05-ninguno.png` | Ídem. | «No tengo un agente para eso…», **Agente: ninguno** y su motivo. |
| `06-datos-faltantes.png` | Ídem. | Una respuesta que **pide los datos** (tipo de feria y cantidad de personas) sin recomendar todavía ningún recinto; **Agente: Agente de Alex**. |
| `registro-local.txt` | Es la salida del servidor, completa. | El arranque, y por cada pregunta las líneas del registro A2A: pregunta recibida, agente elegido y su motivo, `A2A →` (envío a `127.0.0.1`) y `A2A ←` (respuesta con su tiempo). |

Cada una de las preguntas 04a a 06 se hace en una **conversación nueva**, para que la
memoria de la anterior no influya. Las preguntas exactas, en el orden en que se hacen:

| # | Captura | Pregunta |
| --- | --- | --- |
| 1 | `04a` | `Necesito armar el programa de una feria infantil de 3 horas desde las 15:00.` |
| 2 | `04b` | `Necesito un recinto interior para una feria tecnológica de 80 personas.` |
| 3 | `04c` | `¿Cuál es el presupuesto simulado de una feria tecnológica para 80 personas y 4 horas?` |
| 4 | `04d` | `Necesito una propuesta de catering para una feria tecnológica de 80 personas, de 4 horas, comenzando a las 10:00. Hay 10 personas vegetarianas y otras 5 que requieren comida sin gluten.` |
| 5 | `05` | `¿Cómo resuelvo una integral cuadrática?` |
| 6 | `06` | `¿Dónde hago una feria?` |

La pregunta de la captura `03` (la misma de `04a`, con la clave incorrecta) la rechaza el
servidor antes de llamar a nadie, así que no gasta una pregunta de Gemini.

## Revisión de las imágenes

Cada imagen se abre a tamaño completo y se comprueba que muestre lo de la tabla y que **no**
aparezca: la `CLAVE_API` ni la `GOOGLE_API_KEY` (el campo de ingreso se ve con puntos),
correos, el nombre de usuario o rutas con él, direcciones IP públicas (solo `127.0.0.1` y
`0.0.0.0`), ni notificaciones del sistema. En `registro-local.txt`, además: la clave aparece
0 veces y no hay rutas con el usuario. Como el navegador corre sin ventana y sin perfil, la
captura solo contiene la página.
