create table usuarios (
  id uuid primary key default gen_random_uuid(),
  nombre text not null,
  numero_telefono text not null unique,
  comodines_disponibles integer not null default 2,
  fecha_registro timestamptz not null default now(),
  rol text not null default 'usuario' check (rol in ('usuario', 'admin'))
);