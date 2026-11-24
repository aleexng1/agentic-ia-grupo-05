# src/comun/

Piezas compartidas por el principal y el verificador.

| Archivo | Origen | Dueño | Estado |
|---|---|---|---|
| `contrato.py` | `tarea-final-c1/src/contrato.py` + campo opcional `cargo`; `MAX_PASOS` viene de `config` | compartido | listo |
| `config.py` | `config.py` de taller-02-c2 y de c1 + variables nuevas | compartido | listo |
| `modelos.py` | `obtener_llm` de c1 (`MODELO_PRINCIPAL`) | Sebastián | falta `obtener_llm_con_respaldo` |
| `seguridad.py` | taller-02-c2 (`CLAVE_API` → `API_KEY_SERVICIO`) | Matías | falta `exigir_accion_permitida` y `revisar_token_a2a` |
| `registro.py` | logging de taller-02-c2 | Sebastián | falta la tabla `ejecuciones` (Postgres) |
| `errores.py` | taller-02-c2 | compartido | listo |
| `servidor.py`, `executor.py`, `tarjeta.py` | taller-02-c2 (sin el panel antiguo) | Alex | listo; `executor` acepta `responder_partes` (FilePart/DataPart) y `tarjeta` los modos de entrada/salida |
| `cliente_a2a.py` | `taller-02-c2/.../coordinador/cliente.py` | Alex | listo; `enviar_partes` (cliente propio por llamada, con tiempo límite y cabeceras) |
