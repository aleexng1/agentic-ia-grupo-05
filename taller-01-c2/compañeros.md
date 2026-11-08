# Agentes de los compañeros · Grupo 5

Fichas descargadas durante la prueba grupal del **8 de noviembre de 2026**, desde la
dirección pública de cada integrante (`/.well-known/agent-card.json`). Las direcciones son
túneles rápidos de Cloudflare: cambian cada vez que se reinicia el túnel.

```bash
curl -s https://DIRECCION-DEL-COMPAÑERO/.well-known/agent-card.json
```

## Matias Muñoz · Programa y horarios

- **Autor:** Matias Muñoz
- **Nombre del agente:** Agente de Matias
- **Skill:** Armar programa de feria (`armar_programa`)
- **URL pública:** `https://plugin-telescope-termination-riverside.trycloudflare.com` (prueba grupal del 2026-11-08; cambia al reiniciar el túnel)
- **Ficha JSON:** [`evidencias/alex/fichas-companeros/matias.json`](evidencias/alex/fichas-companeros/matias.json)

```json
{
  "name": "Agente de Matias",
  "description": "Arma el programa de actividades y el horario de ferias tecnológicas, gastronómicas, culturales o infantiles de 30 minutos a 8 horas, para público familiar, adulto o estudiantes. No responde sobre lugares ni capacidad, comida ni costos, y no reserva ni confirma el programa definitivo: entrega solo propuestas.",
  "supportedInterfaces": [
    {
      "url": "https://plugin-telescope-termination-riverside.trycloudflare.com",
      "protocolBinding": "JSONRPC",
      "protocolVersion": "1.0"
    }
  ],
  "version": "1.0.0",
  "capabilities": {
    "streaming": false
  },
  "defaultInputModes": [
    "text/plain"
  ],
  "defaultOutputModes": [
    "text/plain"
  ],
  "skills": [
    {
      "id": "armar_programa",
      "name": "Armar programa de feria",
      "description": "Propone las actividades que caben en el tiempo disponible, con su hora de inicio y término, según tipo de evento, público y hora de inicio.",
      "tags": [
        "armar_programa"
      ],
      "examples": [
        "Necesito armar el programa de una feria infantil de 3 horas que parta a las 15:00."
      ],
      "inputModes": [
        "text/plain"
      ],
      "outputModes": [
        "text/plain"
      ]
    }
  ]
}
```

## Alex Nail · Lugares y capacidad

- **Autor:** Alex Nail
- **Nombre del agente:** Agente de Alex
- **Skill:** Buscar recintos para una feria (`buscar_recintos`)
- **URL pública:** `https://engaging-dem-merge-momentum.trycloudflare.com` (prueba grupal del 2026-11-08; cambia al reiniciar el túnel)
- **Ficha JSON:** [`evidencias/alex/fichas-companeros/alex.json`](evidencias/alex/fichas-companeros/alex.json)

```json
{
  "name": "Agente de Alex",
  "description": "Recomienda hasta tres recintos para ferias tecnológicas, gastronómicas, culturales o infantiles de 10 a 500 personas, en espacio interior o exterior, e indica para cada uno la capacidad, el % de ocupación, los m² por persona, los stands estimados, el estacionamiento y la accesibilidad. No da precios ni arriendos, no arma el menú ni el catering, no arma el programa de actividades y no reserva recintos.",
  "supportedInterfaces": [
    {
      "url": "https://engaging-dem-merge-momentum.trycloudflare.com",
      "protocolBinding": "JSONRPC",
      "protocolVersion": "1.0"
    }
  ],
  "version": "1.0.0",
  "capabilities": {
    "streaming": false
  },
  "defaultInputModes": [
    "text/plain"
  ],
  "defaultOutputModes": [
    "text/plain"
  ],
  "skills": [
    {
      "id": "buscar_recintos",
      "name": "Buscar recintos para una feria",
      "description": "Busca recintos donde cabe el evento con un 10 % de holgura, según el tipo de feria, la cantidad de personas y si se prefiere un espacio interior o exterior, y avisa cuando un lugar queda demasiado grande.",
      "tags": [
        "buscar_recintos"
      ],
      "examples": [
        "Voy a hacer una feria tecnológica para 150 personas, ¿dónde la puedo hacer?"
      ],
      "inputModes": [
        "text/plain"
      ],
      "outputModes": [
        "text/plain"
      ]
    }
  ]
}
```

