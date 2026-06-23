import argparse
import sys
from myst_tools.add_myst_anchors import run_add_anchors
from myst_tools.generate_apunte_index import run_generate_apunte_index
from myst_tools.generate_guides_index import run_generate_guides_index
from myst_tools.generate_rules_index import run_generate_rules_index

def main() -> None:
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
        default="./apunte_2", 
        help="Directorio del apunte (apunte_2)."
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
    
    args = parser.parse_args()
    
    if args.command == "add-anchors":
        run_add_anchors(args.dir)
    elif args.command == "gen-apunte":
        run_generate_apunte_index(args.dir)
    elif args.command == "gen-guides":
        run_generate_guides_index(args.dir)
    elif args.command == "gen-rules":
        run_generate_rules_index(args.dir)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
