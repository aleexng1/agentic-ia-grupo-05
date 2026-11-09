### ¿Qué ficha eligió mejor el supervisor y qué decía?

En la ronda grupal las 12 preguntas llegaron bien (12 de 12). Cada agente recibió la pregunta de su
dueño y una del tema de otro compañero, y las cuatro preguntas «que nadie sabe» fueron a «ninguno».
Como las cuatro fichas acertaron, elegimos la que funcionó con la pregunta más difícil: la de
**Eduardo**. La pregunta de Alex «¿Cuánta plata necesito más o menos para una feria gastronómica de
120 personas que dura 3 horas?» no dice «presupuesto» ni «costo», y aun así el supervisor la mandó a
Eduardo con el motivo «La pregunta solicita una estimación de presupuesto y costos para un evento».
En la ronda de Eduardo el motivo repite una palabra propia de su ficha: «estimación de un
presupuesto simulado». La frase de la ficha que lo explica es: «Estima presupuestos agregados y
simulados para ferias y eventos usando únicamente tarifas ficticias».

### ¿Hubo preguntas que dos agentes podían responder? ¿Cómo se resolvió?

Sí. En el ensayo general del 8 de noviembre (los 4 agentes en un computador) aparecieron dos casos.
En ambos el supervisor eligió bien según la ficha, pero el prompt del agente contradecía su ficha y
rechazaba la pregunta:

- **Costo del catering (Eduardo y Sebastián).** «¿Cuánto cuesta el catering para 100 personas?» fue
  a Eduardo porque es un costo, pero su prompt la mandaba a Sebastián, que no da precios: nadie la
  respondía. Se corrigió en el PR #64. Ahora el prompt de Eduardo trata el costo de la comida como
  consulta de costos y usa `estimar_presupuesto`. Su ficha pasó de «No prepara menús ni cotiza
  catering» a «Incluye un costo de alimentación genérica por persona, pero no prepara menús
  (Sebastián)». Qué menú servir sigue siendo de Sebastián.
- **Hora del almuerzo (Sebastián y Matías).** «¿A qué hora conviene el almuerzo?» fue a Sebastián,
  porque su ficha dice «con la hora de cada servicio». Pero su prompt la rechazaba como «horario de
  actividades», que es tema de Matías. Se corrigió en el PR #65. Ahora el prompt de Sebastián dice
  primero que cuándo servir la comida sí es su tema y después que el programa de actividades no lo
  es. En la prueba de control pidió los datos en todos los intentos.

En la ronda también hubo preguntas en el borde entre dos temas, y se resolvieron bien:

- La de Eduardo sobre comida para 80 niños con 6 celíacos tocaba un tema que ahora también está en
  su presupuesto. Como preguntaba qué servir y no cuánto cuesta, fue a Sebastián («propuesta de
  comida con opciones específicas para celíacos»).
- La de Sebastián sobre qué charlas o talleres hacer «y en qué orden» fue a Matías. Según
  Sebastián, eso se debió a la frase de su ficha «no arma el programa de actividades».
- La de Matías («¿qué actividades pongo y a qué hora?») fue a Matías, aunque la ficha de Sebastián
  también habla de horas (Matías lo comenta abajo).

### ¿Qué cambiaría cada uno de su ficha?

- **Matias Muñoz:** su descripción usa «horario» sin precisar que es el de las actividades, y la
  ficha de Sebastián también habla de «la hora de cada servicio» de comida. Precisaría «horario de
  las actividades» y agregaría un ejemplo con público de estudiantes, porque el único que tiene es
  de una feria infantil.
- **Alex Nail:** La ficha funcionó: el supervisor me mandó las preguntas de recintos, incluida la de una feria con food trucks del ensayo, en la que el agente pidió la cantidad de personas antes de recomendar. Cambiaría dos cosas. Agregaría a la descripción que necesito tres datos (tipo de feria, cantidad de personas y si se prefiere interior o exterior), para que quien pregunta los dé de entrada. Y haría que el agente indique si un recinto permite servicio de comida (el dato ya está en mi catálogo, pero hoy no lo muestra), aclarando que qué servir es tema de Sebastián, porque esa es la frontera más cercana entre nuestros agentes.
- **Eduardo Basaure:** haría más explícito que estima costos ficticios de alimentación genérica,
  pero no propone menús ni cotiza proveedores reales, que corresponden a Sebastián. También
  destacaría los tres datos necesarios para estimar un presupuesto: tipo de evento, cantidad de
  asistentes y duración.
- **Sebastian Mardones:** la ficha funcionó y el supervisor eligió bien sus tres preguntas. Dejaría
  la frase «no arma el programa de actividades», porque es la que mandó la pregunta de charlas a
  Matías. Le agregaría que también responde la hora de los servicios de comida, porque en el
  ensayo ese tipo de pregunta se confundía con el horario de actividades.
