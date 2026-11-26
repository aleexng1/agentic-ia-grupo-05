# GraphRAG de rendiciones — Eduardo

**Estado:** implementación y pruebas offline. La carga de ensayo y las
consultas reales históricas se documentan como
[resultados informados por el operador](../../../evidencias/ampliacion-graphrag/README.md).
El catálogo sigue siendo una propuesta académica versionada y pendiente de
aprobación grupal. No se repitió la carga para este cierre.

## Modelo y procedencia

```text
(:Cargo)-[:TIENE_NIVEL]->(:Nivel)-[:PUEDE_RENDIR]->(:Categoria)-[:TIENE_TOPE]->(:Tope)
```

Todos los nodos llevan también la etiqueta `Grupo05C2GraphRAG`. Cada nodo
y relación se identifica con `proyecto = grupo05-tarea-final-c2-graphrag`.
La restricción `g05_c2_graphrag_proyecto_id` protege la identidad `(proyecto, id)`
en esa etiqueta propia, no en etiquetas genéricas de otros proyectos.

| Entidad | Ejemplo de ID | Procedencia |
|---|---|---|
| Cargo | `cargo:jefe-de-tienda` | Puesto de ejemplo; su pertenencia a un nivel es ficticia. |
| Nivel | `nivel:jefatura` | Agrupación organizacional ficticia, no un escalafón de la política. |
| Categoria | `P02:hotel`, `P03:hotel` | Tipo de gasto cualificado por subpolítica. P02 es viaje entre sedes; P03 es viaje externo. La subpolítica es una propiedad, no un nodo adicional. |
| Tope | `tope:POL-RG-01:1.6:P02:hotel` | Límite CLP por documento de POL-RG-01 v1.6, con la fuente y versión en el nodo. No es un importe asignado al cargo. |

En `datos/cargos_niveles.json` están separados `normativa` y
`organizacion_ficticia`. `TIENE_TOPE` representa el documento;
`TIENE_NIVEL` y `PUEDE_RENDIR` están marcadas como propuesta pendiente.
Los recorridos de muestra son:

- Jefe de tienda → Jefatura → categorías de estadía de P02 y P03.
- Analista de Operaciones → Profesional → categorías de estadía de P02.

La diferencia entre niveles **solo** permite ensayar recorridos que existen
y recorridos ausentes. No significa que POL-RG-01 prohíba viajes externos a
un analista, ni que un recorrido apruebe un gasto. La política no define
topes por cargo o nivel. Antes de exponerlos en el chat, el grupo debe acordar
la elegibilidad y cómo comunicar su procedencia. No se cambió el contrato.

| Categoría | P02 — CLP por documento | P03 — CLP por documento |
|---|---:|---:|
| Desayuno | 10.000 | 20.000 |
| Almuerzo | 20.000 | 45.000 |
| Cena | 45.000 | 50.000 |
| Hotel | 445.000 | 325.000 |
| Hostal | 295.000 | 265.000 |

Los diez topes se validan contra las secciones P02/P03 de
`datos/politica_ficticia.md`. P08 contiene otros topes, pero no forma parte
de este catálogo. Los IDs de Tope incluyen versión, política y categoría;
incluso dos topes con el mismo monto conservan su identidad y su fuente.

## Lectura

`tope_para(cargo, categoria)` devuelve solo `cargo`, `nivel`, `categoria`,
`tope_clp` y `fuente`. La entrada normaliza espacios, mayúsculas y acentos,
sin coincidencias difusas. Para `hotel` se pide contexto mediante
`ToolException`; se acepta `P02:hotel` o `P03:hotel`. La ambigüedad se detecta
antes del recorrido: no se usa la elegibilidad provisional para deducir
la subpolítica. Si no existe el cargo, la categoría o el recorrido, devuelve
`None`. Fallos de acceso, espera y resultados incompatibles producen un
error controlado; no se convierten en `None` ni en un monto por defecto.

