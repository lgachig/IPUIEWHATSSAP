from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_service_key: str

    # Modelo de embeddings local (multilingüe, corre en CPU)
    embedding_model_name: str = "intfloat/multilingual-e5-small"

    # Umbrales de similitud coseno (0-1). Calibrar con datos reales
    # una vez tengas mensajes de prueba del grupo.
    umbral_alto: float = 0.85   # >= esto: aceptar automáticamente, sin LLM
    umbral_bajo: float = 0.70   # < esto: no se parece a ningún versículo real

    # Gemini (solo fallback, capa 3)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash-lite"

    # Versión bíblica cargada en biblia_vectorizada
    version_biblia: str = "RVR"

    class Config:
        env_file = ".env"


settings = Settings()
