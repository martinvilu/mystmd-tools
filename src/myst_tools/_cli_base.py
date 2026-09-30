"""Base compartida de la CLI de myst-tools: app Typer, consolas y verificación de myst.yml."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from yutani.cli import CONTEXTO, TyperConErrores, opcion_version
from yutani.textos import traducir

from myst_tools import __version__

console = Console()
err_console = Console(stderr=True)

# Contrato de línea de comandos, errores de datos como mensajes y ayuda de Typer/Click en español,
# desde yutani (N-ECO-14). No usa crear_app porque el callback tiene la opción global --force.
traducir()
app = TyperConErrores(
    context_settings=dict(CONTEXTO),
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


# Directorios que nunca contienen material fuente del apunte.
DIRECTORIOS_EXCLUIDOS = {"_build", "node_modules", ".venv", "venv", ".git", "__pycache__"}


def archivos_markdown(rutas: Optional[List[Path]]) -> List[Path]:
    """Expande las rutas recibidas a la lista de archivos .md a procesar.

    - Sin rutas se recorre el directorio actual.
    - Un directorio se recorre recursivamente; se omiten `_build`, dependencias,
      entornos virtuales y directorios ocultos.
    - Una ruta inexistente, o una selección que no contiene ningún .md, es un
      error de uso (exit 2). Antes un directorio se descartaba en silencio y el
      comando informaba éxito sobre 0 archivos (N-MYST-01).
    """
    objetivos = list(rutas) if rutas else [Path(".")]
    encontrados: List[Path] = []
    for ruta in objetivos:
        if not ruta.exists():
            err_console.print(f"[bold red]Error:[/bold red] no existe la ruta: {ruta}")
            raise typer.Exit(code=2)
        if ruta.is_dir():
            for archivo in sorted(ruta.rglob("*.md")):
                partes = archivo.relative_to(ruta).parts[:-1]
                if any(p in DIRECTORIOS_EXCLUIDOS or p.startswith(".") for p in partes):
                    continue
                if archivo.is_file():
                    encontrados.append(archivo)
        elif ruta.suffix.lower() == ".md":
            encontrados.append(ruta)

    unicos: List[Path] = []
    vistos = set()
    for archivo in encontrados:
        clave = archivo.resolve()
        if clave not in vistos:
            vistos.add(clave)
            unicos.append(archivo)
    if not unicos:
        err_console.print(
            "[bold red]Error:[/bold red] no se encontró ningún archivo Markdown (.md) en: "
            + ", ".join(str(r) for r in objetivos)
        )
        raise typer.Exit(code=2)
    return unicos


@app.callback()
def main_callback(
    version: bool = opcion_version("myst-tools", __version__),  # noqa: ARG001
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


SCHEMA_VERSION = "1.0.0"


def emitir_json(comando: str, datos: dict) -> None:
    """Imprime `datos` como JSON con envoltorio versionado (schema_version, herramienta, comando)."""
    import json

    payload = {"schema_version": SCHEMA_VERSION, "herramienta": "myst-tools", "comando": comando}
    payload.update(datos)
    typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))
