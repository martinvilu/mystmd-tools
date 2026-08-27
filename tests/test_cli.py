"""Tests para la interfaz CLI de myst-tools (Typer)."""

from pathlib import Path
from typer.testing import CliRunner
from myst_tools.cli import app

runner = CliRunner()


def test_cli_help():
    res = runner.invoke(app, ["--help"])
    assert res.exit_code == 0
    assert "add-anchors" in res.stdout
    assert "fix-anchors" in res.stdout
    assert "gen-apunte" in res.stdout
    assert "gen-guides" in res.stdout
    assert "gen-rules" in res.stdout
    assert "fmt" in res.stdout


def test_cli_requires_myst_yml_without_force(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["gen-apunte", str(tmp_path)])
    assert res.exit_code == 1
    assert "myst.yml" in res.stderr or "myst.yml" in res.stdout


def test_cli_with_force_flag(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    apunte = tmp_path / "apunte"
    apunte.mkdir()
    (apunte / "01_tema.md").write_text("# Tema Uno\n", encoding="utf-8")

    res = runner.invoke(app, ["--force", "gen-apunte", str(apunte)])
    assert res.exit_code == 0
    assert (apunte / "indice.md").is_file()


def test_cli_fmt_command(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "myst.yml").write_text("version: 1\n", encoding="utf-8")
    doc = tmp_path / "doc.md"
    doc.write_text("# Título\n\nTexto simple.\n", encoding="utf-8")

    res = runner.invoke(app, ["fmt", str(doc)])
    assert res.exit_code == 0
