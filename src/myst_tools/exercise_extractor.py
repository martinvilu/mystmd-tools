"""Extractor de consignas prácticas embebidas hacia formato de banco de ejercicios (Deckard)."""

from __future__ import annotations

import re
import yaml
from typing import List, Dict, Any


def extraer_ejercicios_myst(contenido_md: str) -> List[Dict[str, Any]]:
    """Extrae bloques de directivas ```{exercise} o secciones de consigna."""
    ejercicios = []
    bloques = re.findall(r"```\{exercise\}\s*([^\n]*)\n(.*?)```", contenido_md, re.DOTALL)
    for idx, (titulo, cuerpo) in enumerate(bloques, 1):
        nombre = titulo.strip() or f"Ejercicio {idx}"
        ejercicios.append({
            "titulo": nombre,
            "enunciado": cuerpo.strip(),
            "nivel_bloom": "aplicar",
            "tiempo_estimado_minutos": 30,
        })
    return ejercicios