La lectura ejecuta dos `MATCH` fijos y parametrizados: uno elige los
candidatos por cargo y categoría, y otro recorre las tres relaciones con
ámbito de proyecto en todos los nodos y aristas. El helper interno
`_consultar_recorrido` agrega política, versión, estado de la propuesta y
los tipos **devueltos por `relationships(camino)` en Neo4j**. No construye
una evidencia alternativa leyendo el JSON.

El RAG documental devuelve fragmentos de texto con su fuente. GraphRAG
verifica si existe una ruta entre entidades y recupera el tope vinculado
a la categoría en esa política. Un fragmento puede responder el tope
general del hotel para P02, pero no verifica la pertenencia de un cargo
a un nivel ni su recorrido de elegibilidad.

## Plan offline

Desde `tarea-final-c2/`, en PowerShell:

```powershell
& .\.venv\Scripts\python.exe -X utf8 -B -m src.conocimiento.grafo.cargar_grafo --plan
```

Solo se leen el JSON de `datos/` y la fuente Markdown. El resultado
previsto es **24 nodos** (2 cargos, 2 niveles, 10 categorías y 10 topes) y
**27 relaciones** (2 `TIENE_NIVEL`, 15 `PUEDE_RENDIR` y 10 `TIENE_TOPE`).

## Carga posterior — solo con aprobación y autorización humana

`NEO4J_DATABASE` selecciona la misma base para lectura y carga. Si no está
definida, GraphRAG usa `neo4j`; no delega la selección a la base predeterminada
del servidor. Si está definida, debe tener de 3 a 63 caracteres ASCII:
letras, dígitos, puntos o guiones, empezando por letra o dígito (Aura puede
asignar nombres que empiezan por un dígito). Un valor vacío o con espacios se
rechaza antes de abrir el driver. La validación local no comprueba que la base
exista ni que la cuenta tenga acceso.

**Pendiente de coordinación con Alex y Sebastián:** incorporar la variable
opcional `NEO4J_DATABASE=neo4j` con un comentario en `.env.example`, y acordar
la configuración de la base efectiva en despliegue y en los procesos de carga
y lectura. No se modificó `.env.example`.

1. Confirmar la versión del catálogo, las relaciones propuestas y el
   destino exacto con el grupo. Usar una base de ensayo autorizada
   e inyectar `NEO4J_URI`, `NEO4J_USER` y `NEO4J_PASSWORD` en el proceso
   seguro del operador. Si la base autorizada no se llama `neo4j`,
   definir también `NEO4J_DATABASE`. El componente no carga `.env`.
   No poner credenciales en la URI ni en comandos, logs o evidencias.
2. Usar TLS con certificados verificados si el servicio es remoto. La
   cuenta de carga necesita crear la restricción y leer/escribir las
   entidades propias. Usar otra cuenta para consultar: solo `MATCH` y
   lectura de las propiedades requeridas, con el menor alcance que
   permita la infraestructura. `READ_ACCESS` orienta el driver, **no**
   reemplaza los permisos de lectura del usuario.
3. Solo después de la autorización, sustituir `HOST` y `BASE_AUTORIZADA`
   por los valores aprobados y ajustar el esquema y el puerto si corresponde.
   Verificar el destino de forma independiente: la comparación contra
   `NEO4J_URI` y la base efectiva ocurre antes de abrir el driver.

   ```powershell
   $env:NEO4J_DATABASE = 'BASE_AUTORIZADA'
   & .\.venv\Scripts\python.exe -X utf8 -B -m src.conocimiento.grafo.cargar_grafo --cargar --confirmar-destino 'neo4j+s://HOST:7687/BASE_AUTORIZADA'
   ```

La restricción `CREATE CONSTRAINT … IF NOT EXISTS` se ejecuta primero en
una transacción de esquema. En otra transacción, `UNWIND` y `MERGE`
persisten los nodos y aristas del proyecto y verifican los conteos antes
de confirmar. Si falla la transacción de datos, la restricción puede
quedar creada; no se intenta eliminarla. No ejecutar cargas concurrentes.

