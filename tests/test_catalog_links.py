"""Tests para `myst-tools check-catalog-links` (Ola 15 — validación contra catálogo oficial de gaff y ripley)."""

import json
from pathlib import Path

from typer.testing import CliRunner

from myst_tools.catalog_links_checker import auditar_enlaces_catalogo
from myst_tools.cli import app

runner = CliRunner()


def _hallazgos_tuplas(md: str, archivo: Path | None = None) -> list[tuple[int, str, str]]:
    return [(h.linea, h.regla, h.referencia) for h in auditar_enlaces_catalogo(md, archivo=archivo)]


def test_referencias_validas_a_reglas_y_satelites(tmp_path: Path):
    regla_file = tmp_path / "reglas" / "00_formato" / "0x0001h.md"
    regla_file.parent.mkdir(parents=True)
    regla_file.write_text("# 0x0001h\n", encoding="utf-8")

    indice = tmp_path / "reglas" / "indice.md"
    md = (
        "# Índice\n\n"
        "- Ver {ref}`0x0001h` y {ref}`0x7001h`.\n"
        "- Enlace correcto: [0x0001h](00_formato/0x0001h.md).\n"
        "- Satélite `gaff` y repositorio https://github.com/INGCOM-UNRN-P1/daedalus.\n"
    )
    indice.write_text(md, encoding="utf-8")
    assert _hallazgos_tuplas(md, archivo=indice) == []


def test_detecta_reglas_inexistentes_renumeradas_y_formato():
    md = (
        "# Reglas\n\n"
        "- Regla inexistente: {ref}`0x9999h`.\n"
        "- Regla v1 deprecada/renumerada: `0x0037h` (ahora 0x010Eh).\n"
        "- Formato en minúscula: {ref}`0x000ah`.\n"
    )
    assert _hallazgos_tuplas(md) == [
        (3, "regla-inexistente", "0x9999h"),
        (4, "regla-renumerada", "0x0037h"),
        (5, "regla-formato", "0x000ah"),
    ]


def test_detecta_enlaces_rotos_sin_carpeta_y_anclas_malformadas(tmp_path: Path):
    indice = tmp_path / "reglas" / "indice.md"
    indice.parent.mkdir(parents=True)
    md = (
        "# Índice\n\n"
        "- Sin carpeta de familia (N-APUNTE-02): [0x0001h](0x0001h.md)\n"
        "- Familia equivocada: [0x0101h](00_formato/0x0101h.md)\n"
        "- Rol MyST malformado: `{ref}0x4001h`\n"
        "- Ancla con prefijo viejo: {ref}`regla-0x1005h`\n"
    )
    indice.write_text(md, encoding="utf-8")
    assert _hallazgos_tuplas(md, archivo=indice) == [
        (3, "enlace-regla-roto", "0x0001h.md"),
        (4, "enlace-regla-familia-incorrecta", "00_formato/0x0101h.md"),
        (5, "ancla-myst-malformada", "`{ref}0x4001h`"),
        (6, "ancla-regla-prefijo", "regla-0x1005h"),
    ]


def test_detecta_satelites_retirados_e_inexistentes():
    md = (
        "# Herramientas\n\n"
        "- El satélite `esper` fue retirado.\n"
        "- Enlace a satélite inexistente: https://github.com/INGCOM-UNRN-P1/satelite-fantasma\n"
    )
    assert _hallazgos_tuplas(md) == [
        (3, "satelite-retirado", "esper"),
        (4, "satelite-inexistente", "satelite-fantasma"),
    ]


def test_cli_check_catalog_links(tmp_path: Path):
    doc = tmp_path / "doc.md"
    doc.write_text("# Doc\n\nUsar {ref}`0x0001h` y el satélite `gaff`.\n", encoding="utf-8")
    res_ok = runner.invoke(app, ["check-catalog-links", "-f", str(tmp_path)])
    assert res_ok.exit_code == 0

    doc.write_text("# Doc\n\nEnlace roto [0x0001h](0x0001h.md) y regla `0x9999h`.\n", encoding="utf-8")
    res_err = runner.invoke(app, ["check-catalog-links", "-f", "--json", str(tmp_path)])
    assert res_err.exit_code == 1
    payload = json.loads(res_err.stdout)
    assert payload["errores"] == 2
    assert {h["regla"] for h in payload["hallazgos"]} == {"enlace-regla-roto", "regla-inexistente"}
