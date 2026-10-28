# Guía del rol: Herramientas y estado

Responsable: Sebastián Mardones

> Rama de trabajo: **`tf/herramientas`** · Reglas generales: [AGENTS.md](../../AGENTS.md)

## Tu rol en una frase

Construyes las piezas que aplican reglas exactas y recuerdan cosas: la validación del gasto, el saldo del fondo por rendir y el registro de veredictos.

**Criterios de la pauta que aseguras:**

| Criterio | Puntaje |
|---|---|
| `validar_gasto` con reglas exactas leídas de la política | (base del ReAct) |
| Memoria del fondo por rendir que se actualiza y se usa en una decisión posterior | +1,0 |
| Registro de veredictos en SQLite con estado antes/después y reinicio seguro | +0,5 |

## Tus archivos

Puedes modificar (rutas dentro de `tarea-final-c1/`):

- `src/herramientas.py` (`validar_gasto`)
- `src/memoria.py` (fondo por rendir)
- `src/registro.py` (registro en SQLite)

**No toques** los archivos de otros roles. Si necesitas un cambio en ellos, escribe la propuesta
y avísale a la persona dueña. Los archivos **compartidos** (`src/contrato.py`, `AGENTS.md`,
`requirements.txt`, `.env.example`, `verificar.py`) solo se cambian con acuerdo del grupo.

## Qué entregas y cómo sabes que terminaste

- [ ] `validar_gasto(gasto, politica, categoria)` revisa con **reglas exactas** (código, no LLM):
  - [ ] tipo de documento permitido (incluidas excepciones y la política solo con facturas);
  - [ ] plazo de rendición (días entre `fecha_gasto` y `fecha_rendicion`);
  - [ ] campos obligatorios (patente en Vehículos Propios);
  - [ ] exclusividad de unidad de negocio;
  - [ ] devuelve la `cuenta` correcta según la tabla de la política.
  Las reglas y cuentas se **leen** de `datos/politica_ficticia.md` (no se copian a mano en el código).
- [ ] Cada incumplimiento dice qué `regla` falló y un `detalle` entendible.
- [ ] **Memoria del fondo**: `fondo_inicial` entrega un fondo ficticio; `aplicar_veredicto` descuenta
      el monto si se aprueba y anota el id (sin modificar el fondo recibido); `resumen_fondo` lo
      describe. Demostrar en el notebook (sección 7) que un gasto posterior se decide distinto por
      el saldo (ej. se rechaza o se observa porque ya no alcanza).
- [ ] **Registro SQLite** (`registro_veredictos.db`, Git lo ignora): `registrar_veredicto` guarda y
      devuelve `antes`/`despues`; `reiniciar_registro` deja la base vacía sin borrar nada más.
      Mostrarlo en la sección 8 del notebook.
- [ ] `python verificar.py` pasa.

## De quién dependes y quién depende de ti

- **Dependes de:** Caso y calidad (la política final con sus reglas). Mientras tanto usa el
  borrador de `datos/politica_ficticia.md`: el formato de las tablas no cambia.
- **Dependen de ti:** Núcleo (el agente llama a `validar_gasto` y usa la memoria y el registro) y
  Caso y calidad (el golden set mide tus reglas).

## Puesta en marcha paso a paso

Haz esto una sola vez. Copia y pega cada línea en la terminal y espera a que termine.
Necesitas tener instalados **Git** y **Python 3.12**.

### Windows (PowerShell)

```powershell
# 1. Descargar el repositorio y entrar a él (solo la primera vez)
git clone https://github.com/aleexng1/agentic-ia-grupo-05.git
cd agentic-ia-grupo-05
#    Si YA lo tenías clonado: no lo clones de nuevo. Entra a su carpeta con cd y corre:
#    git fetch origin

# 2. Cambiarte a tu rama de trabajo y entrar a la carpeta del proyecto
#    (la carpeta tarea-final-c1 aparece al estar en tu rama)
git switch tf/herramientas
cd tarea-final-c1

# 3. Crear el entorno virtual con Python 3.12 y activarlo
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
#    Si sale un error de "ejecución de scripts deshabilitada", corre esto una vez y repite:
#    Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

# 4. Instalar las librerías (versiones fijas)
python -m pip install -r requirements.txt

# 5. Crear tu archivo de configuración y completarlo (clave y valores del README)
Copy-Item .env.example .env
notepad .env

# 6. Comprobar que todo funciona: debe terminar con "Todo en orden"
python verificar.py
```

### Linux

```bash
# 1. Descargar el repositorio y entrar a él (solo la primera vez)
git clone https://github.com/aleexng1/agentic-ia-grupo-05.git
cd agentic-ia-grupo-05
#    Si YA lo tenías clonado: no lo clones de nuevo. Entra a su carpeta con cd y corre:
#    git fetch origin

# 2. Cambiarte a tu rama de trabajo y entrar a la carpeta del proyecto
#    (la carpeta tarea-final-c1 aparece al estar en tu rama)
git switch tf/herramientas
cd tarea-final-c1

# 3. Crear el entorno virtual con Python 3.12 y activarlo
python3.12 -m venv .venv
source .venv/bin/activate

# 4. Instalar las librerías (versiones fijas)
python -m pip install -r requirements.txt

# 5. Crear tu archivo de configuración y completarlo (clave y valores del README)
cp .env.example .env
nano .env

# 6. Comprobar que todo funciona: debe terminar con "Todo en orden"
python verificar.py
```

**Cada vez que vuelvas a trabajar:** abre la terminal en `tarea-final-c1`, activa el entorno
(paso 3, solo la línea de activar), revisa que estás en tu rama con `git branch --show-current`
y abre OpenCode (o Claude Code) **dentro de la carpeta `tarea-final-c1`**.

**Para guardar y subir tu avance:** escribe `/subir-cambios` en OpenCode. Hace todo en orden y al
final te da el enlace del pull request.

## Tu primer prompt para OpenCode

Abre OpenCode dentro de `tarea-final-c1`, en tu rama, y pega esto:

```text
Lee AGENTS.md y docs/instrucciones/herramientas.md. Soy del rol Herramientas y estado, en la
rama tf/herramientas. Quiero reemplazar el stub de validar_gasto en src/herramientas.py por
reglas exactas leídas de datos/politica_ficticia.md (documento permitido, plazo, patente,
exclusividad de unidad) y que devuelva la cuenta según la tabla. Primero explícame en simple
cómo leerías las reglas y las tablas del archivo, y espera mi visto bueno. No cambies la firma
ni los tipos de src/contrato.py. Solo toca mis archivos. Al final corre python verificar.py.
```
