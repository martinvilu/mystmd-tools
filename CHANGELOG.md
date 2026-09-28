# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/);
versiones según [SemVer](https://semver.org/lang/es/).

## [0.3.0] - 2026-09-28

Primera versión con registro de cambios; lo anterior está en el historial de git.

### Agregado

- **cli**: cumplir el contrato de línea de comandos de LINEAMIENTOS §3.2 (N-ECO-04) (`f919a0f`)

### Corregido

- **cli**: recorrer los directorios recibidos y fallar si no hay archivos Markdown (N-MYST-01) (`096b108`)

### Documentación

- agregar el texto de la licencia GPL-3.0-or-later que declara pyproject (N-ECO-06) (`976bb42`)
- incorporar manual de uso integral y referencia tecnica (myst-tools) (`a55f7db`)

### Mantenimiento

- **calidad**: verificar errores de Python y dependencias vulnerables (N-ECO-08, N-ECO-13) (`319329a`)
- **deps**: mover las dependencias de desarrollo a dependency-groups (N-ECO-07) (`b28fd15`)
