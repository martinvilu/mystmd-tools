"""Tests para el formateador myst_fmt."""

import io
import sys
from pathlib import Path
import pytest
from myst_tools.myst_fmt import (
    Fence,
    _annotate_close,
    _correct,
    _count_code_lines,
    _has_linenos,
    _is_close,
    _parse_open,
    _prescan_colon_lengths,
    _strip_comment,
    _wrap_line,
    format_myst,
    run_myst_fmt,
)


def test_strip_comment_and_parse_open():
    assert _strip_comment("::: {note} <!-- comment -->") == "::: {note}"
    assert _strip_comment("texto sin comentario") == "texto sin comentario"

    # Solo comentario
    assert _parse_open("<!-- comentario solo -->") is None

    # Colon open
    f_colon = _parse_open(":::: {note}")
    assert f_colon is not None
    assert f_colon.kind == "colon"
    assert f_colon.length == 4
    assert f_colon.label == "{note}"

    # Backtick open
    f_btick = _parse_open("```python")
    assert f_btick is not None
    assert f_btick.kind == "backtick"
    assert f_btick.length == 3
    assert f_btick.label == "python"

    # No es open
    assert _parse_open("Texto común y corriente") is None


def test_is_close():
    top_colon = Fence("colon", 3, "{note}", "colon", 3)
    top_btick = Fence("backtick", 3, "c", "backtick", 3)

    assert _is_close(":::", top_colon) is True
    assert _is_close("::::", top_colon) is True
    assert _is_close("::", top_colon) is False
    assert _is_close("```", top_colon) is False

    assert _is_close("```", top_btick) is True
    assert _is_close("````", top_btick) is True
    assert _is_close("``", top_btick) is False


def test_prescan_colon_lengths_nested():
    # Anidamiento de colons donde el padre tiene 3 colons y el hijo 3 colons
    lines = [
        "::: {card}\n",
        "Texto exterior\n",
        "<!-- comentario 1 --> <!-- comentario 2 -->\n",
        "::: {note}\n",
        "Nota interior\n",
        ":::\n",
        ":::\n",
    ]
    lengths = _prescan_colon_lengths(lines)
    # El padre (línea 0) debe subir a 4 colons porque su hijo tiene 3
    assert lengths[0] == 4
    assert lengths[3] == 3

    # Prescan sin bloques colon
    assert _prescan_colon_lengths(["# Header\n", "Texto\n"]) == {}


def test_count_code_lines_and_has_linenos():
    lines_with_opts = [
        "```{code-block} python\n",
        ":caption: Mi script\n",
        ":linenos:\n",
        ":emphasize-lines: 1\n",
        "\n",
        "def foo():\n",
        "    return 42\n",
        "```\n",
    ]
    fence = Fence("backtick", 3, "{code-block} python", "backtick", 3)
    assert _has_linenos(lines_with_opts, 0, fence) is True
    assert _count_code_lines(lines_with_opts, 0, fence) == 2

    # Caso donde hay línea en blanco inmediatamente
    lines_blank = [
        "```python\n",
        "\n",
        ":linenos:\n",
        "```\n",
    ]
    fence_py = Fence("backtick", 3, "python", "backtick", 3)
    assert _has_linenos(lines_blank, 0, fence_py) is False

    # Caso donde fence se cierra inmediatamente
    lines_empty = [
        "```python\n",
        "```\n",
    ]
    assert _has_linenos(lines_empty, 0, fence_py) is False

    # Caso con texto que no es opción antes de linenos
    lines_no_opt = [
        "```python\n",
        "texto_comun = 1\n",
        ":linenos:\n",
        "```\n",
    ]
    assert _has_linenos(lines_no_opt, 0, fence_py) is False

    lines_without_linenos = [
        "```python\n",
        "x = 1\n",
        "```\n",
    ]
    assert _has_linenos(lines_without_linenos, 0, fence_py) is False
    assert _count_code_lines(lines_without_linenos, 0, fence_py) == 1


def test_correct_fences():
    # Verbatim directive convertida a backticks
    f_verbatim = Fence("colon", 3, "{code-block} c", "colon", 3)
    c1 = _correct(f_verbatim, [], {}, 0)
    assert c1.kind == "backtick"

    # Directiva común convertida a colon
    f_note = Fence("backtick", 3, "{note}", "backtick", 3)
    c2 = _correct(f_note, [], {0: 4}, 0)
    assert c2.kind == "colon"
    assert c2.length == 4

    # Lenguaje puro convertido a backtick
    f_lang = Fence("colon", 3, "python", "colon", 3)
    c3 = _correct(f_lang, [], {}, 0)
    assert c3.kind == "backtick"

    # Fences sin etiqueta
    f_empty_colon = Fence("colon", 3, "", "colon", 3)
    c4 = _correct(f_empty_colon, [], {}, 0)
    assert c4.kind == "colon"

    f_empty_btick = Fence("backtick", 3, "", "backtick", 3)
    # Anidado dentro de otro backtick
    parent_btick = Fence("backtick", 3, "python", "backtick", 3)
    c5 = _correct(f_empty_btick, [parent_btick], {}, 0)
    assert c5.kind == "backtick"
    assert c5.length == 4


