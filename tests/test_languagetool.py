"""Tests para el verificador y corrector ortográfico/gramatical de LanguageTool en myst-tools."""

import json
from pathlib import Path
import pytest
from typer.testing import CliRunner

from myst_tools.cli import app
from myst_tools.languagetool_checker import (
    enmascarar_myst_markdown,
    consultar_languagetool,
    analizar_archivo_languagetool,
    aplicar_autofix_archivo,
    generar_reporte_markdown,
    LanguageToolIssue,
)

runner = CliRunner()


def test_enmascarar_myst_markdown():
    texto = (
        "# Título Principal\n\n"
        "(mi-ancla)=\n"
        "Este es un texto con `codigo inline` y una fórmula $x + y = z$.\n\n"
        "```{code-block} c\n"
        "int main() {\n"
        "    return 0;\n"
        "}\n"
        "```\n\n"
        "Visitar [Enlace](https://example.com/ruta).\n"
    )
    enmascarado, _ = enmascarar_myst_markdown(texto)
    assert "# Título Principal" in enmascarado
    assert "Este es un texto con" in enmascarado
    # El código y anclas deben haber sido reemplazados por espacios sin alterar las líneas
    assert "int main()" not in enmascarado
    assert "(mi-ancla)=" not in enmascarado
    assert "https://example.com" not in enmascarado
    assert len(enmascarado) == len(texto)


def test_consultar_languagetool_mock(monkeypatch):
    sample_response = {
        "matches": [
            {
                "message": "Posible falta de ortografía",
                "shortMessage": "Error ortográfico",
                "offset": 8,
                "length": 6,
                "rule": {"id": "MORFOLOGIK_RULE_ES", "category": {"name": "Ortografía"}},
                "context": {"text": "Texto con prueva de error", "offset": 8, "length": 6},
                "replacements": [{"value": "prueba"}, {"value": "pruebas"}],
            }
        ]
    }

    class MockResponse:
        status = 200
        def read(self):
            return json.dumps(sample_response).encode("utf-8")
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    import urllib.request
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=10.0: MockResponse())

    res = consultar_languagetool("Texto con prueva de error", lang="es-AR")
    assert "matches" in res
    assert len(res["matches"]) == 1
    assert res["matches"][0]["rule"]["id"] == "MORFOLOGIK_RULE_ES"


def test_analizar_y_autofix_archivo(tmp_path: Path, monkeypatch):
    doc = tmp_path / "tema.md"
    doc.write_text("Esta es una prueva de texto con `int a = 5;` en MyST.\n", encoding="utf-8")

    sample_response = {
        "matches": [
            {
                "message": "Posible falta de ortografía",
                "shortMessage": "Error ortográfico",
                "offset": 12,
                "length": 6,
                "rule": {"id": "MORFOLOGIK_RULE_ES", "category": {"name": "Ortografía"}},
                "context": {"text": "Esta es una prueva de texto", "offset": 12, "length": 6},
                "replacements": [{"value": "prueba"}],
            }
        ]
    }

    class MockResponse:
        status = 200
        def read(self):
            return json.dumps(sample_response).encode("utf-8")
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    import urllib.request
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=10.0: MockResponse())

    issues = analizar_archivo_languagetool(doc, lang="es-AR")
    assert len(issues) == 1
    assert issues[0].original_word == "prueva"
    assert issues[0].replacements[0] == "prueba"
    assert issues[0].line == 1

    # Aplicar autofix
    arreglos = aplicar_autofix_archivo(doc, issues)
    assert arreglos == 1
    assert "Esta es una prueba de texto" in doc.read_text(encoding="utf-8")


