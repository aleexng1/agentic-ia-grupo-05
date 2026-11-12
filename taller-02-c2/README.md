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

## Configuración

## Cómo iniciar / probar / detener

## Operación en Heroku

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
