"""Tests para el corrector de anclas duplicadas fix_dup_anchors."""

import pytest
from pathlib import Path
from myst_tools.fix_dup_anchors import (
    apply_to_file,
    build_rename_map,
    collect_anchors,
    run_fix_dup_anchors,
)


def test_collect_anchors_finds_duplicates(tmp_path: Path):
    f1 = tmp_path / "01_intro.md"
    f2 = tmp_path / "02_avanzado.md"

    f1.write_text("(resumen)=\n# Resumen 1\n(resumen)=\n## Repetido en mismo archivo\n", encoding="utf-8")
    f2.write_text("(resumen)=\n# Resumen 2\n:label: etiqueta-dir\n", encoding="utf-8")

    anchors = collect_anchors([f1, f2])
    assert "resumen" in anchors
    assert len(anchors["resumen"]) == 2
    assert "etiqueta-dir" in anchors
    assert len(anchors["etiqueta-dir"]) == 1


def test_collect_anchors_handles_read_error(tmp_path: Path, monkeypatch, capsys):
    f1 = tmp_path / "01_intro.md"
    f1.write_text("(resumen)=\n# Resumen\n", encoding="utf-8")

    def mock_read_text(self, *args, **kwargs):
        raise OSError("Permission denied")

    monkeypatch.setattr(Path, "read_text", mock_read_text)
    anchors = collect_anchors([f1])
    assert anchors == {}
    err = capsys.readouterr().err
    assert "Error al leer" in err


def test_build_rename_map_with_collisions(tmp_path: Path):
    f1 = tmp_path / "doc.md"
    f2 = tmp_path / "otro.md"

    # Caso donde el candidato "doc-resumen" ya existe en all_labels y además "doc-resumen-2" existe
    duplicates = {"resumen": [f1, f2]}
    all_labels = {
        "resumen": [f1, f2],
        "doc-resumen": [f1],
        "doc-resumen-2": [f1],
    }

    renames = build_rename_map(duplicates, all_labels)
    assert renames["resumen"][f1] == "doc-resumen-3"
    assert renames["resumen"][f2] == "otro-resumen"


def test_apply_to_file_all_constructs(tmp_path: Path):
    doc = tmp_path / "01_intro.md"
    doc.write_text(
        "(resumen)=\n"
        ":label: dir_lbl\n"
        "(no_cambia)=\n"
        ":label: dir_no_cambia\n"
        "Ver {ref}`resumen` o {numref}`resumen` o {ref}`Texto con título <resumen>`.\n"
        "Ver {ref}`no_cambia` y {ref}`Título <no_cambia>`.\n",
        encoding="utf-8",
    )
    renames = {
        "resumen": {doc: "01_intro-resumen"},
        "dir_lbl": {doc: "01_intro-dir_lbl"},
    }

    n_defs, n_refs, warnings = apply_to_file(doc, renames, dry_run=False)
    assert n_defs == 2
    assert n_refs == 3
    assert len(warnings) == 0

    content = doc.read_text(encoding="utf-8")
    assert "(01_intro-resumen)=" in content
    assert ":label: 01_intro-dir_lbl" in content
    assert "(no_cambia)=" in content
    assert ":label: dir_no_cambia" in content
    assert "{ref}`01_intro-resumen`" in content
    assert "{numref}`01_intro-resumen`" in content
    assert "{ref}`Texto con título <01_intro-resumen>`" in content
    assert "{ref}`Título <no_cambia>`" in content


def test_apply_to_file_ambiguous_reference_warning(tmp_path: Path):
    doc_def1 = tmp_path / "01_a.md"
    doc_def2 = tmp_path / "02_b.md"
    doc_ref = tmp_path / "03_externo.md"

    doc_ref.write_text(
        "Consulta {ref}`duplicado` y {ref}`Título <duplicado>`.\n",
        encoding="utf-8",
    )

    renames = {
        "duplicado": {
            doc_def1: "01_a-duplicado",
            doc_def2: "02_b-duplicado",
        }
    }

    n_defs, n_refs, warnings = apply_to_file(doc_ref, renames, dry_run=False)
    assert n_defs == 0
    assert n_refs == 2
    assert len(warnings) == 2
    assert "referencia `duplicado` resuelta a `01_a-duplicado`" in warnings[0]


