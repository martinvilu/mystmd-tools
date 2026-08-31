"""Inyector de bloques y callouts didácticos estandarizados para MyST Markdown."""

from __future__ import annotations


def formatear_callout(tipo: str, titulo: str, cuerpo: str) -> str:
    """Formatea un bloque admonition / callout con el estándar MyST."""
    tipo_valido = tipo.lower() if tipo.lower() in ("note", "tip", "warning", "important", "danger") else "note"
    titulo_str = f" {titulo}" if titulo else ""
    return f"""```{{{tipo_valido}}}{titulo_str}
{cuerpo.strip()}
```"""
