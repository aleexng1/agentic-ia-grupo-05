# RAG documental — issue #100

## Cierre para revisión — PR #119

Base del cierre: [commit `ede4b0e`](https://github.com/aleexng1/agentic-ia-grupo-05/commit/ede4b0e)
del [PR #119](https://github.com/aleexng1/agentic-ia-grupo-05/pull/119).
H03 se validó offline; la prueba real se detuvo antes de conectar con
Redis por el requisito de transporte TLS, como registra el
[informe de integridad](../ampliacion-graphrag/08-validacion-integridad-real.md).
Las capturas históricas de esta carpeta corresponden a ejecuciones previas.

El RAG documental recupera fragmentos de la política como respaldo del
tope y su cita. [GraphRAG](../ampliacion-graphrag/README.md) verifica las
relaciones de la propuesta organizacional que permiten recorrer del cargo
al tope. La autenticación en Heroku y las respuestas con `id_ejecucion`
real siguen pendientes.

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

## Capturas de ejecuciones previas verificadas localmente

| Archivo | Tipo y alcance |
|---|---|
| [`04-prueba-real-rag-pass-sanitizada.png`](04-prueba-real-rag-pass-sanitizada.png) (26 424 B) | Pregunta por el tope de hotel por documento entre sedes; muestra tres resultados con fuente y puntaje (`P02`, `P03`, `RG-05`), `P02 recuperada: True`, `Tope esperado encontrado: True` y `PASS` en 2,513 s. |
| [`05-consulta-politica-real-pass.png`](05-consulta-politica-real-pass.png) (22 876 B) | Dos preguntas documentales de hotel: P02, 445 000 CLP; P03, 325 000 CLP. Ambas respuestas citan su sección de `datos/politica_ficticia.md` y muestran `buscar_politica`: **2/2 PASS**. |
| [`capturar_consultas.py`](capturar_consultas.py) | Capturador para RAG y GraphRAG; no es un resultado y no se ejecutó contra Heroku en esta consolidación. |
| `README.md`, `.gitignore`, `.gitkeep` | Documentación, exclusión del original y marcador de directorio. |

Las capturas no muestran el texto de los fragmentos recuperados, el conteo
del índice Redis ni una respuesta `/chat` con `id_ejecucion`. La
[política versionada](../../datos/politica_ficticia.md) y los fixtures son
referencias locales, no exportaciones de Redis.

**Seguridad:** no se observan credenciales, correos, URI de servicios ni
rutas personales en las dos capturas publicables. Solo contienen bloques
`IHDR`, `IDAT` e `IEND`, sin datos finales adicionales. No publicar
`04-prueba-real-rag-pass.png`: el original muestra el usuario y la ruta
personal del operador. `git check-ignore` confirmó su exclusión exacta.

## Otros resultados históricos no repetidos

**Suite histórica**, no repetida en esta consolidación: **481 aprobadas,
12 omitidas, cero fallos** (67,16 s); incluye **302 propias** (85 frontend,
16 capturador, 60 flujo de consulta, 75 GraphRAG, 30 lector Redis y 36 RAG).
Los artefactos simulados y los IDs de pruebas offline no acreditan Heroku.
El operador informó que entregó las credenciales al equipo por separado;
eso no acredita que las Config Vars estén instaladas o funcionen.

**Pendiente documental:** obtener la salida original con el texto de los
fragmentos recuperados y sus fuentes (P02/P03, si se conserva). Para lo
pendiente en remoto, véase la
[matriz de cumplimiento](../ampliacion-graphrag/matriz-cumplimiento.md).

## Captura integral pendiente (operador autorizado)

Desde `tarea-final-c2/`, ejecutar **localmente contra** el principal en Heroku
(no dentro de un dyno), en PowerShell interactivo. Ingresar el origen HTTPS
exacto confirmado por Sebastián, sin ruta, consulta ni credenciales; la URL
del principal de C2 no consta en el README del proyecto.

```powershell
$origen = Read-Host 'Origen HTTPS autorizado del principal de C2 en Heroku'
& .\.venv\Scripts\python.exe -X utf8 -B .\evidencias\ampliacion-rag\capturar_consultas.py $origen
```

Antes de correrlo, confirmar que el release incluye el flujo de este PR,
que Redis, Gemini, Neo4j y Postgres están configurados, y que el principal
tiene un único proceso `web` para el seguimiento asíncrono. No pasar la
clave por argumentos. El script verifica `/health` y pide la
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
Los controles exigen ruta `consulta_politica`, `estado_final: ok`, herramientas
en orden, monto y fuente esperados; los IDs deben coincidir entre aceptación,
respuesta y registro. `/registro` combina memoria y Postgres: además de la
respuesta, comprobar los campos de fila, en particular `fecha` y `duracion_ms`.
Guardar por separado el origen aprobado, release y extracto sanitizado del log
correlacionado por ID si se usa para demostrar despliegue. El JSON no incluye
los fragmentos brutos recuperados ni sustituye una captura de Neo4j.
Revisar manualmente los JSON antes de versionarlos: el filtro no cubre todo
dato personal (por ejemplo, correos o rutas locales en texto libre). Se verificó
`--help` y se revisó el código, sin llamadas de red ni nueva suite.


## Evidencia integrada del equipo (26-11-2026)

- ID: a65dab23-1152-4a93-b336-31c2a99db0bd.
- POST /chat: HTTP 202.
- GET /registro: HTTP 200.
- Ruta: consulta_politica.
- Estado final: ok.
- Herramienta: buscar_politica.
- Duracion: 9654 ms.
- Fuente: RG-03.

[ evidencia original ](../dos-recorridos/01-consulta-politica.md).

Caso GS-33 aprobado:
ID 7f70fe18-74a0-47a5-bb7e-c315c5bf0ebc.

[Informe de evaluacion](../ampliacion-evaluacion/informe-20261126T193234.json).

Evidencia historica del equipo mediante API local.
No acredita Heroku, H03 real ni la extension de fondos.
