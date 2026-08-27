"""Tests para el generador de anclas add_myst_anchors."""

from pathlib import Path
from myst_tools.add_myst_anchors import process_file, run_add_anchors, slugify


def test_slugify():
    assert slugify("Introducción a Punteros") == "introduccion-a-punteros"
    assert slugify("  ¡Hola Mundo! #123  ") == "hola-mundo-123"
    assert slugify("Árboles Binarios & Grafos") == "arboles-binarios-grafos"


def test_process_file_adds_anchors(tmp_path: Path):
    doc = tmp_path / "01_tema.md"
    doc.write_text(
        "# Introducción General\n\nTexto descriptivo.\n\n## Subtema Primero\n\nContenido.\n",
        encoding="utf-8",
    )

    changed = process_file(doc)
    assert changed is True

    result = doc.read_text(encoding="utf-8")
    assert "(introduccion-general)=\n# Introducción General" in result
    assert "(subtema-primero)=\n## Subtema Primero" in result


def test_process_file_preserves_or_updates_existing_label(tmp_path: Path):
    doc = tmp_path / "02_tema.md"
    doc.write_text(
        "(viejo-slug)=\n# Título Nuevo\n",
        encoding="utf-8",
    )

    changed = process_file(doc)
    assert changed is True
    result = doc.read_text(encoding="utf-8")
    assert "(titulo-nuevo)=\n# Título Nuevo" in result


def test_run_add_anchors(tmp_path: Path):
    apunte = tmp_path / "apunte"
    apunte.mkdir()
    (apunte / "01_punteros.md").write_text("# Punteros en C\n", encoding="utf-8")
    (apunte / "indice.md").write_text("# Índice\n", encoding="utf-8")

    run_add_anchors(str(apunte))

    content = (apunte / "01_punteros.md").read_text(encoding="utf-8")
    assert "(punteros-en-c)=\n# Punteros en C" in content
    # indice.md no debe ser tocado
    assert "(indice)=" not in (apunte / "indice.md").read_text(encoding="utf-8")
