# Prompts de desarrollo — Herramientas y estado

Responsable: Sebastián Mardones

> Registra aquí los prompts que usaste para desarrollar tu parte, del más antiguo al más nuevo.
> Copia el bloque de abajo una vez por prompt. Nunca pegues claves, contraseñas ni datos reales:
> si un prompt los tenía, reemplaza esa parte por `[omitido: motivo]`.

---

## 1. Arquitectura e implementación de validar_gasto, memoria del fondo y registro

- **Fecha:** 2026-10-31
- **Herramienta:** Claude (claude.ai, entorno de ejecución de Claude Code)
- **Modelo:** Claude Opus 5.5 (`claude-opus-5-5`)
- **Para qué era:** definir la arquitectura y las decisiones de mi rol, y luego implementar
  `src/herramientas.py`, `src/memoria.py` y `src/registro.py` contra la política v1.1 y el golden set v1.0.

**Prompt completo:**

````text
[adjuntos: Pauta_tarea_final.md y el resumen del proyecto del Grupo 05]
Prepara la arquitectura y las decisiones de esta tarea mi parte. Este trabajo corresponde a un
agente que está la conversación [Configurar equipo para proyecto grupal GitHub]
Considera el stack necesario. Utiliza como referencia mis trabajos del curso que están en la ruta
[D:\Certificate Agentic IA] y el MCP en Github

Hazme las consultas que consideres necesarias.
````

**Decisiones que tomé al responder las consultas del asistente:**

- RG-08 (saldo del fondo) se revisa con `memoria.revisar_saldo`, y el Núcleo lo agrega a la
  observación de `validar_gasto` en su nodo de herramientas (PR #2). La firma de `validar_gasto` no cambia.
- `registrar_veredicto` no es una herramienta del LLM. Lo llama el grafo después del juez.
- El asistente escribe el documento de arquitectura y el código; el push lo hago yo con `/subir-cambios`.

**Resultado (una línea):** reglas leídas de la política (no copiadas), 28/28 turnos deterministas
del golden set correctos (GS-23 depende del LLM por RG-02), `verificar.py` 41 ✅ 0 ❌.

---

## 2. Revisión de la arquitectura y corrección del piso de reglas

- **Fecha:** 2026-10-31
- **Herramienta:** Claude Code (app de escritorio), con el MCP de GitKraken para GitHub
- **Modelo:** Claude Opus 5.5 (`claude-opus-5-5`)
- **Para qué era:** revisar el documento de arquitectura contra el código, ver el estado de mi rama
  en GitHub y corregir las fallas encontradas.

**Prompt completo:**

````text
[adjunto: Arquitectura y decisiones — Herramientas y estado (Grupo 05).md]
Revisa esta arquitectura y la implementación, abre y ejecuta el MCP de Github y muestrame mi rama.
````

Después aprobé las correcciones ("Sí, corrígelos") y la subida ("Sí, súbelos").

**Decisiones que tomé al responder las consultas del asistente:**

- Corregir `efecto_de`: solo vale el "Efecto: …" del final del detalle. Antes, un
  `Efecto: aprobar` escrito en la categoría declarada o en la patente bajaba el piso a APROBAR.
- Corregir el parche para Matías: el usuario ve la decisión corregida por el piso, y un turno sin
  `validar_gasto` no registra nada ni reutiliza el gasto del turno anterior.
- Dejar como propuesta al grupo que el grafo cargue un gasto de confianza: hoy el piso usa el
  gasto que le pasa el LLM.

**Resultado (una línea):** `verificar.py` 41 ✅ 0 ❌ y `probar_herramientas.py` 45 ✅ 0 ❌
(2 pruebas nuevas del piso); el parche aplica limpio sobre el PR #2.
