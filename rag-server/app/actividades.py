import math
import re
import unicodedata
from rapidfuzz import fuzz

from app.embeddings import generar_embedding, normalizar

# Patrón para limpiar saludos y frases introductorias en WhatsApp
PATRON_SALUDOS_ACTIVIDAD = re.compile(
    r"^(?:"
    r"buenos\s+d[ií]as|buenas\s+tardes|buenas\s+noches|"
    r"hola(?:\s+grupo|\s+hermanos?|\s+a\s+todos|\s+todos)?|"
    r"bendiciones(?:\s+a\s+todos|\s+grupo)?|am[eé]n(?:\s+dios\s+les\s+bendiga)?"
    r")"
    r"[\s,.:;-]*"
    r"(?:"
    r"(?:esta\s+es|este\s+es|aqu[ií]\s+est[aá]|les\s+comparto|para|de)?\s*"
    r"(?:mi\s+|la\s+)?(?:respuesta|reto|actividad|soluci[oó]n)(?:\s+de\s+hoy|\s+del\s+d[ií]a)?(?:\s+es)?:?"
    r")*"
    r"[\s,.:;-]*",
    re.IGNORECASE,
)

PALABRAS_GENERICAS = {"el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "en", "con", "por", "para", "que", "y", "o", "a", "al", "monte", "san", "santa"}


def limpiar_saludo_actividad(texto: str) -> str:
    """Remueve prefijos conversacionales (saludos, intros de WhatsApp) para extraer la respuesta core."""
    if not texto:
        return ""
    limpio = PATRON_SALUDOS_ACTIVIDAD.sub("", texto).strip()
    return limpio if len(limpio) >= 2 else texto.strip()


def normalizar_dia(dia: str) -> str:
    """Normaliza el día de la semana (sin tildes, minúsculas)."""
    if not dia:
        return ""
    d = dia.lower().strip()
    d = unicodedata.normalize("NFD", d)
    d = "".join(c for c in d if unicodedata.category(c) != "Mn")
    return d


def calcular_similitud_coseno(vec1: list[float], vec2: list[float]) -> float:
    """Calcula la similitud coseno entre dos vectores de float."""
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    sim = dot / (norm1 * norm2)
    return float(max(0.0, min(1.0, sim)))


def comparar_textos_semantico(texto1: str, texto2: str) -> float:
    """Genera embeddings y calcula similitud coseno entre dos cadenas directamente."""
    emb1 = generar_embedding(texto1)
    emb2 = generar_embedding(texto2)
    return calcular_similitud_coseno(emb1, emb2)


def calcular_similitud_combinada(user_clean: str, respuesta_esperada: str) -> float:
    """Combina similitud léxica (fuzz token set ratio) con similitud semántica de embeddings.
    Evita falsos positivos de embeddings en texto no relacionado que comparte espacio vectorial.
    """
    sim_semantica = comparar_textos_semantico(user_clean, respuesta_esperada)
    sim_fuzz = fuzz.token_set_ratio(normalizar(user_clean), normalizar(respuesta_esperada)) / 100.0
    
    # Si la coincidencia difusa es muy baja, se reduce el peso de la similitud semántica
    if sim_fuzz < 0.20:
        sim_combinada = sim_fuzz * 0.6 + sim_semantica * 0.4
    else:
        sim_combinada = sim_fuzz * 0.5 + sim_semantica * 0.5

    return round(float(max(0.0, min(1.0, sim_combinada))), 4)


def extraer_elementos(texto: str) -> list[str]:
    """Separa el texto esperado en elementos o puntos clave (comas, punto y coma, viñetas, saltos de línea o ' y ')."""
    if not texto:
        return []
    lineas = re.split(r"(?:\r?\n|;|[-•*]|\b\d+[\.\)]\s*)", texto)
    elementos = []
    for l in lineas:
        subpartes = re.split(r",|\s+y\s+", l)
        for sub in subpartes:
            cleaned = sub.strip()
            if cleaned and len(normalizar(cleaned)) >= 2:
                elementos.append(cleaned)
    return elementos if elementos else [texto.strip()]


# =====================================================================
# FUNCIONES DE VALIDACIÓN ESPECÍFICAS POR DÍA
# =====================================================================

def validar_lunes(pregunta: str, respuesta_esperada: str, respuesta_usuario: str) -> dict:
    """Lunes - 'Pregunta / aplicación' (1 punto).
    Comparación semántica simple (embeddings) con umbral permisivo para reflexión personal.
    """
    user_clean = limpiar_saludo_actividad(respuesta_usuario)

    similitud = calcular_similitud_combinada(user_clean, respuesta_esperada)
    umbral = 0.65  # Umbral permisivo para reflexión personal

    es_valido = similitud >= umbral
    puntos = 1 if es_valido else 0
    veredicto = "valido" if es_valido else "invalido"

    if es_valido:
        explicacion = f"Respuesta aceptada. Captura la idea central de la pregunta (similitud: {similitud:.2f})."
    else:
        explicacion = f"La respuesta no alcanza la similitud requerida con la idea esperada (similitud: {similitud:.2f})."

    return {
        "veredicto": veredicto,
        "similitud": similitud,
        "puntos": puntos,
        "explicacion": explicacion,
    }


def validar_martes(pregunta: str, respuesta_esperada: str, respuesta_usuario: str) -> dict:
    """Martes - 'Detective bíblico' (2 puntos).
    Busca un dato específico (nombre, lugar, número). Comparación estricta de palabras clave.
    """
    user_clean = limpiar_saludo_actividad(respuesta_usuario)
    norm_esp = normalizar(respuesta_esperada)
    norm_usr = normalizar(user_clean)

    # 1. Inclusión directa
    sim_inclusion = 1.0 if norm_esp in norm_usr else 0.0

    # 2. Palabras clave específicas (excluyendo conectores genéricos)
    palabras_esp = [w for w in norm_esp.split() if len(w) >= 3 and w not in PALABRAS_GENERICAS]
    if not palabras_esp:
        palabras_esp = norm_esp.split()

    # Verificar si las palabras clave del dato esperado están presentes
    coinciden_clave = all(
        any(w in word_usr or fuzz.ratio(w, word_usr) >= 85 for word_usr in norm_usr.split())
        for w in palabras_esp
    )

    sim_combinada = calcular_similitud_combinada(user_clean, respuesta_esperada)

    if sim_inclusion == 1.0:
        similitud = 1.0
        es_valido = True
    elif coinciden_clave:
        similitud = round(max(0.90, sim_combinada), 4)
        es_valido = True
    elif sim_combinada >= 0.78:
        similitud = sim_combinada
        es_valido = True
    else:
        similitud = sim_combinada
        es_valido = False

    puntos = 2 if es_valido else 0
    veredicto = "valido" if es_valido else "invalido"

    if es_valido:
        explicacion = f"Dato clave ('{respuesta_esperada}') identificado correctamente en la respuesta."
    else:
        explicacion = f"No se identificó el dato clave esperado ('{respuesta_esperada}') en la respuesta."

    return {
        "veredicto": veredicto,
        "similitud": similitud,
        "puntos": puntos,
        "explicacion": explicacion,
    }


def validar_miercoles(pregunta: str, respuesta_esperada: str, respuesta_usuario: str) -> dict:
    """Miércoles - 'Reto de 20 segundos' (2 puntos).
    Validación de lista de elementos clave por presencia de términos exactos/difusos.
    """
    user_clean = limpiar_saludo_actividad(respuesta_usuario)
    norm_usr = normalizar(user_clean)

    items_esperados = extraer_elementos(respuesta_esperada)
    total_items = len(items_esperados)

    encontrados = []
    faltantes = []

    for item in items_esperados:
        norm_item = normalizar(item)

        # Inclusión directa o fuzzy token ratio con palabras de la respuesta
        in_direct = norm_item in norm_usr
        fuzz_score = max(
            fuzz.ratio(norm_item, w) for w in norm_usr.split()
        ) / 100.0 if norm_usr else 0.0

        token_match = fuzz.token_set_ratio(norm_item, norm_usr) >= 88

        if in_direct or fuzz_score >= 0.85 or token_match:
            encontrados.append(item)
        else:
            faltantes.append(item)

    cant_encontrados = len(encontrados)
    min_requeridos = max(1, math.ceil(total_items * 0.6))
    similitud = round(cant_encontrados / total_items if total_items > 0 else 0.0, 4)

    es_valido = cant_encontrados >= min_requeridos
    puntos = 2 if es_valido else 0
    veredicto = "valido" if es_valido else "invalido"

    if es_valido:
        explicacion = f"Contiene {cant_encontrados} de {total_items} elementos esperados (mínimo requerido: {min_requeridos})."
    else:
        explicacion = f"Contiene solo {cant_encontrados} de {total_items} elementos esperados (se requerían al menos {min_requeridos}). Faltó: {', '.join(faltantes)}."

    return {
        "veredicto": veredicto,
        "similitud": similitud,
        "puntos": puntos,
        "explicacion": explicacion,
    }


def validar_jueves(pregunta: str, respuesta_esperada: str, respuesta_usuario: str) -> dict:
    """Jueves - 'Completa la idea' (1 punto).
    Comparación semántica estricta.
    """
    user_clean = limpiar_saludo_actividad(respuesta_usuario)

    similitud = calcular_similitud_combinada(user_clean, respuesta_esperada)
    umbral = 0.72  # Más estricto que lunes

    es_valido = similitud >= umbral
    puntos = 1 if es_valido else 0
    veredicto = "valido" if es_valido else "invalido"

    if es_valido:
        explicacion = f"Completa correctamente la idea planteada (similitud: {similitud:.2f})."
    else:
        explicacion = f"La respuesta no completa adecuadamente la idea requerida (similitud: {similitud:.2f})."

    return {
        "veredicto": veredicto,
        "similitud": similitud,
        "puntos": puntos,
        "explicacion": explicacion,
    }


def validar_viernes(pregunta: str, respuesta_esperada: str, respuesta_usuario: str) -> dict:
    """Viernes - 'Reto sorpresa' (2 puntos).
    Formato variable. Lógica flexible con umbral moderado.
    """
    user_clean = limpiar_saludo_actividad(respuesta_usuario)

    similitud = calcular_similitud_combinada(user_clean, respuesta_esperada)
    umbral = 0.65

    es_valido = similitud >= umbral
    puntos = 2 if es_valido else 0
    veredicto = "valido" if es_valido else "invalido"

    if es_valido:
        explicacion = f"Respuesta válida para el reto sorpresa (similitud: {similitud:.2f})."
    else:
        explicacion = f"La respuesta no cumple el criterio del reto sorpresa (similitud: {similitud:.2f})."

    return {
        "veredicto": veredicto,
        "similitud": similitud,
        "puntos": puntos,
        "explicacion": explicacion,
    }


def validar_sabado(pregunta: str, respuesta_esperada: str, respuesta_usuario: str) -> dict:
    """Sábado - 'Prueba de fuego' (PONDERADO, hasta 5 puntos).
    Calcula un score de calidad de 0.0 a 1.0 según la completitud y precisión de la respuesta.
    Escala:
      >= 0.9 -> 5 pts
      >= 0.7 -> 4 pts
      >= 0.5 -> 3 pts
      >= 0.3 -> 2 pts
      >= 0.1 -> 1 pt
      < 0.1  -> 0 pts
    """
    user_clean = limpiar_saludo_actividad(respuesta_usuario)
    norm_usr = normalizar(user_clean)

    items_esperados = extraer_elementos(respuesta_esperada)
    total_items = len(items_esperados)

    cubiertos = []
    faltantes = []

    for item in items_esperados:
        norm_item = normalizar(item)
        in_direct = norm_item in norm_usr
        fuzz_partial = fuzz.partial_ratio(norm_item, norm_usr) / 100.0
        fuzz_token = fuzz.token_set_ratio(norm_item, norm_usr) / 100.0

        # Palabras clave indispensables del ítem
        palabras_item = [w for w in norm_item.split() if len(w) >= 3 and w not in PALABRAS_GENERICAS]
        if palabras_item:
            tiene_palabras_clave = any(
                any(w in word_usr or fuzz.ratio(w, word_usr) >= 80 for word_usr in norm_usr.split())
                for w in palabras_item
            )
        else:
            tiene_palabras_clave = True

        sem_score = comparar_textos_semantico(user_clean, item) if tiene_palabras_clave else 0.0

        if in_direct or fuzz_partial >= 0.78 or (tiene_palabras_clave and (fuzz_token >= 0.80 or sem_score >= 0.76)):
            cubiertos.append(item)
        else:
            faltantes.append(item)

    ratio_elementos = len(cubiertos) / total_items if total_items > 0 else 0.0
    sim_combinada = calcular_similitud_combinada(user_clean, respuesta_esperada)

    # Si hay múltiples elementos, la proporción de elementos cubiertos es el factor decisivo principal
    if total_items > 1:
        if ratio_elementos == 1.0:
            score = max(0.92, ratio_elementos * 0.85 + sim_combinada * 0.15)
        else:
            score = ratio_elementos * 0.85 + sim_combinada * 0.15
    else:
        score = max(sim_combinada, ratio_elementos)

    score = round(max(0.0, min(1.0, score)), 4)

    # Conversión a puntos enteros según escala especificada
    if score >= 0.9:
        puntos = 5
    elif score >= 0.7:
        puntos = 4
    elif score >= 0.5:
        puntos = 3
    elif score >= 0.3:
        puntos = 2
    elif score >= 0.1:
        puntos = 1
    else:
        puntos = 0

    veredicto = "valido" if puntos > 0 else "invalido"

    # Construcción de la explicación detallada
    if total_items > 1:
        detalles_cubiertos = f"Elementos cubiertos ({len(cubiertos)}/{total_items}): [{', '.join(cubiertos)}]"
        detalles_faltantes = f" | Faltantes: [{', '.join(faltantes)}]" if faltantes else " | Todos los elementos fueron cubiertos"
        explicacion = f"{detalles_cubiertos}{detalles_faltantes}. Score: {score:.2f} -> {puntos}/5 puntos."
    else:
        explicacion = f"Calificación general: {score:.2f} de similitud -> {puntos}/5 puntos."

    return {
        "veredicto": veredicto,
        "similitud": score,
        "puntos": puntos,
        "explicacion": explicacion,
    }


def normalizar_identificador_actividad(identificador: str) -> str:
    """Normaliza identificadores de actividad o día (sin tildes, minúsculas, espacios/guiones a guion bajo)."""
    if not identificador:
        return ""
    s = identificador.lower().strip()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[\s_-]+", "_", s)
    return s


# Router principal de actividades
def verificar_actividad(
    actividad: str,
    pregunta: str,
    respuesta_esperada: str,
    respuesta_usuario: str,
) -> dict:
    """Valida la respuesta del usuario para el reto diario según el tipo de actividad.
    Devuelve un diccionario con veredicto, similitud, puntos y explicacion.
    Lanza ValueError si el tipo de actividad no es reconocido.
    """
    if not actividad:
        raise ValueError("El campo 'actividad' es requerido.")

    clave = normalizar_identificador_actividad(actividad)

    MAPPING = {
        "pregunta_aplicacion": validar_lunes,
        "pregunta": validar_lunes,

        "detective_biblico": validar_martes,
        "detective": validar_martes,

        "reto_20_segundos": validar_miercoles,
        "reto_20s": validar_miercoles,

        "completa_idea": validar_jueves,
        "completa_la_idea": validar_jueves,

        "reto_sorpresa": validar_viernes,
        "sorpresa": validar_viernes,

        "prueba_fuego": validar_sabado,
    }

    if clave not in MAPPING:
        raise ValueError(
            f"Tipo de actividad '{actividad}' no es válido. Opciones válidas: "
            "pregunta_aplicacion, detective_biblico, reto_20_segundos, completa_idea, reto_sorpresa, prueba_fuego."
        )

    validador = MAPPING[clave]
    return validador(pregunta, respuesta_esperada, respuesta_usuario)
