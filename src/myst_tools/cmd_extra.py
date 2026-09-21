"""Comandos de extracción, enlaces y doctor."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

import typer

from myst_tools._cli_base import _check_myst_yml, app, console, emitir_json, err_console


@app.command("extract-c-tests")
def cmd_extract_c_tests(
    file_path: Path = typer.Argument(..., help="Archivo Markdown del cual extraer ejemplos C."),
    output_dir: Path = typer.Option(Path("./test_c_project"), "--output-dir", "-o", help="Directorio destino del proyecto C."),
    force: bool = typer.Option(False, "--force", "-f", help="Fuerza la ejecución ignorando myst.yml."),
) -> None:
    """Extrae bloques C hacia un proyecto C compilable con Makefile."""
    from myst_tools.c_project_extractor import extraer_snippets_c_compilables, exportar_proyecto_c

    _check_myst_yml(force)
    if not file_path.is_file():
        err_console.print(f"[bold red]Error:[/bold red] Archivo no encontrado: {file_path}")
        raise typer.Exit(code=1)

    content = file_path.read_text(encoding="utf-8", errors="replace")
    snippets = extraer_snippets_c_compilables(content)
    archivos = exportar_proyecto_c(snippets, output_dir)
    console.print(f"[bold green]✓ Proyecto C exportado en {output_dir} ({len(archivos)} archivos generados).[/bold green]")


@app.command("extract-dict-terms")
def cmd_extract_dict_terms(
    files: Optional[List[Path]] = typer.Argument(None, help="Archivos Markdown a procesar."),
    output_file: Path = typer.Option(Path("./spelling.txt"), "--output", "-o", help="Archivo destino para términos LanguageTool."),
    force: bool = typer.Option(False, "--force", "-f", help="Fuerza la ejecución ignorando myst.yml."),
) -> None:
    """Extrae identificadores técnicos C y directivas para el diccionario personalizado de LanguageTool."""
    from myst_tools.dict_terms_extractor import extraer_terminos_tecnicos_c, exportar_diccionario_languagetool

    _check_myst_yml(force)
    target_files = files or list(Path(".").glob("**/*.md"))
    todos_terminos = set()

    for f in target_files:
        if not f.is_file() or f.suffix.lower() != ".md":
            continue
        content = f.read_text(encoding="utf-8", errors="replace")
        todos_terminos.update(extraer_terminos_tecnicos_c(content))

    cant = exportar_diccionario_languagetool(todos_terminos, output_file)
    console.print(f"[bold green]✓ Diccionario generado en {output_file} con {cant} términos técnicos.[/bold green]")


@app.command("check-links")
def cmd_check_links(
    files: Optional[List[Path]] = typer.Argument(None, help="Archivos Markdown a auditar."),
    force: bool = typer.Option(False, "--force", "-f", help="Fuerza la ejecución ignorando myst.yml."),
    output_json: bool = typer.Option(False, "--json", help="Emite los hallazgos como JSON versionado."),
) -> None:
    """Audita inmutabilidad y sintaxis de enlaces a GitHub."""
    from myst_tools.github_link_auditor import auditar_enlaces_github

    _check_myst_yml(force)
    target_files = files or list(Path(".").glob("**/*.md"))
    total_issues = 0
    hallazgos = []

    for f in target_files:
        if not f.is_file() or f.suffix.lower() != ".md":
            continue
        content = f.read_text(encoding="utf-8", errors="replace")
        issues = auditar_enlaces_github(content)
        for iss in issues:
            total_issues += 1
            hallazgos.append({"archivo": str(f), "linea": iss.line_number,
                              "tipo": iss.issue_type, "mensaje": iss.message})
            if not output_json:
                console.print(f"[bold yellow]{f.name}:{iss.line_number}[/bold yellow] [{iss.issue_type}] {iss.message}")

    if output_json:
        emitir_json("check-links", {"total": total_issues, "hallazgos": hallazgos})
        raise typer.Exit(code=1 if total_issues else 0)

    if total_issues == 0:
        console.print("[bold green]✓ Todos los enlaces a GitHub cumplen con las pautas de inmutabilidad.[/bold green]")
        raise typer.Exit(code=0)
    else:
        raise typer.Exit(code=1)


@app.command("doctor")
def cmd_doctor(
    json_output: bool = typer.Option(False, "--json", help="Emitir diagnóstico en formato JSON estructurado."),
) -> None:
    """Verifica el estado del entorno de MYST-TOOLS (Python, Node/myst, LanguageTool, Typst)."""
    import shutil
    from rich.table import Table
    diagnostico = []

    py_ok = sys.version_info >= (3, 10)
    diagnostico.append({
        "componente": "Python Runtime",
        "estado": "OK" if py_ok else "ERROR",
        "requerido": True,
        "detalle": f"Python {sys.version.split()[0]}",
    })

    myst_path = shutil.which("myst")
    diagnostico.append({
        "componente": "MyST CLI (Node/npm)",
        "estado": "OK" if myst_path else "ADVERTENCIA",
        "requerido": False,
        "detalle": myst_path or "No encontrado (opcional, para compilar HTML/PDF)",
    })

    lt_path = shutil.which("languagetool") or shutil.which("languagetool-server")
    diagnostico.append({
        "componente": "LanguageTool Local",
        "estado": "OK" if lt_path else "ADVERTENCIA",
        "requerido": False,
        "detalle": lt_path or "No encontrado (se usará API remota si no hay servidor local)",
    })

    typst_path = shutil.which("typst")
    diagnostico.append({
        "componente": "Typst CLI",
        "estado": "OK" if typst_path else "ADVERTENCIA",
        "requerido": False,
        "detalle": typst_path or "No encontrado (opcional para exportación Typst)",
    })

    todo_ok = py_ok

    if json_output:
        import json
        payload = {
            "schema_version": "1.0.0",
            "herramienta": "myst-tools",
            "ok": todo_ok,
            "componentes": diagnostico,
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        raise typer.Exit(code=0 if todo_ok else 1)

    tabla = Table(title="🏥 Diagnóstico del Entorno MYST-TOOLS (doctor)", border_style="cyan")
    tabla.add_column("Componente", style="bold white")
    tabla.add_column("Estado", justify="center")
    tabla.add_column("Detalle")

    for c in diagnostico:
        color = "bold green" if c["estado"] == "OK" else ("bold yellow" if c["estado"] == "ADVERTENCIA" else "bold red")
        simbolo = "✓" if c["estado"] == "OK" else ("⚠️" if c["estado"] == "ADVERTENCIA" else "✗")
        tabla.add_row(c["componente"], f"[{color}]{simbolo} {c['estado']}[/{color}]", c["detalle"])

    console.print(tabla)
    if not todo_ok:
        raise typer.Exit(code=1)
