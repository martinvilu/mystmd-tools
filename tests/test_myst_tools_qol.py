"""Tests para las mejoras QoL de MYST-TOOLS."""

from myst_tools.c_snippet_validator import extraer_y_validar_snippets_c
from myst_tools.glossary_generator import generar_glosario_terminos
from myst_tools.exercise_extractor import extraer_ejercicios_myst
from myst_tools.callout_injector import formatear_callout
from myst_tools.typst_exporter import convertir_myst_a_typst


def test_c_snippet_validator():
    md_ok = """
# Punteros
```c
int main(void) {
    int x = 42;
    return 0;
}
```
"""
    res = extraer_y_validar_snippets_c(md_ok)
    assert len(res) == 1
    assert res[0]["valido"] is True


def test_glossary_generator():
    md = """
# Glosario
**Puntero**: Variable que almacena una dirección de memoria.
**TDA**: Tipo de dato abstracto que encapsula estado y operaciones.
"""
    glosario = generar_glosario_terminos(md)
    assert "Puntero" in glosario
    assert "TDA" in glosario
    assert "dirección de memoria" in glosario["Puntero"]


def test_exercise_extractor():
    md = """
```{exercise} Invertir Cadena
Escriba una función in-place que invierta una cadena de caracteres.
```
"""
    ejercicios = extraer_ejercicios_myst(md)
    assert len(ejercicios) == 1
    assert ejercicios[0]["titulo"] == "Invertir Cadena"
    assert "in-place" in ejercicios[0]["enunciado"]


def test_callout_injector():
    res = formatear_callout("warning", "Atención", "No desreferenciar punteros nulos.")
    assert "```{warning} Atención" in res
    assert "No desreferenciar punteros nulos." in res


def test_typst_exporter():
    md = "# Estructuras\n## Definición\nContenido de estructuras en C."
    typ = convertir_myst_a_typst(md, "Guía de Tipos")
    assert "= Guía de Tipos" in typ
    assert "= Estructuras" in typ
    assert "== Definición" in typ
