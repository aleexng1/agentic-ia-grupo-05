# Documento de entrega — Taller A2A — Grupo 5 — Eduardo Basaure

**Tema del grupo:** planificador de ferias y eventos.
**Agente:** Agente de Eduardo — presupuestos y costos simulados — `src/agente_eduardo/` — puerto 8005.

Este documento separa los archivos y comprobaciones disponibles de las verificaciones que aún no se han realizado. No se agregaron capturas ni se repitieron pruebas A2A en esta integración.

## 1. Blueprint

Ver [`blueprint-Eduardo.md`](blueprint-Eduardo.md). El agente estima presupuestos agregados ficticios en CLP para eventos tecnológicos, gastronómicos, culturales e infantiles. `estimar_presupuesto` calcula recinto referencial, equipamiento, personal, logística, alimentación genérica, subtotal, contingencia y total.

La herramienta acepta de 10 a 500 personas y de 30 a 480 minutos. Redondea la duración a bloques de 30 minutos y calcula una contingencia del 10 %. Los importes son simulados: no son precios reales ni autorizan compras, reservas, pagos o contrataciones. Impuestos no modelados. No prepara menús, recomienda recintos ni arma programas de actividades.

## 2. Integración realizada

Se incorporó el agente individual existente, sin reconstruirlo: `__init__.py`, `tools.py`, `prompts.py`, `graph.py`, `server.py` y `demo.html`. También se incorporó únicamente `tests/test_tools_eduardo.py`, prueba propia de Eduardo.

La comprobación del registro encontró `eduardo` apuntando a `src.agente_eduardo` en `proyecto/main.py`; `.env.example` ya contiene `URL_EDUARDO=http://127.0.0.1:8005`. Ambos archivos compartidos quedaron sin modificar.

## 3. Verificaciones ejecutadas en esta integración

- **Pruebas automatizadas del repositorio:** `70 passed in 1.54s` con `-B -m pytest -p no:cacheprovider tests -q`, ejecutado desde `taller-01-c2/proyecto` usando el Python del entorno individual de origen (`Taller_A2A_Eduardo/proyecto/.venv`), porque el Python global disponible no tiene instalado `pytest`. No se cambiaron dependencias ni se copió el entorno.
- **Importación del paquete:** `import src.agente_eduardo` completó correctamente desde `taller-01-c2/proyecto`.
- **Sintaxis Python:** `ast.parse` aceptó los seis módulos Python del agente y `tests/test_tools_eduardo.py`.
- **Archivos compartidos:** el registro y la variable de entorno se comprobaron; no se modificaron `main.py`, `.env.example`, `src/comun/`, `src/coordinador/`, dependencias ni scripts compartidos.

Estas pruebas no ejecutan el modelo Gemini ni inician el servidor A2A.

## 4. Evidencias disponibles

Se copiaron los artefactos de Eduardo `02-ficha.json`, `04-a2a-publico.json` y `respuesta-a2a.json` a `evidencias/eduardo/`. Son archivos aportados desde el proyecto individual; su presencia no implica que se hayan vuelto a generar o verificar contra un servidor activo durante esta integración.

Se excluyeron `02-ficha-antes.json` y `diagrama.txt`, que corresponden al agente de Sebastián. La revisión de las evidencias seleccionadas no encontró claves, tokens, contraseñas, credenciales ni información personal evidente. La ficha y la respuesta guardada muestran una URL local (`127.0.0.1:8005`), no una dirección pública comprobada en esta integración.

## 5. Pendientes

- Verificar con el responsable que el servidor A2A arranque y que responda en ejecución.
- Repetir una consulta A2A y comprobar la publicación/alcance externo si se requiere evidencia de funcionamiento actual.
- Agregar capturas únicamente cuando se hayan tomado; no se recibieron capturas en las evidencias individuales disponibles.
- Completar la verificación conjunta del coordinador y la ronda de preguntas del grupo.

No se ejecutaron `git add`, commit, push ni creación de pull request. Los archivos quedan preparados para revisión de Eduardo.
