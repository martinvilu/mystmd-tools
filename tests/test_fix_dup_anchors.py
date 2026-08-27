"""Tests para el corrector de anclas duplicadas fix_dup_anchors."""

from pathlib import Path
from myst_tools.fix_dup_anchors import apply_to_file, build_rename_map, collect_anchors, run_fix_dup_anchors


def test_collect_anchors_finds_duplicates(tmp_path: Path):
    f1 = tmp_path / "01_intro.md"
    f2 = tmp_path / "02_avanzado.md"

    f1.write_text("(resumen)=\n# Resumen 1\n", encoding="utf-8")
    f2.write_text("(resumen)=\n# Resumen 2\n(unico)=\n## Unico\n", encoding="utf-8")

    anchors = collect_anchors([f1, f2])
    assert "resumen" in anchors
    assert len(anchors["resumen"]) == 2
    assert "unico" in anchors
    assert len(anchors["unico"]) == 1


def test_build_rename_map(tmp_path: Path):
    f1 = tmp_path / "01_intro.md"
    f2 = tmp_path / "02_avanzado.md"

    duplicates = {"resumen": [f1, f2]}
    all_labels = {"resumen": [f1, f2], "otro": [f1]}

    renames = build_rename_map(duplicates, all_labels)
    assert f1 in renames["resumen"]
    assert f2 in renames["resumen"]
    assert renames["resumen"][f1] == "01_intro-resumen"
    assert renames["resumen"][f2] == "02_avanzado-resumen"


def test_apply_to_file(tmp_path: Path):
    doc = tmp_path / "01_intro.md"
    doc.write_text(
        "(resumen)=\n# Resumen 1\nVer {ref}`resumen` o {numref}`resumen`.\n",
        encoding="utf-8",
    )
    renames = {"resumen": {doc: "01_intro-resumen"}}

    n_defs, n_refs, warnings = apply_to_file(doc, renames, dry_run=False)
    assert n_defs == 1
    assert n_refs == 2
    assert len(warnings) == 0

    content = doc.read_text(encoding="utf-8")
    assert "(01_intro-resumen)=" in content
    assert "{ref}`01_intro-resumen`" in content
    assert "{numref}`01_intro-resumen`" in content


def test_run_fix_dup_anchors_workflow(tmp_path: Path):
    f1 = tmp_path / "01_intro.md"
    f2 = tmp_path / "02_avanzado.md"

    f1.write_text("(resumen)=\n# Resumen 1\nVer {ref}`resumen`.\n", encoding="utf-8")
    f2.write_text("(resumen)=\n# Resumen 2\nVer {ref}`resumen`.\n", encoding="utf-8")

    rc = run_fix_dup_anchors(str(tmp_path), dry_run=False, report=False)
    assert rc == 0

    c1 = f1.read_text(encoding="utf-8")
    c2 = f2.read_text(encoding="utf-8")

    assert "(01_intro-resumen)=" in c1
    assert "(02_avanzado-resumen)=" in c2
