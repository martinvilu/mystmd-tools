"""Comandos de auditoría de tablas y estilo."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer
from rich.markup import escape

from myst_tools._cli_base import _check_myst_yml, app, archivos_markdown, console, emitir_json


@app.command("check-tables")
def cmd_check_tables(
    files: Optional[List[Path]] = typer.Argument(
        None,
        help="Archivos Markdown a auditar.",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Fuerza la ejecución ignorando myst.yml."),
    output_json: bool = typer.Option(False, "--json", help="Emite los hallazgos como JSON versionado."),
) -> None:
    """Audita tablas Markdown en busca de columnas desalineadas o separadores inválidos."""
    from myst_tools.table_auditor import parse_markdown_tables, auditar_tabla

    _check_myst_yml(force)
    target_files = archivos_markdown(files)
    total_issues = 0
    hallazgos = []

    for f in target_files:
        if not f.is_file() or f.suffix.lower() != ".md":
            continue
        content = f.read_text(encoding="utf-8", errors="replace")
        tables = parse_markdown_tables(content)
        for tbl in tables:
            issues = auditar_tabla(tbl["raw_rows"], start_line=tbl["start_line"])
            for iss in issues:
                total_issues += 1
                hallazgos.append({"archivo": str(f), "linea": iss.line_number, "mensaje": iss.message})
                if not output_json:
                    console.print(f"[bold red]{f.name}:{iss.line_number}[/bold red]: {iss.message}")

    if output_json:
        emitir_json("check-tables", {"total": total_issues, "hallazgos": hallazgos})
        raise typer.Exit(code=1 if total_issues else 0)

    if total_issues == 0:
        console.print("[bold green]✓ Todas las tablas Markdown son consistentes.[/bold green]")
        raise typer.Exit(code=0)
    else:
        raise typer.Exit(code=1)


@app.command("fmt-tables")
def cmd_fmt_tables(
    files: Optional[List[Path]] = typer.Argument(
        None,
        help="Archivos Markdown a formatear.",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Fuerza la ejecución ignorando myst.yml."),
) -> None:
    """Formatea y alinea visualmente las columnas de tablas Markdown."""
    from myst_tools.table_auditor import parse_markdown_tables, formatear_tabla

    _check_myst_yml(force)
    target_files = archivos_markdown(files)
    modificados = 0

    for f in target_files:
        if not f.is_file() or f.suffix.lower() != ".md":
            continue
        content = f.read_text(encoding="utf-8", errors="replace")
        tables = parse_markdown_tables(content)
        if not tables:
            continue
        new_content = content
        for tbl in tables:
            original_chunk = "\n".join(tbl["raw_rows"])
            formatted_chunk = "\n".join(formatear_tabla(tbl["raw_rows"]))
            new_content = new_content.replace(original_chunk, formatted_chunk, 1)

        if new_content != content:
            f.write_text(new_content, encoding="utf-8")
            modificados += 1

    console.print(f"[bold green]✓ Tablas formateadas en {modificados} archivos.[/bold green]")


@app.command("check-style")
def cmd_check_style(
    files: Optional[List[Path]] = typer.Argument(
        None,
        help="Archivos Markdown a auditar en estilo rioplatense.",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Fuerza la ejecución ignorando myst.yml."),
    output_json: bool = typer.Option(False, "--json", help="Emite los hallazgos como JSON versionado."),
) -> None:
    """Audita estilo rioplatense (voseo vs tuteo, spanglish)."""
    from myst_tools.rioplatense_checker import auditar_estilo_rioplatense

    _check_myst_yml(force)
    target_files = archivos_markdown(files)
    total_issues = 0
    hallazgos = []

    for f in target_files:
        if not f.is_file() or f.suffix.lower() != ".md":
            continue
        content = f.read_text(encoding="utf-8", errors="replace")
        issues = auditar_estilo_rioplatense(content)
        for iss in issues:
            total_issues += 1
            hallazgos.append({"archivo": str(f), "linea": iss.line_number, "columna": iss.column,
                              "regla": iss.rule_type, "mensaje": iss.message})
            if not output_json:
                console.print(f"[yellow]{f.name}:{iss.line_number}:{iss.column}[/yellow] [{iss.rule_type}] {iss.message}")

    if output_json:
        emitir_json("check-style", {"total": total_issues, "hallazgos": hallazgos})
        raise typer.Exit(code=1 if total_issues else 0)

    if total_issues == 0:
        console.print("[bold green]✓ Estilo rioplatense consistente.[/bold green]")
        raise typer.Exit(code=0)
    else:
        raise typer.Exit(code=1)


@app.command("check-a11y")
def cmd_check_a11y(
    files: Optional[List[Path]] = typer.Argument(
        None,
        help="Archivos o directorios Markdown a auditar.",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Fuerza la ejecución ignorando myst.yml."),
    strict: bool = typer.Option(False, "--strict", help="Sale con 1 también por los avisos, no solo por los errores."),
    output_json: bool = typer.Option(False, "--json", help="Emite los hallazgos como JSON versionado."),
) -> None:
    """Audita accesibilidad: texto alternativo, orden de encabezados, enlaces genéricos y contraste."""
    from myst_tools.a11y_checker import auditar_accesibilidad

    _check_myst_yml(force)
    target_files = archivos_markdown(files)
    hallazgos = []
    for f in target_files:
        content = f.read_text(encoding="utf-8", errors="replace")
        for h in auditar_accesibilidad(content):
            hallazgos.append({"archivo": str(f), "linea": h.linea, "regla": h.regla,
                              "severidad": h.severidad, "mensaje": h.mensaje})
            if not output_json:
                color = "bold red" if h.severidad == "error" else "yellow"
                console.print(f"[{color}]{f}:{h.linea}[/{color}] {escape(f'[{h.regla}]')} {escape(h.mensaje)}")

    errores = sum(1 for h in hallazgos if h["severidad"] == "error")
    avisos = len(hallazgos) - errores
    codigo = 1 if errores or (strict and avisos) else 0
    if output_json:
        emitir_json("check-a11y", {"total": len(hallazgos), "errores": errores, "avisos": avisos,
                                   "hallazgos": hallazgos})
        raise typer.Exit(code=codigo)
    archivos = f"{len(target_files)} archivo{'s' if len(target_files) != 1 else ''}"
    if not hallazgos:
        console.print(f"[bold green]✓ Sin problemas de accesibilidad en {archivos}.[/bold green]")
    else:
        console.print(f"\n{errores} errores y {avisos} avisos de accesibilidad en {archivos}.")
    raise typer.Exit(code=codigo)
