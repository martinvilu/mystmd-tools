"""Los `check-*` deben recorrer los directorios que reciben (N-MYST-01).

Antes, `myst-tools check-tables apunte/` descartaba el directorio (no es un
archivo), analizaba 0 archivos e informaba «✓ Todas las tablas… son
consistentes». Sobre el apunte real, el mismo check sin argumentos
encontraba 2.720 líneas de avisos.
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from myst_tools.cli import app

runner = CliRunner()

TABLA_ROTA = "# Tema\n\n| a | b |\n|---|---|\n| 1 |\n"
TABLA_SANA = "# Tema\n\n| a | b |\n|---|---|\n| 1 | 2 |\n"


def _apunte(tmp_path: Path) -> Path:
    raiz = tmp_path / "apunte"
    (raiz / "bloque_1").mkdir(parents=True)
    (raiz / "bloque_1" / "tema.md").write_text(TABLA_ROTA, encoding="utf-8")
    (raiz / "_build" / "html").mkdir(parents=True)
    (raiz / "_build" / "html" / "tema.md").write_text(TABLA_ROTA, encoding="utf-8")
    return raiz


def test_directorio_se_recorre_recursivamente(tmp_path: Path):
    raiz = _apunte(tmp_path)
    resultado = runner.invoke(app, ["check-tables", "--force", str(raiz)])
    assert resultado.exit_code == 1, resultado.output
    assert "tema.md" in resultado.output
    assert "consistentes" not in resultado.output


def test_build_se_excluye(tmp_path: Path):
    raiz = _apunte(tmp_path)
    (raiz / "bloque_1" / "tema.md").write_text(TABLA_SANA, encoding="utf-8")
    resultado = runner.invoke(app, ["check-tables", "--force", str(raiz)])
    assert resultado.exit_code == 0, resultado.output


def test_directorio_sin_markdown_es_error_de_uso(tmp_path: Path):
    vacio = tmp_path / "vacio"
    vacio.mkdir()
    for comando in ("check-tables", "check-style", "check-links", "check-c-snippets"):
        resultado = runner.invoke(app, [comando, "--force", str(vacio)])
        assert resultado.exit_code == 2, (comando, resultado.output)


def test_ruta_inexistente_es_error_de_uso(tmp_path: Path):
    resultado = runner.invoke(app, ["check-style", "--force", str(tmp_path / "no_existe")])
    assert resultado.exit_code == 2
