"""
Script de ingesta: PDF de la Biblia -> tabla biblia_vectorizada en Supabase.

ESTADO: armazón funcional, PENDIENTE DE CALIBRAR con el PDF real.
Este layout (Reina Valera, números de versículo en el margen derecho de
cada línea en vez de pegados al texto) no se puede parsear de forma
genérica -- necesita que midamos con pdfplumber las coordenadas X y el
tamaño de fuente reales de ese PDF específico.

Cómo calibrar (correr esto primero, con el PDF real, antes de correr
la ingesta completa):

    import pdfplumber
    with pdfplumber.open("biblia.pdf") as pdf:
        pagina = pdf.pages[10]  # una página de contenido normal, no portada
        for palabra in pagina.extract_words(extra_attrs=["size", "fontname"]):
            print(palabra)

Con esa salida se puede ver:
  - x0 / x1 de las palabras normales del cuerpo del texto (columna izq/ancha)
  - x0 de los números de versículo (deberían agruparse en una franja X
    angosta, cerca del margen derecho)
  - 'size' del número de versículo (normalmente más chico que el cuerpo)

Con esos tres datos se ajustan las constantes UMBRAL_X_MARGEN_DERECHO y
UMBRAL_TAMANO_FUENTE_NUMERO más abajo, y el parser debería funcionar.
"""

import json
import re
import unicodedata

import pdfplumber

# ---- Constantes a calibrar con el PDF real (ver docstring arriba) ----
UMBRAL_X_MARGEN_DERECHO = 0.85  # fracción del ancho de página a partir de la cual
                                 # un número se considera "número de versículo"
                                 # y no parte del cuerpo del texto
UMBRAL_TAMANO_FUENTE_NUMERO_MAX = 9.0  # pt, ajustar según el PDF

# Encabezados de libro: líneas en mayúsculas sostenidas, centradas, que no
# contienen dígitos. La lista de libros sirve para validar contra falsos
# positivos (ej. "LIBRO PRIMERO DE MOISÉS" es un subtítulo, no el nombre
# del libro que se usará como referencia -- "GÉNESIS" sí lo es).
LIBROS_BIBLIA = [
    "Génesis", "Éxodo", "Levítico", "Números", "Deuteronomio", "Josué",
    "Jueces", "Rut", "1 Samuel", "2 Samuel", "1 Reyes", "2 Reyes",
    "1 Crónicas", "2 Crónicas", "Esdras", "Nehemías", "Ester", "Job",
    "Salmos", "Proverbios", "Eclesiastés", "Cantares", "Isaías",
    "Jeremías", "Lamentaciones", "Ezequiel", "Daniel", "Oseas", "Joel",
    "Amós", "Abdías", "Jonás", "Miqueas", "Nahúm", "Habacuc", "Sofonías",
    "Hageo", "Zacarías", "Malaquías",
    "Mateo", "Marcos", "Lucas", "Juan", "Hechos", "Romanos",
    "1 Corintios", "2 Corintios", "Gálatas", "Efesios", "Filipenses",
    "Colosenses", "1 Tesalonicenses", "2 Tesalonicenses", "1 Timoteo",
    "2 Timoteo", "Tito", "Filemón", "Hebreos", "Santiago", "1 Pedro",
    "2 Pedro", "1 Juan", "2 Juan", "3 Juan", "Judas", "Apocalipsis",
]

LIBROS_NORMALIZADOS = {
    unicodedata.normalize("NFD", l).encode("ascii", "ignore").decode().upper(): (i + 1, l)
    for i, l in enumerate(LIBROS_BIBLIA)
}


def detectar_encabezado_libro(linea_texto: str):
    """Devuelve (numero_libro, nombre_libro) si la línea es un encabezado
    de libro conocido, o None si no lo es."""
    clave = unicodedata.normalize("NFD", linea_texto.strip()).encode("ascii", "ignore").decode().upper()
    return LIBROS_NORMALIZADOS.get(clave)


