import os
import re

def analyze_and_extract():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Workspace directory: {workspace_dir}")
    
    for i in range(1, 11):
        filename = f"{i}.txt"
        file_path = os.path.join(workspace_dir, filename)
        if not os.path.exists(file_path):
            print(f"File {filename} does not exist.")
            continue
            
        print(f"\n--- Analyzing {filename} ---")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse paragraphs using regex or simple line-by-line parsing
        lines = content.split('\n')
        
        paragraphs = []
        current_p_num = None
        current_section = None
        korean_text = []
        ai_text = []
        
        for line_num, line in enumerate(lines, 1):
            if line_num == 1 and line.startswith('\ufeff'):
                line = line[1:]
            stripped = line.strip()
            
            p_match = re.match(r'^문단\s+(\d+)', stripped)
            if p_match:
                # Save previous paragraph
                if current_p_num is not None:
                    paragraphs.append({
                        "num": current_p_num,
                        "korean": "\n".join(korean_text).strip(),
                        "ai": "\n".join(ai_text).strip()
                    })
                current_p_num = int(p_match.group(1))
                current_section = None
                korean_text = []
                ai_text = []
                continue
                
            if stripped == "- 한글":
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
                
            if current_section == "korean":
                korean_text.append(stripped)
            elif current_section == "ai":
                ai_text.append(stripped)
                
        # Append the last paragraph
        if current_p_num is not None:
            paragraphs.append({
                "num": current_p_num,
                "korean": "\n".join(korean_text).strip(),
                "ai": "\n".join(ai_text).strip()
            })
            
        print(f"Total paragraphs parsed: {len(paragraphs)}")
        empty_korean = [p["num"] for p in paragraphs if not p["korean"]]
        if empty_korean:
            print(f"Paragraphs with empty Korean translation: {empty_korean}")
        else:
            print("All paragraphs have Korean translation!")
            
if __name__ == "__main__":
    analyze_and_extract()
