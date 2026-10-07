"""Accesibilidad del material MyST: texto alternativo, orden de encabezados, enlaces y contraste.

Cubre el gap de accesibilidad de la revisión (05 §3: 22 archivos del apunte la mencionan y ninguna
herramienta la chequeaba sobre MyST). Los criterios son los de WCAG 2.1 que se pueden ver en el fuente:

- imágenes sin texto alternativo (1.1.1), o con uno que no describe nada («imagen», el nombre del archivo);
- saltos en el orden de los encabezados y más de un título `#` por página (1.3.1, 2.4.6);
- enlaces cuyo texto no dice adónde llevan, como «acá» o «click aquí» (2.4.4);
- color de texto con contraste menor que 4.5:1 en estilos en línea (1.4.3);
- iframes sin `title` y `{list-table}` sin fila de encabezado (4.1.2, 1.3.1).

El contenido de los bloques de código no se revisa: un `# comentario` ahí no es un encabezado.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class HallazgoA11y:
    linea: int
    regla: str
    severidad: str  # "error" o "aviso"
    mensaje: str


ALT_GENERICOS = {"imagen", "image", "img", "figura", "figure", "foto", "photo", "captura", "screenshot",
                 "grafico", "gráfico", "diagrama", "icono", "ícono", "logo", "picture"}
ENLACES_GENERICOS = {"aqui", "aquí", "aca", "acá", "click", "clic", "click aqui", "click aquí", "clic aqui",
                     "clic aquí", "hace click aqui", "hacé click aquí", "hacé clic aquí", "este enlace", "enlace",
                     "link", "este link", "ver mas", "ver más", "mas", "más", "leer mas", "leer más", "here",
                     "click here", "more", "read more"}
# Directivas cuyo contenido es código o datos: no se revisa como Markdown.
DIRECTIVAS_CRUDAS = {"code", "code-block", "code-cell", "sourcecode", "literalinclude", "mermaid", "math", "raw",
                     "csv-table", "graphviz", "embed", "include"}

RE_APERTURA = re.compile(r"^(\s*)(`{3,}|~{3,}|:{3,})\s*(\{([\w:-]+)\})?\s*(.*)$")
RE_OPCION = re.compile(r"^\s*:([\w-]+):\s*(.*)$")
RE_ENCABEZADO = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
RE_IMAGEN = re.compile(r"!\[([^\]]*)\]\(\s*<?([^)\s>]+)")
RE_ENLACE = re.compile(r"(?<!!)\[([^\]]+)\]\((?!\s*\))[^)]*\)")
RE_IMG_HTML = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
RE_IFRAME = re.compile(r"<iframe\b[^>]*>", re.IGNORECASE)
RE_ESTILO = re.compile(r"style\s*=\s*([\"'])(.*?)\1", re.IGNORECASE)
RE_ATRIBUTO_ALT = re.compile(r"\balt\s*=\s*([\"'])(.*?)\1", re.IGNORECASE)
RE_TITULO_FRONTMATTER = re.compile(r"^title\s*:\s*\S", re.MULTILINE)

COLORES_CON_NOMBRE = {"black": "#000000", "white": "#ffffff", "red": "#ff0000", "green": "#008000",
                      "blue": "#0000ff", "yellow": "#ffff00", "gray": "#808080", "grey": "#808080",
                      "silver": "#c0c0c0", "orange": "#ffa500", "lightgray": "#d3d3d3", "lightgrey": "#d3d3d3",
                      "lime": "#00ff00", "cyan": "#00ffff", "aqua": "#00ffff", "pink": "#ffc0cb"}


def _normalizar(texto: str) -> str:
    return re.sub(r"[\s\W_]+", " ", texto.lower()).strip()


def color_a_rgb(valor: str) -> Optional[Tuple[int, int, int]]:
    """#rgb, #rrggbb, rgb(r, g, b) o un nombre básico → (r, g, b); None si no se entiende."""
    v = valor.strip().lower()
    v = COLORES_CON_NOMBRE.get(v, v)
    if re.fullmatch(r"#[0-9a-f]{3}", v):
        return tuple(int(c * 2, 16) for c in v[1:])  # type: ignore[return-value]
    if re.fullmatch(r"#[0-9a-f]{6}", v):
        return tuple(int(v[i:i + 2], 16) for i in (1, 3, 5))  # type: ignore[return-value]
    m = re.fullmatch(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*[\d.]+\s*)?\)", v)
    if m:
        return tuple(min(255, int(x)) for x in m.groups())  # type: ignore[return-value]
    return None


