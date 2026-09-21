"""Comandos de índices, anclas y formateo MyST."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer

from myst_tools._cli_base import _check_myst_yml, app
from myst_tools.add_myst_anchors import run_add_anchors
from myst_tools.fix_dup_anchors import run_fix_dup_anchors
from myst_tools.generate_apunte_index import run_generate_apunte_index
from myst_tools.generate_guides_index import run_generate_guides_index
from myst_tools.generate_rules_index import run_generate_rules_index
from myst_tools.myst_fmt import run_myst_fmt


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
