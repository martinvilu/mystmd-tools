"""Auditor de formato de tablas Markdown y alineación de columnas."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Tuple


@dataclass
class TableIssue:
    line_number: int
    message: str
    column_count_expected: int
    column_count_found: int


def parse_markdown_tables(content: str) -> List[Dict[str, Any]]:
    """Identifica bloques de tablas Markdown delimitadas por pipes."""
    lines = content.splitlines()
    tables = []
    current_table_lines: List[Tuple[int, str]] = []

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if "|" in stripped and (stripped.startswith("|") or stripped.endswith("|")):
            current_table_lines.append((idx, line))
        else:
            if len(current_table_lines) >= 2:
                tables.append(current_table_lines)
            current_table_lines = []

    if len(current_table_lines) >= 2:
        tables.append(current_table_lines)

    parsed_tables = []
    for tbl in tables:
        first_line_no = tbl[0][0]
        raw_rows = [row[1] for row in tbl]
        parsed_tables.append({
            "start_line": first_line_no,
            "raw_rows": raw_rows,
        })
    return parsed_tables


def auditar_tabla(raw_rows: List[str], start_line: int = 1) -> List[TableIssue]:
    """Audita inconsistencias de columnas y separadores en una tabla."""
    issues = []
    if len(raw_rows) < 2:
        return issues

    def split_cells(row_str: str) -> List[str]:
        s = row_str.strip()
        if s.startswith("|"):
            s = s[1:]
        if s.endswith("|"):
            s = s[:-1]
        return [c.strip() for c in s.split("|")]

    header_cells = split_cells(raw_rows[0])
    expected_cols = len(header_cells)

    # Verificar separador (fila 1)
    sep_cells = split_cells(raw_rows[1])
    if len(sep_cells) != expected_cols:
        issues.append(TableIssue(
            line_number=start_line + 1,
            message="El separador de tabla no coincide en cantidad de columnas con el encabezado",
            column_count_expected=expected_cols,
            column_count_found=len(sep_cells),
        ))

    # Verificar que cada celda de separador tenga guiones
    for idx_c, cell in enumerate(sep_cells):
        if not re.match(r"^:?-+:?$", cell):
            issues.append(TableIssue(
                line_number=start_line + 1,
                message=f"Separador inválido en columna {idx_c + 1}: '{cell}'",
                column_count_expected=expected_cols,
                column_count_found=len(sep_cells),
            ))

    # Verificar filas de datos
    for r_idx, row_str in enumerate(raw_rows[2:], start=2):
        cells = split_cells(row_str)
        if len(cells) != expected_cols:
            issues.append(TableIssue(
                line_number=start_line + r_idx,
                message=f"Fila con {len(cells)} columnas cuando se esperaban {expected_cols}",
                column_count_expected=expected_cols,
                column_count_found=len(cells),
            ))

    return issues


def formatear_tabla(raw_rows: List[str]) -> List[str]:
    """Alinea uniformemente las columnas de una tabla Markdown respetando alineación."""
    if len(raw_rows) < 2:
        return raw_rows

    def split_cells(row_str: str) -> List[str]:
        s = row_str.strip()
        if s.startswith("|"):
            s = s[1:]
        if s.endswith("|"):
            s = s[:-1]
        return [c.strip() for c in s.split("|")]

    grid = [split_cells(r) for r in raw_rows]
    max_cols = max(len(r) for r in grid)

    # Normalizar número de columnas
    for r in grid:
        while len(r) < max_cols:
            r.append("")

    # Calcular ancho máximo por columna
    col_widths = [3] * max_cols
    for r_idx, row in enumerate(grid):
        if r_idx == 1:
            continue
        for c_idx, cell in enumerate(row):
            col_widths[c_idx] = max(col_widths[c_idx], len(cell))

    # Analizar alineaciones del separador
    alignments = []
    for cell in grid[1]:
        c = cell.strip()
        if c.startswith(":") and c.endswith(":"):
            alignments.append("center")
        elif c.endswith(":"):
            alignments.append("right")
        else:
            alignments.append("left")

    while len(alignments) < max_cols:
        alignments.append("left")

    formatted_rows = []
    for r_idx, row in enumerate(grid):
        if r_idx == 1:
            # Separador
            sep_parts = []
            for c_idx, align in enumerate(alignments):
                w = col_widths[c_idx]
                if align == "center":
                    sep_parts.append(":" + "-" * (w - 2 if w > 2 else 1) + ":")
                elif align == "right":
                    sep_parts.append("-" * (w - 1 if w > 1 else 1) + ":")
                else:
                    sep_parts.append(":" + "-" * (w - 1 if w > 1 else 1))
            formatted_rows.append("| " + " | ".join(sep_parts) + " |")
        else:
            cell_parts = []
            for c_idx, cell in enumerate(row):
                w = col_widths[c_idx]
                align = alignments[c_idx]
                if align == "center":
                    cell_parts.append(cell.center(w))
                elif align == "right":
                    cell_parts.append(cell.rjust(w))
                else:
                    cell_parts.append(cell.ljust(w))
            formatted_rows.append("| " + " | ".join(cell_parts) + " |")

    return formatted_rows
