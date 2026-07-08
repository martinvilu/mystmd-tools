"""
fix_dup_anchors.py — Detecta y corrige anclas MyST duplicadas.

Para cada ancla definida en más de un archivo:
  • Renombra la definición en cada archivo prefijando el stem del archivo.
      (resumen)=   en  05_func.md   →   (5_func-resumen)=
  • Actualiza las referencias en el mismo archivo hacia la nueva etiqueta.
  • Reporta referencias ambiguas (en archivos que no definen el ancla)
    y las resuelve apuntando al primer candidato (orden alfabético).

Fuentes de definición reconocidas:
  • Anclas MyST:          (etiqueta)=
  • Opción de directiva:  :label: etiqueta

Lugares donde se actualizan referencias:
  • Roles MyST:           {ref}`etiqueta`  /  {ref}`texto <etiqueta>`
  • (Cualquier rol)       {numref}`etiqueta`  etc.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

# Expresiones regulares
ANCHOR_DEF = re.compile(r'^\(([^)\n]+)\)=\s*$', re.MULTILINE)
DIRECTIVE_LABEL = re.compile(r'^(\s*:label:\s+)(\S+)[ \t]*$', re.MULTILINE)

ROLE_SIMPLE = re.compile(
    r'(\{[a-z][a-z0-9_-]*\}`)([^`<>\n]+?)(`)'
)

ROLE_TITLED = re.compile(
    r'(\{[a-z][a-z0-9_-]*\}`[^`\n]*?<)([^>\n]+)(>`)'
)


def collect_anchors(files: list[Path]) -> dict[str, list[Path]]:
    """
    Retorna {label: [archivo1, archivo2, ...]} para todos los archivos.
    Cada archivo aparece una sola vez por label aunque lo defina múltiples
    veces en el mismo archivo.
    """
    result: dict[str, list[Path]] = defaultdict(list)

    for path in sorted(files):
        try:
            text = path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error al leer {path}: {e}", file=sys.stderr)
            continue
        seen_in_file: set[str] = set()

        for m in ANCHOR_DEF.finditer(text):
            label = m.group(1).strip()
            if label not in seen_in_file:
                result[label].append(path)
                seen_in_file.add(label)

        for m in DIRECTIVE_LABEL.finditer(text):
            label = m.group(2).strip()
            if label not in seen_in_file:
                result[label].append(path)
                seen_in_file.add(label)

    return dict(result)


def build_rename_map(
    duplicates: dict[str, list[Path]],
    all_labels: dict[str, list[Path]],
) -> dict[str, dict[Path, str]]:
    """
    Para cada label duplicado construye:
        renames[label][archivo] = nuevo_label
    """
    existing: set[str] = set(all_labels.keys())
    renames: dict[str, dict[Path, str]] = {}

    for label, files in duplicates.items():
        renames[label] = {}
        for path in files:
            stem = path.stem
            candidate = f'{stem}-{label}'
            if candidate in existing and candidate != label:
                n = 2
                while f'{candidate}-{n}' in existing:
                    n += 1
                candidate = f'{candidate}-{n}'
            existing.add(candidate)
            renames[label][path] = candidate

    return renames


def apply_to_file(
    path: Path,
    renames: dict[str, dict[Path, str]],
    dry_run: bool,
) -> tuple[int, int, list[str]]:
    """
    Procesa un archivo. Retorna (n_defs, n_refs, warnings).
    """
    try:
        original = path.read_text(encoding='utf-8')
    except Exception as e:
        return 0, 0, [f"No se pudo leer el archivo: {e}"]

    text = original
    n_defs = 0
    n_refs = 0
    warnings: list[str] = []

    # 1. Renombrar definiciones (ancla)=
    def repl_anchor_def(m: re.Match) -> str:
        nonlocal n_defs
        label = m.group(1).strip()
        if label in renames and path in renames[label]:
            n_defs += 1
            return f'({renames[label][path]})='
        return m.group(0)

    text = ANCHOR_DEF.sub(repl_anchor_def, text)

    # 2. Renombrar :label: en directivas
    def repl_directive_label(m: re.Match) -> str:
        nonlocal n_defs
        prefix = m.group(1)
        label  = m.group(2).strip()
        if label in renames and path in renames[label]:
            n_defs += 1
            return f'{prefix}{renames[label][path]}'
        return m.group(0)

    text = DIRECTIVE_LABEL.sub(repl_directive_label, text)

    # 3. Actualizar referencias
    def resolve(label: str) -> tuple[str, str | None]:
        label = label.strip()
        if label not in renames:
            return label, None

        file_map = renames[label]

        if path in file_map:
            return file_map[path], None

        first_path, first_new = next(iter(file_map.items()))
        candidates_str = ', '.join(
            f'{p.name} → {nl}' for p, nl in file_map.items()
        )
        warn = (
            f'referencia `{label}` resuelta a `{first_new}` '
            f'(candidatos: {candidates_str})'
        )
        return first_new, warn

    def repl_role_simple(m: re.Match) -> str:
        nonlocal n_refs
        prefix, label, suffix = m.group(1), m.group(2), m.group(3)
        new_label, warn = resolve(label)
        if warn:
            warnings.append(warn)
        if new_label != label.strip():
            n_refs += 1
            return f'{prefix}{new_label}{suffix}'
        return m.group(0)

    def repl_role_titled(m: re.Match) -> str:
        nonlocal n_refs
        prefix, label, suffix = m.group(1), m.group(2), m.group(3)
        new_label, warn = resolve(label)
        if warn:
            warnings.append(warn)
        if new_label != label.strip():
            n_refs += 1
            return f'{prefix}{new_label}{suffix}'
        return m.group(0)

    text = ROLE_SIMPLE.sub(repl_role_simple, text)
    text = ROLE_TITLED.sub(repl_role_titled, text)

    # 4. Escribir si cambió
    if text != original and not dry_run:
        try:
            path.write_text(text, encoding='utf-8')
        except Exception as e:
            warnings.append(f"No se pudo escribir el archivo: {e}")

    return n_defs, n_refs, warnings


def run_fix_dup_anchors(directory: str = '.', dry_run: bool = False, report: bool = False) -> int:
    root = Path(directory)
    if not root.is_dir():
        print(f'Error: {root} no es un directorio.', file=sys.stderr)
        return 2

    # Recolectar archivos .md
    files = sorted(root.rglob('*.md'))
    # Ignorar archivos en directorios ocultos (como .venv, .git)
    files = [f for f in files if not any(part.startswith('.') for part in f.parts[:-1])]

    if not files:
        print('No se encontraron archivos .md.')
        return 0

    print(f'Escaneando {len(files)} archivos en {root.resolve()} ...\n')

    # Recolectar todos los labels
    all_labels = collect_anchors(files)
    duplicates = {
        label: paths
        for label, paths in all_labels.items()
        if len(paths) > 1
    }

    if not duplicates:
        print('No se encontraron anclas duplicadas.')
        return 0

    # Mostrar duplicados encontrados
    print(f'Anclas duplicadas detectadas: {len(duplicates)}\n')
    for label in sorted(duplicates):
        paths = duplicates[label]
        print(f'  ({label})=')
        for p in paths:
            print(f'      {p.relative_to(root) if p.is_relative_to(root) else p}')
    print()

    if report:
        return 0

    # Construir mapa de renombrado
    renames = build_rename_map(duplicates, all_labels)

    # Mostrar plan de renombrado
    mode = '(dry-run)' if dry_run else ''
    print(f'Plan de renombrado {mode}:\n')
    for label in sorted(renames):
        for path, new_label in renames[label].items():
            print(f'  {path.name}  ({label})=  →  ({new_label})=')
    print()

    # Aplicar a todos los archivos
    total_defs = total_refs = total_warns = 0
    modified_files = 0

    for path in files:
        n_defs, n_refs, warns = apply_to_file(path, renames, dry_run)

        if n_defs or n_refs or warns:
            modified_files += 1
            marker = '~' if dry_run else '✓'
            print(f'  {marker}  {path.relative_to(root) if path.is_relative_to(root) else path}')
            if n_defs:
                print(f'       definiciones renombradas : {n_defs}')
            if n_refs:
                print(f'       referencias actualizadas : {n_refs}')
            for w in warns:
                print(f'       ⚠ {w}')
                total_warns += 1

        total_defs += n_defs
        total_refs += n_refs

    print()
    action = 'serían modificados' if dry_run else 'modificados'
    print(
        f'Resumen: {modified_files} archivos {action} — '
        f'{total_defs} definiciones, {total_refs} referencias'
        + (f', {total_warns} advertencias' if total_warns else '')
    )

    return 1 if total_warns else 0
