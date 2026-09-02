# Procedimiento de Reconexión — MODO ÍNTEGRO

**Qué hacer si el bot deja de responder / la sesión de WhatsApp se cerró inesperadamente.**

Público: Developer o Scrum Master (no requiere conocimientos avanzados de Docker).

---

## 🔍 ¿Cómo saber si la sesión se cayó?

Señales de alerta:
- El grupo deja de recibir la lectura diaria o las respuestas automáticas.
- El celular vinculado muestra una notificación de WhatsApp: *"Se cerró la sesión de [nombre de la instancia]"*.
- En el Manager de Evolution API (`http://localhost:8080/manager`), el estado de la instancia ya no dice `open`, sino `close` o `connecting`.

---

## ✅ Procedimiento de reconexión (5 pasos)

### 1. Confirmar que los servicios están corriendo
Abrir Terminal y ejecutar:
```bash
docker compose ps
```
Ambos contenedores (`modo_integro_n8n` y `modo_integro_evolution_api`) deben decir **Up**. Si alguno no lo dice, ejecutar:
```bash
docker compose up -d
```

### 2. Revisar el estado de la instancia
```bash
curl -H "apikey: TU_API_KEY" \
  http://localhost:8080/instance/connectionState/modo-integro-grupo
```
Si responde `"state":"close"`, la sesión efectivamente se cerró y hay que volver a vincular.

### 3. Generar un nuevo código QR
1. Entrar al Manager: `http://localhost:8080/manager`.
2. Abrir la instancia `modo-integro-grupo`.
3. Seleccionar **Connect / Generate QR** — aparecerá un nuevo código QR.

> No es necesario borrar ni recrear la instancia. El nombre, el token y la configuración del webhook se mantienen intactos gracias al volumen persistente `evolution_instances`.

### 4. Escanear el QR desde el celular
En el celular vinculado al proyecto: **WhatsApp → Ajustes → Dispositivos vinculados → Vincular un dispositivo**, y escanear el nuevo QR.

### 5. Confirmar que todo volvió a funcionar
- El estado debe volver a `open`.
- Enviar un mensaje de prueba al grupo y confirmar que llega.
- Revisar en n8n (`Executions`) que el próximo mensaje entrante genere una ejecución nueva — esto confirma que el webhook sigue conectado sin necesidad de reconfigurarlo.

---

## ⚠️ Causas comunes de la caída de sesión

| Causa | Qué hacer |
|---|---|
| El celular vinculado se quedó sin batería o sin internet por mucho tiempo | Reconectar el celular a internet y repetir el procedimiento |
| Se vinculó WhatsApp Web en muchos dispositivos (límite alcanzado) | Cerrar sesión de un dispositivo no usado antes de reconectar |
| Se actualizó la app de WhatsApp del celular vinculado | Repetir el procedimiento normalmente |
| El contenedor de Evolution API se reinició o se actualizó la imagen | Verificar `docker compose ps` primero (paso 1) |
| Uso prolongado sin actividad (WhatsApp puede cerrar sesiones inactivas) | Repetir el procedimiento; no requiere intervención del developer |

---

## 📞 Si el problema persiste

Si después de 2-3 intentos el estado no vuelve a `open`, revisar los logs para un diagnóstico más profundo:
```bash
docker compose logs -f evolution-api
```
Y escalar al developer del proyecto con el mensaje de error exacto que aparezca ahí.

---

*Procedimiento documentado como parte de la tarea IPUIEWV-35 — Sprint 1, épica IPUIEWV-6.*
