"""Validador de sintaxis C para snippets embebidos en Markdown MyST.

Los bloques del apunte son, en su mayoría, fragmentos didácticos: sentencias sueltas (`x++;`), una
declaración o una función sin `main`. Compilarlos tal cual daba «inválidos» que no lo eran (N-MYST-02:
el 64 %, sobre todo «expected … before '++'», `size_t` sin `<stddef.h>` y declaraciones sin tipo). Por
eso cada bloque se compila con los headers estándar y, si no compila así, se prueba dentro de una
función. Si tampoco, pero todos los errores son de nombres que el texto declara en otra parte (un tipo,
una función o una variable de un bloque anterior), el bloque se da por válido: no es un error del
ejemplo. Un bloque `{code-block} c` con `:class: fragmento` no se compila.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from typing import Any, Dict, List, Tuple

# Solo headers de ISO C: los de POSIX (pthread, sockets) no existen en todas las plataformas.
HEADERS = ("stdio.h", "stdlib.h", "string.h", "stddef.h", "stdbool.h", "stdint.h", "inttypes.h", "limits.h",
           "float.h", "math.h", "ctype.h", "time.h", "errno.h", "assert.h", "stdarg.h")
# `#line 1`: los errores señalan la línea del bloque y no la del archivo con los headers agregados.
PROLOGO = "".join(f"#include <{h}>\n" for h in HEADERS) + "#line 1\n"

# ```c y las directivas ```{code-block} c / ```{code} c, cuyas opciones (:class: …) van al principio.
RE_BLOQUE = re.compile(r"```(?:[cC]|\{code-block\}[ \t]+[cC]|\{code\}[ \t]+[cC])[ \t]*\n(.*?)```", re.DOTALL)
RE_OPCION = re.compile(r"^\s*:[\w-]+:")
RE_FRAGMENTO = re.compile(r"^\s*:class:.*\bfragmento\b")
# Errores que dependen de declaraciones de otra parte del texto, no de la sintaxis del bloque.
RE_CONTEXTO = re.compile(r"unknown type name|undeclared|implicit declaration of function|invalid use of undefined type"
                         r"|has incomplete type|storage size of .* isn.t known|type defaults to .int."
                         r"|initializer element is not (?:constant|a compile-time constant)"
                         r"|\.h: No such file or directory")  # un header del proyecto que el texto define aparte
# Dentro de la función que envuelve al fragmento, un `return valor;` choca con su tipo (void): no es
# un error del bloque.
RE_ARTEFACTO_ENVOLTORIO = re.compile(r"in function returning (?:void|non-void)")
# Consecuencias de un tipo o una función que el compilador no conoce (solo cuentan si en la misma
# compilación hay un error de contexto): el tipo desconocido se toma como int.
RE_CASCADA = re.compile(r"request for member .* in something not a structure or union"
                        r"|makes (?:pointer from integer|integer from pointer) without a cast"
                        r"|expected .=., .,., .;., .asm. or .__attribute__. before .\{. token"
                        r"|conflicting types for|invalid type argument of")


def _errores(stderr: str) -> List[str]:
    return [linea for linea in stderr.splitlines() if " error: " in linea or " fatal error: " in linea]


def _solo_contexto(stderr: str, envuelto: bool = False) -> bool:
    errores = _errores(stderr)
    if not any(RE_CONTEXTO.search(e) for e in errores):
        return False
    return all(RE_CONTEXTO.search(e) or RE_CASCADA.search(e) or (envuelto and RE_ARTEFACTO_ENVOLTORIO.search(e))
               for e in errores)


def _opciones_y_codigo(bloque: str) -> Tuple[List[str], str]:
    lineas = bloque.split("\n")
    opciones = []
    while lineas and RE_OPCION.match(lineas[0]):
        opciones.append(lineas.pop(0))
    return opciones, "\n".join(lineas)


def _compila(gcc_bin: str, codigo: str, nombre: str) -> Tuple[bool, str]:
    with tempfile.NamedTemporaryFile(suffix=".c", mode="w", encoding="utf-8") as tmp:
        tmp.write(codigo)
        tmp.flush()
        res = subprocess.run([gcc_bin, "-fsyntax-only", tmp.name], capture_output=True, text=True)
    return res.returncode == 0, res.stderr.replace(tmp.name, nombre).strip()


def extraer_y_validar_snippets_c(contenido_md: str) -> List[Dict[str, Any]]:
    """Extrae los bloques C y verifica que compilen con `gcc -fsyntax-only`."""
    gcc_bin = shutil.which("gcc")
    resultados: List[Dict[str, Any]] = []
    for idx, bloque in enumerate(RE_BLOQUE.findall(contenido_md), 1):
        opciones, codigo = _opciones_y_codigo(bloque)
        if any(RE_FRAGMENTO.match(o) for o in opciones):
            resultados.append({"bloque": idx, "valido": True, "detalle": "Fragmento (:class: fragmento): no se compila"})
            continue
        if not gcc_bin:
            resultados.append({"bloque": idx, "valido": True, "detalle": "GCC no disponible"})
            continue

        nombre = f"bloque{idx}.c"
        valido, error = _compila(gcc_bin, PROLOGO + codigo + "\n", nombre)
        detalle = "Sintaxis C válida"
        if not valido:
            # Sentencias sueltas: válidas dentro de una función.
            en_funcion, error_en_funcion = _compila(
                gcc_bin, PROLOGO.replace("#line 1\n", "") + "void _fragmento(void)\n{\n#line 1\n" + codigo + "\n}\n",
                nombre)
            if en_funcion:
                valido, detalle = True, "Sintaxis C válida (fragmento dentro de una función)"
            elif _solo_contexto(error) or _solo_contexto(error_en_funcion, envuelto=True):
                valido, detalle = True, "Sintaxis C válida (usa nombres declarados en otra parte del texto)"
            else:
                # El error más útil es el de la forma con menos errores (en un fragmento de sentencias,
                # la de «dentro de una función»; en un archivo completo, la original).
                detalle = min((error, error_en_funcion), key=lambda e: len(_errores(e)))
        resultados.append({"bloque": idx, "valido": valido, "detalle": detalle})

    return resultados
