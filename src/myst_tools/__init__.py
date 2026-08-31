"""Herramientas unificadas para automatizar, formatear e indexar material didáctico MyST."""

from myst_tools.cli import app, main
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

