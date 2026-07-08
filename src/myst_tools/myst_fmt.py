"""
myst_fmt.py — Formateador para archivos MyST Markdown.

Características:
  1. Limita las líneas de prosa a 80 caracteres (no toca bloques de código).
  2. Anota los cierres de guardas con el nombre de la directiva o lenguaje
     en la línea siguiente:
         :::
         <!-- {note} -->
  3. Corrige el tipo de guarda según la regla de anidamiento:
         directivas  ({...})  → colons  ':::'
         código puro (lang)   → backticks '```'
     La longitud original se respeta salvo colisión de anidamiento.
"""

from __future__ import annotations

import re
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

MAX_WIDTH: int = 80


@dataclass
class Fence:
    """Una guarda abierta en el stack de anidamiento."""
    kind:      str   # tipo corregido: 'colon' | 'backtick'
    length:    int   # longitud corregida (cantidad de : o `)
    label:     str   # directiva '{note}' o lenguaje 'python' (puede ser '')
    orig_kind: str   # tipo tal como aparece en el archivo fuente
    orig_len:  int   # longitud tal como aparece en el archivo fuente


# Expresiones regulares
_COLON_OPEN  = re.compile(r'^(:{3,})\s*(.*?)\s*$')
_BTICK_OPEN  = re.compile(r'^(`{3,})\s*(.*?)\s*$')
_COLON_CLOSE = re.compile(r'^(:{3,})\s*$')
_BTICK_CLOSE = re.compile(r'^(`{3,})\s*$')
_TRAILING_COMMENT = re.compile(r'\s*<!--.*?-->\s*$')


def _strip_comment(s: str) -> str:
    return _TRAILING_COMMENT.sub('', s)


_SOLO_COMMENT = re.compile(r'^\s*<!--.*?-->\s*$')

def _parse_open(line: str) -> Fence | None:
    """Intenta parsear la línea como apertura de guarda."""
    if _SOLO_COMMENT.match(line.rstrip()):
        return None

    s = _strip_comment(line.rstrip())

    m = _COLON_OPEN.match(s)
    if m:
        label = m.group(2).strip()
        n = len(m.group(1))
        return Fence('colon', n, label, 'colon', n)

    m = _BTICK_OPEN.match(s)
    if m:
        label = m.group(2).strip()
        n = len(m.group(1))
        return Fence('backtick', n, label, 'backtick', n)

    return None


def _is_close(line: str, top: Fence) -> bool:
    """
    Detecta si la línea cierra la guarda top.
    """
    s = line.rstrip()
    if top.orig_kind == 'colon':
        m = _COLON_CLOSE.match(s)
        return bool(m) and len(m.group(1)) >= top.orig_len
    else:
        m = _BTICK_CLOSE.match(s)
        return bool(m) and len(m.group(1)) >= top.orig_len


def _prescan_colon_lengths(lines: list[str]) -> dict[int, int]:
    """
    Asigna a cada apertura colon la longitud mínima necesaria para que ningún
    padre tenga la misma cantidad de colons (o menos) que un hijo directo.
    """
    stack: list[tuple[int, int, str, int]] = []
    blocks: list[list] = []

    for lineno, line in enumerate(lines):
        s = _strip_comment(line.rstrip())
        if _SOLO_COMMENT.match(s):
            continue

        if stack:
            _, top_orig_len, _, _ = stack[-1]
            m = _COLON_CLOSE.match(s)
            if m and len(m.group(1)) >= top_orig_len:
                stack.pop()
                continue

        m = _COLON_OPEN.match(s)
        if m:
            label    = m.group(2).strip()
            orig_len = len(m.group(1))
            is_lang  = bool(label) and not label.startswith('{')
            if not is_lang:
                parent_idx = stack[-1][3] if stack else None
                idx = len(blocks)
                blocks.append([lineno, orig_len, parent_idx])
                stack.append((lineno, orig_len, label, idx))

    if not blocks:
        return {}

    assigned = [b[1] for b in blocks]
    children: list[list[int]] = [[] for _ in blocks]
    for idx, (_, _, parent_idx) in enumerate(blocks):
        if parent_idx is not None:
            children[parent_idx].append(idx)

    for idx in range(len(blocks) - 1, -1, -1):
        _, _, parent_idx = blocks[idx]
        if parent_idx is None:
            continue
        if assigned[idx] >= assigned[parent_idx]:
            assigned[parent_idx] = assigned[idx] + 1

    return {blocks[idx][0]: assigned[idx] for idx in range(len(blocks))}


_VERBATIM_DIRECTIVES = frozenset([
    '{code-block}', '{code}', '{literalinclude}', '{parsed-literal}',
])

MIN_LINES_FOR_CODEBLOCK = 5


def _directive_base(label: str) -> str:
    return label.split()[0] if label else ''


