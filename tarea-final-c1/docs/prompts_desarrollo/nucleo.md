# Prompts de desarrollo — Núcleo (ReAct)

Responsable: Matías Muñoz

> Registro de los prompts relevantes usados para preparar el trabajo del rol Núcleo.
> No se incluyen claves, contraseñas ni datos privados.

---

## 1. Sincronizar y proponer la siguiente tarea

- **Fecha:** 2026-10-31
- **Herramienta:** OpenCode
- **Modelo:** GPT-6 Luna Fast
- **Para qué era:** Sincronizar la rama de Matías con GitHub, revisar los cambios del proyecto y proponer el siguiente trabajo sin programar todavía.

**Prompt completo:**

````text
Necesito ponerme al día con los últimos cambios del proyecto grupal y preparar mi
siguiente tarea. No tengo mucha experiencia con Git: haz un paso a la vez, explícame cada
comando en una frase y en simple, y detente cuando necesites una decisión mía.
NO programes nada en este prompt: solo sincroniza, revisa y propón.

Proyecto: repositorio agentic-ia-grupo-05, carpeta tarea-final-c1.
Roles y ramas:
- Alex Nail → Caso y calidad → tf/caso-calidad
- Matías Muñoz → Núcleo → tf/nucleo
- Sebastián Mardones → Herramientas y estado → tf/herramientas
- Eduardo Basaure → Conocimiento y seguridad → tf/conocimiento-seguridad

PASO 1 — Sincronizar
1. Pregúntame mi nombre para saber mi rol y mi rama.
2. Entra a la carpeta del repo y muestra git status. Si tengo cambios sin guardar, NO los
   borres: dime cuáles son y pregúntame si los guardo con un commit en mi rama.
3. git fetch origin, cámbiate a mi rama (git switch <rama>), git pull y luego
   git merge origin/main. Si hay un conflicto, NO lo resuelvas: explícame qué archivos
   chocan y espera.
4. Si requirements.txt cambió, reinstala con el Python del entorno .venv.
5. Corre verificar.py desde tarea-final-c1 con el Python del entorno y explícame el
   resultado.

PASO 2 — Qué cambió para mí
1. Lee AGENTS.md, mi guía en docs/instrucciones/ y datos/politica_ficticia.md (v1.1).
2. Explícame en máximo 10 líneas qué cambió en la política v1.1 que afecte mi parte.
3. Muéstrame los avisos de MI rol (de esta lista, solo el mío):

   Herramientas y estado (Sebastián):
   - validar_gasto debe aplicar la v1.1: topes por documento y por categoría, RG-10,
     voucher solo en taxi/apps/bus, RG-03 con visto bueno → observar, RG-07, y la multa
     de P04 → observar.
   - fondo_inicial hoy devuelve siempre $200.000; debe leer datos/fondos_ficticios.json
     sin cambiar su firma.

   Conocimiento y seguridad (Eduardo):
   - PROMPT_SISTEMA está desactualizado: varias reglas observan en vez de rechazar
     (RG-03 con visto bueno, RG-05, RG-07, RG-08, RG-09, RG-10, multa de P04), y el
     motivo debe citar los códigos de regla (RG-xx o Pxx).
   - Volver a indexar la política v1.1, excluyendo la sección "Historial de cambios".
   - El caso GS-33 espera que el agente use buscar_politica.

   Núcleo (Matías):
   - Los turnos de un mismo caso del golden set van en el mismo hilo de conversación, y el
     fondo del caso (contexto.fondo) se carga antes del primer turno.
   - El golden set espera la política como código (P02); hoy el Veredicto usa el nombre.
     Está en discusión usar el código en todo el proyecto.

PASO 3 — Mis casos del golden set
1. Lee pruebas/README.md y pruebas/golden_set.json.
2. Lista los casos cuyo campo "componentes" incluye mi parte (nucleo, herramientas, memoria,
   rag o seguridad, según mi rol), con una línea cada uno: id, qué prueba y la respuesta
   esperada.
3. Explícame cuáles de esos casos dependen solo de mi trabajo y cuáles necesitan también
   el de otro compañero.

PASO 4 — Registro de prompts
1. Revisa si existe docs/prompts_desarrollo/<mi-rol>.md. Si no existe, créalo a partir de
   docs/prompts_desarrollo/_plantilla.md.
2. Pregúntame si ya usé prompts de desarrollo para mi parte. Si me acuerdo de alguno,
   ayúdame a anotarlo con la plantilla.
3. Desde ahora, cada vez que te dé un prompt importante para mi parte, recuérdame
   anotarlo ahí.

PASO 5 — Plan de mi siguiente tarea
Propón un plan corto (3 a 6 pasos) para mi próxima tarea, considerando los avisos de mi
rol y mis casos del golden set. Para cada paso indica qué archivos tocaría (solo los míos,
según AGENTS.md) y cómo sabré que está listo. Espera mi visto bueno antes de programar.

PASO 6 — Cierre
1. Si creé o cambié mi archivo de prompts, súbelo con /subir-cambios (o sigue sus pasos
   si el comando no está disponible).
2. Recuérdame cerrar y volver a abrir OpenCode (o Claude Code) dentro de tarea-final-c1,
   para que cargue la versión nueva de AGENTS.md.
````

**Resultado (una línea):** Rama `tf/nucleo` sincronizada, entorno preparado y casos del golden set revisados; el plan de implementación queda a la espera del visto bueno de Matías.

---

## 2. Preparar el entorno según el material del curso

- **Fecha:** 2026-10-31
- **Herramienta:** OpenCode
- **Modelo:** GPT-6 Luna Fast
- **Para qué era:** Preparar el entorno del proyecto siguiendo las prácticas de clase y usando el material del curso como referencia.

**Prompt completo:**

````text
acá tienes todo lo necesario para poder setear el entrono al igual como lo hemos venido haciendo en la clases con todas las buenas practicas entorno virutal, dependencias, librerias, vesiones de python, .env, .env example, estructura del proyecto, ejecución centralizada, flags, etc. Siempre consultame si lo necesitas.
esto es lo que necesitas cierto?
````

**Resultado (una línea):** Se creó `.venv` con Python 3.12.10, se instalaron las versiones de `requirements.txt`, se copió `.env.example` y `verificar.py` terminó con 41 ✅ y 0 ❌.

---

## 3. Demostrar saludo e historial en el notebook

- **Fecha:** 2026-10-31
- **Herramienta:** OpenCode
- **Modelo:** GPT-6 Luna Fast
- **Para qué era:** Aprobar e iniciar la primera tarea de Núcleo: demostrar que GS-31 responde un saludo sin herramientas y que GS-32 recuerda datos entre dos turnos del mismo hilo.

**Prompt completo:**

````text
me parece bien que avancemos con la primera tarea. apruebo el plan. Entiendo que para el resto mis compañeros tienen que desarrollar su parte para poder probar? esty bien.
no he usado otros prompts
````

**Resultado (una línea):** Se completó la celda de historial de `agente.ipynb`; GS-31 y los dos turnos de GS-32 pasaron con Gemini real sin llamadas a herramientas, y el segundo turno recordó a Pedro y su unidad; `verificar.py` pasó (41 ✅, 0 ❌).

---

## Estado de prompts de implementación

La primera tarea de Núcleo modificó solo la demostración de historial en `agente.ipynb`; aún no se ha cambiado `src/grafo.py` ni `src/config.py`. Los próximos prompts importantes se agregarán aquí junto con su resultado. Nunca se registrará el contenido de `.env` ni una clave.
