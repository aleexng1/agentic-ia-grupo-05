# Guía del rol: Caso y calidad

Responsable: Alex Nail

> Rama de trabajo: **`tf/caso-calidad`** · Reglas generales: [AGENTS.md](../../AGENTS.md)

## Tu rol en una frase

Defines el caso y los datos con que se prueba todo, mides si el agente acierta y eres quien revisa y une el trabajo de todos en `main`.

**Criterios de la pauta que aseguras:**

| Criterio | Puntaje |
|---|---|
| Caso y criterio de éxito | 0,5 |
| Golden set de 20 a 30 casos (incluye mal asignados y adversariales) | +0,5 |
| README y ficha de reproducción | (base de la entrega) |
| Revisión y unión de pull requests | (coordinación) |

## Tus archivos

Puedes modificar (rutas dentro de `tarea-final-c1/`):

- `datos/` (política ficticia y gastos de prueba)
- `pruebas/` (golden set)
- `README.md`
- `docs/` (estas guías)

**No toques** los archivos de otros roles. Si necesitas un cambio en ellos, escribe la propuesta
y avísale a la persona dueña. Los archivos **compartidos** (`src/contrato.py`, `AGENTS.md`,
`requirements.txt`, `.env.example`, `verificar.py`) solo se cambian con acuerdo del grupo.

## Qué entregas y cómo sabes que terminaste

- [ ] **Caso y criterio de éxito** escritos en `README.md` (y sección 1 del notebook): qué problema
      resuelve, para quién, y una meta medible (ej. "≥ 85 % de decisiones correctas en el golden set").
- [ ] **Política ficticia completa** en `datos/politica_ficticia.md`, de **8 a 10 políticas**, cada
      una con `## P01 — <nombre>`, descripción y tabla Grupo / Categoría / Cuenta. Con "trampas":
  - [ ] la misma categoría en varias políticas (ej. "Peajes" en P01, P02, P03 y P06);
  - [ ] excepciones de documento (ej. voucher solo en taxi, apps de transporte y bus, RG-01);
  - [ ] una política que acepta **solo facturas**;
  - [ ] el arriendo de auto que se **reclasifica a Vehículos Propios**;
  - [ ] una política **exclusiva de una unidad de negocio**.
- [ ] Quitar el encabezado "BORRADOR" cuando esté lista.
- [ ] **Golden set** en `pruebas/golden_set.json` con **20 a 30 casos**: normales, políticas mal
      asignadas (deben dar `observar`), incumplimientos (`rechazar`) y **adversariales** (jailbreak
      en la glosa, pedidos fuera de alcance). Sube `version` (ej. `"1.0"`).
- [ ] `datos/rendiciones_prueba.csv` coherente con la política final.
- [ ] Sección 10 del notebook: ejecutar el golden set y mostrar esperado vs obtenido por caso.
- [ ] **Ficha de reproducción** del README completa (incluida la instancia de Redis confirmada).
- [ ] `python verificar.py` pasa.
- [ ] Revisar y unir los pull requests de los demás (ver abajo).

Recuerda: `tipo_documento` solo puede ser `boleta`, `factura` o `voucher` (lo exige el contrato).
Los casos de "documento no permitido" se arman con políticas que exigen un tipo específico.

**Política vigente: v1.2** (`datos/politica_ficticia.md`). Lo que más cambia las decisiones:

- **Plazo (RG-03):** se rinde en el mismo mes o hasta el **día 10 del mes siguiente**. Fuera de plazo
  se rechaza; con visto bueno del Gerente General (`vb_gerente_general`) queda observado.
- **Campos obligatorios (RG-10):** **patente** en P04 y P05 (en P05, un código de la tabla de
  equipos) y **número de OT** en P06. Si falta o no es válido, queda observado. Si la fecha de
  rendición es anterior a la fecha del gasto, los datos son inconsistentes y el gasto queda
  observado hasta que se corrijan.
- **Topes (RG-05):** son **por documento** y distintos por categoría (P02, P03 y P08). Si se
  superan, queda observado.
- **Documentos (RG-01):** boleta o factura; voucher solo en taxi, apps de transporte y bus
  interurbano (puede venir como "Otros"); P07 solo factura. Un documento no válido se rechaza.

## De quién dependes y quién depende de ti

- **Dependen de ti, y pronto:** Herramientas y estado (lee las reglas exactas de tu política),
  Conocimiento y seguridad (indexa tu política en Redis) y Núcleo (usa tus casos en el notebook).
  **Entrega primero la política**, aunque el golden set venga después.
- **Dependes de:** todos, para correr el golden set completo al final.

## Cómo revisar y unir un pull request

1. Abre el PR en GitHub y mira la pestaña **Files changed**: solo deben aparecer archivos del rol.
2. Confirma que no hay `.env`, claves ni datos reales.
3. Si todo está bien, presiona **Merge pull request**. Después avisa al grupo para que cada uno
   traiga lo nuevo (su `/subir-cambios` lo hace solo).

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
git switch tf/caso-calidad
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
git switch tf/caso-calidad
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
Lee AGENTS.md y docs/instrucciones/caso-calidad.md. Soy del rol Caso y calidad, en la rama
tf/caso-calidad. Quiero completar datos/politica_ficticia.md con 8 a 10 políticas
FICTICIAS de Comercial Los Alerces SpA, manteniendo el formato actual (## P01 — <nombre>,
descripción y tabla Grupo / Categoría / Cuenta con cuentas CTA-XXXX) y las reglas generales.
Incluye las trampas de la guía. Primero muéstrame una propuesta de la lista de políticas y
trampas, y espera mi visto bueno antes de escribir. No toques archivos fuera de mi rol.
Al final corre python verificar.py y explícame el resultado en simple.
```
