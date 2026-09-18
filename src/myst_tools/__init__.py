"""Herramientas unificadas para automatizar, formatear e indexar material didáctico MyST."""

from importlib.metadata import PackageNotFoundError, version as _metadata_version

try:
    __version__ = _metadata_version("myst-tools")
except PackageNotFoundError:
    __version__ = "desconocida"

from myst_tools.add_myst_anchors import run_add_anchors
from myst_tools.fix_dup_anchors import run_fix_dup_anchors
from myst_tools.generate_apunte_index import run_generate_apunte_index
from myst_tools.generate_guides_index import run_generate_guides_index
from myst_tools.generate_rules_index import run_generate_rules_index
from myst_tools.myst_fmt import run_myst_fmt

from myst_tools.languagetool_checker import (
    analizar_archivo_languagetool,
    aplicar_autofix_archivo,
    generar_reporte_markdown,
    LanguageToolIssue,
)

__all__ = [
    "app",
    "main",
    "run_add_anchors",
    "run_fix_dup_anchors",
    "run_generate_apunte_index",
    "run_generate_guides_index",
    "run_generate_rules_index",
    "run_myst_fmt",
    "analizar_archivo_languagetool",
    "aplicar_autofix_archivo",
    "generar_reporte_markdown",
    "LanguageToolIssue",
]


def __getattr__(name):
    # `app`/`main` viven en myst_tools.cli, que depende de typer/rich. Se cargan
    # perezosamente para que consumidores externos (alucarD, idkfa, moodle-toolbox)
    # puedan importar submódulos livianos (p. ej. languagetool_checker) sin que
    # typer sea una dependencia transitiva obligatoria de todo el paquete.
    if name in ("app", "main"):
        from myst_tools.cli import app, main

        globals()["app"] = app
        globals()["main"] = main
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

