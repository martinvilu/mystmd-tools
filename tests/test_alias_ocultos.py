"""Regresión de MYST-D0403: los alias de spellcheck no deben repetirse en --help."""

from typer.testing import CliRunner

from myst_tools.cli import app

runner = CliRunner()


import re


def _filas(salida: str) -> list[str]:
    limpia = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", salida)
    return [p for linea in limpia.splitlines() for p in linea.split() if p in ("spellcheck", "grammar", "languagetool")]


def test_help_lista_solo_spellcheck():
    res = runner.invoke(app, ["--help"], env={"NO_COLOR": "1", "COLUMNS": "200"})
    assert res.exit_code == 0
    assert _filas(res.output) == ["spellcheck"]


def test_los_alias_siguen_funcionando():
    for alias in ("grammar", "languagetool"):
        res = runner.invoke(app, [alias, "--help"], env={"NO_COLOR": "1"})
        assert res.exit_code == 0, alias
