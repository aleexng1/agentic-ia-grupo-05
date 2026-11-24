# web/

Chat web. `index.html` es una copia del panel de `taller-02-c2` (pide la clave y la manda en `X-API-Key`).
`api/app.py` lo sirve en `GET /`.

- **Dueño:** Eduardo.
- **Falta:** adaptarlo al caso: hoy llama a `/panel/consultar` con `context_id` y muestra textos del planificador de ferias; debe llamar a `POST /chat` con `{thread_id, texto, imagen?}`, permitir adjuntar la boleta (base64 + `mime_type`) y mostrar `ruta`, `estado_final` e `id_ejecucion`.
