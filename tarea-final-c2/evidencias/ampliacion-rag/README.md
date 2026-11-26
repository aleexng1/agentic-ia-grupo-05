# RAG documental — issue #100

## Resultados reales históricos, informados por el operador (25-11-2026)

Se recuperó el Redis original del Curso 1. Índice `grupo05_v15`, 20 documentos
indexados, modelo `models/gemini-embedding-001`, dimensión 3072, política
POL-RG-01 v1.6. El operador informó recuperación documental real de P02 y P03:

| Política y consulta | Tope de hotel informado | Referencia del corpus |
|---|---:|---|
| P02, viaje interno | 445000 CLP | `datos/politica_ficticia.md#P02` |
| P03, viaje externo | 325000 CLP | `datos/politica_ficticia.md#P03` |

El índice compartido no se modificó. Son resultados informados, no una nueva
ejecución de OpenCode ni una comprobación por `/chat` con ID. Los ensayos
combinados están en [GraphRAG](../ampliacion-graphrag/README.md).

## Artefactos y pruebas locales

- **Originales disponibles:** la [política versionada](../../datos/politica_ficticia.md)
  y los fixtures prueban qué debe recuperarse; no son exportaciones de Redis.
  No se encontraron en esta carpeta logs, capturas ni exportaciones originales de
  la sesión real. No se copiaron archivos de fuera del área autorizada.
- **Nuevas pruebas de OpenCode:** pruebas offline de frontend y del capturador
  (`tests/test_frontend_eduardo.py`, `tests/test_capturar_consultas_eduardo.py`),
  además de regresión offline. Corrida final tras sincronizar con `main`:
  **481 aprobadas y 12 omitidas en 67.16 s**, incluidas las **302 propias**
  (85 frontend, 16 capturador,
  60 flujo de consulta, 75 GraphRAG, 30 lector Redis y 36 RAG).
  Omitidas por configuración: 7 PostgreSQL de prueba y 5 Gemini.
  Sus respuestas, capturas en memoria e IDs de prueba no acreditan ejecución real.
- **Pendientes:** incorporar manualmente la salida sanitizada original de
  recuperación P02/P03 (pregunta, fragmento recuperado y fuente, sin acceso ni
  credenciales), si el operador la conserva. Obtener la consulta documental real
  por `/chat` con su resultado y fila de `/registro/{id_ejecucion}`. El índice
  general de evidencias sigue a cargo de Alex.

## Captura integral pendiente (operador autorizado)

Desde `tarea-final-c2/`, en una terminal interactiva, con la URL aprobada por
el responsable del despliegue (reemplazar el dominio de ejemplo):

```powershell
& .\.venv\Scripts\python.exe -X utf8 -B evidencias/ampliacion-rag/capturar_consultas.py https://principal-autorizado.invalid
```

No pasar la clave por argumentos. El script verifica `/health` y pide la
API Key mediante entrada protegida. Solo envía dos preguntas de política:
hotel P02 sin cargo y hotel P03 para Jefe de tienda. No envía gastos ni
boletas ni llama al verificador. Hace un único POST por caso, acepta 200
o sigue 202 por UUIDv4, y pide el registro terminal. No sigue redirecciones
ni la URL `consultar`. Plazo por caso: 105 s por defecto; si el servidor
usa otro tope, coordinar `--espera`.

Guarda `captura-<UTC>.json` en cada carpeta con entradas, respuestas y
registro proyectados, duración, estado y controles `PASS`/`FAIL`. Un
resultado sin fila persistida o sin respuesta completa no acredita el caso.
Si se pierde la respuesta del POST antes de conocer el ID, no se reenvía.
Revisar manualmente los JSON antes de versionar, incluso cuando el filtro
automático no haya detectado datos sensibles. **No se ejecutó contra un
servicio real en esta sesión.**
