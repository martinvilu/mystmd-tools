# MyST Tools — AI & LLM Integration Guide

Este archivo contiene la especificación técnica del CLI de `myst-tools` diseñada especialmente para que modelos de lenguaje (LLMs), agentes autónomos y skills puedan comprender y operar la herramienta sin ambigüedades.

---

## 1. Información General y Ejecución
* **Nombre de la Herramienta**: `myst-tools`
* **Entry-point principal**: `myst-tools` (si está instalada globalmente) o `uv run myst-tools` (en el contexto del entorno virtual del proyecto).
* **Dependencia crítica**: Por defecto, requiere la presencia de un archivo `myst.yml` en el directorio de ejecución para validar que se está operando dentro del apunte MyST.
* **Bypass de validación**: Podés usar la opción global `-f` o `--force` (antes del subcomando) para forzar la ejecución en directorios que no contengan `myst.yml`.

### Estructura de Invocación
```bash
myst-tools [OPCIONES_GLOBALES] <SUBCOMANDO> [ARGUMENTOS]
```

---

## 2. Opciones Globales
* **`-h, --help`**: Muestra la ayuda del CLI principal y lista los subcomandos disponibles. *No requiere la existencia de `myst.yml`.*
* **`-f, --force`**: Omite el chequeo obligatorio de `myst.yml`.

---

## 3. Subcomandos Disponibles

### A. `fmt`
Formatea archivos MyST Markdown siguiendo convenciones de estilo estables.
* **Propósito**: Limitar ancho de línea a 80 caracteres para prosa, resolver colisiones de anidamiento de guardas (fences) y anotar los cierres con comentarios HTML explicativos. No altera bloques de código.
* **Argumentos posicionales**:
  * `files` (nargs="*"): Archivos o directorios a formatear. Si se indica un directorio, se formatearán todos los `.md` internos recursivamente (ignorando ocultos y entornos virtuales).
* **Modo Pipeline/Stdin**: Si no se especifican archivos y la entrada estándar no es interactiva (TTY), lee de stdin y devuelve el formateado a stdout. También podés pasar `-` como argumento.
* **Opciones**:
  * `--check`: Solo comprueba si el archivo necesita cambios. Retorna código de salida `1` si hay diferencias, o `0` si está correcto.
  * `--stdout`: Retorna el resultado a la salida estándar en lugar de modificar in-place.
  * `--width N`: Especifica un límite de ancho de línea custom (default: 80).

### B. `fix-anchors`
Detecta y soluciona anclas de referencia duplicadas.
* **Propósito**: Resuelve colisiones de anclas `(etiqueta)=` en archivos `.md` renombrándolas con prefijos únicos derivados del nombre del archivo y actualiza todas las referencias locales/externas (`{ref}`, `{numref}`) de forma automática.
* **Argumentos posicionales**:
  * `dir` (opcional): Directorio a escanear (default: `.`).
* **Opciones**:
  * `--dry-run`: Muestra la planificación de renombrado en consola sin escribir ningún cambio físico.
  * `--report`: Identifica y lista los duplicados y finaliza la ejecución con salida informativa sin realizar correcciones.

### C. `add-anchors`
* **Propósito**: Analiza los encabezados (`#`, `##`, `###`) de los archivos `.md` en el apunte y añade etiquetas de anclas estables `(slugify-titulo)=` inmediatamente antes de cada uno si no existen.
* **Argumentos posicionales**:
  * `dir` (opcional): Directorio del apunte (default: `./apunte`).

### D. `gen-apunte`
* **Propósito**: Genera un archivo de índice detallado (`indice.md`) en el directorio especificado agrupando por archivo markdown y listando enlaces internos relativos de niveles 1, 2 y 3.
* **Argumentos posicionales**:
  * `dir` (opcional): Directorio del apunte (default: `./apunte`).

### E. `gen-guides`
* **Propósito**: Genera un archivo de índice de trabajos prácticos (`indice.md`) a partir del título definido en el frontmatter o el encabezado principal de cada archivo de guías de trabajos prácticos.
* **Argumentos posicionales**:
  * `dir` (opcional): Directorio de guías (default: `./guias`).

### F. `gen-rules`
* **Propósito**: Recopila todas las anclas que siguen el patrón `(regla-xxx)=` en el directorio de reglas y genera un archivo de índice unificado (`indice.md`) para las reglas de estilo de programación.
* **Argumentos posicionales**:
  * `dir` (opcional): Directorio de reglas (default: `./reglas`).

---

## 4. Códigos de Retorno (Exit Codes)
* **`0`**: Ejecución exitosa sin errores y sin advertencias pendientes.
* **`1`**: Advertencias en resolución de anclas ambiguas (en `fix-anchors`) o archivos que requieren cambios de formato (en `fmt --check`).
* **`2` / otros**: Excepciones de entrada/salida, errores de sintaxis en argumentos o archivo ausente.

---

## 5. Instrucciones de Operación para Agentes y LLMs
1. **Validación Previa**: Antes de lanzar comandos que modifican archivos (como `fmt` o `add-anchors`), es recomendable simular los cambios o verificar el estado actual. Usá `fmt --check` o `fix-anchors --dry-run` para predecir colisiones o necesidades de formato.
2. **Entorno de Trabajo**: Asegurate de estar en la raíz de la documentación MyST para evitar el fallo por falta de `myst.yml`, o utilizá siempre el flag `-f` / `--force` si sabés que el entorno de ejecución carece de dicho archivo de configuración pero el directorio contiene material markdown válido.
3. **Pipes y Stdin**: Al procesar fragmentos aislados de Markdown provistos por el usuario, podés canalizarlos directamente mediante stdin usando `myst-tools -f fmt -` para recibir la prosa formateada de forma inmediata y segura sin tocar archivos en disco.