Repetir la misma propuesta usa las mismas identidades y no debería
duplicarlas. Un cambio en los datos de la propuesta (incluido el orden de
las listas) cambia su huella: el cargador rechaza una huella distinta en
el proyecto y no actualiza ni borra datos existentes. La huella no es
una auditoría de ediciones hechas fuera del cargador. Una actualización
de catálogo requiere acordar una migración, fuera del alcance de esta fase.

La conexión y la sesión se cierran al terminar. Límites del driver:
3 s de conexión TCP, 5 s de adquisición y 5 s de escritura al socket.
Los tiempos de transacción son 5 s para lectura, 20 s para el esquema y
10 s para carga de datos, sin bucles de reintento de la aplicación.
No se ofrece un plazo total estricto para DNS, enrutamiento y red.

## Validación real posterior

Con autorización, ejecutar dos cargas consecutivas de la misma propuesta
y comparar los conteos e identidades del proyecto (no los totales de la
base). En una sesión operativa de **solo lectura**, comparar snapshots de
los IDs de nodo y de cada tupla `id_origen, tipo_relacion, id_destino`
antes y después de repetir la carga. Las pruebas offline verifican la
estrategia con mocks; no demuestran qué hizo Neo4j.

Usar `$proyecto = "grupo05-tarea-final-c2-graphrag"` como parámetro en
las dos consultas de snapshot:

```cypher
MATCH (n:Grupo05C2GraphRAG {proyecto: $proyecto})
RETURN n.id AS id ORDER BY id
```

```cypher
MATCH (a:Grupo05C2GraphRAG {proyecto: $proyecto})-[r {proyecto: $proyecto}]->
      (b:Grupo05C2GraphRAG {proyecto: $proyecto})
WHERE type(r) IN ['TIENE_NIVEL', 'PUEDE_RENDIR', 'TIENE_TOPE']
RETURN a.id AS origen, type(r) AS tipo, b.id AS destino ORDER BY origen, tipo, destino
```

En otro proceso con las credenciales de lectura y la misma base, ejecutar el diagnóstico
desde `tarea-final-c2/`. Solo después de la carga real autorizada:

```powershell
@'
import json
from langchain_core.tools import ToolException
from src.conocimiento.grafo.consultar import _consultar_recorrido

cargo, categoria = "Jefe de tienda", "P02:hotel"
try:
    recorrido = _consultar_recorrido(cargo, categoria)
except ToolException as error:
    raise SystemExit(str(error)) from None
print(json.dumps({"consulta": [cargo, categoria], "recorrido": recorrido}, ensure_ascii=False))
'@ | & .\.venv\Scripts\python.exe -X utf8 -B -
```

| Cargo | Categoría | Resultado esperado del diagnóstico |
|---|---|---|
| Jefe de tienda | `P02:hotel` | Jefatura, ruta completa, `#P02`, 445.000 CLP. |
| Jefe de tienda | `P03:hotel` | Jefatura, ruta completa, `#P03`, 325.000 CLP. |
| Analista de Operaciones | `P02:hotel` | Profesional, ruta completa, `#P02`, 445.000 CLP. |
| Analista de Operaciones | `P03:hotel` | Sin recorrido en la propuesta; no equivale a prohibición. |
| Jefe de tienda | `hotel` | Categoría ambigua: pide P02 o P03. |
| Cargo inexistente | `P02:hotel` | `None`, sin nivel por defecto. |
| Jefe de tienda | `P02:taxi` | `None`; el catálogo solo cubre topes de estadía. |

Para la pauta, conservar la entrada, el recorrido observado con fuente y
los conteos reales. La pregunta distintiva sería: «¿Qué camino de nivel
tiene un jefe de tienda hasta el tope de hotel en un viaje interno?».
El texto de la respuesta debe distinguir el nivel propuesto del monto
documental. La demostración vía `/chat` y el `id_ejecucion` quedan pendientes
de la validación remota; las pruebas directas informadas no sustituyen esa evidencia.
