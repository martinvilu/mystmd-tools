"""CLI principal de myst-tools unificado con Typer y Rich.

Los comandos viven en los módulos cmd_*; importarlos los registra en `app`.
"""

from __future__ import annotations

from myst_tools._cli_base import _check_myst_yml, app, console, err_console, state  # noqa: F401
from myst_tools import cmd_indices, cmd_languagetool, cmd_calidad, cmd_extra, cmd_biblioteca  # noqa: F401


def main() -> None:
    app()


if __name__ == "__main__":
    main()