def test_apply_to_file_read_error(tmp_path: Path, monkeypatch):
    doc = tmp_path / "error.md"

    def mock_read_text(self, *args, **kwargs):
        raise OSError("Cannot read")

    monkeypatch.setattr(Path, "read_text", mock_read_text)
    n_defs, n_refs, warns = apply_to_file(doc, {}, dry_run=False)
    assert n_defs == 0
    assert n_refs == 0
    assert "No se pudo leer el archivo" in warns[0]


def test_apply_to_file_write_error(tmp_path: Path, monkeypatch):
    doc = tmp_path / "write_err.md"
    doc.write_text("(dup)=\n# Título\n", encoding="utf-8")
    renames = {"dup": {doc: "doc-dup"}}

    def mock_write_text(self, *args, **kwargs):
        raise OSError("Cannot write")

    monkeypatch.setattr(Path, "write_text", mock_write_text)
    n_defs, n_refs, warns = apply_to_file(doc, renames, dry_run=False)
    assert n_defs == 1
    assert "No se pudo escribir el archivo" in warns[0]


def test_run_fix_dup_anchors_not_a_directory(tmp_path: Path, capsys):
    no_dir = tmp_path / "no_dir"
    rc = run_fix_dup_anchors(str(no_dir))
    assert rc == 2
    assert "no es un directorio" in capsys.readouterr().err


def test_run_fix_dup_anchors_no_md_files(tmp_path: Path, capsys):
    empty = tmp_path / "empty"
    empty.mkdir()
    # Agregar archivo en directorio oculto que debe ser ignorado
    hidden = empty / ".hidden"
    hidden.mkdir()
    (hidden / "secret.md").write_text("(dup)=\n", encoding="utf-8")

    rc = run_fix_dup_anchors(str(empty))
    assert rc == 0
    assert "No se encontraron archivos .md" in capsys.readouterr().out


def test_run_fix_dup_anchors_no_duplicates(tmp_path: Path, capsys):
    d = tmp_path / "docs"
    d.mkdir()
    (d / "a.md").write_text("(a)=\n# A\n", encoding="utf-8")
    (d / "b.md").write_text("(b)=\n# B\n", encoding="utf-8")

    rc = run_fix_dup_anchors(str(d))
    assert rc == 0
    assert "No se encontraron anclas duplicadas" in capsys.readouterr().out


def test_run_fix_dup_anchors_report_mode(tmp_path: Path, capsys):
    d = tmp_path / "docs"
    d.mkdir()
    (d / "a.md").write_text("(dup)=\n# A\n", encoding="utf-8")
    (d / "b.md").write_text("(dup)=\n# B\n", encoding="utf-8")

    rc = run_fix_dup_anchors(str(d), report=True)
    assert rc == 0
    out = capsys.readouterr().out
    assert "Anclas duplicadas detectadas: 1" in out
    assert "(dup)=" in out
    # No debe haber modificado
    assert "(dup)=" in (d / "a.md").read_text(encoding="utf-8")


def test_run_fix_dup_anchors_dry_run(tmp_path: Path, capsys):
    d = tmp_path / "docs"
    d.mkdir()
    (d / "a.md").write_text("(dup)=\n# A\n", encoding="utf-8")
    (d / "b.md").write_text("(dup)=\n# B\n", encoding="utf-8")

    rc = run_fix_dup_anchors(str(d), dry_run=True)
    assert rc == 0
    out = capsys.readouterr().out
    assert "Plan de renombrado (dry-run):" in out
    assert "~" in out
    assert "serían modificados" in out
    # Archivos no modificados en disco
    assert "(dup)=" in (d / "a.md").read_text(encoding="utf-8")


def test_run_fix_dup_anchors_with_ambiguous_warnings(tmp_path: Path, capsys):
    d = tmp_path / "docs"
    d.mkdir()
    (d / "a.md").write_text("(dup)=\n# A\n", encoding="utf-8")
    (d / "b.md").write_text("(dup)=\n# B\n", encoding="utf-8")
    (d / "c.md").write_text("Ver {ref}`dup`.\n", encoding="utf-8")

    rc = run_fix_dup_anchors(str(d), dry_run=False)
    assert rc == 1
    out = capsys.readouterr().out
    assert "⚠" in out
    assert "advertencias" in out
