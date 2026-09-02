create table rachas (
  id uuid primary key default gen_random_uuid(),
  usuario_id uuid not null unique references usuarios(id) on delete cascade,
  racha_actual integer not null default 0,
  racha_maxima integer not null default 0,
  ultima_fecha_cumplida date
);