def extraer_versiculos_de_pagina(pagina) -> list[dict]:
    """Separa los números de versículo (margen derecho) del cuerpo del
    texto usando la posición X y el tamaño de fuente, y reconstruye
    pares (numero_versiculo, texto_hasta_el_siguiente_numero).

    PENDIENTE: calibrar UMBRAL_X_MARGEN_DERECHO y
    UMBRAL_TAMANO_FUENTE_NUMERO_MAX con el PDF real antes de confiar
    en la salida de esta función.
    """
    ancho_pagina = pagina.width
    palabras = pagina.extract_words(extra_attrs=["size", "fontname"])

    cuerpo, numeros = [], []
    for p in palabras:
        es_numero = re.fullmatch(r"\d{1,3}", p["text"]) is not None
        en_margen = p["x0"] >= ancho_pagina * UMBRAL_X_MARGEN_DERECHO
        if es_numero and en_margen and p["size"] <= UMBRAL_TAMANO_FUENTE_NUMERO_MAX:
            numeros.append(p)
        else:
            cuerpo.append(p)

    # TODO: una vez calibrado, aquí va la lógica de reconstrucción real:
    # ordenar 'cuerpo' y 'numeros' por (top, x0), y para cada número
    # determinar qué palabras del cuerpo caen "antes" de él en orden de
    # lectura para cerrar el versículo anterior y abrir el siguiente.
    raise NotImplementedError(
        "Calibrar UMBRAL_X_MARGEN_DERECHO / UMBRAL_TAMANO_FUENTE_NUMERO_MAX "
        "con el PDF real (ver docstring del script) antes de usar esta función."
    )


def parsear_pdf(ruta_pdf: str) -> list[dict]:
    """Recorre el PDF completo y devuelve una lista de
    {libro, libro_num, capitulo, versiculo, texto}.
    """
    registros = []
    libro_actual = None
    capitulo_actual = 1

    with pdfplumber.open(ruta_pdf) as pdf:
        for pagina in pdf.pages:
            texto_pagina = pagina.extract_text() or ""
            for linea in texto_pagina.split("\n"):
                encabezado = detectar_encabezado_libro(linea)
                if encabezado:
                    libro_actual = encabezado[1]
                    capitulo_actual = 1

            if libro_actual is None:
                continue  # portada / índice, aún no llegamos al contenido

            versiculos = extraer_versiculos_de_pagina(pagina)
            for v in versiculos:
                registros.append(
                    {
                        "libro": libro_actual,
                        "libro_num": LIBROS_NORMALIZADOS[
                            unicodedata.normalize("NFD", libro_actual).encode("ascii", "ignore").decode().upper()
                        ][0],
                        "capitulo": v["capitulo"],
                        "versiculo": v["versiculo"],
                        "texto": v["texto"],
                    }
                )

    return registros


def validar_extraccion(registros: list[dict]):
    """Chequeo mínimo antes de vectorizar: la Reina Valera completa
    tiene 31,102 versículos. Si el conteo se aleja mucho, hay texto
    mal parseado (columnas mezcladas, notas coladas, etc.)."""
    total = len(registros)
    print(f"Versículos extraídos: {total} (esperado ~31,102)")
    if abs(total - 31102) > 500:
        print("ADVERTENCIA: el conteo se aleja demasiado del esperado. "
              "Revisar manualmente antes de vectorizar.")

    libros_vistos = {r["libro"] for r in registros}
    faltantes = set(LIBROS_BIBLIA) - libros_vistos
    if faltantes:
        print(f"ADVERTENCIA: no se detectaron estos libros: {faltantes}")


if __name__ == "__main__":
    import sys

    ruta = sys.argv[1] if len(sys.argv) > 1 else "biblia.pdf"
    registros = parsear_pdf(ruta)
    validar_extraccion(registros)

    with open("biblia_extraida.json", "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)

    print("Guardado en biblia_extraida.json -- revisar una muestra al azar "
          "contra el PDF antes de continuar con la vectorización.")
