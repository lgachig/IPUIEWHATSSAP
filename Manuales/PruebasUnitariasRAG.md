# Guía de Pruebas Unitarias e Integración del Motor RAG (rag-server)

Este documento detalla los casos de prueba unitarios y de integración para validar el funcionamiento del motor de verificación bíblica RAG en **MODO ÍNTEGRO**.

---

## 1. Preparación del Entorno de Pruebas

Asegúrate de que el servidor esté activo ejecutando en la terminal:

```bash
cd rag-server
python -m uvicorn app.main:app --port 8000
```

---

## 2. Casos de Prueba con `curl`

### Caso A: Enviar un Versículo VÁLIDO de la lectura del día (Texto escrito completo)
- **Fecha de prueba:** `2026-09-02`
- **Lectura del día programada:** `1 Pedro 3–4`
- **Texto enviado:** `"Puesto que Cristo ha padecido por nosotros en la carne, vosotros también armaos del mismo pensamiento"` (1 Pedro 4:1)

```bash
curl -X POST http://127.0.0.1:8000/verificar-lectura \
  -H "Content-Type: application/json" \
  -d '{
    "telefono": "+573001234567",
    "texto": "Puesto que Cristo ha padecido por nosotros en la carne, vosotros también armaos del mismo pensamiento",
    "fecha": "2026-09-02"
  }'
```

**Resultado esperado:**
```json
{
  "veredicto": "valido",
  "metodo": "embedding",
  "similitud": 0.891,
  "match": "1 Pedro 4:1",
  "coincide_con_hoy": true
}
```

---

### Caso B: Enviar SOLO LA CITA BÍBLICA VÁLIDA del día (`1 Pedro 4:1`)
- **Fecha de prueba:** `2026-09-02` (Lectura programada: `1 Pedro 3–4`)
- **Texto enviado:** `"1 Pedro 4:1"`

```bash
curl -X POST http://127.0.0.1:8000/verificar-lectura \
  -H "Content-Type: application/json" \
  -d '{
    "telefono": "+573001234567",
    "texto": "1 Pedro 4:1",
    "fecha": "2026-09-02"
  }'
```

**Resultado esperado:**
```json
{
  "veredicto": "valido",
  "metodo": "cita_directa",
  "similitud": 1.0,
  "match": "1 Pedro 4:1",
  "coincide_con_hoy": true
}
```

---

### Caso C: Enviar SOLO LA CITA BÍBLICA de OTRO DÍA (`Génesis 1:1`)
- **Fecha de prueba:** `2026-09-02` (Lectura programada: `1 Pedro 3–4`)
- **Texto enviado:** `"Génesis 1:1"`

```bash
curl -X POST http://127.0.0.1:8000/verificar-lectura \
  -H "Content-Type: application/json" \
  -d '{
    "telefono": "+573001234567",
    "texto": "Génesis 1:1",
    "fecha": "2026-09-02"
  }'
```

**Resultado esperado:**
```json
{
  "veredicto": "invalido",
  "metodo": "cita_directa",
  "similitud": 1.0,
  "match": "Génesis 1:1",
  "coincide_con_hoy": false
}
```

---

### Caso D: Enviar un Versículo Bíblico VÁLIDO pero de OTRO DÍA (Texto escrito)
- **Fecha de prueba:** `2026-09-02` (Lectura programada: `1 Pedro 3–4`)
- **Texto enviado:** `"En el principio creo Dios los cielos y la tierra"` (Génesis 1:1)

```bash
curl -X POST http://127.0.0.1:8000/verificar-lectura \
  -H "Content-Type: application/json" \
  -d '{
    "telefono": "+573001234567",
    "texto": "En el principio creo Dios los cielos y la tierra",
    "fecha": "2026-09-02"
  }'
```

**Resultado esperado:**
```json
{
  "veredicto": "invalido",
  "metodo": "embedding",
  "similitud": 0.9895,
  "match": "Génesis 1:1",
  "coincide_con_hoy": false
}
```

---

### Caso E: Enviar un Mensaje NADA RELACIONADO (Texto no bíblico / Comentario)
- **Fecha de prueba:** `2026-09-02`
- **Texto enviado:** `"Hola grupo bendiciones hoy no alcancé a realizar mi lectura"`

```bash
curl -X POST http://127.0.0.1:8000/verificar-lectura \
  -H "Content-Type: application/json" \
  -d '{
    "telefono": "+573001234567",
    "texto": "Hola grupo bendiciones hoy no alcancé a realizar mi lectura",
    "fecha": "2026-09-02"
  }'
```

**Resultado esperado:**
```json
{
  "veredicto": "invalido",
  "metodo": "embedding",
  "similitud": 0.855,
  "match": "Génesis 1:2",
  "coincide_con_hoy": false
}
```

---

## 3. Script Automatizado de Pruebas Unitarias (`test_rag.py`)

Se incluye este script de pruebas en Python para validar automáticamente todos los casos del servidor.

### Ejecutar el test automatizado:

```bash
cd rag-server
./venv/bin/python test_rag.py
```
