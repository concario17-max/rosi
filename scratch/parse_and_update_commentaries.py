import os
import sys
import re
import json
import unicodedata
from read_odt import read_odt_text

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def is_emoji_heading(text):
    if not text:
        return False
    if text.startswith("📝 핵심 요약") or text.startswith("📝핵심 요약"):
        return True
    first_char = text[0]
    val = ord(first_char)
    if (0xAC00 <= val <= 0xD7A3) or (0x1100 <= val <= 0x11FF) or (0x3130 <= val <= 0x318F) or (0x4E00 <= val <= 0x9FFF):
        return False
    if first_char.isalnum() or first_char in ['"', "'", '-', '[', '(']:
        return False
        
    category = unicodedata.category(first_char)
    if (category in ('So', 'Sk', 'Sm') or val > 0x2000) and len(text) < 120:
        return True
    return False

def parse_and_update():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    odt_path = os.path.join(workspace_dir, "장미 2-1.odt")
    
    if not os.path.exists(odt_path):
        print(f"File {odt_path} does not exist.")
        return
        
    paragraphs = read_odt_text(odt_path)
    
    entries = {}
    current_num = None
    current_lines = []
    
    for p in paragraphs:
        if p.startswith("[🟢 Online Mode"):
            continue
            
        match = re.match(r'^(\d+)\.\s+(.+)$', p)
        if match:
            if current_num is not None:
                entries[current_num] = current_lines
            current_num = int(match.group(1))
            current_lines = [f"# {p}"]
        else:
            if current_num is not None:
                if p.startswith("🔑 핵심 키워드:"):
                    current_lines.append(p)
                elif is_emoji_heading(p):
                    current_lines.append(f"### {p}")
                else:
                    has_summary_header = any(line.startswith("### 📝 핵심 요약") for line in current_lines)
                    if has_summary_header:
                        if p.startswith("-"):
                            current_lines.append(p)
                        else:
                            current_lines.append(f"- {p}")
                    else:
                        current_lines.append(p)
                        
    if current_num is not None:
        entries[current_num] = current_lines
        
    print(f"Parsed {len(entries)} entries from ODT.")
    
    # Load existing JSON
    json_path = os.path.join(workspace_dir, "public", "bodhi-commentary.json")
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            commentaries = json.load(f)
        print(f"Loaded existing commentary file with {len(commentaries)} entries.")
    else:
        commentaries = {}
        print("Creating new commentary JSON database.")
        
    # Update entries
    for num, lines in entries.items():
        key = f"rosi.2.{num}"
        # Format as markdown blocks separated by double newlines
        markdown_text = "\n\n".join(lines)
        commentaries[key] = markdown_text
        
    # Save back to JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(commentaries, f, ensure_ascii=False, indent=2)
        
    print(f"Saved {len(commentaries)} total commentaries to {json_path}.")

if __name__ == "__main__":
    parse_and_update()
