create table lecturas_diarias (
  id uuid primary key default gen_random_uuid(),
  fecha date not null unique,
  lectura text not null,
  tema text,
  pregunta_reto text,
  respuesta_esperada text,
  created_at timestamptz default now()
);

create index idx_lecturas_fecha on lecturas_diarias (fecha);