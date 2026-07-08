import json
import os

def check_commentaries():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(workspace_dir, "public", "bodhi-commentary.json")
    
    if not os.path.exists(json_path):
        print(f"File {json_path} does not exist.")
        return
        
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"Total keys in bodhi-commentary.json: {len(data)}")
    keys = sorted(data.keys())
    # Group by chapter number
    chapters = {}
    for key in keys:
        parts = key.split('.')
        if len(parts) >= 3:
            chap = parts[1]
            chapters[chap] = chapters.get(chap, 0) + 1
            
    print("Chapters in bodhi-commentary.json:")
    for chap, count in sorted(chapters.items(), key=lambda x: int(x[0])):
        print(f"  Chapter {chap}: {count} entries")

if __name__ == "__main__":
    check_commentaries()
