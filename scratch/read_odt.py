import zipfile
import xml.etree.ElementTree as ET
import os
import sys

# Ensure UTF-8 output formatting for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def read_odt_text(odt_path):
    if not os.path.exists(odt_path):
        print(f"File {odt_path} does not exist.")
        return ""
        
    with zipfile.ZipFile(odt_path, 'r') as zip_ref:
        content_xml = zip_ref.read('content.xml')
        
    # Parse XML
    root = ET.fromstring(content_xml)
    
    # namespaces
    ns = {
        'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
        'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
    }
    
    # Find all paragraph elements: <text:p>
    paragraphs = []
    for elem in root.iter():
        if elem.tag.endswith('}p') or elem.tag.endswith('}h'):
            # Extract text from element and its children
            text = "".join(elem.itertext()).strip()
            if text:
                paragraphs.append(text)
                
    return paragraphs

def main():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    odt_path = os.path.join(workspace_dir, "장미 2-1.odt")
    paragraphs = read_odt_text(odt_path)
    print(f"Read {len(paragraphs)} paragraphs from {odt_path}.")
    for idx, p in enumerate(paragraphs[:30]):
        print(f"{idx+1}: {p[:100]}...")

if __name__ == "__main__":
    main()
