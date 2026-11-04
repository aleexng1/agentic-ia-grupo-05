# Aporte de Eduardo — Notebook: RAG (sección 6) y juez LLM (sección 9)

**Estado:** material listo para incorporar por Matías, responsable de `agente.ipynb`. No modifica `src/`, golden set ni índice Redis. La ejecución final del notebook requiere autorización de Alex para consumir Gemini y Redis. Revisado frente a `main` en `3efd17e` y evidencia de la corrida 3, **34/34**.

## Resultado verificable que debe quedar visible al revisor

| Sección | Caso | Conducta esperada | Evidencia ya guardada |
|---|---|---|---|
| 6 — no buscar | GS-31 «Hola» | Responde sin `buscar_politica` ni veredicto | `pruebas/resultados/corrida_3.json` |
| 6 — buscar | GS-33 «¿Hasta qué día puedo rendir un gasto de octubre?» | Usa RAG; RG-03, respuesta «10 de noviembre»; fuentes y puntajes | `corrida_3.json` |
| 9 — benigno | GS-01 | Juez evalúa una aprobación P02; `valido=True` y razón | `prueba_dirigida_PR41_general.json` |
| 9 — adversarial | GS-29 | El agente rechaza P07 por boleta incompatible; juez evalúa el **rechazo** `valido=True` con motivo | `prueba_dirigida_PR41_general.json` |

**Precisión importante:** `valido=True` significa «el veredicto del agente está justificado», **no** «gasto aprobado». Un rechazo P07 puede estar correctamente validado por el juez. La corrida 3 no certifica que el juez detecte *todas* las malas clasificaciones posibles.

**Metadatos del índice, según configuración de código y carga registrada por Alex:** `REDIS_PREFIJO=grupo05_v15`, política POL-RG-01 v1.6, 20 documentos (P01–P10 y RG-01–RG-10), modelo `models/gemini-embedding-001`, dimensión `3072`, `COSINE`, `FLAT`, `legacy_key_format=False`. Campos publicados: `text`, `embedding`, `_index_name`, `_metadata_json`. Referencia de inspección real por Alex: `README.md`, sección «Embeddings e índice». Eduardo no volvió a consultar Redis.

## 6.A — Código de apoyo: evidencia archivada (OFFLINE, no consulta servicios)

Esta celda es independiente del notebook y se puede ejecutar inmediatamente. **Rotularla «evidencia de corrida 3»**, no «ejecución real de esta celda»: sirve para entender el golden set y mostrar fuentes históricas sin consumir cuota.

```python
import json
from pathlib import Path

archivo = Path("pruebas/resultados/corrida_3.json")
corrida = json.loads(archivo.read_text(encoding="utf-8"))
assert corrida["resumen"]["pasan"] == 34
assert corrida["indice"] == "grupo05_v15"

for identificador in ("GS-31", "GS-33"):
    caso = next(c for c in corrida["casos"] if c["id"] == identificador)
    obtenido = caso["turnos"][0]["obtenido"]
    herramientas = obtenido.get("herramientas", [])
    print("\n", identificador, "| herramientas:", herramientas)
    print("Respuesta:", obtenido.get("texto", ""))
    for fragmento in obtenido.get("fragmentos", []):
        print("RAG:", fragmento["politica"], fragmento["fuente"], fragmento["puntaje"])
    if identificador == "GS-31":
        assert "buscar_politica" not in herramientas
    else:
        assert "buscar_politica" in herramientas
        assert any("RG-03" in f["fuente"] for f in obtenido["fragmentos"])
```

## 6.B — Código de la demostración REAL (Matías; ejecutar solo con autorización de cuota)

Ejecuta el agente **una vez por pregunta** y examina el historial real del grafo para demostrar la decisión de usar o no `buscar_politica`. Esta celda **sí consume Gemini**, y GS-33 también puede consumir embeddings/Redis. Si falla por cuota o disponibilidad, conservar la salida sin repetir a ciegas. No requiere base de registro porque no hay gasto estructurado.

