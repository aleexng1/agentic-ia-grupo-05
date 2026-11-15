# Pendientes locales de Eduardo · 14-11-2026

**Base publicada:** `d8cce1337b7caf0bcd63df2d9ce21d9dc96a3f91`, rama
`c2t2/eduardo-frontend`, **PR #82 abierto**. Esta nueva continuación no tiene commit/push
ni staging. Solo cambian documentación y evidencias de Eduardo, no producción.

**Entorno:** Windows; Python 3.12.10; Playwright 1.65.1; httpx 0.28.1;
Chrome 157.0.8103.78 sin ventana, vista de 1280 × 960. `.venv` reutilizada, sin instalar
dependencias. Horas locales **UTC−03:00**, 14:50:56–15:05:37 del 14-11-2026.

## Resultados finales y fuentes

| Caso | Resultado | Fuente y captura |
| --- | --- | --- |
| R08 · app integrada real y autorización válida | **400** con `texto: "   "`; **422** al omitir `texto`. Cero preguntas al coordinador y cero A2A antes de las consultas funcionales. | [Captura HTTP completa](r08-entrada-protegida.png), [log integrado](servidor-integrado-consultas.txt). La imagen es una visualización rotulada de httpx, no un aviso nativo del panel. |
| R01-actual · Matías · consulta real | **200**, `Agente de Matias`, motivo y programa con 60 minutos libres. | [Pregunta/respuesta íntegras](r01-actual-intercambio.json), [captura actual](r01-actual-consulta-real.png). |
| R02-actual · Alex · consulta real | **200**, `Agente de Alex`, motivo y tres recintos con advertencias. | [Pregunta/respuesta íntegras](r02-actual-intercambio.json), [captura actual](r02-actual-consulta-real.png). |
| R04-actual · Sebastián · consulta real | **200**, `Agente de Sebastian`, motivo; servicios 11:00/13:30, dietas 65/10/5 y 88 litros de agua. | [Pregunta/respuesta íntegras](r04-actual-intercambio.json), [captura actual](r04-actual-consulta-real.png). |
| R10 · app propia real detenida y restaurada | **`ERR_CONNECTION_REFUSED`**, aviso de conexión, pregunta y controles recuperados. Restauración en el mismo puerto: salud/panel 200 y POST autorizado con espacios 400. | [Resultado](finalizacion/r10-resultado.json), [desconexión](finalizacion/r10-desconexion-real.png), [restauración](finalizacion/r10-restaurado.png), [log previo](finalizacion/servidor-r10-antes.txt), [log restaurado](finalizacion/servidor-r10-restaurado.txt). |
| R11 · **falla inducida en entorno controlado** | Aviso tras **65,471770 segundos reales**; demora del servidor **70,009151 s**. Nueva conversación con contexto distinto, sin respuesta vieja. | [Mediciones y eventos](complemento/r11-resultado.json), [espera](complemento/r11-espera-real-inducida.png), [timeout](complemento/r11-timeout-real-inducido.png), [conversación nueva](complemento/r11-nueva-sin-respuesta-vieja.png), [log](complemento/servidor-r11.txt). |
| R12 · **falla inducida en entorno controlado** | HTTP real **200 `text/html`**; aviso no JSON, HTML no insertado, script no ejecutado y controles/pregunta recuperados. | [Resultado](finalizacion/r12-resultado.json), [captura](finalizacion/r12-html-controlado.png), [log](finalizacion/servidor-r12-html.txt). |

**R11/R12 NO son fallas reales de Gemini ni Heroku.** Son respuestas/demoras deliberadas
de un servidor separado, sin claves del proveedor y sin cargar `.env`. Sirve el
`panel.html` intacto por HTTP de loopback, sin interceptar `fetch` ni cambiar el reloj.
En R11 el navegador aborta; el servidor sigue hasta generar su respuesta a los 70 s.
No se fuerza a `fetch` a ignorar la cancelación. En R12 se conserva el HTML crudo con
una **segunda petición httpx**, identificada separadamente de la del panel.

Las tres consultas funcionales sí pasan por **coordinador, A2A y Gemini reales**, con un
envío/recepción A2A por agente en [el log](servidor-integrado-consultas.txt). Se enviaron
una vez cada una, en conversaciones distintas; no se repitieron durante las fases
complementarias. Los datos de los agentes son de demostración, no reservas/contratos.

## Procedencia e incidencias del instrumental

[resultados-consolidados.json](resultados-consolidados.json) es un **índice posterior**
que referencia las fuentes, no una supuesta salida original del primer ejecutor.

