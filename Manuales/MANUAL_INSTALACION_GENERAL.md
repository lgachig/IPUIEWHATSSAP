# Manual General de Instalación y Replicación — MODO ÍNTEGRO

Este manual describe detalladamente los pasos necesarios para instalar, configurar y replicar desde cero todo el ecosistema de **MODO ÍNTEGRO**: la base de datos en Supabase, el servidor RAG e IA en Python, la infraestructura contenerizada con Docker Compose (n8n y Evolution API) y la vinculación de WhatsApp.

---

## 📋 Índice

1. [Arquitectura del Sistema](#1-arquitectura-del-sistema)
2. [Requisitos Previos](#2-requisitos-previos)
3. [Estructura del Proyecto](#3-estructura-del-proyecto)
4. [Paso 1: Variables de Entorno](#paso-1-variables-de-entorno)
5. [Paso 2: Configuración de la Base de Datos en Supabase](#paso-2-configuración-de-la-base-de-datos-en-supabase)
6. [Paso 3: Configuración del Servidor RAG e Ingesta Bíblica](#paso-3-configuración-del-servidor-rag-e-ingesta-bíblica)
7. [Paso 4: Despliegue de Servicios Docker (n8n y Evolution API)](#paso-4-despliegue-de-servicios-docker-n8n-y-evolution-api)
8. [Paso 5: Vinculación de la Instancia de WhatsApp](#paso-5-vinculación-de-la-instancia-de-whatsapp)
9. [Paso 6: Conexión del Webhook de Evolution API con n8n](#paso-6-conexión-del-webhook-de-evolution-api-con-n8n)
10: [Paso 7: Pruebas y Verificación del Sistema](#paso-7-pruebas-y-verificación-del-sistema)
11. [Solución de Problemas Comunes](#solución-de-problemas-comunes)

---

## 1. Arquitectura del Sistema

El ecosistema **MODO ÍNTEGRO** integra los siguientes componentes:

```
                                  ┌──────────────────────────┐
                                  │      WhatsApp User       │
                                  └────────────┬─────────────┘
                                               │
                                               ▼
┌─────────────────┐  Webhook HTTP  ┌──────────────────────────┐
│   n8n Workflow  │ ◄───────────── │ Evolution API (WhatsApp) │
└────────┬────────┘                └──────────────────────────┘
         │
         ├──────────────────────────┐
         ▼                          ▼
┌──────────────────┐       ┌──────────────────┐
│  RAG API Server  │       │  Supabase (DB)   │
│ (FastAPI/Python) │       │   PostgreSQL +   │
└────────┬─────────┘       │     pgvector     │
         │                 └────────┬─────────┘
         └──────────────────────────┘
```

* **Evolution API**: Interfaz puente HTTP/REST para enviar y recibir mensajes de WhatsApp Web.
* **n8n**: Orquestador de automatización de flujos diarios (publicaciones matutinas, recepción de respuestas, gestión de rachas y puntuación).
* **Supabase (PostgreSQL)**: Almacena usuarios, puntajes, lecturas diarias, actividades, comodines, rachas y logs.
* **RAG Server (FastAPI / PyTorch)**: Servidor Python con modelos de embeddings (`multilingual-e5-small`) y validación de actividades bíblicas mediante similitud de vectores y LLM.

---

## 2. Requisitos Previos

Asegúrate de contar con los siguientes elementos instalados en el sistema:

1. **Docker Desktop** (macOS, Linux o Windows) con `docker compose` v2+.
2. **Python 3.10** o superior y `pip`.
3. **Git** para control de versiones.
4. **Proyecto en Supabase** (con extensión `pgvector` activada y clave Service Role).
5. **Número de celular dedicado** a WhatsApp para el bot.

---

## 3. Estructura del Proyecto

La estructura consolidada y limpia del proyecto es la siguiente:

```
PROYECTO WHATSSAP IPUIE/
├── docker-compose.yml              # Definición de contenedores n8n y Evolution API
├── .env.example                    # Plantilla de variables de entorno globales
├── README.md                       # Resumen del proyecto y referencias
├── Manuales/                       # Guías y documentación técnica
│   └── MANUAL_INSTALACION_GENERAL.md
├── supabase/
│   └── migrations/                 # Estructura SQL limpia de la base de datos
│       ├── 20260902032316_create_usuarios.sql
│       ├── 20260902033439_create_puntajes.sql
│       ├── 20260902033844_create_rachas.sql
│       ├── 20260902034142_create_comodines.sql
│       ├── 20260902034403_create_logs.sql
│       ├── 20260902035218_configurar_rls.sql
│       ├── 20260902055943_lecturas_diarias.sql
│       └── 20260902060023_cargar_lecturas_diarias.sql
└── rag-server/                     # Motor RAG e IA para validación de actividades
    ├── app/                        # Aplicación FastAPI
    ├── schema.sql                  # Esquema pgvector y función match_biblia
    ├── ingest_biblia.py            # Script para vectorizar e ingerir la Biblia RVR
    ├── test_actividades.py         # Pruebas unitarias de actividades
    ├── test_rag.py                 # Pruebas unitarias del motor RAG
    └── requirements.txt            # Dependencias Python
```

---

## Paso 1: Variables de Entorno

1. **Configurar el archivo `.env` principal**:
   ```bash
   cp .env.example .env
   ```
   Edita `.env` con tus claves reales:
   ```env
   # n8n
   N8N_BASIC_AUTH_USER=admin
   N8N_BASIC_AUTH_PASSWORD=TuPasswordSeguro123!
   
   # Evolution API
   EVOLUTION_API_KEY=TuApiKeySecretaDeEvolution
   
   # Supabase
   SUPABASE_URL=https://tu-proyecto.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=tu-service-role-key-secreta
   ```

2. **Configurar el archivo `.env` en `rag-server`**:
   ```bash
   cp rag-server/.env.example rag-server/.env
   ```
   Asegúrate de incluir las credenciales de Supabase en `rag-server/.env`:
   ```env
   SUPABASE_URL=https://tu-proyecto.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=tu-service-role-key-secreta
   ```

---

## Paso 2: Configuración de la Base de Datos en Supabase

Ejecuta las migraciones en el SQL Editor de tu dashboard de Supabase (o vía CLI) en el siguiente orden:

1. **Tablas de Usuarios y Sistema**:
   * `supabase/migrations/20260902032316_create_usuarios.sql`
   * `supabase/migrations/20260902033439_create_puntajes.sql`
   * `supabase/migrations/20260902033844_create_rachas.sql`
   * `supabase/migrations/20260902034142_create_comodines.sql`
   * `supabase/migrations/20260902034403_create_logs.sql`
   * `supabase/migrations/20260902035218_configurar_rls.sql`

2. **Estructura y Carga de Lecturas Diarias**:
   * `supabase/migrations/20260902055943_lecturas_diarias.sql`: Crea la tabla `lecturas_diarias` con la columna `actividad` integrada de forma nativa.
   * `supabase/migrations/20260902060023_cargar_lecturas_diarias.sql`: Carga las 26 lecturas programadas con todas las actividades, preguntas reto y respuestas esperadas.

3. **Esquema Vectorial RAG**:
   * Executa `rag-server/schema.sql` en Supabase para crear la extensión `vector` (pgvector), la tabla `biblia_vectorizada`, la función RPC `match_biblia` y los logs de verificación.

---

## Paso 3: Configuración del Servidor RAG e Ingesta Bíblica

1. **Crear entorno virtual e instalar dependencias**:
   ```bash
   cd rag-server
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **Vectorizar e Ingerir la Biblia en Supabase**:
   Ejecuta el script de ingesta (este proceso procesará los versículos de la Biblia y generará embeddings de 384 dimensiones):
   ```bash
   python ingest_biblia.py
   ```

3. **Ejecutar Pruebas Unitarias de Validación**:
   Verifica que los algoritmos de evaluadores de actividades funcionen correctamente:
   ```bash
   python -m unittest test_actividades.py
   python test_rag.py
   ```

4. **Iniciar el Servidor RAG en Desarrollo**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   El servidor estará disponible en `http://localhost:8000` (documentación Swagger en `/docs`).

---

## Paso 4: Despliegue de Servicios Docker (n8n y Evolution API)

1. **Validar archivo Docker Compose**:
   ```bash
   docker compose config
   ```

2. **Levantar los contenedores**:
   ```bash
   docker compose up -d
   ```

3. **Verificar estado de los contenedores**:
   ```bash
   docker compose ps
   ```
   * **n8n**: `http://localhost:5678`
   * **Evolution API**: `http://localhost:8080`

---

## Paso 5: Vinculación de la Instancia de WhatsApp

1. Abre el gestor de Evolution API en `http://localhost:8080/manager` e ingresa tu `EVOLUTION_API_KEY`.
2. Crea una nueva instancia con el nombre `modo-integro-grupo` y selecciona el canal **Baileys**.
3. Abre el código QR generado en pantalla.
4. En tu teléfono WhatsApp: **Ajustes → Dispositivos vinculados → Vincular un dispositivo** y escanea el código QR.
5. Confirma el estado de conexión vía API:
   ```bash
   curl -H "apikey: TU_EVOLUTION_API_KEY" \
     http://localhost:8080/instance/connectionState/modo-integro-grupo
   ```
   Debe responder `"state": "open"`.

---

## Paso 6: Conexión del Webhook de Evolution API con n8n

Conecta el flujo de WhatsApp entrante hacia n8n ejecutando la llamada REST (sustituyendo `TU_EVOLUTION_API_KEY`):

```bash
curl -X POST http://localhost:8080/webhook/set/modo-integro-grupo \
  -H "apikey: TU_EVOLUTION_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "webhook": {
      "enabled": true,
      "url": "http://n8n:5678/webhook/whatsapp-eventos",
      "webhookByEvents": false,
      "events": ["MESSAGES_UPSERT"]
    }
  }'
```

> **Importante**: Se usa el nombre de servicio Docker `http://n8n:5678` porque ambos contenedores están dentro de la misma red interna `modo_integro_net`.

---

## Paso 7: Pruebas y Verificación del Sistema

1. **Prueba de Verificación de Actividades (RAG Server)**:
   Envía una solicitud POST a `http://localhost:8000/verificar-actividad`:
   ```json
   {
     "actividad": "detective_biblico",
     "pregunta": "¿Quién fue el personaje que lideró al pueblo a través del Mar Rojo?",
     "respuesta_esperada": "Moisés",
     "respuesta_usuario": "La respuesta es Moisés"
   }
   ```
   Respuesta esperada: `veredicto: "valido"`, `puntos: 2`.

2. **Prueba de Envío de Mensaje por WhatsApp**:
   ```bash
   curl -X POST http://localhost:8080/message/sendText/modo-integro-grupo \
     -H "apikey: TU_EVOLUTION_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"number":"593XXXXXXXXX@s.whatsapp.net","text":"Prueba de instalación MODO ÍNTEGRO exitosa"}'
   ```

---

## Solución de Problemas Comunes

| Problema | Causa Probable | Solución |
|---|---|---|
| `extension "vector" does not exist` | pgvector no activado en PostgreSQL/Supabase | Ejecutar `CREATE EXTENSION IF NOT EXISTS vector;` en el SQL Editor de Supabase. |
| Error `401 Unauthorized` en Evolution API | Header `apikey` faltante o incorrecto | Verificar que el valor del header `apikey` coincida exactamente con `EVOLUTION_API_KEY` del `.env`. |
| Error al conectar Webhook a n8n | Se usó `localhost` en lugar de `n8n` | Asegúrate de usar la URL `http://n8n:5678/webhook/...` en la configuración del webhook. |
| QR Code no se escanea o expira rápido | Sesión desactualizada o tiempo agotado | Reinicia el contenedor con `docker compose restart evolution-api` y genera un nuevo QR. |
| `0/26 lecturas` | Migración SQL de lecturas no ejecutada | Ejecutar la migración `20260902060023_cargar_lecturas_diarias.sql`. |

---

*Manual de Instalación y Replicación General — MODO ÍNTEGRO.*
