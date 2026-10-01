"""`myst-tools check-a11y`: accesibilidad del material MyST (revisión, 05 §3)."""

import json

from typer.testing import CliRunner

from myst_tools.a11y_checker import auditar_accesibilidad, color_a_rgb, contraste
from myst_tools.cli import app

runner = CliRunner()


def _reglas(md: str) -> list:
    return [(h.linea, h.regla, h.severidad) for h in auditar_accesibilidad(md)]


def test_texto_alternativo():
    md = ("# T\n\n![](a.png)\n![imagen](b.png)\n![Pila con dos marcos](c.png)\n"
          "<img src=\"d.png\">\n<img src=\"e.png\" alt=\"Diagrama del heap\">\n")
    assert _reglas(md) == [(3, "alt-faltante", "error"), (4, "alt-generico", "aviso"), (6, "alt-faltante", "error")]


def test_directivas_de_imagen_y_tablas():
    md = ("# T\n\n```{figure} f.png\n:width: 50%\n\nLeyenda.\n```\n\n"
          "```{image} i.png\n:alt: i.png\n```\n\n"
          ":::{image} j.png\n:alt: Árbol binario con tres niveles\n:::\n\n"
          "```{list-table}\n* - a\n```\n\n"
          "```{list-table}\n:header-rows: 1\n* - a\n```\n")
    assert _reglas(md) == [(3, "alt-faltante", "aviso"), (9, "alt-generico", "aviso"),
                           (17, "tabla-sin-encabezado", "aviso")]


def test_orden_de_encabezados_y_codigo():
    md = "# T\n\n## A\n\n#### B\n\n```bash\n# un comentario no es un título\n```\n\n# Otro\n"
    assert _reglas(md) == [(5, "encabezado-salto", "error"), (11, "titulo-repetido", "error")]
    # Con title: en el frontmatter, la página puede empezar con # o con ##.
    assert _reglas("---\ntitle: Punteros\n---\n\n# Punteros\n\n## Uso\n") == []
    assert _reglas("---\ntitle: Punteros\n---\n\n## Uso\n") == []
    assert _reglas("## Uso\n") == [(1, "sin-titulo", "aviso")]
    # Una directiva de código con opciones también se saltea.
    assert _reglas("# T\n\n```{code-block} bash\n:linenos:\n# paso 1\n```\n") == []


def test_enlaces_iframes_y_contraste():
    md = ("# T\n\nMirá [acá](x.md) y la [guía de estilo](guia.md).\n"
          "<iframe src=\"https://youtube.com/embed/x\"></iframe>\n"
          "<iframe title=\"Video: punteros\" src=\"y\"></iframe>\n"
          "<span style=\"color: #aaa\">gris</span>\n"
          "<span style=\"color: #777; background-color: #555\">x</span>\n"
          "<span style=\"color: #222\">ok</span>\n")
    assert _reglas(md) == [(3, "enlace-generico", "error"), (4, "iframe-sin-titulo", "error"),
                           (6, "contraste", "aviso"), (7, "contraste", "error")]
    assert round(contraste(color_a_rgb("#000"), color_a_rgb("white")), 1) == 21.0
    assert color_a_rgb("rgb(255, 0, 0)") == (255, 0, 0) and color_a_rgb("var(--x)") is None


def test_cli(tmp_path):
    (tmp_path / "pag.md").write_text("# T\n\n![](a.png)\n\n```{figure} f.png\n```\n", encoding="utf-8")
    res = runner.invoke(app, ["check-a11y", "-f", str(tmp_path), "--json"])
    datos = json.loads(res.stdout)
    assert res.exit_code == 1 and datos["errores"] == 1 and datos["avisos"] == 1
    (tmp_path / "pag.md").write_text("# T\n\n```{figure} f.png\n```\n", encoding="utf-8")
    assert runner.invoke(app, ["check-a11y", "-f", str(tmp_path)]).exit_code == 0
    assert runner.invoke(app, ["check-a11y", "-f", "--strict", str(tmp_path)]).exit_code == 1
