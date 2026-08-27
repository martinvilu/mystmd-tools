"""Tests para el formateador myst_fmt."""

from pathlib import Path
from myst_tools.myst_fmt import format_myst, run_myst_fmt


def test_format_myst_line_wrapping():
    raw = (
        "Este es un párrafo de texto bastante largo que excede los ochenta caracteres y por "
        "lo tanto debería ser partido en varias líneas por el formateador sin perder ninguna palabra "
        "ni alterar la estructura del texto.\n"
    )
    formatted = format_myst(raw, width=60)
    for line in formatted.splitlines():
        assert len(line) <= 65


def test_format_myst_preserves_code_fences():
    raw = (
        "# Título\n\n"
        "Texto antes del código.\n\n"
        "```c\n"
        "int main(void) {\n"
        "    printf(\"Línea de código muy pero muy larga que no debe ser partida jamás por el formateador\");\n"
        "    return 0;\n"
        "}\n"
        "```\n"
    )
    formatted = format_myst(raw, width=40)
    assert 'printf("Línea de código muy pero muy larga que no debe ser partida jamás por el formateador");' in formatted
    assert "``` c" in formatted or "```c" in formatted


def test_format_myst_directive_colons_and_comments():
    raw = (
        "```{note}\n"
        "Esta es una nota importante.\n"
        "```\n"
    )
    formatted = format_myst(raw, width=80)
    # Directiva convertida a colons ::: y cierre con comentario
    assert ":::{note}" in formatted or "::: {note}" in formatted
    assert ":::" in formatted
    assert "<!-- {note} -->" in formatted


def test_run_myst_fmt_check_mode(tmp_path: Path):
    doc = tmp_path / "test.md"
    doc.write_text("```{note}\nNota.\n```\n", encoding="utf-8")

    # En modo check debe detectar que necesita cambios y retornar 1
    rc = run_myst_fmt([str(doc)], check=True, stdout=False, width=80)
    assert rc == 1

    # Formatear archivo in-place
    rc_fix = run_myst_fmt([str(doc)], check=False, stdout=False, width=80)
    assert rc_fix == 0

    # Ahora en modo check debe retornar 0
    rc_clean = run_myst_fmt([str(doc)], check=True, stdout=False, width=80)
    assert rc_clean == 0
