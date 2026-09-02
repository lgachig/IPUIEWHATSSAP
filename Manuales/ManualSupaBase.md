# Base de datos — MODO ÍNTEGRO (Supabase)

Este documento describe el esquema de las tablas creadas en la épica **IPUIEWV-7 (Base de Datos)** y el flujo para publicar cambios de esquema (migraciones) hacia Supabase Cloud.

Proyecto: `IPUIEWV`
Project ref: `ypmpzikvlzrwioyaojgu`
Dashboard: https://supabase.com/dashboard/project/ypmpzikvlzrwioyaojgu

---

## 1. Esquema de tablas

### usuarios (IPUIEWV-38)
```sql
create table usuarios (
  id uuid primary key default gen_random_uuid(),
  nombre text not null,
  numero_telefono text not null unique,
  comodines_disponibles integer not null default 2,
  fecha_registro timestamptz not null default now(),
  rol text not null default 'usuario' check (rol in ('usuario', 'admin'))
);
```
Tabla raíz del sistema. Todas las demás tablas referencian a `usuarios.id`.

### puntajes (IPUIEWV-39)
```sql
create table puntajes (
  id uuid primary key default gen_random_uuid(),
  usuario_id uuid not null references usuarios(id) on delete cascade,
  fecha date not null,
  categoria text not null,
  puntos integer not null,
  valido boolean not null default true,
  motivo text
);
```
Relación `1—N` con `usuarios`. `motivo` se usa para registrar por qué una participación quedó inválida (fuera de horario, duplicado, formato incorrecto).

### rachas (IPUIEWV-40)
```sql
create table rachas (
  id uuid primary key default gen_random_uuid(),
  usuario_id uuid not null unique references usuarios(id) on delete cascade,
  racha_actual integer not null default 0,
  racha_maxima integer not null default 0,
  ultima_fecha_cumplida date
);
```
Relación `1—1` con `usuarios` (por eso `usuario_id` es `unique`): un solo contador de racha por usuario, no un historial de filas.

### comodines (IPUIEWV-41)
```sql
create table comodines (
  id uuid primary key default gen_random_uuid(),
  usuario_id uuid not null references usuarios(id) on delete cascade,
  mes text not null,
  cantidad_usada integer not null default 1,
  fecha_uso date not null default current_date,
  motivo text
);
```
Relación `1—N` con `usuarios`. Cada uso de comodín queda como una fila auditable.

### logs (IPUIEWV-42)
```sql
create table logs (
  id uuid primary key default gen_random_uuid(),
  fecha timestamptz not null default now(),
  tipo_evento text not null,
  descripcion text,
  usuario_id uuid references usuarios(id) on delete set null,
  nivel text not null default 'info' check (nivel in ('info', 'error'))
);
```
`usuario_id` es opcional (`on delete set null`) porque pueden existir logs de sistema sin usuario asociado (ej. fallo de un webhook de n8n o de Evolution API).

---

## 2. Requisitos previos (una sola vez por máquina)

```
supabase login
supabase link --project-ref ypmpzikvlzrwioyaojgu
```

`login` abre el navegador para autenticar la CLI. `link` conecta la carpeta local del repo con este proyecto de Supabase (pide la contraseña de la base de datos, no la de la cuenta).

---

## 3. Flujo para crear y publicar una migración nueva

Repite esto por cada tabla o cambio de esquema:

```bash
# 1. Crear una rama nueva a partir de main
git checkout main
git pull origin main
git checkout -b feature/IPUIEWV-XX-nombre-de-la-tarea

# 2. Generar el archivo de migración
supabase migration new nombre_del_cambio
# Crea: supabase/migrations/TIMESTAMP_nombre_del_cambio.sql

# 3. Editar ese archivo y pegar el SQL (create table / alter table / etc.)

# 4. Confirmar que está pendiente (solo aparece en "Local")
supabase migration list

# 5. Publicar el cambio en Supabase Cloud
supabase db push
# Responder "Y" cuando pregunte si aplicar las migraciones

# 6. Confirmar que ya quedó aplicada (ahora aparece también en "Remote")
supabase migration list

# 7. Verificar visualmente en el dashboard
# https://supabase.com/dashboard/project/ypmpzikvlzrwioyaojgu/editor

# 8. Subir el cambio al repositorio
git add supabase/
git commit -m "IPUIEWV-XX: descripción del cambio"
git push origin feature/IPUIEWV-XX-nombre-de-la-tarea
```

Después, abrir el Pull Request hacia `main` para revisión y merge.

---

## 4. Comandos útiles de diagnóstico

| Comando | Para qué sirve |
|---|---|
| `supabase projects list` | Confirma que estás logueado y ver los project refs disponibles |
| `supabase migration list` | Compara migraciones locales vs. las ya aplicadas en remoto |
| `supabase db diff --linked` | Verifica que el esquema local y el remoto estén sincronizados |
| `cat supabase/.temp/project-ref` | Confirma a qué proyecto está linkeada la carpeta actual |

---

## 5. Orden de dependencia entre tablas

`usuarios` debe crearse primero: `puntajes`, `rachas`, `comodines` y `logs` tienen foreign keys hacia `usuarios.id`, así que sus migraciones deben aplicarse después.
