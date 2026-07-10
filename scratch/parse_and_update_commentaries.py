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
    # Accept chapter number from arguments, default to 2
    chapter = "2"
    if len(sys.argv) > 1:
        chapter = sys.argv[1]
        
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Find all 장미 <chapter>-*.odt files
    odt_files = []
    pattern = re.compile(rf'^장미 {chapter}-\d+\.odt$')
    for f in os.listdir(workspace_dir):
        if pattern.match(f):
            odt_files.append(os.path.join(workspace_dir, f))
            
    odt_files.sort()
    
    if not odt_files:
        print(f"No 장미 {chapter}-*.odt files found.")
        return
        
    all_entries = {}
    
    for odt_path in odt_files:
        print(f"Parsing {os.path.basename(odt_path)}...")
        paragraphs = read_odt_text(odt_path)
        
        current_num = None
        current_lines = []
        
        for p in paragraphs:
            if p.startswith("[🟢 Online Mode"):
                continue
                
            match = re.match(r'^(\d+)\.\s+(.+)$', p)
            if match:
                if current_num is not None:
                    all_entries[current_num] = current_lines
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
            all_entries[current_num] = current_lines
            
    print(f"Successfully parsed {len(all_entries)} total entries from {len(odt_files)} ODT files.")
    
    # Load existing JSON
    json_path = os.path.join(workspace_dir, "public", "bodhi-commentary.json")
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            commentaries = json.load(f)
        print(f"Loaded existing commentary file with {len(commentaries)} entries.")
    else:
        commentaries = {}
        print("Creating new commentary JSON database.")
        
    # Update entries in the JSON dictionary
    for num, lines in all_entries.items():
        key = f"rosi.{chapter}.{num}"
        markdown_text = "\n\n".join(lines)
        commentaries[key] = markdown_text
        
    # Save back to JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(commentaries, f, ensure_ascii=False, indent=2)
        
    print(f"Saved {len(commentaries)} total commentaries to {json_path}.")

if __name__ == "__main__":
    parse_and_update()
