# MyST Tools

Herramientas unificadas para automatizar y gestionar el material didáctico escrito en formato MyST Markdown para la cátedra de Programación II.

Este proyecto está gestionado con [uv](https://github.com/astral-sh/uv).

> [!IMPORTANT]
> **Requisito de ejecución:** Las herramientas del CLI deben ser ejecutadas desde un directorio que contenga el archivo de configuración `mystm.yml` (es decir, la raíz del proyecto de documentación MyST). Si el archivo no está presente, el comando fallará con un error.


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

## Desarrollo

Si querés modificar las herramientas o agregar nuevas funcionalidades, podés ejecutar el CLI en modo desarrollo:

```bash
uv run myst-tools --help
```

El backend de construcción utilizado es `hatchling`.

