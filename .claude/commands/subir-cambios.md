---
description: Revisa, prueba y sube los cambios de tu rama, y entrega el enlace del pull request
---

Vas a ayudar a subir los cambios de la Tarea Final a GitHub. La persona puede no saber Git:
antes de cada paso explícale en UNA frase simple qué vas a hacer y por qué. Haz los pasos
en este orden y no te saltes ninguno. Si un paso dice "detente", no sigas con los demás.

Contexto: el proyecto está en la carpeta `tarea-final-c1/` del repositorio. Lee primero
`tarea-final-c1/AGENTS.md`: ahí están la tabla de roles y ramas, y el dueño de cada archivo.
Ejecuta los comandos de Git desde la raíz del repositorio (`git rev-parse --show-toplevel`).

1. **Revisar la rama.** Corre `git branch --show-current`.
   Si la rama es `main`, detente y avisa: "Estás en main, y ahí no se trabaja. Cámbiate a tu
   rama con `git switch <tu-rama>`". Busca la rama en la tabla de AGENTS.md para saber el rol.
   Si la rama no aparece en la tabla, pregunta cuál es el rol antes de seguir.

2. **Revisar qué archivos cambiaron.** Corre `git status --short` y muéstrale la lista en
   palabras simples. Si algún archivo es `.env` (o contiene claves), o no pertenece al rol de
   esta rama según AGENTS.md (incluidos los COMPARTIDOS y las carpetas de talleres anteriores),
   detente y pregunta qué hacer con él. No lo agregues sin una respuesta clara.
   Si no hay cambios, dilo y termina.

3. **Traer lo último de main.** Corre `git fetch origin` y luego `git merge origin/main`.
   Si Git se niega porque hay cambios sin guardar en archivos que también cambiaron en main,
   o si hay conflictos, NO los resuelvas tú: explica en simple qué archivos chocan (alguien más
   cambió lo mismo) y pide ayuda a la persona. Si hubo conflictos, puedes deshacer el intento
   con `git merge --abort` solo si la persona lo aprueba.

4. **Probar.** Desde `tarea-final-c1/`, con el entorno virtual activado, corre
   `python verificar.py`. Si aparece algún ❌, detente: explica en simple qué falló y qué
   archivo hay que revisar. No subas nada hasta que pase.

5. **Guardar (commit).** Agrega SOLO los archivos del rol que revisaste en el paso 2
   (`git add <archivo> ...`; nunca `git add .` ni `git add -A`). Luego haz
   `git commit -m "<mensaje>"` con un mensaje claro en español que diga qué se hizo,
   por ejemplo: "Herramientas: validar_gasto revisa plazo y documento". Muestra el mensaje
   antes de hacer el commit.

6. **Subir (push).** Corre `git push -u origin <rama>` con el nombre de la rama actual.

7. **Pull request.** Muestra este enlace, reemplazando `<rama>` por la rama actual:
   https://github.com/aleexng1/agentic-ia-grupo-05/compare/main...<rama>
   y di: "Abre el enlace, revisa y presiona 'Create pull request'. Alex lo revisa y lo une."

Al terminar, resume en 3 líneas: qué archivos se subieron, el resultado de verificar.py y el
enlace del pull request.
