# Validación del lector RAG de solo lectura

El lector usa `redis-py` para ejecutar `FT.INFO` y `FT.SEARCH`, y RedisVL
`VectorQuery` para generar la consulta KNN. No instancia `RedisVectorStore`,
no llama a `create` y no comparte su ruta con el cargador. La conexión se abre
en la primera operación; cada consulta valida el esquema antes de pedir el
embedding. Las operaciones adicionales de conexión de Redis pueden incluir
`AUTH` y `SELECT` (si se usa una base distinta de 0).

## Requisitos antes de una prueba real autorizada

1. Confirmar con el operador que `grupo05_v15` ya existe y contiene el corpus
   POL-RG-01 v1.6 de 20 documentos. Confirmar por el registro de la carga que
   los vectores corresponden a `models/gemini-embedding-001` y a la configuración
   del cargador. **`FT.INFO` no identifica el modelo de embeddings.**
2. Usar una cuenta Redis dedicada, con permisos únicamente de conexión e
   inspección y búsqueda (`FT.INFO`, `FT.SEARCH`) sobre el alcance autorizado.
   El operador debe confirmar el alcance con el proveedor y que la cuenta no
   pueda crear índices ni modificar claves. No verificarlo ejecutando escrituras
   contra el índice de trabajo. Preferir TLS en conexiones remotas.
3. El esquema esperado es HASH, prefijo `grupo05_v15` o `grupo05_v15:`,
   campos `text` y `_metadata_json`, y `embedding` de tipo `FLOAT32` con 3072
   dimensiones, `COSINE` y `FLAT`. Si existe `_index_name`, se requiere que sea
   `TEXT` y se aplica el mismo filtro que en el lector heredado. La cuenta y la
   configuración deben permitir a Redis devolver `_metadata_json` con
   `politica`, `texto_completo` y `fuente`.
4. Inyectar `REDIS_URL`, `REDIS_PREFIJO`, `EMBEDDING_MODEL` y la credencial de
   Gemini en el proceso mediante el mecanismo seguro del equipo, sin imprimir
   los valores. No escribir secretos en comandos, código, trazas o evidencias.
   La URL solo admite `db` como opción de consulta para evitar que sobrescriba
   los límites del lector: 3 s al conectar y 5 s de socket, sin reintentos de
   Redis. Gemini recibe un timeout de solicitud de 10 s y un intento.

## Corrida posterior, desde `tarea-final-c2/` en PowerShell

Una vez autorizada y configurada, ejecutar primero una consulta conocida:

```powershell
$env:PYTHON_DOTENV_DISABLED = '1'
$env:LANGSMITH_TRACING = 'false'
$env:LANGCHAIN_TRACING_V2 = 'false'
@'
from langchain_core.tools import ToolException
from src.conocimiento.rag.rag import buscar_politica

consulta = "¿Cuál es el tope de hotel por documento en un viaje entre sedes de la empresa?"
try:
    for fragmento in buscar_politica.invoke({"consulta": consulta, "k": 3}):
        print(fragmento["fuente"], fragmento["puntaje"])
except ToolException as error:
    raise SystemExit(str(error)) from None
'@ | & .\.venv\Scripts\python.exe -B -
```

El resultado esperado para esa consulta (no observado aún) es `#P02` en el
top‑3 y el tope documental de $445.000 CLP en su texto. Repetir con RG‑01 a
RG‑06, el hotel en viajes externos (`#P03`, $325.000 CLP) y una pregunta que el
corpus no cubra. Para esta última, KNN puede devolver fragmentos sin respaldo;
no confundir vecinos con evidencia ni exigir una lista vacía.

Registrar las consultas, fuentes, orden y puntajes observados y contrastar
los hechos con el corpus versionado. Para comprobar paridad con el lector
anterior, comparar sobre una copia autorizada o resultados de referencia
capturados con los mismos vectores: top‑k, fuentes, texto completo y puntajes
con tolerancia numérica, registrando posibles empates. No ejecutar el cargador
ni la inicialización del lector anterior contra el índice compartido para
obtener esa referencia.
