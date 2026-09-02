# Manual de Implementación — MODO ÍNTEGRO

Guía paso a paso desde la instalación del entorno hasta la vinculación de WhatsApp y la conexión con n8n. Documenta el trabajo realizado en las épicas **IPUIEWV-5** (Infraestructura Docker) e **IPUIEWV-6** (Vinculación de WhatsApp).

---

## Índice

1. [Requisitos previos](#1-requisitos-previos)
2. [Instalación de Docker Desktop (macOS)](#2-instalación-de-docker-desktop-macos)
3. [Estructura del proyecto](#3-estructura-del-proyecto)
4. [Configuración de docker-compose.yml](#4-configuración-de-docker-composeyml)
5. [Variables de entorno (.env)](#5-variables-de-entorno-env)
6. [.gitignore y control de versiones](#6-gitignore-y-control-de-versiones)
7. [Levantar los servicios](#7-levantar-los-servicios)
8. [Validar la instalación](#8-validar-la-instalación)
9. [Verificar volúmenes persistentes](#9-verificar-volúmenes-persistentes)
10. [Crear la instancia de WhatsApp en Evolution API](#10-crear-la-instancia-de-whatsapp-en-evolution-api)
11. [Vincular el número por código QR](#11-vincular-el-número-por-código-qr)
12. [Validar la conexión con un mensaje de prueba](#12-validar-la-conexión-con-un-mensaje-de-prueba)
13. [Configurar el webhook hacia n8n](#13-configurar-el-webhook-hacia-n8n)
14. [Flujo de ramas Git usado](#14-flujo-de-ramas-git-usado)
15. [Solución de problemas comunes](#15-solución-de-problemas-comunes)

---

## 1. Requisitos previos

- macOS 12 (Monterey) o superior
- Cuenta de WhatsApp dedicada al proyecto (recomendado no usar tu número personal)
- Acceso a Terminal
- Cuenta de GitHub/GitLab para el repositorio

---

## 2. Instalación de Docker Desktop (macOS)

1. Verifica el chip de tu Mac: menú Apple → **Acerca de este Mac** (Apple Silicon o Intel).
2. Descarga el instalador correspondiente desde [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/).
3. Abre el `.dmg` y arrastra Docker a **Aplicaciones**.
4. Abre Docker Desktop, acepta los permisos del sistema y espera a que el ícono de la ballena deje de animarse.
5. Valida la instalación:
   ```bash
   docker --version
   docker compose version
   docker run hello-world
   ```

---

## 3. Estructura del proyecto

```
modo-integro/
├── docker-compose.yml
├── .env                  # Real, NO se sube a git
├── .env.example          # Plantilla segura, sí se sube
├── .gitignore
├── README.md
├── MANUAL.md
└── scripts/              # (opcional) pruebas funcionales / CI
```

Crear la carpeta local:
```bash
mkdir -p ~/modo-integro && cd ~/modo-integro
git init
```

---

## 4. Configuración de docker-compose.yml

Servicios definidos:

| Servicio | Imagen | Puerto | Función |
|---|---|---|---|
| `n8n` | `n8nio/n8n:latest` | 5678 | Orquestador de flujos |
| `evolution-api` | `atendai/evolution-api:latest` | 8080 | Puente con WhatsApp |

Ambos comparten la red interna `modo_integro_net` y usan volúmenes con nombre para persistencia (`n8n_data`, `evolution_instances`, `evolution_store`).

> El archivo completo está en la raíz del proyecto: `docker-compose.yml`.

---

## 5. Variables de entorno (.env)

Copiar la plantilla y completar valores propios:
```bash
cp .env.example .env
```

Variables clave:

| Variable | Descripción |
|---|---|
| `N8N_BASIC_AUTH_USER` / `PASSWORD` | Credenciales de acceso al editor de n8n |
| `EVOLUTION_API_KEY` | Clave global de autenticación de Evolution API (**la inventas tú**, no la entrega nadie) |
| `EVOLUTION_SERVER_URL` | URL interna de Evolution API |
| `N8N_WEBHOOK_URL` | URL base de los webhooks de n8n |

Generar una clave segura:
```bash
openssl rand -hex 32
```

**Nunca subas el `.env` real a git.**

---

## 6. .gitignore y control de versiones

El `.gitignore` excluye: `.env`, datos persistentes de Docker, sesiones/QR de WhatsApp, backups, logs y archivos de sistema/editor. Ver archivo completo en la raíz.

Primer commit:
```bash
git add docker-compose.yml .gitignore .env.example README.md
git commit -m "feat(IPUIEWV-5): configuracion inicial Docker (n8n + Evolution API)"
git push -u origin feature/IPUIEWV-5-configuracion-docker-compose
```

---

## 7. Levantar los servicios

```bash
cd ~/modo-integro
docker compose config      # valida sintaxis y variables
docker compose up -d       # levanta los contenedores
docker compose ps          # confirma que ambos estén "Up"
```

---

## 8. Validar la instalación

```bash
docker compose logs -f n8n
docker compose logs -f evolution-api
```

- n8n: abrir `http://localhost:5678` → debe pedir usuario/contraseña y cargar el editor.
- Evolution API: abrir `http://localhost:8080` o `curl http://localhost:8080` → debe responder (no rechazar la conexión).

Confirmar la red interna:
```bash
docker network inspect modo_integro_net
```

---

## 9. Verificar volúmenes persistentes

```bash
docker volume ls
```

Prueba de persistencia:
1. Crear un workflow de prueba en n8n.
2. `docker compose restart n8n` → el workflow debe seguir ahí.
3. `docker compose down && docker compose up -d` → el workflow debe seguir ahí incluso tras recrear el contenedor.

> `docker compose down` **no borra volúmenes**. Solo `docker compose down -v` lo hace — usar con cuidado.

---

## 10. Crear la instancia de WhatsApp en Evolution API

1. Abrir el Manager: `http://localhost:8080/manager` (pide el `EVOLUTION_API_KEY`).
2. Clic en **Create Instance / New Instance**.
3. Completar el formulario:
   - **Name**: identificador sin espacios, ej. `modo-integro-grupo`.
   - **Channel**: `Baileys` (protocolo tipo WhatsApp Web, gratuito). *No usar "WhatsApp Cloud API"* (requiere cuenta Meta Business aprobada).
   - **Token**: se puede generar con `openssl rand -hex 16` si el formulario lo exige.
   - **Number**: dejar vacío (solo aplica al canal Cloud API).
4. Guardar. La instancia queda creada en estado `close` (aún no vinculada).

Confirmar vía API:
```bash
curl -H "apikey: TU_API_KEY" http://localhost:8080/instance/fetchInstances
```

---

## 11. Vincular el número por código QR

1. En el Manager, abrir la instancia y localizar el código QR.
2. En el celular: WhatsApp → **Ajustes → Dispositivos vinculados → Vincular un dispositivo**.
3. Escanear el QR mostrado en pantalla.
4. El estado debe cambiar de `close` a `open`.

Confirmar vía API:
```bash
curl -H "apikey: TU_API_KEY" \
  http://localhost:8080/instance/connectionState/modo-integro-grupo
```

### Problemas comunes al vincular
- **QR expirado**: expira en 20–60s, regenerarlo y escanear rápido.
- **Límite de dispositivos**: WhatsApp permite máx. 4–5 vinculados; cerrar sesión en alguno si es necesario.
- **Imagen desactualizada**: `docker compose pull evolution-api && docker compose up -d evolution-api`.

---

## 12. Validar la conexión con un mensaje de prueba

Envío de prueba vía API:
```bash
curl -X POST http://localhost:8080/message/sendText/modo-integro-grupo \
  -H "apikey: TU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"number":"593XXXXXXXXX@s.whatsapp.net","text":"Prueba MODO INTEGRO - conexion validada"}'
```

Una respuesta con `"status":"PENDING"` confirma el envío. Verificar que el mensaje llegó al celular destino.

---

## 13. Configurar el webhook hacia n8n

### 13.1 En n8n
1. Crear un workflow nuevo, agregar un nodo **Webhook**.
2. Configurar método **POST** y un **Path** simple, ej. `whatsapp-eventos`.
3. **Guardar** el workflow con un nombre descriptivo.
4. **Activar el workflow** (toggle "Active", esquina superior derecha) — paso obligatorio, sin esto la URL de producción no responde.
5. Abrir el nodo Webhook y copiar la pestaña **"Production URL"** (nunca la de "Test URL", que trae el sufijo `-test` y solo sirve una vez con el editor abierto).

### 13.2 En Evolution API
Como n8n y Evolution API están en **contenedores distintos** dentro de la misma red Docker, la URL debe usar el **nombre del servicio** (`n8n`), nunca `localhost`.

Configurar el webhook por API (más confiable que la interfaz visual del Manager, que puede fallar al guardar los toggles de eventos):

```bash
curl -X POST http://localhost:8080/webhook/set/modo-integro-grupo -H "apikey: TU_API_KEY" -H "Content-Type: application/json" -d '{"webhook":{"enabled":true,"url":"http://n8n:5678/webhook/whatsapp-eventos","webhookByEvents":false,"events":["MESSAGES_UPSERT"]}}'
```

> ⚠️ Ejecutar el comando en **una sola línea**. Los saltos de línea con `\` en Terminal pueden agregar espacios que rompen el comando.

Verificar lo guardado:
```bash
curl -H "apikey: TU_API_KEY" http://localhost:8080/webhook/find/modo-integro-grupo
```

### 13.3 Prueba end-to-end
Enviar un mensaje real desde el WhatsApp vinculado y revisar la pestaña **"Executions"** en n8n (`Editor → Executions`). Debe aparecer una ejecución nueva con el payload del mensaje.

---

## 14. Flujo de ramas Git usado

Cada tarea del backlog de Jira corresponde a su propio código (`IPUIEWV-XX`). Cuando varias tareas pertenecen a la **misma épica**, se agrupan en una sola rama; al pasar a una épica distinta, se abre una rama nueva.

```bash
# Ejemplo: una tarea puntual
git checkout -b feature/IPUIEWV-34-webhook-evolution-n8n
git add .
git commit -m "feat(IPUIEWV-34): configurar webhook de Evolution API hacia n8n"
git push -u origin feature/IPUIEWV-34-webhook-evolution-n8n
```

Ramas creadas hasta ahora:

| Rama | Épica/Tarea |
|---|---|
| `feature/IPUIEWV-5-configuracion-docker-compose` | Infraestructura Docker (varias tareas) |
| `feature/IPUIEWV-28-red-interna-docker` | Red interna Docker |
| `feature/IPUIEWV-29-levantar-contenedores-logs` | Levantar contenedores y logs |
| `feature/IPUIEWV-30-dominio-reverse-proxy-ssl` | Dominio/SSL (pendiente, solo para producción) |
| `feature/IPUIEWV-31-generar-instancia-evolution-api` | Generar instancia WhatsApp |
| `feature/IPUIEWV-32-vincular-numero-qr` | Vincular número por QR |
| `feature/IPUIEWV-33-validar-conexion-envio-prueba` | Validar conexión con mensaje de prueba |
| `feature/IPUIEWV-34-webhook-evolution-n8n` | Webhook Evolution API → n8n |

---

## 15. Solución de problemas comunes

| Síntoma | Causa probable | Solución |
|---|---|---|
| No se puede escanear el QR | QR expirado o imagen desactualizada | Regenerar QR / `docker compose pull evolution-api` |
| `Nothing here yet` en Executions de n8n | Webhook usando URL de prueba (`-test`) o workflow no activado | Usar Production URL + activar el workflow |
| `401 Unauthorized` en curl | Falta el header `apikey` o comando roto por saltos de línea | Verificar headers y ejecutar el comando en una sola línea |
| Evolution API no puede llamar a n8n | Se usó `localhost` en vez de `n8n` en la URL del webhook | Usar el nombre del servicio Docker (`n8n`), no `localhost` |
| Los toggles de eventos no se guardan en el Manager | Bug conocido de la interfaz visual | Configurar el webhook vía `curl` directo a la API |
| Workflow pierde datos al reiniciar | Volúmenes no persistentes | Verificar que `docker-compose.yml` defina volúmenes con nombre, no usar `down -v` accidentalmente |

---

*Última actualización: 1 de septiembre de 2026 — cubre las épicas IPUIEWV-5 e IPUIEWV-6.*
