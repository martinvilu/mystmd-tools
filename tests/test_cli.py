"""Tests para la interfaz CLI de myst-tools (Typer)."""

import sys
from pathlib import Path
import pytest
import typer
from typer.testing import CliRunner
import myst_tools.cli as cli
from myst_tools.cli import app, main, _check_myst_yml, state

runner = CliRunner()


@pytest.fixture(autouse=True)
def reset_state():
    state["force"] = False
    yield
    state["force"] = False


def test_cli_help():
    res = runner.invoke(app, ["--help"])
    assert res.exit_code == 0
    assert "add-anchors" in res.output
    assert "fix-anchors" in res.output
    assert "gen-apunte" in res.output
    assert "gen-guides" in res.output
    assert "gen-rules" in res.output
    assert "fmt" in res.output


def test_check_myst_yml_direct(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # Sin myst.yml ni force debe fallar
    with pytest.raises(typer.Exit) as exc_info:
        _check_myst_yml(force=False)
    assert exc_info.value.exit_code == 1

    # Con force=True como parámetro
    _check_myst_yml(force=True)

    # Con state["force"] = True
    state["force"] = True
    _check_myst_yml(force=False)
    state["force"] = False

    # Con myst.yml presente
    (tmp_path / "myst.yml").write_text("version: 1\n", encoding="utf-8")
    _check_myst_yml(force=False)


def test_cli_requires_myst_yml_without_force(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["gen-apunte", str(tmp_path)])
    assert res.exit_code == 1
    assert "myst.yml" in res.output


def test_cli_global_force_flag(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    apunte = tmp_path / "apunte"
    apunte.mkdir()
    (apunte / "01_tema.md").write_text("# Tema Uno\n", encoding="utf-8")

    res = runner.invoke(app, ["--force", "gen-apunte", str(apunte)])
    assert res.exit_code == 0
    assert (apunte / "indice.md").is_file()


def test_cli_add_anchors(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "myst.yml").write_text("version: 1\n", encoding="utf-8")
    apunte = tmp_path / "apunte"
    apunte.mkdir()
    (apunte / "01_tema.md").write_text("# Tema Uno\n", encoding="utf-8")

    # Ejecución con ruta default (cuando ./apunte existe)
    res = runner.invoke(app, ["add-anchors"])
    assert res.exit_code == 0
    assert "(tema-uno)=" in (apunte / "01_tema.md").read_text(encoding="utf-8")

    # Ejecución con ruta explícita y --force
    otro_dir = tmp_path / "otro"
    otro_dir.mkdir()
    (otro_dir / "02_tema.md").write_text("# Tema Dos\n", encoding="utf-8")
    res2 = runner.invoke(app, ["add-anchors", str(otro_dir), "--force"])
    assert res2.exit_code == 0
    assert "(tema-dos)=" in (otro_dir / "02_tema.md").read_text(encoding="utf-8")


def test_cli_gen_apunte(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "myst.yml").write_text("version: 1\n", encoding="utf-8")
    apunte = tmp_path / "apunte"
    apunte.mkdir()
    (apunte / "01_tema.md").write_text("# Tema Uno\n", encoding="utf-8")

    # default path
    res = runner.invoke(app, ["gen-apunte"])
    assert res.exit_code == 0
    assert (apunte / "indice.md").is_file()

    # explicit path and -f
    res2 = runner.invoke(app, ["gen-apunte", str(apunte), "-f"])
    assert res2.exit_code == 0


def test_cli_gen_guides(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "myst.yml").write_text("version: 1\n", encoding="utf-8")
    guias = tmp_path / "guias"
    guias.mkdir()
    (guias / "guia1.md").write_text("# Guía 1\n", encoding="utf-8")

    # default path
    res = runner.invoke(app, ["gen-guides"])
    assert res.exit_code == 0
    assert (guias / "indice.md").is_file()

    # explicit path and --force
    res2 = runner.invoke(app, ["gen-guides", str(guias), "--force"])
    assert res2.exit_code == 0


def test_cli_gen_rules(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "myst.yml").write_text("version: 1\n", encoding="utf-8")
    reglas = tmp_path / "reglas"
    reglas.mkdir()
    (reglas / "regla1.md").write_text("(regla-1)=\n## Regla 1\n", encoding="utf-8")

    # default path
    res = runner.invoke(app, ["gen-rules"])
    assert res.exit_code == 0
    assert (reglas / "indice.md").is_file()

    # explicit path and --force
    res2 = runner.invoke(app, ["gen-rules", str(reglas), "--force"])
    assert res2.exit_code == 0


def test_cli_fix_anchors(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "myst.yml").write_text("version: 1\n", encoding="utf-8")
    doc1 = tmp_path / "doc1.md"
    doc2 = tmp_path / "doc2.md"
    doc1.write_text("(dup)=\n# Doc 1\n", encoding="utf-8")
    doc2.write_text("(dup)=\n# Doc 2\n", encoding="utf-8")

    # default path and --report
    res_report = runner.invoke(app, ["fix-anchors", "--report"])
    assert res_report.exit_code == 0

    # --dry-run
    res_dry = runner.invoke(app, ["fix-anchors", str(tmp_path), "--dry-run", "--force"])
    assert res_dry.exit_code == 0

    # fix in place
    res_fix = runner.invoke(app, ["fix-anchors", str(tmp_path), "--force"])
    assert res_fix.exit_code == 0


def test_cli_fix_anchors_with_error_code(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "myst.yml").write_text("version: 1\n", encoding="utf-8")
    # directorio inexistente devuelve rc=2 en run_fix_dup_anchors
    no_dir = tmp_path / "no_existe"
    res = runner.invoke(app, ["fix-anchors", str(no_dir)])
    assert res.exit_code == 2


def test_cli_fmt(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "myst.yml").write_text("version: 1\n", encoding="utf-8")
    doc = tmp_path / "doc.md"
    doc.write_text("# Título\n\nTexto simple.\n", encoding="utf-8")

    # Con archivo especificado y opciones
    res = runner.invoke(app, ["fmt", str(doc), "--width", "80", "--stdout"])
    assert res.exit_code == 0
    assert "# Título" in res.output

    # Sin archivos pasados (files=None)
    res_all = runner.invoke(app, ["fmt", "--force"])
    assert res_all.exit_code == 0

    # Con --check que falla cuando requiere formato
    doc_bad = tmp_path / "bad.md"
    doc_bad.write_text("```{note}\nNota\n```\n", encoding="utf-8")
    res_check = runner.invoke(app, ["fmt", str(doc_bad), "--check", "--force"])
    assert res_check.exit_code == 1


def test_main_function(monkeypatch):
    called = False

    def mock_app():
        nonlocal called
        called = True

    monkeypatch.setattr(cli, "app", mock_app)
    main()
    assert called is True


def test_cli_module_main(monkeypatch, ejecutar_como_main):
    monkeypatch.setattr(sys, "argv", ["myst-tools", "--help"])
    with pytest.raises(SystemExit) as exc_info:
        ejecutar_como_main("myst_tools.cli")
    assert exc_info.value.code == 0


def test_cli_doctor():
    res = runner.invoke(app, ["doctor"])
    assert res.exit_code == 0
    assert "Diagnóstico del Entorno MYST-TOOLS" in res.output

    res_json = runner.invoke(app, ["doctor", "--json"])
    assert res_json.exit_code == 0
    assert '"schema_version": "1.0.0"' in res_json.output
    assert '"herramienta": "myst-tools"' in res_json.output
    assert '"ok": true' in res_json.output

