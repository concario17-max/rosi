import os
import sys
from read_odt import read_odt_text

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def check_first():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    odt_path = os.path.join(workspace_dir, "장미 3-1.odt")
    paragraphs = read_odt_text(odt_path)
    
    print("First 20 paragraphs in ODT:")
    for i, p in enumerate(paragraphs[:20]):
        print(f"[{i}]: {p[:120]}")

if __name__ == "__main__":
    check_first()
