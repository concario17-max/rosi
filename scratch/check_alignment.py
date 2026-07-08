import os
import sys
import re
from read_odt import read_odt_text

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def check_alignment():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    odt_path = os.path.join(workspace_dir, "장미 2-1.odt")
    paragraphs = read_odt_text(odt_path)
    
    current_num = None
    curr_text = []
    
    for p in paragraphs:
        match = re.match(r'^(\d+)\.\s+(.+)$', p)
        if match:
            if current_num is not None:
                # Print title and snippet of first paragraph
                text_content = "\n".join(curr_text).strip()
                snippet = text_content[:200] if text_content else "No text"
                print(f"[{current_num}] {snippet}\n")
            current_num = int(match.group(1))
            curr_text = []
        else:
            if current_num is not None:
                curr_text.append(p)
                
    if current_num is not None:
        text_content = "\n".join(curr_text).strip()
        snippet = text_content[:200] if text_content else "No text"
        print(f"[{current_num}] {snippet}\n")

if __name__ == "__main__":
    check_alignment()
