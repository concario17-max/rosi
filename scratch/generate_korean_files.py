import os
import re

def parse_and_generate():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(workspace_dir, "새 폴더")
    print(f"Workspace directory: {workspace_dir}")
    print(f"Data directory: {data_dir}")
    
    for i in range(1, 11):
        filename = f"{i}.txt"
        file_path = os.path.join(data_dir, filename)
        if not os.path.exists(file_path):
            print(f"File {filename} does not exist.")
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        lines = content.split('\n')
        
        paragraphs = []
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
                    paragraphs.append((current_p_num, "\n".join(korean_text).strip()))
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
            elif re.match(r'^=+$', stripped):
                continue
                
            if current_section == "korean":
                korean_text.append(stripped)
                
        if current_p_num is not None:
            paragraphs.append((current_p_num, "\n".join(korean_text).strip()))
            
        # Write to output file in the same directory (새 폴더)
        output_filename = f"{i}_한글.txt"
        output_path = os.path.join(data_dir, output_filename)
        
        output_lines = []
        for p_num, text in paragraphs:
            text_lines = text.split('\n')
            if text_lines:
                output_lines.append(f"{p_num}. {text_lines[0]}")
                for extra_line in text_lines[1:]:
                    output_lines.append(extra_line)
            output_lines.append("")
            
        with open(output_path, 'w', encoding='utf-8') as f_out:
            f_out.write("\n".join(output_lines).strip() + "\n")
            
        print(f"Generated {output_filename} with {len(paragraphs)} paragraphs.")

if __name__ == "__main__":
    parse_and_generate()
