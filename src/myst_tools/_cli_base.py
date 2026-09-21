"""Base compartida de la CLI de myst-tools: app Typer, consolas y verificación de myst.yml."""

from __future__ import annotations

import os
from typing import Optional

import typer
from rich.console import Console


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


def _version_callback(value: bool) -> None:
    if value:
        from myst_tools import __version__
        console.print(f"[bold cyan]MYST-TOOLS[/bold cyan] versión [bold]{__version__}[/bold]")
        raise typer.Exit(code=0)


@app.callback()
def main_callback(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", help="Muestra la versión y termina.",
        callback=_version_callback, is_eager=True,
    ),
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