def contraste(primero: Tuple[int, int, int], segundo: Tuple[int, int, int]) -> float:
    """Relación de contraste WCAG 2.1 entre dos colores (1 a 21)."""
    def luminancia(rgb: Tuple[int, int, int]) -> float:
        canales = []
        for c in rgb:
            s = c / 255
            canales.append(s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4)
        return 0.2126 * canales[0] + 0.7152 * canales[1] + 0.0722 * canales[2]

    claro, oscuro = sorted((luminancia(primero), luminancia(segundo)), reverse=True)
    return (claro + 0.05) / (oscuro + 0.05)


def _declaraciones(estilo: str) -> Dict[str, str]:
    resultado = {}
    for parte in estilo.split(";"):
        if ":" in parte:
            nombre, valor = parte.split(":", 1)
            resultado[nombre.strip().lower()] = valor.strip()
    return resultado


def _revisar_estilo(estilo: str, linea: int) -> Optional[HallazgoA11y]:
    declaraciones = _declaraciones(estilo)
    texto = color_a_rgb(declaraciones.get("color", ""))
    if texto is None:
        return None
    fondo_declarado = declaraciones.get("background-color") or declaraciones.get("background")
    fondo = color_a_rgb(fondo_declarado) if fondo_declarado else None
    if fondo_declarado and fondo is None:
        return None
    relacion = contraste(texto, fondo or (255, 255, 255))
    if relacion >= 4.5:
        return None
    if fondo is not None:
        return HallazgoA11y(linea, "contraste", "error",
                            f"El texto ({declaraciones['color']}) sobre {fondo_declarado} tiene contraste "
                            f"{relacion:.1f}:1; WCAG pide al menos 4.5:1.")
    return HallazgoA11y(linea, "contraste", "aviso",
                        f"El texto ({declaraciones['color']}) sobre fondo blanco tiene contraste {relacion:.1f}:1 "
                        "(WCAG pide 4.5:1); además, con el tema oscuro el fondo cambia y el color fijo puede no verse.")


def _revisar_alt(alt: str, origen: str, linea: int, que: str) -> Optional[HallazgoA11y]:
    if not alt.strip():
        return HallazgoA11y(linea, "alt-faltante", "error",
                            f"{que} {origen} no tiene texto alternativo: describí qué muestra (si es decorativa, "
                            "decilo con un texto alternativo vacío explícito en la directiva).")
    nombre = origen.rsplit("/", 1)[-1]
    if _normalizar(alt) in ALT_GENERICOS or alt.strip() == nombre or re.fullmatch(r"[\w-]+\.(png|jpe?g|gif|svg|webp)", alt.strip(), re.I):
        return HallazgoA11y(linea, "alt-generico", "aviso",
                            f"El texto alternativo «{alt.strip()}» de {origen} no describe la imagen: decí qué "
                            "muestra y por qué está ahí.")
    return None


def _revisar_linea(linea: str, numero: int, hallazgos: List[HallazgoA11y]) -> None:
    for m in RE_IMAGEN.finditer(linea):
        hallazgo = _revisar_alt(m.group(1), m.group(2), numero, "La imagen")
        if hallazgo:
            hallazgos.append(hallazgo)
    for m in RE_ENLACE.finditer(linea):
        if _normalizar(m.group(1)) in {_normalizar(e) for e in ENLACES_GENERICOS}:
            hallazgos.append(HallazgoA11y(numero, "enlace-generico", "error",
                                          f"El enlace «{m.group(1)}» no dice adónde lleva: un lector de pantalla "
                                          "lista los enlaces sueltos, así que el texto tiene que nombrar el destino."))
    for m in RE_IMG_HTML.finditer(linea):
        alt = RE_ATRIBUTO_ALT.search(m.group(0))
        if alt is None:
            hallazgos.append(HallazgoA11y(numero, "alt-faltante", "error",
                                          "La etiqueta <img> no tiene atributo alt."))
        else:
            src = re.search(r"\bsrc\s*=\s*([\"'])(.*?)\1", m.group(0))
            hallazgo = _revisar_alt(alt.group(2), src.group(2) if src else "<img>", numero, "La imagen") \
                if alt.group(2).strip() else None
            if hallazgo:
                hallazgos.append(hallazgo)
    for m in RE_IFRAME.finditer(linea):
        if not re.search(r"\btitle\s*=", m.group(0), re.IGNORECASE):
            hallazgos.append(HallazgoA11y(numero, "iframe-sin-titulo", "error",
                                          "El <iframe> no tiene title: un lector de pantalla no puede decir qué "
                                          "contiene (un video, un ejercicio…)."))
    for m in RE_ESTILO.finditer(linea):
        hallazgo = _revisar_estilo(m.group(2), numero)
        if hallazgo:
            hallazgos.append(hallazgo)


