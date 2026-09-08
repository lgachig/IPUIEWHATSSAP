-- =========================================================
-- MODO ÍNTEGRO — Esquema Supabase para el motor RAG bíblico
-- =========================================================

-- 1. Habilitar la extensión pgvector
create extension if not exists vector;

-- 2. Tabla con la Biblia completa vectorizada
-- Un registro por versículo. El modelo sugerido (multilingual-e5-small)
-- produce embeddings de 384 dimensiones.
create table if not exists biblia_vectorizada (
    id            bigserial primary key,
    libro         text not null,          -- ej. 'Génesis', 'Juan'
    libro_num     smallint not null,      -- 1-66, orden canónico, útil para ordenar/depurar
    capitulo      smallint not null,
    versiculo     smallint not null,
    texto         text not null,
    version       text not null default 'RVR', -- por si luego cargas otra versión
    embedding     vector(384),
    created_at    timestamptz not null default now(),
    unique (libro_num, capitulo, versiculo, version)
);

-- Índice para búsqueda por similitud coseno.
-- Con ~31,000 filas, un índice ivfflat ya es cómodo (no hace falta hnsw todavía).
create index if not exists biblia_embedding_idx
    on biblia_vectorizada
    using ivfflat (embedding vector_cosine_ops)
    with (lists = 100);

-- 3. Función RPC que usará el servidor FastAPI para buscar el/los versículo(s)
-- más parecido(s) a un texto entrante.
create or replace function match_biblia(
    query_embedding vector(384),
    match_count int default 3,
    version_filter text default 'RVR'
)
returns table (
    id bigint,
    libro text,
    capitulo smallint,
    versiculo smallint,
    texto text,
    similitud float
)
language sql stable
as $$
    select
        b.id,
        b.libro,
        b.capitulo,
        b.versiculo,
        b.texto,
        1 - (b.embedding <=> query_embedding) as similitud
    from biblia_vectorizada b
    where b.version = version_filter
    order by b.embedding <=> query_embedding
    limit match_count;
$$;

-- 4. Calendario de lecturas diarias (ya lo tenías contemplado en Sprint 2,
-- lo dejo aquí referenciado con libro_num/capitulo/versiculo_inicio/fin
-- para poder comparar contra el resultado de match_biblia sin ambigüedad).
create table if not exists lecturas_diarias (
    id                  bigserial primary key,
    fecha               date not null unique,
    libro               text not null,
    libro_num           smallint not null,
    capitulo            smallint not null,
    versiculo_inicio    smallint not null,
    versiculo_fin       smallint not null,
    lectura_completa    text,           -- texto completo de la lectura del día (opcional, para el envío matutino)
    actividad           text,           -- tipo de actividad (ej. pregunta_aplicacion, detective_biblico, etc.)
    created_at          timestamptz not null default now()
);

-- 5. Log de verificaciones del RAG (útil para auditar falsos positivos/negativos
-- y para medir cuántos mensajes terminan escalando a Gemini).
create table if not exists verificaciones_rag (
    id                  bigserial primary key,
    telefono            text not null,
    fecha_mensaje       date not null,
    texto_recibido      text not null,
    metodo              text not null,     -- 'exacto' | 'embedding' | 'llm_fallback'
    match_libro         text,
    match_capitulo      smallint,
    match_versiculo     smallint,
    similitud           float,
    coincide_con_hoy    boolean,
    veredicto           text not null,     -- 'valido' | 'invalido' | 'revision_manual'
    created_at          timestamptz not null default now()
);
