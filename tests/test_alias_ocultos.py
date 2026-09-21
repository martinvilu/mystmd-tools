"""Regresión de MYST-D0403: los alias de spellcheck no deben repetirse en --help."""

from typer.testing import CliRunner

from myst_tools.cli import app

runner = CliRunner()


def _filas(salida: str) -> list[str]:
    return [p for linea in salida.splitlines() for p in linea.split() if p in ("spellcheck", "grammar", "languagetool")]


def test_help_lista_solo_spellcheck():
    res = runner.invoke(app, ["--help"], env={"NO_COLOR": "1", "COLUMNS": "200"})
    assert res.exit_code == 0
    assert _filas(res.output) == ["spellcheck"]


def test_los_alias_siguen_funcionando():
    for alias in ("grammar", "languagetool"):
        res = runner.invoke(app, [alias, "--help"], env={"NO_COLOR": "1"})
        assert res.exit_code == 0, alias
