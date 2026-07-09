import os
import sys
import re
from read_odt import read_odt_text

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def list_headings():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    odt_path = os.path.join(workspace_dir, "장미 2-2.odt")
    
    if not os.path.exists(odt_path):
        print(f"File {odt_path} does not exist.")
        return
        
    paragraphs = read_odt_text(odt_path)
    
    headings = []
    for p in paragraphs:
        match = re.match(r'^(\d+)\.\s+(.+)$', p)
        if match:
            num = int(match.group(1))
            title = match.group(2)
            headings.append((num, title))
            
    print(f"Found {len(headings)} headings in 장미 2-2.odt.")
    for num, title in headings:
        print(f"  {num}. {title[:50]}...")

if __name__ == "__main__":
    list_headings()
