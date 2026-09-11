"""Auditor de enlaces a commits y líneas de código de repositorios de GitHub."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any


@dataclass
class GitHubLinkIssue:
    line_number: int
    url: str
    issue_type: str
    message: str


# Expresión regular para detectar URLs de GitHub
GITHUB_URL_PATTERN = r"https?://github\.com/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-]+)/(blob|tree|commit)/([a-zA-Z0-9_\-./#]+)"


def auditar_enlaces_github(contenido_md: str) -> List[GitHubLinkIssue]:
    """Audita la inmutabilidad y formato de los enlaces a GitHub en documentos Markdown."""
    issues = []
    lines = contenido_md.splitlines()

    for idx, line in enumerate(lines, 1):
        for m in re.finditer(r"https?://github\.com/[^\s)\]\"'>]+", line):
            url = m.group(0)
            
            # Enlaces a branches móviles (main, master) en vez de tags o commits SHA
            if "/blob/main/" in url or "/blob/master/" in url or "/tree/main/" in url or "/tree/master/" in url:
                issues.append(GitHubLinkIssue(
                    line_number=idx,
                    url=url,
                    issue_type="enlace_mutable",
                    message="El enlace apunta a una rama móvil ('main'/'master') en lugar de un commit SHA inmutable o tag de release.",
                ))

            # Enlaces a commits con SHA incompleto (menos de 7 caracteres)
            commit_match = re.search(r"/commit/([a-fA-F0-9]+)", url)
            if commit_match:
                sha = commit_match.group(1)
                if len(sha) < 7:
                    issues.append(GitHubLinkIssue(
                        line_number=idx,
                        url=url,
                        issue_type="sha_demasiado_corto",
                        message=f"El SHA del commit es demasiado corto ({len(sha)} caracteres), se requieren al menos 7.",
                    ))

            # Enlaces a líneas de código con rangos invertidos (#L20-L10)
            line_match = re.search(r"#L(\d+)(?:-L(\d+))?", url)
            if line_match:
                start_l = int(line_match.group(1))
                end_l_str = line_match.group(2)
                if end_l_str:
                    end_l = int(end_l_str)
                    if start_l > end_l:
                        issues.append(GitHubLinkIssue(
                            line_number=idx,
                            url=url,
                            issue_type="rango_lineas_invalido",
                            message=f"Rango de líneas invertido (#L{start_l}-L{end_l}).",
                        ))

    return issues