```python
import json
import os
from langchain_core.messages import AIMessage, ToolMessage
from src.grafo import construir_agente, conversar

assert os.getenv("REDIS_PREFIJO") == "grupo05_v15", "Revisar .env antes de ejecutar"
agente_rag_demo = construir_agente()

for identificador, consulta in [
    ("GS-31", "Hola"),
    ("GS-33", "¿Hasta qué día puedo rendir un gasto de octubre?"),
]:
    hilo = "notebook-eduardo-rag-" + identificador
    respuesta = conversar(agente_rag_demo, consulta, hilo)
    estado = agente_rag_demo.get_state({"configurable": {"thread_id": hilo}}).values
    mensajes = estado.get("messages", [])
    llamadas = [
        llamada["name"]
        for mensaje in mensajes if isinstance(mensaje, AIMessage)
        for llamada in getattr(mensaje, "tool_calls", [])
    ]
    print(f"\n{identificador} | herramientas realmente solicitadas: {llamadas}")
    print("Respuesta:", respuesta)

    for mensaje in mensajes:
        if not isinstance(mensaje, ToolMessage) or mensaje.name != "buscar_politica":
            continue
        # El grafo recibe las salidas de las herramientas como JSON.
        try:
            fragmentos = json.loads(mensaje.content)
        except (TypeError, ValueError):
            print("RAG: contenido no legible como JSON, revisar la traza.")
            continue
        if not isinstance(fragmentos, list):
            continue
        for f in fragmentos:
            if not isinstance(f, dict):
                continue
            print("Fuente:", f.get("fuente"))
            print("Política/regla:", f.get("politica"), "| puntaje:", f.get("puntaje"))
            print("Extracto:", str(f.get("texto", ""))[:160].replace("\n", " "))

    if identificador == "GS-31":
        assert "buscar_politica" not in llamadas
    else:
        assert "buscar_politica" in llamadas
```

**Interpretación esperada:** GS-31 no debe llamar herramientas. GS-33 debe recuperar RG-03 y responder el límite del día 10 del mes siguiente. El puntaje mostrado por `src/rag.py` es el negativo de la distancia devuelta por Redis; **mayor puntaje = mayor similitud**, no una probabilidad ni un porcentaje. No imprimir la URL de Redis ni variables secretas.

## 9.A — Código de apoyo: razones REALES ya publicadas (OFFLINE)

La siguiente celda reproduce evidencia generada previamente por Alex, no vuelve a llamar al juez. Es la mejor verificación documental sin cuota, pero **no sustituye** una ejecución del juez dentro del notebook.

```python
import json
from pathlib import Path
from src.config import MODELO_DEL_CURSO
from src.seguridad import PROMPT_JUEZ

print("Modelo del juez:", MODELO_DEL_CURSO)
print("PROMPT_JUEZ (versión vigente):\n", PROMPT_JUEZ)

archivo = Path("pruebas/resultados/prueba_dirigida_PR41_general.json")
prueba = json.loads(archivo.read_text(encoding="utf-8"))
for identificador in ("G-0101", "G-2901"):
    dictamenes = [d for d in prueba["dictamenes_juez"] if d["gasto"] == identificador]
    assert dictamenes, f"No hay evidencia de {identificador}"
    for d in dictamenes:
        print("\nGasto:", identificador)
        print("Decisión auditada:", d["decision_auditada"])
        print("Política auditada:", d["politica_auditada"])
        print("Evaluado:", d["evaluado"], "| válido:", d["valido"])
        print("Razón del juez:", d["razon"])
```

**Control:** `G-0101` tiene dictamen `aprobar/P02`. `G-2901` tiene tres dictámenes `rechazar/P07` y `valido=True`. No debe mostrarse que el juez «rechazó» automáticamente una petición maliciosa: lo que hizo fue auditar y dar por justificado el **veredicto de rechazo** del agente.

## 9.B — Demostración REAL en notebook: decisión aplicada y dictamen de juez (Matías)

**Solo ejecutar en la corrida final coordinada con Alex.** Recorre GS-01 y GS-29 con gasto estructurado real del golden set, activa trazas reales, obtiene el evento `juez` registrado por el grafo y compara con el estado final. Esta celda ejecuta el agente (Gemini/Redis) y escribe **solo** en un SQLite temporal; restaura la ruta del registro y las variables de entorno incluso si hay un error. Puede utilizarse como implementación de la sección 9, o adaptarse para reutilizar las corridas previas del notebook y evitar llamadas duplicadas.

