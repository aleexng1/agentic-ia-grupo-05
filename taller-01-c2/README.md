# Taller 1 · Curso 2 · Grupo 5 — "Tu skill es un agente y habla por A2A"

Tema común: **planificador de ferias y eventos**. Cada integrante hace un agente con
una habilidad y todos se conectan por A2A a un coordinador.

La entrega es **un solo zip**: `grupo-5-taller-a2a.zip`.

## Quién hace qué

| Integrante | Rol | Puerto | Rama | Carpeta del agente |
|------------|-----|--------|------|--------------------|
| Alex Nail | Lugares y capacidad | 8004 | `c2t1/alex-lugares` | `src/agente_alex/` |
| Matias Muñoz | Programa y horarios | 8003 | `c2t1/matias-programa` | `src/agente_matias/` |
| Eduardo Basaure | Presupuesto y costos | 8005 | `c2t1/eduardo-presupuesto` | `src/agente_eduardo/` |
| Sebastian Mardones | Comida y catering | 8006 | `c2t1/sebastian-catering` | `src/agente_sebastian/` |

## Qué toca cada uno

Cada uno cambia **solo** lo suyo (cambia `NOMBRE` por el tuyo):

- `proyecto/src/agente_NOMBRE/`
- sus pruebas en `proyecto/tests/`
- `blueprint-NOMBRE.md`
- `documento-NOMBRE.md`
- `evidencias/NOMBRE/`
- su sección en `compañeros.md`

**Archivos compartidos:** `proyecto/main.py`, `proyecto/.env.example`,
`proyecto/requirements*.txt`, `proyecto/README.md`, `proyecto/src/comun/`,
`proyecto/src/coordinador/` y `proyecto/scripts/`. Estos los cambia Alex. Si
necesitas cambiar alguno, dilo en la descripción de tu pull request.

> **Nunca subas el `.env`**: lleva tu clave de Gemini. Tampoco `.venv`,
> `__pycache__` ni `.pytest_cache`.

## Cómo subir tu avance (Windows PowerShell)

```powershell
git clone https://github.com/aleexng1/agentic-ia-grupo-05.git   # solo la primera vez
cd agentic-ia-grupo-05
git fetch
git switch c2t1/NOMBRE-ROL
# (copia tus archivos dentro de taller-01-c2/)
git status
git add taller-01-c2
git commit -m "c2t1: agente de NOMBRE"
git push
```

Qué hace cada comando:

- `git clone ...`: descarga el repo a tu computador (solo la primera vez).
- `cd agentic-ia-grupo-05`: entra a la carpeta del repo.
- `git fetch`: trae de GitHub las ramas nuevas, sin cambiar tus archivos.
- `git switch c2t1/NOMBRE-ROL`: te cambia a tu rama (por ejemplo `c2t1/matias-programa`).
- `git status`: muestra qué archivos cambiaste. Revisa que **no** aparezca `.env` ni `.venv`.
- `git add taller-01-c2`: prepara para subir solo lo que está en esta carpeta.
- `git commit -m "..."`: guarda tus cambios con un mensaje.
- `git push`: sube tu rama a GitHub.

Después, en GitHub, aparece el botón **"Compare & pull request"**. Ábrelo, revisa
que la base sea **`main`**, escribe una descripción corta y crea el pull request.
