# Recorrido 03-revisar-gasto: ruta esperada `revisar_gasto`

Capturado el 2026-11-26T21:34:55-03:00 contra `http://127.0.0.1:8000` con `evidencias/dos-recorridos/capturar.py`.

**id_ejecucion:** `a078d302-b429-4448-9774-cdaafe74343d`

## Entrada
```bash
curl -s -X POST http://127.0.0.1:8000/chat -H 'Content-Type: application/json' -H 'X-API-Key: ***' \
  -d '{"thread_id": "evidencia-03-revisar-gasto-20261126T213442", "texto": "Revisa este gasto rendido.", "gasto": {"id": "G-0101", "fecha_gasto": "2026-10-06", "fecha_rendicion": "2026-10-09", "monto": 7800, "tipo_documento": "boleta", "proveedor": "Concesionaria Vial Lago Verde", "glosa": "peaje ida y vuelta CD - tienda Norte, camión de reparto", "politica_declarada": "Viajes Internos", "categoria_declarada": "Peaje", "unidad_negocio": "CD", "patente": "RZPT41", "numero_ot": null, "vb_gerente_general": false, "id_fondo": "FR-001"}}'
```

Respuesta inmediata (HTTP 202, `/chat` asíncrono):
```json
{
  "id_ejecucion": "a078d302-b429-4448-9774-cdaafe74343d",
  "estado": "en_proceso",
  "consultar": "/registro/a078d302-b429-4448-9774-cdaafe74343d",
  "thread_id": "evidencia-03-revisar-gasto-20261126T213442"
}
```

## Ejecución observada (log del servidor con este id_ejecucion)
```text
2026-11-26 21:34:42 INFO    [tarea_final] chat · a078d302-b429-4448-9774-cdaafe74343d · aceptado en segundo plano (tope 90 s)
2026-11-26 21:34:54 INFO    [tarea_final] ejecución a078d302-b429-4448-9774-cdaafe74343d · ruta=revisar_gasto · estado=ok · 11395 ms · a2a=False · herramientas=buscar_politica,consultar_fondo,validar_gasto,emitir_veredicto
2026-11-26 21:34:54 INFO    [tarea_final] chat · a078d302-b429-4448-9774-cdaafe74343d · «Revisa este gasto rendido.» → revisar_gasto
(más 12 consultas GET /registro/a078d302-b429-4448-9774-cdaafe74343d → 200 mientras corría; omitidas)
```

## Paso a paso del ReAct (traza de esta ejecución)

`id_ejecucion = a078d302-b429-4448-9774-cdaafe74343d`. Con `MOSTRAR_TRAZAS=1` el ReAct imprime cada paso (`registrar_traza`) sin el id; aquí van las líneas del log entre «chat · <id> · aceptado» y «ejecución <id> · ruta=…», sin otra ejecución en medio. **Calza con el registro:** 4 pasos y herramientas `buscar_politica`, `consultar_fondo`, `validar_gasto`, `emitir_veredicto`.

### Paso 1

- **Pide** `buscar_politica` con:
  ```json
  {
    "consulta": "peajes camion de reparto P02 P03 P04",
    "k": 3
  }
  ```
