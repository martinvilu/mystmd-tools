import runpy
import sys

import pytest


@pytest.fixture
def ejecutar_como_main(monkeypatch):
    """`python -m <modulo>` en proceso, sin el RuntimeWarning de runpy.

    El paquete importa estos módulos desde `__init__`, así que ya están en
    `sys.modules`; runpy avisa de eso salvo que se los saque antes (monkeypatch
    los restaura al terminar el test).
    """

    def _run(modulo: str):
        monkeypatch.delitem(sys.modules, modulo, raising=False)
        return runpy.run_module(modulo, run_name="__main__")

    return _run
