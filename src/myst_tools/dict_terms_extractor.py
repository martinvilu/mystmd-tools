"""Extractor de términos técnicos y TDAs para diccionario personalizado de LanguageTool."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Set, List


def extraer_terminos_tecnicos_c(contenido_md: str) -> Set[str]:
    """Extrae identificadores C, tipos, structs y palabras clave técnicas de documentos MyST."""
    terminos: Set[str] = set()

    # 1. Tipos de C terminados en _t
    tipos_t = re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*_t)\b", contenido_md)
    terminos.update(tipos_t)

    # 2. Tipos de structs (struct Nombre, typedef struct)
    structs = re.findall(r"\bstruct\s+([a-zA-Z_][a-zA-Z0-9_]*)\b", contenido_md)
    terminos.update(structs)

    # 3. Nombres de funciones en código C o inline (ej: nombre_funcion(...) o `mi_funcion()`)
    funciones = re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]{2,})\s*\(", contenido_md)
    terminos.update(funciones)

    # 4. Constantes en UPPER_SNAKE_CASE
    constantes = re.findall(r"\b([A-Z][A-Z0-9_]{2,})\b", contenido_md)
    terminos.update(constantes)

    # 5. Directivas MyST (ej: ```{exercise} consigna-1, ```{admonition}, (mi-ancla)=)
    directivas = re.findall(r"```\{([a-zA-Z0-9_\-]+)\}\s*([a-zA-Z0-9_\-]*)", contenido_md)
    for dir_name, dir_arg in directivas:
        if dir_name:
            terminos.add(dir_name)
        if dir_arg:
            terminos.add(dir_arg)
    anclas = re.findall(r"\(([a-zA-Z0-9_\-]+)\)=", contenido_md)
    terminos.update(anclas)

    # Filtrar palabras comunes en español o palabras muy cortas
    palabras_comunes = {"para", "como", "pero", "esta", "este", "todo", "cada", "unos", "unas"}
    terminos_filtrados = {
        t for t in terminos
        if len(t) > 2 and t.lower() not in palabras_comunes and not t.isdigit()
    }
    return terminos_filtrados


def exportar_diccionario_languagetool(terminos: Set[str], output_file: Path) -> int:
    """Exporta los términos ordenados alfabéticamente para spelling.txt de LanguageTool."""
    ordenados = sorted(terminos)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(ordenados) + "\n", encoding="utf-8")
    return len(ordenados)
