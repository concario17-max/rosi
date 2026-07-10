import os
import re

def merge_paragraphs_3_93_96():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(workspace_dir, "새 폴더", "3.txt")
    
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = content.split('\n')
    
    paragraphs = []
    current_p_num = None
    current_section = None
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
            p_data[current_section].append(line)
            
    if p_data:
        paragraphs.append(p_data)
        
    print(f"Read {len(paragraphs)} paragraphs from 3.txt.")
    
    # Gather paragraphs 93, 94, 95, 96
    target_nums = [93, 94, 95, 96]
    target_paras = {num: None for num in target_nums}
    for p in paragraphs:
        if p['num'] in target_paras:
            target_paras[p['num']] = p
            
    # Check if all targets exist
    for num, p in target_paras.items():
        if not p:
            print(f"Could not find paragraph {num}. Maybe already merged?")
            return
            
    # Merge 93 to 96
    p93 = target_paras[93]
    p94 = target_paras[94]
    p95 = target_paras[95]
    p96 = target_paras[96]
    
    merged_p = {
        'num': 93,
        'german': p93['german'] + p94['german'] + p95['german'] + p96['german'],
        'english': p93['english'] + p94['english'] + p95['english'] + p96['english'],
        'korean': p93['korean'] + p94['korean'] + p95['korean'] + p96['korean'],
        'ai': p93['ai'] + p94['ai'] + p95['ai'] + p96['ai']
    }
    
    new_paragraphs = []
    for p in paragraphs:
        if p['num'] < 93:
            new_paragraphs.append(p)
        elif p['num'] == 93:
            new_paragraphs.append(merged_p)
        elif p['num'] in [94, 95, 96]:
            continue # skip merged
        else:
            # Shift num by -3
            p_copy = p.copy()
            p_copy['num'] = p['num'] - 3
            new_paragraphs.append(p_copy)
            
    # Write back to 3.txt
    output_lines = []
    output_lines.append("3강 전체 정밀재검수본")
    output_lines.append("")
    output_lines.append(f"※ 3강 전체 {len(new_paragraphs)}문단을 기준으로 재검수했습니다.")
    output_lines.append("※ 형식: 문단 번호 → 독일어 → 영어 → 한글 → AI 번역")
    output_lines.append("")
    
    for p in new_paragraphs:
        output_lines.append(f"문단 {p['num']}")
        
        # 독일어
        output_lines.append("- 독일어")
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
        f_out.write("\n".join(output_lines).strip() + "\n")
        
    print(f"Successfully merged paragraphs 93-96. New paragraph count: {len(new_paragraphs)}")

if __name__ == "__main__":
    merge_paragraphs_3_93_96()