def test_annotate_close():
    f_labeled = Fence("colon", 3, "{note}", "colon", 3)
    assert _annotate_close(f_labeled) == [":::\n", "<!-- {note} -->\n"]

    f_unlabeled = Fence("backtick", 3, "", "backtick", 3)
    assert _annotate_close(f_unlabeled) == ["```\n"]


def test_wrap_line():
    # Líneas cortas o NOWRAP no se tocan
    assert _wrap_line("# Título muy largo que sobrepasa pero es un encabezado y no debe partirse\n") == [
        "# Título muy largo que sobrepasa pero es un encabezado y no debe partirse\n"
    ]
    assert _wrap_line("(ancla-larga)=\n") == ["(ancla-larga)=\n"]
    assert _wrap_line("| col1 | col2 | col3 | col4 | col5 |\n") == ["| col1 | col2 | col3 | col4 | col5 |\n"]
    assert _wrap_line("-------------------------------------------------------------------------\n") == [
        "-------------------------------------------------------------------------\n"
    ]
    assert _wrap_line("![Imagen descriptiva con alt text largo](path/to/image/very/long/location.png)\n") == [
        "![Imagen descriptiva con alt text largo](path/to/image/very/long/location.png)\n"
    ]
    assert _wrap_line(":opcion_directiva: valor_largo\n") == [":opcion_directiva: valor_largo\n"]
    assert _wrap_line("% Comentario MyST largo\n") == ["% Comentario MyST largo\n"]
    assert _wrap_line("<!-- Comentario HTML largo -->\n") == ["<!-- Comentario HTML largo -->\n"]
    assert _wrap_line("<div class='container' data-info='large'>\n") == ["<div class='container' data-info='large'>\n"]
    assert _wrap_line("$$\n") == ["$$\n"]
    assert _wrap_line("   \n") == ["   \n"]

    # Wrap con sangría de lista y citas
    bullet_text = "* Este es un ítem de lista bastante largo que debe ser envuelto preservando la sangría del segundo renglón correctamente sin alterar el contenido.\n"
    wrapped_bullet = _wrap_line(bullet_text)
    assert len(wrapped_bullet) > 1
    assert wrapped_bullet[1].startswith("  ")

    num_text = "1. Primer elemento numerado de una lista extensa que necesita ajuste de línea automático por superar el ancho configurado.\n"
    wrapped_num = _wrap_line(num_text)
    assert len(wrapped_num) > 1
    assert wrapped_num[1].startswith("   ")

    quote_text = "> Esta es una cita en bloque bastante extensa que sobrepasa el límite máximo establecido de columnas y debe envolverse respetando la sangría.\n"
    wrapped_quote = _wrap_line(quote_text)
    assert len(wrapped_quote) > 1
    assert wrapped_quote[1].startswith("  ")


def test_format_myst_frontmatter_preservation():
    source = (
        "---\n"
        "title: Mi Documento con Frontmatter\n"
        "author: Martín René\n"
        "...\n"
        "# Título Principal\n\n"
        "Texto descriptivo del documento.\n"
    )
    formatted = format_myst(source, width=80)
    assert formatted.startswith("---\ntitle: Mi Documento con Frontmatter\nauthor: Martín René\n...\n")
    assert "# Título Principal" in formatted


def test_format_myst_math_blocks():
    source = (
        "# Matemática\n\n"
        "$$\n"
        "\\int_{0}^{\\infty} e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}\n"
        "$$\n\n"
        "Texto luego de la fórmula.\n"
    )
    formatted = format_myst(source, width=40)
    assert "\\int_{0}^{\\infty} e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}" in formatted


def test_format_myst_short_codeblock_preserves_language():
    source = (
        "```python\n"
        "x = 1\n"
        "y = 2\n"
        "```\n"
    )
    formatted = format_myst(source, width=80)
    assert "``` python\n" in formatted
    assert "x = 1\n" in formatted


