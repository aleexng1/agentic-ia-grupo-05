# Reglas para programar con agentes (Claude Code, OpenCode u otro)

**Antes de trabajar, lee `docs/pauta.md`, `docs/reparto.md` (tu sección) y `docs/contratos.md`.**

Estas reglas valen para cualquier persona del grupo y para el asistente que use.

1. **No salir de `tarea-final-c2/`.** No crear, cambiar ni borrar nada fuera de esta carpeta.
   En especial, no tocar el `Procfile`, el `requirements.txt` ni el `.slugignore` de la raíz:
   el taller 02 depende de ellos.
2. **Respetar `docs/contratos.md`.** Nombres de herramientas, firmas, formato de `/chat`, encargo y
   respuesta A2A, columnas de `ejecuciones` y estados finales salen de ahí. Si hace falta
   cambiar un contrato, se cambia primero ese archivo, en el mismo PR, y se avisa al grupo.
3. **Trabajar solo en lo tuyo.** Mira `docs/reparto.md` y confirma tu rama con
   `git branch --show-current` antes de empezar. Un archivo de otra persona se toca solo si ella
   está de acuerdo.
4. **Nunca subir claves.** El `.env` no se lee, no se muestra y no se sube. Las variables nuevas
   van a `.env.example` con un valor ficticio y un comentario de para qué sirven.
5. **Sin respuestas inventadas.** Si algo no está implementado, queda `raise NotImplementedError`
   con un mensaje claro. Si una herramienta o el A2A fallan, el agente lo dice; no rellena datos.
6. **Todo es ficticio.** "Comercial Los Alerces SpA", personas, RUT, montos y boletas son inventados.
7. **`git add` solo de rutas de esta carpeta.** Nunca `git add .` ni `git add -A` (en el repo hay
   carpetas sin seguimiento que no se suben).
8. **Antes de un PR:** `python -m pytest` desde `tarea-final-c2/` con el `.venv` activado, y que pase.
9. **Código copiado de talleres anteriores:** se ajustan imports y rutas, no se reescribe sin acuerdo.
   El origen de cada archivo está en su docstring y en el README de su carpeta.
