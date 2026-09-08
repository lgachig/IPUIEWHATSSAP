import os
import re
import unicodedata

from app.config import settings

_model = None
_model_failed = False


def get_model():
    global _model, _model_failed
    if _model is None:
        from sentence_transformers import SentenceTransformer
        try:
            _model = SentenceTransformer(settings.embedding_model_name, local_files_only=True)
        except Exception:
            try:
                _model = SentenceTransformer(settings.embedding_model_name)
                _model_failed = False
            except Exception as e:
                _model_failed = True
                raise e
    return _model



def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes, sin puntuación, espacios colapsados.
    Se usa tanto en la Capa 1 (comparación exacta/difusa) como para
    limpiar antes de generar el embedding.
    """
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def generar_embedding(texto: str) -> list[float]:
    """El prefijo 'query:' / 'passage:' es requerido por los modelos e5
    para obtener buena calidad de similitud. Los versículos de la Biblia
    se deben haber indexado con prefijo 'passage:' (ver script de ingesta).
    """
    try:
        modelo = get_model()
        vector = modelo.encode(f"query: {normalizar(texto)}", normalize_embeddings=True)
        return vector.tolist()
    except Exception:
        return [0.0] * 384


