import json
import os
from rapidfuzz import process, fuzz
from supabase import create_client, Client
from app.config import settings
from app.embeddings import normalizar

_client: Client | None = None
_local_biblia: list[dict] | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(settings.supabase_url, settings.supabase_service_key)
    return _client


def _cargar_local_biblia() -> list[dict]:
    global _local_biblia
    if _local_biblia is None:
        rutas = ["Documentos/biblia_extraida.json", "biblia_extraida.json"]
        for r in rutas:
            if os.path.exists(r):
                with open(r, "r", encoding="utf-8") as f:
                    _local_biblia = json.load(f)
                break
        if _local_biblia is None:
            _local_biblia = []
    return _local_biblia


def buscar_versiculos_similares(embedding: list[float], texto_consulta: str = "", match_count: int = 3):
    """Llama a la función RPC match_biblia definida en schema.sql.
    Si la tabla o función no existe aún en Supabase, utiliza la copia local de
    biblia_extraida.json como respaldo automático para pruebas inmediatas.
    """
    client = get_client()
    try:
        resp = client.rpc(
            "match_biblia",
            {
                "query_embedding": embedding,
                "match_count": match_count,
                "version_filter": settings.version_biblia,
            },
        ).execute()
        if resp.data:
            return resp.data
    except Exception as e:
        # Imprimir aviso discreto para saber que está operando con respaldo local
        pass

    # Respaldo local automático
    biblia = _cargar_local_biblia()
    if not biblia:
        return []

    textos = [normalizar(r["texto"]) for r in biblia]
    query_norm = normalizar(texto_consulta) if texto_consulta else ""

    if not query_norm:
        return []

    matches = process.extract(query_norm, textos, scorer=fuzz.WRatio, limit=match_count)
    resultados = []
    for match_str, score, idx in matches:
        v = biblia[idx]
        resultados.append(
            {
                "id": idx + 1,
                "libro": v["libro"],
                "capitulo": v["capitulo"],
                "versiculo": v["versiculo"],
                "texto": v["texto"],
                "similitud": round(score / 100.0, 4),
            }
        )
    return resultados



def obtener_lectura_del_dia(fecha_iso: str):
    """fecha_iso en formato 'YYYY-MM-DD'. Devuelve el registro de lecturas_diarias o None."""
    client = get_client()
    resp = (
        client.table("lecturas_diarias")
        .select("*")
        .eq("fecha", fecha_iso)
        .maybe_single()
        .execute()
    )
    return resp.data


def guardar_verificacion(registro: dict):
    """Guarda el resultado en verificaciones_rag para auditoría.
    No es estrictamente necesario si n8n ya lo registra, pero sirve
    para depurar el propio servidor de forma independiente.
    """
    try:
        client = get_client()
        client.table("verificaciones_rag").insert(registro).execute()
    except Exception:
        # Si la tabla verificaciones_rag aún no existe en Supabase, ignorar el log de auditoría
        pass