def test_format_myst_long_codeblock_promotion_and_linenos():
    # Código en lenguaje puro con más de 5 líneas -> promovido a {code-block} y añade :linenos:
    source = (
        "```c\n"
        "#include <stdio.h>\n"
        "int main(void) {\n"
        "    int x = 10;\n"
        "    printf(\"%d\\n\", x);\n"
        "    return 0;\n"
        "}\n"
        "```\n"
    )
    formatted = format_myst(source, width=80)
    assert "```{code-block} c" in formatted
    assert ":linenos:" in formatted
    assert "<!-- {code-block} c -->" in formatted

    # Directiva {code-block} existente con más de 5 líneas pero sin :linenos:
    source2 = (
        "```{code-block} python\n"
        "a = 1\n"
        "b = 2\n"
        "c = 3\n"
        "d = 4\n"
        "e = 5\n"
        "f = 6\n"
        "```\n"
    )
    formatted2 = format_myst(source2, width=80)
    assert ":linenos:" in formatted2

    # Directiva con :linenos: ya presente no debe duplicarlo
    source3 = (
        "```{code-block} python\n"
        ":linenos:\n"
        "a = 1\n"
        "b = 2\n"
        "c = 3\n"
        "d = 4\n"
        "e = 5\n"
        "f = 6\n"
        "```\n"
    )
    formatted3 = format_myst(source3, width=80)
    assert formatted3.count(":linenos:") == 1


def test_format_myst_unlabeled_fences():
    source = (
        "```\n"
        "bloque de texto sin lenguaje\n"
        "```\n"
    )
    formatted = format_myst(source, width=80)
    assert "```\n" in formatted
    assert "bloque de texto sin lenguaje\n" in formatted


def test_format_myst_directives_spacing_and_existing_closing_comment():
    source = (
        "::: {warning}\n"
        "Este es un aviso importante sin opciones.\n"
        ":::\n"
        "<!-- {warning} -->\n"
    )
    formatted = format_myst(source, width=80)
    assert ":::{warning}\n\n" in formatted
    assert formatted.count("<!-- {warning} -->") == 1


def test_format_myst_directives_with_options_spacing():
    source = (
        "::: {dropdown} Ver Detalles\n"
        ":open:\n"
        "Contenido desplegable.\n"
        ":::\n"
    )
    formatted = format_myst(source, width=80)
    assert ":::{dropdown} Ver Detalles\n:open:\n" in formatted


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


def test_run_myst_fmt_stdin_tty_and_piped(monkeypatch):
    # Piped stdin (not a tty)
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    monkeypatch.setattr(sys.stdin, "read", lambda: "# Titulo Piped\n")
    out_capture = io.StringIO()
    monkeypatch.setattr(sys.stdout, "write", out_capture.write)

    rc = run_myst_fmt(files=None, check=False, stdout=False, width=80)
    assert rc == 0
    assert "# Titulo Piped\n" in out_capture.getvalue()

    # files=['-']
    out_capture2 = io.StringIO()
    monkeypatch.setattr(sys.stdout, "write", out_capture2.write)
    rc2 = run_myst_fmt(files=["-"], check=False, stdout=False, width=80)
    assert rc2 == 0
    assert "# Titulo Piped\n" in out_capture2.getvalue()


def test_run_myst_fmt_interactive_dir_expansion(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    doc = tmp_path / "doc.md"
    doc.write_text("# Interactivo\n", encoding="utf-8")

    rc = run_myst_fmt(files=None, check=False, stdout=False, width=80)
    assert rc == 0


def test_run_myst_fmt_nonexistent_file(tmp_path: Path, capsys):
    no_file = tmp_path / "no_existe.md"
    rc = run_myst_fmt([str(no_file)])
    assert rc == 2
    assert "no existe" in capsys.readouterr().err


def test_run_myst_fmt_no_md_files(tmp_path: Path, capsys):
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()
    rc = run_myst_fmt([str(empty_dir)])
    assert rc == 0
    assert "No se encontraron archivos .md para formatear." in capsys.readouterr().err


def test_run_myst_fmt_read_error(tmp_path: Path, monkeypatch, capsys):
    doc = tmp_path / "unreadable.md"
    doc.write_text("# Test\n", encoding="utf-8")

    def mock_read_text(self, *args, **kwargs):
        raise OSError("Permission denied")

    monkeypatch.setattr(Path, "read_text", mock_read_text)
    rc = run_myst_fmt([str(doc)])
    assert rc == 2
    assert "error —" in capsys.readouterr().err


def test_run_myst_fmt_stdout_mode(tmp_path: Path, monkeypatch):
    doc = tmp_path / "test_out.md"
    doc.write_text("# Salida Estándar\n", encoding="utf-8")
    out_capture = io.StringIO()
    monkeypatch.setattr(sys.stdout, "write", out_capture.write)

    rc = run_myst_fmt([str(doc)], stdout=True)
    assert rc == 0
    assert "# Salida Estándar\n" in out_capture.getvalue()


def test_run_myst_fmt_inplace_modification(tmp_path: Path, capsys):
    doc = tmp_path / "test_mod.md"
    doc.write_text("```{note}\nNota\n```\n", encoding="utf-8")

    rc = run_myst_fmt([str(doc)], check=False, stdout=False)
    assert rc == 0
    assert "formateado:" in capsys.readouterr().out
    assert ":::{note}" in doc.read_text(encoding="utf-8")
