"""Regresión de MYST-D0202: los módulos solo-biblioteca quedan expuestos como comandos."""

import json
import shutil

import pytest
from typer.testing import CliRunner

from myst_tools.cli import app

runner = CliRunner()
MD = """# Título

**Puntero**: dirección de memoria.

```{exercise} Suma
Escribí una suma.
```

```c
int main(void) { return 0; }
```
"""


@pytest.fixture
def md(tmp_path):
    f = tmp_path / "a.md"
    f.write_text(MD, encoding="utf-8")
    return f


def _j(res):
    assert res.exit_code == 0, res.output
    d = json.loads(res.output)
    assert d["schema_version"] == "1.0.0" and d["herramienta"] == "myst-tools"
    return d


def test_glossary(md):
    d = _j(runner.invoke(app, ["-f", "glossary", str(md), "--json"]))
    assert d["terminos"] == {"Puntero": "dirección de memoria."}


def test_extract_exercises(md):
    d = _j(runner.invoke(app, ["-f", "extract-exercises", str(md), "--json"]))
    assert d["ejercicios"][0]["titulo"] == "Suma"


def test_to_typst(md):
    d = _j(runner.invoke(app, ["-f", "to-typst", str(md), "--json", "-t", "X"]))
    assert "= Título" in d["typst"] and 'title: "X"' in d["typst"]


def test_callout():
    res = runner.invoke(app, ["callout", "tip", "hola", "-t", "Ojo"])
    assert res.exit_code == 0
    assert "```{tip} Ojo" in res.output


@pytest.mark.skipif(shutil.which("gcc") is None, reason="Requiere gcc en PATH")
def test_check_c_snippets(md):
    d = _j(runner.invoke(app, ["-f", "check-c-snippets", str(md), "--json"]))
    assert d["invalidos"] == 0 and d["total"] == 1
