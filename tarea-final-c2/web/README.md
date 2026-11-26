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
El backend integrado usa `/chat` asíncrono por defecto. Para comprobar
recorridos reales se necesitan los servicios configurados; la portada
por sí sola no prueba su disponibilidad.

## Flujo y contrato

- Las sugerencias rellenan un borrador vacío; el envío es deliberado.
  `POST /chat` envía `{thread_id, texto, imagen?, gasto?}`. El identificador se
  genera con Web Crypto, se mantiene durante el hilo y cambia al iniciar
  otro. El texto debe tener 1 a 4000 caracteres Unicode.
- **Datos del gasto (JSON)** es opcional y plegable; expone un ejemplo basado
  en `G-001` y la boleta ficticia `000123`. Admite solo objetos JSON y se puede
  combinar con la imagen. Si está vacío no se envía. El navegador no completa
  campos ni reserializa el objeto (incluidos montos, `rut_emisor`, `folio`
  y `cargo`); el servidor valida el contrato §4 y §11.1.
- Según §11.1 bis, el `202` debe devolver un UUIDv4, el mismo `thread_id`
  y `estado: en_proceso`. El chat ignora `consultar` y construye la URL
  local `/registro/{id_ejecucion}`. Consulta de a una vez (1,5 s entre
  respuestas en progreso), con clave en cada GET. También acepta el `200`
  completo que usa el modo síncrono (`POST /chat?esperar=true`); la web no
  fuerza ese modo ni repite el POST.
- Se verifica `id_ejecucion` (UUIDv4), `thread_id`, `ruta`, `respuesta`
  y `estado_final`. El `veredicto`, si viene en `revisar_gasto`, se valida
  y se muestra como tarjeta. La interfaz no infiere una decisión, no
  calcula montos y no inventa un campo de fuentes: mantiene las citas
  del texto. HTTP 200 no equivale a `estado_final: ok`.
- El registro puede devolver `ok`, `bloqueado`, `fallback` o `error` con
  resultado completo o, en un error, `detail`. Tras reinicio o expulsión de
  memoria puede quedar solo la fila: se muestra lo registrado sin inventar
  una respuesta. También pueden aparecer 404 (sin registro) o 503 (registro
  no disponible). El estado en memoria requiere un único proceso/dyno hasta
  que se persista en el backend. Limitación conocida del #100: la API usa
  `sin_ruta` para errores previos al enrutamiento, pero el `CHECK` de la
  tabla actual no lo admite; esos casos podrían perder su fila al reiniciar.
- Los detalles de cada respuesta ofrecen `GET /registro/{id_ejecucion}`
  bajo demanda. El identificador se valida y codifica. Se muestran la
  fecha, ruta, pasos, herramientas, A2A, estado y duración que devolvió
  el servidor. 404 indica que ese registro no se encontró.
- Las fallas conservan texto, imagen y gasto. Los 422/502 muestran el `detail`
  seguro y su referencia de ejecución si viene, o el mensaje HTTP si no hay
  detalle utilizable. En validaciones FastAPI solo se muestran campos conocidos
  y mensajes, nunca `input`, contexto ni el cuerpo completo.
- La espera automática está acotada a **105 s** (tope por defecto del
  servidor §11.1 ter: 90 s + margen); una consulta bajo demanda, a 15 s.
  «Detener espera» solo detiene el navegador; ninguna respuesta tardía
  se incorpora. Con un 202 válido, el borrador queda bloqueado y «Retomar
  consulta del registro» consulta el mismo ID sin un nuevo POST, incluso
  tras reautenticación. «Nueva conversación» descarta el borrador y permite
  consultar el último ID conocido en esta pestaña sin incorporar el turno anterior.
  Si se detuvo antes de recibir el 202, no hay ID que la web pueda recuperar.
  Si no hay confirmación del POST, verifica el estado antes de reenviar el
  gasto: detener la espera o recibir una respuesta inválida no implica que se canceló.
  Si se aumenta el tope del servidor por sobre 105 s, el navegador puede
  dejar de esperar mientras el servidor sigue; usar «Retomar» y coordinar
  el margen con el equipo de despliegue.

## Seguridad e imágenes

La clave se borra del campo al cargarla y vive en memoria, no en URL,
cookies, almacenamiento web ni logs de la interfaz. Se envía solo en
`X-API-Key`, al mismo origen, sin credenciales ambientales ni
redirecciones. «Clave cargada» no implica autorización: «Acceso
verificado» se muestra tras una respuesta autenticada y válida. Un
401 elimina la clave y conserva el borrador; si ya se aceptó el turno, se
retoma solo el GET. Cambiar clave conserva el borrador; salir de la página
limpia la sesión. La clave y el gasto no se guardan en almacenamiento web.
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
La prueba estática comprueba esos hashes. No se acepta una clave por HTTP
fuera de `localhost`, `127.0.0.1` o `[::1]`; para un entorno remoto usa HTTPS.

## Pruebas y evidencias posteriores

```powershell
$env:PYTHON_DOTENV_DISABLED = '1'
$env:LANGSMITH_TRACING = 'false'
$env:LANGCHAIN_TRACING_V2 = 'false'
# En una consola sin credenciales de servicios, usar un temporal nuevo dentro del proyecto.
& .\.venv\Scripts\python.exe -X utf8 -B -m pytest tests/test_frontend_eduardo.py -p no:cacheprovider
& .\.venv\Scripts\python.exe -X utf8 -B -m pytest -ra -p no:cacheprovider --basetemp ".pytest-offline-$PID"
```

Las pruebas verifican la portada y protección de `/chat` con FastAPI en
proceso. Los casos del navegador usan Chromium local vía DevTools y
respuestas **simuladas solo en pruebas**. No instalan herramientas ni
entran a servicios remotos; si Chromium o el cliente WebSocket local no
están disponibles, se omiten solo los casos del navegador.
Cubren errores HTTP y XSS, JSON de gasto con imagen, respuestas 200 y
202, seguimiento de estados, reinicio simulado, cancelación, timeout,
reautenticación, respuestas tardías y ausencia de POST duplicados.

En Chrome se comprobaron `1920×1080`, `1366×768`, `768×1024`, `390×844`
y `320×640`: sin desborde horizontal, con adjunto, JSON plegable y trazabilidad
presentes y con los controles alcanzables al desplazarse. El navegador
generó capturas de prueba en memoria; no se guardaron como evidencia.

Con un despliegue autorizado, queda repetir la revisión web ficticia junto
con Sebastián y capturar conversación, veredicto y registro sin mostrar la
clave. Para evidencia de solo lectura por API, ver
[`ampliacion-rag`](../evidencias/ampliacion-rag/README.md). Las respuestas
simuladas no acreditan una ejecución real.