- **Devuelve** `buscar_politica`: [{"politica": "Flota de Camiones y Camionetas", "texto": "## Reglas generales\n\nEstas reglas aplican a todas las políticas, además de las reglas propias de cada una.\n\n**RG-01 — Documentos válidos.** Solo se aceptan **boleta** o **factura**. Se acepta **voucher** únicamente en taxi, aplicaciones de transporte (tipo Uber) y bus interurbano. Un voucher de cualquier otro tipo de comercio no es válido. En algunos sistemas el voucher aparece como tipo de documento **\"Otros\"**; se trata igual que un voucher. Un gasto con un documento no válido (según esta regla o según los documentos que exige cada política) se **rechaza**.\n\n**RG-02 — Solo gastos laborales.** Se prohíbe rendir gastos person… (12878 caracteres en total)
- **Decide después:** paso 2, pide `consultar_fondo`.

### Paso 2

- **Pide** `consultar_fondo` con:
  ```json
  {
    "id_fondo": "FR-001"
  }
  ```
- **Devuelve** `consultar_fondo`: {"id_fondo": "FR-001", "responsable": "Jefatura de Administración (ficticia)", "saldo_inicial": 200000, "saldo_actual": 200000, "gastos_aprobados": []}
- **Decide después:** paso 3, pide `validar_gasto`.

### Paso 3

- **Pide** `validar_gasto` con:
  ```json
  {
    "gasto": {
      "glosa": "peaje ida y vuelta CD - tienda Norte, camión de reparto",
      "unidad_negocio": "CD",
      "vb_gerente_general": false,
      "patente": "RZPT41",
      "id_fondo": "FR-001",
      "cargo": "Chofer Camión",
      "id": "G-0101",
      "fecha_rendicion": "2026-10-09",
      "proveedor": "Concesionaria Vial Lago Verde",
      "categoria_declarada": "Peaje",
      "fecha_gasto": "2026-10-06",
      "politica_declarada": "Viajes Internos",
      "monto": 7800,
      "numero_ot": null,
      "tipo_documento": "boleta"
    },
    "politica": "P02",
    "categoria": "Peaje"
  }
  ```
- **Control del grafo** `[campos_alterados]`: {"gasto": "G-0101", "campos": ["cargo"]}
- **Control del grafo** `[gasto_original_restaurado]`: {"gasto": "G-0101", "motivo": "se ignoraron cambios propuestos por el LLM"}
- **Devuelve** `validar_gasto`: {"cumple": true, "incumplimientos": [], "cuenta": "CTA-6100"}
- **Decide después:** paso 4, pide `emitir_veredicto`.

### Paso 4

- **Pide** `emitir_veredicto` con:
  ```json
  {
    "politica": "P02",
    "decision": "aprobar",
    "cuenta": "CTA-6100",
    "categoria": "Peaje",
    "motivo": "El gasto cumple con todas las normativas aplicables: documento válido (boleta), plazo correcto de rendición (RG-03), monto dentro del saldo disponible del fondo (RG-08), y la clasificación en P02 (Viajes Internos), categoría Peaje, es correcta para un viaje entre sedes de la empresa (CD - tienda Norte)."
  }
  ```
- **Devuelve** `emitir_veredicto`: el veredicto estructurado. El grafo lo valida y, como es válido, no vuelve al modelo; por eso esta observación no sale en la traza (el ReAct imprime cada observación al empezar la vuelta siguiente).
- **Decide después:** nada más: emitió el veredicto (**APROBAR** / P02 / Peaje / CTA-6100) → **parada por veredicto válido**; el grafo pasa al cierre.

### Cierre (grafo, sin el modelo del ReAct)

- **Juez** `[juez]`: {"valido": true, "razon": "El veredicto está justificado. El gasto cumple con las normas de P02 para un viaje de trabajo entre sedes (CD a tienda Norte), documento boleta válido (RG-01), plazo correcto (RG-03), y clasificación adecuada en P02 / Peaje / CTA-6100.", "evaluado": true, "uso_respaldo": false}
- **Fondo por rendir** `[fondo]`: {"antes": "Fondo FR-001 (Jefatura de Administración (ficticia)): saldo disponible $200.000 de $200.000 CLP; 0 gasto(s) aprobado(s).", "despues": "Fondo FR-001 (Jefatura de Administración (ficticia)): saldo disponible $192.200 de $200.000 CLP; 1 gasto(s) aprobado(s) (G-0101)."}
- **Registro de veredictos** `[registro]`: {"antes": {"registros": 0, "por_decision": {}, "gasto": null}, "despues": {"registros": 1, "por_decision": {"aprobar": 1}, "gasto": {"id_gasto": "G-0101", "id_fondo": "FR-001", "monto": 7800, "decision": "aprobar", "motivo": "El gasto cumple con todas las normativas aplicables: documento válido (boleta), plazo correcto de rendición (RG-03), monto dentro del saldo disponible del fondo (RG-08), y la clasificación en P02 (Viajes Internos), categoría Peaje, es correcta para un viaje entre sedes de… (748 caracteres en total)

## Condición de parada

El ciclo ReAct de `revisar_gasto` termina por una condición explícita. Las dos que pide la pauta:

1. **Por veredicto válido (la de esta corrida).** En el paso 4 el modelo pidió `emitir_veredicto`; el grafo valida el veredicto, no vuelve al modelo y pasa al cierre (juez, fondo y registro), con `estado_final = "ok"`.
2. **Por máximo de pasos (`MAX_PASOS_REACT`: 6 en esta corrida, que cerró en 4 pasos).** En `src/principal/flujos/revisar_gasto.py`, `elegir_siguiente` manda al nodo `parada` cuando `pasos >= MAX_PASOS` (línea 759), y `nodo_parada` (línea 739) responde «Me detuve: alcancé el máximo de N pasos…», sin veredicto y sin registrar, con `estado_final = "error"`. Lo prueba:
   ```bash
   python -m pytest -q "tests/test_react_mcp.py::test_se_detiene_por_max_pasos_con_estado_error"
   ```
   (un modelo que nunca emite veredicto, `MAX_PASOS=2` → 2 pasos, 2 llamadas al modelo, `error`, sin veredicto y sin escribir en el registro). La corrida real con `MAX_PASOS_REACT=2` está en `evidencias/react/02-parada-max-pasos-gs01.txt`.

<details><summary>Traza completa (los bloques tal como salen en el log)</summary>

```text
── [llm] ──
{
  "paso": 1,
  "pide_herramientas": [
    {
      "name": "buscar_politica",
      "args": {
        "consulta": "peajes camion de reparto P02 P03 P04",
        "k": 3
      },
      "id": "call_17093935341889234819",
      "type": "tool_call"
    }
  ],
  "texto": ""
}
── [observacion] ──
{
  "herramienta": "buscar_politica",
  "resultado": "[{\"politica\": \"Flota de Camiones y Camionetas\", \"texto\": \"## Reglas generales\\n\\nEstas reglas aplican a todas las políticas, además de las reglas propias de cada una.\\n\\n**RG-01 — Documentos válidos.** Solo se aceptan **boleta** o **factura**. Se acepta **voucher** únicamente en taxi, aplicaciones de transporte (tipo Uber) y bus interurbano. Un voucher de cualquier otro tipo de comercio no es válido. En algunos sistemas el voucher aparece como tipo de documento **\\\"Otros\\\"**; se trata igual que un voucher. Un gasto con un documento no válido (según esta regla o según los documentos que exige cada política) se **rechaza**.\\n\\n**RG-02 — Solo gastos laborales.** Se prohíbe rendir gastos personales: compras para uso propio, alcohol, regalos personales, multas de tránsito de vehículos personales o de arriendo, propinas sobre el 10%, la alimentación individual en el lugar de trabajo, sin viaje ni reunión. Un gasto personal se **rechaza**.\\n\\n**RG-03 — Plazo de rendición.** El gasto se rinde en el mismo mes en que se hizo o, como máximo, hasta el **día 10 del mes siguiente**. Fuera de ese plazo el gasto se **rechaza**, salvo que el informe incluya el visto bueno escrito del Gerente General; en ese caso queda **observado** para revisión.\\n\\n**RG-04 — Segregación de funciones.** Quien hizo el gasto nunca puede aprobar su propia rendición.\\n\\n**RG-05 — Topes.** Algunas categorías tienen un monto máximo **por documento**. Si el monto por documento supera el tope, el gasto queda **observado** y el colaborador debe justificar el exceso.\\n\\n**RG-06 — Reclasificación de arriendo de autos livianos.** Si se arrienda un auto liviano (sedán, hatchback, station wagon o similar), el arriendo y **todos sus gastos asociados** (combustible, peajes, estacionamiento, transbordador) se rinden en la política **P01 Vehículos Propios**, aunque el viaje sea de trabajo. El arriendo de camionetas o furgones sí va en P02 o P03 según el viaje.\\n\\n**RG-07 — Exclusividad de unidad.** Algunas políticas solo pueden ser usadas por una unidad de negocio. Si otra unidad la usa, el gasto se **observa** para reclasificarlo.\\n\\n**RG-08 — Fondos por rendir.** Un gasto pagado con un fondo por rendir no puede superar el saldo disponible del fondo. Si lo supera, queda **observado**.\\n\\n**RG-09 — Gasto mal clasificado.** Si el gasto es válido pero el colaborador eligió una política o categoría incorrecta, queda **observado** con la política, categoría y cuenta correctas sugeridas.\\n\\n**RG-10 — Campos obligatorios.** Si falta un campo obligatorio de la política (patente, número de OT) o su valor no es válido (por ejemplo, un código de grúa que no está en la tabla de equipos), el gasto queda **observado** hasta que se corrija. Si la fecha de rendición es anterior a la fecha del gasto, los datos son inconsistentes y el gasto queda observado hasta que se corrijan.\\n\\n---\\n\\n## P04 — Flota de Camiones y Camionetas\\n\\n**Descripción.** Gastos menores de mantención y operación de camiones, carros, camionetas y furgones **de la empresa**.\\n\\n**Cuándo usarla.** Cambio de aceite, revisión técnica, reparación de neumáticos, permiso de circulación de un vehículo de la empresa.\\n\\n**Cuándo NO usarla.** El combustible de un viaje va en P02 o P03. Vehículos personales van en P01. Peajes, estacionamiento y combustible de un viaje con un vehículo de la empresa van en P02 o P03, según el viaje; P04 es solo para mantención, remolque, permisos y multas de la flota.\\n\\n**Unidades permitidas.** Todas.\\n**Documentos.** Boleta o factura.\\n**Campos obligatorios.** **Patente** del vehículo.\\n**Regla especial.** Las multas de tránsito de vehículos de la empresa se rinden aquí, pero se registran como Gasto Rechazado (no deducible) y quedan **observadas** para que la jefatura decida si se descuentan al conductor.\\n\\n| Grupo | Categoría | Cuenta |\\n|---|---|---|\\n| Mantención Flota | Mantenciones menores | CTA-6300 |\\n| Mantención Flota | Neumáticos y recauchaje | CTA-6300 |\\n| Mantención Flota | Revisión técnica | CTA-6300 |\\n| Patentes y Permisos | Permiso de circulación | CTA-8002 |\\n| Máquinas y Equipos | Servicio de remolque | CTA-7100 |\\n| Gastos Rechazados | Multa | CTA-8500 |\\n\\n---\", \"fuente\": \"datos/politica_ficticia.md#P04\", \"puntaje\": -0.230600357056}, {\"politica\": \"Viajes Internos\", \"texto\": \"## Reglas generales\\n\\nEstas reglas aplican a todas las políticas, además de las reglas propias de cada una.\\n\\n**RG-01 — Documentos válidos.** Solo se aceptan **boleta** o **factura**. Se acepta **voucher** únicamente en taxi, aplicaciones de transporte (tipo Uber) y bus interurbano. Un voucher de cualquier otro tipo de comercio no es válido. En algunos sistemas el voucher aparece como tipo de documento **\\\"Otros\\\"**; se trata igual que un voucher. Un gasto con un documento no válido (según esta regla o según los documentos que exige cada política) se **rechaza**.\\n\\n**RG-02 — Solo gastos laborales.** Se prohíbe rendir gastos personales: compras para uso propio, alcohol, regalos personales, multas de tránsito de vehículos personales o de arriendo, propinas sobre el 10%, la alimentación individual en el lugar de trabajo, sin viaje ni reunión. Un gasto personal se **rechaza**.\\n\\n**RG-03 — Plazo de rendición.** El gasto se rinde en el mismo mes en que se hizo o, como máximo, hasta el **día 10 del mes siguiente**. Fuera de ese plazo el gasto se **rechaza**, salvo que el informe incluya el visto bueno escrito del Gerente General; en ese caso queda **observado** para revisión.\\n\\n**RG-04 — Segregación de funciones.** Quien hizo el gasto nunca puede aprobar su propia rendición.\\n\\n**RG-05 — Topes.** Algunas categorías tienen un monto máximo **por documento**. Si el monto por documento supera el tope, el gasto queda **observado** y el colaborador debe justificar el exceso.\\n\\n**RG-06 — Reclasificación de arriendo de autos livianos.** Si se arrienda un auto liviano (sedán, hatchback, station wagon o similar), el arriendo y **todos sus gastos asociados** (combustible, peajes, estacionamiento, transbordador) se rinden en la política **P01 Vehículos Propios**, aunque el viaje sea de trabajo. El arriendo de camionetas o furgones sí va en P02 o P03 según el viaje.\\n\\n**RG-07 — Exclusividad de unidad.** Algunas políticas solo pueden ser usadas por una unidad de negocio. Si otra unidad la usa, el gasto se **observa** para reclasificarlo.\\n\\n**RG-08 — Fondos por rendir.** Un gasto pagado con un fondo por rendir no puede superar el saldo disponible del fondo. Si lo supera, queda **observado**.\\n\\n**RG-09 — Gasto mal clasificado.** Si el gasto es válido pero el colaborador eligió una política o categoría incorrecta, queda **observado** con la política, categoría y cuenta correctas sugeridas.\\n\\n**RG-10 — Campos obligatorios.** Si falta un campo obligatorio de la política (patente, número de OT) o su valor no es válido (por ejemplo, un código de grúa que no está en la tabla de equipos), el gasto queda **observado** hasta que se corrija. Si la fecha de rendición es anterior a la fecha del gasto, los datos son inconsistentes y el gasto queda observado hasta que se corrijan.\\n\\n---\\n\\n## P02 — Viajes Internos\\n\\n**Descripción.** Gastos de viajes de trabajo **entre sedes de la empresa** (tiendas, Centro de Distribución, oficinas).\\n\\n**Cuándo usarla.** Un jefe de tienda que viaja al Centro de Distribución, un analista que visita tiendas de otra ciudad.\\n\\n**Cuándo NO usarla.** Viajes a proveedores, clientes o ferias van en P03. Si el viaje es con auto propio o auto liviano arrendado, los gastos del vehículo van en P01. Comidas sin un viaje de por medio no son gastos de viaje. Si son para una reunión interna o una capacitación, van en P08; si son una comida individual (por ejemplo, el almuerzo diario en la oficina), son un gasto personal y se rechazan (RG-02).\\n\\n**Unidades permitidas.** Todas.\\n**Documentos.** Boleta o factura (voucher solo según RG-01).\\n**Campos obligatorios.** Ninguno adicional.\\n**Topes (por documento).** Desayuno: $10.000. Almuerzo: $20.000. Cena: $45.000. Hotel: $445.000. Hostal: $295.000.\\n\\n| Grupo | Categoría | Cuenta |\\n|---|---|---|\\n| Movilización | Peaje | CTA-6100 |\\n| Movilización | Estacionamiento | CTA-6100 |\\n| Movilización | Pasaje | CTA-6100 |\\n| Movilización | Locomoción | CTA-6100 |\\n| Movilización | Transbordador | CTA-6100 |\\n| Movilización | Arriendo de camioneta o furgón | CTA-6100 |\\n| Gastos de Estadía | Hotel | CTA-6110 |\\n| Gastos de Estadía | Hostal | CTA-6110 |\\n| Gastos de Estadía | Desayuno | CTA-6110 |\\n| Gastos de Estadía | Almuerzo | CTA-6110 |\\n| Gastos de Estadía | Cena | CTA-6110 |\\n| Combustible | Gasolina (vehículo empresa o camioneta arrendada) | CTA-6900 |\\n| Combustible | Petróleo (vehículo empresa o camioneta arrendada) | CTA-6901 |\\n\\n---\", \"fuente\": \"datos/politica_ficticia.md#P02\", \"puntaje\": -0.261834800243}, {\"politica\": \"Grúas Horquilla\", \"texto\": \"## Reglas generales\\n\\nEstas reglas aplican a todas las políticas, además de las reglas propias de cada una.\\n\\n**RG-01 — Documentos válidos.** Solo se aceptan **boleta** o **factura**. Se acepta **voucher** únicamente en taxi, aplicaciones de transporte (tipo Uber) y bus interurbano. Un voucher de cualquier otro tipo de comercio no es válido. En algunos sistemas el voucher aparece como tipo de documento **\\\"Otros\\\"**; se trata igual que un voucher. Un gasto con un documento no válido (según esta regla o según los documentos que exige cada política) se **rechaza**.\\n\\n**RG-02 — Solo gastos laborales.** Se prohíbe rendir gastos personales: compras para uso propio, alcohol, regalos personales, multas de tránsito de vehículos personales o de arriendo, propinas sobre el 10%, la alimentación individual en el lugar de trabajo, sin viaje ni reunión. Un gasto personal se **rechaza**.\\n\\n**RG-03 — Plazo de rendición.** El gasto se rinde en el mismo mes en que se hizo o, como máximo, hasta el **día 10 del mes siguiente**. Fuera de ese plazo el gasto se **rechaza**, salvo que el informe incluya el visto bueno escrito del Gerente General; en ese caso queda **observado** para revisión.\\n\\n**RG-04 — Segregación de funciones.** Quien hizo el gasto nunca puede aprobar su propia rendición.\\n\\n**RG-05 — Topes.** Algunas categorías tienen un monto máximo **por documento**. Si el monto por documento supera el tope, el gasto queda **observado** y el colaborador debe justificar el exceso.\\n\\n**RG-06 — Reclasificación de arriendo de autos livianos.** Si se arrienda un auto liviano (sedán, hatchback, station wagon o similar), el arriendo y **todos sus gastos asociados** (combustible, peajes, estacionamiento, transbordador) se rinden en la política **P01 Vehículos Propios**, aunque el viaje sea de trabajo. El arriendo de camionetas o furgones sí va en P02 o P03 según el viaje.\\n\\n**RG-07 — Exclusividad de unidad.** Algunas políticas solo pueden ser usadas por una unidad de negocio. Si otra unidad la usa, el gasto se **observa** para reclasificarlo.\\n\\n**RG-08 — Fondos por rendir.** Un gasto pagado con un fondo por rendir no puede superar el saldo disponible del fondo. Si lo supera, queda **observado**.\\n\\n**RG-09 — Gasto mal clasificado.** Si el gasto es válido pero el colaborador eligió una política o categoría incorrecta, queda **observado** con la política, categoría y cuenta correctas sugeridas.\\n\\n**RG-10 — Campos obligatorios.** Si falta un campo obligatorio de la política (patente, número de OT) o su valor no es válido (por ejemplo, un código de grúa que no está en la tabla de equipos), el gasto queda **observado** hasta que se corrija. Si la fecha de rendición es anterior a la fecha del gasto, los datos son inconsistentes y el gasto queda observado hasta que se corrijan.\\n\\n---\\n\\n## P05 — Grúas Horquilla\\n\\n**Descripción.** Gastos menores de mantención y combustible de las grúas horquilla del Centro de Distribución.\\n\\n**Cuándo usarla.** Recarga de gas, reparación menor o cambio de neumáticos de una grúa horquilla.\\n\\n**Cuándo NO usarla.** Generadores u otras máquinas de tienda no van aquí (usar P10 si es mantención de instalaciones).\\n\\n**Unidades permitidas.** Solo **CD** (Centro de Distribución).\\n**Documentos.** Boleta o factura.\\n**Campos obligatorios.** **Patente** (código interno del equipo, ver tabla de equipos).\\n\\n| Grupo | Categoría | Cuenta |\\n|---|---|---|\\n| Mantención Grúas | Mantenciones menores | CTA-6310 |\\n| Mantención Grúas | Neumáticos y recauchaje | CTA-6310 |\\n| Combustible | Gas | CTA-6902 |\\n| Combustible | Petróleo | CTA-6901 |\\n| Combustible | Gasolina | CTA-6900 |\\n\\n**Equipos vigentes**\\n\\n| Código | Marca | Ubicación |\\n|---|---|---|\\n| GH-01 | Montacarga Sur | CD |\\n| GH-02 | Montacarga Sur | CD |\\n| GH-03 | Elevex | CD |\\n| GH-04 | Elevex | CD |\\n| GH-05 | Liftora | CD |\\n\\nUn código que no esté en esta tabla no es válido.\\n\\n---\", \"fuente\": \"datos/politica_ficticia.md#P05\", \"puntaje\": -0.270871162415}]"
}
── [llm] ──
{
  "paso": 2,
  "pide_herramientas": [
    {
      "name": "consultar_fondo",
      "args": {
        "id_fondo": "FR-001"
      },
      "id": "call_4536609767341705602",
      "type": "tool_call"
    }
  ],
  "texto": ""
}
── [observacion] ──
{
  "herramienta": "consultar_fondo",
  "resultado": "{\"id_fondo\": \"FR-001\", \"responsable\": \"Jefatura de Administración (ficticia)\", \"saldo_inicial\": 200000, \"saldo_actual\": 200000, \"gastos_aprobados\": []}"
}
── [llm] ──
{
  "paso": 3,
  "pide_herramientas": [
    {
      "name": "validar_gasto",
      "args": {
        "gasto": {
          "glosa": "peaje ida y vuelta CD - tienda Norte, camión de reparto",
          "unidad_negocio": "CD",
          "vb_gerente_general": false,
          "patente": "RZPT41",
          "id_fondo": "FR-001",
          "cargo": "Chofer Camión",
          "id": "G-0101",
          "fecha_rendicion": "2026-10-09",
          "proveedor": "Concesionaria Vial Lago Verde",
          "categoria_declarada": "Peaje",
          "fecha_gasto": "2026-10-06",
          "politica_declarada": "Viajes Internos",
          "monto": 7800,
          "numero_ot": null,
          "tipo_documento": "boleta"
        },
        "politica": "P02",
        "categoria": "Peaje"
      },
      "id": "call_12506654510361290229",
      "type": "tool_call"
    }
  ],
  "texto": ""
}
── [campos_alterados] ──
{
  "gasto": "G-0101",
  "campos": [
    "cargo"
  ]
}
── [gasto_original_restaurado] ──
{
  "gasto": "G-0101",
  "motivo": "se ignoraron cambios propuestos por el LLM"
}
── [observacion] ──
{
  "herramienta": "validar_gasto",
  "resultado": "{\"cumple\": true, \"incumplimientos\": [], \"cuenta\": \"CTA-6100\"}"
}
── [llm] ──
{
  "paso": 4,
  "pide_herramientas": [
    {
      "name": "emitir_veredicto",
      "args": {
        "politica": "P02",
        "decision": "aprobar",
        "cuenta": "CTA-6100",
        "categoria": "Peaje",
        "motivo": "El gasto cumple con todas las normativas aplicables: documento válido (boleta), plazo correcto de rendición (RG-03), monto dentro del saldo disponible del fondo (RG-08), y la clasificación en P02 (Viajes Internos), categoría Peaje, es correcta para un viaje entre sedes de la empresa (CD - tienda Norte)."
      },
      "id": "call_16609336463944169000",
      "type": "tool_call"
    }
  ],
  "texto": ""
}
── [juez] ──
{
  "valido": true,
  "razon": "El veredicto está justificado. El gasto cumple con las normas de P02 para un viaje de trabajo entre sedes (CD a tienda Norte), documento boleta válido (RG-01), plazo correcto (RG-03), y clasificación adecuada en P02 / Peaje / CTA-6100.",
  "evaluado": true,
  "uso_respaldo": false
}
── [fondo] ──
{
  "antes": "Fondo FR-001 (Jefatura de Administración (ficticia)): saldo disponible $200.000 de $200.000 CLP; 0 gasto(s) aprobado(s).",
  "despues": "Fondo FR-001 (Jefatura de Administración (ficticia)): saldo disponible $192.200 de $200.000 CLP; 1 gasto(s) aprobado(s) (G-0101)."
}
── [registro] ──
{
  "antes": {
    "registros": 0,
    "por_decision": {},
    "gasto": null
  },
  "despues": {
    "registros": 1,
    "por_decision": {
      "aprobar": 1
    },
    "gasto": {
      "id_gasto": "G-0101",
      "id_fondo": "FR-001",
      "monto": 7800,
      "decision": "aprobar",
      "motivo": "El gasto cumple con todas las normativas aplicables: documento válido (boleta), plazo correcto de rendición (RG-03), monto dentro del saldo disponible del fondo (RG-08), y la clasificación en P02 (Viajes Internos), categoría Peaje, es correcta para un viaje entre sedes de la empresa (CD - tienda Norte).",
      "politica_sugerida": "P02",
      "categoria_sugerida": "Peaje",
      "cuenta_sugerida": "CTA-6100",
      "registrado_en": "2026-11-27T00:34:54.177185+00:00"
    }
  },
  "id_gasto": "G-0101",
  "decision": "aprobar",
  "operacion": "insertado"
}
```

</details>

## Resultado (`GET /registro/a078d302-b429-4448-9774-cdaafe74343d` al terminar → `resultado`)
```json
{
  "id_ejecucion": "a078d302-b429-4448-9774-cdaafe74343d",
  "thread_id": "evidencia-03-revisar-gasto-20261126T213442",
  "ruta": "revisar_gasto",
  "motivo": "El mensaje solicita la revisión de un gasto concreto con datos estructurados adjuntos.",
  "respuesta": "Decisión: APROBAR\nPolítica: P02\nCategoría: Peaje\nCuenta: CTA-6100\nMotivo: El gasto cumple con todas las normativas aplicables: documento válido (boleta), plazo correcto de rendición (RG-03), monto dentro del saldo disponible del fondo (RG-08), y la clasificación en P02 (Viajes Internos), categoría Peaje, es correcta para un viaje entre sedes de la empresa (CD - tienda Norte).",
  "estado_final": "ok",
  "hubo_a2a": false,
  "herramientas_usadas": [
    "buscar_politica",
    "consultar_fondo",
    "validar_gasto",
    "emitir_veredicto"
  ],
  "pasos": 4,
  "veredicto": {
    "decision": "aprobar",
    "motivo": "El gasto cumple con todas las normativas aplicables: documento válido (boleta), plazo correcto de rendición (RG-03), monto dentro del saldo disponible del fondo (RG-08), y la clasificación en P02 (Viajes Internos), categoría Peaje, es correcta para un viaje entre sedes de la empresa (CD - tienda Norte).",
    "politica_sugerida": "P02",
    "categoria_sugerida": "Peaje",
    "cuenta_sugerida": "CTA-6100"
  }
}
```

## Registro (`GET /registro/a078d302-b429-4448-9774-cdaafe74343d` con `X-API-Key: ***` → HTTP 200)
```json
{
  "id_ejecucion": "a078d302-b429-4448-9774-cdaafe74343d",
  "fecha": "2026-11-27T00:34:42.810136+00:00",
  "ruta": "revisar_gasto",
  "pasos": 4,
  "herramientas_usadas": [
    "buscar_politica",
    "consultar_fondo",
    "validar_gasto",
    "emitir_veredicto"
  ],
  "hubo_a2a": false,
  "estado_final": "ok",
  "duracion_ms": 11395,
  "estado": "ok",
  "thread_id": "evidencia-03-revisar-gasto-20261126T213442",
  "inicio": "2026-11-27T00:34:42+00:00",
  "fin": "2026-11-27T00:34:54+00:00",
  "segundos": 11.4,
  "detail": null
}
```

Ruta obtenida: `revisar_gasto` · estado_final: `ok` · coincide con la esperada.
