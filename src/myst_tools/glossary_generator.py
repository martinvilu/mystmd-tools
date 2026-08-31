"""Generador de glosario e indexador de términos técnicos en MyST Markdown."""

from __future__ import annotations

import re
from typing import Dict, List, Any


def generar_glosario_terminos(contenido_md: str) -> Dict[str, str]:
    """Detecta definiciones de términos técnicos en formato `{term}` o negritas introductorias."""
    terminos = {}
    # Patrón: **Término**: Definición...
    matches = re.findall(r"\*\*([a-zA-Z0-9_\s]{3,30})\*\*\s*:\s*([^\n]+)", contenido_md)
    for term, definicion in matches:
        terminos[term.strip()] = definicion.strip()

    return terminos
