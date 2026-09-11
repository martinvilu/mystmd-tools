"""Verificador de estilo y reglas gramaticales en español rioplatense."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any


@dataclass
class StyleIssue:
    line_number: int
    column: int
    matched_text: str
    suggested_text: str
    rule_type: str
    message: str


# Reglas de spanglish informático común a desaconsejar o sugerir término técnico en español/código
SPANGLISH_PATTERNS = [
    (r"\bdebuggear\b", "depurar", "spanglish"),
    (r"\bdeployar\b", "desplegar", "spanglish"),
    (r"\bmergear\b", "fusionar o integrar", "spanglish"),
    (r"\bcustomizar\b", "personalizar", "spanglish"),
    (r"\bprintar\b", "imprimir o mostrar", "spanglish"),
    (r"\bhardcodear\b", "fijar en código o codificar directamente", "spanglish"),
    (r"\bparsear\b", "analizar sintácticamente", "spanglish"),
    (r"\bcommitear\b", "hacer commit de", "spanglish"),
]

# Tuteo vs Voseo rioplatense (detectar imperativos o pronombres tuteantes fuera de bloques de código)
TUTEO_PATTERNS = [
    (r"\btú\b", "vos", "voseo_inconsistente"),
    (r"\btienes\b", "tenés", "voseo_inconsistente"),
    (r"\bhaz\b", "hacé", "voseo_inconsistente"),
    (r"\bpiensa\b", "pensá", "voseo_inconsistente"),
    (r"\bmira\b", "mirá", "voseo_inconsistente"),
    (r"\bpuedes\b", "podés", "voseo_inconsistente"),
    (r"\bquieres\b", "querés", "voseo_inconsistente"),
    (r"\bpon\b", "poné", "voseo_inconsistente"),
    (r"\bve\s+a\b", "andá a", "voseo_inconsistente"),
    (r"\bdebes\b", "debés", "voseo_inconsistente"),
]


def auditar_estilo_rioplatense(contenido_md: str) -> List[StyleIssue]:
    """Audita inconsistencias de voseo y spanglish fuera de bloques de código y enlaces."""
    issues = []
    lines = contenido_md.splitlines()
    in_code_block = False

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Omitir contenido dentro de backticks inline `...`
        line_sans_code = re.sub(r"`[^`]+`", lambda m: " " * len(m.group(0)), line)

        for pat, sug, kind in SPANGLISH_PATTERNS:
            for match in re.finditer(pat, line_sans_code, flags=re.IGNORECASE):
                issues.append(StyleIssue(
                    line_number=idx,
                    column=match.start() + 1,
                    matched_text=match.group(0),
                    suggested_text=sug,
                    rule_type=kind,
                    message=f"Término de spanglish detectado ('{match.group(0)}'). Sugerencia: '{sug}'.",
                ))

        for pat, sug, kind in TUTEO_PATTERNS:
            for match in re.finditer(pat, line_sans_code, flags=re.IGNORECASE):
                issues.append(StyleIssue(
                    line_number=idx,
                    column=match.start() + 1,
                    matched_text=match.group(0),
                    suggested_text=sug,
                    rule_type=kind,
                    message=f"Forma de tuteo detectada ('{match.group(0)}'). En estilo rioplatense se prefiere '{sug}'.",
                ))

    return issues
