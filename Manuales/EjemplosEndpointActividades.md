# Guía Visual de Ejemplos: Endpoint `POST /verificar-actividad`

Este documento está diseñado de forma clara y visual para **personas no técnicas** o evaluadores del proyecto. Muestra exactamente cómo responde el sistema ante diferentes mensajes enviados por WhatsApp según la actividad de cada día.

---

## 📊 Tabla Comparativa Resumen (Respuestas Válidas vs. Inválidas)

| Día y Actividad | Pregunta del Reto | Respuesta Esperada en la BD | Mensaje Enviado por el Usuario en WhatsApp | Veredicto | Puntos | Explicación / Feedback Entregado |
|---|---|---|---|---|---|---|
| **Lunes**<br>*(Pregunta / Aplicación)* | ¿Qué enseñanza práctica te deja el pasaje de hoy sobre el amor al prójimo? | Debemos amar a nuestro prójimo con acciones verdaderas y no solo de palabra. | **Válida**: *"Hola grupo buenos días, la enseñanza es que hay que demostrar el amor al prójimo con obras reales y no solo hablando."* | `valido` | **1 pt** | Respuesta aceptada. Captura la idea central. |
| | | | **Inválida**: *"Bendiciones, hoy voy a salir de viaje con mi familia."* | `invalido` | **0 pts** | La respuesta no alcanza la similitud requerida con la idea esperada. |
| **Martes**<br>*(Detective Bíblico)* | ¿Quién fue el personaje que lideró al pueblo a través del Mar Rojo? | Moisés | **Válida**: *"Buenas tardes hermano, la respuesta al reto de hoy es Moisés."* | `valido` | **2 pts** | Dato clave ('Moisés') identificado correctamente. |
| | | | **Inválida**: *"Hola bendiciones creo que fue Josué."* | `invalido` | **0 pts** | No se identificó el dato clave esperado ('Moisés'). |
| **Miércoles**<br>*(Reto 20 segundos)* | Menciona 3 frutos del Espíritu Santo. | amor, gozo, paz | **Válida Completa**: *"Bendiciones a todos, mis respuestas son: amor, gozo y paz"* | `valido` | **2 pts** | Contiene 3 de 3 elementos esperados. |
| | | | **Válida Parcial (2/3)**: *"Hola grupo, me acordé de amor y gozo"* | `valido` | **2 pts** | Contiene 2 de 3 elementos esperados (mínimo requerido: 2). |
| | | | **Inválida (1/3)**: *"Hola solo recuerdo paciencia"* | `invalido` | **0 pts** | Contiene solo 0 de 3 elementos esperados. Faltó: amor, gozo, paz. |
| **Jueves**<br>*(Completa la Idea)* | Completa el versículo: *"El Señor es mi pastor..."* | nada me faltará | **Válida**: *"Amén hermanos, nada me faltará"* | `valido` | **1 pt** | Completa correctamente la idea planteada. |
| | | | **Inválida**: *"Hola bendiciones, todo lo puedo en Cristo que me fortalece"* | `invalido` | **0 pts** | La respuesta no completa adecuadamente la idea requerida. |
| **Viernes**<br>*(Reto Sorpresa)* | Reto Sorpresa: Explica qué hizo Abraham cuando Dios probó su fe. | Abraham estuvo dispuesto a obedecer a Dios y ofrecer a su hijo Isaac. | **Válida**: *"Buenas noches hermanos, la respuesta es que Abraham demostró su fe obedeciendo a Dios al ofrecer a Isaac."* | `valido` | **2 pts** | Respuesta válida para el reto sorpresa. |
| | | | **Inválida**: *"Hola no alcancé a leer hoy."* | `invalido` | **0 pts** | La respuesta no cumple el criterio del reto sorpresa. |
| **Sábado**<br>*(Prueba de Fuego)* | Resume los 3 puntos principales del Éxodo de Israel. | 1. Moisés guió al pueblo<br>2. Cruzaron el Mar Rojo<br>3. Recibieron la ley en el Sinaí | **Excelente (100%)**: *"Hola bendiciones a todos. 1. Moisés fue quien guió al pueblo. 2. Cruzaron el Mar Rojo. 3. Dios les entregó la ley en el monte Sinaí."* | `valido` | **5 pts** | Cubrió 3/3 puntos esperados. Score: 0.92 -> 5/5 pts. |
| | | | **Media (66%)**: *"Buenas tardes, Moisés guió al pueblo de Israel y también cruzaron el Mar Rojo."* | `valido` | **3 pts** | Cubrió 2/3 puntos. Faltó: [Recibieron la ley en el Sinaí]. Score: 0.67 -> 3/5 pts. |
| | | | **Nula (0%)**: *"Hola grupo hoy no alcancé a repasar."* | `invalido` | **0 pts** | Cubrió 0/3 puntos. Faltantes todos los elementos. Score: 0.00 -> 0/5 pts. |
| **Domingo**<br>*(Día de Descanso)* | N/A | N/A | Cualquier mensaje | **Error** | **HTTP 400** | *"Día de la semana 'domingo' no es válido. Domingo es día de descanso."* |

---

## 🔍 Detalle Técnico por Petición JSON

A continuación se muestra cómo se ve cada ejemplo técnicamente cuando la aplicación n8n consulta el servidor RAG:

