import os
import re
import unicodedata

def slugify(text):
    # Quitar acentos y normalizar a ASCII
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    # Pasar a minúsculas
    text = text.lower()
    # Reemplazar caracteres no alfanuméricos por guiones
    text = re.sub(r'[^a-z0-9]+', '-', text)
    # Limpiar guiones duplicados y extremos
    return text.strip('-')

def extract_headers(content):
    # Regex to find headers #, ##, ###
    header_pattern = r'^(#{1,3})\s+(.*)'
    headers = re.findall(header_pattern, content, re.MULTILINE)
    return headers

def run_generate_apunte_index(apunte_dir='./apunte_2'):
    if not os.path.exists(apunte_dir):
        print(f"Error: El directorio '{apunte_dir}' no existe.")
        return
        
    # List all .md files in apunte/ except indice.md
    files = sorted([f for f in os.listdir(apunte_dir) if f.endswith('.md') and f != 'indice.md'])
    
    if not files:
        print(f"No se encontraron archivos markdown en '{apunte_dir}'.")
        return
        
    output = ["# Apunte de Cátedra\n"]
    
    for filename in files:
        path = os.path.join(apunte_dir, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        headers = extract_headers(content)
        
        if not headers:
            continue
            
        # First header is usually Level 1 and matches the file title
        # We use {doc} for the main file entry
        file_base = filename.replace('.md', '')
        
        # We'll group by file. The first # header will be our main link.
        # If there's a Level 1 header, use it as the main point.
        main_title = None
        for level, title in headers:
            if level == '#':
                main_title = title.strip()
                break
        
        if main_title:
            output.append(f"## {{doc}}`{file_base}`")
        else:
            # Fallback if no # header (unlikely given our files)
            output.append(f"## {{doc}}`{file_base}`")

        # Now add ## and ### as sub-items
        for level, title in headers:
            clean_title = title.strip()
            # Skip if it's the main title we already used for the {doc} link
            if level == '#' and clean_title == main_title:
                continue
                
            indent = ""
            if level == '##':
                indent = "  *"
            elif level == '###':
                indent = "    *"
            else:
                continue # Skip # if it wasn't the main one or if we want to list it too? 
                # User asked for "hasta nivel 3", grouped by file.
            
            # Create internal link to the header within the doc
            # MyST/Sphinx syntax for linking to a header in another doc:
            # [Title](docname.md#header-slug)
            slug = slugify(clean_title)
            output.append(f"{indent} [{clean_title}]({file_base}.md#{slug})")
            
        output.append("") # Spacer between files
            
    dest_file = os.path.join(apunte_dir, 'indice.md')
    with open(dest_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(output))
    
    print(f"Índice detallado de apunte generado en {dest_file}")

def main():
    import sys
    apunte_dir = sys.argv[1] if len(sys.argv) > 1 else './apunte_2'
    run_generate_apunte_index(apunte_dir)

if __name__ == "__main__":
    main()

