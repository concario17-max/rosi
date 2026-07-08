import os
import re

def merge_paragraphs_in_file():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(workspace_dir, "2.txt")
    
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = content.split('\n')
    
    paragraphs = []
    current_p_num = None
    current_section = None
    
    # We will store paragraph data structured as:
    # { 'num': int, 'german': [], 'english': [], 'korean': [], 'ai': [] }
    p_data = None
    
    for line_num, line in enumerate(lines, 1):
        if line_num == 1 and line.startswith('\ufeff'):
            line = line[1:]
        stripped = line.strip()
        
        p_match = re.match(r'^문단\s+(\d+)', stripped)
        if p_match:
            if p_data:
                paragraphs.append(p_data)
            p_num = int(p_match.group(1))
            p_data = {
                'num': p_num,
                'german': [],
                'english': [],
                'korean': [],
                'ai': []
            }
            current_section = None
            continue
            
        if not p_data:
            continue
            
        if stripped == "- 독일어":
            current_section = "german"
            continue
        elif stripped == "- 영어":
            current_section = "english"
            continue
        elif stripped == "- 한글":
            current_section = "korean"
            continue
        elif stripped == "- AI 번역":
            current_section = "ai"
            continue
        elif stripped.startswith("- "):
            current_section = "other"
            continue
        elif re.match(r'^=+$', stripped):
            continue
            
        if current_section in ['german', 'english', 'korean', 'ai']:
            p_data[current_section].append(line) # keep original line including spaces if any
            
    if p_data:
        paragraphs.append(p_data)
        
    print(f"Read {len(paragraphs)} paragraphs from 2.txt.")
    
    # Find paragraph 7 and 8
    p7 = None
    p8 = None
    for p in paragraphs:
        if p['num'] == 7:
            p7 = p
        elif p['num'] == 8:
            p8 = p
            
    if not p7 or not p8:
        print("Could not find paragraph 7 or 8. Maybe already merged?")
        return
        
    # Merge 7 and 8
    merged_p = {
        'num': 7,
        'german': p7['german'] + p8['german'],
        'english': p7['english'] + p8['english'],
        'korean': p7['korean'] + p8['korean'],
        'ai': p7['ai'] + p8['ai']
    }
    
    new_paragraphs = []
    for p in paragraphs:
        if p['num'] < 7:
            new_paragraphs.append(p)
        elif p['num'] == 7:
            new_paragraphs.append(merged_p)
        elif p['num'] == 8:
            continue # skip 8, merged into 7
        else:
            # Shift num by -1
            p_copy = p.copy()
            p_copy['num'] = p['num'] - 1
            new_paragraphs.append(p_copy)
            
    # Write back to 2.txt
    output_lines = []
    output_lines.append("2강 전체 정밀재검수본")
    output_lines.append("")
    output_lines.append("※ 2강 전체 81문단을 기준으로 재검수했습니다.")
    output_lines.append("※ 형식: 문단 번호 → 독일어 → 영어 → 한글 → AI 번역")
    output_lines.append("")
    
    for p in new_paragraphs:
        output_lines.append(f"문단 {p['num']}")
        
        # 독일어
        output_lines.append("- 독일어")
        # Join lines, strip, and make sure we don't have double space
        german_text = " ".join([l.strip() for l in p['german'] if l.strip()])
        output_lines.append(german_text)
        output_lines.append("")
        
        # 영어
        output_lines.append("- 영어")
        english_text = " ".join([l.strip() for l in p['english'] if l.strip()])
        output_lines.append(english_text)
        output_lines.append("")
        
        # 한글
        output_lines.append("- 한글")
        korean_text = " ".join([l.strip() for l in p['korean'] if l.strip()])
        output_lines.append(korean_text)
        output_lines.append("")
        
        # AI 번역
        output_lines.append("- AI 번역")
        ai_text = " ".join([l.strip() for l in p['ai'] if l.strip()])
        output_lines.append(ai_text)
        output_lines.append("")
        
        output_lines.append("================================================================================")
        output_lines.append("")
        
    with open(file_path, 'w', encoding='utf-8') as f_out:
        # Write without trailing empty lines
        f_out.write("\n".join(output_lines).strip() + "\n")
        
    print(f"Successfully merged paragraph 7 & 8. New paragraph count: {len(new_paragraphs)}")

if __name__ == "__main__":
    merge_paragraphs_in_file()
