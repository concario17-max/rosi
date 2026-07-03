import os
import shutil
import re
import json
import sys

# Ensure UTF-8 output formatting for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def copy_project_skeleton(src_dir, dest_dir):
    print(f"Copying project skeleton from {src_dir} to {dest_dir}...")
    
    # Exclude directories
    exclude_dirs = {'.git', 'node_modules', 'dist', 'miracle', 'lamp', 'scratch', '.github', '.idea', '__pycache__', '학습만화'}
    # Exclude specific files in the root if they are not needed
    exclude_files = {'기적수업 (영-한).docx', '기적수업-1.odt', '기적수업-2.odt', '기적수업-3.odt', '기적수업-4.odt', 'tsconfig.node.tsbuildinfo', 'tsconfig.tsbuildinfo'}
    
    # Copy root files and directories
    for item in os.listdir(src_dir):
        src_item = os.path.join(src_dir, item)
        dest_item = os.path.join(dest_dir, item)
        
        if os.path.isdir(src_item):
            if item in exclude_dirs:
                continue
            print(f"  Copying directory: {item}")
            shutil.copytree(src_item, dest_item, dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', '*.test.ts', '*.test.tsx', 'node_modules', 'dist'))
        else:
            if item in exclude_files:
                continue
            print(f"  Copying file: {item}")
            shutil.copy2(src_item, dest_item)

def parse_rosi_text(txt_path, subchapter_id, chapter_title="장미십자 방법"):
    print(f"Parsing translations from: {txt_path}")
    
    if not os.path.exists(txt_path):
        raise FileNotFoundError(f"Source text file not found at {txt_path}")
        
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    paragraphs = []
    current_p = None
    current_section = None
    
    for line_num, line in enumerate(lines, 1):
        # Handle BOM if present in the first line
        if line_num == 1 and line.startswith('\ufeff'):
            line = line[1:]
            
        stripped = line.strip()
        
        # Check if this line starts a new paragraph (e.g. "문단 1", "문단 2")
        p_match = re.match(r'^문단\s+(\d+)$', stripped)
        if p_match:
            if current_p:
                paragraphs.append(current_p)
            
            p_num = int(p_match.group(1))
            current_p = {
                "id": f"rosi.{subchapter_id}.{p_num}",
                "title": f"문단 {p_num}",
                "paragraphNumber": p_num,
                "chapterTitle": chapter_title,
                "text": {
                    "german": "",
                    "english": "",
                    "korean": "",
                    "ai_translation": ""
                }
            }
            current_section = None
            continue
            
        if not current_p:
            # Skip any lines before the first paragraph
            continue
            
        # Check for section headers
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
            current_section = "ai_translation"
            continue
            
        # Append line content to the active section
        if current_section:
            existing = current_p["text"][current_section]
            if existing:
                current_p["text"][current_section] = existing + "\n" + stripped
            else:
                current_p["text"][current_section] = stripped

    # Append the last paragraph
    if current_p:
        paragraphs.append(current_p)
        
    # Clean up empty lines at the end of sections
    for p in paragraphs:
        for key in p["text"]:
            p["text"][key] = p["text"][key].strip()
            
    print(f"Successfully parsed {len(paragraphs)} paragraphs.")
    return paragraphs

def main():
    dest_project = os.getcwd()
    src_project = r"J:\홈페이지\miracle"
    
    print(f"Working directory: {dest_project}")
    
    # 1. Copy Skeleton files
    copy_project_skeleton(src_project, dest_project)
    
    # 2. Find and parse all lecture text files dynamically (e.g. 1-1.txt, 1-2.txt)
    txt_files = []
    for f in os.listdir(dest_project):
        # Match filenames like 1-1.txt, 1-2.txt, etc.
        match = re.match(r'^1-(\d+)\.txt$', f)
        if match:
            lecture_num = int(match.group(1))
            txt_files.append((lecture_num, os.path.join(dest_project, f)))
            
    # Sort by lecture number to keep order
    txt_files.sort()
    
    if not txt_files:
        print("Error: Could not find any translation text files (e.g. 1-1.txt) in the current directory.")
        sys.exit(1)
        
    subchapters = []
    for lecture_num, txt_path in txt_files:
        paragraphs = parse_rosi_text(txt_path, subchapter_id=lecture_num)
        
        # Calculate paragraph range text for tocHeadings
        if paragraphs:
            start_p = paragraphs[0]["paragraphNumber"]
            end_p = paragraphs[-1]["paragraphNumber"]
            toc_range = f"Paragraphs {start_p} - {end_p}"
        else:
            toc_range = "Paragraphs"
            
        subchapters.append({
            "id": f"rosi.{lecture_num}",
            "chapterName": f"제 {lecture_num}강",
            "title": f"Lecture {lecture_num}",
            "tocHeadings": [toc_range],
            "paragraphs": paragraphs
        })
        
    # 3. Save as reading-data.json
    reading_data = {
        "chapters": [
            {
                "id": "bodhi", # Keep "bodhi" to match dataFetcher filtering
                "chapterName": "장미십자 방법",
                "title": "The Rosicrucian Method",
                "isGroup": True,
                "subchapters": subchapters
            }
        ]
    }
    
    public_dir = os.path.join(dest_project, "public")
    os.makedirs(public_dir, exist_ok=True)
    json_path = os.path.join(public_dir, "reading-data.json")
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(reading_data, f, ensure_ascii=False, indent=4)
        
    print(f"Saved reading data to {json_path}")
    
    # 4. Remove unnecessary bodhi-commentary.json if exists in public
    comm_path = os.path.join(public_dir, "bodhi-commentary.json")
    if os.path.exists(comm_path):
        os.remove(comm_path)
        print("Removed bodhi-commentary.json")

if __name__ == "__main__":
    main()
