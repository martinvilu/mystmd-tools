import os
import re

def extract_file_title(content):
    # Try frontmatter first
    fm_match = re.search(r'^---\s*\n.*?title:\s*(.*?)\n.*?---', content, re.DOTALL | re.MULTILINE)
    if fm_match:
        return fm_match.group(1).strip()
    
    # Try first # header
    h1_match = re.search(r'^#\s+(.*)', content, re.MULTILINE)
    if h1_match:
        return h1_match.group(1).strip()
    
    return None

def run_generate_guides_index(guias_dir='./guias'):
    if not os.path.exists(guias_dir):
        print(f"Error: El directorio '{guias_dir}' no existe.")
        return
        
    # List all .md files in guias/ except indice.md
    files = sorted([f for f in os.listdir(guias_dir) if f.endswith('.md') and f != 'indice.md'])
    
    if not files:
        print(f"No se encontraron archivos markdown en '{guias_dir}'.")
        return
        
    output = ["# Índice de Guías\n"]
    
    for filename in files:
        path = os.path.join(guias_dir, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        title = extract_file_title(content)
        if not title:
            # Fallback to filename if no title found
            title = filename.replace('.md', '').replace('_', ' ').capitalize()
            
        # Create a MyST-friendly link
        # Use {doc}`filename` for MyST cross-references between documents
        output.append(f"* {{doc}}`{filename.replace('.md', '')}`")
        
    dest_file = os.path.join(guias_dir, 'indice.md')
    with open(dest_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(output))
    
    print(f"Índice de guías generado en {dest_file}")

def main():
    import sys
    guias_dir = sys.argv[1] if len(sys.argv) > 1 else './guias'
    run_generate_guides_index(guias_dir)

if __name__ == "__main__":
    main()

