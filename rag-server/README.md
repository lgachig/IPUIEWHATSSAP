# MODO ÍNTEGRO — Motor RAG de verificación bíblica

Servicio independiente que n8n consulta para verificar si un mensaje
del grupo de WhatsApp corresponde a la lectura bíblica del día,
usando la Biblia completa vectorizada como fuente de verdad y
llamando a Gemini solo como último recurso en casos ambiguos.

## Arquitectura (3 capas en cascada)

1. **Exacta/difusa** (`rapidfuzz`, gratis, instantánea): compara el
   mensaje contra el texto exacto de la lectura de hoy.
2. **Semántica** (embeddings locales + `pgvector` en Supabase, gratis):
   si la capa 1 no fue concluyente, busca el versículo más parecido
   en TODA la Biblia y compara su referencia contra la de hoy.
3. **LLM fallback** (Gemini, con costo): solo si la similitud de la
   capa 2 cae en zona ambigua (entre `UMBRAL_BAJO` y `UMBRAL_ALTO`).

## Estado actual — qué falta antes de poder probar de punta a punta

- [ ] **Subir el PDF real de la Biblia.** El de la captura tiene un
  layout particular (números de versículo en el margen derecho, no
  pegados al texto). `ingest_biblia.py` trae el armazón del parser
  pero las constantes `UMBRAL_X_MARGEN_DERECHO` y
  `UMBRAL_TAMANO_FUENTE_NUMERO_MAX` están sin calibrar — hay que
  correr el snippet de calibración que está en el docstring del
  script contra una página real para fijar esos valores.
- [ ] Crear el proyecto en Supabase y correr `schema.sql`.
- [ ] Completar `.env` (copiar de `.env.example`).
- [ ] Poblar `lecturas_diarias` con el calendario del mes (aunque sea
  a mano al inicio, para poder probar `/verificar-lectura`).

## Pasos para levantarlo localmente

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # y completar con tus credenciales

# 1. Calibrar y extraer el PDF (ver docstring de ingest_biblia.py)
python ingest_biblia.py ruta/a/biblia.pdf
#   -> revisar biblia_extraida.json a mano (muestra al azar de ~20-30
#      versículos comparados contra el PDF) antes de continuar

# 2. Vectorizar y subir a Supabase (una sola vez, ~31,000 filas)
python vectorize_biblia.py biblia_extraida.json

# 3. Levantar el servidor
uvicorn app.main:app --reload
```

## Probar el endpoint

```bash
curl -X POST http://localhost:8000/verificar-lectura \
  -H "Content-Type: application/json" \
  -d '{
        "telefono": "593999999999",
        "texto": "En el principio creó Dios los cielos y la tierra...",
        "fecha": "2026-09-02"
      }'
```

Respuesta esperada:

```json
{
  "veredicto": "valido",
  "metodo": "exacto",
  "similitud": 0.97,
  "match": "Génesis 1:1",
  "coincide_con_hoy": true
}
```

## Integración con n8n

Nodo HTTP Request, método `POST`, hacia
`http://rag-server:8000/verificar-lectura` (nombre del servicio en la
red interna de Docker si están en el mismo `docker-compose.yml`).
n8n sigue siendo dueño de escribir en `Puntajes`/`Logs` — este
servicio solo devuelve el veredicto.

## Calibración de umbrales

`UMBRAL_ALTO` y `UMBRAL_BAJO` en `.env` están en valores de partida
razonables (0.90 / 0.75) pero **hay que ajustarlos con mensajes
reales del grupo** una vez empiecen las pruebas — hay una tabla
`verificaciones_rag` pensada justo para eso: revisar ahí cuántos
casos cayeron en cada método y si el veredicto fue correcto.
