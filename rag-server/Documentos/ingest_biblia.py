"""
ingest_biblia.py
=================
Extrae el texto completo de LA_SANTA_BIBLIA_Reina_Valera_1960.pdf (edición
Bibles.org.uk, pdfLaTeX, 2001-2005 — "Permission for personal use only is
hereby given", ver página 1 del PDF) a un JSON estructurado:

    [
      {"libro": "Génesis", "libro_num": 1, "capitulo": 1, "versiculo": 1, "texto": "..."},
      ...
    ]

CALIBRACIÓN (hecha inspeccionando el PDF real con pdfplumber.extract_words):

  - Texto de cuerpo:        fuente *LMRoman12-Regular (o variantes small-caps/
                             itálica del mismo tamaño ~12pt: LMCaps10-Regular a
                             12pt para títulos de Salmos, LMRoman12-Italic para
                             "Selah", etc.) -> todo esto se trata como texto normal.
  - Número de versículo:    fuente *LMRoman8-Regular, tamaño ~8pt. Aparece
                             insertado en medio del flujo de palabras, justo
                             antes de la primera palabra del versículo.
  - Número de capítulo:     fuente *LMRoman12-Bold, tamaño ~12pt. Marca el
                             inicio de un capítulo nuevo. El versículo 1 de
                             cada capítulo NO lleva número propio (implícito).
                             Cuando el versículo 2 empieza inmediatamente,
                             aparecen pegados "1" (negrita) + "," + "2" (8pt);
                             la coma es un artefacto de maquetación en fuente
                             LMRoman9-Regular ~9pt y se descarta siempre.
  - Encabezado de página:   todo lo que está en la franja superior (top < 25pt)
                             -> número de página impresa, nombre de libro
                             (LMCaps10-Regular ~10pt) y rango cap.versículo.
                             Se ignora para el cuerpo, pero se usa para
                             autovalidar el libro/capítulo esperado en cada
                             página.
  - Título de libro:        fuente LMCaps10-Regular con tamaño > 14pt (17.2 o
                             24.8) -> "LIBRO PRIMERO DE MOISÉS" / "GÉNESIS",
                             etc. Se ignora (no es texto bíblico).
  - Capitular (drop cap):   fuente 'unknown', tamaño ~46pt. Es la primera letra
                             en mayúscula grande del primer versículo de cada
                             libro. Se antepone como carácter simple al primer
                             token de cuerpo de esa página.

  Los límites libro -> página se derivan del ÍNDICE del propio PDF (páginas 2
  y 3), no de heurísticas de estilo, porque es 100% confiable: cada entrada
  del índice da la página IMPRESA de inicio del libro. El offset entre página
  impresa y página real del PDF es constante (+3), pero el script lo valida
  también contra el encabezado de cada página y avisa si alguna vez no cuadra.

USO:
    pip install pdfplumber --break-system-packages
    python3 ingest_biblia.py --pdf LA_SANTA_BIBLIA_Reina_Valera_1960.pdf --out biblia_extraida.json
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field

import pdfplumber

# ---------------------------------------------------------------------------
# 1. Tabla canónica de libros (orden bíblico, tal como aparecen en el índice
#    del PDF: columna izquierda AT, columna derecha AT, columna izquierda NT,
#    columna derecha NT). start_pagina_impresa viene literal del índice
#    (páginas 2-3 del PDF).
# ---------------------------------------------------------------------------

LIBROS = [
    # (nombre_normalizado, nombre_como_aparece_en_encabezado, pagina_impresa_inicio)
    ("Génesis", "Génesis", 1),
    ("Éxodo", "Éxodo", 81),
    ("Levítico", "Levítico", 147),
    ("Números", "Números", 196),
    ("Deuteronomio", "Deuteronomio", 264),
    ("Josué", "Josué", 321),
    ("Jueces", "Jueces", 361),
    ("Rut", "Rut", 401),
    ("1 Samuel", "I Samuel", 407),
    ("2 Samuel", "II Samuel", 460),
    ("1 Reyes", "I Reyes", 504),
    ("2 Reyes", "II Reyes", 556),
    ("1 Crónicas", "I Crónicas", 605),
    ("2 Crónicas", "II Crónicas", 650),
    ("Esdras", "Esdras", 707),
    ("Nehemías", "Nehemías", 724),
    ("Ester", "Ester", 747),
    ("Job", "Job", 760),
    ("Salmos", "Salmos", 800),
    ("Proverbios", "Proverbios", 898),
    ("Eclesiastés", "Eclesiastés", 932),
    ("Cantares", "Cantar de los Cantares", 945),
    ("Isaías", "Isaías", 951),
    ("Jeremías", "Jeremías", 1028),
    ("Lamentaciones", "Lamentaciones", 1117),
    ("Ezequiel", "Ezequiel", 1125),
    ("Daniel", "Daniel", 1206),
    ("Oseas", "Oseas", 1231),
    ("Joel", "Joel", 1242),
    ("Amós", "Amós", 1247),
    ("Abdías", "Abdías", 1256),
    ("Jonás", "Jonás", 1258),
    ("Miqueas", "Miqueas", 1261),
    ("Nahum", "Nahum", 1268),
    ("Habacuc", "Habacuc", 1271),
    ("Sofonías", "Sofonías", 1275),
    ("Hageo", "Hageo", 1279),
    ("Zacarías", "Zacarías", 1282),
    ("Malaquías", "Malaquías", 1296),
    ("Mateo", "Mateo", 1301),
    ("Marcos", "Marcos", 1352),
    ("Lucas", "Lucas", 1384),
    ("Juan", "Juan", 1439),
    ("Hechos", "Hechos", 1480),
    ("Romanos", "Romanos", 1535),
    ("1 Corintios", "I Corintios", 1558),
    ("2 Corintios", "II Corintios", 1580),
    ("Gálatas", "Gálatas", 1595),
    ("Efesios", "Efesios", 1603),
    ("Filipenses", "Filipenses", 1611),
    ("Colosenses", "Colosenses", 1617),
    ("1 Tesalonicenses", "I Tesalonicenses", 1623),
    ("2 Tesalonicenses", "II Tesalonicenses", 1628),
    ("1 Timoteo", "I Timoteo", 1631),
    ("2 Timoteo", "II Timoteo", 1637),
    ("Tito", "Tito", 1642),
    ("Filemón", "Filemón", 1645),
    ("Hebreos", "Hebreos", 1647),
    ("Santiago", "Santiago", 1664),
    ("1 Pedro", "I Pedro", 1670),
    ("2 Pedro", "II Pedro", 1677),
    ("1 Juan", "I Juan", 1681),
    ("2 Juan", "II Juan", 1687),
    ("3 Juan", "III Juan", 1688),
    ("Judas", "Judas", 1689),
    ("Apocalipsis", "El Apocalipsis", 1691),
]

assert len(LIBROS) == 66, f"Se esperaban 66 libros, hay {len(LIBROS)}"

OFFSET_PAGINA = 3  # pagina_pdf_index = pagina_impresa + OFFSET_PAGINA (calibrado y verificado)

# umbrales de tamaño de fuente (en puntos) calibrados con extract_words()
UMBRAL_TOP_HEADER = 25.0          # todo lo que está por encima de esto es encabezado de página
UMBRAL_TAMANO_TITULO_MIN = 14.0   # títulos de libro (17.2 y 24.8pt)
UMBRAL_TAMANO_CUERPO_MIN = 11.0
UMBRAL_TAMANO_CUERPO_MAX = 13.0
UMBRAL_TAMANO_VERSICULO_MIN = 7.0
UMBRAL_TAMANO_VERSICULO_MAX = 9.0
UMBRAL_TAMANO_DROPCAP_MIN = 30.0


def _font_stem(fontname: str) -> str:
    # pdfplumber da fuentes tipo "IRJQHN+LMRoman12-Regular"; nos quedamos con
    # la parte útil tras el "+"
    return fontname.split("+")[-1] if "+" in fontname else fontname


@dataclass
class Versiculo:
    libro: str
    libro_num: int
    capitulo: int
    versiculo: int
    texto: str = ""


def construir_rangos_libros():
    """Devuelve lista de (libro, libro_num, pagina_pdf_inicio, pagina_pdf_fin)."""
    rangos = []
    for i, (nombre, nombre_header, pag_impresa) in enumerate(LIBROS):
        pdf_inicio = pag_impresa + OFFSET_PAGINA
        if i + 1 < len(LIBROS):
            pdf_fin = LIBROS[i + 1][2] + OFFSET_PAGINA - 1
        else:
            pdf_fin = None  # se completa con total de páginas al usarlo
        rangos.append(
            {
                "libro": nombre,
                "libro_header": nombre_header,
                "libro_num": i + 1,
                "pdf_inicio": pdf_inicio,
                "pdf_fin": pdf_fin,
            }
        )
    return rangos


def libro_para_pagina(rangos, pdf_index, total_paginas):
    for r in rangos:
        fin = r["pdf_fin"] if r["pdf_fin"] is not None else total_paginas - 1
        if r["pdf_inicio"] <= pdf_index <= fin:
            return r
    return None


_RE_LIMITE_ORACION = re.compile(r"^[A-ZÁÉÍÓÚÑÜ]")


def _punto_de_division(buffer_palabras):
    """
    Busca, de derecha a izquierda, el último límite de oración dentro de
    `buffer_palabras` (palabra que termina en . ; : seguida de una palabra
    que empieza en mayúscula). Devuelve el índice donde debería empezar el
    "resto" (fragmento que en realidad pertenece al verso siguiente), o None
    si no se encontró ninguno razonable.

    Esto se usa para des-mezclar el caso en que dos marcas de versículo caen
    tan cerca verticalmente que LaTeX las combina en una sola nota al margen
    (p. ej. "12,13"): el texto de ambos versículos termina acumulado junto en
    el mismo buffer, y hay que partirlo por el límite de oración más
    plausible.
    """
    for i in range(len(buffer_palabras) - 1, 0, -1):
        anterior = buffer_palabras[i - 1]
        actual = buffer_palabras[i]
        if anterior.rstrip()[-1:] in ".;:" and _RE_LIMITE_ORACION.match(actual):
            return i
    return None


def extraer_versiculos_de_pagina(page, libro_actual: dict, estado: dict, avisos: list):
    """
    Extrae los versículos (o fragmentos de versículo) contenidos en `page`.

    `estado` es un diccionario mutable con:
        - capitulo: capítulo actual (int, 0 si aún no se vio ningún marcador)
        - versiculo: versículo actual (int)
        - buffer: lista de palabras acumuladas para el versículo en curso
        - resultados: lista de Versiculo ya cerrados (se va rellenando)
        - drop_cap_pendiente: letra capitular a anteponer al próximo texto

    Devuelve `estado` actualizado (se muta in-place y también se retorna).
    """
    words = page.extract_words(extra_attrs=["size", "fontname"], use_text_flow=False)
    # orden de lectura: arriba->abajo, izquierda->derecha
    words.sort(key=lambda w: (round(w["top"], 0), w["x0"]))

    def es_marcador_pequeno(w):
        fuente = _font_stem(w["fontname"])
        return (
            UMBRAL_TAMANO_VERSICULO_MIN <= w["size"] <= UMBRAL_TAMANO_VERSICULO_MAX
            and "Roman8" in fuente
            and w["text"].strip().isdigit()
        )

    def es_coma_marcador(w):
        fuente = _font_stem(w["fontname"])
        return fuente == "LMRoman9-Regular" and w["text"].strip() in {",", ";"}

    def cerrar_versiculo_actual(semilla_siguiente=None):
        """Cierra el versículo en curso. Si `semilla_siguiente` no es None,
        intenta partir el buffer por el último límite de oración y deja esa
        cola como semilla para el próximo versículo (caso de marcas
        combinadas tipo '12,13')."""
        cola = None
        buf = estado["buffer"]
        if semilla_siguiente is not None and len(buf) >= 2:
            idx = _punto_de_division(buf)
            if idx is not None:
                cola = buf[idx:]
                buf = buf[:idx]

        if buf:
            texto = " ".join(buf).strip()
            texto = re.sub(r"\s+([,.;:])", r"\1", texto)
            if texto:
                estado["resultados"].append(
                    Versiculo(
                        libro=libro_actual["libro"],
                        libro_num=libro_actual["libro_num"],
                        capitulo=estado["capitulo"],
                        versiculo=estado["versiculo"],
                        texto=texto,
                    )
                )
        estado["buffer"] = cola if cola else []

    for idx_w, w in enumerate(words):
        texto_palabra = w["text"]
        size = w["size"]
        fuente = _font_stem(w["fontname"])
        top = w["top"]

        # 1) Encabezado de página: se ignora para el cuerpo
        if top < UMBRAL_TOP_HEADER:
            continue

        # 2) Capitular (drop cap): se guarda para anteponer a la próxima palabra de cuerpo
        if fuente == "unknown" or size >= UMBRAL_TAMANO_DROPCAP_MIN:
            estado["drop_cap_pendiente"] = texto_palabra
            continue

        # 3) Título de libro (tamaño grande, small caps) -> ignorar
        if size >= UMBRAL_TAMANO_TITULO_MIN:
            continue

        # 4) Coma-artefacto del complejo capítulo+versículo -> ignorar
        if fuente == "LMRoman9-Regular" and texto_palabra.strip() in {",", ";"}:
            continue

        # 5) Número de capítulo (negrita ~12pt) -> nuevo capítulo, versículo 1 implícito
        if "Bold" in fuente and UMBRAL_TAMANO_CUERPO_MIN <= size <= UMBRAL_TAMANO_CUERPO_MAX:
            if not texto_palabra.strip().isdigit():
                avisos.append(f"Marcador de capítulo no numérico: {texto_palabra!r} en pág {page.page_number}")
                continue
            # look-ahead: ¿viene "coma + otro marcador" pegado? (combo capítulo,versículo)
            combo = (
                idx_w + 2 < len(words)
                and es_coma_marcador(words[idx_w + 1])
                and es_marcador_pequeno(words[idx_w + 2])
            )
            cerrar_versiculo_actual(semilla_siguiente=True if combo else None)
            estado["capitulo"] = int(texto_palabra)
            estado["versiculo"] = 1
            continue

        # 6) Número de versículo (~8pt) -> nuevo versículo
        if UMBRAL_TAMANO_VERSICULO_MIN <= size <= UMBRAL_TAMANO_VERSICULO_MAX and "Roman8" in fuente:
            if not texto_palabra.strip().isdigit():
                avisos.append(f"Marcador de versículo no numérico: {texto_palabra!r} en pág {page.page_number}")
                continue
            # look-ahead: ¿viene "coma + otro marcador" pegado? (combo N,M -> versos muy cortos)
            combo = (
                idx_w + 2 < len(words)
                and es_coma_marcador(words[idx_w + 1])
                and es_marcador_pequeno(words[idx_w + 2])
            )
            cerrar_versiculo_actual(semilla_siguiente=True if combo else None)
            estado["versiculo"] = int(texto_palabra)
            continue

        # 7) Texto de cuerpo normal (incluye small-caps de títulos de Salmos e itálicas)
        if UMBRAL_TAMANO_CUERPO_MIN <= size <= UMBRAL_TAMANO_CUERPO_MAX:
            if estado["capitulo"] == 0:
                # Texto de cuerpo antes de ver ningún marcador de capítulo:
                # no debería pasar salvo en la primerísima palabra de un libro
                # (drop cap + resto del versículo 1 del capítulo 1).
                estado["capitulo"] = 1
                estado["versiculo"] = 1
            if estado["drop_cap_pendiente"]:
                texto_palabra = estado["drop_cap_pendiente"] + texto_palabra
                estado["drop_cap_pendiente"] = None
            estado["buffer"].append(texto_palabra)
            continue

        avisos.append(f"Palabra sin clasificar: {texto_palabra!r} fuente={fuente} size={size} pág {page.page_number}")

    return estado


def procesar_pdf(pdf_path: str, avisos: list):
    resultados_totales = []
    rangos = construir_rangos_libros()

    with pdfplumber.open(pdf_path) as pdf:
        total_paginas = len(pdf.pages)
        libro_actual = None
        estado = None

        for pdf_index, page in enumerate(pdf.pages):
            r = libro_para_pagina(rangos, pdf_index, total_paginas)
            if r is None:
                continue  # portada, copyright, índice, páginas en blanco antes de Génesis

            if libro_actual is None or r["libro"] != libro_actual["libro"]:
                # cerrar el libro anterior y empezar uno nuevo
                if estado is not None:
                    resultados_totales.extend(estado["resultados"])
                libro_actual = r
                estado = {
                    "capitulo": 0,
                    "versiculo": 0,
                    "buffer": [],
                    "resultados": [],
                    "drop_cap_pendiente": None,
                }

            extraer_versiculos_de_pagina(page, libro_actual, estado, avisos)
            page.flush_cache()
            if pdf_index % 50 == 0:
                print(f"  ... pagina {pdf_index}/{total_paginas}", file=sys.stderr)

        # cerrar el último versículo del último libro
        if estado is not None:
            if estado["buffer"]:
                texto = " ".join(estado["buffer"]).strip()
                texto = re.sub(r"\s+([,.;:])", r"\1", texto)
                if texto:
                    estado["resultados"].append(
                        Versiculo(
                            libro=libro_actual["libro"],
                            libro_num=libro_actual["libro_num"],
                            capitulo=estado["capitulo"],
                            versiculo=estado["versiculo"],
                            texto=texto,
                        )
                    )
                estado["buffer"] = []
            resultados_totales.extend(estado["resultados"])

    return resultados_totales


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", default="biblia_extraida.json")
    args = ap.parse_args()

    avisos = []
    versiculos = procesar_pdf(args.pdf, avisos)

    data = [
        {
            "libro": v.libro,
            "libro_num": v.libro_num,
            "capitulo": v.capitulo,
            "versiculo": v.versiculo,
            "texto": v.texto,
        }
        for v in versiculos
    ]

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Total de versículos extraídos: {len(data)}")
    print(f"Avisos: {len(avisos)}")
    for a in avisos[:30]:
        print("  -", a)
    if len(avisos) > 30:
        print(f"  ... y {len(avisos) - 30} avisos más")


if __name__ == "__main__":
    sys.exit(main())
