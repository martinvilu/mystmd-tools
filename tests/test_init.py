"""Tests para la inicialización y exportaciones de myst_tools."""

import myst_tools


def test_package_exports():
    expected_all = [
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
    assert myst_tools.__all__ == expected_all
    for symbol in expected_all:
        assert hasattr(myst_tools, symbol)
