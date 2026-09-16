"""CLI principal de myst-tools unificado con Typer y Rich."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console

from myst_tools.add_myst_anchors import run_add_anchors
from myst_tools.fix_dup_anchors import run_fix_dup_anchors
from myst_tools.generate_apunte_index import run_generate_apunte_index
from myst_tools.generate_guides_index import run_generate_guides_index
from myst_tools.generate_rules_index import run_generate_rules_index
from myst_tools.myst_fmt import run_myst_fmt

console = Console()
err_console = Console(stderr=True)

app = typer.Typer(
    name="myst-tools",
    help="Herramientas unificadas para automatizar, formatear e indexar material didáctico MyST Markdown.",
    no_args_is_help=True,
)

state = {"force": False}


def _check_myst_yml(force: bool = False) -> None:
    if force or state.get("force", False):
        return
    if not os.path.exists("myst.yml"):
        err_console.print(
            "[bold red]Error:[/bold red] El directorio actual no contiene un archivo 'myst.yml'.\n"
            "Este comando debe ejecutarse desde la raíz del proyecto MyST (o usá [bold]--force / -f[/bold] para ignorar esta verificación)."
        )
        raise typer.Exit(code=1)


@app.callback()
def main_callback(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Fuerza la ejecución saliéndose de la verificación de la existencia de 'myst.yml'.",
    ),
) -> None:
    """Opciones globales de myst-tools."""
    if force:
        state["force"] = True


@app.command("add-anchors")
def cmd_add_anchors(
    dir_path: Path = typer.Argument(
        Path("./apunte"),
        help="Directorio que contiene los archivos Markdown del apunte.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Fuerza la ejecución ignorando la verificación de 'myst.yml'.",
    ),
) -> None:
    """Agrega etiquetas/anclas de MyST a los encabezados de archivos Markdown."""
    _check_myst_yml(force)
    run_add_anchors(str(dir_path))


@app.command("gen-apunte")
def cmd_gen_apunte(
    dir_path: Path = typer.Argument(
        Path("./apunte"),
        help="Directorio del apunte (apunte).",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Fuerza la ejecución ignorando la verificación de 'myst.yml'.",
    ),
) -> None:
    """Genera el índice detallado para el apunte de cátedra."""
    _check_myst_yml(force)
    run_generate_apunte_index(str(dir_path))


@app.command("gen-guides")
def cmd_gen_guides(
    dir_path: Path = typer.Argument(
        Path("./guias"),
        help="Directorio que contiene las guías.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Fuerza la ejecución ignorando la verificación de 'myst.yml'.",
    ),
) -> None:
    """Genera el índice para las guías de trabajos prácticos."""
    _check_myst_yml(force)
    run_generate_guides_index(str(dir_path))


@app.command("gen-rules")
def cmd_gen_rules(
    dir_path: Path = typer.Argument(
        Path("./reglas"),
        help="Directorio que contiene las reglas de estilo.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Fuerza la ejecución ignorando la verificación de 'myst.yml'.",
    ),
) -> None:
    """Genera el índice de las reglas de estilo de programación."""
    _check_myst_yml(force)
    run_generate_rules_index(str(dir_path))


@app.command("fix-anchors")
def cmd_fix_anchors(
    dir_path: Path = typer.Argument(
        Path("."),
        help="Directorio raíz a escanear.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Muestra los cambios sin escribir ningún archivo.",
    ),
    report: bool = typer.Option(
        False,
        "--report",
        help="Solo lista los duplicados y termina sin modificar nada.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Fuerza la ejecución ignorando la verificación de 'myst.yml'.",
    ),
) -> None:
    """Detecta y corrige anclas MyST duplicadas."""
    _check_myst_yml(force)
    rc = run_fix_dup_anchors(str(dir_path), dry_run=dry_run, report=report)
    if rc:
        raise typer.Exit(code=rc)


@app.command("fmt")
def cmd_fmt(
    files: Optional[List[str]] = typer.Argument(
        None,
        help="Archivos o directorios a formatear (por defecto, todos los archivos .md si la entrada es interactiva).",
    ),
    check: bool = typer.Option(
        False,
        "--check",
        help="Solo verifica si los archivos necesitan formato.",
    ),
    stdout: bool = typer.Option(
        False,
        "--stdout",
        help="Imprime el resultado a la salida estándar en vez de modificar in-place.",
    ),
    width: int = typer.Option(
        80,
        "--width",
        "-w",
        help="Ancho máximo de línea (default: 80).",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Fuerza la ejecución ignorando la verificación de 'myst.yml'.",
    ),
) -> None:
    """Formatea archivos MyST Markdown (longitud de línea, fences y comentarios)."""
    _check_myst_yml(force)
    target_files = files or []
    rc = run_myst_fmt(target_files, check=check, stdout=stdout, width=width)
    if rc:
        raise typer.Exit(code=rc)


@app.command("spellcheck")
@app.command("grammar")
@app.command("languagetool")
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
) -> None:
    """Audita inmutabilidad y sintaxis de enlaces a GitHub."""
    from myst_tools.github_link_auditor import auditar_enlaces_github

    _check_myst_yml(force)
    target_files = files or list(Path(".").glob("**/*.md"))
    total_issues = 0

    for f in target_files:
        if not f.is_file() or f.suffix.lower() != ".md":
            continue
        content = f.read_text(encoding="utf-8", errors="replace")
        issues = auditar_enlaces_github(content)
        for iss in issues:
            total_issues += 1
            console.print(f"[bold yellow]{f.name}:{iss.line_number}[/bold yellow] [{iss.issue_type}] {iss.message}")

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


def main() -> None:
    app()


if __name__ == "__main__":
    main()
