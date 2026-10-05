"""Enlaces externos caídos (QoL #713) y bloques de código sin lenguaje (QoL #709).

Bajan los números del informe del apunte (N-APUNTE-02): un enlace a un recurso que ya no existe y
un bloque ``` sin lenguaje (sin resaltado, y que el lector de pantalla no sabe anunciar).
"""

from __future__ import annotations

import re
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

_URL = re.compile(r"https?://[^\s)\]\"'<>`]+")
_APERTURA = re.compile(r"^(?P<sangria>\s*)(?P<cerca>`{3,}|~{3,})(?P<info>.*)$")
AGENTE = "myst-tools check-links (+https://github.com/INGCOM-UNRN-P1/myst-tools)"


@dataclass
class Hallazgo:
    linea: int
    tipo: str
    mensaje: str


def urls_de(contenido: str) -> List[Tuple[int, str]]:
    """(línea, url) de cada enlace http(s), sin la puntuación final que no es parte de la URL."""
    encontradas = []
    for n, linea in enumerate(contenido.splitlines(), 1):
        for m in _URL.finditer(linea):
            encontradas.append((n, m.group(0).rstrip(".,;:")))
    return encontradas


def estado_de(url: str, timeout: float = 10.0) -> Optional[str]:
    """None si responde bien; si no, la causa (código HTTP o error de conexión)."""
    for metodo in ("HEAD", "GET"):  # algunos servidores no aceptan HEAD
        pedido = urllib.request.Request(url, method=metodo, headers={"User-Agent": AGENTE})
        try:
            with urllib.request.urlopen(pedido, timeout=timeout):
                return None
        except urllib.error.HTTPError as exc:
            if metodo == "HEAD" and exc.code in (403, 405, 501):
                continue
            return f"HTTP {exc.code}"
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            razon = getattr(exc, "reason", exc)
            return f"sin respuesta ({razon})"
    return None


def enlaces_caidos(urls: Iterable[str], hilos: int = 8, timeout: float = 10.0) -> Dict[str, str]:
    """URL → causa, de las que no responden bien. Cada URL se consulta una sola vez."""
    unicas = sorted(set(urls))
    with ThreadPoolExecutor(max_workers=hilos) as grupo:
        estados = list(grupo.map(lambda u: estado_de(u, timeout), unicas))
    return {u: e for u, e in zip(unicas, estados) if e}


def bloques_sin_lenguaje(contenido: str) -> List[Hallazgo]:
    """Bloques de código abiertos con ``` (o ~~~) sin lenguaje. Los de directiva (```{note}) y
    los anidados en un bloque más largo no cuentan."""
    hallazgos: List[Hallazgo] = []
    abierto: Optional[str] = None
    for n, linea in enumerate(contenido.splitlines(), 1):
        m = _APERTURA.match(linea)
        if not m:
            continue
        cerca, info = m.group("cerca"), m.group("info").strip()
        if abierto is None:
            abierto = cerca
            if not info:
                hallazgos.append(Hallazgo(n, "bloque-sin-lenguaje",
                                          "Bloque de código sin lenguaje: indicá c, bash, text… (```c) para el resaltado y la accesibilidad."))
        elif cerca[0] == abierto[0] and len(cerca) >= len(abierto) and not info:
            abierto = None
    return hallazgos
