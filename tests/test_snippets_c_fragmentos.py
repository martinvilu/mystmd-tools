"""check-c-snippets no marca como inválidos los fragmentos didácticos (N-MYST-02)."""

from __future__ import annotations

import shutil

import pytest

from myst_tools.c_snippet_validator import extraer_y_validar_snippets_c

pytestmark = pytest.mark.skipif(shutil.which("gcc") is None, reason="requiere gcc")

CERCA = "`" * 3


def _md(*bloques: str) -> str:
    return "\n\n".join(f"{CERCA}c\n{b}\n{CERCA}" for b in bloques)


def test_sentencias_sueltas_y_tipos_de_la_biblioteca_estandar_son_validos():
    resultados = extraer_y_validar_snippets_c(_md("int x = 0;\nx++;", "size_t n = 3;",
                                                  "for (int i = 0; i < 3; i++) {\n    printf(\"%d\\n\", i);\n}"))
    assert [r["valido"] for r in resultados] == [True, True, True], resultados


def test_un_error_real_se_informa_con_la_linea_del_bloque():
    resultados = extraer_y_validar_snippets_c(_md("int main(void)\n{\n    return 0\n}"))
    assert resultados[0]["valido"] is False
    assert "bloque1.c:3" in resultados[0]["detalle"], resultados[0]["detalle"]


def test_un_bloque_marcado_como_fragmento_no_se_compila():
    md = f"{CERCA}{{code-block}} c\n:class: fragmento\nesto no es C;\n{CERCA}\n\n{CERCA}{{code-block}} c\nint y = 2;\n{CERCA}"
    resultados = extraer_y_validar_snippets_c(md)
    assert [r["valido"] for r in resultados] == [True, True]
    assert "fragmento" in resultados[0]["detalle"]
