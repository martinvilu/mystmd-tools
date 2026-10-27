"""Verificador de referencias, enlaces cruzados y anclas hacia el catálogo oficial de reglas (0xXXXXh) y satélites."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Catálogo oficial de reglas canónicas v2.0 (codigo -> directorio de familia en apunte/reglas)
REGLAS_OFICIALES: Dict[str, str] = {'0x0001h': '00_formato', '0x0002h': '00_formato', '0x0003h': '00_formato', '0x0004h': '00_formato', '0x0005h': '00_formato', '0x0006h': '00_formato', '0x0007h': '00_formato', '0x0008h': '00_formato', '0x0009h': '00_formato', '0x000Ah': '00_formato', '0x000Bh': '00_formato', '0x000Ch': '00_formato', '0x000Dh': '00_formato', '0x000Eh': '00_formato', '0x000Fh': '00_formato', '0x0010h': '00_formato', '0x0011h': '00_formato', '0x0012h': '00_formato', '0x0013h': '00_formato', '0x0014h': '00_formato', '0x0015h': '00_formato', '0x0016h': '00_formato', '0x0017h': '00_formato', '0x0101h': '01_nomenclatura', '0x0102h': '01_nomenclatura', '0x0103h': '01_nomenclatura', '0x0104h': '01_nomenclatura', '0x0105h': '01_nomenclatura', '0x0106h': '01_nomenclatura', '0x0107h': '01_nomenclatura', '0x0108h': '01_nomenclatura', '0x0109h': '01_nomenclatura', '0x010Ah': '01_nomenclatura', '0x010Bh': '01_nomenclatura', '0x010Ch': '01_nomenclatura', '0x010Dh': '01_nomenclatura', '0x010Eh': '01_nomenclatura', '0x010Fh': '01_nomenclatura', '0x0110h': '01_nomenclatura', '0x0111h': '01_nomenclatura', '0x0112h': '01_nomenclatura', '0x0201h': '02_documentacion', '0x0202h': '02_documentacion', '0x0203h': '02_documentacion', '0x0204h': '02_documentacion', '0x0205h': '02_documentacion', '0x0206h': '02_documentacion', '0x1001h': '10_control', '0x1002h': '10_control', '0x1003h': '10_control', '0x1004h': '10_control', '0x1005h': '10_control', '0x1006h': '10_control', '0x1007h': '10_control', '0x1008h': '10_control', '0x1009h': '10_control', '0x100Ah': '10_control', '0x100Bh': '10_control', '0x100Ch': '10_control', '0x100Dh': '10_control', '0x100Eh': '10_control', '0x100Fh': '10_control', '0x1010h': '10_control', '0x1011h': '10_control', '0x1012h': '10_control', '0x1013h': '10_control', '0x1014h': '10_control', '0x1015h': '10_control', '0x1016h': '10_control', '0x1017h': '10_control', '0x1018h': '10_control', '0x2001h': '20_funciones', '0x2002h': '20_funciones', '0x2003h': '20_funciones', '0x2004h': '20_funciones', '0x2005h': '20_funciones', '0x2006h': '20_funciones', '0x2007h': '20_funciones', '0x2008h': '20_funciones', '0x2009h': '20_funciones', '0x200Ah': '20_funciones', '0x200Bh': '20_funciones', '0x200Ch': '20_funciones', '0x200Dh': '20_funciones', '0x200Eh': '20_funciones', '0x200Fh': '20_funciones', '0x2010h': '20_funciones', '0x2011h': '20_funciones', '0x2012h': '20_funciones', '0x2013h': '20_funciones', '0x2014h': '20_funciones', '0x2015h': '20_funciones', '0x2016h': '20_funciones', '0x2017h': '20_funciones', '0x2018h': '20_funciones', '0x3001h': '30_memoria', '0x3002h': '30_memoria', '0x3003h': '30_memoria', '0x3004h': '30_memoria', '0x3005h': '30_memoria', '0x3006h': '30_memoria', '0x3007h': '30_memoria', '0x3008h': '30_memoria', '0x3009h': '30_memoria', '0x300Ah': '30_memoria', '0x300Bh': '30_memoria', '0x300Ch': '30_memoria', '0x300Dh': '30_memoria', '0x300Eh': '30_memoria', '0x300Fh': '30_memoria', '0x3010h': '30_memoria', '0x3011h': '30_memoria', '0x3012h': '30_memoria', '0x3013h': '30_memoria', '0x3014h': '30_memoria', '0x3015h': '30_memoria', '0x3016h': '30_memoria', '0x3017h': '30_memoria', '0x3018h': '30_memoria', '0x3019h': '30_memoria', '0x301Ah': '30_memoria', '0x301Bh': '30_memoria', '0x301Ch': '30_memoria', '0x301Dh': '30_memoria', '0x301Eh': '30_memoria', '0x301Fh': '30_memoria', '0x3020h': '30_memoria', '0x4001h': '40_archivos', '0x4002h': '40_archivos', '0x4003h': '40_archivos', '0x4004h': '40_archivos', '0x4005h': '40_archivos', '0x4006h': '40_archivos', '0x4007h': '40_archivos', '0x4008h': '40_archivos', '0x4009h': '40_archivos', '0x400Ah': '40_archivos', '0x400Bh': '40_archivos', '0x400Ch': '40_archivos', '0x5001h': '50_seguridad', '0x5002h': '50_seguridad', '0x5003h': '50_seguridad', '0x5004h': '50_seguridad', '0x5005h': '50_seguridad', '0x5006h': '50_seguridad', '0x5007h': '50_seguridad', '0x5008h': '50_seguridad', '0x5009h': '50_seguridad', '0x500Ah': '50_seguridad', '0x500Bh': '50_seguridad', '0x500Ch': '50_seguridad', '0x500Dh': '50_seguridad', '0x500Eh': '50_seguridad', '0x500Fh': '50_seguridad', '0x5010h': '50_seguridad', '0x5011h': '50_seguridad', '0x5012h': '50_seguridad', '0x5013h': '50_seguridad', '0x5014h': '50_seguridad', '0x5015h': '50_seguridad', '0x6001h': '60_proceso', '0x6002h': '60_proceso', '0x6003h': '60_proceso', '0x6004h': '60_proceso', '0x6005h': '60_proceso', '0x7001h': '70_robustez', '0x7002h': '70_robustez', '0x7003h': '70_robustez', '0x7004h': '70_robustez', '0x7005h': '70_robustez', '0x7006h': '70_robustez', '0x7007h': '70_robustez', '0x8001h': '80_verificacion', '0x8002h': '80_verificacion', '0x8003h': '80_verificacion', '0x8004h': '80_verificacion'}

# Códigos v1.0 deprecados que cambiaron de código en la renumeración oficial v2.0
REGLAS_RENUMERADAS: Dict[str, str] = {'0x0000h': '0x0001h', '0x0018h': '0x010Ah', '0x0019h': '0x000Ah', '0x001Ah': '0x000Bh', '0x001Bh': '0x000Ch', '0x001Ch': '0x000Dh', '0x001Dh': '0x000Eh', '0x001Eh': '0x000Fh', '0x001Fh': '0x0010h', '0x0020h': '0x010Bh', '0x0022h': '0x0011h', '0x0023h': '0x301Ch', '0x0025h': '0x0012h', '0x0026h': '0x010Ch', '0x0027h': '0x0206h', '0x0028h': '0x0013h', '0x0029h': '0x0014h', '0x002Bh': '0x0015h', '0x002Ch': '0x010Dh', '0x002Dh': '0x0016h', '0x0035h': '0x301Dh', '0x0036h': '0x301Eh', '0x0037h': '0x010Eh', '0x0038h': '0x010Fh', '0x5016h': '0x5014h', '0x6006h': '0x6004h', '0x6007h': '0x2015h', '0x6008h': '0x2016h', '0x6009h': '0x0110h', '0x600Ah': '0x0111h', '0x600Bh': '0x0112h', '0x600Ch': '0x1016h', '0x600Dh': '0x1017h', '0x600Eh': '0x0017h', '0x600Fh': '0x6005h', '0x6010h': '0x7002h', '0x6011h': '0x7003h', '0x6012h': '0x7004h', '0x6013h': '0x7005h', '0x6014h': '0x7006h', '0x6015h': '0x7007h', '0x6016h': '0x8002h', '0x6017h': '0x8003h', '0x6018h': '0x8004h'}

# Satélites y herramientas oficiales del ecosistema (ripley SATELLITE_CATALOG + ecosistema.toml)
SATELITES_OFICIALES: Set[str] = {
    "alucard", "apone", "ash", "bishop", "bitmaps", "brett", "bryant", "burke",
    "callahan", "corbel", "crowe", "daedalus", "dallas", "deckard", "dietrich",
    "drake", "dredd", "ferro", "gaff", "giger", "gorman", "hal", "hardboiled",
    "hicks", "holden", "hudson", "idkfa", "jonesy", "kane", "kaneda", "lambert",
    "leon", "meet-tools", "moodle-toolbox", "mother", "motoko", "myst-tools",
    "mystmd-tools", "newt", "nostromo", "p1-tools", "parker", "priss", "rachael",
    "rachel", "ripley", "roy", "scorm-tools", "sebastian", "slide-tools",
    "sonido", "spunkmeyer", "tetsuo", "treadstone", "tyrell", "tyrone",
    "vasquez", "vassili", "voight", "weyl", "wierzbowski", "yutani", "zhora",
    # Claves de etapa en SATELLITE_CATALOG de ripley
    "abi_audit", "antipatterns", "binary_io", "callgraph", "compiler",
    "dataset_generator", "documentation", "fault_injection", "formal_contracts",
    "fuzzing", "hardware_profiler", "headers_audit", "macro_security",
    "mcdc_coverage", "mocks", "mutation_testing", "padding", "portability",
    "sandbox", "sanitizer_translator", "security", "semantic_diff", "style",
    "tda_encapsulation",
    # Repositorios de contenido de cátedra
    "apunte", "p1-apunte", "ejercicios", "p1-ejemplos", "plantilla-tp",
}

SATELITES_RETIRADOS: Dict[str, str] = {
    "esper": "daedalus (N-ESPER-01)",
}

FAMILIAS_REGLAS: Set[str] = set(REGLAS_OFICIALES.values())

RE_CODIGO_HEX = re.compile(r"(?<![A-Za-z0-9_])(0x[0-9a-fA-F]{4}h)(?![A-Za-z0-9_])")
RE_ENLACE_MD = re.compile(r'(?<!!)\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
RE_REF_MYST = re.compile(r"\{ref\}`([^`]+)`")
RE_REF_MALFORMADO = re.compile(r"`?\{ref\}\s*(0x[0-9a-fA-F]{4}h)`?")
RE_GITHUB_REPO = re.compile(
    r"https?://github\.com/(?:INGCOM-UNRN-P1|INGCOM-UNRN|unsam)/([A-Za-z0-9_.-]+)"
)
RE_SATELITE_REF = re.compile(
    r"(?:\{ref\}`satelite-([A-Za-z0-9_-]+)`|\bsat[eé]lite\s+`([A-Za-z0-9_-]+)`)",
    re.IGNORECASE,
)


@dataclass
class HallazgoCatalogo:
    linea: int
    regla: str
    severidad: str  # "error" o "aviso"
    referencia: str
    mensaje: str
    sugerencia: str = ""

    def to_dict(self, archivo: str = "") -> dict:
        d = {
            "archivo": archivo,
            "linea": self.linea,
            "regla": self.regla,
            "severidad": self.severidad,
            "referencia": self.referencia,
            "mensaje": self.mensaje,
        }
        if self.sugerencia:
            d["sugerencia"] = self.sugerencia
        return d


def cargar_catalogo_oficial() -> Tuple[Dict[str, str], Dict[str, str], Set[str]]:
    """Devuelve (reglas_oficiales, reglas_renumeradas, satelites_oficiales) sincronizados con gaff y ripley."""
    reglas = dict(REGLAS_OFICIALES)
    renum = dict(REGLAS_RENUMERADAS)
    satelites = set(SATELITES_OFICIALES)
    try:
        from gaff.core.rules import CATALOGO_REGLAS, MAPA_RENUMERACION  # type: ignore[import-not-found]
        for k, info in CATALOGO_REGLAS.items():
            if k.startswith("0x") and info.get("codigo") == k:
                reglas[k] = info.get("directorio", reglas.get(k, "00_formato"))
        for k, v in MAPA_RENUMERACION.items():
            if k not in reglas:
                renum[k] = v
    except Exception:
        pass
    try:
        from ripley.core.entrypoints_catalogo import SATELLITE_CATALOG  # type: ignore[import-not-found]
        for clave, info in SATELLITE_CATALOG.items():
            satelites.add(clave.lower())
            if "tool" in info:
                satelites.add(str(info["tool"]).lower())
    except Exception:
        pass
    return reglas, renum, satelites


def _canonizar_codigo(raw: str) -> str:
    return f"0x{raw[2:-1].upper()}h"


def _revisar_enlaces_y_anclas_regla(
    linea: str,
    numero: int,
    archivo: Optional[Path],
    reglas_oficiales: Dict[str, str],
    hallazgos: List[HallazgoCatalogo],
) -> None:
    for m_mal in RE_REF_MALFORMADO.finditer(linea):
        cod = _canonizar_codigo(m_mal.group(1))
        hallazgos.append(
            HallazgoCatalogo(
                numero, "ancla-myst-malformada", "error", m_mal.group(0),
                f"Rol MyST malformado «{m_mal.group(0)}» hacia la regla {cod}.",
                f"Usar {{ref}}`{cod}`",
            )
        )

    for m_ref in RE_REF_MYST.finditer(linea):
        interior = m_ref.group(1).strip()
        destino_ref = interior.split("<")[-1].rstrip(">").strip() if "<" in interior else interior
        if destino_ref.lower().startswith("regla-0x") and destino_ref.lower().endswith("h"):
            cod_extraido = _canonizar_codigo(destino_ref[6:])
            hallazgos.append(
                HallazgoCatalogo(
                    numero, "ancla-regla-prefijo", "error", destino_ref,
                    f"El ancla «{destino_ref}» usa el prefijo regla-; las páginas del apunte definen el ancla canónica «({cod_extraido})=».",
                    f"Usar {{ref}}`{cod_extraido}`",
                )
            )

    for m_link in RE_ENLACE_MD.finditer(linea):
        destino = m_link.group(2).strip()
        if destino.startswith(("http://", "https://", "mailto:")):
            continue
        ruta_parte, _, ancla_parte = destino.partition("#")
        m_regla_md = re.search(r"(?:^|/)(0x[0-9a-fA-F]{4}h)\.md$", ruta_parte)
        if not m_regla_md:
            continue
        cod = _canonizar_codigo(m_regla_md.group(1))
        familia = reglas_oficiales.get(cod)
        if not familia:
            continue
        partes_ruta = [p for p in Path(ruta_parte).parts if p not in (".", "..")]
        familias_en_ruta = [p for p in partes_ruta if p in FAMILIAS_REGLAS]
        if familias_en_ruta and familias_en_ruta[-1] != familia:
            hallazgos.append(
                HallazgoCatalogo(
                    numero, "enlace-regla-familia-incorrecta", "error", destino,
                    f"El enlace «{destino}» ubica a {cod} en «{familias_en_ruta[-1]}», pero en el catálogo oficial pertenece a «{familia}».",
                    f"Usar {familia}/{cod}.md",
                )
            )
        elif not familias_en_ruta:
            en_misma_familia = archivo is not None and archivo.parent.name == familia
            existe_local = archivo is not None and (archivo.parent / ruta_parte).is_file()
            if not en_misma_familia and not existe_local:
                hallazgos.append(
                    HallazgoCatalogo(
                        numero, "enlace-regla-roto", "error", destino,
                        f"El enlace «{destino}» a la regla {cod} omite el directorio de su familia («{familia}») y no resuelve al archivo destino.",
                        f"Usar {familia}/{cod}.md",
                    )
                )
        elif archivo is not None and not (archivo.parent / ruta_parte).is_file():
            hallazgos.append(
                HallazgoCatalogo(
                    numero, "enlace-regla-roto", "error", destino,
                    f"El archivo destino «{ruta_parte}» para la regla {cod} no existe.",
                    f"Verificar la ruta hacia reglas/{familia}/{cod}.md",
                )
            )
        if ancla_parte:
            ancla_limpia = ancla_parte[6:] if ancla_parte.lower().startswith("regla-") else ancla_parte
            if re.fullmatch(r"0x[0-9a-fA-F]{4}h", ancla_limpia) and _canonizar_codigo(ancla_limpia) != cod:
                hallazgos.append(
                    HallazgoCatalogo(
                        numero, "ancla-regla-inconsistente", "error", destino,
                        f"El ancla «#{ancla_parte}» no coincide con el archivo de la regla {cod}.",
                        f"Usar #{cod}",
                    )
                )


def _revisar_codigos_y_satelites(
    linea: str,
    numero: int,
    reglas_oficiales: Dict[str, str],
    reglas_renumeradas: Dict[str, str],
    satelites_oficiales: Set[str],
    hallazgos: List[HallazgoCatalogo],
) -> None:
    for m_cod in RE_CODIGO_HEX.finditer(linea):
        raw = m_cod.group(1)
        canon = _canonizar_codigo(raw)
        if raw != canon:
            hallazgos.append(
                HallazgoCatalogo(
                    numero, "regla-formato", "error", raw,
                    f"El código «{raw}» debe escribirse con dígitos hexadecimales en mayúsculas («{canon}»).",
                    f"Reemplazar por {canon}",
                )
            )
        if canon not in reglas_oficiales:
            if canon in reglas_renumeradas:
                nuevo = reglas_renumeradas[canon]
                hallazgos.append(
                    HallazgoCatalogo(
                        numero, "regla-renumerada", "error", raw,
                        f"El código «{canon}» corresponde a la numeración v1.0 deprecada; en el catálogo oficial v2.0 fue renumerado a «{nuevo}».",
                        f"Reemplazar por {nuevo}",
                    )
                )
            else:
                hallazgos.append(
                    HallazgoCatalogo(
                        numero, "regla-inexistente", "error", raw,
                        f"El código de regla «{canon}» no existe en el catálogo oficial de gaff/ripley.",
                        "Consultar `gaff rules` para ver los códigos vigentes",
                    )
                )

    candidatos_satelite: List[str] = []
    for m_gh in RE_GITHUB_REPO.finditer(linea):
        candidatos_satelite.append(m_gh.group(1).removesuffix(".git").rstrip(".,;:)"))
    for m_sat in RE_SATELITE_REF.finditer(linea):
        sat = (m_sat.group(1) or m_sat.group(2) or "").strip()
        if sat:
            candidatos_satelite.append(sat)

    for sat in candidatos_satelite:
        sat_low = sat.lower()
        if sat_low in SATELITES_RETIRADOS:
            reemplazo = SATELITES_RETIRADOS[sat_low]
            hallazgos.append(
                HallazgoCatalogo(
                    numero, "satelite-retirado", "error", sat,
                    f"El satélite «{sat}» fue retirado del ecosistema y reemplazado por {reemplazo}.",
                    f"Actualizar la referencia a {reemplazo.split()[0]}",
                )
            )
        elif sat_low not in satelites_oficiales:
            hallazgos.append(
                HallazgoCatalogo(
                    numero, "satelite-inexistente", "error", sat,
                    f"El satélite o repositorio «{sat}» no pertenece al catálogo oficial del ecosistema (ripley).",
                    "Verificar el nombre en el catálogo de satélites de ripley",
                )
            )


def auditar_enlaces_catalogo(
    contenido: str,
    archivo: Optional[Path] = None,
) -> List[HallazgoCatalogo]:
    """Valida que toda referencia, ancla o enlace a reglas 0xXXXXh y satélites coincida con el catálogo oficial."""
    reglas_oficiales, reglas_renumeradas, satelites_oficiales = cargar_catalogo_oficial()
    hallazgos: List[HallazgoCatalogo] = []
    lineas = contenido.splitlines()

    inicio = 0
    if lineas and lineas[0].strip() == "---":
        for idx in range(1, len(lineas)):
            if lineas[idx].strip() == "---":
                inicio = idx + 1
                break

    for i in range(inicio, len(lineas)):
        linea = lineas[i]
        numero = i + 1
        _revisar_enlaces_y_anclas_regla(linea, numero, archivo, reglas_oficiales, hallazgos)
        _revisar_codigos_y_satelites(
            linea, numero, reglas_oficiales, reglas_renumeradas, satelites_oficiales, hallazgos
        )

    return hallazgos
