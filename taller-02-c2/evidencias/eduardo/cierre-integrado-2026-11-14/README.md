# Cierre integrado de Eduardo · LOCAL · 2026-11-14

Base probada **`741305bf0fed986b523898114bb1d851d28d063b`** más cambios locales sin
commit: fallback genérico de 503, regresión específica y retirada de la demo sin uso
del Taller 2. Las huellas SHA-256 del HTML, suite y ejecutor están en ambos JSON de
resultados. Los documentos se actualizaron después, sin cambiar esos archivos probados.

## Automatización sin proveedor real

| Evidencia | Resultado / procedencia |
| --- | --- |
| [pytest-proyecto.txt](pytest-proyecto.txt) | **168 passed in 10.88s**, salida 0. Pruebas del proyecto, con dobles; sin credenciales reales. |
| [pytest-frontend.txt](pytest-frontend.txt) | **68 passed in 69.11s**, salida 0; sin `xfail`. Incluye 401 reales de middleware con grafo sustituido y 503 JSON/HTML de regresión. |
| [resultados-pruebas.json](resultados-pruebas.json) | Fecha, commit base, huellas, salidas y comprobaciones de conservación. |
| [capturas-regresion/](capturas-regresion/) | Ocho capturas de esta repetición: 01, 02, 04, 05, 06, 07, 08 y 09. Las respuestas/errores/demoras son **SIMULADOS**, salvo la propia pantalla de ingreso real. No se genera una nueva 03 en la suite actual. |
| [09-503-html-simulado.png](capturas-regresion/09-503-html-simulado.png) | HTML de proxy simulado: indisponibilidad temporal, sin atribuirlo a `CLAVE_API`. |

Ejecución con Python 3.12.10, pytest 9.2.0, Playwright 1.65.1 y Chrome instalado.
`CARPETA_CAPTURAS` apuntó a `capturas-regresion` de esta carpeta nueva. Las capturas
originales de la carpeta superior y las seis manuales no se sobrescribieron.
El timeout usa reloj virtual; móvil es emulación, no dispositivo físico.

Se mantiene intacta la comprobación del backend
`tests/test_seguridad.py::test_servidor_sin_clave_no_queda_abierto`, que exige 503 con
`detail` JSON cuando falta la configuración de acceso. La suite del frontend mantiene
su variante JSON 503 y comprueba que el texto corto válido se conserve como texto
inerte; el cambio genérico no borra esa información válida.

## Casos HTTP reales, sin dobles

[resultados-locales.json](resultados-locales.json) conserva pregunta exacta, estado,
cuerpo, comprobaciones y respuesta visible. Ejecución 13:55:05–13:55:50, UTC−03:00;
orden R06 → R07 → R05 → R09. R05 no se reintentó.

| Caso | Obtenido | Captura y registro |
| --- | --- | --- |
| R05 · clave temporal válida | **200**. Agente de Eduardo, motivo, presupuesto $2.173.600 CLP, supuestos y advertencias. **Llamada real al coordinador, A2A y Gemini**, con precios de demostración. | [r05-acceso-permitido.png](r05-acceso-permitido.png), [servidor-integrado.txt](servidor-integrado.txt) |
| R06 · sin cabecera de acceso | **401** con detalle de clave ausente; aún 0 preguntas al coordinador y 0 envíos A2A. | [r06-sin-clave.png](r06-sin-clave.png), mismo registro integrado |
| R07 · clave incorrecta en panel | **401** con detalle, retorno al ingreso, campo de clave vacío y pregunta conservada; aún 0 preguntas al coordinador y 0 envíos A2A. | [r07-clave-incorrecta.png](r07-clave-incorrecta.png), mismo registro integrado |
| R09 · otro proceso sin configuración del proveedor | **502** con detalle sanitizado de falta de configuración de Gemini; pregunta conservada y envío habilitado. Error real del SDK, **no prueba de rechazo remoto, cuota ni caída de Gemini**. | [r09-proveedor-sin-configuracion.png](r09-proveedor-sin-configuracion.png), [servidor-r09-aislado.txt](servidor-r09-aislado.txt) |

R06 usa httpx sin `X-API-Key`. Su imagen incorpora una visualización rotulada del estado
y JSON realmente recibidos; no finge que el panel tenga un flujo nativo de envío sin
clave. Las otras tres imágenes muestran el resultado real del panel, con una franja de
procedencia y altura del chat ampliada para conservar el contenido, sin editar respuestas.

La clave de acceso temporal y las variables locales se pasaron solo por el entorno del
proceso hijo. R05 leyó la configuración privada existente del proveedor; para R09 se
vaciaron `GOOGLE_API_KEY` y `GEMINI_API_KEY`, se desactivó Vertex y se deshabilitó dotenv
solo en el otro hijo. **`.env` no se editó ni se copió a las evidencias.** Los hijos
escucharon únicamente en loopback y se detuvieron al finalizar. No se tocó Heroku ni
ninguna instancia previa. No se guardaron claves, cabeceras de petición, HAR o trazas.
Los registros se sanitizaron en memoria antes de guardarlos; usan UTF-8 y conservan A2A
sin los errores históricos de codificación.

## Alcance, repetición y PR

- [referencias-demo.txt](referencias-demo.txt): búsquedas y rutas que justifican retirar
  solo `taller-02-c2/proyecto/src/agente_eduardo/demo.html`.
- [revision-final.json](revision-final.json): conservación, huellas, privacidad y alcance.
- [archivos-para-pr.txt](archivos-para-pr.txt): lista exacta desde la raíz, incluida la
  eliminación: **29 rutas (5 modificadas, 23 nuevas y 1 retirada)**. No incluye `.env`,
  `.venv`, la foto del Taller 1 ni archivos ajenos.
- [../validar_cierre_local.py](../validar_cierre_local.py): ejecutor reproducible; fases
  `pruebas` y `casos`, con `--carpeta` nueva dentro de `evidencias/eduardo`. La fase
  `casos` sí consume una consulta real a Gemini. No repetirla innecesariamente.
- [Documento vigente](../../../documento-Eduardo.md): comandos, revisión de Alex y
  pendientes R08/R10/R11/R12, otros agentes con formato actual y despliegue público.

Las pruebas del 13-11-2026 se mantienen como históricas en la carpeta superior y en el
documento, no como estado actual. Este cierre se publicó después en el commit `d8cce13`
(PR #82, unido a `main` el 2026-11-15).
