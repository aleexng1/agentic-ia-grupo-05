# Tarea final del Curso 2 · Grupo 05

**Agente revisor de rendiciones de gastos** para *Comercial Los Alerces SpA*, una **empresa
ficticia** (el mismo caso de `tarea-final-c1/`), montado sobre la infraestructura de los
talleres del Curso 2 (`taller-01-c2/` y `taller-02-c2/`): servidor A2A, API FastAPI con
clave, chat web y despliegue en Heroku.

> Estado: **esqueleto**. `/health` funciona y `/chat` valida la clave. Mientras el router no
> exista, `/chat` responde 501 con un mensaje claro. Quién hace qué: [docs/reparto.md](docs/reparto.md).
> Los formatos que todos respetan: [docs/contratos.md](docs/contratos.md).

## Alcance

El agente principal es **router y worker**: clasifica cada mensaje y además ejecuta el trabajo
del flujo elegido.

| Flujo | Ejemplo de mensaje | Qué hace |
|---|---|---|
| `consulta_politica` | «¿Cuál es el tope de hotel para un jefe de tienda?» | Busca en la política (RAG) y en el grafo de topes (GraphRAG) y responde citando la fuente. |
| `revisar_gasto` | «Revisa este gasto: bencina $45.000 del 2 de octubre» + foto de la boleta | Ciclo **ReAct** con condición de parada (`MAX_PASOS_REACT`): busca la política, valida reglas, consulta el fondo (MCP) y **delega por A2A** la lectura de la boleta al verificador. Cierra con aprobar / observar / rechazar. |
| `fuera_de_alcance` | «Escríbeme un poema» | Explica qué sí puede hacer, sin usar herramientas. |

Requisitos base que cubre: router + worker, ReAct con parada explícita, delegación A2A,
seguridad (clave + bloqueo de acción no autorizada), resiliencia (timeout y fallback sin
inventar) y despliegue con registro de ejecuciones.
Ampliaciones planeadas: RAG documental, GraphRAG (Neo4j), MCP, memoria persistente (Postgres),
evaluación con golden set y, de respaldo, un caso A2A adicional con n8n.

## Arranque local del esqueleto

Desde `tarea-final-c2/`:
```bash
python3.12 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                 # y completa tus valores
python -m pytest                     # pruebas de humo
uvicorn api.app:app --port 8000      # principal  → http://127.0.0.1:8000/health
uvicorn src.verificador.app:app --port 8001   # verificador (otra terminal)
```

## Estructura

| Carpeta | Qué hay |
|---|---|
| `api/` | API FastAPI del principal (`/health`, `/chat`, `/registro/{id}`) |
| `src/principal/` | Grafo, router, flujos y herramientas del agente principal |
| `src/verificador/` | Agente especialista A2A que lee la boleta |
| `src/comun/` | Contrato de tipos, configuración, seguridad, registro, modelos y A2A |
| `src/conocimiento/` | RAG (Redis) y GraphRAG (Neo4j) |
| `src/mcp_fondos/` | Servidor MCP con `consultar_fondo` |
| `web/` | Chat web |
| `n8n/` | Caso A2A adicional con n8n (ampliación de respaldo) |
| `datos/` | Política, fondos, rendiciones y boletas: todo ficticio |
| `evaluacion/` | Golden set versionado y script de % de aciertos |
| `tests/` | Pruebas de humo |
| `evidencias/` | Una subcarpeta por prueba de la pauta y por ampliación |
| `docs/` | Contratos, reparto y referencia de c1 |

---

## Ficha mínima

### Alcance y flujos

_Pendiente._

### Entorno

_Pendiente._

### Acceso al servicio

_Pendiente._

### Configuración

_Pendiente._

### Datos de ejemplo

_Pendiente._

### Evidencias

_Pendiente._

### Ampliaciones declaradas

_Pendiente._
