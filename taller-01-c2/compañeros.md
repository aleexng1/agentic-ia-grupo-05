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

- **Nombre del agente:** (pendiente)
- **URL pública:** (pendiente)
- **Ficha JSON:** (pendiente)
