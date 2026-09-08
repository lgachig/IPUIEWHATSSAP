import re
import unicodedata
from rapidfuzz import fuzz

from app.config import settings
from app.embeddings import generar_embedding, normalizar
from app.supabase_client import buscar_versiculos_similares, obtener_lectura_del_dia
from app.llm_fallback import verificar_con_llm


CITA_REGEX = re.compile(
    r"\b([1-3]?\s*[a-záéíóúñA-ZÁÉÍÓÚÑ]{3,})\s+(\d+)[\s:\.,]+(\d+)(?:\s*[-–]\s*(\d+))?\b"
)


def _referencia(libro: str, capitulo: int, versiculo: int) -> str:
    return f"{libro} {capitulo}:{versiculo}"


def extraer_cita(texto: str):
    """Detecta si el mensaje enviado contiene una cita bíblica (ej. '1 Pedro 4:1', 'Génesis 1:1')."""
    m = CITA_REGEX.search(texto)
    if m:
        libro = m.group(1).strip()
        capitulo = int(m.group(2))
        vers_ini = int(m.group(3))
        vers_fin = int(m.group(4)) if m.group(4) else vers_ini
        return libro, capitulo, vers_ini, vers_fin
    return None


def _norm(s: str) -> str:
    s = s.lower().strip()
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")



def coincide_con_lectura(libro: str, capitulo: int, versiculo: int, lectura_str: str) -> bool:
    """Verifica si un versículo específico (libro, capítulo, versículo) está dentro de la
    cadena de lectura del día (ej. '1 Pedro 3–4', 'Salmos 15 y 24', 'Salmos 19 y 119:9–16').
    """
    if not lectura_str:
        return False

    norm_libro = _norm(libro)
    norm_lectura = _norm(lectura_str)

    if norm_libro not in norm_lectura:
        return False

    partes = [p.strip() for p in norm_lectura.split(" y ")]
    for parte in partes:
        # Intentar extraer libro de la parte si viene especificado
        m_book = re.match(r"^([1-3]\s+[a-z]+|[a-z]+)\s+(.*)$", parte)
        if m_book:
            b_parte = m_book.group(1)
            rest = m_book.group(2)
            if b_parte not in norm_libro and norm_libro not in b_parte:
                continue
        else:
            rest = parte

        # Caso versículos: ej. "119:9-16" o "119:9–16"
        m_v = re.search(r"(\d+):(\d+)(?:[–-](\d+))?", rest)
        if m_v:
            cap = int(m_v.group(1))
            v_ini = int(m_v.group(2))
            v_fin = int(m_v.group(3)) if m_v.group(3) else v_ini
            if capitulo == cap and (v_ini <= versiculo <= v_fin):
                return True
            continue

        # Caso capítulos: ej. "1-2", "3-4" o capítulo único "3"
        m_c = re.search(r"(\d+)(?:\s*[–-]\s*(\d+))?", rest)
        if m_c:
            c_ini = int(m_c.group(1))
            c_fin = int(m_c.group(2)) if m_c.group(2) else c_ini
            if c_ini <= capitulo <= c_fin:
                return True

    return False


PATRON_SALUDOS = re.compile(
    r"^(?:buenos\s+d[ií]as|buenas\s+tardes|buenas\s+noches|hola(?:\s+grupo|\s+hermanos?|\s+todos)?|bendiciones|am[eé]n)"
    r"(?:\s*(?:este\s+es|aqu[ií]\s+esta|les\s+comparto)?\s*(?:el\s+)?vers[ií]culo(?:\s+que\s+me\s+llam[oó]\s+la\s+atenci[oó]n)?)*[\s,.:;-]*",
    re.IGNORECASE,
)


def limpiar_saludo(texto: str) -> str:
    """Remueve prefijos conversacionales (saludos, frases comunes de grupo) para dejar solo el contenido del versículo."""
    cleaned = PATRON_SALUDOS.sub("", texto).strip()
    return cleaned if len(cleaned) > 5 else texto


