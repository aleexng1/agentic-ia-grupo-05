# Reproducibilidad de 2b754e2 · LOCAL · 15-11-2026

**Resultado:** instalación, `pip check`, arranque y seis comprobaciones HTTP aprobados
en una copia temporal del commit **`2b754e2e2bb8b035888f281ced1b3c36d6b1bab4`**.
No se consultó Gemini. Esto **no** certifica toda la aplicación ni un despliegue remoto.

**Estado de publicación:** el **PR #82 está fusionado en `main`** mediante
`71df3e80adea7ec675db73eefe884cb82eeffc9a`. La rama local incorporó ese commit por
fast-forward y las 12 rutas del cierre quedan preparadas en el índice, sin commit
ni push. **La versión usada para la instalación limpia sigue siendo `2b754e2`**;
sus fechas y resultados originales no se cambiaron ni se repitieron las pruebas.

## Fuente y aislamiento

- Se leyeron los README de la raíz, del Taller 2 y del proyecto, y `proyecto/AGENTS.md`.
  La guía de instalación seguida es `taller-02-c2/README.md`, enlazada por el README
  del proyecto: secciones Instalación, Configuración y Cómo iniciar. No se instaló
  el hook Git del flujo de notebooks de la raíz ni se cambió ningún hook existente.
- Rama durante la instalación: `c2t2/eduardo-frontend`. `HEAD`, la rama publicada y
  `refs/pull/82/head` coincidían entonces en `2b754e2`. `git ls-remote` solo lee
  referencias; no actualiza ramas ni el PR. El avance posterior a `71df3e8` no cambia
  la procedencia de la instalación limpia.
- Fuente exportada con `git archive`, sin copiar `.env`, `.venv` ni archivos sin seguimiento.
  La copia y el entorno nuevo están bajo la carpeta temporal aprobada de OpenCode, fuera
  del repositorio. No se creó un worktree ni se cambió la rama de trabajo.
- Python **3.12.10, Windows AMD64**; pip **25.0.1**. La `.venv` recién creada contenía
  **solo pip**; `include-system-site-packages = false`. Se quitaron `PYTHONPATH`,
  `PYTHONHOME` y `VIRTUAL_ENV` heredados en los hijos y se deshabilitó el sitio de usuario.
  No se usó el Python ni los paquetes de la `.venv` original; instalación sin caché.
- Se copió `.env.example` a `.env` **solo dentro de la copia nueva**, sin claves.
  Para el servidor se deshabilitó dotenv y se vaciaron las credenciales Google/Gemini,
  Vertex y el trazado externo. La clave temporal de acceso y otra incorrecta se generaron
  con `secrets.token_urlsafe(32)` en memoria; sus valores no se imprimen ni se guardan.
- Servidor propio: lanzador **29636**, uvicorn **32100**, puerto libre **58569**.
  `PORT = PUERTO = 58569`, `URL_BASE = http://127.0.0.1:58569`, `URLS_AGENTES` vacía.
  Solo se escuchó en loopback; el servidor previo de **8000, PID 3772**, no se utilizó.

## Comandos y versiones

Secuencia, desde la raíz y después desde el proyecto **de la copia**, respectivamente.
En una repetición, sustituir los marcadores `<...>` por rutas propias:

```powershell
git status --short --branch
git diff --cached --name-status
git ls-remote origin refs/heads/c2t2/eduardo-frontend refs/pull/82/head
git archive --format=zip --output="<TEMPORAL>\fuente-2b754e2.zip" 2b754e2e2bb8b035888f281ced1b3c36d6b1bab4
# Extraer el ZIP en <TEMPORAL>/copia; situarse en copia/taller-02-c2/proyecto.
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip list --format=json
.\.venv\Scripts\python.exe -m pip install --no-cache-dir --timeout 30 -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pip list --format=json
Copy-Item .env.example .env
```

Se usó el ejecutable explícito del entorno nuevo en lugar de activar PowerShell; no se
cambió la política de ejecución ni se actualizó pip. Los indicadores adicionales solo
desactivan la caché, fijan timeout y evitan avisos/interacción de pip. El servidor se
inició con el equivalente de la instrucción del README, sin `--reload` para mantener
un único árbol propio y con puerto distinto de 8000:

```powershell
.\.venv\Scripts\python.exe -B -m uvicorn app:app --host 127.0.0.1 --port 58569
```

El [ejecutor puntual](comprobar_http.py) pasa las variables solo al proceso hijo,
elige otro puerto libre en cada ejecución y emite exactamente dos GET y cuatro POST:

```powershell
# Con Python de la .venv NUEVA, no con el de la instalación original:
& "<VENV_NUEVO>\Scripts\python.exe" -B "<EVIDENCIAS>\comprobar_http.py" --proyecto "<COPIA>\taller-02-c2\proyecto" --destino "<OTRO_DESTINO_NUEVO>" --etiqueta readme
```

Registro de instalación: **12:52:59–12:53:46, UTC−03:00**. HTTP:
**12:54:18–12:54:24**, del **15-11-2026**. Todas las salidas de instalación y `pip check`
fueron **0**. Versiones principales resueltas:

| Paquete | Versión | Paquete | Versión |
| --- | --- | --- | --- |
| langchain | 1.5.0 | langchain-core | 1.8.1 |
| langgraph | 1.2.22 | langchain-google-genai | 4.5.0 |
| fastapi | 0.163.1 | uvicorn | 0.54.0 |
| a2a-sdk | 1.3.0 | sse-starlette | 3.7.0 |
| pydantic | 2.14.3 | python-dotenv | 1.2.4 |
| httpx | 0.28.1 | pytest (instalado, no ejecutado) | 9.2.0 |

