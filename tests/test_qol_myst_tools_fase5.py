import pytest
from pathlib import Path
from typer.testing import CliRunner

from myst_tools.cli import app
from myst_tools.table_auditor import parse_markdown_tables, auditar_tabla, formatear_tabla
from myst_tools.c_project_extractor import extraer_snippets_c_compilables, exportar_proyecto_c, compilar_y_ejecutar_snippets
from myst_tools.rioplatense_checker import auditar_estilo_rioplatense
from myst_tools.dict_terms_extractor import extraer_terminos_tecnicos_c, exportar_diccionario_languagetool
from myst_tools.github_link_auditor import auditar_enlaces_github

runner = CliRunner()


def test_table_auditor_detects_mismatch():
    raw_table = [
        "| Col1 | Col2 | Col3 |",
        "| :--- | :---: |",
        "| A | B |",
    ]
    issues = auditar_tabla(raw_table, start_line=10)
    assert len(issues) >= 1
    assert any("separador" in iss.message.lower() for iss in issues)


def test_table_auditor_formatear():
    raw_table = [
        "| Columna Uno | C2 |",
        "| :--- | ---: |",
        "| Val | Dato Largo |",
    ]
    formatted = formatear_tabla(raw_table)
    assert len(formatted) == 3
    assert formatted[0].startswith("| Columna Uno")
    assert formatted[1].startswith("| :")
    assert formatted[2].endswith(" |")


def test_c_project_extractor_generates_files(tmp_path):
    md_content = """# Apunte
```{c}
int suma(int a, int b) {
    return a + b;
}
```
```{c}
#include <stdio.h>
int main(void) {
    printf("Hola\\n");
    return 0;
}
```
"""
    snippets = extraer_snippets_c_compilables(md_content)
    assert len(snippets) == 2
    assert not snippets[0]["tiene_main"]
    assert snippets[1]["tiene_main"]

    proj_dir = tmp_path / "c_proj"
    archivos = exportar_proyecto_c(snippets, proj_dir)
    assert len(archivos) == 3
    assert (proj_dir / "Makefile").exists()
    assert (proj_dir / "ejemplo_01.c").exists()
    assert (proj_dir / "ejemplo_02.c").exists()


def test_compilar_y_ejecutar_snippets(tmp_path):
    md_content = """```{c}
#include <assert.h>
int main(void) {
    assert(1 + 1 == 2);
    return 0;
}
```"""
    snippets = extraer_snippets_c_compilables(md_content)
    resultados = compilar_y_ejecutar_snippets(snippets, tmp_path)
    assert len(resultados) == 1
    assert resultados[0]["compilado"] is True
    assert resultados[0]["ejecutado"] is True


def test_rioplatense_checker():
    texto = """
    Tú tienes que debuggear este programa antes de deployar.
    Mirá este bloque:
    `debuggear` no debe detectarse dentro de backticks.
    ```c
    int tú = 1;
    ```
    """
    issues = auditar_estilo_rioplatense(texto)
    tipos = [iss.rule_type for iss in issues]
    assert "spanglish" in tipos
    assert "voseo_inconsistente" in tipos
    # Verificar que no detectó el código en backtick
    palabras = [iss.matched_text.lower() for iss in issues]
    assert "tú" in palabras
    assert "debuggear" in palabras


def test_dict_terms_extractor(tmp_path):
    texto = """
    # Memoria y TDAs
    Usamos el tipo nodo_t y la estructura struct lista.
    Llamamos a malloc_custom(10) y definimos MAX_BUFFER.
    ```{exercise} consigna-1
    Texto
    ```
    """
    terminos = extraer_terminos_tecnicos_c(texto)
    assert "nodo_t" in terminos
    assert "lista" in terminos
    assert "MAX_BUFFER" in terminos
    assert "consigna-1" in terminos

    out_file = tmp_path / "dict.txt"
    cant = exportar_diccionario_languagetool(terminos, out_file)
    assert cant == len(terminos)
    assert out_file.exists()


def test_github_link_auditor():
    texto = """
    Enlace móvil: https://github.com/torvalds/linux/blob/main/Makefile
    Enlace con sha corto: https://github.com/torvalds/linux/commit/123a
    Enlace con rango invertido: https://github.com/torvalds/linux/blob/0123456789abcdef/Makefile#L50-L20
    Enlace válido: https://github.com/torvalds/linux/blob/0123456789abcdef/Makefile#L10-L20
    """
    issues = auditar_enlaces_github(texto)
    assert len(issues) == 3
    tipos = {iss.issue_type for iss in issues}
    assert "enlace_mutable" in tipos
    assert "sha_demasiado_corto" in tipos
    assert "rango_lineas_invalido" in tipos


def test_cli_commands(tmp_path):
    # Probar CLI con --force
    test_md = tmp_path / "test.md"
    test_md.write_text("""# Titulo
| A | B |
| :--- | :--- |
| 1 | 2 |

```c
int main() { return 0; }
```
""", encoding="utf-8")

    res_tables = runner.invoke(app, ["check-tables", str(test_md), "--force"])
    assert res_tables.exit_code == 0

    res_fmt = runner.invoke(app, ["fmt-tables", str(test_md), "--force"])
    assert res_fmt.exit_code == 0

    res_dict = runner.invoke(app, ["extract-dict-terms", str(test_md), "-o", str(tmp_path / "terms.txt"), "--force"])
    assert res_dict.exit_code == 0
    assert (tmp_path / "terms.txt").exists()

    res_c = runner.invoke(app, ["extract-c-tests", str(test_md), "-o", str(tmp_path / "c_out"), "--force"])
    assert res_c.exit_code == 0
    assert (tmp_path / "c_out" / "Makefile").exists()

    res_links = runner.invoke(app, ["check-links", str(test_md), "--force"])
    assert res_links.exit_code == 0
