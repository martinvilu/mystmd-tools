# Manual de Uso y Referencia Técnica: myst-tools

> **MYST-TOOLS** — Herramientas unificadas para automatizar, formatear e indexar material didáctico MyST Markdown
> **Versión:** `0.2.0` · **CLI principal:** `myst-tools` · **Plugin Ripley:** `myst-tools`

---

## 1. Arquitectura y Propósito Pedagógico

`myst-tools` forma parte del ecosistema de herramientas de la cátedra de Programación 1 (UNRN). Su objetivo central es resolver de forma modular, determinista y automatizada las tareas asociadas a su dominio específico dentro del ciclo de desarrollo, evaluación y aprendizaje de software en C.

### Alcance Funcional (Qué cubre)
- Herramientas de soporte, auditoría y mantenimiento para apuntes y material didáctico en formato MyST Markdown.
- Verificación ortográfica y gramatical contextualizada mediante LanguageTool, con diccionario técnico de programación.
- Detección y resolución de colisiones en anclas y etiquetas cruzadas.
- Generación automatizada de índices temáticos y verificación de consistencia de enlaces.

### Límites de Responsabilidad y Delegación (Qué no cubre)
- Formateo de código fuente en C (delegado a `gaff`).
- Ejecución de suites de prueba de ejercicios (delegado a `nostromo`).
- Generación de exámenes institucionales Typst/OMR (delegado a `alucard`).

### Principios de Diseño
- **Enfoque Pedagógico:** Diagnósticos y mensajes en español rioplatense orientados a facilitar la comprensión de errores conceptuales.
- **Salida Estructurada Dual:** Soporte nativo para visualización enriquecida en terminal (Rich) y salida parseable para orquestadores (`--json`).
- **Integración Contractual:** Capacidad de emitir secciones de reporte para `dredd` (`dredd-section`) y actuar como satélite orquestado por `ripley`.
- **Idempotencia y Robustez:** Validación de precondiciones y comandos de autodiagnóstico (`doctor`) para verificación del entorno.

---

## 2. Instalación y Requisitos

