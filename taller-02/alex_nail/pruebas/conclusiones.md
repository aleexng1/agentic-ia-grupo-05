E1. Armé el agente solo con prompts a Claude Code, adaptados a Linux y al Redis compartido. A la primera pregunta respondió citando el resumen (p. 1), pero con solo 0,699 de parecido y dos fragmentos de bibliografía arriba. Los tropiezos fueron del entorno, no del código: la cuota diaria de Gemini y el Redis lleno obligaron a agregar caché de embeddings y a corregir el orden del --reset.

E2. Los embeddings miden significado: las dos frases sobre reembolsar una comida dieron 0,872 sin compartir palabras, frente a ~0,69 con la frase de otro tema. En la prueba del banco, la frase con otras palabras y el mismo sentido (0,865) superó a la que compartía "banco" (0,808). Para buscar, el índice gana siempre que los datos estén en un servidor.

E3. Las tres configuraciones respondieron bien citando la p. 4, así que la diferencia estuvo en los detalles: 400/50 deja fragmentos muy chicos y casi sin solape (16% de los pares), y 1200/200 mezcla temas. Elegí 800/120 por su parecido más alto (0,822). También aprendí que el solape repite oraciones completas, no un número fijo de caracteres.

E4. 0 falsos positivos y 0 falsos negativos en 12 preguntas. La bibliografía fue el principal ruido y dejó la pregunta F a 0,002 del umbral original. Por eso subí UMBRAL a 0,68 y dejé TOP_K en 3.

E5. Cambié dos reglas que ya mostraban problemas: las citas (dejó de juntar páginas) y el formato (desaparecieron los símbolos de LaTeX). El agente pasó la trampa del 2010 antes y después, y no inventó ni sin las reglas de protección. Como corrí cada configuración una vez, parte de los cambios puede ser variación normal del modelo.

E6. El nodo reformular no cumplió su objetivo principal: la pregunta general casi no subió (0,699 → 0,700) y el resumen salió del top-3. Los controles se mantuvieron, pero el nodo cuesta una llamada más por pregunta y acercó la F al umbral. Aprendí que reescribir no arregla una pregunta sobre el documento mismo.
