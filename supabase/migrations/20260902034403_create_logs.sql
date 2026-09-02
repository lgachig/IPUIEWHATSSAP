create table logs (
  id uuid primary key default gen_random_uuid(),
  fecha timestamptz not null default now(),
  tipo_evento text not null,
  descripcion text,
  usuario_id uuid references usuarios(id) on delete set null,
  nivel text not null default 'info' check (nivel in ('info', 'error'))
);