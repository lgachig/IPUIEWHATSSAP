# MODO ÍNTEGRO

Sistema automatizado con **n8n** y **Evolution API** para gestionar una dinámica diaria de lectura, retos y puntuación dentro de un grupo de WhatsApp.

## 📋 Descripción

MODO ÍNTEGRO envía automáticamente cada mañana un versículo y una lectura al grupo de WhatsApp, reconoce las respuestas de los participantes dentro de una ventana horaria estricta (09:00–09:05), asigna puntos según el tipo de actividad, gestiona rachas, bonificaciones y comodines, y ofrece a los administradores un panel de control y una bitácora de errores en tiempo real.

## 🧱 Stack técnico

- **n8n** — orquestador de flujos de automatización.
- **Evolution API** — puente entre WhatsApp y n8n (mensajería vía webhooks).
- **Supabase (PostgreSQL)** — base de datos relacional (usuarios, puntajes, rachas, comodines, logs).
- **Docker / Docker Compose** — entorno de despliegue contenerizado.
- **Dashboard** (Google Sheets / Looker Studio o similar) — visualización de resultados para el administrador.

## 👥 Roles del sistema

| Rol | Puede hacer |
|---|---|
| **Usuario / Participante** | Recibir contenido diario, participar en retos, acumular puntos, usar comodines, consultar su estado (`!miestado`). |
| **Administrador** | Lanzar preguntas manuales, corregir participaciones, gestionar comodines, supervisar errores, ver el dashboard y el podio. |

## 🗂️ Estructura del proyecto

```
modo-integro/
├── docker-compose.yml   # Servicios n8n + Evolution API
├── .env.example         # Plantilla de variables de entorno (sin datos reales)
├── .env                 # Variables reales (NO se sube al repo)
├── .gitignore
└── README.md
```

## 🚀 Estado actual del desarrollo

Este proyecto sigue un backlog organizado en 4 sprints (ver Jira). Progreso actual:

- [x] Docker Desktop instalado (macOS)
- [x] `docker-compose.yml` con servicios n8n y Evolution API
- [x] `.gitignore` y `.env.example` configurados
- [ ] Definir variables de entorno reales (`.env`)
- [ ] Configurar volúmenes persistentes
- [ ] Configurar red interna Docker
- [ ] Levantar contenedores y validar logs
- [ ] Configurar dominio, reverse proxy y SSL

> Sprints siguientes: vinculación de WhatsApp, esquema en Supabase, envío diario automatizado, reconocimiento de respuestas y puntuación, comodines, dashboard de administrador, pruebas E2E y despliegue.

## ⚙️ Cómo levantar el entorno (local, en desarrollo)

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd modo-integro

# 2. Crear tu archivo de variables de entorno
cp .env.example .env
# Editar .env con tus valores reales

# 3. Validar la sintaxis del compose (aún no levanta nada)
docker compose config

# 4. Levantar los contenedores
docker compose up -d

# 5. Verificar que todo esté corriendo
docker compose ps
```

- n8n quedará disponible en: `http://localhost:5678`
- Evolution API quedará disponible en: `http://localhost:8080`

## 🔐 Seguridad

- Nunca subas el archivo `.env` real al repositorio (ya está en `.gitignore`).
- Las credenciales de WhatsApp (sesión/QR) y la API key de Evolution API son sensibles: no se comparten fuera del equipo.

## 📄 Licencia

Proyecto interno — uso restringido al equipo de desarrollo.
