"""Comandos spellcheck (LanguageTool) y report."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer

from myst_tools._cli_base import _check_myst_yml, app, console


@app.command("spellcheck")
@app.command("grammar", hidden=True)
@app.command("languagetool", hidden=True)
def cmd_spellcheck(
    paths: Optional[List[Path]] = typer.Argument(
        None,
        help="Archivos .md o directorios a revisar con LanguageTool (por defecto todo el apunte/guías).",
    ),
    fix: bool = typer.Option(
        False,
        "--fix",
        "-f",
        help="Aplica automáticamente las sugerencias de corrección ortográfica y gramatical.",
    ),
    lang: str = typer.Option(
        "es-AR",
        "--lang",
        "-l",
        help="Código de idioma para LanguageTool (ej: 'es-AR', 'es', 'en-US').",
    ),
    server: Optional[str] = typer.Option(
        None,
        "--server",
        "-s",
        help="URL del servidor LanguageTool (por defecto http://localhost:8081 y API pública).",
    ),
    username: Optional[str] = typer.Option(
        None,
        "--username",
        "-u",
        help="Usuario / correo de LanguageTool Premium.",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        "-k",
        help="API Key / Token de LanguageTool Premium.",
    ),
    premium: bool = typer.Option(
        False,
        "--premium",
        help="Fuerza el uso de la API LanguageTool Premium (https://api.languagetoolplus.com/v2/check).",
    ),
    ignore_rules: Optional[str] = typer.Option(
        None,
        "--ignore-rules",
        help="Reglas a ignorar separadas por comas (ej: 'MORFOLOGIK_RULE_ES,UPPERCASE_SENTENCE_START').",
    ),
    ignore_words: Optional[str] = typer.Option(
        None,
        "--ignore-words",
        help="Palabras personalizadas a ignorar separadas por comas.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Emite salida estructurada en formato JSON.",
    ),
    output_md: Optional[Path] = typer.Option(
        None,
        "--md",
        "--output-md",
        "-o",
        help="Genera reporte en formato Markdown para fusión en Dredd o documentación.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Fuerza la ejecución ignorando la verificación de 'myst.yml'.",
    ),
) -> None:
    """Verifica y corrige ortografía y gramática en documentos MyST Markdown usando LanguageTool."""
    import json
    from rich.table import Table
    from rich.panel import Panel
    from myst_tools.languagetool_checker import (
        analizar_archivo_languagetool,
        aplicar_autofix_archivo,
        generar_reporte_markdown,
    )

    _check_myst_yml(force)

    # Descubrir archivos
    archivos_a_revisar: List[Path] = []
    if paths:
        for p in paths:
            if p.is_file() and p.suffix.lower() == ".md":
                archivos_a_revisar.append(p)
            elif p.is_dir():
                archivos_a_revisar.extend(sorted(p.glob("**/*.md")))
    else:
        for folder_name in ("apunte", "guias", "reglas"):
            f_dir = Path(folder_name)
            if f_dir.is_dir():
                archivos_a_revisar.extend(sorted(f_dir.glob("**/*.md")))
        if not archivos_a_revisar:
            archivos_a_revisar = sorted(Path(".").glob("**/*.md"))

    if not archivos_a_revisar:
        console.print("[yellow]No se encontraron archivos Markdown (.md) para analizar.[/yellow]")
        raise typer.Exit(code=0)

    reglas_ign = set(r.strip() for r in ignore_rules.split(",") if r.strip()) if ignore_rules else None
    palabras_ign = set(w.strip() for w in ignore_words.split(",") if w.strip()) if ignore_words else None

    todos_los_issues = []
    total_arreglos = 0

    for arch in archivos_a_revisar:
        issues_arch = analizar_archivo_languagetool(
            arch,
            lang=lang,
            server_url=server,
            username=username,
            api_key=api_key,
            premium=premium,
            ignore_words=palabras_ign,
            ignore_rules=reglas_ign,
        )
        if fix and issues_arch:
            arreglos = aplicar_autofix_archivo(arch, issues_arch)
            total_arreglos += arreglos
        todos_los_issues.extend(issues_arch)

    if output_md:
        md_text = generar_reporte_markdown(todos_los_issues)
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_md.write_text(md_text, encoding="utf-8")
        console.print(f"[bold green]✓ Reporte Markdown generado en:[/bold green] [cyan]{output_md}[/cyan]")
        raise typer.Exit(code=0 if not todos_los_issues else 1)

    if json_output:
        res = {
            "total_archivos": len(archivos_a_revisar),
            "total_issues": len(todos_los_issues),
            "total_arreglos": total_arreglos,
            "issues": [i.to_dict() for i in todos_los_issues],
        }
        print(json.dumps(res, indent=2, ensure_ascii=False))
        raise typer.Exit(code=0 if not todos_los_issues else 1)

    if not todos_los_issues:
        console.print(Panel(
            f"[bold green]✓ Ortografía y Gramática Impecables[/bold green]\n"
            f"• Archivos analizados: {len(archivos_a_revisar)}\n"
            f"• Idioma: {lang}\n"
            f"• No se detectaron errores con LanguageTool.",
            title="[bold green]LanguageTool MyST Checker[/bold green]",
            border_style="green",
        ))
        raise typer.Exit(code=0)

    tabla = Table(title=f"Observaciones de LanguageTool ({len(todos_los_issues)} encontradas)", show_header=True)
    tabla.add_column("Ubicación", style="cyan")
    tabla.add_column("Palabra / Error", style="bold red")
    tabla.add_column("Regla", style="yellow")
    tabla.add_column("Sugerencia", style="green")
    tabla.add_column("Diagnóstico", style="white")

    for iss in todos_los_issues:
        sug_txt = ", ".join(iss.replacements[:2]) if iss.replacements else "[dim]N/A[/dim]"
        tabla.add_row(
            f"{iss.file_path.name}:{iss.line}:{iss.column}",
            iss.original_word or iss.context[:20],
            iss.rule_id,
            sug_txt,
            iss.message[:60],
        )

    console.print(tabla)

    if fix and total_arreglos > 0:
        console.print(f"\n[bold green]✓ Se aplicaron automáticamente {total_arreglos} correcciones ortográficas/gramaticales.[/bold green]")
    elif not fix:
        console.print("\n[dim]💡 Ejecutá con '--fix' o '-f' para aplicar automáticamente las correcciones sugeridas.[/dim]")

    raise typer.Exit(code=1)


@app.command("report")
def cmd_report(
    paths: Optional[List[Path]] = typer.Argument(
        None,
        help="Archivos .md o directorios a auditar.",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Ruta de destino del archivo Markdown.",
    ),
    lang: str = typer.Option(
        "es-AR",
        "--lang",
        "-l",
        help="Código de idioma para LanguageTool.",
    ),
    server: Optional[str] = typer.Option(
        None,
        "--server",
        "-s",
        help="URL del servidor LanguageTool.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Fuerza la ejecución ignorando 'myst.yml'.",
    ),
) -> None:
    """Genera directamente la sección de reporte Markdown de LanguageTool para Dredd o documentación."""
    from myst_tools.languagetool_checker import analizar_archivo_languagetool, generar_reporte_markdown

    _check_myst_yml(force)
    archivos: List[Path] = []
    if paths:
        for p in paths:
            if p.is_file() and p.suffix.lower() == ".md":
                archivos.append(p)
            elif p.is_dir():
                archivos.extend(sorted(p.glob("**/*.md")))
    else:
        for folder_name in ("apunte", "guias", "reglas"):
            f_dir = Path(folder_name)
            if f_dir.is_dir():
                archivos.extend(sorted(f_dir.glob("**/*.md")))
        if not archivos:
            archivos = sorted(Path(".").glob("**/*.md"))

    todos_los_issues = []
    for arch in archivos:
        todos_los_issues.extend(analizar_archivo_languagetool(arch, lang=lang, server_url=server))

    md_content = generar_reporte_markdown(todos_los_issues)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(md_content, encoding="utf-8")
        console.print(f"[bold green]✓ Reporte Markdown generado en:[/bold green] [cyan]{output}[/cyan]")
    else:
        print(md_content)
