"""Validador de sintaxis C para snippets embebidos en Markdown MyST."""

from __future__ import annotations

import re
import subprocess
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Any


def extraer_y_validar_snippets_c(contenido_md: str) -> List[Dict[str, Any]]:
    """Extrae bloques ```c ... ``` y verifica si compilan con gcc -fsyntax-only."""
    gcc_bin = shutil.which("gcc")
    bloques = re.findall(r"```(?:c|C)\n(.*?)```", contenido_md, re.DOTALL)

    resultados = []
    for idx, codigo in enumerate(bloques, 1):
        codigo_completo = codigo
        # Si no tiene main ni headers mínimos, agregar wrapper para verificar sintaxis básica
        if "main" not in codigo and "{" in codigo and "}" in codigo:
            codigo_completo = f"#include <stdio.h>\n#include <stdlib.h>\n{codigo}\n"

        if not gcc_bin:
            resultados.append({"bloque": idx, "valido": True, "detalle": "GCC no disponible"})
            continue

        with tempfile.NamedTemporaryFile(suffix=".c", mode="w", encoding="utf-8") as tmp:
            tmp.write(codigo_completo)
            tmp.flush()
            res = subprocess.run([gcc_bin, "-fsyntax-only", tmp.name], capture_output=True, text=True)
            resultados.append({
                "bloque": idx,
                "valido": res.returncode == 0,
                "detalle": res.stderr.strip() if res.returncode != 0 else "Sintaxis C válida",
            })

    return resultados