La lista completa y las huellas del código exportado están en [entorno.json](entorno.json).
Los requisitos tienen rangos abiertos: esta resolución observada no promete versiones
idénticas mañana ni compatibilidad en otros sistemas operativos.

## Resultados primarios

| Comprobación | Esperado | Obtenido |
| --- | --- | --- |
| Instalar `requirements.txt` | Salida 0 | **0**, sin dependencias adicionales. |
| `pip check` | Sin incompatibilidades declaradas | **0**, `No broken requirements found.` |
| Arranque | `Application startup complete.` | **Completado**, puerto 58569. |
| `GET /salud` | 200, `{"ok":true}` | **200**, cuerpo exacto. |
| `GET /` | 200 y panel del commit | **200**, HTML idéntico por SHA-256, título `Planifica tu feria · Grupo 5`, `no-store`. |
| POST con espacios, sin clave | 401 antes de validar texto | **401**, `Falta la clave de acceso. Envíala en la cabecera X-API-Key.` |
| POST con espacios, clave incorrecta | 401 | **401**, `La clave de acceso es incorrecta.` |
| POST `{"texto":""}`, clave válida | 400 | **400**, `Escribe una pregunta para continuar.` |
| POST `{"texto":"   "}`, clave válida | 400 | **400**, mismo detalle. |

Los rechazos también usan texto de espacios para no poder iniciar una pregunta
funcional aunque hubiera una regresión de autorización. No hay dobles de aplicación
ni respuestas HTTP simuladas. El log registra **0 preguntas al coordinador y 0 envíos
A2A**. No se ejecutaron agentes ni consultas Gemini, ni se reutilizaron las suites de
168/68 como resultados nuevos. Tampoco se instalaron las dependencias opcionales de
navegador, se abrió Chrome ni se comprobó visualmente el panel.

**Hallazgos y responsables:** no se detectó una dependencia o instrucción faltante
que impida estas comprobaciones con esta resolución. No hay corrección de producción
justificada por este ensayo. Dependencias/base e integración corresponden a **Alex**;
acceso/errores a **Matías** y despliegue/operación a **Sebastián**. Ninguno de sus archivos
se modificó. La falta de validación REMOTA no se transforma en un resultado aprobado.

## Conservación, publicación y alcance

El proceso propio se cerró mediante `taskkill /PID 29636 /T /F`. La salida del proceso
**1** se debe a ese cierre deliberado **después de pasar los casos**, no a un arranque
fallido. El puerto 58569 quedó cerrado. La [revisión final](revision-final.json) conserva
el corte original de la instalación: archivos protegidos, metadatos del entorno original,
servidor previo, fuente exportada, alcance del diff e índice vacío **en aquel momento**;
no describe el índice preparado posteriormente. Las huellas privadas de `.env`
y la línea base permanecen fuera del repositorio; no se publican.

Las referencias vigentes se corrigieron: las evidencias del 14-11-2026 ya se publicaron
en **2b754e2, PR #82 ya fusionado**. Se conservaron `d8cce13` y `741305b` como bases históricas probadas,
sus fechas, conteos, intentos y registros, incluidos los cortes históricos sin commit/push.
La ejecución original de instalación terminó sin staging, fetch/merge, commit, push
ni cambios de Heroku. En la preparación posterior de este cierre se ejecutaron
`git fetch origin` y `git merge --ff-only origin/main`: **`2b754e2` → `71df3e8`**,
sin diferencias de contenido entre esos commits y conservando las 12 rutas locales.
Solo esas 12 rutas del manifiesto se preparan en el índice; **sin commit ni push**.
No se modificaron código, resultados primarios ni fechas de pruebas. No se consultó
Gemini, se repitieron pruebas ni se modificó Heroku durante esta preparación.

La [tabla REMOTA futura](../../../documento-Eduardo.md#validación-remota-futura--todavía-no-ejecutada)
queda enteramente **pendiente**, con URL y versión desplegada **por confirmar**. No se
heredan resultados LOCAL ni se asume que publicar Git equivale a desplegar Heroku.

## Evidencias útiles guardadas

| Archivo | Contenido |
| --- | --- |
| [entorno.json](entorno.json) | Fuente, referencias Git, Python/venv, comandos y versiones de todos los paquetes. |
| [instalacion.txt](instalacion.txt) | Salidas reales de creación, instalación y `pip check`; rutas personales sustituidas. |
| [resultados-http.json](resultados-http.json) | Puertos, condiciones, solicitudes sin secretos y respuestas reales por caso. |
| [servidor.txt](servidor.txt) | Arranque y seis peticiones; sin claves ni cabeceras de petición. |
| [comprobar_http.py](comprobar_http.py) | Ejecutor de estas comprobaciones, sin suites ni preguntas funcionales. |
| [revision-final.json](revision-final.json) | Conservación y límites de la comprobación final. |
| [archivos-modificados.txt](archivos-modificados.txt) | Inventario exacto de esta revisión desde la raíz; excluye la foto previa. |

No se incorporan el ZIP, la copia, el entorno virtual, `.env`, cachés ni manifiestos
privados. Los logs solo normalizan saltos de línea y anonimización de rutas; no cambian
resultados. Estas comprobaciones no son una auditoría integral de seguridad.
