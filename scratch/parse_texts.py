import os
import re
import json
import sys

# Ensure UTF-8 output formatting for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def parse_rosi_text(txt_path, lecture_num, chapter_title="장미십자 방법"):
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
        
        # Skip separator lines
        if re.match(r'^=+$', stripped):
            continue
            
        # Check if this line starts a new paragraph (e.g. "문단 1", "문단 2")
        p_match = re.match(r'^문단\s+(\d+)(?:\s+.*)?$', stripped)
        if p_match:
            if current_p:
                paragraphs.append(current_p)
            
            p_num = int(p_match.group(1))
            current_p = {
                "id": f"rosi.{lecture_num}.{p_num}",
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
            
    print(f"Successfully parsed {len(paragraphs)} paragraphs from {os.path.basename(txt_path)}.")
    return paragraphs

LECTURE_TITLES = {
    1: {
        "chapterName": "1강 장미십자의 비교",
        "title": "Rosicrucian Esotericism"
    },
    2: {
        "chapterName": "2강 우리 바깥 세계에 존재하는 혼",
        "title": "Soul in the World around Us"
    },
    3: {
        "chapterName": "3강 인간의 성질과 존재",
        "title": "The Nature and Being of Man"
    },
    4: {
        "chapterName": "4강 죽음과 탄생 사이의 인간",
        "title": "Man Between Death and Rebirth"
    },
    5: {
        "chapterName": "5강 영적 힘과 존재들의 표출인 물질계",
        "title": "The Physical World as an Expression of Spiritual Forces and Beings"
    },
    6: {
        "chapterName": "6강 인간 육체의 형성과 변용",
        "title": "The Configuration and Metamorphoses of Man's Physical Body"
    },
    7: {
        "chapterName": "7강 레무리아기 이전의 지구진화단계",
        "title": "Evolutionary Stages of our Earth before the Lemurian Epoch"
    },
    8: {
        "chapterName": "8강 지구진화단계 : 레무리아, 아틀란티스, 후아틀란티스",
        "title": "Stages in the Evolution of our Earth. Lemurian, Atlantean, Post-Atlantean Epochs"
    },
    9: {
        "chapterName": "9강 인간의 사후경험",
        "title": "Man's Experience after Death"
    },
    10: {
        "chapterName": "10강 카르마, 재육화, 비의입문",
        "title": "On Karma, Reincarnation and Initiation"
    }
}



def main():
    dest_project = os.getcwd()
    print(f"Working directory: {dest_project}")
    
    # Group files by lecture number: e.g. 1-1.txt, 1-2.txt, 1-3.txt all map to lecture_num = 1
    # Key: lecture_num (int), Value: list of file paths
    lecture_groups = {}
    
    for f in os.listdir(dest_project):
        match_part = re.match(r'^(\d+)-(\d+)\.txt$', f)
        match_single = re.match(r'^(\d+)\.txt$', f)
        
        if match_part:
            lecture_num = int(match_part.group(1))
            part_num = int(match_part.group(2))
            
            if lecture_num not in lecture_groups:
                lecture_groups[lecture_num] = []
            
            lecture_groups[lecture_num].append((part_num, os.path.join(dest_project, f)))
        elif match_single:
            lecture_num = int(match_single.group(1))
            part_num = 1
            
            if lecture_num not in lecture_groups:
                lecture_groups[lecture_num] = []
            
            lecture_groups[lecture_num].append((part_num, os.path.join(dest_project, f)))
            
    if not lecture_groups:
        print("Error: Could not find any translation text files (e.g. 1-1.txt) in the current directory.")
        sys.exit(1)
        
    subchapters = []
    
    # Process each lecture group in order
    for lecture_num in sorted(lecture_groups.keys()):
        # Sort files in this group by part number (e.g. 1-1, 1-2, 1-3)
        parts = lecture_groups[lecture_num]
        parts.sort()
        
        all_paragraphs = []
        for part_num, txt_path in parts:
            paragraphs = parse_rosi_text(txt_path, lecture_num=lecture_num)
            all_paragraphs.extend(paragraphs)
            
        # Sort all paragraphs in the lecture by paragraphNumber to ensure numerical order
        all_paragraphs.sort(key=lambda p: p["paragraphNumber"])
        
        # Calculate paragraph range text for tocHeadings
        if all_paragraphs:
            start_p = all_paragraphs[0]["paragraphNumber"]
            end_p = all_paragraphs[-1]["paragraphNumber"]
            toc_range = f"Paragraphs {start_p} - {end_p}"
        else:
            toc_range = "Paragraphs"
            
        title_info = LECTURE_TITLES.get(lecture_num, {
            "chapterName": f"제 {lecture_num}강",
            "title": f"Lecture {lecture_num}"
        })
        
        subchapters.append({
            "id": f"rosi.{lecture_num}",
            "chapterName": title_info["chapterName"],
            "title": title_info["title"],
            "tocHeadings": [toc_range],
            "paragraphs": all_paragraphs
        })
        
    # Save as reading-data.json
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

if __name__ == "__main__":
    main()
