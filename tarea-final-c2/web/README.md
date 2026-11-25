# Rendiciones IA — frontend

**Dueño:** Eduardo. Panel académico de Comercial Los Alerces SpA (ficticia).
FastAPI sirve `index.html` en `GET /`. Conserva del Taller 2 la entrada con
clave, la estructura responsive de tarjetas, las burbujas de texto con un
subconjunto de Markdown seguro y la cancelación con descarte de respuestas
tardías. No usa CDN ni tiene modo de demostración.

## Arranque local

Desde `tarea-final-c2/`, con el entorno existente y sin cargar `.env`:

```powershell
$env:PYTHON_DOTENV_DISABLED = '1'
$secreta = Read-Host 'API_KEY_SERVICIO para esta sesión local' -AsSecureString
$env:API_KEY_SERVICIO = [System.Net.NetworkCredential]::new('', $secreta).Password
try {
    & .\.venv\Scripts\python.exe -B -m uvicorn api.app:app --host 127.0.0.1 --port 8000
} finally {
    Remove-Item Env:API_KEY_SERVICIO -ErrorAction SilentlyContinue
    $secreta.Dispose()
}
```

Abre `http://127.0.0.1:8000/` e ingresa la misma clave, sin pegarla en la
conversación. Abrir `index.html` directamente no conecta con la API.
Con el backend de esta rama, una consulta autenticada a `/chat` todavía
puede devolver **501** porque el router no está integrado; el panel lo
explica sin simular una respuesta. `/registro` depende también del registro
de ejecuciones. No se garantiza continuidad tras reiniciar el servidor
hasta integrar y validar el checkpointer.

## Flujo y contrato

- Las sugerencias rellenan un borrador vacío; el envío es deliberado.
  `POST /chat` envía `{thread_id, texto, imagen?}`. El identificador se
  genera con Web Crypto, se mantiene durante el hilo y cambia al iniciar
  otro. El texto debe tener 1 a 4000 caracteres Unicode.
- Se verifica `id_ejecucion` (UUIDv4), `thread_id`, `ruta`, `respuesta`
  y `estado_final`. El `veredicto`, si viene en `revisar_gasto`, se valida
  y se muestra como tarjeta. La interfaz no infiere una decisión, no
  calcula montos y no inventa un campo de fuentes: mantiene las citas
  del texto. HTTP 200 no equivale a `estado_final: ok`.
- Los detalles de cada respuesta ofrecen `GET /registro/{id_ejecucion}`
  bajo demanda. El identificador se valida y codifica. Se muestran la
  fecha, ruta, pasos, herramientas, A2A, estado y duración que devolvió
  el servidor. 404 indica que ese registro no se encontró.
- Las fallas conservan el borrador. El chat espera hasta 65 s y la consulta
  de registro hasta 15 s. Se evita el doble envío y no hay reintentos
  automáticos. Cancelar la espera no garantiza que el servidor deje de
  procesar. Una respuesta tardía no se incorpora a otro hilo.

## Seguridad e imágenes

La clave se borra del campo al cargarla y vive en memoria, no en URL,
cookies, almacenamiento web ni logs de la interfaz. Se envía solo en
`X-API-Key`, al mismo origen, sin credenciales ambientales ni
redirecciones. «Clave cargada» no implica autorización: «Acceso
verificado» se muestra tras una respuesta autenticada y válida. Un
401 elimina la clave y conserva el borrador para reintentar. Cambiar
clave expresamente o salir de la página limpia sesión y borrador.
`GET /health` es público y no se usa para declarar acceso o disponibilidad.

Se aceptan JPEG, PNG y WebP con tipo y firma binaria compatibles.
El límite de **5 MiB** es un control del navegador, no un límite
contractual del backend. Se muestra nombre, tamaño y una vista previa
local; los Object URLs se revocan al sustituir, quitar, limpiar o enviar
la imagen. Se envía `{mime_type, datos_base64}` sin prefijo Data URL.
No hay OCR ni persistencia local de imágenes.

El DOM presenta texto literal, negritas, títulos y código en línea como
nodos seguros, sin interpretar HTML o enlaces de la respuesta. La CSP
limita conexiones al mismo origen e imágenes a Object URLs; los bloques
inline de CSS y JavaScript se autorizan por hash. Si se editan, actualizar
los hashes SHA-256 en la meta CSP, incluyendo saltos de línea del bloque.
La prueba estática comprueba esos hashes. Para un entorno remoto usar HTTPS.

## Pruebas y evidencias posteriores

```powershell
$env:PYTHON_DOTENV_DISABLED = '1'
$env:LANGSMITH_TRACING = 'false'
$env:LANGCHAIN_TRACING_V2 = 'false'
& .\.venv\Scripts\python.exe -X utf8 -B -m pytest tests/test_frontend_eduardo.py -p no:cacheprovider
& .\.venv\Scripts\python.exe -X utf8 -B -m pytest -p no:cacheprovider
```

Las pruebas verifican la portada y protección de `/chat` con FastAPI en
proceso. Los casos del navegador usan Chromium local vía DevTools y
respuestas **simuladas solo en pruebas**. No instalan herramientas ni
entran a servicios remotos; si Chromium o el cliente WebSocket local no
están disponibles, se omiten solo los casos del navegador.

En Chrome se comprobaron `1920×1080`, `1366×768`, `768×1024`, `390×844`
y `320×640`: sin desborde horizontal, con el adjunto y la trazabilidad
presentes y con los controles alcanzables al desplazarse. El navegador
generó capturas de prueba en memoria; no se guardaron como evidencia.

Después de que Alex integre las rutas y Sebastián habilite el registro y
la memoria, repetir la revisión con servicios autorizados. Registrar las
dimensiones, la entrada ficticia, la respuesta real y el ID de ejecución
correspondiente. Capturar acceso (sin mostrar la clave), conversación,
veredicto y detalle del registro, además de escenarios 401 y 501 si
corresponden. No usar las respuestas simuladas como evidencia del agente.
