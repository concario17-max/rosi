import os
import sys
import re
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def analyze():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(workspace_dir, "새 폴더")
    
    print("================================================================================")
    print("                           [ROSI DATA COMPREHENSIVE ANALYSIS]                  ")
    print("================================================================================\n")
    
    # 1. Load public/reading-data.json
    reading_data_path = os.path.join(workspace_dir, "public", "reading-data.json")
    if not os.path.exists(reading_data_path):
        print("❌ Error: public/reading-data.json not found.")
        return
        
    with open(reading_data_path, 'r', encoding='utf-8') as f:
        reading_data = json.load(f)
        
    # 2. Load public/bodhi-commentary.json
    commentary_path = os.path.join(workspace_dir, "public", "bodhi-commentary.json")
    if not os.path.exists(commentary_path):
        print("❌ Error: public/bodhi-commentary.json not found.")
        return
        
    with open(commentary_path, 'r', encoding='utf-8') as f:
        commentaries = json.load(f)
        
    # Extract subchapters from reading-data.json
    subchapters = []
    for ch in reading_data.get("chapters", []):
        subchapters.extend(ch.get("subchapters", []))
        
    print(f"Total Chapters (Subchapters) in reading-data.json: {len(subchapters)}")
    
    chapter_paragraph_counts = {}
    for ch in subchapters:
        ch_id_str = ch.get("id")
        ch_num = int(ch_id_str.replace("rosi.", ""))
        paragraphs = ch.get("paragraphs", [])
        p_nums = [p.get("paragraphNumber") for p in paragraphs]
        chapter_paragraph_counts[ch_num] = p_nums
        print(f"  • Chapter {ch_num} ({ch.get('title')}): {len(paragraphs)} paragraphs (IDs: {p_nums[0]} ~ {p_nums[-1]})")
        
    print("\n--------------------------------------------------------------------------------")
    print("1. PARAGRAPH SEQUENCE CHECK (Txt source files in '새 폴더')")
    print("--------------------------------------------------------------------------------")
    
    for i in range(1, 11):
        txt_filename = f"{i}.txt"
        txt_path = os.path.join(data_dir, txt_filename)
        if not os.path.exists(txt_path):
            print(f"  ⚠️ {txt_filename} not found in '새 폴더'.")
            continue
            
        with open(txt_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            
        headers = [int(n) for n in re.findall(r'^문단\s+(\d+)', content, re.MULTILINE)]
        
        seen = set()
        duplicates = []
        for h in headers:
            if h in seen:
                duplicates.append(h)
            seen.add(h)
            
        gaps = []
        if headers:
            expected = 1
            for h in sorted(headers):
                while expected < h:
                    gaps.append(expected)
                    expected += 1
                expected = h + 1
                
        status = "✅ OK"
        details = []
        if duplicates:
            status = "❌ DUPLICATES FOUND"
            details.append(f"Duplicates: {duplicates}")
        if gaps:
            status = "❌ GAPS FOUND"
            details.append(f"Missing paragraph numbers: {gaps}")
            
        print(f"  • {txt_filename}: {len(headers)} paragraphs. Status: {status}")
        for d in details:
            print(f"    -> {d}")

    print("\n--------------------------------------------------------------------------------")
    print("2. COMMENTARY DATABASE CHECK (bodhi-commentary.json)")
    print("--------------------------------------------------------------------------------")
    
    commentary_keys = list(commentaries.keys())
    print(f"Total entries in bodhi-commentary.json: {len(commentary_keys)}")
    
    orphan_commentaries = []
    missing_commentaries = {}
    
    for key in commentary_keys:
        match = re.match(r'^rosi\.(\d+)\.(\d+)$', key)
        if not match:
            orphan_commentaries.append((key, "Invalid key format"))
            continue
            
        ch_num = int(match.group(1))
        p_num = int(match.group(2))
        
        if ch_num not in chapter_paragraph_counts:
            orphan_commentaries.append((key, f"Chapter {ch_num} does not exist in reading-data.json"))
        elif p_num not in chapter_paragraph_counts[ch_num]:
            orphan_commentaries.append((key, f"Paragraph {p_num} does not exist in Chapter {ch_num}"))
            
    # Check which paragraphs are missing commentaries (for chapters 1, 2, 3)
    for ch_num in [1, 2, 3]:
        if ch_num in chapter_paragraph_counts:
            missing_commentaries[ch_num] = []
            for p_num in chapter_paragraph_counts[ch_num]:
                key = f"rosi.{ch_num}.{p_num}"
                if key not in commentaries:
                    missing_commentaries[ch_num].append(p_num)
                    
    print("\n  [Missing Commentaries by Chapter]")
    for ch_num, missing in missing_commentaries.items():
        if missing:
            print(f"  • Chapter {ch_num}: Missing {len(missing)} commentaries (Paragraphs: {missing})")
        else:
            print(f"  • Chapter {ch_num}: ✅ All paragraphs have commentaries")
            
    if orphan_commentaries:
        print(f"\n  [Orphan Commentaries ({len(orphan_commentaries)} found)]")
        for key, reason in orphan_commentaries[:10]:
            print(f"  • {key}: {reason}")
        if len(orphan_commentaries) > 10:
            print(f"  ... and {len(orphan_commentaries)-10} more orphans.")
    else:
        print("\n  • ✅ No orphan commentaries found")

    print("\n--------------------------------------------------------------------------------")
    print("3. WEBTOON / COMIC IMAGES CHECK (src/assets/learning-comic/)")
    print("--------------------------------------------------------------------------------")
    
    comic_base_dir = os.path.join(workspace_dir, "src", "assets", "learning-comic")
    
    for ch_num in [1, 2, 3]:
        if ch_num not in chapter_paragraph_counts:
            continue
            
        ch_folder = os.path.join(comic_base_dir, f"chapter-{ch_num}")
        p_nums = chapter_paragraph_counts[ch_num]
        
        missing_images = []
        orphan_images = []
        
        if not os.path.exists(ch_folder):
            print(f"  • Chapter {ch_num} webtoon folder does not exist at {ch_folder}!")
            continue
            
        existing_images = []
        for f in os.listdir(ch_folder):
            match = re.match(r'^(\d+)\.webp$', f)
            if match:
                existing_images.append(int(match.group(1)))
                
        # Find missing
        for p_num in p_nums:
            if p_num not in existing_images:
                missing_images.append(p_num)
                
        # Find orphans
        for img_num in existing_images:
            if img_num not in p_nums:
                orphan_images.append(img_num)
                
        print(f"  • Chapter {ch_num}:")
        if missing_images:
            print(f"    - Missing {len(missing_images)} webtoon images: {missing_images}")
        else:
            print("    - ✅ All paragraphs have corresponding webtoon WebP images")
            
        if orphan_images:
            print(f"    - Orphan webtoon images found (image exists but no paragraph): {orphan_images}")
        else:
            print("    - ✅ No orphan webtoon images found")

    print("\n================================================================================")

if __name__ == "__main__":
    analyze()
