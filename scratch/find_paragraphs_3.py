import os
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def find_paras():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(workspace_dir, "새 폴더", "3.txt")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = content.split('\n')
    
    current_p_num = None
    current_section = None
    korean_text = []
    
    for line_num, line in enumerate(lines, 1):
        if line_num == 1 and line.startswith('\ufeff'):
            line = line[1:]
        stripped = line.strip()
        
        p_match = re.match(r'^문단\s+(\d+)', stripped)
        if p_match:
            if current_p_num is not None:
                joined = " ".join(korean_text).strip()
                if "2개의 유골을" in joined or "내일 우리는 죽음 이후" in joined:
                    print(f"Paragraph {current_p_num}: {joined[:150]}...")
            current_p_num = int(p_match.group(1))
            current_section = None
            korean_text = []
            continue
            
        if stripped == "- 한글":
            current_section = "korean"
            continue
        elif stripped.startswith("- "):
            current_section = "other"
            continue
            
        if current_section == "korean" and stripped:
            korean_text.append(stripped)
            
    if current_p_num is not None:
        joined = " ".join(korean_text).strip()
        if "2개의 유골을" in joined or "내일 우리는 죽음 이후" in joined:
            print(f"Paragraph {current_p_num}: {joined[:150]}...")

if __name__ == "__main__":
    find_paras()
