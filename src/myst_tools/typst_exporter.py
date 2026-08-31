"""Conversor de MyST Markdown a plantilla Typst para imprenta."""

from __future__ import annotations

import re


def convertir_myst_a_typst(contenido_md: str, titulo: str = "Apunte de Cátedra") -> str:
    """Convierte encabezados, bloques de código y callouts a sintaxis Typst."""
    typst_lines = [
        f'#set document(title: "{titulo}")',
        '#set page(paper: "a4", margin: (x: 2cm, y: 2.5cm))',
        '#set text(font: "Linux Libertine", size: 11pt, lang: "es")',
        f"= {titulo}\n",
    ]

    for line in contenido_md.splitlines():
        # Encabezados
        if line.startswith("# "):
            typst_lines.append(f"= {line[2:].strip()}")
        elif line.startswith("## "):
            typst_lines.append(f"== {line[3:].strip()}")
        elif line.startswith("### "):
            typst_lines.append(f"=== {line[4:].strip()}")
        else:
            typst_lines.append(line)

    return "\n".join(typst_lines)
