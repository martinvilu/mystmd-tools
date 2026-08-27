"""Tests para generadores de índices (apunte, guías, reglas)."""

from pathlib import Path
from myst_tools.generate_apunte_index import run_generate_apunte_index
from myst_tools.generate_guides_index import run_generate_guides_index
from myst_tools.generate_rules_index import run_generate_rules_index


def test_generate_apunte_index(tmp_path: Path):
    apunte = tmp_path / "apunte"
    apunte.mkdir()
    (apunte / "01_intro.md").write_text("# Introducción a C\n\n## Variables\n\n### Enteros\n", encoding="utf-8")
    (apunte / "02_punteros.md").write_text("# Punteros y Memoria\n\n## Aritmética\n", encoding="utf-8")

    run_generate_apunte_index(str(apunte))

    indice = apunte / "indice.md"
    assert indice.is_file()
    text = indice.read_text(encoding="utf-8")
    assert "# Apunte de Cátedra" in text
    assert "{doc}`01_intro`" in text
    assert "{doc}`02_punteros`" in text


def test_generate_guides_index(tmp_path: Path):
    guias = tmp_path / "guias"
    guias.mkdir()
    (guias / "guia_01.md").write_text("# Guía 1: Sintaxis Básica\n\nEjercicios iniciales.\n", encoding="utf-8")
    (guias / "guia_02.md").write_text("---\ntitle: Guía 2: Punteros\n---\n\nEjercicios de punteros.\n", encoding="utf-8")

    run_generate_guides_index(str(guias))

    indice = guias / "indice.md"
    assert indice.is_file()
    text = indice.read_text(encoding="utf-8")
    assert "# Índice de Guías" in text
    assert "{doc}`guia_01`" in text
    assert "{doc}`guia_02`" in text


def test_generate_rules_index(tmp_path: Path):
    reglas = tmp_path / "reglas"
    reglas.mkdir()
    (reglas / "nombres.md").write_text(
        "# Reglas de Nomenclatura\n\n(regla-variables)=\n## Nombres de Variables\n\n(regla-funciones)=\n### Nombres de Funciones\n",
        encoding="utf-8",
    )

    run_generate_rules_index(str(reglas))

    indice = reglas / "indice.md"
    assert indice.is_file()
    text = indice.read_text(encoding="utf-8")
    assert "# Índice de Reglas de Estilo" in text
    assert "{ref}`regla-variables`" in text
    assert "{ref}`regla-funciones`" in text
