import argparse
import sys
from myst_tools.add_myst_anchors import run_add_anchors
from myst_tools.generate_apunte_index import run_generate_apunte_index
from myst_tools.generate_guides_index import run_generate_guides_index
from myst_tools.generate_rules_index import run_generate_rules_index
from myst_tools.fix_dup_anchors import run_fix_dup_anchors
from myst_tools.myst_fmt import run_myst_fmt

def main() -> None:
    import os
    # El archivo de configuración de MyST es 'myst.yml'. Corregimos el mensaje de error para que sea consistente con la búsqueda.
    if not os.path.exists("myst.yml"):
        print("Error: El directorio actual no contiene un archivo 'myst.yml'. Este comando debe ejecutarse desde la raíz del proyecto MyST.", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Herramientas unificadas para automatizar material didáctico MyST.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar", required=True)
    
    # Subcomando: add-anchors
    parser_anchors = subparsers.add_parser(
        "add-anchors", 
        help="Agrega etiquetas/anclas de MyST a los encabezados de archivos Markdown."
    )
    parser_anchors.add_argument(
        "dir", 
        nargs="?", 
        default="./apunte", 
        help="Directorio que contiene los archivos Markdown del apunte."
    )
    
    # Subcomando: gen-apunte
    parser_apunte = subparsers.add_parser(
        "gen-apunte", 
        help="Genera el índice detallado para el apunte de cátedra."
    )
    parser_apunte.add_argument(
        "dir", 
        nargs="?", 
        default="./apunte", 
        help="Directorio del apunte (apunte)."
    )
    
    # Subcomando: gen-guides
    parser_guides = subparsers.add_parser(
        "gen-guides", 
        help="Genera el índice para las guías de trabajos prácticos."
    )
    parser_guides.add_argument(
        "dir", 
        nargs="?", 
        default="./guias", 
        help="Directorio que contiene las guías."
    )
    
    # Subcomando: gen-rules
    parser_rules = subparsers.add_parser(
        "gen-rules", 
        help="Genera el índice de las reglas de estilo de programación."
    )
    parser_rules.add_argument(
        "dir", 
        nargs="?", 
        default="./reglas", 
        help="Directorio que contiene las reglas de estilo."
    )

    # Subcomando: fix-anchors
    parser_fix = subparsers.add_parser(
        "fix-anchors", 
        help="Detecta y corrige anclas MyST duplicadas."
    )
    parser_fix.add_argument(
        "dir", 
        nargs="?", 
        default=".", 
        help="Directorio raíz a escanear."
    )
    parser_fix.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Muestra los cambios sin escribir ningún archivo."
    )
    parser_fix.add_argument(
        "--report", 
        action="store_true", 
        help="Solo lista los duplicados y termina sin modificar nada."
    )

    # Subcomando: fmt
    parser_fmt = subparsers.add_parser(
        "fmt", 
        help="Formatea archivos MyST Markdown."
    )
    parser_fmt.add_argument(
        "files", 
        nargs="*", 
        help="Archivos o directorios a formatear (por defecto, todos los archivos .md si la entrada es interactiva)."
    )
    parser_fmt.add_argument(
        "--check", 
        action="store_true", 
        help="Solo verifica si los archivos necesitan formato."
    )
    parser_fmt.add_argument(
        "--stdout", 
        action="store_true", 
        help="Imprime el resultado a la salida estándar en vez de modificar in-place."
    )
    parser_fmt.add_argument(
        "--width", 
        type=int, 
        default=80, 
        help="Ancho máximo de línea (default: 80)."
    )
    
    args = parser.parse_args()
    
    if args.command == "add-anchors":
        run_add_anchors(args.dir)
    elif args.command == "gen-apunte":
        run_generate_apunte_index(args.dir)
    elif args.command == "gen-guides":
        run_generate_guides_index(args.dir)
    elif args.command == "gen-rules":
        run_generate_rules_index(args.dir)
    elif args.command == "fix-anchors":
        sys.exit(run_fix_dup_anchors(args.dir, dry_run=args.dry_run, report=args.report))
    elif args.command == "fmt":
        sys.exit(run_myst_fmt(args.files, check=args.check, stdout=args.stdout, width=args.width))
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
