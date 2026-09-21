"""Comandos de auditoría de tablas y estilo."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer

from myst_tools._cli_base import _check_myst_yml, app, console


@app.command("check-tables")
def cmd_check_tables(
    files: Optional[List[Path]] = typer.Argument(
        None,
        help="Archivos Markdown a auditar.",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Fuerza la ejecución ignorando myst.yml."),
) -> None:
    """Audita tablas Markdown en busca de columnas desalineadas o separadores inválidos."""
    from myst_tools.table_auditor import parse_markdown_tables, auditar_tabla

    _check_myst_yml(force)
    target_files = files or list(Path(".").glob("**/*.md"))
    total_issues = 0

    for f in target_files:
        if not f.is_file() or f.suffix.lower() != ".md":
            continue
        content = f.read_text(encoding="utf-8", errors="replace")
        tables = parse_markdown_tables(content)
        for tbl in tables:
            issues = auditar_tabla(tbl["raw_rows"], start_line=tbl["start_line"])
            for iss in issues:
                total_issues += 1
                console.print(f"[bold red]{f.name}:{iss.line_number}[/bold red]: {iss.message}")

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
    target_files = files or list(Path(".").glob("**/*.md"))
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
) -> None:
    """Audita estilo rioplatense (voseo vs tuteo, spanglish)."""
    from myst_tools.rioplatense_checker import auditar_estilo_rioplatense

    _check_myst_yml(force)
    target_files = files or list(Path(".").glob("**/*.md"))
    total_issues = 0

    for f in target_files:
        if not f.is_file() or f.suffix.lower() != ".md":
            continue
        content = f.read_text(encoding="utf-8", errors="replace")
        issues = auditar_estilo_rioplatense(content)
        for iss in issues:
            total_issues += 1
            console.print(f"[yellow]{f.name}:{iss.line_number}:{iss.column}[/yellow] [{iss.rule_type}] {iss.message}")

    if total_issues == 0:
        console.print("[bold green]✓ Estilo rioplatense consistente.[/bold green]")
        raise typer.Exit(code=0)
    else:
        raise typer.Exit(code=1)
