# src/mcp_fondos/

Servidor MCP con la herramienta `consultar_fondo`, que reutiliza `src/principal/herramientas/fondos.py`.

- **Dueño:** Matías (`c2tf/matias-react-seguridad`), porque `consultar_fondo` se usa dentro del ReAct de `revisar_gasto`.
- **Transporte:** stdio. El cliente (`src/principal/herramientas/consultar_fondo.py`) arranca el servidor como
  proceso hijo en cada consulta, con un tiempo máximo de 20 s, y lo cierra. No hay que levantarlo aparte
  ni configurar variables, y en Heroku no necesita una app aparte (corre dentro del dyno del principal;
  falta probarlo allí).
- **Solo lectura:** devuelve el fondo registrado en `datos/fondos_ficticios.json`. Si el hilo ya tiene ese
  fondo con gastos aprobados, el ReAct le muestra al modelo el saldo vigente del hilo (RG-08).
- **Errores:** fondo inexistente, timeout o falla al arrancar → `ToolException` de una línea; nunca un saldo inventado.

Probarlo a mano (desde `tarea-final-c2/`, con el `.venv` activado):

```
python -m src.mcp_fondos.servidor --listar
```
Levanta el servidor igual que el agente y muestra su nombre y sus herramientas (evidencia de
`evidencias/ampliacion-mcp/`). Para pedir un fondo:

```
python -c "from src.principal.herramientas.consultar_fondo import consultar_fondo; print(consultar_fondo.invoke({'id_fondo': 'FR-001'}))"
```