### Requisitos del Sistema
- **Python:** `>= 3.10` (recomendado Python 3.11 o 3.12).
- **Gestor de paquetes:** [`uv`](https://github.com/astral-sh/uv) (entorno estándar de cátedra).
- **Toolchain C (si aplica):** GCC / Clang, Make, GDB y bibliotecas estándar de desarrollo.

### Instalación en el Entorno de Usuario
Para instalar la herramienta de forma global y aislada en el sistema mediante `uv tool`:
```bash
uv tool install --editable /home/mrtin/dev/tools/myst-tools
```

### Verificación de Instalación
Ejecutá el comando `doctor` para constatar que todas las dependencias y binarios requeridos estén presentes y operativos:
```bash
myst-tools doctor
```

---

## 3. Guía Integral de Comandos (CLI)

| Comando | Descripción Breve |
| :--- | :--- |
| [`myst-tools add-anchors`](#addanchors) | Agrega etiquetas/anclas de MyST a los encabezados de archivos Markdown. |
| [`myst-tools gen-apunte`](#genapunte) | Genera el índice detallado para el apunte de cátedra. |
| [`myst-tools gen-guides`](#genguides) | Genera el índice para las guías de trabajos prácticos. |
| [`myst-tools gen-rules`](#genrules) | Genera el índice de las reglas de estilo de programación. |
| [`myst-tools fix-anchors`](#fixanchors) | Detecta y corrige anclas MyST duplicadas. |
| [`myst-tools fmt`](#fmt) | Formatea archivos MyST Markdown (longitud de línea, fences y comentarios). |
| [`myst-tools languagetool`](#languagetool) | Verifica y corrige ortografía y gramática en documentos MyST Markdown usando LanguageTool. |
| [`myst-tools grammar`](#grammar) | Verifica y corrige ortografía y gramática en documentos MyST Markdown usando LanguageTool. |
| [`myst-tools spellcheck`](#spellcheck) | Verifica y corrige ortografía y gramática en documentos MyST Markdown usando LanguageTool. |
| [`myst-tools report`](#report) | Genera directamente la sección de reporte Markdown de LanguageTool para Dredd o documentación. |
| [`myst-tools check-tables`](#checktables) | Audita tablas Markdown en busca de columnas desalineadas o separadores inválidos. |
| [`myst-tools fmt-tables`](#fmttables) | Formatea y alinea visualmente las columnas de tablas Markdown. |
| [`myst-tools check-style`](#checkstyle) | Audita estilo rioplatense (voseo vs tuteo, spanglish). |
| [`myst-tools extract-c-tests`](#extractctests) | Extrae bloques C hacia un proyecto C compilable con Makefile. |
| [`myst-tools extract-dict-terms`](#extractdictterms) | Extrae identificadores técnicos C y directivas para el diccionario personalizado de LanguageTool. |
| [`myst-tools check-links`](#checklinks) | Audita inmutabilidad y sintaxis de enlaces a GitHub. |
| [`myst-tools doctor`](#doctor) | Verifica el estado del entorno de MYST-TOOLS (Python, Node/myst, LanguageTool, Typst). |
| [`myst-tools check-c-snippets`](#checkcsnippets) | Verifica con `gcc -fsyntax-only` que los bloques ```c compilen (requiere gcc). |
| [`myst-tools to-typst`](#totypst) | Convierte encabezados de un MyST Markdown a una plantilla Typst. |
| [`myst-tools extract-exercises`](#extractexercises) | Extrae las directivas {exercise} como candidatos a ejercicios del banco (deckard). |
| [`myst-tools glossary`](#glossary) | Detecta definiciones tipo **Término**: definición y arma un glosario. |
| [`myst-tools callout`](#callout) | Imprime un callout MyST (admonition) con el formato estándar. |

### `myst-tools add-anchors`

Agrega etiquetas/anclas de MyST a los encabezados de archivos Markdown.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--dir-path` | `Path` | `apunte` | Directorio que contiene los archivos Markdown del apunte. |
| `--force`, `-f` | `bool` | `False` | Fuerza la ejecución ignorando la verificación de 'myst.yml'. |

#### Ejemplo de Invocación
```bash
myst-tools add-anchors
```

### `myst-tools gen-apunte`

Genera el índice detallado para el apunte de cátedra.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--dir-path` | `Path` | `apunte` | Directorio del apunte (apunte). |
| `--force`, `-f` | `bool` | `False` | Fuerza la ejecución ignorando la verificación de 'myst.yml'. |

#### Ejemplo de Invocación
```bash
myst-tools gen-apunte
```

### `myst-tools gen-guides`

Genera el índice para las guías de trabajos prácticos.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--dir-path` | `Path` | `guias` | Directorio que contiene las guías. |
| `--force`, `-f` | `bool` | `False` | Fuerza la ejecución ignorando la verificación de 'myst.yml'. |

#### Ejemplo de Invocación
```bash
myst-tools gen-guides
```

### `myst-tools gen-rules`

Genera el índice de las reglas de estilo de programación.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--dir-path` | `Path` | `reglas` | Directorio que contiene las reglas de estilo. |
| `--force`, `-f` | `bool` | `False` | Fuerza la ejecución ignorando la verificación de 'myst.yml'. |

#### Ejemplo de Invocación
```bash
myst-tools gen-rules
```

### `myst-tools fix-anchors`

Detecta y corrige anclas MyST duplicadas.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--dir-path` | `Path` | `.` | Directorio raíz a escanear. |
| `--dry-run` | `bool` | `False` | Muestra los cambios sin escribir ningún archivo. |
| `--report` | `bool` | `False` | Solo lista los duplicados y termina sin modificar nada. |
| `--force`, `-f` | `bool` | `False` | Fuerza la ejecución ignorando la verificación de 'myst.yml'. |

#### Ejemplo de Invocación
```bash
myst-tools fix-anchors
```

### `myst-tools fmt`

Formatea archivos MyST Markdown (longitud de línea, fences y comentarios).

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--files` | `Optional[List[str]]` | `None` | Archivos o directorios a formatear (por defecto, todos los archivos .md si la entrada es interactiva). |
| `--check` | `bool` | `False` | Solo verifica si los archivos necesitan formato. |
| `--stdout` | `bool` | `False` | Imprime el resultado a la salida estándar en vez de modificar in-place. |
| `--width`, `-w` | `int` | `80` | Ancho máximo de línea (default: 80). |
| `--force`, `-f` | `bool` | `False` | Fuerza la ejecución ignorando la verificación de 'myst.yml'. |

#### Ejemplo de Invocación
```bash
myst-tools fmt
```

### `myst-tools languagetool`

Verifica y corrige ortografía y gramática en documentos MyST Markdown usando LanguageTool.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--paths` | `Optional[List[Path]]` | `None` | Archivos .md o directorios a revisar con LanguageTool (por defecto todo el apunte/guías). |
| `--fix`, `-f` | `bool` | `False` | Aplica automáticamente las sugerencias de corrección ortográfica y gramatical. |
| `--lang`, `-l` | `str` | `es-AR` | Código de idioma para LanguageTool (ej: 'es-AR', 'es', 'en-US'). |
| `--server`, `-s` | `Optional[str]` | `None` | URL del servidor LanguageTool (por defecto http://localhost:8081 y API pública). |
| `--username`, `-u` | `Optional[str]` | `None` | Usuario / correo de LanguageTool Premium. |
| `--api-key`, `-k` | `Optional[str]` | `None` | API Key / Token de LanguageTool Premium. |
| `--premium` | `bool` | `False` | Fuerza el uso de la API LanguageTool Premium (https://api.languagetoolplus.com/v2/check). |
| `--ignore-rules` | `Optional[str]` | `None` | Reglas a ignorar separadas por comas (ej: 'MORFOLOGIK_RULE_ES,UPPERCASE_SENTENCE_START'). |
| `--ignore-words` | `Optional[str]` | `None` | Palabras personalizadas a ignorar separadas por comas. |
| `--json` | `bool` | `False` | Emite salida estructurada en formato JSON. |
| `--md`, `--output-md`, `-o` | `Optional[Path]` | `None` | Genera reporte en formato Markdown para fusión en Dredd o documentación. |
| `--force` | `bool` | `False` | Fuerza la ejecución ignorando la verificación de 'myst.yml'. |

#### Ejemplo de Invocación
```bash
myst-tools languagetool
```

### `myst-tools grammar`

Verifica y corrige ortografía y gramática en documentos MyST Markdown usando LanguageTool.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--paths` | `Optional[List[Path]]` | `None` | Archivos .md o directorios a revisar con LanguageTool (por defecto todo el apunte/guías). |
| `--fix`, `-f` | `bool` | `False` | Aplica automáticamente las sugerencias de corrección ortográfica y gramatical. |
| `--lang`, `-l` | `str` | `es-AR` | Código de idioma para LanguageTool (ej: 'es-AR', 'es', 'en-US'). |
| `--server`, `-s` | `Optional[str]` | `None` | URL del servidor LanguageTool (por defecto http://localhost:8081 y API pública). |
| `--username`, `-u` | `Optional[str]` | `None` | Usuario / correo de LanguageTool Premium. |
| `--api-key`, `-k` | `Optional[str]` | `None` | API Key / Token de LanguageTool Premium. |
| `--premium` | `bool` | `False` | Fuerza el uso de la API LanguageTool Premium (https://api.languagetoolplus.com/v2/check). |
| `--ignore-rules` | `Optional[str]` | `None` | Reglas a ignorar separadas por comas (ej: 'MORFOLOGIK_RULE_ES,UPPERCASE_SENTENCE_START'). |
| `--ignore-words` | `Optional[str]` | `None` | Palabras personalizadas a ignorar separadas por comas. |
| `--json` | `bool` | `False` | Emite salida estructurada en formato JSON. |
| `--md`, `--output-md`, `-o` | `Optional[Path]` | `None` | Genera reporte en formato Markdown para fusión en Dredd o documentación. |
| `--force` | `bool` | `False` | Fuerza la ejecución ignorando la verificación de 'myst.yml'. |

#### Ejemplo de Invocación
```bash
myst-tools grammar
```

### `myst-tools spellcheck`

Verifica y corrige ortografía y gramática en documentos MyST Markdown usando LanguageTool.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--paths` | `Optional[List[Path]]` | `None` | Archivos .md o directorios a revisar con LanguageTool (por defecto todo el apunte/guías). |
| `--fix`, `-f` | `bool` | `False` | Aplica automáticamente las sugerencias de corrección ortográfica y gramatical. |
| `--lang`, `-l` | `str` | `es-AR` | Código de idioma para LanguageTool (ej: 'es-AR', 'es', 'en-US'). |
| `--server`, `-s` | `Optional[str]` | `None` | URL del servidor LanguageTool (por defecto http://localhost:8081 y API pública). |
| `--username`, `-u` | `Optional[str]` | `None` | Usuario / correo de LanguageTool Premium. |
| `--api-key`, `-k` | `Optional[str]` | `None` | API Key / Token de LanguageTool Premium. |
| `--premium` | `bool` | `False` | Fuerza el uso de la API LanguageTool Premium (https://api.languagetoolplus.com/v2/check). |
| `--ignore-rules` | `Optional[str]` | `None` | Reglas a ignorar separadas por comas (ej: 'MORFOLOGIK_RULE_ES,UPPERCASE_SENTENCE_START'). |
| `--ignore-words` | `Optional[str]` | `None` | Palabras personalizadas a ignorar separadas por comas. |
| `--json` | `bool` | `False` | Emite salida estructurada en formato JSON. |
| `--md`, `--output-md`, `-o` | `Optional[Path]` | `None` | Genera reporte en formato Markdown para fusión en Dredd o documentación. |
| `--force` | `bool` | `False` | Fuerza la ejecución ignorando la verificación de 'myst.yml'. |

#### Ejemplo de Invocación
```bash
myst-tools spellcheck
```

### `myst-tools report`

Genera directamente la sección de reporte Markdown de LanguageTool para Dredd o documentación.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--paths` | `Optional[List[Path]]` | `None` | Archivos .md o directorios a auditar. |
| `--output`, `-o` | `Optional[Path]` | `None` | Ruta de destino del archivo Markdown. |
| `--lang`, `-l` | `str` | `es-AR` | Código de idioma para LanguageTool. |
| `--server`, `-s` | `Optional[str]` | `None` | URL del servidor LanguageTool. |
| `--force` | `bool` | `False` | Fuerza la ejecución ignorando 'myst.yml'. |

#### Ejemplo de Invocación
```bash
myst-tools report
```

### `myst-tools check-tables`

Audita tablas Markdown en busca de columnas desalineadas o separadores inválidos.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--files` | `Optional[List[Path]]` | `None` | Archivos Markdown a auditar. |
| `--force`, `-f` | `bool` | `False` | Fuerza la ejecución ignorando myst.yml. |
| `--json` | `bool` | `False` | Emite los hallazgos como JSON versionado. |

#### Ejemplo de Invocación
```bash
myst-tools check-tables
```

### `myst-tools fmt-tables`

Formatea y alinea visualmente las columnas de tablas Markdown.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--files` | `Optional[List[Path]]` | `None` | Archivos Markdown a formatear. |
| `--force`, `-f` | `bool` | `False` | Fuerza la ejecución ignorando myst.yml. |

#### Ejemplo de Invocación
```bash
myst-tools fmt-tables
```

### `myst-tools check-style`

Audita estilo rioplatense (voseo vs tuteo, spanglish).

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--files` | `Optional[List[Path]]` | `None` | Archivos Markdown a auditar en estilo rioplatense. |
| `--force`, `-f` | `bool` | `False` | Fuerza la ejecución ignorando myst.yml. |
| `--json` | `bool` | `False` | Emite los hallazgos como JSON versionado. |

#### Ejemplo de Invocación
```bash
myst-tools check-style
```

### `myst-tools extract-c-tests`

Extrae bloques C hacia un proyecto C compilable con Makefile.

#### Argumentos
| Argumento | Tipo | Descripción |
| :--- | :--- | :--- |
| `file_path` | `Path` | Archivo Markdown del cual extraer ejemplos C. |

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--output-dir`, `-o` | `Path` | `test_c_project` | Directorio destino del proyecto C. |
| `--force`, `-f` | `bool` | `False` | Fuerza la ejecución ignorando myst.yml. |

#### Ejemplo de Invocación
```bash
myst-tools extract-c-tests <file_path>
```

### `myst-tools extract-dict-terms`

Extrae identificadores técnicos C y directivas para el diccionario personalizado de LanguageTool.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--files` | `Optional[List[Path]]` | `None` | Archivos Markdown a procesar. |
| `--output`, `-o` | `Path` | `spelling.txt` | Archivo destino para términos LanguageTool. |
| `--force`, `-f` | `bool` | `False` | Fuerza la ejecución ignorando myst.yml. |

#### Ejemplo de Invocación
```bash
myst-tools extract-dict-terms
```

### `myst-tools check-links`

Audita inmutabilidad y sintaxis de enlaces a GitHub.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--files` | `Optional[List[Path]]` | `None` | Archivos Markdown a auditar. |
| `--force`, `-f` | `bool` | `False` | Fuerza la ejecución ignorando myst.yml. |
| `--json` | `bool` | `False` | Emite los hallazgos como JSON versionado. |

#### Ejemplo de Invocación
```bash
myst-tools check-links
```

### `myst-tools doctor`

Verifica el estado del entorno de MYST-TOOLS (Python, Node/myst, LanguageTool, Typst).

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--json` | `bool` | `False` | Emitir diagnóstico en formato JSON estructurado. |

#### Ejemplo de Invocación
```bash
myst-tools doctor
```

### `myst-tools check-c-snippets`

Verifica con `gcc -fsyntax-only` que los bloques ```c compilen (requiere gcc).

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--files` | `Optional[List[Path]]` | `None` | Archivos Markdown a auditar. |
| `--force`, `-f` | `bool` | `False` | Fuerza la ejecución ignorando myst.yml. |
| `--json` | `bool` | `False` | Emite el resultado como JSON versionado. |

#### Ejemplo de Invocación
```bash
myst-tools check-c-snippets
```

### `myst-tools to-typst`

Convierte encabezados de un MyST Markdown a una plantilla Typst.

#### Argumentos
| Argumento | Tipo | Descripción |
| :--- | :--- | :--- |
| `file_path` | `Path` | Archivo Markdown MyST a convertir. |

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--titulo`, `-t` | `str` | `Apunte de Cátedra` | Título del documento Typst. |
| `--output`, `-o` | `Optional[Path]` | `None` | Archivo .typ de salida (por defecto stdout). |
| `--force`, `-f` | `bool` | `False` | Fuerza la ejecución ignorando myst.yml. |
| `--json` | `bool` | `False` | Emite el resultado como JSON versionado. |

#### Ejemplo de Invocación
```bash
myst-tools to-typst <file_path>
```

### `myst-tools extract-exercises`

Extrae las directivas {exercise} como candidatos a ejercicios del banco (deckard).

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--files` | `Optional[List[Path]]` | `None` | Archivos Markdown con directivas ```{exercise}. |
| `--force`, `-f` | `bool` | `False` | Fuerza la ejecución ignorando myst.yml. |
| `--json` | `bool` | `False` | Emite el resultado como JSON versionado. |

#### Ejemplo de Invocación
```bash
myst-tools extract-exercises
```

### `myst-tools glossary`

Detecta definiciones tipo **Término**: definición y arma un glosario.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--files` | `Optional[List[Path]]` | `None` | Archivos Markdown a procesar. |
| `--force`, `-f` | `bool` | `False` | Fuerza la ejecución ignorando myst.yml. |
| `--json` | `bool` | `False` | Emite el resultado como JSON versionado. |

#### Ejemplo de Invocación
```bash
myst-tools glossary
```

### `myst-tools callout`

Imprime un callout MyST (admonition) con el formato estándar.

#### Argumentos
| Argumento | Tipo | Descripción |
| :--- | :--- | :--- |
| `tipo` | `str` | note, tip, warning, important o danger (otro valor cae en note). |
| `cuerpo` | `str` | Texto del callout. |

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--titulo`, `-t` | `str` | `` | Título del callout. |

#### Ejemplo de Invocación
```bash
myst-tools callout <tipo> <cuerpo>
```

---

## 4. Formatos de Salida e Integración con el Ecosistema

### Modo Interactivo / Terminal (Rich)
Por defecto, la herramienta renderiza paneles, árboles y tablas estilizadas para facilitar la lectura del estudiante y docente en terminales modernas con soporte ANSI.

### Modo Estructurado JSON (`--json`)
Para integración con pipelines de CI/CD, scripts de automatización u orquestadores externos, la opción `--json` emite un documento JSON estricto por la salida estándar (`stdout`), dirigiendo cualquier mensaje de logging a `stderr`:
```bash
myst-tools add-anchors --json
```

### Integración con Dredd (`dredd-section`)
Cuando la herramienta genera reportes de evaluación para entregas de alumnos, produce una sección Markdown estandarizada conforme al contrato de integración de Dredd (v1.0.0):
```markdown
<!-- dredd-section: myst-tools, tool=myst-tools, version=0.2.0, status=ok -->
```
Este encabezado garantiza la agregación determinista de los hallazgos en la rúbrica docente.

### Integración con Ripley
`myst-tools` está registrada en el catálogo de plugins satélites de Ripley (`SATELLITE_CATALOG`). Puede invocarse directamente a través del motor de evaluación de Ripley configurando el análisis en `ripley.toml`.

---

## 5. Diagnóstico y Códigos de Salida

### Códigos de Retorno (`exit code`)
| Código | Significado |
| :---: | :--- |
| `0` | Ejecución exitosa sin hallazgos críticos ni errores de sintaxis. |
| `1` | Hallazgos pedagógicos detectados, infracción de reglas o advertencias activas. |
| `2` | Error de sintaxis en argumentos CLI o archivo fuente no encontrado. |
| `>2` | Error no recuperable del sistema, fallo de memoria o excepción interna. |

### Diagnóstico del Entorno (`doctor`)
Ante comportamientos inesperados, verificá el estado operativo con:
```bash
myst-tools doctor
```
Comprueba la presencia de las dependencias requeridas y la integridad de los componentes del paquete.