### 1. Ejemplo Lunes (VÁLIDO)
- **Request Body**:
```json
{
  "dia_semana": "lunes",
  "pregunta": "¿Qué enseñanza práctica te deja el pasaje de hoy sobre el amor al prójimo?",
  "respuesta_esperada": "Debemos amar a nuestro prójimo con acciones verdaderas y no solo de palabra.",
  "respuesta_usuario": "Hola grupo buenos días, la enseñanza es que hay que demostrar el amor al prójimo con obras reales y no solo hablando."
}
```
- **Response Body**:
```json
{
  "veredicto": "valido",
  "similitud": 0.725,
  "puntos": 1,
  "explicacion": "Respuesta aceptada. Captura la idea central de la pregunta (similitud: 0.73)."
}
```

---

### 2. Ejemplo Martes (VÁLIDO)
- **Request Body**:
```json
{
  "dia_semana": "martes",
  "pregunta": "¿Quién fue el personaje que lideró al pueblo a través del Mar Rojo?",
  "respuesta_esperada": "Moisés",
  "respuesta_usuario": "Buenas tardes hermano, la respuesta al reto de hoy es Moisés."
}
```
- **Response Body**:
```json
{
  "veredicto": "valido",
  "similitud": 1.0,
  "puntos": 2,
  "explicacion": "Dato clave ('Moisés') identificado correctamente en la respuesta."
}
```

---

### 3. Ejemplo Miércoles (VÁLIDO)
- **Request Body**:
```json
{
  "dia_semana": "miercoles",
  "pregunta": "Menciona 3 frutos del Espíritu Santo.",
  "respuesta_esperada": "amor, gozo, paz",
  "respuesta_usuario": "Bendiciones a todos, mis respuestas son: amor, gozo y paz"
}
```
- **Response Body**:
```json
{
  "veredicto": "valido",
  "similitud": 1.0,
  "puntos": 2,
  "explicacion": "Contiene 3 de 3 elementos esperados (mínimo requerido: 2)."
}
```

---

### 4. Ejemplo Jueves (VÁLIDO)
- **Request Body**:
```json
{
  "dia_semana": "jueves",
  "pregunta": "Completa el versículo: 'El Señor es mi pastor...'",
  "respuesta_esperada": "nada me faltará",
  "respuesta_usuario": "Amén hermanos, nada me faltará"
}
```
- **Response Body**:
```json
{
  "veredicto": "valido",
  "similitud": 1.0,
  "puntos": 1,
  "explicacion": "Completa correctamente la idea planteada (similitud: 1.00)."
}
```

---

### 5. Ejemplo Viernes (VÁLIDO)
- **Request Body**:
```json
{
  "dia_semana": "viernes",
  "pregunta": "Reto Sorpresa: Explica qué hizo Abraham cuando Dios probó su fe.",
  "respuesta_esperada": "Abraham estuvo dispuesto a obedecer a Dios y ofrecer a su hijo Isaac.",
  "respuesta_usuario": "Buenas noches hermanos, la respuesta es que Abraham demostró su fe obedeciendo a Dios al ofrecer a Isaac."
}
```
- **Response Body**:
```json
{
  "veredicto": "valido",
  "similitud": 0.78,
  "puntos": 2,
  "explicacion": "Respuesta válida para el reto sorpresa (similitud: 0.78)."
}
```

---

### 6. Ejemplo Sábado (5 Puntos vs 3 Puntos vs 0 Puntos)

#### 🥇 5 Puntos (Excelente)
- **Request Body**:
```json
{
  "dia_semana": "sabado",
  "pregunta": "Resume los 3 puntos principales del Éxodo de Israel.",
  "respuesta_esperada": "1. Moisés guió al pueblo\n2. Cruzaron el Mar Rojo\n3. Recibieron la ley en el Sinaí",
  "respuesta_usuario": "Hola bendiciones a todos. 1. Moisés fue quien guió al pueblo. 2. Cruzaron el Mar Rojo. 3. Dios les entregó la ley en el monte Sinaí."
}
```
- **Response Body**:
```json
{
  "veredicto": "valido",
  "similitud": 0.92,
  "puntos": 5,
  "explicacion": "Elementos cubiertos (3/3): [Moisés guió al pueblo, Cruzaron el Mar Rojo, Recibieron la ley en el Sinaí] | Todos los elementos fueron cubiertos. Score: 0.92 -> 5/5 puntos."
}
```

#### 🥈 3 Puntos (Parcial)
- **Request Body**:
```json
{
  "dia_semana": "sabado",
  "pregunta": "Resume los 3 puntos principales del Éxodo de Israel.",
  "respuesta_esperada": "1. Moisés guió al pueblo\n2. Cruzaron el Mar Rojo\n3. Recibieron la ley en el Sinaí",
  "respuesta_usuario": "Buenas tardes, Moisés guió al pueblo de Israel y también cruzaron el Mar Rojo."
}
```
- **Response Body**:
```json
{
  "veredicto": "valido",
  "similitud": 0.6667,
  "puntos": 3,
  "explicacion": "Elementos cubiertos (2/3): [Moisés guió al pueblo, Cruzaron el Mar Rojo] | Faltantes: [Recibieron la ley en el Sinaí]. Score: 0.67 -> 3/5 puntos."
}
```

---

### 7. Ejemplo Domingo (Día no válido -> Error 400)
- **Request Body**:
```json
{
  "dia_semana": "domingo",
  "pregunta": "Pregunta de descanso",
  "respuesta_esperada": "Descanso",
  "respuesta_usuario": "Hola grupo"
}
```
- **Response Body (HTTP 400 Bad Request)**:
```json
{
  "detail": "Día de la semana 'domingo' no es válido. Debe ser uno de: lunes, martes, miercoles, jueves, viernes, sabado."
}
```
