"""Comandos que exponen módulos antes solo-biblioteca: snippets C, Typst, ejercicios, glosario, callouts."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer

from myst_tools._cli_base import _check_myst_yml, app, console, emitir_json

_FORCE = typer.Option(False, "--force", "-f", help="Fuerza la ejecución ignorando myst.yml.")
_JSON = typer.Option(False, "--json", help="Emite el resultado como JSON versionado.")


def _archivos_md(files: Optional[List[Path]]) -> List[Path]:
    objetivos = files or list(Path(".").glob("**/*.md"))
    return [f for f in objetivos if f.is_file() and f.suffix.lower() == ".md"]


@app.command("check-c-snippets")
def cmd_check_c_snippets(
    files: Optional[List[Path]] = typer.Argument(None, help="Archivos Markdown a auditar."),
    force: bool = _FORCE,
    output_json: bool = _JSON,
) -> None:
    """Verifica con `gcc -fsyntax-only` que los bloques ```c compilen (requiere gcc)."""
    from myst_tools.c_snippet_validator import extraer_y_validar_snippets_c

    _check_myst_yml(force)
    resultados = []
    for f in _archivos_md(files):
        for r in extraer_y_validar_snippets_c(f.read_text(encoding="utf-8", errors="replace")):
            resultados.append({"archivo": str(f), **r})
    invalidos = [r for r in resultados if not r["valido"]]

    if output_json:
        emitir_json("check-c-snippets", {"total": len(resultados), "invalidos": len(invalidos), "resultados": resultados})
    else:
        for r in invalidos:
            console.print(f"[bold red]{r['archivo']}[/bold red] bloque {r['bloque']}: {r['detalle']}")
        if not invalidos:
            console.print(f"[bold green]✓ {len(resultados)} bloques C con sintaxis válida.[/bold green]")
    if invalidos:
        raise typer.Exit(code=1)


@app.command("to-typst")
def cmd_to_typst(
    file_path: Path = typer.Argument(..., help="Archivo Markdown MyST a convertir."),
    titulo: str = typer.Option("Apunte de Cátedra", "--titulo", "-t", help="Título del documento Typst."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Archivo .typ de salida (por defecto stdout)."),
    force: bool = _FORCE,
    output_json: bool = _JSON,
) -> None:
    """Convierte encabezados de un MyST Markdown a una plantilla Typst."""
    from myst_tools.typst_exporter import convertir_myst_a_typst

    _check_myst_yml(force)
    if not file_path.is_file():
        typer.echo(f"Error: Archivo no encontrado: {file_path}", err=True)
        raise typer.Exit(code=1)
    typst = convertir_myst_a_typst(file_path.read_text(encoding="utf-8", errors="replace"), titulo=titulo)
    if output:
        output.write_text(typst, encoding="utf-8")
    if output_json:
        emitir_json("to-typst", {"archivo": str(file_path), "salida": str(output) if output else None,
                                 "typst": None if output else typst})
    elif output:
        console.print(f"[bold green]✓ Typst generado en {output}.[/bold green]")
    else:
        typer.echo(typst)


@app.command("extract-exercises")
def cmd_extract_exercises(
    files: Optional[List[Path]] = typer.Argument(None, help="Archivos Markdown con directivas ```{exercise}."),
    force: bool = _FORCE,
    output_json: bool = _JSON,
) -> None:
    """Extrae las directivas {exercise} como candidatos a ejercicios del banco (deckard)."""
    from myst_tools.exercise_extractor import extraer_ejercicios_myst

    _check_myst_yml(force)
    ejercicios = []
    for f in _archivos_md(files):
        for e in extraer_ejercicios_myst(f.read_text(encoding="utf-8", errors="replace")):
            ejercicios.append({"archivo": str(f), **e})
    if output_json:
        emitir_json("extract-exercises", {"total": len(ejercicios), "ejercicios": ejercicios})
        return
    for e in ejercicios:
        console.print(f"[bold]{e['archivo']}[/bold]: {e['titulo']}")
    console.print(f"[bold green]✓ {len(ejercicios)} ejercicios encontrados.[/bold green]")


@app.command("glossary")
def cmd_glossary(
    files: Optional[List[Path]] = typer.Argument(None, help="Archivos Markdown a procesar."),
    force: bool = _FORCE,
    output_json: bool = _JSON,
) -> None:
    """Detecta definiciones tipo **Término**: definición y arma un glosario."""
    from myst_tools.glossary_generator import generar_glosario_terminos

    _check_myst_yml(force)
    glosario = {}
    for f in _archivos_md(files):
        glosario.update(generar_glosario_terminos(f.read_text(encoding="utf-8", errors="replace")))
    if output_json:
        emitir_json("glossary", {"total": len(glosario), "terminos": glosario})
        return
    for termino, definicion in sorted(glosario.items()):
        console.print(f"[bold]{termino}[/bold]: {definicion}")
    console.print(f"[bold green]✓ {len(glosario)} términos.[/bold green]")


@app.command("callout")
def cmd_callout(
    tipo: str = typer.Argument(..., help="note, tip, warning, important o danger (otro valor cae en note)."),
    cuerpo: str = typer.Argument(..., help="Texto del callout."),
    titulo: str = typer.Option("", "--titulo", "-t", help="Título del callout."),
) -> None:
    """Imprime un callout MyST (admonition) con el formato estándar."""
    from myst_tools.callout_injector import formatear_callout

    typer.echo(formatear_callout(tipo, titulo, cuerpo))