def test_generar_reporte_markdown(tmp_path: Path):
    issues = [
        LanguageToolIssue(
            file_path=tmp_path / "capitulo.md",
            line=5,
            column=10,
            message="Palabra desconocida",
            short_message="Error",
            rule_id="SPELL_CHECK",
            category="Ortografía",
            context="El puntero apunta a nada",
            replacements=["puntero", "puente"],
            length=7,
            original_word="puntro",
        )
    ]
    md = generar_reporte_markdown(issues)
    assert "## Auditoría de Ortografía y Gramática (LanguageTool)" in md
    assert "`capitulo.md`" in md
    assert "`puntro`" in md
    assert "`puntero`" in md


def test_cli_spellcheck_y_report(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "myst.yml").write_text("version: 1\n", encoding="utf-8")
    apunte = tmp_path / "apunte"
    apunte.mkdir()
    doc = apunte / "01_intro.md"
    doc.write_text("Texto con errror tipografico.\n", encoding="utf-8")

    sample_response = {
        "matches": [
            {
                "message": "Falta de ortografía",
                "shortMessage": "Error",
                "offset": 10,
                "length": 6,
                "rule": {"id": "MORFOLOGIK_RULE_ES", "category": {"name": "Ortografía"}},
                "context": {"text": "Texto con errror tipografico", "offset": 10, "length": 6},
                "replacements": [{"value": "error"}],
            }
        ]
    }

    class MockResponse:
        status = 200
        def read(self):
            return json.dumps(sample_response).encode("utf-8")
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    import urllib.request
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=10.0: MockResponse())

    # 1. Chequeo CLI sin fix (exit code 1 por encontrar observaciones)
    res = runner.invoke(app, ["spellcheck", str(doc)])
    assert res.exit_code == 1
    assert "errror" in res.output or "Observaciones" in res.output

    # 2. Salida JSON
    res_json = runner.invoke(app, ["spellcheck", str(doc), "--json"])
    assert res_json.exit_code == 1
    assert "total_issues" in res_json.output

    # 3. Reporte Markdown
    md_out = tmp_path / "reporte_lt.md"
    res_md = runner.invoke(app, ["spellcheck", str(doc), "--md", str(md_out)])
    assert res_md.exit_code == 1
    assert md_out.is_file()
    assert "LanguageTool" in md_out.read_text(encoding="utf-8")

    # 4. Chequeo con Autofix
    res_fix = runner.invoke(app, ["spellcheck", str(doc), "--fix"])
    assert "Texto con error tipografico." in doc.read_text(encoding="utf-8")

    # 5. Comando report
    res_rep = runner.invoke(app, ["report", str(doc)])
    assert res_rep.exit_code == 0
    assert "Auditoría de Ortografía y Gramática" in res_rep.output


def test_consultar_languagetool_premium_y_env_vars(monkeypatch):
    captured_requests = []

    class MockResponse:
        status = 200
        def read(self):
            return b'{"matches": []}'
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    import urllib.request
    def mock_urlopen(req, timeout=10.0):
        captured_requests.append(req)
        return MockResponse()

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)

    # Test 1: Parámetros explícitos premium
    consultar_languagetool(
        "Texto de prueba",
        username="docente@uba.ar",
        api_key="secret-api-key-123",
        premium=True,
    )
    assert len(captured_requests) == 1
    req = captured_requests[0]
    assert "api.languagetoolplus.com" in req.full_url
    data_str = req.data.decode("utf-8")
    assert "username=docente%40uba.ar" in data_str
    assert "apiKey=secret-api-key-123" in data_str

    # Test 2: Env vars
    monkeypatch.setenv("LANGUAGETOOL_USERNAME", "env_user@uba.ar")
    monkeypatch.setenv("LANGUAGETOOL_API_KEY", "env-key-999")
    monkeypatch.setenv("LANGUAGETOOL_PREMIUM", "true")

    consultar_languagetool("Texto de prueba dos")
    assert len(captured_requests) == 2
    req2 = captured_requests[1]
    assert "api.languagetoolplus.com" in req2.full_url
    data_str2 = req2.data.decode("utf-8")
    assert "username=env_user%40uba.ar" in data_str2
    assert "apiKey=env-key-999" in data_str2