def auditar_accesibilidad(contenido: str) -> List[HallazgoA11y]:
    """Hallazgos de accesibilidad de un archivo MyST Markdown."""
    lineas = contenido.splitlines()
    hallazgos: List[HallazgoA11y] = []
    inicio = 0
    nivel_anterior = 0
    titulos = 0
    if lineas and lineas[0].strip() == "---":
        for i in range(1, len(lineas)):
            if lineas[i].strip() == "---":
                inicio = i + 1
                if RE_TITULO_FRONTMATTER.search("\n".join(lineas[1:i])):
                    # Con title: en el frontmatter, la página puede empezar con # o con ##; lo que se
                    # cuenta como repetido es un segundo # en el contenido.
                    nivel_anterior = 1
                break

    pila: List[Tuple[str, int, Optional[str]]] = []  # (carácter del cerco, largo, directiva)
    i = inicio
    while i < len(lineas):
        linea, numero = lineas[i], i + 1
        apertura = RE_APERTURA.match(linea)
        if pila:
            caracter, largo, directiva = pila[-1]
            cierre = linea.strip()
            if cierre and set(cierre) == {caracter} and len(cierre) >= largo:
                pila.pop()
                i += 1
                continue
            if directiva is None or directiva in DIRECTIVAS_CRUDAS:
                i += 1
                continue  # contenido de un bloque de código
        if apertura and (apertura.group(4) or apertura.group(2)[0] in "`~"):
            cerco, directiva, argumento = apertura.group(2), apertura.group(4), apertura.group(5).strip()
            pila.append((cerco[0], len(cerco), directiva))
            # Opciones de la directiva (:alt:, :header-rows:…), al principio del contenido.
            opciones: Dict[str, str] = {}
            j = i + 1
            while j < len(lineas) and (m_opcion := RE_OPCION.match(lineas[j])):
                nombre, valor = m_opcion.groups()
                opciones[nombre] = valor
                j += 1
            if directiva in ("image", "figure"):
                if "alt" not in opciones:
                    severidad = "aviso" if directiva == "figure" else "error"
                    hallazgos.append(HallazgoA11y(
                        numero, "alt-faltante", severidad,
                        f"La {'figura' if directiva == 'figure' else 'imagen'} {argumento} no tiene :alt:"
                        + (" (la leyenda no reemplaza al texto alternativo: describe el contexto, no la imagen)."
                           if directiva == "figure" else ".")))
                else:
                    hallazgo = _revisar_alt(opciones["alt"], argumento, numero, "La imagen")
                    if hallazgo and hallazgo.regla == "alt-generico":
                        hallazgos.append(hallazgo)
            elif directiva == "list-table" and "header-rows" not in opciones:
                hallazgos.append(HallazgoA11y(numero, "tabla-sin-encabezado", "aviso",
                                              "La {list-table} no tiene :header-rows:: sin fila de encabezado, un "
                                              "lector de pantalla no puede decir a qué columna pertenece cada dato."))
            i = j
            continue

        encabezado = RE_ENCABEZADO.match(linea)
        if encabezado:
            nivel = len(encabezado.group(1))
            if nivel == 1:
                titulos += 1
                if titulos > 1:
                    hallazgos.append(HallazgoA11y(numero, "titulo-repetido", "error",
                                                  "La página tiene más de un título #: usá ## para las secciones "
                                                  "(los lectores de pantalla navegan por niveles)."))
            if nivel_anterior and nivel > nivel_anterior + 1:
                hallazgos.append(HallazgoA11y(numero, "encabezado-salto", "error",
                                              f"El encabezado salta de {'#' * nivel_anterior} a {'#' * nivel}: "
                                              f"usá {'#' * (nivel_anterior + 1)} (los niveles no se eligen por "
                                              "tamaño de letra sino por estructura)."))
            elif not nivel_anterior and nivel > 1:
                hallazgos.append(HallazgoA11y(numero, "sin-titulo", "aviso",
                                              f"La página empieza con {'#' * nivel}: falta el título # (o title: "
                                              "en el frontmatter)."))
            nivel_anterior = nivel
        _revisar_linea(linea, numero, hallazgos)
        i += 1
    return hallazgos
