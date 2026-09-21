"""Tests para generadores de índices (apunte, guías, reglas)."""

import sys
from pathlib import Path
from myst_tools.generate_apunte_index import (
    extract_headers as apunte_extract_headers,
    run_generate_apunte_index,
    slugify as apunte_slugify,
    main as apunte_main,
)
from myst_tools.generate_guides_index import (
    extract_file_title as guides_extract_title,
    run_generate_guides_index,
    main as guides_main,
)
from myst_tools.generate_rules_index import (
    extract_file_title as rules_extract_title,
    extract_rules,
    run_generate_rules_index,
    main as rules_main,
)


# --- Tests para generate_apunte_index ---

def test_apunte_slugify_and_extract_headers():
    assert apunte_slugify("Árboles & Grafos 101!") == "arboles-grafos-101"
    headers = apunte_extract_headers("# Titulo\n\n## Sub\n\n### Subsub\n#### Nivel4\n")
    assert len(headers) == 3
    assert headers[0] == ("#", "Titulo")
    assert headers[1] == ("##", "Sub")
    assert headers[2] == ("###", "Subsub")


def test_generate_apunte_index_complete_flow(tmp_path: Path):
    apunte = tmp_path / "apunte"
    apunte.mkdir()
    # Archivo con #, ##, ### y múltiples #
    (apunte / "01_intro.md").write_text(
        "# Introducción a C\n\n## Variables\n\n### Enteros\n\n# Otro H1 en mismo archivo\n",
        encoding="utf-8",
    )
    # Archivo sin H1 (solo H2)
    (apunte / "02_punteros.md").write_text("## Aritmética de Punteros\n", encoding="utf-8")
    # Archivo sin ningún encabezado (debe ser ignorado)
    (apunte / "03_vacio.md").write_text("Texto sin encabezados.\n", encoding="utf-8")
    # Archivo indice.md previo (no debe procesarse como sección)
    (apunte / "indice.md").write_text("# Indice Viejo\n", encoding="utf-8")

    run_generate_apunte_index(str(apunte))

    indice = apunte / "indice.md"
    assert indice.is_file()
    text = indice.read_text(encoding="utf-8")
    assert "# Apunte de Cátedra" in text
    assert "## {doc}`01_intro`" in text
    assert "  * [Variables](01_intro.md#variables)" in text
    assert "    * [Enteros](01_intro.md#enteros)" in text
    assert "## {doc}`02_punteros`" in text
    assert "03_vacio" not in text


def test_generate_apunte_index_nonexistent_and_empty(tmp_path: Path, capsys):
    no_dir = tmp_path / "no_apunte"
    run_generate_apunte_index(str(no_dir))
    assert "Error: El directorio" in capsys.readouterr().out

    empty = tmp_path / "empty_apunte"
    empty.mkdir()
    run_generate_apunte_index(str(empty))
    assert "No se encontraron archivos markdown" in capsys.readouterr().out


def test_generate_apunte_index_main(tmp_path: Path, monkeypatch, ejecutar_como_main):
    apunte = tmp_path / "apunte"
    apunte.mkdir()
    (apunte / "01_test.md").write_text("# Test Apunte\n", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["generate_apunte_index.py", str(apunte)])
    apunte_main()
    assert (apunte / "indice.md").is_file()

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["generate_apunte_index.py"])
    apunte_main()

    # Run as script
    ejecutar_como_main("myst_tools.generate_apunte_index")


# --- Tests para generate_guides_index ---

def test_guides_extract_title():
    fm_content = "---\ntitle: Guía de Algoritmos\n---\n# Otro título\n"
    assert guides_extract_title(fm_content) == "Guía de Algoritmos"

    h1_content = "# Guía Práctica 01\nTexto...\n"
    assert guides_extract_title(h1_content) == "Guía Práctica 01"

    no_title_content = "Texto sin frontmatter ni h1.\n"
    assert guides_extract_title(no_title_content) is None


def test_generate_guides_index_flow(tmp_path: Path):
    guias = tmp_path / "guias"
    guias.mkdir()
    (guias / "guia_01.md").write_text("# Guía 1: Sintaxis Básica\n\nEjercicios.\n", encoding="utf-8")
    (guias / "guia_02.md").write_text("---\ntitle: Guía 2: Punteros\n---\n", encoding="utf-8")
    (guias / "guia_sin_titulo.md").write_text("Solo texto.\n", encoding="utf-8")
    (guias / "indice.md").write_text("# Indice anterior\n", encoding="utf-8")

    run_generate_guides_index(str(guias))

    indice = guias / "indice.md"
    assert indice.is_file()
    text = indice.read_text(encoding="utf-8")
    assert "# Índice de Guías" in text
    assert "* {doc}`guia_01`" in text
    assert "* {doc}`guia_02`" in text
    assert "* {doc}`guia_sin_titulo`" in text


