"""Enlaces externos caídos (QoL #713) y bloques sin lenguaje (QoL #709)."""

import http.server
import threading

import pytest

from myst_tools.enlaces_y_bloques import bloques_sin_lenguaje, enlaces_caidos, urls_de


def test_bloques_sin_lenguaje():
    md = "```\nx\n```\n\n```c\nint a;\n```\n\n````{note}\n```\nadentro\n```\n````\n\n~~~\ny\n~~~\n"
    assert [h.linea for h in bloques_sin_lenguaje(md)] == [1, 15]


def test_urls_sin_puntuacion_final():
    assert urls_de("Ver https://ejemplo.org/a. y (https://b.org/c)") == [(1, "https://ejemplo.org/a"), (1, "https://b.org/c")]


class _Manejador(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200 if self.path == "/ok" else 404)
        self.end_headers()

    do_GET = do_HEAD

    def log_message(self, *args):
        pass


@pytest.fixture
def servidor(monkeypatch):
    for variable in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"):
        monkeypatch.delenv(variable, raising=False)
    monkeypatch.setenv("no_proxy", "*")
    srv = http.server.HTTPServer(("127.0.0.1", 0), _Manejador)
    hilo = threading.Thread(target=srv.serve_forever, daemon=True)
    hilo.start()
    yield f"http://127.0.0.1:{srv.server_port}"
    srv.shutdown()


def test_enlaces_caidos(servidor):
    caidos = enlaces_caidos([f"{servidor}/ok", f"{servidor}/nada", "http://127.0.0.1:1/x"], timeout=3)
    assert set(caidos) == {f"{servidor}/nada", "http://127.0.0.1:1/x"}
    assert caidos[f"{servidor}/nada"] == "HTTP 404"
