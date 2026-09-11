"""Extractor de ejemplos de código hacia proyectos C compilables de prueba."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional


def extraer_snippets_c_compilables(contenido_md: str) -> List[Dict[str, Any]]:
    """Extrae snippets C identificando si son programas completos o fragmentos con aserciones."""
    patron = r"```+(?:\{c\}|c|C)[^\n]*\n(.*?)```+"
    bloques = re.findall(patron, contenido_md, re.DOTALL)
    snippets = []

    for idx, raw_code in enumerate(bloques, 1):
        code = raw_code.strip()
        tiene_main = "int main(" in code or "void main(" in code or "main()" in code
        tiene_asserts = "assert(" in code
        headers = re.findall(r"#include\s+<[^>]+>", code)

        if not tiene_main:
            codigo_compilable = (
                "#include <stdio.h>\n"
                "#include <stdlib.h>\n"
                "#include <assert.h>\n"
                "#include <string.h>\n"
                "#include <stdbool.h>\n\n"
                f"{code}\n\n"
                "int main(void) {\n"
                "    return 0;\n"
                "}\n"
            )
        else:
            codigo_compilable = code
            if "#include <assert.h>" not in codigo_compilable and tiene_asserts:
                codigo_compilable = "#include <assert.h>\n" + codigo_compilable

        snippets.append({
            "indice": idx,
            "codigo_original": code,
            "codigo_compilable": codigo_compilable,
            "tiene_main": tiene_main,
            "tiene_asserts": tiene_asserts,
        })
    return snippets


def exportar_proyecto_c(
    snippets: List[Dict[str, Any]],
    output_dir: Path,
    cflags: str = "-Wall -Wextra -std=c11",
) -> List[Path]:
    """Genera archivos de código C y un Makefile para compilar los ejemplos."""
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_files = []
    targets = []

    for snip in snippets:
        idx = snip["indice"]
        filename = f"ejemplo_{idx:02d}.c"
        filepath = output_dir / filename
        filepath.write_text(snip["codigo_compilable"], encoding="utf-8")
        generated_files.append(filepath)
        targets.append(f"ejemplo_{idx:02d}")

    makefile_content = [
        "CC ?= gcc",
        f"CFLAGS ?= {cflags}",
        f"TARGETS = {' '.join(targets)}",
        "",
        "all: $(TARGETS)",
        "",
    ]
    for t in targets:
        makefile_content.append(f"{t}: {t}.c")
        makefile_content.append(f"\t$(CC) $(CFLAGS) $< -o $@")
        makefile_content.append("")

    makefile_content.append("test: all")
    for t in targets:
        makefile_content.append(f"\t./{t}")
    makefile_content.append("")
    makefile_content.append("clean:")
    makefile_content.append(f"\trm -f $(TARGETS)")

    makefile_path = output_dir / "Makefile"
    makefile_path.write_text("\n".join(makefile_content), encoding="utf-8")
    generated_files.append(makefile_path)
    return generated_files


def compilar_y_ejecutar_snippets(
    snippets: List[Dict[str, Any]],
    temp_dir: Path,
    gcc_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Compila y ejecuta snippets evaluando retorno y aserciones."""
    compiler = gcc_path or shutil.which("gcc")
    resultados = []

    for snip in snippets:
        idx = snip["indice"]
        c_file = temp_dir / f"test_{idx}.c"
        bin_file = temp_dir / f"test_{idx}.out"
        c_file.write_text(snip["codigo_compilable"], encoding="utf-8")

        if not compiler:
            resultados.append({
                "indice": idx,
                "compilado": False,
                "ejecutado": False,
                "error": "Compilador GCC no localizado",
            })
            continue

        cmd_comp = [compiler, "-Wall", "-Wextra", "-std=c11", str(c_file), "-o", str(bin_file)]
        res_comp = subprocess.run(cmd_comp, capture_output=True, text=True)

        if res_comp.returncode != 0:
            resultados.append({
                "indice": idx,
                "compilado": False,
                "ejecutado": False,
                "error": res_comp.stderr.strip(),
            })
            continue

        res_exec = subprocess.run([str(bin_file)], capture_output=True, text=True, timeout=5)
        resultados.append({
            "indice": idx,
            "compilado": True,
            "ejecutado": res_exec.returncode == 0,
            "stdout": res_exec.stdout,
            "stderr": res_exec.stderr,
            "error": res_exec.stderr.strip() if res_exec.returncode != 0 else "",
        })

    return resultados
