import os
import sys
import re
from PIL import Image

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def convert_comics():
    # Accept chapter number from arguments, default to 2
    chapter = "2"
    if len(sys.argv) > 1:
        chapter = sys.argv[1]
        
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_folder = os.path.join(workspace_dir, "학습만화", chapter)
    dest_folder = os.path.join(workspace_dir, "src", "assets", "learning-comic", f"chapter-{chapter}")
    
    if not os.path.exists(src_folder):
        print(f"Source folder {src_folder} does not exist.")
        return
        
    os.makedirs(dest_folder, exist_ok=True)
    print(f"Converting png files from {src_folder} to webp in {dest_folder}...")
    
    # List files matching <number>.png
    png_files = []
    for f in os.listdir(src_folder):
        match = re.match(r'^(\d+)\.png$', f)
        if match:
            num = int(match.group(1))
            png_files.append((num, f))
            
    png_files.sort()
    
    if not png_files:
        print("No png files found to convert.")
        return
        
    for num, filename in png_files:
        src_path = os.path.join(src_folder, filename)
        dest_filename = f"{num}.webp"
        dest_path = os.path.join(dest_folder, dest_filename)
        
        try:
            with Image.open(src_path) as img:
                # Convert to webp with quality=80 to match previous file size/quality
                img.save(dest_path, "WEBP", quality=80)
            print(f"  Converted {filename} -> {dest_filename}")
        except Exception as e:
            print(f"  Error converting {filename}: {e}")
            
    print(f"Successfully converted {len(png_files)} files to webp.")

if __name__ == "__main__":
    convert_comics()