## Eduardo Basaure · Presupuesto y costos estimados

- **Autor:** Eduardo Basaure
- **Nombre del agente:** Agente de Eduardo
- **Skill:** Estimar presupuesto de evento (`estimar_presupuesto`)
- **URL pública:** `https://legend-origin-minor-admissions.trycloudflare.com` (prueba grupal del 2026-11-08; cambia al reiniciar el túnel)
- **Ficha JSON:** [`evidencias/alex/fichas-companeros/eduardo.json`](evidencias/alex/fichas-companeros/eduardo.json)

```json
{
  "name": "Agente de Eduardo",
  "description": "Estima presupuestos agregados y simulados para ferias y eventos usando únicamente tarifas ficticias. Incluye un costo de alimentación genérica por persona, pero no prepara menús (Sebastián), ni recomienda recintos (Alex); tampoco autoriza compras, reservas, pagos o contrataciones.",
  "supportedInterfaces": [
    {
      "url": "https://legend-origin-minor-admissions.trycloudflare.com",
      "protocolBinding": "JSONRPC",
      "protocolVersion": "1.0"
    }
  ],
  "version": "1.0.0",
  "capabilities": {
    "streaming": false
  },
  "defaultInputModes": [
    "text/plain"
  ],
  "defaultOutputModes": [
    "text/plain"
  ],
  "skills": [
    {
      "id": "estimar_presupuesto",
      "name": "Estimar presupuesto de evento",
      "description": "Calcula partidas agregadas simuladas en CLP para un evento, según tipo, asistentes y duración.",
      "tags": [
        "estimar_presupuesto"
      ],
      "examples": [
        "¿Cuál es el presupuesto simulado de una feria tecnológica para 80 personas y 4 horas?"
      ],
      "inputModes": [
        "text/plain"
      ],
      "outputModes": [
        "text/plain"
      ]
    }
  ]
}
```

## Sebastian Mardones · Comida y catering

- **Autor:** Sebastian Mardones
- **Nombre del agente:** Agente de Sebastian
- **Skill:** Armar catering del evento (`armar_catering`)
- **URL pública:** `https://defining-envelope-obtaining-dem.trycloudflare.com` (prueba grupal del 2026-11-08; cambia al reiniciar el túnel)
- **Ficha JSON:** [`evidencias/alex/fichas-companeros/sebastian.json`](evidencias/alex/fichas-companeros/sebastian.json)

```json
{
  "name": "Agente de Sebastian",
  "description": "Propone la comida que se sirve a los asistentes de ferias tecnológicas, gastronómicas, culturales o infantiles de 10 a 500 personas y de 30 minutos a 8 horas: coffee break, cóctel, box lunch, almuerzo buffet, food trucks o colación infantil, con la hora de cada servicio, las cantidades y el agua calculadas, y menús vegetarianos, veganos, sin gluten y sin lactosa. No da precios ni presupuestos, no recomienda recintos ni capacidad, no arma el programa de actividades y no contrata proveedores: entrega solo propuestas.",
  "supportedInterfaces": [
    {
      "url": "https://defining-envelope-obtaining-dem.trycloudflare.com",
      "protocolBinding": "JSONRPC",
      "protocolVersion": "1.0"
    }
  ],
  "version": "1.0.0",
  "capabilities": {
    "streaming": false
  },
  "defaultInputModes": [
    "text/plain"
  ],
  "defaultOutputModes": [
    "text/plain"
  ],
  "skills": [
    {
      "id": "armar_catering",
      "name": "Armar catering del evento",
      "description": "Propone qué servir y a qué hora, con cantidades y litros de agua calculados, según tipo de evento, personas, duración, hora de inicio y dietas especiales.",
      "tags": [
        "armar_catering"
      ],
      "examples": [
        "Voy a hacer una feria infantil de 3 horas desde las 11:00 para 80 personas y 6 niños son celíacos, ¿qué les damos de comer?"
      ],
      "inputModes": [
        "text/plain"
      ],
      "outputModes": [
        "text/plain"
      ]
    }
  ]
}
```
