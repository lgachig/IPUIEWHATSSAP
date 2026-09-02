-- Activar RLS en las 5 tablas
alter table usuarios enable row level security;
alter table puntajes enable row level security;
alter table rachas enable row level security;
alter table comodines enable row level security;
alter table logs enable row level security;
alter table lecturas_diarias enable row level security;

-- Solo lectura para el admin autenticado (dashboard)
create policy "admin_read_usuarios" on usuarios
  for select to authenticated using (true);

create policy "admin_read_puntajes" on puntajes
  for select to authenticated using (true);

create policy "admin_read_rachas" on rachas
  for select to authenticated using (true);

create policy "admin_read_comodines" on comodines
  for select to authenticated using (true);

create policy "admin_read_logs" on logs
  for select to authenticated using (true);

create policy "Permitir lectura con service role"
on lecturas_diarias
for select
using (true);