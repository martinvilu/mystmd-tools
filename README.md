# MyST Tools

Herramientas unificadas para automatizar y gestionar el material didáctico escrito en formato MyST Markdown para la cátedra de Programación II.

Este proyecto está gestionado con [uv](https://github.com/astral-sh/uv).

> [!IMPORTANT]
> **Requisito de ejecución:** Las herramientas del CLI deben ser ejecutadas desde un directorio que contenga el archivo de configuración `myst.yml` (es decir, la raíz del proyecto de documentación MyST). Si el archivo no está presente, puede ignorarse la restricción usando la opción global `-f/--force`.

---

## 🎯 Alcance

### Qué cubre
- Herramientas de soporte, auditoría y mantenimiento para apuntes y material didáctico en formato MyST Markdown.
- Verificación ortográfica y gramatical contextualizada mediante LanguageTool, con diccionario técnico de programación.
- Detección y resolución de colisiones en anclas y etiquetas cruzadas.
- Generación automatizada de índices temáticos y verificación de consistencia de enlaces.

### Qué no cubre (Límites y Delegación)
- Formateo de código fuente en C (delegado a `gaff`).
- Ejecución de suites de prueba de ejercicios (delegado a `nostromo`).
- Generación de exámenes institucionales Typst/OMR (delegado a `alucard`).

---

## 📋 Requisitos

### Requisitos de Sistema y Entorno
- Multiplataforma. Python >= 3.10.

### Dependencias Externas y Binarios
- Java Runtime Environment (JRE) opcional (para ejecución de servidor local LanguageTool).

### Integración en el Ecosistema
- CLI `myst-tools`.

---

## Instalación

Podés instalar estas herramientas como una herramienta global en tu sistema usando `uv tool`:

```bash
# Desde el directorio raíz del proyecto
uv tool install .
```

Una vez instalada, vas a tener disponible el comando `myst-tools` globalmente en tu terminal.

Si preferís ejecutarlo sin instalarlo globalmente:

```bash
uv run myst-tools [comando] [argumentos]
```

## Uso General

```bash
myst-tools [OPCIONES_GLOBALES] [COMANDO] [ARGUMENTOS]
```

### Opciones Globales:
* **`-f, --force`**: Fuerza la ejecución del comando seleccionado ignorando la verificación de la existencia de `myst.yml` en el directorio actual.

## Comandos Disponibles

El comando unificado `myst-tools` provee los siguientes subcomandos:

### 1. `add-anchors`
Agrega etiquetas/anclas de MyST (`(slug)=`) de manera automática antes de cada encabezado (`#`, `##`, `###`) en los archivos Markdown del apunte. Esto facilita las referencias cruzadas estables.

```bash
myst-tools add-anchors [APUNTE_DIR]
```
* **`APUNTE_DIR`** (opcional): Directorio que contiene los archivos Markdown del apunte. Por defecto es `./apunte`.

### 2. `gen-apunte`
Genera un índice detallado (`indice.md`) agrupado por archivo y con enlaces internos a encabezados de nivel 1, 2 y 3.

```bash
myst-tools gen-apunte [APUNTE_DIR]
```
* **`APUNTE_DIR`** (opcional): Directorio del apunte. Por defecto es `./apunte`.

### 3. `gen-guides`
Genera el índice de guías de trabajos prácticos (`indice.md`) leyendo el título del frontmatter o el primer encabezado `#` de cada guía.

```bash
myst-tools gen-guides [GUIAS_DIR]
```
* **`GUIAS_DIR`** (opcional): Directorio que contiene las guías. Por defecto es `./guias`.

### 4. `gen-rules`
Genera el índice de reglas de estilo de programación (`indice.md`) recopilando todas las referencias de tipo `(regla-xxx)=` y sus respectivos títulos.

```bash
myst-tools gen-rules [REGLAS_DIR]
```
* **`REGLAS_DIR`** (opcional): Directorio que contiene las reglas de estilo. Por defecto es `./reglas`.

### 5. `fix-anchors`
Detecta y corrige anclas MyST duplicadas en los archivos Markdown del proyecto. Renombra las definiciones duplicadas anteponiendo el nombre del archivo y actualiza todas las referencias correspondientes.

```bash
myst-tools fix-anchors [DIR] [OPCIONES]
```
* **`DIR`** (opcional): Directorio raíz a escanear. Por defecto es el directorio actual `.`.
* **Opciones**:
  * `--dry-run`: Muestra los cambios planificados sin modificar ningún archivo.
  * `--report`: Solo lista las anclas duplicadas detectadas y finaliza.

### 6. `fmt`
Formatea archivos MyST Markdown aplicando un límite de 80 caracteres de ancho de línea para la prosa (sin modificar bloques de código) y normalizando el anidamiento y cierre de directivas (guardas).

```bash
myst-tools fmt [ARCHIVOS/DIR...] [OPCIONES]
```
* **`ARCHIVOS/DIR`** (opcional): Archivos o directorios a formatear (acepta múltiples). Si no se especifica y la entrada es interactiva, formatea todos los archivos `.md` del proyecto de forma recursiva. Si la entrada no es interactiva, lee desde la entrada estándar (stdin). Usar `-` para forzar la lectura desde stdin.
* **Opciones**:
  * `--check`: Verifica si los archivos necesitan formato (retorna código 1 si requieren cambios).
  * `--stdout`: Imprime el resultado en la salida estándar en vez de modificar los archivos in-place.
  * `--width N`: Especifica un ancho de línea personalizado (por defecto 80).

### 7. `spellcheck` (alias: `grammar`, `languagetool`)
Audita y corrige ortografía y gramática en documentos MyST Markdown usando LanguageTool, enmascarando inteligentemente directivas MyST, bloques de código C, matemáticas LaTeX y anclas para evitar falsos positivos.

```bash
myst-tools spellcheck [ARCHIVOS/DIR...] [OPCIONES]
```
* **`ARCHIVOS/DIR`** (opcional): Archivos o directorios a analizar.
* **Opciones**:
  * `-f, --fix`: Aplica automáticamente las correcciones sugeridas in-place sobre los archivos.
  * `-l, --lang`: Código de idioma (por defecto `es-AR`; soporta `es`, `en-US`, etc.).
  * `-s, --server`: URL de servidor LanguageTool personalizado (por defecto intenta servidor local `http://localhost:8081` y API pública).
  * `--ignore-words`: Lista de palabras adicionales a ignorar separadas por coma.
  * `--ignore-rules`: Reglas específicas a deshabilitar separadas por coma.
  * `--json`: Salida estructurada JSON.
  * `-o, --md`: Genera reporte en formato Markdown para fusión en Dredd o documentación.

### 8. `report`
Genera un informe integral del estado del proyecto MyST Markdown (anclas huérfanas, tablas, enlaces y directivas).

```bash
myst-tools report [DIRECTORIO] [--md]
```

### 9. `check-tables` y `fmt-tables`
Audita y formatea tablas Markdown para asegurar alineación visual homogénea y sintaxis válida.

```bash
myst-tools check-tables [ARCHIVOS/DIR...]
myst-tools fmt-tables [ARCHIVOS/DIR...]
```

### 10. `check-style`
Verifica directivas MyST, bloques de admonición y normas de estilo pedagógico.

```bash
myst-tools check-style [ARCHIVOS/DIR...]
```

### 11. `extract-c-tests`
Extrae bloques de código C incluidos en el material didáctico para verificación de compilación.

```bash
myst-tools extract-c-tests [ARCHIVOS/DIR...] -o ./pruebas_c
```

### 12. `extract-dict-terms`
Extrae términos técnicos del apunte para alimentar diccionarios ortográficos especializados.

```bash
myst-tools extract-dict-terms [ARCHIVOS/DIR...]
```

### 13. `check-links`
Valida la integridad de enlaces internos y referencias cruzadas entre documentos.

```bash
myst-tools check-links [ARCHIVOS/DIR...]
```

## Desarrollo

Si querés modificar las herramientas o agregar nuevas funcionalidades, podés ejecutar el CLI en modo desarrollo:

```bash
uv run myst-tools --help
```

El backend de construcción utilizado es `hatchling`.