def _count_code_lines(lines: list[str], open_idx: int, fence: Fence) -> int:
    """
    Cuenta las líneas de código no vacías dentro del fence.
    """
    j = open_idx + 1
    in_options = True
    count = 0
    while j < len(lines):
        if _is_close(lines[j], fence):
            break
        s = lines[j].strip()
        if in_options:
            if re.match(r'^:(?!:)\w', s):
                j += 1
                continue
            in_options = False
        if s:
            count += 1
        j += 1
    return count


def _has_linenos(lines: list[str], open_idx: int, fence: Fence) -> bool:
    """Retorna True si el fence ya tiene la opción ':linenos:' activa."""
    j = open_idx + 1
    while j < len(lines):
        if _is_close(lines[j], fence):
            break
        s = lines[j].strip()
        if not s:
            break
        if s == ':linenos:':
            return True
        if not re.match(r'^:(?!:)\w', s):
            break
        j += 1
    return False


def _correct(
    fence: Fence,
    stack: list[Fence],
    colon_lengths: dict[int, int],
    lineno: int,
) -> Fence:
    """
    Determina el tipo y longitud correctos para un fence.
    """
    is_directive = fence.label.startswith('{')
    is_lang      = bool(fence.label) and not is_directive
    is_verbatim  = _directive_base(fence.label) in _VERBATIM_DIRECTIVES

    def _btick_length() -> int:
        parent = max((f.length for f in stack if f.kind == 'backtick'), default=2)
        return max(fence.orig_len, parent + 1)

    if is_directive and is_verbatim:
        kind   = 'backtick'
        length = _btick_length()
    elif is_directive:
        kind   = 'colon'
        length = colon_lengths.get(lineno, fence.orig_len)
    elif is_lang:
        kind   = 'backtick'
        length = _btick_length()
    else:
        kind = fence.orig_kind
        if kind == 'colon':
            length = colon_lengths.get(lineno, fence.orig_len)
        else:
            length = _btick_length()

    return Fence(kind, length, fence.label, fence.orig_kind, fence.orig_len)


def _annotate_close(fence: Fence) -> list[str]:
    """
    Genera el cierre de guarda como dos líneas.
    """
    char = ':' if fence.kind == 'colon' else '`'
    base = char * fence.length
    if fence.label:
        return [base + '\n', f'<!-- {fence.label} -->\n']
    return [base + '\n']


_NOWRAP = re.compile(
    r'^\s*('
    r'#{1,6} '          # encabezados
    r'|\(.*\)=\s*$'     # anclas MyST
    r'|\|'              # filas de tabla
    r'|[-*_]{3,}\s*$'   # separadores / HR
    r'|!\['             # imágenes
    r'|:\S'             # opciones directiva
    r'|%\s'             # comentarios MyST
    r'|<!--'            # comentarios HTML
    r'|<[a-zA-Z/!]'    # etiquetas HTML
    r'|\$\$'            # bloques / inline math
    r'|\s*$'            # líneas vacías
    r')'
)


def _wrap_line(line: str) -> list[str]:
    """
    Envuelve una línea de prosa que supera MAX_WIDTH.
    """
    s = line.rstrip('\n')

    if len(s) <= MAX_WIDTH or _NOWRAP.match(s):
        return [s + '\n']

    m = re.match(r'^(\s*(?:[*\-+]\s+|\d+[.)]\s+|>\s*)*)', s)
    first_indent = m.group(1) if m else ''

    cont_indent = re.sub(
        r'[*\-+](?=\s)|>(?=\s?)|\d+[.)](?=\s)',
        lambda x: ' ' * len(x.group()),
        first_indent,
    )

    filled = textwrap.fill(
        s,
        width=MAX_WIDTH,
        initial_indent='',
        subsequent_indent=cont_indent,
        break_long_words=False,
        break_on_hyphens=False,
    )
    return [l + '\n' for l in filled.split('\n')]


