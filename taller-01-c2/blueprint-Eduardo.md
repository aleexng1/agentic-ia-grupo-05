# Blueprint — Agente de Eduardo

| Elemento | Definición |
|---|---|
| Especialidad | Estimaciones agregadas simuladas de presupuesto para ferias y eventos. |
| Datos requeridos | Tipo de evento, personas (10–500) y duración (30–480 minutos). |
| Categorías | Tecnológico, gastronómico, cultural e infantil; con normalización de tildes y variantes comunes. |
| Herramienta | `estimar_presupuesto`: recinto referencial, equipamiento, personal, logística, alimentación genérica, subtotal, contingencia y total en CLP. |
| Cálculo | Tarifas locales completamente ficticias, bloques de 30 minutos redondeados hacia arriba y contingencia del 10 % redondeada hacia arriba al peso. |
| Límites | No son precios reales; impuestos no modelados. No determina menús, catering ni recintos, y no autoriza compras, reservas, pagos ni contratación. |
| Integración | LangChain/LangGraph, `MemorySaver`, herramienta registrada en el grafo y servidor A2A común en `URL_EDUARDO` (local: `http://127.0.0.1:8005`). |

Las tarifas existen únicamente para hacer reproducible la demostración y sus pruebas. No deben interpretarse como cotización o recomendación comercial.