def verificar_lectura(texto_usuario: str, fecha_iso: str) -> dict:
    """Punto de entrada principal. Devuelve un dict con el veredicto y
    el detalle de qué capa lo resolvió, para poder loguearlo.
    """
    lectura_hoy = obtener_lectura_del_dia(fecha_iso)
    if lectura_hoy is None:
        return {
            "veredicto": "revision_manual",
            "metodo": "sin_lectura_programada",
            "detalle": f"No hay lectura programada para {fecha_iso} en lecturas_diarias.",
        }

    # Soporte tanto si viene 'lectura' (ej. "1 Pedro 3–4") como si vienen campos estructurados
    lectura_str = lectura_hoy.get("lectura") or ""
    if not lectura_str and "libro" in lectura_hoy:
        lectura_str = _referencia(
            lectura_hoy["libro"], lectura_hoy["capitulo"], lectura_hoy["versiculo_inicio"]
        )

    texto_esperado = lectura_hoy.get("lectura_completa") or lectura_str
    texto_limpio = limpiar_saludo(texto_usuario)

    # ---------- Capa 0: detección de cita bíblica directa (ej. "1 Pedro 4:1", "Génesis 1:1") ----------
    cita = extraer_cita(texto_usuario)
    if cita:
        libro_c, cap_c, v_ini_c, v_fin_c = cita
        coincide = coincide_con_lectura(libro_c, cap_c, v_ini_c, lectura_str)
        return {
            "veredicto": "valido" if coincide else "invalido",
            "metodo": "cita_directa",
            "similitud": 1.0,
            "match": f"{libro_c} {cap_c}:{v_ini_c}",
            "coincide_con_hoy": coincide,
        }

    # ---------- Capa 1: comparación exacta / difusa (gratis, instantánea) ----------
    if texto_esperado:
        ratio = fuzz.token_set_ratio(normalizar(texto_limpio), normalizar(texto_esperado))
        if ratio >= 92:  # calibrar con datos reales del grupo
            return {
                "veredicto": "valido",
                "metodo": "exacto",
                "similitud": ratio / 100,
                "match": lectura_str,
                "coincide_con_hoy": True,
            }

    # ---------- Capa 2: búsqueda semántica contra la Biblia completa ----------
    embedding = generar_embedding(texto_limpio)
    candidatos = buscar_versiculos_similares(embedding, texto_consulta=texto_limpio, match_count=3)


    if candidatos:
        top = candidatos[0]
        if top["similitud"] >= settings.umbral_alto:
            if "libro" in lectura_hoy and lectura_hoy["libro"] is not None:
                coincide = (
                    top["libro"] == lectura_hoy["libro"]
                    and top["capitulo"] == lectura_hoy["capitulo"]
                    and lectura_hoy.get("versiculo_inicio", 0) <= top["versiculo"] <= lectura_hoy.get("versiculo_fin", 999)
                )
            else:
                coincide = coincide_con_lectura(
                    top["libro"], top["capitulo"], top["versiculo"], lectura_str
                )

            return {
                "veredicto": "valido" if coincide else "invalido",
                "metodo": "embedding",
                "similitud": top["similitud"],
                "match": _referencia(top["libro"], top["capitulo"], top["versiculo"]),
                "coincide_con_hoy": coincide,
            }

        if top["similitud"] < settings.umbral_bajo:
            # No se parece a ningún versículo real de la Biblia.
            return {
                "veredicto": "invalido",
                "metodo": "embedding",
                "similitud": top["similitud"],
                "match": None,
                "coincide_con_hoy": False,
            }

    # ---------- Capa 3: zona ambigua -> único caso que llama a Gemini ----------
    es_valido = verificar_con_llm(texto_usuario, lectura_str, texto_esperado)
    return {
        "veredicto": "valido" if es_valido else "invalido",
        "metodo": "llm_fallback",
        "similitud": candidatos[0]["similitud"] if candidatos else None,
        "match": lectura_str if es_valido else None,
        "coincide_con_hoy": es_valido,
    }

