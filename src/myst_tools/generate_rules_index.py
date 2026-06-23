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
    
    return "Sin título"

def extract_rules(content):
    # Match (label)= followed by a header
    # Pattern: (label)=\n## Title
    rules = []
    # Using re.MULTILINE and re.DOTALL is tricky for this.
    # Let's find all (label)= and then the next header.
    
    pattern = r'\((regla-[^\)]+)\)=\s*\n(?:###?|####?)\s+(.*)'
    matches = re.findall(pattern, content)
    for label, title in matches:
        rules.append((label.strip(), title.strip()))
    
    return rules

def run_generate_rules_index(reglas_dir='./reglas'):
    if not os.path.exists(reglas_dir):
        print(f"Error: El directorio '{reglas_dir}' no existe.")
        return
        
    files = sorted([f for f in os.listdir(reglas_dir) if f.endswith('.md') and f not in ['indice.md', 'indice_nuevo.md', 'reglas_.md', 'convenciones_codigo_java.md', 'reglas.md']])
    
    if not files:
        print(f"No se encontraron archivos markdown en '{reglas_dir}'.")
        return
        
    output = ["# Índice de Reglas de Estilo\n"]
    
    for filename in files:
        path = os.path.join(reglas_dir, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        file_title = extract_file_title(content)
        rules = extract_rules(content)
        
        if rules:
            output.append(f"## {file_title}")
            for label, title in rules:
                output.append(f"* {{ref}}`{label}`")
            output.append("") # Spacer
            
    dest_file = os.path.join(reglas_dir, 'indice.md')
    with open(dest_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(output))
    
    print(f"Índice actualizado en {dest_file}")

def main():
    import sys
    reglas_dir = sys.argv[1] if len(sys.argv) > 1 else './reglas'
    run_generate_rules_index(reglas_dir)

if __name__ == "__main__":
    main()
