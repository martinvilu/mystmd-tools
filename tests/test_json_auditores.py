"""Regresión de MYST-D0601: --json versionado en los auditores."""

import json

from typer.testing import CliRunner

from myst_tools.cli import app

runner = CliRunner()


def _run(cmd, contenido, tmp_path):
    f = tmp_path / "a.md"
    f.write_text(contenido, encoding="utf-8")
    res = runner.invoke(app, ["-f", cmd, str(f), "--json"])
    d = json.loads(res.output)
    assert d["schema_version"] == "1.0.0" and d["comando"] == cmd
    return res, d


def test_check_tables_json(tmp_path):
    res, d = _run("check-tables", "| a | b |\n|---|---|\n| 1 |\n", tmp_path)
    assert d["total"] == len(d["hallazgos"]) and res.exit_code == (1 if d["total"] else 0)


def test_check_style_json(tmp_path):
    res, d = _run("check-style", "Hacé esto. Tenés que usarlo.\n", tmp_path)
    assert d["total"] == len(d["hallazgos"])


def test_check_links_json(tmp_path):
    res, d = _run("check-links", "[x](https://github.com/o/r/blob/main/a.c)\n", tmp_path)
    assert d["total"] >= 1 and res.exit_code == 1
    assert {"archivo", "linea", "tipo", "mensaje"} <= set(d["hallazgos"][0])