1. [verificar_pendientes.py](verificar_pendientes.py) ejecutó R08 y las tres consultas
   funcionales aprobadas. También observó un primer R11 real (65,404 s en su captura),
   pero el comando terminó por su límite de **360 s** antes del resumen final.
   **No existe `resultados-locales.json` de esa fase.** Se conservan sus imágenes y logs.
   Los cuerpos de R08 se transcriben en la consolidación desde la captura completa,
   contrastados con los estados HTTP del log; no se inventa una fuente primaria JSON.
2. [verificar_complemento.py](complemento/verificar_complemento.py) guarda inmediatamente
   cada resultado y cada línea sanitizada. Conserva [los no aprobados](complemento/resultados-complemento.json):
   R10 quedó en `ConnectTimeout` del chequeo auxiliar, **antes** del envío del panel;
   R12 quedó esperando `response.text()` del instrumental aunque el log registra 200
   HTML. **R11 sí terminó aprobado**, con mediciones completas y reloj real.
3. [completar_r10_r12.py](finalizacion/completar_r10_r12.py) corrigió **solo el instrumental**:
   acepta los dos errores posibles al chequear un puerto detenido y evita bloquearse
   leyendo el cuerpo HTML descartado por el panel. Primero comprueba el aviso y luego
   obtiene el HTML con httpx. [R10/R12 aprobados](finalizacion/resultados-finalizacion.json).

No se borraron intentos ni se convirtió un no aprobado en aprobado retroactivamente.
No se detectó ni corrigió un defecto de producción. **No se ejecutó pytest ni se
repitieron las suites completas** ya aprobadas: 168 y 68 son resultados anteriores,
no conteos nuevos de esta carpeta.

## Aislamiento y privacidad

- Las apps integradas propias usan `PORT`, `PUERTO`, `URL_BASE`, `URLS_AGENTES` y una
  `CLAVE_API` temporal solo en el entorno de sus hijos. Las consultas funcionales leen
  la configuración privada del proveedor existente; el servidor de ensayo no la recibe.
- En R10 se detuvo exclusivamente el árbol del PID de `Popen`, no procesos por nombre
  ni por un puerto ajeno. El servidor se **restauró y verificó en el mismo puerto** antes
  de cerrar los procesos propios de la comprobación. No se cortó la conexión del equipo.
- El servidor previo **127.0.0.1:8000, PID 3772**, del 13-11-2026, no se detuvo ni reinició.
  Seguía escuchando con el mismo PID al terminar. No se modificó Heroku.
- Los registros se sanitizaron en memoria antes de guardarlos. No se guardaron claves,
  cabeceras de petición, HAR, trazas de navegador ni archivos de configuración privados.
  Las capturas verifican el campo de clave vacío y el contenido del DOM sin valores
  sensibles, añaden procedencia y solo amplían la altura del chat; no cambian respuestas.
- [revision-final.json](revision-final.json): 90 archivos protegidos de la línea base
  conservados, incluido `.env`, foto y demo del Taller 1, capturas/logs históricos y
  código de producción; revisión de alcance, enlaces, índice y privacidad. La línea base
  privada permanece fuera del repo. La revisión no equivale a una auditoría de seguridad.
- [archivos-modificados.txt](archivos-modificados.txt): lista cerrada de esta continuación,
  sin la foto previa, `.env` ni archivos ajenos. No es la selección del commit anterior.

## Repetir solo las comprobaciones necesarias

Desde `taller-02-c2/proyecto`, elegir **otro destino nuevo** en cada ocasión:

```powershell
$destino = Join-Path "../evidencias/eduardo" ("repeticion-r11-" + [guid]::NewGuid().ToString("N"))
.\.venv\Scripts\python.exe -B ../evidencias/eduardo/pendientes-locales-2026-11-14-144554/complemento/verificar_complemento.py --carpeta $destino --casos R11

$destino = Join-Path "../evidencias/eduardo" ("repeticion-r10-r12-" + [guid]::NewGuid().ToString("N"))
.\.venv\Scripts\python.exe -B ../evidencias/eduardo/pendientes-locales-2026-11-14-144554/finalizacion/completar_r10_r12.py --carpeta $destino
```

Estos comandos no consumen consultas a Gemini, no ejecutan suites y no usan reloj virtual.
No repetir el ejecutor inicial innecesariamente: contiene las tres consultas reales al
proveedor y se conserva como fuente de lo efectivamente ejecutado, con sus límites.

[Documento vigente de Eduardo](../../../documento-Eduardo.md).