def format_myst(source: str, width: int = MAX_WIDTH) -> str:
    """
    Formatea un string MyST Markdown.
    """
    global MAX_WIDTH
    MAX_WIDTH = width

    lines = source.splitlines(keepends=True)
    out: list[str] = []
    stack: list[Fence] = []

    i = 0
    colon_lengths = _prescan_colon_lengths(lines)

    # Preservar YAML frontmatter sin tocar
    if lines and lines[0].rstrip() == '---':
        out.append(lines[0])
        i = 1
        while i < len(lines):
            out.append(lines[i])
            if lines[i].rstrip() in ('---', '...'):
                i += 1
                break
            i += 1

    math_block = False
    while i < len(lines):
        line = lines[i]

        if stack and _is_close(line, stack[-1]):
            closed = stack.pop()
            if closed.label.startswith('{') and out and out[-1].strip() != '':
                out.append('\n')
            out.extend(_annotate_close(closed))
            i += 1
            if closed.label and i < len(lines):
                expected = f'<!-- {closed.label} -->'
                if lines[i].strip() == expected:
                    i += 1
            continue

        fence = _parse_open(line)
        if fence is not None:
            is_plain_lang = (
                fence.orig_kind == 'backtick'
                and bool(fence.label)
                and not fence.label.startswith('{')
            )
            is_codeblock_directive = (
                fence.orig_kind == 'backtick'
                and _directive_base(fence.label) in _VERBATIM_DIRECTIVES
            )

            if is_plain_lang or is_codeblock_directive:
                n_code = _count_code_lines(lines, i, fence)
                if n_code > MIN_LINES_FOR_CODEBLOCK:
                    if is_plain_lang:
                        lang      = fence.label
                        new_label = f'{{code-block}} {lang}'
                    else:
                        new_label = fence.label
                        parts     = fence.label.split()
                        lang      = parts[1] if len(parts) > 1 else ''

                    synthetic = Fence(
                        fence.orig_kind, fence.orig_len, new_label,
                        fence.orig_kind, fence.orig_len,
                    )
                    corrected = _correct(synthetic, stack, colon_lengths, i)
                    stack.append(corrected)

                    fence_str = '`' * corrected.length
                    out.append(f'{fence_str}{new_label}\n')

                    if not _has_linenos(lines, i, fence):
                        out.append(':linenos:\n')

                    i += 1
                    continue

            corrected = _correct(fence, stack, colon_lengths, i)
            stack.append(corrected)
            char = ':' if corrected.kind == 'colon' else '`'
            fence_str = char * corrected.length
            if corrected.label.startswith('{'):
                label_part = corrected.label
            elif corrected.label:
                label_part = ' ' + corrected.label
            else:
                label_part = ''
            out.append(fence_str + label_part + '\n')
            if corrected.label.startswith('{') and _directive_base(corrected.label) not in _VERBATIM_DIRECTIVES:
                next_raw = lines[i + 1] if i + 1 < len(lines) else ''
                next_s   = next_raw.strip()
                is_opt   = bool(re.match(r'^:(?!:)[\w-]', next_s))
                if next_s and not is_opt:
                    out.append('\n')
            i += 1
            continue

        if stack and stack[-1].kind == 'backtick':
            out.append(line if line.endswith('\n') else line + '\n')
            i += 1
            continue

        if line.rstrip() == '$$':
            math_block = not math_block
            out.append(line if line.endswith('\n') else line + '\n')
            i += 1
            continue

        if math_block:
            out.append(line if line.endswith('\n') else line + '\n')
            i += 1
            continue

        out.extend(_wrap_line(line))
        i += 1

    return ''.join(out)


def run_myst_fmt(
    files: list[str] | None = None,
    check: bool = False,
    stdout: bool = False,
    width: int = MAX_WIDTH
) -> int:
    # Si files es None o "-", leemos de stdin.
    # Pero si la entrada estándar es TTY y files es None/vacio, buscamos recursivamente en el directorio actual.
    if not files:
        if sys.stdin.isatty():
            # Buscar recursivamente en el directorio actual
            files = ["."]
        else:
            # Leer de stdin
            sys.stdout.write(format_myst(sys.stdin.read(), width=width))
            return 0
    elif files == ['-']:
        sys.stdout.write(format_myst(sys.stdin.read(), width=width))
        return 0

    # Expandir directorios si se han pasado
    expanded_files: list[Path] = []
    for f in files:
        path = Path(f)
        if path.is_dir():
            # Buscar todos los .md recursivamente
            md_files = path.rglob("*.md")
            # Filtrar ocultos
            md_files = [p for p in md_files if not any(part.startswith('.') for part in p.parts[:-1])]
            expanded_files.extend(md_files)
        elif path.is_file():
            expanded_files.append(path)
        else:
            print(f'myst_fmt: {path}: no existe', file=sys.stderr)
            return 2

    # Remover duplicados manteniendo el orden
    seen = set()
    unique_files = []
    for f in expanded_files:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)

    if not unique_files:
        print('No se encontraron archivos .md para formatear.', file=sys.stderr)
        return 0

    exit_code = 0
    for path in unique_files:
        try:
            source = path.read_text(encoding='utf-8')
            result = format_myst(source, width=width)
        except Exception as exc:
            print(f'myst_fmt: {path}: error — {exc}', file=sys.stderr)
            exit_code = 2
            continue

        if check:
            if source != result:
                print(f'necesita formato: {path}')
                exit_code = 1
        elif stdout:
            sys.stdout.write(result)
        else:
            if source != result:
                path.write_text(result, encoding='utf-8')
                print(f'formateado: {path}')

    return exit_code
