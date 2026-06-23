# MyST Tools

Herramientas unificadas para automatizar y gestionar el material didáctico escrito en formato MyST Markdown para la cátedra de Programación II.

Este proyecto está gestionado con [uv](https://github.com/astral-sh/uv).

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
* **`APUNTE_DIR`** (opcional): Directorio del apunte. Por defecto es `./apunte_2`.

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

## Desarrollo

Si querés modificar las herramientas o agregar nuevas funcionalidades, podés ejecutar el CLI en modo desarrollo:

```bash
uv run myst-tools --help
```

El backend de construcción utilizado es `hatchling`.
