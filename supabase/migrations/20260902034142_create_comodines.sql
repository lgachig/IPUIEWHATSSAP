create table comodines (
  id uuid primary key default gen_random_uuid(),
  usuario_id uuid not null references usuarios(id) on delete cascade,
  mes text not null,
  cantidad_usada integer not null default 1,
  fecha_uso date not null default current_date,
  motivo text
);