import os
import sys
import re
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
    # Check if Hangul or CJK
    if (0xAC00 <= val <= 0xD7A3) or (0x1100 <= val <= 0x11FF) or (0x3130 <= val <= 0x318F) or (0x4E00 <= val <= 0x9FFF):
        return False
    # Check if alphanumeric or standard punctuation
    if first_char.isalnum() or first_char in ['"', "'", '-', '[', '(']:
        return False
        
    category = unicodedata.category(first_char)
    if (category in ('So', 'Sk', 'Sm') or val > 0x2000) and len(text) < 120:
        return True
    return False

def test_parse():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    odt_path = os.path.join(workspace_dir, "장미 2-1.odt")
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
                    # Bullet points under "핵심 요약"
                    # Let's search if "핵심 요약" was already pushed in current_lines
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
        
    print(f"Parsed {len(entries)} entries.")
    
    # Print entry 1 and 2
    for num in [1, 2]:
        if num in entries:
            print(f"\n--- ENTRY {num} ---")
            print("\n\n".join(entries[num]))

if __name__ == "__main__":
    test_parse()
