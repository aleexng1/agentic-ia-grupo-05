# Agente revisor de rendiciones de gastos — Tarea Final Curso 1 (Grupo 05)

> BORRADOR — Alex completa la versión final.
> Empresa, personas, cuentas y montos son **ficticios**. No se usan datos reales de ninguna empresa.

## El caso

**Comercial Los Alerces SpA** (ficticia) reembolsa a sus trabajadores los gastos que pagan con un
fondo por rendir. Cada gasto se rinde con su documento, una glosa y la política que el trabajador
cree que corresponde. Revisarlos a mano es lento y se cometen errores de clasificación.

El agente revisa cada gasto en dos pasos:

1. **Clasificar**: busca en la política de gastos (RAG con Redis) la política, categoría y cuenta
   contable correctas, y las compara con lo que eligió el trabajador.
2. **Validar**: aplica reglas exactas (tipo de documento, plazo, campos obligatorios, exclusividad
   de unidad) y decide **APROBAR**, **OBSERVAR** (por ejemplo, reclasificar) o **RECHAZAR**,
   explicando la regla aplicada.

**Criterio de éxito:** _TODO(caso-calidad): por ejemplo, % de casos del golden set con la decisión
y la política correctas, y 0 jailbreaks exitosos._

## Estructura

```
tarea-final-c1/
├── agente.ipynb          notebook de entrega (solo importa desde src/)
├── verificar.py          juez del contrato: python verificar.py
├── src/                  código del agente (contrato, grafo, herramientas, RAG, memoria, ...)
├── scripts/              carga de la política en Redis
├── datos/                política ficticia y gastos de prueba
├── pruebas/              golden set
└── docs/instrucciones/   una guía por rol
```

Roles, dueños de archivos y reglas de trabajo: ver [AGENTS.md](AGENTS.md).

## Instalación

Requisitos: Python 3.12 y Git.

**Linux**
```bash
cd tarea-final-c1
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env        # y completa los valores
```

**Windows (PowerShell)**
```powershell
cd tarea-final-c1
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env   # y completa los valores
```

## Ejecución

```bash
python verificar.py              # revisa el contrato (no necesita clave)
python verificar.py --con-llm    # además conversa con el agente real
python scripts/cargar_indice.py  # carga la política en Redis
```

Luego abre `agente.ipynb` y ejecútalo de arriba abajo (kernel: el `.venv` de esta carpeta).

## Ficha de reproducción

| Elemento | Valor |
|---|---|
| Modelo de lenguaje | `gemini-3.5-flash-lite` (modelo del curso, clase-05) |
| Temperatura | 0 |
| Modelo de embeddings | `models/gemini-embedding-001` (clase-05) |
| Máximo de pasos ReAct | 6 (`MAX_PASOS` en `src/contrato.py`) |
| Python | 3.12 |
| Librerías | versiones fijas en `requirements.txt` (langgraph 1.2.16, langchain 1.4.6, langchain-google-genai 4.4.2, langchain-redis 0.2.6, redis 8.1.0, redisvl 0.28.0) |
| Almacén vectorial | Redis del curso — _TODO: confirmar con la coordinación qué instancia vale_ |
| Variables de entorno | `GOOGLE_API_KEY`, `GEMINI_MODEL`, `EMBEDDING_MODEL`, `REDIS_URL`, `REDIS_PREFIJO`, `MOSTRAR_TRAZAS` (ver `.env.example`) |
| Datos | `datos/politica_ficticia.md`, `datos/rendiciones_prueba.csv`, `pruebas/golden_set.json` (todos ficticios) |
| Golden set | versión indicada en el campo `version` de `pruebas/golden_set.json` |

Valores para tu `.env` (sin la clave):

```
GEMINI_MODEL=gemini-3.5-flash-lite
EMBEDDING_MODEL=models/gemini-embedding-001
MOSTRAR_TRAZAS=1
```
