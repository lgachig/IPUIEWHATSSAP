"""
Paso 2 de la ingesta: toma biblia_extraida.json (ya revisado a mano),
genera los embeddings y los sube a Supabase en lotes.

Correr DESPUÉS de validar la muestra de ingest_biblia.py, nunca antes.
"""

import json
import os
import sys

from sentence_transformers import SentenceTransformer

from app.config import settings
from app.embeddings import normalizar
from app.supabase_client import get_client

LOTE = 500


def cargar_json(ruta: str) -> list[dict]:
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def resolver_ruta(ruta_dada: str) -> str:
    if os.path.exists(ruta_dada):
        return ruta_dada
    ruta_doc = os.path.join("Documentos", ruta_dada)
    if os.path.exists(ruta_doc):
        return ruta_doc
    return ruta_dada


def main(ruta_json: str = "biblia_extraida.json"):
    ruta_json = resolver_ruta(ruta_json)
    registros = cargar_json(ruta_json)
    print(f"Cargando {len(registros)} versículos desde {ruta_json}...")

    modelo = SentenceTransformer(settings.embedding_model_name)
    client = get_client()

    for i in range(0, len(registros), LOTE):
        lote = registros[i : i + LOTE]
        # Prefijo 'passage:' -- requerido por los modelos e5 para el lado
        # "documento" de la búsqueda (el lado "consulta" usa 'query:',
        # ver app/embeddings.py::generar_embedding).
        textos = [f"passage: {normalizar(r['texto'])}" for r in lote]
        embeddings = modelo.encode(textos, normalize_embeddings=True, show_progress_bar=False)

        filas = [
            {
                "libro": r["libro"],
                "libro_num": r["libro_num"],
                "capitulo": r["capitulo"],
                "versiculo": r["versiculo"],
                "texto": r["texto"],
                "version": settings.version_biblia,
                "embedding": emb.tolist(),
            }
            for r, emb in zip(lote, embeddings)
        ]

        client.table("biblia_vectorizada").upsert(
            filas, on_conflict="libro_num,capitulo,versiculo,version"
        ).execute()

        print(f"  {min(i + LOTE, len(registros))}/{len(registros)} cargados")

    print("Listo. Verifica en Supabase: select count(*) from biblia_vectorizada;")


if __name__ == "__main__":
    ruta = sys.argv[1] if len(sys.argv) > 1 else "biblia_extraida.json"
    main(ruta)

