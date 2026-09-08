from google import genai
from app.config import settings

_client: genai.Client | None = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


PROMPT_TEMPLATE = """Eres un verificador de lecturas bíblicas. Un usuario debía leer:

Referencia esperada: {referencia_esperada}
Texto esperado: {texto_esperado}

El usuario envió este mensaje:
"{texto_usuario}"

Responde ÚNICAMENTE con una de estas dos palabras, sin explicación:
VALIDO - si el mensaje corresponde razonablemente a esa lectura (aunque tenga errores de tipeo, esté resumido o parafraseado).
INVALIDO - si el mensaje no tiene relación con esa lectura o es otro tipo de mensaje.
"""


def verificar_con_llm(texto_usuario: str, referencia_esperada: str, texto_esperado: str) -> bool:
    """Fallback de última instancia. Solo se debe llamar cuando la Capa 1
    (exacta) y la Capa 2 (embeddings contra la Biblia completa) no dieron
    un veredicto confiable.
    """
    if not settings.gemini_api_key:
        return False

    try:
        client = get_client()
        prompt = PROMPT_TEMPLATE.format(
            referencia_esperada=referencia_esperada,
            texto_esperado=texto_esperado,
            texto_usuario=texto_usuario,
        )
        resp = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
        )
        respuesta = (resp.text or "").strip().upper()
        return respuesta.startswith("VALIDO")
    except Exception as e:
        return False

