"""Tests para el generador de anclas add_myst_anchors."""

import sys
from pathlib import Path
import pytest
from myst_tools.add_myst_anchors import process_file, run_add_anchors, slugify, main


def test_slugify():
    assert slugify("Introducción a Punteros") == "introduccion-a-punteros"
    assert slugify("  ¡Hola Mundo! #123  ") == "hola-mundo-123"
    assert slugify("Árboles Binarios & Grafos") == "arboles-binarios-grafos"
    assert slugify("---Texto--Con--Guiones---") == "texto-con-guiones"


def test_process_file_adds_anchors(tmp_path: Path):
    doc = tmp_path / "01_tema.md"
    doc.write_text(
        "# Introducción General\n\nTexto descriptivo.\n\n## Subtema Primero\n\nContenido.\n\n### Subsub\n",
        encoding="utf-8",
    )

    changed = process_file(doc)
    assert changed is True

    result = doc.read_text(encoding="utf-8")
    assert "(introduccion-general)=\n# Introducción General" in result
    assert "(subtema-primero)=\n## Subtema Primero" in result
    assert "(subsub)=\n### Subsub" in result


def test_process_file_preserves_existing_exact_label(tmp_path: Path):
    doc = tmp_path / "02_tema.md"
    doc.write_text(
        "(titulo-existente)=\n# Titulo Existente\n\n(subtitulo)=\n## Subtitulo\n",
        encoding="utf-8",
    )

    changed = process_file(doc)
    assert changed is False


def test_process_file_updates_outdated_label(tmp_path: Path):
    doc = tmp_path / "03_tema.md"
    doc.write_text(
        "(viejo-slug)=\n# Título Nuevo\n",
        encoding="utf-8",
    )

    changed = process_file(doc)
    assert changed is True
    result = doc.read_text(encoding="utf-8")
    assert "(titulo-nuevo)=\n# Título Nuevo" in result
    assert "(viejo-slug)=" not in result


def test_process_file_with_myst_roles_in_title(tmp_path: Path):
    doc = tmp_path / "04_tema.md"
    doc.write_text(
        "# Header con ｛ref｝`regla-especial` en título\n",
        encoding="utf-8",
    )

    changed = process_file(doc)
    assert changed is True
    result = doc.read_text(encoding="utf-8")
    assert "(header-con-regla-especial-en-titulo)=" in result


def test_process_file_no_headers(tmp_path: Path):
    doc = tmp_path / "no_headers.md"
    doc.write_text("Solo texto sin encabezados.\nOtra línea.\n", encoding="utf-8")

    changed = process_file(doc)
    assert changed is False


def test_run_add_anchors_workflow(tmp_path: Path, capsys):
    apunte = tmp_path / "apunte"
    apunte.mkdir()
    (apunte / "01_punteros.md").write_text("# Punteros en C\n", encoding="utf-8")
    (apunte / "indice.md").write_text("# Índice\n", encoding="utf-8")
    (apunte / "ignore.txt").write_text("no markdown\n", encoding="utf-8")

    run_add_anchors(str(apunte))

    content = (apunte / "01_punteros.md").read_text(encoding="utf-8")
    assert "(punteros-en-c)=\n# Punteros en C" in content
    # indice.md no debe ser tocado
    assert "(indice)=" not in (apunte / "indice.md").read_text(encoding="utf-8")

    out = capsys.readouterr().out
    assert "Actualizado: 01_punteros.md" in out
    assert "Proceso completado. Se actualizaron 1 archivos." in out


def test_run_add_anchors_no_changes(tmp_path: Path, capsys):
    apunte = tmp_path / "apunte"
    apunte.mkdir()
    (apunte / "01_punteros.md").write_text("(punteros-en-c)=\n# Punteros en C\n", encoding="utf-8")

    run_add_anchors(str(apunte))

    out = capsys.readouterr().out
    assert "No se realizaron cambios o no se encontraron archivos markdown." in out


def test_run_add_anchors_nonexistent_dir(tmp_path: Path, capsys):
    no_dir = tmp_path / "no_dir"
    run_add_anchors(str(no_dir))
    out = capsys.readouterr().out
    assert "Error: El directorio" in out


def test_add_myst_anchors_main_with_args(tmp_path: Path, monkeypatch):
    apunte = tmp_path / "custom_apunte"
    apunte.mkdir()
    (apunte / "01_test.md").write_text("# Test Main\n", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["add_myst_anchors.py", str(apunte)])
    main()

    content = (apunte / "01_test.md").read_text(encoding="utf-8")
    assert "(test-main)=" in content


def test_add_myst_anchors_main_default_arg(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    apunte = tmp_path / "apunte"
    apunte.mkdir()
    (apunte / "01_test.md").write_text("# Test Default\n", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["add_myst_anchors.py"])
    main()

    content = (apunte / "01_test.md").read_text(encoding="utf-8")
    assert "(test-default)=" in content


def test_add_myst_anchors_run_as_script(tmp_path: Path, monkeypatch, ejecutar_como_main):
    monkeypatch.chdir(tmp_path)
    apunte = tmp_path / "apunte"
    apunte.mkdir()
    (apunte / "01_script.md").write_text("# Script Test\n", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["add_myst_anchors.py", str(apunte)])
    ejecutar_como_main("myst_tools.add_myst_anchors")

    content = (apunte / "01_script.md").read_text(encoding="utf-8")
    assert "(script-test)=" in content
