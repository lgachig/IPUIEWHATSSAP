create table puntajes (
  id uuid primary key default gen_random_uuid(),
  usuario_id uuid not null references usuarios(id) on delete cascade,
  fecha date not null,
  categoria text not null,
  puntos integer not null,
  valido boolean not null default true,
  motivo text
);