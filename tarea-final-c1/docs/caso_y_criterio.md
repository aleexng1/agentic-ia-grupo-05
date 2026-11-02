# Caso y criterio de éxito

## Problema

En la rendición de gastos, el colaborador debe elegir la política y la categoría de cada gasto. Es
común que elija mal, porque una misma categoría (peaje, combustible, almuerzo) existe en varias
políticas. No es un detalle de forma: cada política tiene un tratamiento contable distinto que debe
definirse desde el origen.

- **Costo o gasto:** un peaje para una orden de trabajo del taller es costo de venta recuperable (se
  cobra al cliente); uno de un viaje entre sedes es gasto operacional.
- **Naturaleza del pago:** con auto propio, el gasto se paga como bono de traslado al colaborador.
- **Efecto tributario:** el respaldo y el uso determinan si el IVA puede usarse como crédito fiscal y
  si el gasto es aceptado o rechazado tributariamente (por ejemplo, las multas).
- **Control de gestión:** cada cuenta alimenta presupuestos y centros de costo distintos.

Clasificar mal genera cuentas equivocadas, reportes distorsionados y reprocesos. En una empresa
grande pueden llegar cientos de rendiciones al mes, y revisarlas una por una consume buena parte del
tiempo de los analistas de Control de Gestión.

## Usuario

- **Principal:** analista de Control de Gestión de "Comercial Los Alerces SpA" (empresa ficticia), que
  hace la primera revisión normativa de las rendiciones.
- **Secundario:** el colaborador que rinde, que recibe la observación y corrige.

## Entrada

Un gasto rendido: fecha del gasto y de la rendición, monto, tipo de documento, glosa, política y
categoría declaradas, unidad de negocio, fondo y campos obligatorios (patente, número de OT). También
acepta preguntas sobre la política.

La política declarada por el usuario se usa como contexto: junto con la glosa, revela qué creía el
colaborador que era el gasto. El agente la trata como una pista, no como la respuesta, y la verifica
contra la política.

## Alcance

- Revisa gastos de a uno contra la política POL-RG-01 v1.5 (10 políticas, reglas RG-01 a RG-10).
- Puede buscar en la política (RAG), validar reglas exactas, emitir un veredicto y registrarlo en una
  base de prueba.
- No paga, no borra registros y solo actualiza la fila del gasto que revisa. No aprueba sin validar y
  no responde temas ajenos a las rendiciones.
- El agente no evalúa efectos tributarios (IVA, gastos rechazados), presupuestos ni centros de costo:
  esas consecuencias son la razón de clasificar bien desde el origen, y quedan a cargo de Contabilidad
  y Control de Gestión.

## Salida esperada

Una decisión (aprobar, observar o rechazar), con la política, categoría y cuenta correctas, los
códigos de las reglas aplicadas y el motivo. Si corresponde, el saldo del fondo actualizado y el
registro del veredicto. El agente no reemplaza al analista: aprueba lo claro, con un criterio siempre
igual, y le deja los casos observados.

## Comprobación observable

- **Ejemplo:** un peaje pagado con auto propio y declarado como Viajes Internos (P02) debe quedar
  observado, reclasificado a P01 / Peajes / CTA-5100, citando RG-09.
- **Criterio general:** el golden set ([`pruebas/golden_set.json`](../pruebas/golden_set.json), 34
  casos) define para cada caso lo que se espera (decisión, política, cuenta, reglas y herramientas,
  según corresponda). El evaluador ([`pruebas/evaluar.py`](../pruebas/evaluar.py)) los corre con Gemini
  real, y la corrida final debe pasar todos.

Gemini no responde siempre igual entre corridas. Si un caso falla, se analiza la causa con los
fragmentos y errores guardados, se corrige el agente (nunca se borra ni se relaja el caso para que
pase) y se vuelve a ejecutar. La evolución y las pruebas de estabilidad quedan en
[`pruebas/resultados/`](../pruebas/resultados/).

## Por qué un LLM

Elegir la política correcta requiere interpretar una glosa escrita libremente ("visita a proveedor
con mi auto") y contrastarla con las descripciones y excepciones de la política. Una regla fija no
distingue, por ejemplo, un peaje con auto propio de uno con vehículo de la empresa.

## Por qué herramientas

Las reglas exactas (plazos, topes, tipos de documento, campos obligatorios, saldo del fondo) deben
aplicarse siempre igual y ser auditables: se calculan con código (`validar_gasto`), no las decide el
LLM. La política se consulta con RAG para que el agente cite la fuente.

## Por qué un agente

La revisión no es un solo paso: buscar la política, validar, interpretar el resultado, corregir si una
herramienta rechaza el veredicto, y decidir. El ciclo ReAct permite repetir hasta tener una decisión
válida o detenerse de forma segura.