def test_generate_guides_index_nonexistent_and_empty(tmp_path: Path, capsys):
    no_dir = tmp_path / "no_guias"
    run_generate_guides_index(str(no_dir))
    assert "Error: El directorio" in capsys.readouterr().out

    empty = tmp_path / "empty_guias"
    empty.mkdir()
    run_generate_guides_index(str(empty))
    assert "No se encontraron archivos markdown" in capsys.readouterr().out


def test_generate_guides_index_main(tmp_path: Path, monkeypatch, ejecutar_como_main):
    guias = tmp_path / "guias"
    guias.mkdir()
    (guias / "g1.md").write_text("# G1\n", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["generate_guides_index.py", str(guias)])
    guides_main()
    assert (guias / "indice.md").is_file()

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["generate_guides_index.py"])
    guides_main()

    # Run as script
    ejecutar_como_main("myst_tools.generate_guides_index")


# --- Tests para generate_rules_index ---

def test_rules_extract_title_and_rules():
    fm_content = "---\ntitle: Título Frontmatter\n---\n"
    assert rules_extract_title(fm_content) == "Título Frontmatter"

    h1_content = "# Título H1\n"
    assert rules_extract_title(h1_content) == "Título H1"

    none_content = "Texto sin nada\n"
    assert rules_extract_title(none_content) == "Sin título"

    sample = (
        "(regla-var)=\n## Variables\n\n"
        "(regla-func)=\n### Funciones\n\n"
        "(regla-const)=\n#### Constantes\n\n"
        "(otra-cosa)=\n## No regla\n"
    )
    rules = extract_rules(sample)
    assert len(rules) == 3
    assert rules[0] == ("regla-var", "Variables")
    assert rules[1] == ("regla-func", "Funciones")
    assert rules[2] == ("regla-const", "Constantes")


def test_generate_rules_index_flow(tmp_path: Path):
    reglas = tmp_path / "reglas"
    reglas.mkdir()
    (reglas / "nombres.md").write_text(
        "# Reglas de Nomenclatura\n\n(regla-variables)=\n## Variables\n",
        encoding="utf-8",
    )
    # Archivo sin reglas
    (reglas / "general.md").write_text("# General\n\nTexto general sin reglas.\n", encoding="utf-8")
    # Archivos excluidos
    (reglas / "indice.md").write_text("Indice\n", encoding="utf-8")
    (reglas / "indice_nuevo.md").write_text("Indice nuevo\n", encoding="utf-8")
    (reglas / "reglas_.md").write_text("Reglas draft\n", encoding="utf-8")
    (reglas / "convenciones_codigo_java.md").write_text("Java\n", encoding="utf-8")
    (reglas / "reglas.md").write_text("Reglas root\n", encoding="utf-8")

    run_generate_rules_index(str(reglas))

    indice = reglas / "indice.md"
    assert indice.is_file()
    text = indice.read_text(encoding="utf-8")
    assert "# Índice de Reglas de Estilo" in text
    assert "## Reglas de Nomenclatura" in text
    assert "* {ref}`regla-variables`" in text
    assert "General" not in text


def test_generate_rules_index_nonexistent_and_empty(tmp_path: Path, capsys):
    no_dir = tmp_path / "no_reglas"
    run_generate_rules_index(str(no_dir))
    assert "Error: El directorio" in capsys.readouterr().out

    empty = tmp_path / "empty_reglas"
    empty.mkdir()
    # Crear un archivo de la lista excluida para que no queden archivos válidos
    (empty / "indice_nuevo.md").write_text("test", encoding="utf-8")
    run_generate_rules_index(str(empty))
    assert "No se encontraron archivos markdown" in capsys.readouterr().out


def test_generate_rules_index_main(tmp_path: Path, monkeypatch, ejecutar_como_main):
    reglas = tmp_path / "reglas"
    reglas.mkdir()
    (reglas / "r1.md").write_text("(regla-1)=\n## Regla 1\n", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["generate_rules_index.py", str(reglas)])
    rules_main()
    assert (reglas / "indice.md").is_file()

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["generate_rules_index.py"])
    rules_main()

    # Run as script
    ejecutar_como_main("myst_tools.generate_rules_index")