```python
import io
import json
import os
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

from src import registro
from src.config import CARPETA_PROYECTO, MODELO_DEL_CURSO
from src.grafo import construir_agente, conversar_con_caso
from src.seguridad import PROMPT_JUEZ

assert os.getenv("REDIS_PREFIJO") == "grupo05_v15"
print("Modelo juez:", MODELO_DEL_CURSO)
print("PROMPT_JUEZ:\n", PROMPT_JUEZ)

golden = json.loads(
    (CARPETA_PROYECTO / "pruebas" / "golden_set.json").read_text(encoding="utf-8")
)
ruta_original = registro.RUTA_REGISTRO
trazas_original = os.environ.get("MOSTRAR_TRAZAS")

with tempfile.TemporaryDirectory() as temporal:
    try:
        registro.RUTA_REGISTRO = Path(temporal) / "registro_juez.db"
        os.environ["MOSTRAR_TRAZAS"] = "1"

        for identificador, decision_esperada in [("GS-01", "aprobar"), ("GS-29", "rechazar")]:
            caso = next(c for c in golden["casos"] if c["id"] == identificador)
            turno = caso["turnos"][0]
            gasto = turno["gasto"]
            mensaje = turno["mensaje"] + "\nGasto rendido:\n" + json.dumps(gasto, ensure_ascii=False)
            agente = construir_agente()
            hilo = "notebook-eduardo-juez-" + identificador

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                respuesta = conversar_con_caso(agente, mensaje, hilo, gasto)

            estado = agente.get_state({"configurable": {"thread_id": hilo}}).values
            veredicto = estado.get("veredicto") or {}
            registro_juez = buffer.getvalue()
            marcador = "── [juez] ──\n"
            assert marcador in registro_juez, "No se observó registrar_traza('juez', ...)"
            bloque = registro_juez.split(marcador)[-1].split("\n── [", 1)[0]
            juicio = json.loads(bloque.strip())

            print("\n", identificador)
            print("Decisión final aplicada:", veredicto.get("decision"))
            print("Política final:", veredicto.get("politica_sugerida"))
            print("Juez evaluado:", juicio.get("evaluado"))
            print("Juez válido:", juicio.get("valido"))
            print("Razón del juez:", juicio.get("razon"))
            print("Herramientas RAG/validación solicitadas en esta ejecución:")
            from langchain_core.messages import AIMessage
            llamadas = [
                llamada["name"]
                for m in estado["messages"] if isinstance(m, AIMessage)
                for llamada in getattr(m, "tool_calls", [])
            ]
            print(llamadas)
            assert veredicto.get("decision") == decision_esperada, "No coincide la decisión esperada"
    finally:
        registro.RUTA_REGISTRO = ruta_original
        if trazas_original is None:
            os.environ.pop("MOSTRAR_TRAZAS", None)
        else:
            os.environ["MOSTRAR_TRAZAS"] = trazas_original
```

**Aviso:** la salida de un LLM no es completamente determinista, aun con temperatura 0. Si una ejecución final contradice la corrida 3 o falta el evento del juez, guardar la traza y coordinar con Alex; **no modificar** `src/`, `golden_set.json` ni ejecutar reintentos repetidos para esconder un fallo. Las celdas 6.B y 9.B son **propuestas de integración** inspeccionadas contra el código; no se han ejecutado localmente en este documento.

## Checklist de aceptación para Matías y Alex

- [ ] Cambiar `REDIS_PREFIJO=grupo05_v15` en el `.env` local con credenciales propias, sin publicarlas.
- [ ] Sección 6: mostrar configuración, GS-31 **sin RAG**, GS-33 **con RAG**, fuentes, puntajes y respuesta que utiliza RG-03.
- [ ] Sección 9: mostrar `PROMPT_JUEZ`, modelo, razón, `valido`, `evaluado` y **decisión final aplicada** de GS-01 y GS-29.
- [ ] Mantener diferencia entre salidas **reales del notebook** y **evidencia archivada** o simulada.
- [ ] Trazas legibles; no imprimir ruta absoluta de usuario ni secretos. No guardar el texto completo de los fragmentos si contiene información sensible.
- [ ] Ejecutar el notebook **una sola vez desde cero**, con cuota coordinada por Alex; revisar `agente_ejecutado.ipynb` antes de publicar.
- [ ] No hacer cambios en `src/` después de la corrida 3; comentario de versión del PR #42 fue documentado sin cambio funcional.
