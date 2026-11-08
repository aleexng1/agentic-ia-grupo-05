# Agentes de los compañeros · Grupo 5

Completar cuando cada compañero comparta su dirección pública. Pegar la ficha JSON
descargada con:

```powershell
Invoke-RestMethod https://DIRECCION-DEL-COMPAÑERO/.well-known/agent-card.json | ConvertTo-Json -Depth 10
```

## Alex Nail · Lugares y capacidad

- **Nombre del agente:** Agente de Alex
- **URL pública:** `https://jenny-regulated-airfare-possibilities.trycloudflare.com` (túnel del 2026-11-07; cambia al reiniciarlo)
- **Ficha JSON:** descargada desde la URL pública (`evidencias/alex/03-ficha-publica.json`):

```json
{
    "name": "Agente de Alex",
    "description": "Recomienda hasta tres recintos para ferias tecnológicas, gastronómicas, culturales o infantiles de 10 a 500 personas, en espacio interior o exterior, e indica para cada uno la capacidad, el % de ocupación, los m² por persona, los stands estimados, el estacionamiento y la accesibilidad. No da precios ni arriendos, no arma el menú ni el catering, no arma el programa de actividades y no reserva recintos.",
    "supportedInterfaces": [
        {
            "url": "https://jenny-regulated-airfare-possibilities.trycloudflare.com",
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

- **Nombre del agente:** (pendiente)
- **URL pública:** (pendiente)
- **Ficha JSON:** (pendiente)

## Sebastian Mardones · Comida y catering

- **Nombre del agente:** Agente de Sebastian
- **URL pública:** `https://replace-earl-univ-robinson.trycloudflare.com` (túnel del 2026-11-08; cambia al reiniciarlo)
- **Ficha JSON:** descargada desde la URL pública (`evidencias/sebastian/02-ficha.json`):

```json
{
  "name": "Agente de Sebastian",
  "description": "Propone la comida que se sirve a los asistentes de ferias tecnológicas, gastronómicas, culturales o infantiles de 10 a 500 personas y de 30 minutos a 8 horas: coffee break, cóctel, box lunch, almuerzo buffet, food trucks o colación infantil, con la hora de cada servicio, las cantidades y el agua calculadas, y menús vegetarianos, veganos, sin gluten y sin lactosa. No da precios ni presupuestos, no recomienda recintos ni capacidad, no arma el programa de actividades y no contrata proveedores: entrega solo propuestas.",
  "supportedInterfaces": [
    {
      "url": "https://replace-earl-univ-robinson.trycloudflare.com",
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
