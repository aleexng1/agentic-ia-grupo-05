# datos/boletas/

Cuatro boletas **FICTICIAS** para probar el verificador A2A. Todas dicen «DOCUMENTO DE PRUEBA» y
sus emisores, RUT (11.111.111-1, 22.222.222-2, 33.333.333-3), folios y montos son inventados.

| Imagen | Caso | Qué debería decir el verificador |
|---|---|---|
| `boleta-01-cuadra.png` | todo coincide | `cuadra` = sí en los 5 campos |
| `boleta-02-monto-distinto.png` | la boleta dice $62.000; se declaró $52.000 | `monto` = no |
| `boleta-03-fecha-distinta.png` | la boleta es del 12-09-2026; se declaró 2026-10-12 | `fecha` = no |
| `boleta-04-ilegible.png` | borrosa y con ruido | todo `null` en `leido`, `cuadra` = no |

- `declarado.json`: lo declarado en cada rendición y el `cuadra` esperado.
- `generar_boletas.py`: las vuelve a generar. Necesita Pillow (`pip install Pillow`), que **no**
  está en `requirements.txt` porque el servicio no lo usa.
- **Dueño:** Alex.
